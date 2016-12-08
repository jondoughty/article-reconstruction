# hltagger.py
# Daniel Kauffman

import copy
import glob
import pprint
import regex
import string

import pandas as pd

from tagger.basetagger import *


def main():
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
#    get_pos_patterns()
#    return
    paths = glob.glob("tagged_data/*.csv")
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]
    content_tags = ["BL", "TXT"]
    tp = fp = fn = 0
    for path in paths:
        issue = pd.read_csv(path, header = 2, names = columns)
        issue = issue.dropna(how = "all")
        issue = tag(issue, test = True).join(issue.function, rsuffix = "_act")
        tp += len(issue[(issue.function_act == "HL") &
                        (issue.function == "HL")])
        fp += len(issue[(issue.function_act.isin(content_tags)) &
                        (issue.function == "HL")])
        fn += len(issue[(issue.function_act == "HL") &
                        (issue.function != "HL")])
        print("\n\nTrue Positives:")
        print(issue[(issue.function_act == "HL") &
                    (issue.function == "HL")])
        print("\n\nFalse Positives:")
        print(issue[(issue.function_act.isin(content_tags)) &
                    (issue.function == "HL")])
        print("\n\nFalse Negatives:")
        print(issue[(issue.function_act == "HL") &
                    (issue.function != "HL")])
        print("\n\n\n")
    print("Precision", tp / (tp + fp))
    print("Recall", tp / (tp + fn))


def tag(issue, test = False):
    issue = copy.deepcopy(issue)
    if test:
        issue.function = None
    matched = pd.concat([find_headline(issue)])
    matched = matched.drop_duplicates().sort_index()
    for i, row in matched.iterrows():
        if issue.loc[i].function is None:
            issue.set_value(i, "function", "HL")
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
