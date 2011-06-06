#!/usr/bin/python

#Just copies features

import sys

for line in sys.stdin:
    fields = line.rstrip('\n').split(' ')
    print ' '.join(['%s t_%s' % (x, x) for x in fields[0:len(fields)-2]]) + " " + fields[len(fields)-1]
