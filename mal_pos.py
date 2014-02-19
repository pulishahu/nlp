import nltk
import codecs
import json
import string
from  urllib import urlopen



def createDataJson(url):

    raw = urlopen(url).read()
    raw  = nltk.clean_html(raw)
    tokens = raw.decode('utf8')
    tokens = nltk.word_tokenize( tokens)

    txt = {}
    txt["mal_data"] = tokens

    file = open('corp.txt', 'rw+')
    file.write(json.dumps(txt))
    file.close()

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
                    search_word_part = word[0:2]
                elif len(word) == 3:
                    search_word_part = word[0:1]
                else:
                    search_word_part = word
                if search_word_part in key:
                    li = {}
                    if word_hash.has_key(word):
                        li = word_hash[word]
                    li[key] = len(key)
                    word_hash[word] = li
    return word_hash

#source_encoding = "iso-8859-1"
#url = "http://www.mathrubhumi.com/story.php?id=429181"
#createDataJson(url)


tokens = getDataFromFile()
tokens = getequalantWords(tokens)
for word in tokens:
    for key in tokens:
        w_hash =  tokens[key]
        for w in w_hash
            if len(word) > len(w):
                

#print "Word %s == %s " %(key,  len(tokens[key]))






"""
for key in tokens:
    l1 =  list(key)
    if l1[0] == u'\u0D07':
        print "detected %s " % l1[0]
        """
