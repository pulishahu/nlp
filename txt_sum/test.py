import nltk
import codecs
import json
import string
import time
from  urllib import urlopen
from nltk.corpus import wordnet as wn


def getSynonym(word, tag):
    pos_list = {"JJ":"ADJ","JJR":"ADJ", "JJS":"ADJ","NN":"NOUN","NNS":"NOUN","NPS":"NOUN","NP":"NOUN","RBR":"ADV","RBS":"ADV","RB":"ADV","VB":"VERB","VBD":"VERB","VBG":"VERB","VBN":"VERB","VBP":"VERB","VBZ":"VERB"};
    tag_list = pos_list.keys()
    li = {} 
    if tag in tag_list:
        dd = pos_list.get(tag)
        if dd == "VERB":
            tt =  wn.synsets(word,pos=wn.VERB)
            for key in tt:
                ss = key.lemma_names
                for s in ss:
                    li[s] = s
        if dd == "NOUN":
            tt =  wn.synsets(word,pos=wn.NOUN)
            for key in tt:
                ss = key.lemma_names
                for s in ss:
                    li[s] = s

        if dd == "ADV":
            tt =  wn.synsets(word,pos=wn.ADV)
            for key in tt:
                ss = key.lemma_names
                for s in ss:
                    li[s] = s
        if dd == "ADJ":
            tt =  wn.synsets(word,pos=wn.ADJ)
            for key in tt:
                ss = key.lemma_names
                for s in ss:
                    li[s] = s
    return li.keys()

sentence = "In a major blow to the CPM in Kerala, an additional sessions court found 12 accused, including three CPM local leaders, guilty of the murder of TP Chandrasekharan--the leader of the Revolutionary Marxist Party. This is the most political murder in the state in recent times, and sent waves of shock across Kerala in 2012. Though the acquittal of another prominent CPM leader, P Mohanan--a member of the Kozhikode district secretariat--brought some relief to the party, the comments made by the judge referring to the 'political animosity behind the murder' left little doubt about the CPM's involvement.  Among the 12 who were found guilty of the crime, eleven have been awarded life imprisonment. This includes Manojan, a former branch secretary in Kozhikode district, PK Kunjanandan, a member of Panoor area committee, and KC Ramachandran, another local committee member in Kozhikode district. The seven- member killer gang, whom the court found to have been assassins hired to annihilate a 'political enemy', was awarded life imprisonment, too.  TP Chandrasekharan, who walked out of the party and formed the RMP in 2009, was hacked to death on 4 May 2012. The brutality of the murder by the hired assassins sent a shiver down people's spines, even those belonging to the CPM. The undercurrents triggered by this murder in and outside the CPM were manifold. The party lost a by-election in Neyyattinkara Assembly constituency, which was held soon after the murder, despite the existence of a strong anti- incumbency sentiment against the Congress. Many local level and area-level committees of the party were shaken by the mass exodus in protest against the murder. "

sentence = "Many local level and area-level committees of the party were shaken by the mass exodus in protest against the murder. "
#print sentence


#POS_LIST = {"NN":"NOUN", VERB, ADJ, ADV}

#print wn.synsets("dog", "VERB")
print "\n\n"

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

datasource = urlopen("raw_text.txt").read()
sentence  = nltk.clean_html(datasource)
sentence = sentence.decode('utf8')

tokens = nltk.word_tokenize(sentence)
tagged = nltk.pos_tag(tokens)
#entities = nltk.chunk.ne_chunk(tagged)
#print tokens

syn = {}
for key in tagged:
    syn[key[0]] = getSynonym(key[0], key[1])

json_hash = {}
json_hash["para"] = sentence
json_hash["tags"] = tagged
json_hash["syn"] = syn

json_hash["para"] =  '\n'.join(tokenizer.tokenize(json_hash["para"]))

FILE = open("corp.json", "w+")
FILE.write(json.dumps(json_hash))
FILE.close()
#print json_hash
#print tagged


"""
Egypt will remain a military dictatorship indefinitely.
Egypt is as far away from the revolutionary promise of Tahrir Square as it was in November 2010 when Mubarak staged perhaps the most fraudulent parliamentary election since they began in the late 1970s.
Just as Egypt's political system before the January 25 uprising was rigged in favor of Mubarak and his constituents, the Brothers sought to stack the new order in their favor, and today's winners will build a political system that reflects their interests.
Yet, across the political spectrum, leaders defaulted to their traditional corners rather than confront the sheer complexity of Egypt's political, social, and economic problems.
The Brothers were in charge, but it was still Mubarak's Egypt: whoever ruled could do so without regard to anyone who might disagree.
"""
