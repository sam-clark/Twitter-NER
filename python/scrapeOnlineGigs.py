##############################################################################################################
# Note: run this program like so:
# export PYTHONIOENCODING=utf8; python scrapeOnlineGigs.py > venues
##############################################################################################################

import urllib2
import re
from BeautifulSoup import BeautifulSoup

def FetchLinkText(link):
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)
    return([x.text for x in soup('a')])

def FetchVenues(linkText):
    gotStates = False
    venues = []
    for i in range(len(linkText)):
        if re.match(r'^[A-Z][A-Z]/[A-Z][A-Z]', linkText[i]) or linkText[i] == "WY":
            gotStates = True
        elif gotStates:
            venues.append(linkText[i])
        elif linkText[i] == 'Privacy Policy':
            return venues
    return venues

linkText = FetchLinkText("http://www.onlinegigs.com/entities.asp?entity=venues&State=VA_WA")

states = []
for text in linkText:
    if re.match(r'^[A-Z][A-Z]/[A-Z][A-Z]', text) or text == "WY":
        states.append(text)

for state in states:
    linkText = FetchLinkText("http://www.onlinegigs.com/entities.asp?entity=venues&State=%s" % state)
    venues = FetchVenues(linkText)
    for v in list(set(venues)):
        print v
