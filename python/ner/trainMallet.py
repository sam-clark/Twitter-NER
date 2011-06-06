#!/usr/bin/python

import sys
import os

os.system("/usr/local/bin/java -Xmx1400m -cp /homes/gws/aritter/mallet-2.0.6/lib/mallet-deps.jar:/homes/gws/aritter/mallet-2.0.6/dist/mallet.jar cc.mallet.fst.SimpleTagger --train true --gaussian-variance 10.0 --iterations 200  --feature-induction false --orders 1 --model-file %s %s" % (sys.argv[1], sys.argv[2]))
