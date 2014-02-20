import nltk
import codecs
import json
import string
import time
from  urllib import urlopen

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

def log_write(datasource, murl, datalength, i):
    print "url status code: %s, Data length: %s, Count: %s " % (datasource.getcode(), datalength, i)
    filename = "Mboomilogfile.txt"
    l = datasource.info()
    log = { }
    log['url'] = murl
    log['response_code'] = datasource.getcode()
    log['datalength'] = datalength
    log['url-content-length'] = l.get('content-length',"unknown")
    log['count'] = i
    log['time'] = time.ctime()
    logjson = json.dumps(log)

    FILE = open(filename, "a")
    FILE.write("\n")
    FILE.write(logjson)
    FILE.close()


def createDataJson(raw, url):
    
    raw = raw.read()
    raw  = nltk.clean_html(raw)
    tokens = raw.decode('utf8')
    tokens = nltk.word_tokenize( tokens)
    txt = {}
    txt[url] = tokens
    file = open('corp.txt', 'a')
    file.write("\n")
    file.write(json.dumps(txt))
    file.close()
    return tokens

def getDataFromFile():
    with open("corp.txt") as json_file:
        json_data = json.load(json_file)
        tokens =  json_data.get("mal_data")
        return tokens

def getequalantWords(tokens):
    word_hash = {}
    for word in tokens:
        for key in tokens:
            if len(word) < len(key):
                if len(word) > 4:
                    search_word_part = word[0:-2]
                elif len(word) == 3:
                    search_word_part = word[0:-1]
                elif len(word) == 2:
                    search_word_part = word
                else:
                    continue
                if search_word_part in key:
                    li = {}
                    if word_hash.has_key(word):
                        li = word_hash[word]
                    li[key] = len(key)
                    word_hash[word] = li
    return word_hash

def cleanupWords(tokens):

    eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-."
    fresh = {}
    li ={}
    word_keys = tokens.keys()
    for key in tokens:
        words = tokens[key]
        if key[0] in eng:
            li[key] = len(key)
        for word in words:
            if word in word_keys:
                li[word] = key

    for key in li:
        if key[0] in eng:
            del tokens[key]
            continue
        xx = tokens[li[key]]
        yy = tokens[key]
        xx.update(yy)
        tokens[li[key]] = xx
        del tokens[key]
    return tokens

def addToCorp(tokens):
    old_tokens = {}
    try:
        with open("words.json") as json_file:
            if json_file:
                json_data = json.load(json_file)
                old_tokens =  json_data.get("words")
    except:
        print "Exception on words file read."

    for key in tokens:
        if key in old_tokens.keys():
            old_words = old_tokens[key]
            old_words.update(tokens[key])
            old_tokens[key] = old_words
        else:
            old_tokens[key] = tokens[key]
    print "Before Total count of wordslist:   %s" %len(old_tokens)
    cleanupWords(old_tokens)
    print "After Total count of wordslist:   %s" %len(old_tokens)

    json_hash = {}
    json_hash["words"] = old_tokens
    file = open('words.json', 'w+')
    file.write(json.dumps(json_hash))
    file.close()

#source_encoding = "iso-8859-1"
#url = "http://www.mathrubhumi.com/story.php?id=429181"
#createDataJson(url)



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
#time.sleep(5)
for i in range(start_point, 1649000):

    for murl in url_list:

        murl = murl+str(i)
        print "url: ",murl
        datasource = urlopen(murl)
        check_status(datasource.getcode())
        tokens = createDataJson(datasource, murl)
        log_write(datasource, murl, len(tokens), i)

        #tokens = getDataFromFile()
        tokens = getequalantWords(tokens)
        tokens = cleanupWords(tokens)
        addToCorp(tokens)


"""
for key in tokens:
    l1 =  list(key)
    if l1[0] == u'\u0D07':
        print "detected %s " % l1[0]
"""
