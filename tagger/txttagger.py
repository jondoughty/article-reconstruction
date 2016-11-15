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
    sent_count = len(sent_tokenize(text))
    features.update(create_features_for_ranges(feature_name="sent_count",
                                                variable=sent_count,
                                                ranges=[1, 2, 3]))
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
    percent = 0

    if word_count:
        readable_word_score = 0
        for word in alpha_only:
            if _ENGLISH_DICTIONARY.check(word):
                readable_word_score += 1
            # else:
            #     suggestions = _ENGLISH_DICTIONARY.suggest(word)
            #     if suggestions:
            #         matcher = difflib.SequenceMatcher(None, word, suggestions[0])
            #         sim = matcher.real_quick_ratio()
            #         if sim > THRESHOLD:
            #             readable_word_score += sim
        percent = readable_word_score / word_count

    # print('Percent: %f' %percent)
    features.update(create_features_for_ranges(feature_name="readable_word_percent",
                                                variable=percent,
                                                ranges=[.25, .5, .75]))
                                                #ranges=[.35, .65]))
    return features


# ========================================
# ========= CLASSIFIER FUNCTIONS =========
# ========================================


def _generate_features_txt(data):
    """
    Generates a classifier that identifies article text (TXT).

    data: obj
        Series containing issue data.

    returns: dict
    """
    features = {}
    text = data.text.strip()
    features.update(_features_stats_sent_word_count(text))
    features.update(_features_stats_readable_word_percentage(text))
    return features


# =====================================
# ========= TAGGING FUNCTIONS =========
# =====================================


def _tag_txt(row, classifier, features_func):
    """
    Tags the row as article text (TXT) if the classifier indicates True.

    row: obj
        DataFrame row to return value for.
    features_func: func
        Function that generates the features.

    returns: str
    """
    if (pd.isnull(row.function) and
        not pd.isnull(row.text) and
        classifier.classify(features_func(row))):
        return "TXT"
    return row.function


# ==================================
# ========= MAIN FUNCTIONS =========
# ==================================


def tag(issue):
    """
    Tags the issue with the TXT tag.

    issue: obj
        Issue object to apply tags to.
    """
    assert check_tags_exist(issue, ["PI", "HL", "BL", "B", "N", "AT"])

    issue = copy.deepcopy(issue)
    # issue.apply(col="function", label_func=_tag_txt)

    filename = _TXTTAGGER_CLASSIFIER[0]
    features_func = _TXTTAGGER_CLASSIFIER[1]
    label_func = _TXTTAGGER_CLASSIFIER[3]
    issue.apply_classifier(col="function", filename=filename,
                            features_func=features_func, label_func=label_func)

    return issue


_TXTTAGGER_CLASSIFIER = ("txttagger_TXT_naive_bayes.pickle", _generate_features_txt, ["TXT"], _tag_txt)


def main():
    # Get issues with and without tags.
    issues, untagged_issues = get_issues(columns=["article", "paragraph", "jump"],
                                         tags=["PI", "HL", "BL", "B", "N", "AT"])

    # Create classifier.
    filename = _TXTTAGGER_CLASSIFIER[0]
    features_func = _TXTTAGGER_CLASSIFIER[1]
    tags = _TXTTAGGER_CLASSIFIER[2]
    create_classifier(issues=issues,
                      classifier_func=create_naive_bayes_classifier,
                      features_func=features_func, tags=tags, filename=filename,
                      stats=True, debug=False)

    # Tag the untagged issues.
    tagged_issues = [tag(issue) for issue in untagged_issues]
    tagged_issues[2].to_csv('txt_test.csv')

    # Print the accuracy of the results.
    print_accuracy_tag(issues, tagged_issues, tag="TXT", print_incorrect=False)


if __name__ == "__main__":
    main()
