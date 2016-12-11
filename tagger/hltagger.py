# hltagger.py
# Daniel Kauffman

import copy
import glob
import regex
import string
import re

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
                tokens = nltk.word_tokenize(prev.text)
                pos_tags = [tag for _, tag in
                            nltk.pos_tag(tokens, tagset = "universal")]
                n_real = [en_dict.check(token)
                          for token in tokens if not token.isdigit()].count(True)
                if row.function == "BL" and n_real > 1:
                    matched.append(prev)
                else:
                    non_alphabetic = re.sub(r"[A-Za-z\ ]+", "", str(prev.text))
                    all_uppercase_words = [token for token in tokens
                                           if token and token.isupper()]
                    title_words = [token for token in tokens
                                   if token and token[0].isupper()]
                    punctuation = re.findall(r"\*|\"|\,", prev.text)

                    is_hl = (len(tokens) > 1 and len(tokens) < 10 and
                             len(prev.text) < 70 and
                             n_real > 3 and n_real < 10 and
                             (len(tokens) - n_real) <= 2 and
                             len(non_alphabetic) <= 2 and
                             not len(all_uppercase_words) and
                             len(title_words) <= 2 and
                             (tokens and tokens[0].istitle()) and
                             not punctuation and
                             pos_tags.count("NOUN") >= 3 and
                             pos_tags.count("VERB") <= 2 and
                             not pos_tags.count("DET") and
                             not pos_tags.count("PRON"))
                    if is_hl:
                        matched.append(prev)
    return pd.DataFrame(matched)


if __name__ == "__main__":
    main()
