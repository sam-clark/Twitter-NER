#!/homes/gws/aritter/local/bin/python

###############################################################################
# Evaluate how well a Yamcha model predicts test values.
###############################################################################

import yamcha_wrapper

"""
MODEL_PATH = ('/home/ssclark/YamchaModels/'
              'ExtraFeaturesMediumSize/model_name.model')
TEST_FILE = ('/home/ssclark/YamchaModels/'
              'ExtraFeaturesMediumSize/ptb_extra_medium_test.txt')
"""

#MODEL_PATH = '/home/ssclark/YamchaModels/NpsChat/model_name.model'
MODEL_PATH = '/home/ssclark/YamchaModels/combination_model_small/model_name.model'
TEST_FILE = '/home/ssclark/YamchaModels/NpsChat/nps_small_test.txt'


# Note: WSJ model gets 57% accuracy on chat, 95% accuracy on itself.
# Note: 10K WSJ + 1K NPS -> 71.7% accuracy on chat
# Note: 50K WSJ + 5K NPS -> 83.3% accuracy on chat

def eval(model_path, test_file):
    # Load pos tagger model
    pos_tagger = yamcha_wrapper.YamchaWrapper(model_path, None, None)
    total_correct, total_tags = run_model(pos_tagger, test_file)
    print 'Overall:'
    print_results(total_correct, total_tags)


def run_model(model, test_file):

    # Test model on held out data
    sentence = []
    true_tags = []
    total_tags = 0
    total_correct = 0
    for line in open(test_file):
        line = line.strip()
        if not line and not sentence:
            continue
        elif not line:
            output_tags = model.get_POS_tags(sentence)

            # Check that the tags were correct
            for index, tp in enumerate(output_tags):
                total_tags += 1
                if tp[-1] == true_tags[index]:
                    total_correct += 1
                # Keep track of progress
                if total_tags % 100 == 0:
                    print_results(total_correct, total_tags)
            sentence = []
            true_tags = []
        else:
            # Record tags and features
            tpl = line.split(' ')
            sentence.append(tuple(tpl[:-1]))
            true_tags.append(tpl[-1])
    return total_correct, total_tags


def print_results(total_correct, total_tags):
    print "%d / %d = %s" % (total_correct, total_tags,
                            "%.3f" % (float(total_correct) / total_tags))

if __name__ == '__main__':
    eval(MODEL_PATH, TEST_FILE)
