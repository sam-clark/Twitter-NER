#!/usr/bin/python

##############################################################################################
# fb2dictionaries.py
# Input:  freebase type list and list of types with dictionary names
# Output: directory containing FB dictionaries
##############################################################################################

import sys
import re

outDir = sys.argv[3]

type2dict = {}
dict2file = {}
for line in open(sys.argv[1]):
    (name, types) = line.rstrip('\n').split(' ')
    types = types.split(',')
    for t in types:
        type2dict[t] = name
    if not dict2file.has_key(name):
        dict2file[name] = open('%s/%s' % (outDir,name), 'w')

for line in open(sys.argv[2]):
    (mention,t) = line.rstrip('\n').split('\t')
    if type2dict.has_key(t):
        dict2file[type2dict[t]].write('%s\n' % mention)
