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
#    hl_pos, txt_pos = basetagger.find_unique_pos_tags("HL", "TXT")
    basetagger.measure_precision_recall("HL", tag)#, limit = 5)


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
    MAX_HEADLINE_LEN = 10
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
                all_pos_tags = set([tag for _, tag in nltk.pos_tag(tokens)])
#                hl_only = set(["FW", "UH", "JJS"])
                txt_only = set(["EX", "NNPS", "("])

                if not all_pos_tags & txt_only:
                    pos_tags = [tag for _, tag in
                                nltk.pos_tag(tokens, tagset = "universal")]
                    n_real = [en_dict.check(token)
                              for token in tokens if not token.isdigit()].count(True)
                    all_uppercase_words = [token for token in tokens
                                           if token and token.isupper()]

                    # Titles have to have minimum one token.
                    if not tokens or not pos_tags:
                        pass
                    # Titles have less than MAX_HEADLINE_LEN and 1 real word.
                    elif len(tokens) >= MAX_HEADLINE_LEN or n_real <= 1:
                        pass
                    # Titles have less than 3 all uppercase words.
                    elif len(all_uppercase_words) >= 4:
                        pass
                    # Titles cannot end with "CONJ".
                    elif pos_tags[-1] == "CONJ":
                        pass
                    # Titles do not have more than one punctuation.
                    elif pos_tags.count(".") > 2:
                        pass
                    # Likely a title if previous row is BL.
                    elif row.function == "BL":
                        matched.append(prev)
                    else:
                        non_alphabetic = re.sub(r"[A-Za-z\ ]+", "", str(prev.text))
                        title_words = [token for token in tokens
                                       if token and token[0].isupper()]
                        punctuation = re.findall(r"\*|\"|\,", prev.text)

                        # Gets a subset of the headlines.
                        is_hl_generic = (len(tokens) > 1 and len(tokens) < MAX_HEADLINE_LEN and
                                         len(prev.text) < 70 and
                                         (len(tokens) - n_real) <= 2 and
                                         len(non_alphabetic) <= 2 and
                                         (tokens and tokens[0].istitle()) and
                                         not punctuation and
                                         pos_tags.count("NOUN") >= 3 and
                                         pos_tags.count("VERB") <= 2 and
                                         not pos_tags.count("DET") and
                                         not pos_tags.count("PRON"))

                        if is_hl_generic:
                            if (n_real > 3 and n_real < 10 and
                                not len(all_uppercase_words) and
                                len(title_words) <= 2):
                                matched.append(prev)
                            elif (n_real > 1 and n_real < 10 and
                                  len(all_uppercase_words) <= 1 and
                                  len(title_words) / len(tokens) <= 0.5 and
                                  not pos_tags.count("PRT") and
                                  not pos_tags.count("ADP")):
                                matched.append(prev)
    return pd.DataFrame(matched)


if __name__ == "__main__":
    main()
