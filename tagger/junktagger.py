# junktagger.py
# Nupur Garg

from nltk.corpus import names
import enchant
import re

from tagger.basetagger import *


_JUNKTAGGER_CLASSIFIERS = []
_ENGLISH_DICTIONARY = enchant.Dict("en_US")

_ENGLISH_ALL_NAMES = names.words("female.txt") + names.words("male.txt")
_ENGLISH_ALL_NAMES_STR = "|".join(_ENGLISH_ALL_NAMES)

_ENGLISH_NAMES = [word.lower() for word in _ENGLISH_ALL_NAMES
                               if not _ENGLISH_DICTIONARY.check(word)]
_ENGLISH_NAMES_STR = "\W|\W".join(_ENGLISH_NAMES)
_REQUIRED_TAGS = ["PI", "HL", "BL", "SH"]


# ===============================================
# ========= CLASSIFIER HELPER FUNCTIONS =========
# ===============================================


def _has_page_jump(text):
    """
    Determines if the text has a page jump.

    text: str
        Text to perform analysis on.

    returns: bool
    """
    return bool(re.search(r"page \d+", text))


def _features_stats_alphabetic(text):
    """
    Gets features on the alphabetic characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    # Percent alphabetic.
    alphabetic = re.sub(r"[^A-Za-z\ ]+", "", text)
    percent = len(alphabetic) / float(len(text))
    features.update(create_features_for_ranges(feature_name="percent_alpha",
                                               variable=percent,
                                               ranges=[0.05, 0.1, 0.5, 0.7, 0.8, 0.9]))

    # Number of words.
    words = alphabetic.split(" ")
    features.update(create_features_for_ranges(feature_name="avg_num_alpha_words",
                                               variable=len(words),
                                               ranges=[2, 5, 11, 25, 30, 40, 50]))

    # Average number of words.
    len_words = [len(word) for word in words]
    avg_len_words = sum(len_words) / float(len(len_words))
    features.update(create_features_for_ranges(feature_name="avg_len_alpha_words",
                                               variable=avg_len_words,
                                               ranges=[2, 3, 4, 5, 6, 8]))

    features["start_alphabetic"] = text[0].isalpha()
    return features


def _features_stats_uppercase(text):
    """
    Gets features on the uppercase characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    words = text.split(" ")

    # Percent uppercase.
    alphabetic = re.sub(r"[^A-Z]+", "", text)
    percent = len(alphabetic) / float(len(text))
    features.update(create_features_for_ranges(feature_name="percent_uppercase",
                                               variable=percent,
                                               ranges=[0.05, 0.1, 0.2, 0.8, 0.9, 0.95]))

    # Uppercase words statistics.
    uppercase_words = [word for word in words if word and word[0].isupper()]
    features["all_words_start_uppercase"] = len(uppercase_words) == len(text[0])
    features["start_uppercase"] = text[0].isupper()
    return features


def _features_stats_dictionary(text):
    """
    Gets features on the dictionary from the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    words = text.lower().split(" ")
    words_synset = [word for word in words
                         if word and _ENGLISH_DICTIONARY.check(word)]

    # Percent words in dictionary.
    percent = len(words_synset) / float(len(words))
    features.update(create_features_for_ranges(feature_name="percent_dict_words",
                                               variable=percent,
                                               ranges=[0.9]))
                                               # ranges=[0.05, 0.33, 0.9, 0.98]))

    # Number distinct dictionary words.
    features.update(create_features_for_ranges(feature_name="count_dict_words",
                                               variable=len(set(words_synset)),
                                               ranges=[30]))
                                               # ranges=[1, 5, 10, 15, 20, 25, 30, 40]))

    # Length dictionary words.
    len_words = [len(word) for word in words_synset]
    avg_len_words = sum(len_words) / float(len(len_words)) if len_words else 0
    features.update(create_features_for_ranges(feature_name="avg_len_dict_words",
                                               variable=avg_len_words,
                                               ranges=[10]))
                                               # ranges=[2, 3, 4, 5, 6, 8]))

    return features


def _features_stats_names(text):
    """
    Gets features on the names in the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    words = text.split(" ")
    words_synset = [word for word in words
                         if (word and _ENGLISH_DICTIONARY.check(word) and
                             word not in _ENGLISH_ALL_NAMES)]

    # Number of names.
    features.update(create_features_for_ranges(feature_name="num_names",
                                               variable=len(words_synset),
                                               ranges=[1, 3, 10, 40]))

    # Number of non-name words.
    features.update(create_features_for_ranges(feature_name="num_non_names",
                                               variable=len(words),
                                               ranges=[1, 3, 5]))
    return features


