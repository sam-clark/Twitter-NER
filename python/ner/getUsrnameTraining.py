#!/usr/bin/python

import sys
import re
import Features

for line in sys.stdin:
    line = line.rstrip('\n')
    fields = line.split('\t')
    text = fields[6]

    #Throw out posts which are retweets
    if re.search(r'(^RT| RT:| RT )', text, re.IGNORECASE):
        continue
    
    #strip initial usernames, and ending usernames
    text = re.sub(r'^\s*(@[^ ]+\s*)*', '', text)
    text = re.sub(r'\s*(@[^ ]+\s*)*$', '', text)

    #Skip if text doesn't contain any usernames
    if not re.search(r' @[^ ]', text):
        continue

    print text
