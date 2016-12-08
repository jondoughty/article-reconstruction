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
    tp = fp = fn = 0
    for path in paths:
        issue = pd.read_csv(path, header = 2, names = columns)
        issue = issue.dropna(how = "all")
        issue = tag(issue).join(issue.function, rsuffix = "_act")
        tp += len(issue[(issue.function_act == "PI") &
                        (issue.function == "PI")])
        fp += len(issue[(issue.function_act.isin(content_tags)) &
                        (issue.function == "PI")])
        fn += len(issue[(issue.function_act == "PI") &
                        (issue.function != "PI")])
        print("\n\nTrue Positives:")
        print(issue[(issue.function_act == "PI") &
                    (issue.function == "PI")])
        print("\n\nFalse Positives:")
        print(issue[(issue.function_act.isin(content_tags)) &
                    (issue.function == "PI")])
        print("\n\nFalse Negatives:")
        print(issue[(issue.function_act == "PI") &
                    (issue.function != "PI")])
        print("\n\n\n")
    print("Precision", tp / (tp + fp))
    print("Recall", tp / (tp + fn))


def tag(issue):
    issue = copy.deepcopy(issue)
    issue.page = None
    issue.function = None
    matched = pd.concat([find_volume(issue), find_page_info(issue),
                         find_date(issue), find_pub_name(issue)])
    matched = matched.drop_duplicates().sort_index()
    for i, row in matched.iterrows():
        if issue.loc[i].function is None:
            issue.set_value(i, "function", "PI")
    pages = count_pages(matched)
#    print(issue.drop_duplicates("page"))
#    print("actual:", len(issue.page.unique()))
#    print()
#    print(matched)
#    print("found:", len(pages), pages)
#    print("\n\n")
    ptr = 0
    for i, row in matched.iterrows():
        issue.set_value(i, "page", pages[ptr])
        if i >= pages[ptr]:
            ptr += 1
    return issue


def remove_punctuation(text):
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
    fmt_str = (r"(?:^(?:PAGE){0}\s*" +      # "Page"
                ".{{1,2}}" +                # "page number"
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


def count_pages(matched, error = 2):
    months = "|".join(map(str.upper, calendar.month_name))[1:]
    err_str = "{{s<={0},i<=1,d<=1,e<={0}}}".format(error)
    fmt_str = r"(?:{1}){0}".format(err_str, months)
    pattern = regex.compile(fmt_str)
    pages = []
    for i, row in matched.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text)
            match = regex.search(pattern, text, concurrent = True)
            if match and i not in pages:
                pages.append(i)
    return pages


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


#def edit_match(match, candidates):
#    return min(candidates,
#               key = lambda candidate: distance.edit_distance(match, candidate))


if __name__ == "__main__":
    main()
