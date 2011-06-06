#!/usr/bin/python

import re
import sys
import subprocess

import Features

import nltk

sys.path.append('python/cap')
#sys.path.append('python')
import cap_classifier
#import pos_tagger_stdin

sys.path.append('/homes/gws/aritter/twitter_nlp_subversion/python/stable_nlp')
from nlp2 import Tag

#cap_fe = cap_classifier.FeatureExtractor('data/cap/tweets_cap.vocab')
cap_fe = cap_classifier.FeatureExtractor('data/cap2/tweets_cap.vocab')

USE_TAGS = True
#TAG_MAP = {
#    "per":"PERSON",
#    "loc":"LOCATION",
#    "org":"OTHER",
#    "event":"OTHER",
#    "other":"OTHER",
#    "entity":"XXX_ERROR_XXX",
#}

####################################################
# Map to Entity
####################################################
TAG_MAP = {
    "per":"ENTITY",
    "loc":"ENTITY",
    "venue":"ENTITY",
    "org":"ENTITY",
    "event":"ENTITY",
    "company":"ENTITY",
    "product":"ENTITY",
    "tvshow":"ENTITY",
    "film":"ENTITY",
    "internetwebsite":"ENTITY",
    "internet_website":"ENTITY",
    "other":"ENTITY",
    "musicartist":"ENTITY",
    "sportsteam":"ENTITY",
    "entity":"ENTITY",
}

####################################################
# Map to test set tags
####################################################
TRAIN_MAP = {
    "per":"person",
    "loc":"geo-loc",
    "venue":"facility",
    "org":"other",
    "event":"other",
    "company":"company",
    "product":"product",
    "tvshow":"tvshow",
    "film":"movie",
    "internetwebsite":"company",
    "internet_website":"company",
    "other":"other",
    "musicartist":"musicartist",
    "sportsteam":"sportsteam",
    "entity":"other"
}


####################################################
# Map to test set tags
####################################################
TEST_MAP = {
    "gov_agency":"other",
    "person":"person",
    "geo-loc":"geo-loc",
    "company":"company",
    "other":"other",
    "musicartist":"musicartist",
    "facility":"facility",
    "product":"product",
    "sportsteam":"sportsteam",
    "movie":"movie",
    "tvshow":"tvshow",
    "award":"other",
    "holiday":"other",
    "politician":"person",
    "tvnetwork":"other",
    "food":"product",
    "restaurant":"facility",
    "athlete":"person",
    "sportsleague":"other",
    "videogame":"product",
}

####################################################
# Map to person, location, organization
####################################################
TRAIN_PLO_MAP = {
    "per":"per",
    "loc":"loc",
    "venue":"loc",
    "org":"org",
    "event":"other",
    "company":"org",
    "product":"other",
    "tvshow":"other",
    "film":"other",
    "internetwebsite":"org",
    "internet_website":"org",
    "other":"other",
    "musicartist":"org",
    "sportsteam":"org",
    "entity":"other"
}

TEST_PLO_MAP = {
    "gov_agency":"org",
    "person":"per",
    "geo-loc":"loc",
    "company":"org",
    "other":"other",
    "musicartist":"org",
    "facility":"loc",
    "product":"other",
    "sportsteam":"org",
    "movie":"other",
    "tvshow":"other",
    "award":"other",
    "holiday":"other",
    "politician":"per",
    "tvnetwork":"other",
    "food":"other",
    "restaurant":"loc",
    "athlete":"per",
    "sportsleague":"other",
    "videogame":"other",
}


####################################################
# Map to PERSON/LOC/ORG/MISC
####################################################
#TAG_MAP = {
#    "per":"PER",
#    "loc":"LOC",
#    "venue":"LOC",
#    "org":"ORG",
#    "event":"MISC",
#    "company":"ORG",
#    "product":"MISC",
#    "tvshow":"MISC",
#    "film":"MISC",
#    "internetwebsite":"ORG",
#    "internet_website":"ORG",
#    "other":"MISC",
#    "musicartist":"ORG",
#    "sportsteam":"ORG",
#    "entity":"MISC",
#}

MAPTAG = None
def mapTag(tag):
    if MAPTAG == 'NONE':
        return tag
    elif MAPTAG == 'ENTITY':
        return 'ENTITY'
    elif MAPTAG == 'TRAIN':
        return TRAIN_MAP[tag]
    elif MAPTAG == 'PLO_TRAIN':
        return TRAIN_PLO_MAP[tag]
    elif MAPTAG == 'TEST':
        return TEST_MAP[tag]
    elif MAPTAG == 'PLO_TEST':
        return TEST_PLO_MAP[tag]
    else:
        return TAG_MAP[tag]

