# junktagger.py
# Nupur Garg

import re

from tagger.basetagger import *


# TODO(ngarg): Ideas for future tagging:
#   - N: 1) Above & below row have row.function == 'N'
#        2) 3 or less consequtive alphanumerics in row.text
# TODO(ngarg): Add connection for classifier into the code.


_JUNKTAGGER_CLASSIFIERS = []


# ========================================
# ========= CLASSIFIER FUNCTIONS =========
# ========================================


def _features_stats_alphabetic(text):
    """
    Gets features on the alphabetic characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    alphabetic = [char for char in text if char.isalpha() or char == ' ']
    percent = len(alphabetic) / float(len(text))
    features = create_features_for_ranges(feature_name='percent_alphabetic',
                                          variable=percent,
                                          ranges=[0.1, 0.5, 0.7, 0.8, 0.9])
    features['start_alphabetic'] = text[0].isalpha()
    return features


def _features_stats_uppercase(text):
    """
    Gets features on the uppercase characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    alphabetic = [char for char in text if char.isupper()]
    percent = len(alphabetic) / float(len(text))
    features = create_features_for_ranges(feature_name='percent_uppercase',
                                          variable=percent,
                                          ranges=[0.05, 0.1, 0.2, 0.8, 0.9, 0.95])
    return features


def _features_stats_non_ascii(text):
    """
    Gets features on the ascii vs non-ascii characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    alphabetic = [char for char in text if ord(char) < 128]
    percent = len(alphabetic) / float(len(text))
    features = create_features_for_ranges(feature_name='percent_ascii',
                                          variable=percent,
                                          ranges=[0.8, 0.9, 0.96])
    return features


def _generate_features_advertisement(data):
    """
    Generates a classifier that identify an advertisement (AT).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    text = data.text.strip()

    # TODO: Percent of tokens in a dictionary
    features.update(_features_stats_non_ascii(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_alphabetic(text))

    return features


def _generate_features_unintelligible(data):
    """
    Generates features that identify unintelligible text (N).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    return features


def _generate_features_other(data):
    """
    Generates features that identify other (OT).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    return features


def _generate_features_comic(data):
    """
    Generates features that identify comic strip titles (CN) or
    comic strip text (CT).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    return features


# =====================================
# ========= TAGGING FUNCTIONS =========
# =====================================


def _tag_blank(row):
    """
    Tags the row as blank (B) if the row's text is np.nan.

    row: obj
        DataFrame row to return value for.

    returns: str
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

    returns: str
    """
    if (pd.isnull(row.function) and
        not pd.isnull(row.text) and
        not re.search(r"\w+", row.text)):
        return "N"
    return row.function


def _tag_advertisement(row, classifier, features_func):
    """
    Tags the row as advertisement (AT) if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    features_func: func
        Function that generates the features.

    returns: str
    """
    if (pd.isnull(row.function) and
        not pd.isnull(row.text) and
        classifier.classify(features_func(row))):
        return "AT"
    return row.function


# ==================================
# ========= MAIN FUNCTIONS =========
# ==================================


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
    issue.apply(col="function", label_func=_tag_blank)
    issue.apply(col="function", label_func=_tag_unintelligible)

    for classifiers in _JUNKTAGGER_CLASSIFIERS:
        filename = classifiers[0]
        features_func = classifiers[1]
        label_func = classifiers[3]
        issue.apply_classifier(col="function", filename=filename,
                               features_func=features_func, label_func=label_func)

    return issue


def tag_junk(issue, replace_nan=True, replace_all=False):
    """
    Tags any untagged rows in 'function' column as junk (JNK).

    issue: obj
        Issue object to apply tags to.
    replace_nan: bool
        Whether to replace np.nan with JNK.
    replace_all: bool
        Whether to replace the tag on other junk coumns with JNK.
    """
    issue = copy.deepcopy(issue)
    tags = []
    if replace_nan:
        tags.append(np.nan)
    if replace_all:
        tags.extend(["N", "B", "AT"]) # "AT", "OT", "CN", "CT"])

    for tag in tags:
        issue.tags_df.function.replace(tag, "JNK", inplace=True)
    return issue


# TODO: Determine a better place/method to do this.
# Updates junk classifiers.
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_AT_naive_bayes.pickle", _generate_features_advertisement, ["AT"], _tag_advertisement))
# TODO(ngarg): Comment back in.
# _JUNKTAGGER_CLASSIFIERS.append(("junktagger_N_naive_bayes.pickle", _generate_features_unintelligible, ["N"]))
# _JUNKTAGGER_CLASSIFIERS.append(("junktagger_OT_naive_bayes.pickle", _generate_features_other, ["OT"]))
# _JUNKTAGGER_CLASSIFIERS.append(("junktagger_C_naive_bayes.pickle", _generate_features_comic, ["CN", "CT"]))


def main():
    # Gets issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump", "ad"],
                                         tags=["PI", "HL", "BL"])

    # Create classifiers.
    for classifiers in _JUNKTAGGER_CLASSIFIERS:
        filename = classifiers[0]
        func = classifiers[1]
        tags = classifiers[2]
        create_classifier(issues=issues,
                          classifier_func=create_naive_bayes_classifier,
                          features_func=func, filename=filename, tags=tags,
                          stats=True, debug=False)

    # Tags the untagged issues.
    tagged_issues = [tag(issue) for issue in untagged_issues]
    tagged_issues[2].to_csv("test.csv")

    # Prints the accuracy of the results.
    print_accuracy_tag(issues, tagged_issues, tag="B", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="N", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="AT", print_incorrect=False)

    # Replaces the tags in the issues with JNK.
    final_issues = [tag_junk(issue, replace_nan=False, replace_all=True) for issue in tagged_issues]
    jnk_issues = [tag_junk(issue, replace_all=True) for issue in issues]
    final_issues[2].to_csv("test2.csv")
    jnk_issues[2].to_csv("test3.csv")

    # Prints the accuracy of the results.
    print_accuracy_tag(jnk_issues, final_issues, tag="JNK", print_incorrect=False)


if __name__ == "__main__":
    main()
