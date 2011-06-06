#!/bin/bash

OUTDIR=$1
echo $OUTDIR

python python/ner/mmax2mallet.py data/ner/tweets/typed_entities2/mmax_ner $OUTDIR/train $OUTDIR/dev 750 $2 $3
python python/ner/mmax2mallet.py data/ner/tweets/typed_entities2/mmax_ner2 $OUTDIR/train2 $OUTDIR/test 750 $2 $3

cat $OUTDIR/train $OUTDIR/train2 > $OUTDIR/train.both
rm $OUTDIR/train
mv $OUTDIR/train.both $OUTDIR/train
