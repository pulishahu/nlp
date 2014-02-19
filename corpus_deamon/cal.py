import urllib
import re
import json
import sys
import time
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def check_status(status):

    if(status != 200):
        print "The requested page could not be found\nCheck your net connection or check the above url in your browser"
        print "If net connection is not available press '2' to exit.\nTo continue with next url press '1'\n"
        inp = raw_input("Enter your choice :")
        if(inp == 2):
            print "System exit"
            sys.exit()
        elif(inp == 1):
            print "Continuing with new url..."


def get_start_point():
    decoder = json.JSONDecoder()

    try:
        with open('Mboomilogfile.txt') as logfile:
            start = list(logfile)[-1]
    except:
        print "error on read log file"
        sys.exit()
    try:
    
        dicti =  decoder.decode(start)
        if(not( dicti['count'] > 164000 and dicti['count'] < 1649000)):
            print "Incorrect starting point: ",dicti['count'], " Please check log file for details."
            sys.exit()
        return dicti['count']
    except:
        print "Starting point is unavailable. System exit."
        sys.exit()



def write_file(filename, data, url):
    
    encoder =  json.JSONEncoder()
    l = {"url":url,"data":data}
    data = encoder.encode(l)
    FILE = open(filename, "a")
    FILE.write("\n")
    FILE.write(encoder.encode(l))
    FILE.close()

def log_write(filename, data):
    FILE = open(filename, "a")
    FILE.write("\n")
    FILE.write(data)
    FILE.close()

def get_url_data( url, filename):

    data = ""
    while 1:
        line = url.readline()
        if(line == ""): break
        data = data+line
    
    data = remove_html_tags(data)
    data_words = data.split()
    data = ""
    for item in data_words:
        if( ord(item[0]) == 224):
            data = data+" "+item
    if(data != ""):        
        write_file(filename, data, url.geturl())
    return len(data)

print "\n\n\n\n"
print "================================"
print "PYTHON MALAYALAM CORPUS PROGRAME"
print "UNIVERISTY OF KERALA"
print "DEPT OF LINGUISTICS"
print "================================"
print "\n\n\n\n"

print "Programe will start within 10 minutes"
print "Check log files"
time.sleep(5)
print "\n\n\n"

url_list = ['http://www.mathrubhumi.com/new09/php/print.php?id=',
        'http://sports.mathrubhumi.com/print.php?id=',
        'http://wellness.mathrubhumi.com/print.php?id=',
        'http://wheels.mathrubhumi.com/print.php?id=',
        'http://www.mathrubhumi.com/business/php/print.php?id=',
        'http://www.mathrubhumi.com/kids/print.php?id=',
        'http://www.mathrubhumi.com/cj/php/print.php?id=',
        'http://www.mathrubhumi.com/nri/section/print.php?id=',
        'http://www.mathrubhumi.com/mb4eves/php/print.php?id=']

filename = "Mboomi.txt"
encoder =  json.JSONEncoder()
decoder = json.JSONDecoder()

start_point = get_start_point() 
print "start from ",start_point
time.sleep(5)
for i in range(start_point, 1649000):

    for murl in url_list:
        murl = murl+str(i)
        datasource = urllib.urlopen(murl)
        print "URL : ",murl
        l = datasource.info()
        check_status(datasource.getcode())
        datalength = get_url_data(datasource, filename )
        print "URL STATUS : ",datasource.getcode()," DATA LENGTH : ",datalength
        log = { }
        log['url'] = murl
        log['response_code'] = datasource.getcode()
        log['datalength'] = datalength
        log['url-content-length'] = l.get('content-length',"unknown")
        log['count'] = i
        log['time'] = time.ctime()
        logjson = encoder.encode(log)
        log_write("Mboomilogfile.txt",logjson)

