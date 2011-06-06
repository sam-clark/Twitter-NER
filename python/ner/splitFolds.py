#!/usr/bin/python

import sys
import re

foldsOut = []

for i in range(int(sys.argv[1])):
    foldsOut.append(open('fold%s' % str(i+1), 'w'))

sentence = []
i = 0
for line in sys.stdin:
    if re.match(r'^\s*$', line):
        foldsOut[i % len(foldsOut)].write(''.join(sentence) + "\n")
        sentence = []
        i += 1
    else:
        sentence.append(line)
