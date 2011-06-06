#!/homes/gws/aritter/local/bin/python

###############################################################################
# Library for extracting various types of features
###############################################################################
import os
import re

import symbol_tag

class POSFeatureExtractor:
    def __init__(self, token2pos_dir, token_dir, bigram_dir=None):
        # Dictionaries with POS information
        self.dictionaries = {} 
        for dict_name in os.listdir(token2pos_dir):
            if dict_name == '.svn':
                continue
            dict_file = os.path.join(token2pos_dir, dict_name)
            self.dictionaries[dict_name] = Dictionary(dict_file, True)
        # Dictionaries with random info about tokens
        self.occurences = {}
        for dict_name in os.listdir(token_dir):
            if dict_name == '.svn':
                continue
            dict_file = os.path.join(token_dir, dict_name)
            self.occurences[dict_name] = Dictionary(dict_file, False)
        # Dictionaries with bigram information
        self.bigram_dictionaries = {} 
        if bigram_dir:
            for dict_name in os.listdir(bigram_dir):
                if dict_name == '.svn':
                    continue
                dict_file = os.path.join(bigram_dir, dict_name)
                self.bigram_dictionaries[dict_name] = Dictionary(dict_file,
                                                                 True)

    def get_features(self, token, use_dicts=True, use_cap=True, use_num=True,
                     use_prefix='PREFIX=', use_suffix='SUFFIX=',
                     use_major_pos=True, diction_avail=False,
                     new_maj=True, all_caps=True, new_dictions=True,
                     use_domain_transfer=False, dt_label='TARG',
                     use_symbol_tag=True, lim_suffix=True,
                     new_ortho=True, lim_tags=True):
        ltoken = token.lower()
        feature_list = [ltoken]

        # First off, if it looks like it's a RT, HT, USR, or URL don't
        # add any features but the symbol tags
        # Get potential symbol tags
        if use_symbol_tag:
            pos = symbol_tag.tag_token(ltoken)
            if pos:
                feature_list.append('SYMBOL_REGX=' + str(pos))        
            if lim_tags and pos in ['usr', 'rt', 'ht', 'url']:
                return ['SYMBOL_REGX=' + str(pos)]

        # Use the dictionaries to see what common tags exist
        if use_dicts:
            dictionary_list = []
            for dict_name, dictionary in self.dictionaries.iteritems():
                if ltoken in dictionary.token_pos_set:
                    # Record all POS tags the token has been seen with
                    pos_set = dictionary.token_pos_set[ltoken]
                    for pos in pos_set:
                        feature_list.append(dict_name + '=' + pos)
                    # Record if it has only been seen with one
                    if len(pos_set) == 1:
                        feature_list.append(dict_name + '_ONLY=' + pos)
                    # Record the majority POS tag
                    if use_major_pos:
                        if not new_maj:
                            major = dictionary.token_pos_majority[ltoken]
                            feature_list.append(dict_name + '_MAJORITY=' 
                                                + major)
                        else:
                            # Make sure the majority is a real majority
                            pos_l = [(count, pos) for pos, count
                                     in pos_set.items()]
                            pos_l.sort()
                            pos_l.reverse()
                            # If one tag and count greater than 1
                            if len(pos_l) == 1 and pos_l[0][0] > 1:
                                feature_list.append(dict_name + '_MAJORITY='
                                                    + pos_l[0][1])
                            elif len(pos_l) > 1 and (pos_l[0][0] > 
                                                     1.5*pos_l[1][0]):
                                feature_list.append(dict_name + '_MAJORITY='
                                                    + pos_l[0][1])
                            
                    # Record that dictionary found something
                    dictionary_list.append(dict_name)

            # Record which dictionaries the token is found int
            if diction_avail:
                if not dictionary_list:
                    feature_list.append('NOT_IN_DICTS')
                elif len(dictionary_list) > 1:
                    feature_list.append('IN_MULTIPLE_DICTS')
                else:
                    feature_list.append('ONLY_IN=' + dictionary_list[0])

        # Check if the token occurs in new dictionaries
        if new_dictions:
            for dictname, dictionary in self.occurences.iteritems():
                if ltoken in dictionary.token_pos_set:
                    feature_list.append(dictname)

        # Get basic reg expression features
        # Check if the token is all caps and no symbols
        if all_caps:
            if len(token) > 1 and re.match('^[A-Z]*$', token):
                feature_list.append('ALL_CAPS')

        # Check if the token is capitalized  
        if re.match('[A-Z]', token[0]):
            feature_list.append('IS_CAPITALIZED')
        elif not new_ortho:
            feature_list.append('IS_LOWERCASE')

        # Check if the token contains a number 
        if re.match('.*[0-9].*', token):
            feature_list.append('IS_NUM')
        elif not new_ortho:
            feature_list.append('NOT_NUM')

        # New ortho features
        if new_ortho:
            if re.match(r'[0-9]', token):
                feature_list.append('SINGLEDIGIT')
            if re.match(r'[0-9][0-9]', token):
                feature_list.append('DOUBLEDIGIT')
            if re.match(r'.*-.*', token):
                feature_list.append('HASDASH')
            if re.match(r'[.,;:?!-+\'"]', token):
                feature_list.append('PUNCTUATION')


        # Only for words with 4 or longer chars
        if (not lim_suffix) or len(ltoken) >= 4:
            # Get prefixes
            for i in range(1, 5):
                if i <= len(ltoken):
                    feature_list.append(use_prefix + ltoken[:i])
            # Get suffixes                            
            for i in range(1, 5):
                if i <= len(ltoken):
                    feature_list.append(use_suffix + ltoken[-1*i:])

        # Modify features for domain transfer if necessary
        if use_domain_transfer:
            return create_dt_features(feature_list, dt_label)
        else:
            return feature_list

    def add_bigram_features(self, current_feature_list, prefix_list=[],
                            remove_pos=True):
        new_current_feature_list = []
        for i in range(len(current_feature_list)):
            feature_list = current_feature_list[i]
            if remove_pos:
                last_feature = feature_list.pop()  # Remove the POS tag
            current_word = _clean_word(feature_list[0], prefix_list)
            if i > 0:
                before_word = _clean_word(current_feature_list[i - 1][0],
                                          prefix_list)
                feature_list.extend(self._check_bigrams(before_word,
                                                        current_word,
                                                        False))
            if i < len(current_feature_list) - 1:
                after_word = _clean_word(current_feature_list[i + 1][0],
                                         prefix_list)
                feature_list.extend(self._check_bigrams(current_word,
                                                        after_word,
                                                        True))
            if remove_pos:
                feature_list.append(last_feature)
            new_current_feature_list.append(feature_list)
        return new_current_feature_list

    def _check_bigrams(self, word1, word2, use_first):
        bigram = word1 + '_' + word2
        new_features = []
        for dict_name, d in self.bigram_dictionaries.iteritems():
            if bigram in d.token_pos_set:
                tag1, tag2 = d.token_pos_set[bigram].items()[0][0].split('_')
                tag = (use_first and tag1) or tag2
                ttype = (use_first and 'AFTER') or 'BEFORE'
                new_features.append(dict_name + '_BIGRAM_' + ttype + '_' + tag)
        return new_features

