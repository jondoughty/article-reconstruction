# junktagger.py
# Nupur Garg

from nltk.corpus import names
import enchant
import random
import re

from tagger.basetagger import *


# Global classifiers metadata.
_REGENERATE_CLASSIFIERS = False
_JUNKTAGGER_CLASSIFIERS = []
_SHUFFLE = False

# Required function tags metadata.
_REQUIRED_TAGS = ["PI", "HL", "BL"]
_TAGS_TO_KEEP = _REQUIRED_TAGS + ["PL"]

# English dictionary.
_ENGLISH_DICTIONARY = enchant.Dict("en_US")

# All English names.
_ENGLISH_ALL_NAMES = names.words("female.txt") + names.words("male.txt")
_ENGLISH_ALL_NAMES_STR = "|".join(_ENGLISH_ALL_NAMES)

# English names not in the dictionary.
_ENGLISH_NAMES = [word.lower() for word in _ENGLISH_ALL_NAMES
                               if not _ENGLISH_DICTIONARY.check(word)]
_ENGLISH_NAMES_STR = "\W|\W".join(_ENGLISH_NAMES)


# ===============================================
# ========= CLASSIFIER HELPER FUNCTIONS =========
# ===============================================


def _preprocess_text(text):
    """
    Preprocesses text by stripping and replacing the "\t".

    text: str
        Text to perofrm analysis on.

    returns: str
    """
    return text.strip().replace("\t", " ")


def _is_section_header(text):
    """
    Determines if the text is a section header (SH).

    text: str
        Text to perform analysis on.

    returns: bool
    """
    # Compile regex.
    text = re.sub(r"[^A-Za-z\ ]+", "", text)
    fmt_str = ("(^(WELLNESS)$){e<=1}|"
               "(^(NOTEBOOK)$){e<=1}|"
               "(^(editorial)$){e<=0}|"
               "(^(IN QUOTES)$){e<=1}|"
               "(^(Newsbriefs)$){e<=1}|"
               "(^(SCOREBOARD)$){e<=1}|"
               "(^(ON THE STREET)$){e<=1}|"
               "(^(MUSTANG DAILY)$){e<=1}|"
               "(^(Sports|SPORTS)$){e<=2}|"
               "(^(Campus|CAMPUS)$){e<=1}|"
               "(^(Opinion|OPINION)$){e<=1}|"
               "(^(Letters|LETTERS)$){e<=2}|"
               "(^(Calendar|CALENDAR)$){e<=1}|"
               "(^(QUOTE OE THE DAY)$){e<=1}|"
               "(^(Reader Viewpoint)$){e<=1}|"
               "(^(Newsline|NEWSLINE)$){e<=1}|"
               "(^(Notables|NOTABLES)$){e<=1}|"
               "(^(Commentary|COMMENTARY)$){e<=1}|"
               "(^(LETTERS TO THE EDITOR)$){e<=1}|"
               "(^(Editorials|EDITORIALS)$){e<=1}|"
               "(^(Reporter's|REPORTER'S)$){e<=1}|"
               "(^(Perspectives|PERSPECTIVES)$){e<=1}|"
               "(^(Classified|CLASSIFIED|CiassifieD)$){e<=1}")
    pattern = regex.compile(fmt_str, flags=regex.ENHANCEMATCH)
    match = regex.search(pattern, text, concurrent=True)

    # Determine if a match is found.
    if match:
        num_words = len(text.split(" "))
        diff = sum(match.fuzzy_counts)
        is_match = bool(match) and (num_words < 10 if diff > 1 else True)
        return is_match
    return False


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

    # Number of words with capital first letter.
    titles = [word for word in words if re.sub(r'\W+', '', word).istitle()]
    features.update(create_features_for_ranges(feature_name="num_titles",
                                               variable=len(titles),
                                               ranges=[2, 5, 10, 20]))

    # Finds "- <NAME>" pattern.
    starts_dash = ord(text.strip()[0]) in [45, 8212]
    features["starts_dash"] = starts_dash
    features["starts_dash_num_titles"] = starts_dash and len(titles) < 5

    return features


def _features_stats_numerals(text):
    """
    Gets features on the numerals of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    # Percent of characters that are numerals.
    numerals = re.sub(r"\d+", "", text)
    percent = len(numerals) / float(len(text))
    features.update(create_features_for_ranges(feature_name="percent_numerals",
                                               variable=percent,
                                               ranges=[0.35, 0.7, 0.9, 0.98]))

    # Other numeric statistics.
    features["colon_number"] = bool(re.search(r"\: \d{1,3}$", text))
    return features


def _features_stats_non_alphabetic(text):
    """
    Gets features on the non-alphabetic characteristics of the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}

    # Gets ascii vs non-ascii letters.
    alphabetic = re.sub(r"[^\x00-\x7F]+", "", text)
    percent = len(alphabetic) / float(len(text))
    features.update(create_features_for_ranges(feature_name='percent_ascii',
                                               variable=percent,
                                               ranges=[0.8, 0.9, 0.96]))

    # Gets number of a-caret operations.
    a_caret = re.findall(r"a\^", text)
    features.update(create_features_for_ranges(feature_name='num_a_caret',
                                               variable=len(a_caret),
                                               ranges=[1, 2]))

    # Gets number of %a.
    percent_a = re.findall(r"\%a", text)
    features.update(create_features_for_ranges(feature_name='num_percent_a',
                                               variable=len(a_caret),
                                               ranges=[1]))

    return features


