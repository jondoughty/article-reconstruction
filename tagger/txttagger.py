# txttagger.py
# Vivian Fong

from nltk.corpus import names
from nltk import sent_tokenize
from nltk import word_tokenize
import enchant
import re
import string

from tagger.basetagger import *

_PUNCTUATION = string.punctuation + "''"
_ENGLISH_DICTIONARY = enchant.Dict("en_US")
_ENGLISH_NAMES = [word.lower() for word in (names.words("female.txt") + names.words("male.txt"))
                               if not _ENGLISH_DICTIONARY.check(word)]
_REQUIRED_TAGS = ["PI", "BL", "B", "N", "MH"]


# ===============================================
# ========= CLASSIFIER HELPER FUNCTIONS =========
# ===============================================


def _features_stats_word_count(text):
    """
    Gets the features on word count.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    words = word_tokenize(text)
    alpha_only = [w for w in words if w not in _PUNCTUATION]
    word_count = len(alpha_only)
    features.update(create_features_for_ranges(feature_name="word_count",
                                                variable=word_count,
                                                ranges=[1, 3, 5, 15, 25]))
    return features


def _features_stats_punctuation(text):
    """
    Gets the features on punctuation.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    sents = sent_tokenize(text)
    words = word_tokenize(text)

    if '“' in text or '”' in text:
        features["has_quotes"] = True

    period_count = 0
    question_mark_count = 0
    exclamation_mark_count = 0
    for sent in sents:
        if len(sent) > 1:
            if sent[-1] == "." and sent[-2] != ".":
                period_count += 1
            elif sent[-1] == "?":
                question_mark_count += 1
            elif sent[-1] == "!":
                exclamation_mark_count += 1

    features.update(create_features_for_ranges(feature_name="sent_period_count",
                                                variable=period_count,
                                                ranges=[0, 1, 2, 3]))
    features.update(create_features_for_ranges(feature_name="sent_exclamation_count",
                                                variable=exclamation_mark_count,
                                                ranges=[0, 1, 2]))
    features.update(create_features_for_ranges(feature_name="sent_question_count",
                                                variable=question_mark_count,
                                                ranges=[0, 1, 2]))
    return features


