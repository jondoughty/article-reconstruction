# pubtagger.py
# Daniel Kauffman

import calendar
import copy
import regex
import string

import pandas as pd

import tagger.basetagger as basetagger


def main():
    basetagger.measure_precision_recall("PI", tag)


def tag(issue, test = False):
    issue = copy.deepcopy(issue)
    issue.tags_df.page = None
    issue.tags_df.function = None
    matched = pd.concat([find_volume(issue.tags_df),
                         find_page_info(issue.tags_df),
                         find_date(issue.tags_df),
                         find_pub_name(issue.tags_df)])
    matched = matched.drop_duplicates().sort_index()
    for i, row in matched.iterrows():
        if issue.tags_df.loc[i].function is None:
            issue.tags_df.set_value(i, "function", "PI")
    breaks = get_page_breaks(matched)
    ptr = 0
    for i, _ in issue.tags_df.iterrows():
        issue.tags_df.set_value(i, "page", ptr + 1)
        if ptr < len(breaks) - 1 and i >= breaks[ptr + 1]:
            ptr += 1
    return issue


def remove_punctuation(text):
    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    return text.translate(table).strip().upper()


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


def get_page_breaks(matched, error = 2):
    months = "|".join(map(str.upper, calendar.month_name))[1:]
    err_str = "{{s<={0},i<=1,d<=1,e<={0}}}".format(error)
    fmt_str = r"(?:{1}){0}".format(err_str, months)
    pattern = regex.compile(fmt_str)
    breaks = [0]
    for i, row in matched.iterrows():
        if pd.notnull(row.text):
            text = remove_punctuation(row.text)
            match = regex.search(pattern, text, concurrent = True)
            if match and i > breaks[-1] + 20:
                breaks.append(i)
    # TODO: tags "Mustang Daily"
    return breaks


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


if __name__ == "__main__":
    main()