def _features_stats_numerals(text):
    """
    Gets features on the numerals of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    numerals = re.sub(r"\d+", "", text)
    percent = len(numerals) / float(len(text))
    features.update(create_features_for_ranges(feature_name="percent_numerals",
                                               variable=percent,
                                               ranges=[0.35, 0.7, 0.9, 0.98]))
    return features


def _features_stats_non_ascii(text):
    """
    Gets features on the ascii vs non-ascii characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    alphabetic = re.sub(r"[^\x00-\x7F]+", "", text)
    percent = len(alphabetic) / float(len(text))
    features.update(create_features_for_ranges(feature_name='percent_ascii',
                                               variable=percent,
                                               ranges=[0.8, 0.9, 0.96]))
    return features


def _features_stats_patterns(text):
    """
    Gets features on the patterns within the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    text = text.lower()

    # Special number types to exclude.
    features["has_page_jump"] = _has_page_jump(text)
    features["has_year"] = bool(re.search(r"[^\d]((1[7-9])|2[0-1])\d{2}([^\d]|$)", text))
    features["has_full_phone_number"] = bool(re.search(r"\(\d{3}\) \d{3}\-\d{4}", text))
    features["has_thousands"] = bool(re.search(r"\d+\,\d{3}", text))
    features["has_keyword"] = bool(re.search(r"editor|manager|adviser|mustang", text))
    features["has_quotes"] = bool(re.search(r"\“.*\”", text))
    # features["encoded_apostrophe"] = bool(re.search(r"â€™", text))

    # Special number types to include.
    features["has_phone_number"] = (False if features["has_full_phone_number"] else
                                    bool(re.search(r"[^\d]\d{3}\-\d{4}", text)))
    features["has_money"] = bool(re.search(r"\$\d+|\d+\$", text))
    features["has_elipses"] = bool(re.search(r"\.\.\.", text))
    features["has_percent"] = bool(re.search(r"\d+\%", text))
    features["has_time"] = bool(re.search(r"\d\:\d\d", text))
    features["has_time_am_pm"] = bool(re.search(r"\d+ (a\.m\.|p\.m\.|am|pm)", text))
    features["has_underscores"] = bool(re.search(r"(\_{5})+", text))

    return features


# ========================================
# ========= CLASSIFIER FUNCTIONS =========
# ========================================


def _generate_features_advertisement(data):
    """
    Generates a classifier that identify an advertisement (AT).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    text = data.text.strip()

    features.update(_features_stats_alphabetic(text))
    features.update(_features_stats_names(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_dictionary(text))
    features.update(_features_stats_numerals(text))
    features.update(_features_stats_non_ascii(text))
    features.update(_features_stats_patterns(text))

    return features


def _generate_features_unintelligible(data):
    """
    Generates a classifier that identify text as unintelligible (N).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    text = data.text.strip()

    features.update(_features_stats_alphabetic(text))
    features.update(_features_stats_names(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_numerals(text))
    features.update(_features_stats_non_ascii(text))
    features.update(_features_stats_patterns(text))

    return features


def _generate_features_other(data):
    """
    Generates a classifier that identify text as other (OT).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    text = data.text.strip()

    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_non_ascii(text))
    features.update(_features_stats_patterns(text))

    return features


