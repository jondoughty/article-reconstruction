# txttagger.py
# Vivian Fong
#
from nltk.corpus import names
from nltk import sent_tokenize
from nltk import word_tokenize
import difflib
import enchant
import re
import string

from tagger.basetagger import *

_PUNCTUATION = string.punctuation + "''"
_ENGLISH_DICTIONARY = enchant.Dict("en_US")
_ENGLISH_NAMES = [word.lower() for word in (names.words("female.txt") + names.words("male.txt"))
                               if not _ENGLISH_DICTIONARY.check(word)]


# ===============================================
# ========= CLASSIFIER HELPER FUNCTIONS =========
# ===============================================


def _features_stats_sent_word_count(text):
    """
    Gets the features on sentence and word count.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    # Sentence count.
    # sent_count = len(sent_tokenize(text))
    # features.update(create_features_for_ranges(feature_name="sent_count",
    #                                             variable=sent_count,
    #                                             ranges=[1, 2, 3]))
    # Word count.
    words = word_tokenize(text)
    alpha_only = [w for w in words if w not in _PUNCTUATION]
    word_count = len(alpha_only)
    features.update(create_features_for_ranges(feature_name="word_count",
                                                variable=word_count,
                                                ranges=[5, 15, 25, 35]))
    return features


def _features_stats_readable_word_percentage(text):
    """
    Gets the percentage of readable words.

    Each word that exists in a dictionary adds 1 point.
    # For all other words, the edit distance is computed with the most similar
    # dictionary word. If the similarity score is above the threshold, the score
    # is added to the total score. The percentage is computed at the end with by
    # dividing the score by the total number of words.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    THRESHOLD = 0.75
    features = {}

    words = word_tokenize(text)
    alpha_only = [w.lower() for w in words if w not in _PUNCTUATION]
    word_count = len(alpha_only)
    readable_word_percent = 0
    potential_word_percent = 0

    if word_count:
        readable_word_score = 0
        potential_word_score = 0

        for word in alpha_only:
            potential_word_score += 1
            if _ENGLISH_DICTIONARY.check(word):
                readable_word_score += 1
            # else:
            #     suggestions = _ENGLISH_DICTIONARY.suggest(word)
            #     if suggestions:
            #         matcher = difflib.SequenceMatcher(None, word, suggestions[0])
            #         sim = matcher.real_quick_ratio()
            #         if sim > THRESHOLD:
            #             readable_word_score += sim
        readable_word_percent = readable_word_score / word_count
        potential_word_percent = potential_word_score / word_count

    features.update(create_features_for_ranges(feature_name="readable_word_percent",
                                                variable=readable_word_percent,
                                                ranges=[.75]))
    features.update(create_features_for_ranges(feature_name="potential_word_percent",
                                                variable=potential_word_percent,
                                                ranges=[.90]))
    return features


def _features_stats_alpha_char_percentage(text):
    """
    Gets the percentage of alphabetic characters.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    char_count = len(text)
    alpha_char_count = len([c for c in text if c.isalpha()])
    percent = alpha_char_count / char_count
    features.update(create_features_for_ranges(feature_name="alpha_char_percentage",
                                                variable=percent,
                                                ranges=[.25, .5, .75]))
    return features


def _features_stats_uppercase(text):
    """
    Gets the percentage of uppercased words.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    words = word_tokenize(text)
    alpha_only = [w for w in words if w not in _PUNCTUATION]
    word_count = len(alpha_only)
    uppercase_count = len([w for w in words if w.isupper()])
    percent = uppercase_count / word_count if word_count else 0

    features.update(create_features_for_ranges(feature_name="uppercase_percentage",
                                                variable=percent,
                                                ranges=[.25, .5, .75]))
    # features.update(create_features_for_ranges(feature_name="uppercase_count",
    #                                             variable=uppercase_count,
    #                                             ranges=[0, 2]))
    return features

# TODO: This is not working.
def _features_sent_prefix(text):
    features = {}

    words = word_tokenize(text)
    if '—' in words[0:5]:
        if words[0].isalpha() and words[0].isupper():
            features["sent_prefix_with_hyphen"] = 1
        else:
            features["sent_prefix_with_hyphen"] = 2
        print(str(words[0:5]) + ' = ' + str(features["sent_prefix_with_hyphen"]))

    #     else:
    #         features["sent_prefix_with_hyphen"] = "non-upper"
    # else:
    #     features["sent_prefix_with_hyphen"] = None

    return features


# ========================================
# ========= CLASSIFIER FUNCTIONS =========
# ========================================


