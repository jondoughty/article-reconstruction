# hltagger.py
# Daniel Kauffman

import copy
import glob
import pprint
import regex
import string

import nltk
import pandas as pd

import tagger.basetagger as basetagger


def main():
    basetagger.measure_precision_recall("HL", tag)


def tag(issue):
    issue = copy.deepcopy(issue)
    matched = pd.concat([find_headline(issue.tags_df)])
    matched = matched.drop_duplicates().sort_index()
    for i, row in matched.iterrows():
        if issue.tags_df.loc[i].function is None:
            issue.tags_df.set_value(i, "function", "HL")
    return issue


def remove_punctuation(text):
#    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
#    return text.translate(table).strip().upper()
    replaced = regex.sub("[^{0}]".format("\s:"), "", text)
    replaced = regex.sub("[^{0}]".format(string.ascii_letters + string.digits),
                         " ", text)
    return replaced.upper()


def find_headline(issue):
    matched = []
    for i, row in issue.iterrows():
        if i > issue.index.min():
            prev = issue.loc[i - 1]
            if pd.notnull(prev.text):
                tokens = nltk.word_tokenize(prev.text)
                if len(tokens) > 1 and len(tokens) < 10:
                    pos_tags = [pos for _, pos in nltk.pos_tag(tokens, tagset = "universal")]
                    is_hl = (pd.isnull(prev.function) or \
                             prev.function not in ["PI", "BL"]) and \
                            "." not in prev.text and len(prev.text) < 80 and \
                            pos_tags[0] == "NOUN" and pos_tags.count("NOUN") > 1
#                            (row.function == "BL")
                    if is_hl:
                        matched.append(prev)
    return pd.DataFrame(matched)


def get_pos_patterns():
    paths = glob.glob("tagged_data/*.csv")
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]
    hl_pos_sent_list = []
    txt_pos_sent_list = []
    for path in paths:
        issue = pd.read_csv(path, header = 2, names = columns)
        issue = issue.dropna(how = "all")
        for _, row in issue.iterrows():
            if pd.notnull(row.text):
                if row.function == "HL" or row.function == "TXT":
                    tokens = nltk.word_tokenize(row.text)
                    if len(tokens) < 10:
                        pos_tags = nltk.pos_tag(tokens, tagset = "universal")
                        if row.function == "HL":
                            hl_pos_sent_list.append([pos for _, pos in pos_tags])
                        elif row.function == "TXT":
                            txt_pos_sent_list.append([pos for _, pos in pos_tags])
    pprint.pprint(dict(nltk.FreqDist(tuple(pos) for pos in hl_pos_sent_list).most_common(40)))
    print("\n")
    pprint.pprint(dict(nltk.FreqDist(tuple(pos) for pos in txt_pos_sent_list).most_common(40)))


if __name__ == "__main__":
    main()
