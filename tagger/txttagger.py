# txttagger.py
# Vivian Fong


from tagger.basetagger import *
from nltk import word_tokenize


# TODO: Replace heuristic with classifier.


def _tag_txt(row):
    """
    Tags the row as article text (TXT) if text contains at least 10 words.

    row: obj
        DataFrame row to return value for.
    """
    if row.text:
        words = word_tokenize(row.text)
        if pd.isnull(row.function) and len(words) >= 10:
            return "TXT"
    return row.function


def tag(issue):
    """
    Tags the issue with the TXT tag.

    issue: obj
        Issue object to apply tags to.
    """
    assert check_tags_exist(issue, ["PI", "HL", "BL", "B"])#, "NA"])

    issue = copy.deepcopy(issue)
    # TODO; Fix this.
    #issue.apply(col="function", func=_tag_txt)

    return issue


def main():
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump", "ad"],
                                         tags=["PI", "HL", "BL", "B", "NA"])
    tagged_issues = [tag(issue) for issue in untagged_issues]
    tagged_issues[2].to_csv('txt_test.csv')

    #print_accuracy_tag(issues, tagged_issues, tag="TXT", print_incorrect=True)


if __name__ == "__main__":
    main()
