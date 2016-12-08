# hltagger.py
# Daniel Kauffman

import copy
import glob
import regex
import string

import pandas as pd

from tagger.basetagger import *


def main():
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
    paths = glob.glob("tagged_data/*.csv")
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]
    content_tags = ["BL", "TXT"]
    tp = fp = fn = 0
    for path in paths:
        issue = pd.read_csv(path, header = 2, names = columns)
        issue = issue.dropna(how = "all")
        issue = tag(issue)
        tp += len(issue[(issue.function == "HL") &
                        (issue.prediction == "HL")])
        fp += len(issue[(issue.function.isin(content_tags)) &
                        (issue.prediction == "HL")])
        fn += len(issue[(issue.function == "HL") &
                        (issue.prediction != "HL")])
        print("\n\nTrue Positives:")
        print(issue[(issue.function == "HL") &
                        (issue.prediction == "HL")])
        print("\n\nFalse Positives:")
        print(issue[(issue.function.isin(content_tags)) &
                        (issue.prediction == "HL")])
        print("\n\nFalse Negatives:")
        print(issue[(issue.function == "HL") &
                        (issue.prediction != "HL")])
        print("\n\n\n")
    print("Precision", tp / (tp + fp))
    print("Recall", tp / (tp + fn))


def tag(issue):
    issue = copy.deepcopy(issue)
    matched = pd.concat([find_headline(issue)])
    matched = matched.drop_duplicates().sort_index()
    predictions = ["HL" if i in matched.index else None for i in issue.index]
    issue["prediction"] = predictions
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
                is_hl = (pd.isnull(prev.function) or \
                         prev.function not in ["PI", "BL"]) and \
                        "." not in prev.text and len(prev.text) < 80 and \
                        (row.function == "BL" or \
                         (len(prev.text.split()) > 1 and \
                          len(prev.text.split()) <= 6))
                if is_hl:
                    matched.append(prev)
    return pd.DataFrame(matched)


if __name__ == "__main__":
    main()
