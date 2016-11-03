# pubtagger.py
# Daniel Kauffman

import calendar
import copy
import regex

from nltk.metrics import distance
import pandas as pd

from basetagger import *


def main():
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
    issue = pd.read_csv(path, header = 2, names = columns)
    tag(issue)


def tag(issue):
    issue = copy.deepcopy(issue)
    return issue


def find_date(issue, max_error = 5):
    dows = "|".join(calendar.day_name)
    months = "|".join(calendar.month_name)[1:]
    fmt_str = "(?:\s*({0})\s*.\s*({1})\s*([1-3]?[0-9])\s*.\s*" + \
              "((?:19|20)[0-9]{{2}})\s*){{e<{2}}}"
    pattern = regex.compile(fmt_str.format(dows, months, max_error),
                            flags = regex.ENHANCEMATCH)
    best_match = None
    best_counts = sys.maxsize
    for _, row in issue[issue.function == "PI"].iterrows():
        match = regex.search(pattern, row.text, concurrent = True)
        if match:
            print(match.fuzz_counts)
            if best_match is None or match.fuzzy_counts < best_counts:
                best_match = match
                best_counts = match.fuzzy_counts
    dow = edit_match(match.group(1), calendar.day_name)
    month = edit_match(match.group(2), calendar.month_name)


def edit_match(match, candidates):
    return min(candidates,
               key = lambda candidate: distance.edit_distance(match, candidate))


if __name__ == "__main__":
    main()
