# bltagger.py
# Daniel Kauffman

import copy
import regex
import string

import numpy as np
import pandas as pd

import tagger.basetagger as basetagger


def main():
    basetagger.measure_precision_recall("BL", tag, limit = 30)


def tag(issue, test = False):
    issue = copy.deepcopy(issue)
    if test:
        all_tags = "|".join(t for t in issue.tags_df.function.unique()
                              if pd.notnull(t) and t != "PI")
        pattern = r"^(?:{0})$".format(all_tags)
        issue.tags_df.function = issue.tags_df.function.replace(pattern, np.NaN,
                                                                regex = True)
    matched = pd.concat([find_byline(issue.tags_df),
                         find_description(issue.tags_df)])
    matched = matched.drop_duplicates().sort_index()
    for i, row in matched.iterrows():
        if pd.isnull(issue.tags_df.loc[i].function):
            issue.tags_df.set_value(i, "function", "BL")
    return issue


def remove_punctuation(text):
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
