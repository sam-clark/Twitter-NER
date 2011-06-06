#!/usr/bin/python

import sys

sys.path.append('python/cap')
sys.path.append('python')

import Features

fe  = Features.FeatureExtractor()
cap = Features.CapClassifier()

entityCounts = {}
#First pass; compute counts
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
    entityCounts[key] = entityCounts.get(key, 0) + 1

prevSid = None
minRedund = None
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

    if prevSid and prevSid != sid and minRedund and minRedund > 1:
        goodCap = cap.Classify(prevWords) > 0.5
        quotes = Features.GetQuotes(prevWords)

        for i in range(len(prevWords)):
            features = fe.Extract(prevWords, prevPos, i, goodCap) + ['DOMAIN=Twitter']
            if quotes[i]:
                features.append("QUOTED")
            print " ".join(features) + " %s" % prevTags[i]
        print

    if prevSid != sid:
        minRedund = None
        
    prevWords = words
    prevPos   = pos
    prevTags  = neTags
    prevSid   = sid
    if minRedund:
        minRedund = min(minRedund,entityCounts.get(key,0))
    else:
        minRedund = entityCounts.get(key,0)