if __name__ == "__main__":
    words = []
    tags = []
    startSentence = {}
    endSentence = {}
    quotes = {}
    #cap = {}

    DATA_DIR = sys.argv[1]
    TRAIN_OUT = open(sys.argv[2], 'w')
    TEST_OUT = open(sys.argv[3], 'w')
    N_TRAIN = int(sys.argv[4])
    FEATURES = sys.argv[5]
    MAPTAG = sys.argv[6]

    project_name = DATA_DIR.rstrip('/').split('/')[-1]
    print project_name

    #Read in the words
    #for line in open(DATA_DIR + "/mmax_ner_words.xml"):
    for line in open(DATA_DIR + "/%s_words.xml" % (project_name)):
        line = line.rstrip('\n')
        m = re.match(r'<word id="word_(\d+)">([^>]+)</word>', line)
        if m:
            words.append(m.group(2))
            #if(m.group(2)[0] == '@'):
            if False:
                tags.append("B-ENTITY")
            else:
                tags.append("O")
            #words[int(m.group(1))] = m.group(2)
            #tags[int(m.group(1))] = "O"

    #Read in the tags
    #for line in open(DATA_DIR + "/mmax_ner_NER_level.xml"):
    for line in open(DATA_DIR + "/%s_NER_level.xml" % (project_name)):
        line = line.rstrip('\n')
        m = re.match(r'<markable id="markable_(\d+)" span="word_(\d+)(?:\.\.|,)word_(\d+)" mmax_level="[^"]+"  tag="([^"]+)" />', line)
        if m:
            start = int(m.group(2))-1
            end = int(m.group(3))-1
            
            #print "%s\t%s\t%s\t%s" % (end-start, start, end, line)

            if m.group(4) == 'entity':
                print line
            tags[start] = "B-%s" % mapTag(m.group(4))
            for i in range(start+1, end+1):
                if USE_TAGS:
                    tags[i] = "I-%s" % mapTag(m.group(4))
                else:
                    tags[i] = "I-ENTITY"
            continue

        m = re.match(r'<markable id="markable_(\d+)" span="word_(\d+)" mmax_level="[^"]+"  tag="([^"]+)" />', line)
        if m:
            if USE_TAGS:
                tags[int(m.group(2))-1] = "B-%s" % mapTag(m.group(3))
            else:
                tags[int(m.group(2))-1] = "B-ENTITY"

    #Read in the sentences, and get output of capitalization classifier
    #cap_classifier = subprocess.Popen('python/cap/cap_classify data/cap/tweets_cap_labeled.csv.model',
    #                                  shell=True,
    #                                  stdin=subprocess.PIPE,
    #                                  stdout=subprocess.PIPE)
    #for line in open(DATA_DIR + "/mmax_ner_sentence_level.xml"):
    for line in open(DATA_DIR + "/%s_sentence_level.xml" % (project_name)):
        line = line.rstrip('\n')
        m = re.match(r'<markable id="markable_(\d+)" span="word_(\d+)..word_(\d+)" mmax_level="[^"]+" />', line)
        if m:
            start = int(m.group(2))-1
            end = int(m.group(3))

            q = Features.GetQuotes(words[start:end])
            #sys.stderr.write(str(words[start:end]) + "\n") 
            #sys.stderr.write(str(q) + "\n")
            for i in range(len(q)):
                if q[i]:
                    quotes[start + i] = 1

            startSentence[start] = end
            endSentence[end-1] = 1

    sentences      = [words[i:startSentence[i]] for i in startSentence.keys()]
    sentenceTags   = [tags[i:startSentence[i]] for i in startSentence.keys()]
    posChunk       = Tag(sentences)

    #Print out the data
    #posTagger = pos_tagger_stdin.PosTagger()
    capClassifier = cap_classifier.CapClassifier()
    if "NOBROWN" in FEATURES:
        fe = Features.FeatureExtractor("data/dictionaries", None)
    else:
        fe = Features.FeatureExtractor("data/dictionaries")
    nSentences = 0
#    for i in range(len(words)):
#        if startSentence.has_key(i):
#            sentenceWords = words[i:startSentence[i]]
    for sentenceWords in sentences:
            if "NOPOS" in FEATURES:
                pos = None
            elif "NEWSPOS" in FEATURES:
                pos = [x[1] for x in nltk.pos_tag(sentenceWords)]
            else:
                #pos = posTagger.TagSentence(sentenceWords)
                pos = [x[1] for x in posChunk[nSentences]]

            if "NOCAP" in FEATURES:
                goodCap = None
            else:
                goodCap = capClassifier.Classify(sentenceWords) > 0.9

            if "NOCHUNK" in FEATURES:
                chunk = None
            else:
                chunk = [x[2] for x in posChunk[nSentences]]

            for j in range(len(sentenceWords)):
                features = fe.Extract(sentenceWords, pos, chunk, j, goodCap) + ['DOMAIN=Twitter']

                if quotes.has_key(i+j):
                    features.append("QUOTED")
                if nSentences > N_TRAIN:
                    TEST_OUT.write(" ".join(features) + " %s" % sentenceTags[nSentences][j] + "\n")
                else:
                    TRAIN_OUT.write(" ".join(features) + " %s" % sentenceTags[nSentences][j] + "\n")

            if nSentences > N_TRAIN:
                TEST_OUT.write("\n")
            else:
                TRAIN_OUT.write("\n")
            nSentences += 1
            