def _features_stats_readable_word_percentage(text):
    """
    Gets the percentage of readable words.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    words = word_tokenize(text)
    alpha_only = [w.lower() for w in words if w not in _PUNCTUATION]
    word_count = len(alpha_only)
    readable_word_percent = 0
    name_count = 0

    if word_count:
        readable_word_score = 0
        for word in alpha_only:
            if _ENGLISH_DICTIONARY.check(word):
                readable_word_score += 1
            if word in _ENGLISH_NAMES:
                name_count += 1
        readable_word_percent = readable_word_score / word_count

    features.update(create_features_for_ranges(feature_name="name_count",
                                                variable=name_count,
                                                ranges=[1, 3]))
    features.update(create_features_for_ranges(feature_name="readable_word_percent",
                                                variable=readable_word_percent,
                                                ranges=[.75]))
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
    random_symbol_count = len([c for c in text if c not in string.punctuation and not c.isalpha() and not c.isdigit()])
    alpha_char_percent = alpha_char_count / char_count if char_count else 0
    random_symbol_percent = random_symbol_count / char_count if char_count else 0

    features.update(create_features_for_ranges(feature_name="alpha_char_percentage",
                                                variable=alpha_char_percent,
                                                ranges=[.25, .75]))
    features.update(create_features_for_ranges(feature_name="random_symbol_percentage",
                                                variable=random_symbol_percent,
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
                                                ranges=[.25, .75]))
    features.update(create_features_for_ranges(feature_name="uppercase_count",
                                                variable=uppercase_count,
                                                ranges=[0, 2]))
    return features


def _features_stats_prefix(text):
    """
    Gets features for the first character and first word.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    if text:
        first_char = text[0]
        if first_char.isalpha():
            features["first_char"] = "upper" if first_char.isupper() else "lower"
        elif first_char.isdigit():
            features["first_char"] = "digit"
        elif first_char == '“':
            features["first_char"] = "quote"

        words = word_tokenize(text)
        if words:
            first_word = words[0]
            if first_word.isalpha():
                features["first_word"] = "upper" if first_word.isupper() else "lower"

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
    features.update(_features_stats_word_count(text))
    features.update(_features_stats_punctuation(text))
    features.update(_features_stats_readable_word_percentage(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_alpha_char_percentage(text))
    features.update(_features_stats_prefix(text))
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
    if pd.isnull(row.function) and not pd.isnull(row.text):
        features = features_func(row)
        if classifier.classify(features):
            return "TXT"

    return row.function


# ==================================
# ========= MAIN FUNCTIONS =========
# ==================================


def _check_line_prefix(word):
    """
    Determines whether the given word for the sentence prefix.

    text: str
        Text to perform analysis on.

    returns: boolean
    """
    if word.lower() == "editor":
        return True

    upper_chars = [c for c in word if c.isupper()]
    ratio = len(upper_chars) / len(word)
    return ratio > 0.5


def _is_non_text_prefix(text):
    if len(words) < 5:
        return False
    if words[0] in '-—':
        return True
    if '-' in words[1:5] or '—' in words[1:5]:
        if not _check_line_prefix(words[0]):
            return True
    for word in words:
        if '-' in word or '—' in word:
            return True
    return False


def smooth(issue):
    """
    Additional rules to clean up the results after statistical analysis.

    text: Issue
        Issue to clean up.

    returns: Issue
    """

    _setup_surrounding_funcs_references(issue)

    for index, row in issue.tags_df.iterrows():
        curr_func = row.function if row.function != "TXT" else None
        valid_prev_funcs = ["TXT", "HL", "BL"]

        # Fill in gaps
        if (pd.isnull(row.function) and
            (row.func_prev_two == "TXT" or row.func_next_two == "TXT") and
            row.func_prev in valid_prev_funcs and
            row.func_next == "TXT"):
            issue.tags_df.loc[index, "function"] = "TXT"

        # Remove outliers
        if (row.function == "TXT" and
            (row.func_prev_two not in valid_prev_funcs or row.func_next_two != "TXT") and
            row.func_prev not in valid_prev_funcs and
            row.func_next != "TXT"):
            issue.tags_df.loc[index, "function"] = curr_func

        # Revise
        if not pd.isnull(row.text):
            if "(AP) —" in row.text:
                issue.tags_df.loc[index, "function"] = "TXT"

            words = word_tokenize(row.text)
            if words:
                if len(words) == 1 and row.function == "TXT":
                    issue.tags_df.loc[index, "function"] = None
                elif words[0].islower() == "editor":
                    issue.tags_df.loc[index, "function"] = "TXT"
                elif len(words) >= 5 and ('-' in words[1:5] or '—' in words[1:5]):
                    if  _check_line_prefix(words[0]):
                        issue.tags_df.loc[index, "function"] = "TXT"
                    else:
                        issue.tags_df.loc[index, "function"] = curr_func
                elif len(words) <= 7 and ('page' in words[:5]):
                    issue.tags_df.loc[index, "function"] = None

    _drop_surrounding_funcs_references(issue)

    return issue


_TXTTAGGER_CLASSIFIER = ("txttagger_TXT_naive_bayes.pickle", _generate_features_txt, ["TXT"], _tag_txt)


def tag(issue):
    """
    Tags the issue with the TXT tag.

    issue: obj
        Issue object to apply tags to.
    """
    assert check_tags_exist(issue, _REQUIRED_TAGS)
    issue = copy.deepcopy(issue)

    filename = _TXTTAGGER_CLASSIFIER[0]         # "txttagger_TXT_naive_bayes.pickle"
    features_func = _TXTTAGGER_CLASSIFIER[1]    # _generate_features_txt
    label_func = _TXTTAGGER_CLASSIFIER[3]       # _tag_txt

    issue.apply_classifier(col="function", filename=filename,
                            features_func=features_func, label_func=label_func)
    issue = smooth(issue)
    return issue


def main():
    # Get issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump"],
                                         tags=_REQUIRED_TAGS)

    # Create classifier.
    filename = _TXTTAGGER_CLASSIFIER[0]         # "txttagger_TXT_naive_bayes.pickle"
    features_func = _TXTTAGGER_CLASSIFIER[1]    # _generate_features_txt
    tags = _TXTTAGGER_CLASSIFIER[2]             # ["TXT"]
    create_classifier(issues=issues,
                      classifier_func=create_naive_bayes_classifier,
                      features_func=features_func, tags=tags, filename=filename,
                      stats=True, debug=False)

    # Tag the untagged issues.
    tagged_issues = [tag(issue) for issue in untagged_issues]
    # for index, issue in enumerate(tagged_issues):
    #     name = 'txt_test' + str(index) + '.csv'
    #     issue.to_csv(name)
    # tagged_issues[2].to_csv('txt_test.csv')

    # Print the accuracy of the results.
    print_accuracy_tag(issues, tagged_issues, tag="TXT", print_incorrect=False)


if __name__ == "__main__":
    main()
