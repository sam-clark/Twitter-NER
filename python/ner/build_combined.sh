#!/bin/bash

OUTPUTDIR=$1
echo $OUTPUTDIR

python python/ner/muc2mallet.py data/ner/muc_7/data/training.ne.eng.keys.980205 > data/ner/muc_7/muc_7.mallet
python python/ner/muc2mallet.py data/ner/muc_6/MOD/muc6/data/keys/dryrun-trng.NE-combined.key.v1.3.clean > data/ner/muc_6/muc_6.mallet
cat data/ner/muc_7/muc_7.mallet data/ner/muc_6/muc_6.mallet | python python/ner/easyadapt.py > $OUTPUTDIR/combined_train
cat $OUTPUTDIR/train >> $OUTPUTDIR/combined_train