def _generate_features_txt(row_data):
    """
    Generates a classifier that identifies article text (TXT).

    row_data: obj
        Series containing a row of issue data.

    returns: dict
    """
    features = {}
    text = row_data.text.strip()
    features.update(_features_stats_sent_word_count(text))
    features.update(_features_stats_readable_word_percentage(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_alpha_char_percentage(text))
    # features.update(_features_sent_prefix(text))
    return features


# =====================================
# ========= TAGGING FUNCTIONS =========
# =====================================


def _setup_surrounding_funcs_references(issue):
    """
    Sets up references to surrounding functions.

    issue: obj
        Issue object to apply tags to.

    returns: None
    """
    issue.tags_df["func_prev"] = issue.tags_df['function'].shift(periods=1)
    issue.tags_df["func_next"] = issue.tags_df['function'].shift(periods=-1)
    issue.tags_df["func_prev_two"] = issue.tags_df['function'].shift(periods=2)
    issue.tags_df["func_next_two"] = issue.tags_df['function'].shift(periods=-2)


def _drop_surrounding_funcs_references(issue):
    """
    Drops references to surrounding functions.

    issue: obj
        Issue object to apply tags to.

    returns: None
    """
    issue.tags_df.drop(["func_prev", "func_next", "func_prev_two", "func_next_two"],
                       axis=1, inplace=True)


def _tag_txt(row, classifier, features_func):
    """
    Tags the row as article text (TXT) if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    features_func: func
        Function that generates the features.

    returns: str
    """
    valid_funcs = ["HL", "BL"]

    if pd.isnull(row.function) and not pd.isnull(row.text):
        features = features_func(row)

        # features["func_prev_two"] = row.func_prev_two
        # features["func_prev"] = row.func_prev

        # If row is directly after HL or BL.
        # if row.func_prev in valid_funcs:
        #     features["after_HL_BL"] = True

        # # If previous row is TXT.
        # if row.func_prev == "TXT":
        #     print("**PREV_TXT**")
        #     features["after_TXT"] = 2 if row.func_prev_two == "TXT" else 1

        if classifier.classify(features):
            return "TXT"

    return row.function


# ==================================
# ========= MAIN FUNCTIONS =========
# ==================================


def smooth(issue):
    _setup_surrounding_funcs_references(issue)

    for index, row in issue.tags_df.iterrows():
        # Fill in gaps
        if pd.isnull(row.function) and row.func_prev == "TXT" and row.func_next == "TXT":
            issue.tags_df.loc[index, "function"] = "TXT"

        # Remove outliers
        if row.function == "TXT" and pd.isnull(row.func_prev) and pd.isnull(row.func_next):
            issue.tags_df.loc[index, "function"] = None

        # Revise

    _drop_surrounding_funcs_references(issue)

    return issue


def tag(issue):
    """
    Tags the issue with the TXT tag.

    issue: obj
        Issue object to apply tags to.
    """
    assert check_tags_exist(issue, ["PI", "HL", "BL", "B", "N", "AT"])
    issue = copy.deepcopy(issue)

    filename = _TXTTAGGER_CLASSIFIER[0]
    features_func = _TXTTAGGER_CLASSIFIER[1]
    label_func = _TXTTAGGER_CLASSIFIER[3]

    issue.apply_classifier(col="function", filename=filename,
                            features_func=features_func, label_func=label_func)
    issue = smooth(issue)

    return issue


_TXTTAGGER_CLASSIFIER = ("txttagger_TXT_naive_bayes.pickle", _generate_features_txt, ["TXT"], _tag_txt)


def main():
    # Get issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump"],
                                         tags=["PI", "HL", "BL", "B", "N", "AT"])

    # Create classifier.
    filename = _TXTTAGGER_CLASSIFIER[0]         # "txttagger_TXT_naive_bayes.pickle"
    features_func = _TXTTAGGER_CLASSIFIER[1]    # _generate_features_txt
    tags = _TXTTAGGER_CLASSIFIER[2]             # _tag_txt
    create_classifier(issues=issues,
                      classifier_func=create_naive_bayes_classifier,
                      features_func=features_func, tags=tags, filename=filename,
                      stats=True, debug=False)

    # Tag the untagged issues.
    tagged_issues = [tag(issue) for issue in untagged_issues]
    # for index, issue in enumerate(tagged_issues):
    #     name = 'txt_test' + str(index) + '.csv'
    #     issue.to_csv(name)
    tagged_issues[2].to_csv('txt_test.csv')

    # Print the accuracy of the results.
    print_accuracy_tag(issues, tagged_issues, tag="TXT", print_incorrect=True)


if __name__ == "__main__":
    main()
