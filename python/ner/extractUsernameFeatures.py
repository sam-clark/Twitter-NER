#!/usr/bin/python

import re
import sys

import Features

df = Features.DictionaryFeatures("data/dictionaries")
for line in sys.stdin:
    words = line.rstrip('\n').split(' ')

    for i in range(len(words)):
        #Orthographic features of the username will not help?
        features = []
        #features = Features.GetOrthographicFeatures(words[i]) + df.GetDictFeatures(words[i])

        if words[i][0] == '@':
            tag = "B-ENTITY"
        else:
            tag = "O"

        if i > 0:
            features += ["p1=%s" % x for x in  Features.GetOrthographicFeatures(words[i-1]) + df.GetDictFeatures(words[i-1])]
        if i < len(words)-1:
            features += ["n1=%s" % x for x in  Features.GetOrthographicFeatures(words[i+1]) + df.GetDictFeatures(words[i+1])]

        print " ".join(features) + " %s" % tag