def _generate_features_header(data):
    """
    Generates a classifier that identify text as photo header (PH) or masthead (MH).

    data: obj
       Series containing issue data.

    returns: dict
    """
    features = {}
    text = data.text.strip()

    features.update(_features_stats_names(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_patterns(text))

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


def _tag_unintelligible(row, classifier, features_func):
    """
    Tags the row as unintelligible (N) if there are not two consequtive
    alphanumeric characters or if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    classifier: obj
        Classifier.
    features_func: func
        Function that generates the features.

    returns: str
    """
    if pd.isnull(row.function) and not pd.isnull(row.text):
        if not re.search(r"\w+", row.text):
            return "N"
        if not _has_page_jump(row.text) and classifier.classify(features_func(row)):
            return "N"
    return row.function


def _tag_advertisement(row, classifier, features_func):
    """
    Tags the row as advertisement (AT) if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    classifier: obj
        Classifier.
    features_func: func
        Function that generates the features.

    returns: str
    """
    if pd.isnull(row.function) and not pd.isnull(row.text):
        if not _has_page_jump(row.text) and classifier.classify(features_func(row)):
            return "AT"
    return row.function


def _tag_other(row, classifier, features_func):
    """
    Tags the row as other (OT) if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    classifier: obj
        Classifier.
    features_func: func
        Function that generates the features.

    returns: str
    """
    if pd.isnull(row.function) and not pd.isnull(row.text):
        if not _has_page_jump(row.text) and classifier.classify(features_func(row)):
            return "OT"
    return row.function


def _tag_headers(row, classifier, features_func):
    """
    Tags the row as masthead (MH) if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    classifier: obj
        Classifier.
    features_func: func
        Function that generates the features.

    returns: str
    """
    if pd.isnull(row.function) and not pd.isnull(row.text):
        if not _has_page_jump(row.text) and classifier.classify(features_func(row)):
            return "MH"
    return row.function


def _tag_in_range(row):
    """
    Tags the row based on previous row if the previous or next row are:
        - unintelligible (N)
        - other (OT)
        - advertisement (AT)

    row: obj
        DataFrame row to return value for.

    returns: str
    """
    valid_funcs = ["N", "OT", "AT"]
    if pd.isnull(row.function) and not pd.isnull(row.text):
        if row.func_prev in valid_funcs and row.func_next in valid_funcs:
            words = row.text.lower().split(" ")
            words_synset = [word for word in words
                                 if word and _ENGLISH_DICTIONARY.check(word)]
            if len(words_synset) <= 5:
                return row.func_prev
            if row.func_prev_two in valid_funcs and row.func_next_two in valid_funcs:
                return row.func_prev
    return row.function


def _apply_in_range(issue):
    """
    Determines unintelligible text based on surrounding the rows.

    issue: obj
        Issue object to apply tags to.

    returns: None
    """
    issue.tags_df["func_prev"] = issue.tags_df['function'].shift(periods=1)
    issue.tags_df["func_next"] = issue.tags_df['function'].shift(periods=-1)
    issue.tags_df["func_prev_two"] = issue.tags_df['function'].shift(periods=2)
    issue.tags_df["func_next_two"] = issue.tags_df['function'].shift(periods=-2)
    issue.tags_df["function"] = issue.tags_df.apply(lambda row: _tag_in_range(row), axis=1)
    issue.tags_df.drop(["func_prev", "func_next", "func_prev_two", "func_next_two"],
                       axis=1, inplace=True)


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

    return: obj
    """
    assert check_tags_exist(issue, _REQUIRED_TAGS)

    # Labels rows.
    issue = copy.deepcopy(issue)
    issue.apply(col="function", label_func=_tag_blank)

    # Labels rows with classifiers.
    for classifiers in _JUNKTAGGER_CLASSIFIERS:
        filename = classifiers[0]
        features_func = classifiers[1]
        label_func = classifiers[3]
        issue.apply_classifier(col="function", filename=filename,
                               features_func=features_func, label_func=label_func)

    # Labels rows based labels on nearby rows.
    _apply_in_range(issue)
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

    returns: obj
    """
    issue = copy.deepcopy(issue)
    tags = []
    if replace_nan:
        tags.append(np.nan)
    if replace_all:
        tags.extend(["B", "AT", "N", "CT", "CN", "OT", "PH", "MH"])

    for tag in tags:
        issue.tags_df.function.replace(tag, "JNK", inplace=True)
    return issue


# TODO(ngarg): Determine a better place/method to do this.
# List of junk classifiers.
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_AT_naive_bayes.pickle", _generate_features_advertisement, ["AT"], _tag_advertisement))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_N_naive_bayes.pickle", _generate_features_unintelligible, ["N", "CT", "CN"], _tag_unintelligible))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_MH_naive_bayes.pickle", _generate_features_header, ["MH", "PH"], _tag_headers))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_OT_naive_bayes.pickle", _generate_features_other, ["OT"], _tag_other))


def main():
    # Gets issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump", "ad"],
                                         tags=_REQUIRED_TAGS)

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
    tagged_issues[0].to_csv("test.csv")

    # Prints the accuracy of the results.
    print_accuracy_tag(issues, tagged_issues, tag="B", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="N", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="AT", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="OT", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="MH", print_incorrect=False)

    # Replaces the tags in the issues with JNK.
    final_issues = [tag_junk(issue, replace_nan=False, replace_all=True) for issue in tagged_issues]
    jnk_issues = [tag_junk(issue, replace_all=True) for issue in issues]
    final_issues[0].to_csv("test2.csv")
    jnk_issues[0].to_csv("test3.csv")

    # Prints the accuracy of the results.
    print_accuracy_tag(jnk_issues, final_issues, tag="JNK", print_incorrect=True)


if __name__ == "__main__":
    main()
