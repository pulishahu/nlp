#!/usr/bin/env python

'''
Dump events from the Manager interface to stdout.
'''

__author__  = 'David Wilson'
__id__      = '$Id$'

import sys, time, socket
import thread
import datetime
import json, logging
from fysom import Fysom
from Asterisk.Config import Config
from Asterisk.Manager import CoreManager
import Asterisk.Manager, Asterisk.Util
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from gevent import monkey; monkey.patch_all()
import gevent
import psutil

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

import optparse

OUTBOUND_CHANNEL="DAHDI"
PORT=8080
IP='0.0.0.0'

numbers = {}
unique = {}
hash = {}
_connections = {}

LOGGING_LEVELS = {'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG}


class MyManager(CoreManager):
    '''
    Print events to stdout.
    '''
    def get_uniqueid(self, packet):
        uniqueid = packet.get('Uniqueid', None)
        if uniqueid is None:
            uniqueid = packet.get('UniqueID', None)
        if uniqueid is None:
            uniqueid = packet.get('Uniqueid1', None)
        if uniqueid is None:
            logger.debug ("Could not get uniqueid from packet: %s"%packet)
        return uniqueid

    def printstatechange(self,e):
        packet = e.args[0]

        timestamp = datetime.datetime.now()
        try:
            t = int(packet["Timestamp"].split('.')[0])
        except:
            logger.info("Error parsing event time stamp: %s"%packet["Timestamp"])
            timestamp = datetime.datetime.now()
        else:
            try:
                timestamp = datetime.datetime.fromtimestamp(t)
            except:
                logger.info("Error converting event time stamp to python structure: %s"%t)
                timestamp = datetime.datetime.now()

        tid = e.args[1]
        uniqueid = self.get_uniqueid(packet)
        data = {}
        data["src"] = e.src
        data["status"] = e.dst
        data["tid"] = tid
        formatted_ts = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        data["timestamp"] = formatted_ts
        data["reason"] = "Normal Termination"
        sent_status = json.dumps(data)
        logger.debug('event: %s, src: %s, dst: %s, uniqueid: %s, tid: %s, timestamp: %s' % (e.event, e.src, e.dst, uniqueid, tid, formatted_ts))
        logger.info('State Sent to %s: %s' % (tid, sent_status))
        #print('State Sent to %s: %s' % (uniqueid, sent_status))
        if tid in _connections:
            _connections[tid].emit(tid,sent_status)
            if e.dst == "customer_hangup":
                del _connections[tid]

    def __init__(self, *args):
        super(MyManager,self).__init__(*args)
        self.hash = {}
        self.link_call_legs = {}

    def lookupMethod(self, event):
        return getattr(self, 'do_' + event.lower(), None)

    def do_unknown(self,packet):
        event = packet.get('Event')
        logger.debug ("Unhandled event: %s"% event)
        #logger.debug ("Event: %s"%packet)

    def do_newcallerid(self,packet):
        sm = Fysom({
                'initial': 'idle',
                'events': [
                    {'name': 'new_callerid',    'src': 'idle',         'dst': 'call_started'},
                    {'name': 'caller_dialling', 'src': 'call_started', 'dst': 'dialling_customer_phone'},
                    {'name': 'caller_ringing',  'src': 'dialling_customer_phone',     'dst': 'customer_phone_ringing'},
                    {'name': 'caller_answered',    'src': 'customer_phone_ringing',      'dst': 'answered'},
                    {'name': 'calling_callcenter', 'src': 'answered',      'dst': 'dialling_callcenter'},
                    {'name': 'callcenter_pickup', 'src': 'dialling_callcenter',      'dst': 'call_picked_up_and_talking'},
                    {'name': 'customer_hangup',    'src': 'dialling_callcenter',      'dst': 'call_terminated'},
                    {'name': 'customer_hangup',    'src': 'customer_phone_ringing',      'dst': 'call_terminated'},
                    {'name': 'customer_hangup',    'src': 'answered',      'dst': 'call_terminated'},
                    {'name': 'customer_hangup',    'src': 'call_picked_up_and_talking',      'dst': 'call_terminated'},
                    ]
                })
        logger.debug ("Hash length is: %d"%len(self.hash))
        logger.debug ("Received a NewCallerid event in state %s"%sm.current)
        #logger.info("Event: %s"%packet)
        uniqueid = self.get_uniqueid(packet)
        channel = packet.get('Channel')
        # We process only new callerids for channels starting in OUTBOUND_CHANNEL
        if not str(channel).startswith(OUTBOUND_CHANNEL):
            logger.info("Ignoring new callerid event on channel %s"%channel)
            return
        call = self.hash.get(uniqueid, None)
        if call is None:
            call = {}
            call["tid"] = packet.get('CallerIDNum')
            call["customer_channel"] = channel
            call['sm'] = sm
            call['sm'].onchangestate = self.printstatechange
        else:
            logger.error("New callerid event seen for an existing call")
            logger.error("Event: %s"%packet)
        if call['sm'].can("new_callerid"):
            call['sm'].new_callerid(packet,call["tid"])
            self.hash[uniqueid] = call
            logger.debug ("Current State: %s"% call['sm'].current)
        else:
            logger.debug ("Ignoring this event")

    def do_dial(self,packet):
        logger.debug ("Received a Dial event")
        uniqueid = self.get_uniqueid(packet)
        call = self.hash.get(uniqueid, None)
        if call is not None:
            if call['sm'].can("calling_callcenter"):
                # destuniqueid = packet.get('DestUniqueID', None)
                # if destuniqueid is not None:
                #     self.link_call_legs[destuniqueid] = uniqueid
                callcenter_channel = packet.get('Destination', None)
                if callcenter_channel is not None:
                    call["callcenter_channel"] = callcenter_channel
                else:
                    logger.debug ("Destination channel missing in dial event: %s"%packet)
                call['sm'].calling_callcenter(packet,call["tid"])
            else:
                logger.debug ("Invalid State transition")
        else:
            logger.debug ("Hash missing for uniqueid %s"% uniqueid)
            logger.debug (packet)

    def do_hangup(self,packet):
        logger.debug ("Received a Hangup event")
        uniqueid = self.get_uniqueid(packet)
        call = self.hash.get(uniqueid, None)
        channel = packet.get('Channel')
        if call is not None:
            if call['sm'].can("customer_hangup") and channel == call['customer_channel']:
                call['sm'].customer_hangup(packet,call["tid"])
            else:
                logger.debug ("Invalid State transition")
            logger.debug ("Removing unique id %s from hash"%uniqueid)
            del self.hash[uniqueid]
            logger.debug ("Hash length is: %d"%len(self.hash))
        else:
            logger.debug ("Hash missing for uniqueid %s"% uniqueid)
            logger.debug (packet)

    def do_newstate(self,packet):
        logger.debug ("Received a Newstate event")
        uniqueid = self.get_uniqueid(packet)
        state = packet.get('ChannelStateDesc')
        call = self.hash.get(uniqueid, None)
        channel = packet.get('Channel')
        if call is not None:
            current = call['sm'].current
            if current == 'call_started' and state == 'Dialing':
                call['sm'].caller_dialling(packet,call["tid"])
            elif current == 'dialling_customer_phone'  and state == 'Ringing':
                call['sm'].caller_ringing(packet,call["tid"])
            elif current == 'customer_phone_ringing'  and state == 'Up' and channel == call['customer_channel']:
                call['sm'].caller_answered(packet,call["tid"])
            else:
                logger.debug ("Not handling %s event uniqueid: %s"%(packet.get('Channel'), uniqueid))
                #print packet
        else:
            logger.debug ("Hash missing for uniqueid %s"% uniqueid)

    def do_bridge(self,packet):
        logger.debug ("Received a Bridge event")
        uniqueid = self.get_uniqueid(packet)
        call = self.hash.get(uniqueid, None)
        if call is not None:
            if call['sm'].can("callcenter_pickup"):
                call['sm'].callcenter_pickup(packet,call["tid"])
            else:
                logger.debug ("Invalid State transition")
        else:
            logger.debug ("Hash missing for uniqueid %s"% uniqueid)
            logger.debug (packet)

    def do_varset(self,packet):
        pass
    def do_newchannel(self,packet):
        pass
    def do_newaccountcode(self,packet):
        pass
    def do_rtpreceiverstat(self,packet):
        pass
    def do_newexten(self,packet):
        pass
    def do_jitterbufstats(self,packet):
        pass
    def do_unlink(self,packet):
        pass
    def do_peerstatus(self,packet):
        pass
    def do_channelupdate(self,packet):
        pass
    def do_queuememberstatus(self,packet):
        pass

    def on_Event(self, event):
        packet = dict(event)
        if 'Event' in packet:
            event = packet.get('Event')
            method = self.lookupMethod(event) or self.do_unknown
            method(packet)

class EventsServer(BaseNamespace, BroadcastMixin):
    def initialize(self):
        _connections["socket"] = self
        super(EventsServer, self).initialize()

    def on_tidSession(self, tid):
        _connections[tid] = self
        print _connections

class Application(object):
    def __init__(self):
        self.buffer = []

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')
        if path.startswith("socket.io"):
            logger.debug ("Listening for incoming HTTP requests")
            socketio_manage(environ, {'/pounz': EventsServer})
        else:
            logger.error ("Error Listening for incoming HTTP requests")
            return not_found(start_response)

def start_asterisk():
    logger.debug ("Asterisk Connection parameters: %s"%str(Config().get_connection()))
    manager = MyManager(*Config().get_connection())
    try:
        logger.debug ("Starting Asterisk Listener")
        manager.serve_forever()
    except KeyboardInterrupt, e:
        logger.debug ("Exiting via Keyboard interrupt")
        raise SystemExit ("Exiting via Keyboard interrupt")
    except:
        logger.exception("Error in manager.serve_forever")

def main(argv):
    try:
        thread.start_new_thread(start_asterisk,())
    except:
        logger.error ("Unable to start Asterisk connection thread")


if __name__ == '__main__':
    """
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.DEBUG)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('PounzEventDaemon')
    """
    logger = logging.getLogger('PounzEventDaemon')
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(name)s:%(levelname)s] %(message)s')
    ch = logging.FileHandler("/tmp/pounzeventdaemon.log")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    main(sys.argv[1:])
    try:
        SocketIOServer((IP, PORT), Application(),
                        resource="socket.io", policy_server=True,
                        policy_listener=('0.0.0.0', 10843)).serve_forever()
    except KeyboardInterrupt:
        logger.debug ("Exiting via Keyboard interrupt")
        raise SystemExit ("Exiting via Keyboard interrupt")
    except:
        logger.exception ("Exiting due to unknown cause")
        raise SystemExit ("Exiting due to unknown cause")
