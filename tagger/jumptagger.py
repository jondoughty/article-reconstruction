# jumptagger.py
# Vivian Fong

from tagger.basetagger import *

import regex


_REQUIRED_TAGS = ["PI", "BL", "HL", "N", "B", "AT", "TXT"]
_FORMAT_STRINGS = [
    ("(From page (\d{1,2})){e<=2}", 2, -1),        # (format_string, group_num, direction)
    ("(Please see page (\d{1,2})){e<=4}", 2, 1),
    ("(See \w{1,10}, page (\d{1,2})){e<=2}", 2, 1),
    ("(See \w{1,10}, (\w{1,10}) page){e<=2}", 2, 1),
]


def _match_pattern(text, fmt_str):
    pattern = regex.compile(fmt_str, flags=regex.ENHANCEMATCH)
    return regex.search(pattern, text, concurrent=True)


def _get_jump_with_pattern(text, format_tuple):
    """
    Extracts the jump page number if exists.

    text: str
        Text to perform analysis on.
    format_tuple:
        Tuple with (format string, group number, and jump direction).

    returns: bool
    """
    fmt_str = format_tuple[0]
    group = format_tuple[1]
    direction = format_tuple[2]

    match = _match_pattern(text, fmt_str)
    if match and match[group]:
        page = match[group]
        if page.isdigit() and int(page) < 20:
            return int(page) * direction    # "from" jumps are negative
        elif _match_pattern(page, "(front|back){e<=2}"):
            return page

    return False


def _has_page_jump(text):
    """
    Determines if the text has a page jump.

    text: str
        Text to perform analysis on.

    returns: bool
    """
    for format_tuple in _FORMAT_STRINGS:
        jump = _get_jump_with_pattern(text, format_tuple)
        if jump:
            return jump


def tag(issue):
    """
    Tags the issue's JUMP column.

    issue: obj
        Issue object to apply tags to.

    return: obj
    """
    assert check_tags_exist(issue, _REQUIRED_TAGS)

    # Labels rows.
    issue = copy.deepcopy(issue)

    for index, row in issue.tags_df.iterrows():
        issue.tags_df.loc[index, "jump"] = 0
        if not pd.isnull(row.text):
            jump = _has_page_jump(row.text)
            if jump:
                issue.tags_df.loc[index, "jump"] = jump
                if pd.isnull(row.function):
                    is_ME = len(row.text.split()) < 5
                    issue.tags_df.loc[index, "function"] = "ME" if is_ME else "TXT"

    return issue


def main():
    # Gets issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump"],
                                         tags=_REQUIRED_TAGS)
    # Tags the untagged issues.
    tagged_issues = [tag(issue) for issue in untagged_issues]
    for i in range(len(tagged_issues)):
        tagged_issues[i].to_csv('jump_test' + str(i) + '.csv')

    # Print the accuracy of the results.
    # print_accuracy_tag(issues, tagged_issues, tag="JUMP", jump_col=True, print_incorrect=True)

    compute_jump_metric(issues, tagged_issues)



if __name__ == "__main__":
    main()
