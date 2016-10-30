# junktagger.py
# Nupur Garg

import copy

from basetagger import *


def _tag_blank(row):
    """
    Tags the row as blank.

    row: obj
        DataFrame row to return value for.
    """
    if pd.isnull(row.text) and pd.isnull(row.function):
        return "B"
    return row.function


def tag(issue):
    """
    Tags the issue with the following extraneous tags:
        B - Blank line

    issue: obj
        Issue object to apply tags to.
    """
    assert check_tags_exist(issue, ["PI", "HL", "BL"])

    issue = copy.deepcopy(issue)
    issue.apply(col='function', func=_tag_blank)

    return issue


def main():
    issues = get_issues(columns=["article", "paragraph", "jump", "ad"],
                        tags=["PI", "HL", "BL"])

    issue = issues[1]
    issue = tag(issue)
    issue.to_csv('test.csv')


if __name__ == "__main__":
    main()