def _clean_word(word, prefix_list):
    new_word = word
    for prefix in prefix_list:
        new_word = re.sub(prefix, '', new_word)
    return new_word

def add_context_features(current_feature_list, spec_toks=False, window=0):
    new_current_feature_list = []
    for i in range(len(current_feature_list)):
        feature_list = current_feature_list[i]
        if spec_toks:
            check_context(current_feature_list, i - 1, 'PREV_TWIT',
                          feature_list)
            check_context(current_feature_list, i + 1, 'NEXT_TWIT',
                          feature_list)
        # Won't find windows for special characters
        if window > 0 and feature_list[0].lstrip('SYMBOL_REGX=') not in \
                ['url', 'usr', 'ht', 'rt']:
            window_context(current_feature_list, max(i - window, 0), i, 'PWIN',
                           feature_list)
            window_context(current_feature_list, i + 1, i + window + 1, 'NWIN',
                           feature_list)

        new_current_feature_list.append(feature_list)
    return new_current_feature_list

def check_context(current_feature_list, index, ctype, feature_list):
    if index < 0 or index >= len(current_feature_list):
        return
    cont_feature_list = current_feature_list[index]
    if 'SYMBOL_REGX=usr' in cont_feature_list:
        feature_list.insert(-1, ctype + '=USR')
    if 'SYMBOL_REGX=url' in cont_feature_list:
        feature_list.insert(-1, ctype + '=URL')
    if 'SYMBOL_REGX=rt' in cont_feature_list:
        feature_list.insert(-1, ctype + '=RT')

def window_context(current_feature_list, si, ei, ctype, feature_list):
    for cont_feature_list in current_feature_list[si:ei]:
        feature_list.insert(-1, ctype + '=' + cont_feature_list[0])

class Dictionary:
    def __init__(self, dictionary_file, has_tags):
        self.token_pos_set = {}
        self.token_pos_majority = {}
        for line in open(dictionary_file):
            if has_tags:
                tp_list = line.strip().split('\t')
                pos_counts = {}
                max_count = None
                max_pos = None
                for tp in tp_list[1:]:
                    pos, count = tp.split(';;')
                    count = int(count)
                    pos_counts[pos] = count
                    if not max_count or max_count < count:
                        max_count = count
                        max_pos = pos
                self.token_pos_set[tp_list[0]] = pos_counts
                self.token_pos_majority[tp_list[0]] = max_pos
            else:
                self.token_pos_set[line.strip()] = 1

def create_dt_features(feature_list, data_src):
    new_feature_list = []
    new_feature_list.extend(['DEFAULT=' + ft for ft in feature_list[:-1]])
    new_feature_list.extend([data_src + '=' + ft for ft in feature_list[:-1]])
    new_feature_list.append(feature_list[-1])
    return new_feature_list

# Sample usage
_token2pos = ('/home/ssclark/stable_twitter_nlp/data/'
               'pos_dictionaries/token2pos')
_token = '/home/ssclark/stable_twitter_nlp/data/pos_dictionaries/token'
_bigram = '/home/ssclark/stable_twitter_nlp/data/pos_dictionaries/bigram'

if __name__ == '__main__':
    mfe = POSFeatureExtractor(_token2pos, _token, _bigram)
    feat_list = []
    temp1 = mfe.get_features('I')
    feat_list.append(temp1)
    temp2 = mfe.get_features('get')
    feat_list.append(temp2)
    temp3 = mfe.get_features('you')
    feat_list.append(temp3)
    for features in mfe.add_bigram_features(feat_list, ['DEFAULT=', 'TARG=']):
        print features
