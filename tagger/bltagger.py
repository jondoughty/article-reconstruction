# bltagger.py
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
    content_tags = ["HL", "TXT"]
    tp = fp = fn = 0
    for path in paths:
        issue = pd.read_csv(path, header = 2, names = columns)
        issue = issue.dropna(how = "all")
        issue = tag(issue, test = True).join(issue.function, rsuffix = "_act")
        print(issue)
        tp += len(issue[(issue.function_act == "BL") &
                        (issue.function == "BL")])
        fp += len(issue[(issue.function_act.isin(content_tags)) &
                        (issue.function == "BL")])
        fn += len(issue[(issue.function_act == "BL") &
                        (issue.function != "BL")])
        print("\n\nTrue Positives:")
        print(issue[(issue.function_act == "BL") &
                    (issue.function == "BL")])
        print("\n\nFalse Positives:")
        print(issue[(issue.function_act.isin(content_tags)) &
                    (issue.function == "BL")])
        print("\n\nFalse Negatives:")
        print(issue[(issue.function_act == "BL") &
                    (issue.function != "BL")])
        print("\n\n\n")
    print("Precision", tp / (tp + fp))
    print("Recall", tp / (tp + fn))


def tag(issue, test = False):
    issue = copy.deepcopy(issue)
    # issue = issue.tags_df
    if test:
        issue.tags_df.function = None
    matched = pd.concat([find_byline(issue.tags_df), find_description(issue.tags_df)])
    matched = matched.drop_duplicates().sort_index()
    for i, row in matched.iterrows():
        if issue.tags_df.loc[i].function is None:
            issue.tags_df.set_value(i, "function", "BL")
    return issue


def remove_punctuation(text):
#    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
#    return text.translate(table).strip().upper()
    replaced = regex.sub("[^{0}]".format("\s:"), "", text)
    replaced = regex.sub("[^{0}]".format(string.ascii_letters + string.digits),
                         " ", text)
    return replaced.upper()


def e(error):
    return "{{" + "s<={0},i<=1,d<=1,e<={0}".format(error) + "}}"


def find_byline(issue, error = 3):
    adjs = "|".join(["ASSOCIATED", "STAFF", "EDITORIAL", "MANAGING",
                     "CONTRIBUTING", "COMMENTARY", "SPORTS", "OUTDOOR"])
    nouns = "|".join(["PRESS", "STAFF", "EDITOR", "WRITER", "REPORT",
                      "REPORTER", "ARTIST"])
    fmt_str = (r"^(?:(?:(?:STORY)" + e(2) + "\s+)?" +   # "story"
                    "(?:BY)" + e(1) + "\s+" +           # "by"
                    "(?:[A-Z]+\s*){{2,3}}" +            # name
                    "(?:(?:AND)" + e(1) + "\s*" +       # "and"
                        "(?:[A-Z]+\s*){{2,3}})?)?" +    # name
                "(?:(?:(?:DAILY|AP)" + e(1) + "\s+)?" + # "Daily" or "AP"
                    "(?:(?:{0})" + e(2) + "\s*)?" +     # title adj
                    "(?:(?:{1})" + e(2) + "\s*)?)?" +   # title noun
                "(?:SPEACIAL TO THE DAILY)?" +          # "Special to the Daily"
                "$").format(adjs, nouns)
    pattern = regex.compile(fmt_str, flags = regex.ENHANCEMATCH)
    matched = []
    for _, row in issue.iterrows():
        if pd.notnull(row.text) and len(row.text) < 100 and ":" not in row.text:
            text = remove_punctuation(row.text)
            match = regex.match(pattern, text, concurrent = True)
#            if row.function == "BL" and not match:
#                print(text)
            if match:
                matched.append(row)
    return pd.DataFrame(matched)


def find_description(issue):
    nouns = "|".join(["FRESHMAN", "SOPHOMORE", "JUNIOR", "SENIOR", "MAJOR",
                      "PROFESSOR"])
    fmt_str = (r"^(?:[A-Z]+\s*){{2,3}}" +   # name
                "(?:IS A)\s*" +             # "is a"
                "(?:CAL POLY\s*)?" +        # "Cal Poly"
                "([A-Z]+\s*){{1,2}}" +      # title adj
                "(?:{0})" +                 # title noun
                "(?:AND\s+.+)?" +           # "and ..."
                "$").format(nouns)
    pattern = regex.compile(fmt_str, flags = regex.ENHANCEMATCH)
    matched = []
    for _, row in issue.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text).strip()
            match = regex.match(pattern, text, concurrent = True)
            if match:
                matched.append(row)
    return pd.DataFrame(matched)


if __name__ == "__main__":
    main()
