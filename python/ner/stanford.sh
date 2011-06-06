cat test | perl -nle 'split / /; if (@_ > 0) {print pwd[0] pwd[0_]} else {print};' | sed 's/^word=//' > test.stanford
java -cp stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier classifiers/ner-eng-ie.crf-3-all2008-distsim.ser.gz -testFile ~/twitter_nlp/experiments/newpos/test.stanford > ~/twitter_nlp/experiments/newpos/stanford.predictions

