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


def find_unique_pos_groups(size = 2):
    hls = set(basetagger.create_tag_pattern("HL").split("|"))
    txts = set(basetagger.create_tag_pattern("TXT").split("|"))
    hl_patterns = []
    for hl in hls:
        split = hl.split()
        if len(split) > size - 1:
            for i in range(len(split) - size - 1):
                hl_patterns.append(" ".join(split[i:i + size]))
    txt_patterns = []
    for txt in txts:
        split = txt.split()
        if len(split) > size - 1:
            for i in range(len(split) - size - 1):
                txt_patterns.append(" ".join(split[i:i + size]))
    hl_set = set(hl_patterns) - set(txt_patterns)
    txt_set = set(txt_patterns) - set(hl_patterns)
    return (hl_set, txt_set)


def find_headline(issue):
    MAX_HEADLINE_LEN = 10
    en_dict = enchant.Dict("en_US")
    matched = []
    _, txt_set = find_unique_pos_groups(size = 2)
    for i, row in issue.iterrows():
        if i > issue.index.min():
            prev = issue.loc[i - 1]
            is_valid = pd.isnull(prev.function) and \
                       pd.notnull(prev.text) and \
                       "." not in prev.text
            if is_valid:
                tokens = nltk.word_tokenize(prev.text)
                all_pos_tags = [tag for _, tag in nltk.pos_tag(tokens)]
                has_txt_pat = any([pattern in " ".join(all_pos_tags)
                                       for pattern in txt_set])
                txt_only = ["EX", "NNPS", "("]
                

                if not set(all_pos_tags) & set(txt_only) and not has_txt_pat:
                    pos_tags = [tag for _, tag in
                                nltk.pos_tag(tokens, tagset = "universal")]
                    n_real = [en_dict.check(token.lower())
                              for token in tokens
                              if not token.isdigit() and len(token) > 1].count(True)
                    all_uppercase_words = [token for token in tokens
                                           if token and token.isupper()]

                    # Ensure titles are within a certain size.
                    if (len(tokens) < 1 or len(tokens) >= MAX_HEADLINE_LEN or
                        n_real <= 1 or len(prev.text) > 70):
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
                        is_hl_generic = ((len(tokens) - n_real) <= 2 and
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
