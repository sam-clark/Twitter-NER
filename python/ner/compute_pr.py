#!/usr/bin/python

import sys
import re

############################################################################################
# For computing P/R of cap_extract.py
############################################################################################

goldEntity      = None
predictedEntity = None

tp = 0
fp = 0
fn = 0
tn = 0

type_tp = {}
type_fn = {}
type_fp = {}

confusion_matrix = {}

inFile = None
if len(sys.argv) > 1:
    inFile = open(sys.argv[1])

TYPE_MAP = {
    'per':'PERSON',
    'org':'ORGANIZATION',
    'loc':'LOCATION',
}

def MapType(t):
    if TYPE_MAP.has_key(t):
        return TYPE_MAP[t]
    else:
        return t

i = 0
goldType = None
predictedType = None
for line in sys.stdin:
    line = line.rstrip('\n').rstrip(' ')
    fields = re.split(r'\s', line)

    if(len(fields) < 2):
        continue

    if re.match('\s', line):
        gold      = 'O'
        predicted = 'O'
    else:
        if inFile:
            l2 = inFile.readline().rstrip('\n')
            if l2 == "":
                l2 = inFile.readline().rstrip('\n')
            gold = l2.split(' ')[-1]
        else:
            gold = fields[-1]
        predicted = fields[-2]
#            gold = fields[-2]
#        predicted = fields[-1]

    print "%s\t%s" % (gold, predicted)

    ge = None
    pe = None
    
    if (gold[0] == 'B' or (gold[0] != 'O' and gold[0] != 'I')) and not goldEntity:
        goldEntity = [i]
        goldType = gold[2:]
    elif gold[0] == 'I' or (gold[0] != 'O'):
        goldEntity.append(i)
    elif gold[0] == 'O' and goldEntity:
        ge = ' '.join([str(x) for x in goldEntity])
        goldEntity = None
    elif gold[0] == 'B' and goldEntity:
        ge = ' '.join([str(x) for x in goldEntity])
        goldType = gold[2:]
        goldEnity = [i]

#    print "%s\t%s\t%s" % (fields[0], predicted[0], str(pe))
    if (predicted[0] == 'B' or (predicted != 'O' and predicted[0] != 'I')) and not predictedEntity:
        predictedEntity = [i]
        #predictedType = predicted.split(':')[0]
        predictedType = predicted
    elif predicted[0] == 'I' or (predicted != 'O'):
        predictedEntity.append(i)
    elif predicted == 'O' and predictedEntity:
        pe = ' '.join([str(x) for x in predictedEntity])
        predictedEntity = None
    elif predicted[0] == 'B' and predictedEntity:
        pe = ' '.join([str(x) for x in predictedEntity])
        #predictedType = predicted.split(':')[0]
        predictedType = predicted
        predictedEntity = [i]

    predicted = re.sub(r':.*$', '', predicted)

    if ge:
#        print ">>>%s\t%s" % (ge, pe)
#        if predictedType and goldType:
#            print ">>> %s\t%s" % (MapType(goldType), predictedType)
        if pe and pe == ge and (goldType == 'ENTITY' or MapType(goldType) == predictedType):
            type_tp[goldType] = type_tp.get(goldType,0) + 1
            confusion_matrix["%s\t%s" % (MapType(goldType), predictedType)] = confusion_matrix.get("%s\t%s" % (MapType(goldType), predictedType),0) + 1
            tp += 1
        else:
            type_fn[MapType(goldType)] = type_fn.get(MapType(goldType),0) + 1
            fn += 1
        print ">>> tp=%s\tfp=%s\tfn=%s" % (tp, fp, fn)
    
    if (pe and predictedType != 'MISC') and (pe != ge or (MapType(goldType) != predictedType and goldType != 'ENTITY' and predictedType != 'NONE')):
#        print ">>>%s\t%s" % (pe, ge)
#        print ">>>%s\t%s" % (goldType, predictedType)
        fp += 1
        print ">>> tp=%s\tfp=%s\tfn=%s" % (tp, fp, fn)


    if ge:
        ge = None
    if pe:
        pe = None

    i += 1

print "Confusion Matrix"
goldTypes = list(set([x.split('\t')[0] for x in confusion_matrix.keys()]))
predictedTypes = list(set([x.split('\t')[1] for x in confusion_matrix.keys()]))
allTypes = list(set(goldTypes + predictedTypes))

print goldTypes
print predictedTypes

print "\\begin{tabular}{|%s|}" % '|'.join(['l' for x in range(len(allTypes) + 1)])
print '\hline'
print " & " + " & ".join([x[0:5] for x in allTypes]) + "\\\\"
print '\hline'
print '\hline'
type_correct = 0
type_wrong = 0
for g in allTypes:
    sys.stderr.write('%s' % g)
    for p in allTypes:
        pg_count = confusion_matrix.get("%s\t%s" % (g,p), 0)
        if p == g:
            type_correct += pg_count
        else:
            type_wrong += pg_count
        sys.stderr.write(' & %s' % pg_count)
    print "\\\\"
    print '\hline'
print "\end{tabular}"
print "type accuracy:"
print float(type_correct) / float(type_correct + type_wrong)
print


print "Segmentation Recall:"
for t in allTypes:
    if (type_tp.get(t,0) + type_fn.get(t,0)) == 0:
        r = 0
    else:
        r = float(type_tp.get(t,0)) / float(type_tp.get(t,0) + type_fn.get(t,0))
    print "%s & %s \\\\" % (t, r)
print

print "Overall PR (no type)"
print "%s\t%s\t%s\t%s" % (tp, tn, fp, fn)

p = float(tp) / float(tp + fp)
r = float(tp) / float(tp + fn)
f = 2 * p * r / (p + r)

print "P:%s\nR:%s\nF:%s" % (p,r,f)
