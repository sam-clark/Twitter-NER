#!/usr/bin/python

import sys

sys.path.append('python/cap')
sys.path.append('python')

import Features

fe  = Features.FeatureExtractor()
cap = Features.CapClassifier()

entityConf = {}
#First pass; confidence
for line in open(sys.argv[1]):
    line = line.rstrip('\n')
    fields = line.split('\t')

    sid    = fields[0]
    date   = fields[9][0:10]
    confidence = 1.0 / float(fields[-1])
    eType  = fields[-2]
    entity = fields[-3]
    neTags = fields[-4].split(' ')
    pos    = fields[-5].split(' ')
    words  = fields[-6].split(' ')

    key = "%s\t%s\t%s" % (entity, eType, date)
    if entityConf.has_key(key):
        entityConf[key] = max(entityConf.get(key), confidence)
    else:
        entityConf[key] = confidence

prevSid = None
minConf = None
prevWords = None
prevPos   = None
prevTags  = None
for line in open(sys.argv[1]):
    line = line.rstrip('\n')
    fields = line.split('\t')

    sid    = fields[0]
    date   = fields[9][0:10]
    confidence = 1.0 / float(fields[-1])
    eType  = fields[-2]
    entity = fields[-3]
    neTags = fields[-4].split(' ')
    pos    = fields[-5].split(' ')
    words  = fields[-6].split(' ')

    key = "%s\t%s\t%s" % (entity, eType, date)

    if prevSid and prevSid != sid and minConf and minConf > 0.9:
        goodCap = cap.Classify(prevWords) > 0.5
        quotes = Features.GetQuotes(prevWords)

        for i in range(len(prevWords)):
            features = fe.Extract(prevWords, prevPos, i, goodCap) + ['DOMAIN=Twitter']
            if quotes[i]:
                features.append("QUOTED")
            print " ".join(features) + " %s" % prevTags[i]
        print

    if prevSid != sid:
        minConf = None
        
    prevWords = words
    prevPos   = pos
    prevTags  = neTags
    prevSid   = sid
    if minConf:
        minConf = min(minConf,entityConf.get(key,0))
    else:
        minConf = entityConf.get(key,0)
