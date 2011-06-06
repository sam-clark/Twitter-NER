#!/usr/bin/python

import sys
import re
import nltk

import Features

USE_TAGS = True
#TAG_MAP = {
#    "PERSON":"PERSON",
#    "LOCATION":"LOCATION",
#    "ORGANIZATION":"MUC_ORGANIZATION",
#}

#TAG_MAP = {
#    "PERSON":"per",
#    "LOCATION":"loc",
#    "ORGANIZATION":"MUC_ORGANIZATION",
#}

TAG_MAP = {
    "PERSON":"ENTITY",
    "LOCATION":"ENTITY",
    "ORGANIZATION":"MUC_ORGANIZATION",
}


def mapTag(t):
    if TAG_MAP.has_key(t):
        return TAG_MAP[t]
    else:
        return t

fe = Features.FeatureExtractor('data/dictionaries')
def PrintFeatures(sentences):
    for s in sentences:
        words = s.split(' ')
        pos = [x[1] for x in nltk.pos_tag(words)]
        tags = []

        tag = None
        last = True
        for i in range(len(words)):
            mstart = re.search(r'^XXX([A-Z]+)-', words[i])
            mend   = re.search(r'-([A-Z]+)XXX$', words[i])
            if mstart:
                tag = "B-%s" % mapTag(mstart.group(1))
                words[i] = re.sub(r'^XXX([A-Z]+)-', '', words[i])
                last = False
            if mend:
                if not mstart:
                    tag = "I-%s" % mapTag(mend.group(1))
                words[i] = re.sub(r'-([A-Z]+)XXX$', '', words[i])
                last = True
            elif last:
                tag = "O"
            elif not last and not mstart:
                tag = tag.replace('B', 'I')

            #Just do entities (no person, loc, etc...)
            if "DATE" in tag or "TIME" in tag or "MONEY" in tag or "PERCENT" in tag:
                tag = "O"
            elif (tag[0] == 'B' or tag[0] == 'I') and not USE_TAGS:
                tag = tag[0] + "-ENTITY"
            tags.append(tag)

        quotes = Features.GetQuotes(words)
        #capFeatures = fe.ExtractCapFeatures(words)
        for i in range(len(words)):
            #features = fe.Extract(words, i) + ['DOMAIN=News'] + capFeatures
            features = fe.Extract(words, pos, i) + ['DOMAIN=News']
            #features = fe.Extract(words, i)
            if quotes[i]:
                features.append("QUOTED")
            #print " ".join(features) + " " + tags[i] + "\n"
            print " ".join(features) + " " + tags[i]

        print

document = ""
collecting = False
for line in open(sys.argv[1]):
    line = line.rstrip('\n')
    if line == "</TEXT>" or line == "</TXT>" and len(document) > 0:
        document = document.replace('<p>', '')
        document = document.replace('</p>', '')
        document = document.replace('<s>', '')
        document = document.replace('</s>', '')
        document = document.replace('<TEXT>', '')
        document = document.replace('<TXT>', '')
        document = document.replace('</TXT>', '')
        document = re.sub(r'<[A-Z]+ TYPE="([A-Z]+)("|\|)[^>]*?>([^<]+)</[A-Z]+?>', r" XXX\1-\3-\1XXX ", document)
        sentences = nltk.sent_tokenize(document)
        sentences = [' '.join(nltk.word_tokenize(s.replace("''", '"').replace("``", '"'))) for s in sentences]
        PrintFeatures(sentences)
        collecting = False
        document = ""
    elif line == "<TEXT>" or line == "<TXT>":
        collecting = True
    if collecting:
        document += ' ' + line
