#!/usr/bin/python

#############################################################################
# pos2cap.py
#
# Convets yamcha POS training data into training data for capitalization
# (second feature is capitalization, just throw out POS target, and move
# it to the end)
#############################################################################

import sys

for line in sys.stdin:
    line = line.rstrip("\n")
    if line == "":
        print
        continue
    line = line.lower()
    fields = line.split(' ')
    print " ".join([fields[0]] + fields[2:len(fields)-2] + [fields[1]])
