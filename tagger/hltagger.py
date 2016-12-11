# hltagger.py
# Daniel Kauffman

import copy
import glob
import regex
import string

import nltk
import numpy as np
import pandas as pd

import tagger.basetagger as basetagger


def main():
    basetagger.measure_precision_recall("HL", tag, limit = 30)


def tag(issue, test = False):
    issue = copy.deepcopy(issue)
    if test:
        all_tags = "|".join(t for t in issue.tags_df.function.unique()
                              if pd.notnull(t) and t not in ["PI", "BL"])
        pattern = r"^(?:{0})$".format(all_tags)
        issue.tags_df.function = issue.tags_df.function.replace(pattern, np.NaN,
                                                                regex = True)
    matched = pd.concat([find_headline(issue.tags_df)])
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
    matched = []
    for i, row in issue.iterrows():
        if i > issue.index.min():
            prev = issue.loc[i - 1]
            is_valid = pd.isnull(prev.function) and \
                       pd.notnull(prev.text) and \
                       "." not in prev.text
            if is_valid and row.function == "BL":
                matched.append(prev)
    return pd.DataFrame(matched)


if __name__ == "__main__":
    main()
