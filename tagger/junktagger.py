# junktagger.py
# Nupur Garg

import re

from basetagger import *


# TODO(ngarg): Ideas for future tagging:
#   - N: 1) Above & below row have row.function == 'N'
#        2) 3 or less consequtive alphanumerics in row.text


def _tag_blank(row):
    """
    Tags the row as blank (B) if the row's text is np.nan.

    row: obj
        DataFrame row to return value for.
    """
    if (pd.isnull(row.function) and
        (pd.isnull(row.text) or re.search(r"^[\t\s]+$", row.text))):
        return "B"
    return row.function


def _tag_unintelligible(row):
    """
    Tags the row as unintelligible (N) if there are not two consequtive
    alphanumeric characters.

    row: obj
        DataFrame row to return value for.
    """
    if (pd.isnull(row.function) and 
        not pd.isnull(row.text) and
        not re.search(r"\w\w+", row.text)):
        return "N"
    return row.function


def tag(issue):
    """
    Tags the issue with the following extraneous tags:
        B - Blank line
        N - Unintelligible

    issue: obj
        Issue object to apply tags to.
    """
    assert check_tags_exist(issue, ["PI", "HL", "BL"])

    issue = copy.deepcopy(issue)
    issue.apply(col="function", func=_tag_blank)
    issue.apply(col="function", func=_tag_unintelligible)

    return issue


def main():
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump", "ad"],
                                         tags=["PI", "HL", "BL"])
    tagged_issues = [tag(issue) for issue in untagged_issues]
    tagged_issues[2].to_csv('test.csv')

    print_accuracy_tag(issues, tagged_issues, tag="B", print_incorrect=True)
    print_accuracy_tag(issues, tagged_issues, tag="N", print_incorrect=True)


if __name__ == "__main__":
    main()