def _features_stats_positional(text):
    """
    Gets features based on the position in the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    words = text.lower().split(" ")
    word = words[-1][:-1].strip()

    # Last word has a period.
    features["ends_period"] = bool(re.search(r"\.|\!$", text))
    features["ends_word"] = (_ENGLISH_DICTIONARY.check(word)
                             if word and word[-1].isalpha() else False)
    features["ends_word_1_word"] = features["ends_word"] and len(words) == 1
    features["ends_word_long"] = features["ends_word"] and len(word) >= 5
    features["ends_word_period"] = features["ends_period"] and features["ends_word"]

    # Ends with comma.
    features["ends_comma"] = bool(re.search(r"\,|\;", text))
    features["ends_word_comma"] = features["ends_comma"] and features["ends_word"]

    # Ends with quotation.
    quotations = r"(\u0022|\u0027|\u0060|\u00B4|\u2018|\u2019|\u201C|\u201D)"
    features["has_simple_quotation"] = bool(re.search(r"\“.*\”", text))
    features["starts_quotation"] = bool(re.search(r"^%s" %quotations, text))
    features["ends_period_quotation"] = bool(re.search(r"\.%s$" %quotations, text))
    features["ends_word_period_quotation"] = (_ENGLISH_DICTIONARY.check(word[:-1])
                                              if (features["ends_period_quotation"] and
                                                  word[:-1] and word[-2].isalpha()) else False)

    # # Capital first letter.
    features["has_title_first_word"] = text[0].istitle() and len(words) > 2
    features["is_proper_sentence"] = features["has_title_first_word"] and features["ends_word_long"]
    features["is_quoted_sentence"] = features["has_title_first_word"] and features["ends_word_period_quotation"]
    features["is_full_quoted_sentence"] = features["starts_quotation"] and features["ends_word_period_quotation"]
    return features


def _features_stats_word_patterns(text):
    """
    Gets features on the word patterns within the text.

    text: str
        Text to perform analysis on.

    returns: dict
    """
    features = {}
    text = text.lower()
    words = text.split(' ')

    # Special words to exclude.
    features["has_addressings"] = bool(re.search(r"by|dear ", text)) and len(words) == 3
    features["has_days_of_week"] = bool(re.search(r"(monday|tuesday|wednesday|thursday|friday)(,|.)\ \w+\.? \d{1,2}", text))
    features["is_editor_colon"] = text == "editor:"
    features["has_mustang"] = bool(re.search(r"mustang daily|mustang|musung", text))
    features["has_acronyms"] = bool(re.search(r" \(ap\) -", text))
    features["has_1_word"] = len(words) == 1 and len(words[0]) > 3
    features["has_2_words"] = len(words) == 2 and len(words[0]) > 3 and len(words[1]) > 3
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
    words = text.split(' ')

    # Special words to exclude.
    features["has_positions"] = bool(re.search(r"editor|manager|adviser", text))

    # Special number types to exclude.
    features["has_year"] = bool(re.search(r"[^\d]((1[7-9])|2[0-1])\d{2}([^\d]|$)", text))
    features["has_thousands"] = bool(re.search(r"\d+\,\d{3}", text))
    features["has_score"] = bool(re.search(r" \d{1,2}\-\d{1,2} ", text))
    features["has_fractions"] = bool(re.search(r"\d{1,2}\/\d{1,2} ", text))
    features["has_money_thousands"] = bool(re.search(r"\$\d{1,3}\,\d{1,3}", text))

    # Special number types to include.
    features["has_phone_number"] = bool(re.search(r"[^\d]\d{3}\-\d{4}", text))
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
    text = _preprocess_text(data.text)

    features.update(_features_stats_alphabetic(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_dictionary(text))
    features.update(_features_stats_numerals(text))
    features.update(_features_stats_non_alphabetic(text))
    features.update(_features_stats_positional(text))
    features.update(_features_stats_word_patterns(text))
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
    text = _preprocess_text(data.text)

    features.update(_features_stats_alphabetic(text))
    features.update(_features_stats_names(text))
    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_numerals(text))
    features.update(_features_stats_non_alphabetic(text))
    features.update(_features_stats_positional(text))
    features.update(_features_stats_word_patterns(text))
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
    text = _preprocess_text(data.text)

    features.update(_features_stats_uppercase(text))
    features.update(_features_stats_non_alphabetic(text))
    features.update(_features_stats_positional(text))
    features.update(_features_stats_word_patterns(text))
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
    text = _preprocess_text(data.text)

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
        (pd.isnull(row.text) or (not bool(row.text)) or
         re.search(r"^[\t\s]+$", row.text))):
        return "B"
    return row.function


def _tag_jump(row):
    """
    Tags any row with a jump (JUMP).

    row: obj
        DataFrame row to return value for.

    returns: str
    """
    if pd.isnull(row.function):
        if has_page_jump(row.text):
            return "JUMP"
    return row.function


def _tag_section_header(row):
    """
    Tags any row as a section header (SH).

    row: obj
        DataFrame row to return value for.

    returns: str
    """
    if pd.isnull(row.function):
        if _is_section_header(row.text):
            return "SH"
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
    if pd.isnull(row.function):
        if not re.search(r"\w+", row.text):
            return "N"
        if classifier.classify(features_func(row)):
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
    if pd.isnull(row.function):
        if classifier.classify(features_func(row)):
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
    if pd.isnull(row.function):
        if classifier.classify(features_func(row)):
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
    if pd.isnull(row.function):
        if classifier.classify(features_func(row)):
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
    _get_synset = lambda text: [word for word in text.lower().split(" ")
                               if word and _ENGLISH_DICTIONARY.check(word)]
    valid_funcs = ["B", "AT", "N", "CT", "CN", "OT", "PH", "MH", "BQA", "BQN", "BQT", "NP", "SH", "HL"]
    if pd.isnull(row.function) or row.function == "HL":
        surrounding = {"prev": row.func_prev in valid_funcs,
                       "next": row.func_next in valid_funcs,
                       "prev_two": row.func_prev_two in valid_funcs,
                       "next_two": row.func_next_two in valid_funcs}

        # Checks previous and next functions for junk.
        if surrounding["prev"] and surrounding["next"]:
            words_synset = _get_synset(row.text)

            # Returns previous row function if fewer than 5 words.
            if len(words_synset) <= 5:
                return "N"
            # Returns previous row function two above and below are junk.
            if surrounding["prev_two"] and surrounding["next_two"]:
                return "N"

        # Returns "N" if 3 out of 4 are junk and words synset is less than 20.
        if sum(surrounding.values()) >= 3:
            words_synset = _get_synset(row.text)
            if len(words_synset) < 20:
                return "N"
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
    issue.apply(col="function", label_func=_tag_jump)
    issue.apply(col="function", label_func=_tag_section_header)

    # Labels rows with classifiers.
    for classifiers in _JUNKTAGGER_CLASSIFIERS:
        filename = classifiers[0]
        features_func = classifiers[1]
        label_func = classifiers[3]
        issue.apply_classifier(col="function", filename=filename,
                               features_func=features_func, label_func=label_func)

    # Labels rows based labels on nearby rows.
    for idx in range(3):
        _apply_in_range(issue)

    # Remove JUMP tag prior to returning the issue.
    issue.tags_df.function.replace("JUMP", np.nan, inplace=True)
    return issue


# List of junk classifiers.
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_MH_naive_bayes.pickle", _generate_features_header, ["MH", "PH", "BQN", "BQA"], _tag_headers))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_BQ_naive_bayes.pickle", _generate_features_header, ["PH", "BQN", "BQA"], _tag_headers))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_N_naive_bayes.pickle", _generate_features_unintelligible, ["N", "CT", "CN"], _tag_unintelligible))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_OT_naive_bayes.pickle", _generate_features_other, ["OT", "BQT"], _tag_other))
_JUNKTAGGER_CLASSIFIERS.append(("junktagger_AT_naive_bayes.pickle", _generate_features_advertisement, ["AT"], _tag_advertisement))


def main():
    # Gets issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump", "ad"],
                                         tags=_TAGS_TO_KEEP)
    split = int(len(issues) * 0.75)
    final_idx = 0

    # Shuffle the lists.
    if _SHUFFLE:
        print("Shuffling issues...")
        combined = list(zip(issues, untagged_issues))
        random.shuffle(combined)
        issues[:], untagged_issues[:] = zip(*combined)

    # Create classifiers.
    if _REGENERATE_CLASSIFIERS:
        print("Regenerating classifiers...")
        for classifiers in _JUNKTAGGER_CLASSIFIERS:
            filename = classifiers[0]
            func = classifiers[1]
            tags = classifiers[2]
            create_classifier(issues=issues[:split],
                              classifier_func=create_naive_bayes_classifier,
                              features_func=func, filename=filename, tags=tags,
                              stats=True, debug=False)

    # Tags the untagged issues.
    print("Tagging issues...")
    tagged_issues = [tag(issue) for issue in untagged_issues]
    tagged_issues[final_idx].to_csv("test.csv")

    # Prints the accuracy of the results.
    print("Determining accuracy...")
    print_accuracy_tag(issues, tagged_issues, tag="B", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="N", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="AT", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="OT", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="MH", print_incorrect=False)
    print_accuracy_tag(issues, tagged_issues, tag="SH", print_incorrect=False)

    # Replaces the tags in the issues with JNK.
    final_issues = [tag_junk(issue) for issue in tagged_issues]
    jnk_issues = [tag_junk(issue) for issue in issues]
    final_issues[final_idx].to_csv("test2.csv")
    jnk_issues[final_idx].to_csv("test3.csv")

    # Prints the accuracy of the results.
    print_accuracy_tag(jnk_issues[split:], final_issues[split:], tag="JNK", print_incorrect=True)


if __name__ == "__main__":
    main()
