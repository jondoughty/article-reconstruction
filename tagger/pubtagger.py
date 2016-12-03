# pubtagger.py
# Daniel Kauffman

import calendar
import copy
import glob
import regex
import string

from nltk.metrics import distance
import pandas as pd

from tagger.basetagger import *


def main():
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
    paths = glob.glob("tagged_data/*.csv")
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]
    content_tags = ["HL", "BL", "TXT"]
    for path in paths:
#    for path in paths[:1] + paths[2:]:
#    if True:
#        import sys
#        path = paths[int(sys.argv[1])]
        print(path)
        issue = pd.read_csv(path, header = 2, names = columns)
        matched = pd.concat([find_volume(issue), find_page_info(issue),
                             find_date(issue), find_pub_name(issue)])
        matched = matched.drop_duplicates().sort_index()
        actual = issue[issue.function == "PI"]
        print("True Positives:")
        print(matched[~matched.function.isin(content_tags)])
        print("False Positives:")
        print(matched[matched.function.isin(content_tags)])
        print("False Negatives:")
        print(actual[~actual.isin(matched)].dropna())
        print("\n")
#        tag(issue)


def tag(issue):
    issue = copy.deepcopy(issue)
    return issue


def remove_punctuation(text):
#    text = text.translate(str.maketrans("", "", string.punctuation))
    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    return text.translate(table).strip().upper()


def find_nameplate(issue, error = 5):
    pub_name = "MUSTANG DAILY"
    school_name = "CALIFORNIA POLYTECHNIC STATE UNIVERSITY"


def find_volume(issue, error = 3):
    err_str = "{{e<={0}}}".format(error)
    fmt_str = (r"(?:^(?:VOLUME){0}\s+" +    # "Volume"
                ".{{1,4}}\s*" +             # volume number
                "(?:NO){0}\s*" +            # "No."
                ".{{1,4}}" +                # issue number
                "$){0}").format(err_str)
    pattern = regex.compile(fmt_str, flags = regex.ENHANCEMATCH)
    for i, row in issue.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text)
            match = regex.match(pattern, text, concurrent = True)
            if match:
                return issue.loc[i:i]
    return pd.DataFrame()


def find_page_info(issue, error = 1):
    err_str = "{{s<={0},i<=1,d<=1,e<={0}}}".format(error)
    fmt_str = (r"(?:^(?:PAGE){0}\s*" +
                ".{{1,2}}" +
                "$){0}").format(err_str)
    pattern = regex.compile(fmt_str, flags = regex.ENHANCEMATCH)
    matched = []
    for _, row in issue.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text)
            match = regex.match(pattern, text, concurrent = True)
            if match:
                matched.append(row)
    return pd.DataFrame(matched)


def find_pub_name(issue, error = 5):
    pub_name = "MUSTANG DAILY"
    fmt_str = r"(?:^{0}$){{e<={1}}}"
    pattern = regex.compile(fmt_str.format(pub_name, error),
                            flags = regex.ENHANCEMATCH)
    matched = []
    for _, row in issue.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text)
            match = regex.match(pattern, text, concurrent = True)
            if match:
                matched.append(row)
    return pd.DataFrame(matched)


def find_date(issue, error = 3):
    pub_name = "MUSTANG DAILY"
    dows = "|".join(map(str.upper, calendar.day_name))
    months = "|".join(map(str.upper, calendar.month_name))[1:]
    err_str = "{{s<={0},i<=1,d<=1,e<={0}}}".format(error)
    fmt_str = (r"(?:^.{{0,2}}\s*(?:(?:{1}){0})?\s*" +   # "Mustang Daily"
                "({2}){0}\s*" +                         # day of week
                "({3}){0}\s*" +                         # month
                "(?:[1-3]?[0-9]){0}\s*" +               # day
                "(?:(?:19|20)[0-9]{{2}}){0}\s*" +       # year
                "(?:(?:{1}){0})?" +                     # "Mustang Daily"
                ".{{0,2}}${0})").format(err_str, pub_name, dows, months)
    pattern = regex.compile(fmt_str)
    matched = []
    prev_i = issue.index.min()
    prev_text = None
    for i, row in issue.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text)
            match = regex.match(pattern, text, concurrent = True)
            if match:
                matched.append(row)
            elif prev_text:
                cat_text = prev_text + " " + text
                match = regex.match(pattern, cat_text, concurrent = True)
                if match:
                    matched.append(issue.loc[prev_i])
                    matched.append(row)
            prev_i = i
            prev_text = text
    return pd.DataFrame(matched)


#def parse_date(rows):
#    best_match = None
#    best_counts = None
#    for row in rows:
#        match = regex.match(pattern, row.text, concurrent = True)
#        if match:
#            fuzzy_counts = sum(match.fuzzy_counts)
#            if best_match is None or fuzzy_counts < best_counts:
#                best_match = match
#                best_counts = fuzzy_counts
#    dow = edit_match(best_match.group(1), calendar.day_name)
#    month = edit_match(best_match.group(2), calendar.month_name)
#    return (dow, month)


def edit_match(match, candidates):
    return min(candidates,
               key = lambda candidate: distance.edit_distance(match, candidate))


if __name__ == "__main__":
    main()
