# hltagger.py
# Daniel Kauffman

import copy
import glob
import regex
import string

import enchant
import nltk
import numpy as np
import pandas as pd

import tagger.basetagger as basetagger


def main():
    basetagger.measure_precision_recall("HL", tag, limit = 5)


def tag(issue, test = False):
    issue = copy.deepcopy(issue)
    if test:
        all_tags = "|".join(t for t in issue.tags_df.function.unique()
                              if pd.notnull(t) and t not in ["PI", "BL"])
        pattern = r"^(?:{0})$".format(all_tags)
        issue.tags_df.function = issue.tags_df.function.replace(pattern, np.NaN,
                                                                regex = True)
    matched = pd.concat([find_headline(issue.tags_df)])
    if len(matched) > 0:
        matched = matched.drop_duplicates().sort_index()
        for i, row in matched.iterrows():
            if pd.isnull(issue.tags_df.loc[i].function):
                issue.tags_df.set_value(i, "function", "HL")
    return issue


def remove_punctuation(text):
    replaced = regex.sub("[^{0}]".format("\s:"), "", text)
    replaced = regex.sub("[^{0}]".format(string.ascii_letters + string.digits),
                         " ", text)
    return replaced.upper()


def find_headline(issue):
    en_dict = enchant.Dict("en_US")
    matched = []
    for i, row in issue.iterrows():
        if i > issue.index.min():
            prev = issue.loc[i - 1]
            is_valid = pd.isnull(prev.function) and \
                       pd.notnull(prev.text) and \
                       "." not in prev.text
            if is_valid:
                if row.function == "BL":
                    matched.append(prev)
                else:
                    tokens = nltk.word_tokenize(prev.text)
#                    pos_tags = [tag for _, tag in
#                                nltk.pos_tag(tokens, tagset = "universal")]
                    n_real = [en_dict.check(token)
                              for token in tokens].count(True)
                    is_hl = len(tokens) > 1 and len(tokens) < 10 and \
                            len(prev.text) < 80 and \
                            n_real / len(tokens) > 0.5 and \
                            not any(c.isdigit for c in prev.text)
                    if is_hl:
                        matched.append(prev)
    return pd.DataFrame(matched)


if __name__ == "__main__":
    main()
