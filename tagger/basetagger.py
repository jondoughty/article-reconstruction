# basetagger.py

from random import shuffle
import pandas as pd
import numpy as np
import pickle
import copy
import math
import nltk
import os
import re


# TODO(ngarg): CHANGE 'NA' to 'N' becuase pandas processes 'NA' as np.nan

_DEFAULT_CLASSIFIER_PATH = "tagger/classifiers"


# ===========================================
# ========= ISSUE CLASS & FUNCTIONS =========
# ===========================================


class Issue(object):
    """
    Represents a newspaper issue.
    Owner: Nupur Garg

    tags_df: DataFrame
        Represents a tagged newspaper.
    date: str
        Date the issue was published.
    edition: (int, int)
        Represents (volume #, issue #).
    filename: str
        Filename of the issue.
    """

    COLUMNS = ["page", "article", "function", "paragraph", "jump", "ad", "text"]

    def __init__(self, tags_df, filename=None):
        self.tags_df = tags_df
        self.filename = filename
        self.date = None
        self.edition = None

    def __str__(self):
        return '%s, %s' %(str(self.date), str(self.edition))

    @staticmethod
    def generate_tags_df(csv_file):
        # Generates a DataFrame from the csv_file provided.
        return pd.read_csv(csv_file, header=1, names=Issue.COLUMNS)

    def apply(self, col, label_func):
        # Applies function to column col.
        self.tags_df[col] = self.tags_df.apply(lambda row: label_func(row), axis=1)

    def apply_classifier(self, col, filename, features_func, label_func):
        # Applies classifier to column col.
        full_filename = os.path.join(os.path.abspath(_DEFAULT_CLASSIFIER_PATH), filename)
        pickle_file = open(full_filename, "rb")
        classifier = pickle.load(pickle_file)

        # Applies classifier.
        self.tags_df[col] = self.tags_df.apply(
            lambda row: label_func(row, classifier, features_func), axis=1)

    def print_rows(self, rows):
        # Prints the rows with the given index of the DataFrame.
        print(self.tags_df.iloc[rows])

    def to_csv(self, filename):
        # Prints the DataFrame to a file.
        self.tags_df.to_csv(filename)

    def get_issue_id(self):
        return re.search(r"(\d{8})\.txt$", self.filename).group(1)


def check_tags_exist(issue, tags):
    """
    Determines if function column in issue.tags_df contains tags.
    Owner: Nupur Garg

    issue: obj
        Issue to check tags for.
    tags: list
        Tags to check.

    returns: obj
    """
    unique_tags = issue.tags_df.function.unique()
    return set(tags).issubset(unique_tags)


def get_issues(folder='tagged_data', columns=None, tags=None):
    """
    Gets all the Issue objects from the folder. Returns original issues and
    untagged issues with certain columns and tags set to np.nan.
    Owner: Nupur Garg

    folder: str
        Folder name.
    columns: list
        Columns to set to None.
    tags: list
        Function tags to keep.

    returns: (list, list)
    """
    files = []
    issues = []
    untagged_issues = []

    # Get test files in the folder.
    foldername = os.path.abspath(folder)
    for filename in os.listdir(foldername):
        full_filename = os.path.join(foldername, filename)
        if os.path.isfile(full_filename) and "csv" in filename:
            files.append(full_filename)

    # Create issue objects from the test files.
    for csv_file in files:
        issue = Issue(Issue.generate_tags_df(csv_file),
                      os.path.basename(os.path.normpath(csv_file)))

        # TODO(ngarg): Consider another approach to replace these columns.
        # Edit the default values within the issue.
        issue.tags_df.function.replace(np.nan, "N", inplace=True)
        issue.tags_df.function = issue.tags_df.function.str.strip()
        issue.tags_df.jump = issue.tags_df.jump.astype(str)
        issue.tags_df.jump.replace("0.0", "0", inplace=True)
        issue.tags_df.jump.replace("nan", "0", inplace=True)

        issues.append(issue)
        issue = copy.deepcopy(issue)

        # Sets columns to None.
        if columns:
            for col in columns:
                issue.tags_df[col] = np.nan

        # Removes function tags.
        if tags:
            unique_tags = issue.tags_df.function.unique()
            remove_tags = set(unique_tags) - set(tags)
            for tag in remove_tags:
                issue.tags_df.function.replace(tag, np.nan, inplace=True)
        untagged_issues.append(issue)

    return issues, untagged_issues


# ========================================
# ========= CLASSIFIER FUNCTIONS =========
# ========================================


# TODO(ngarg): Confirm this calculates precision and recall correctly.
def print_accuracy_tag(orig_issues, tagged_issues, tag, jump_col=False, print_incorrect=False):
    """
    Prints the precision, recall of the function tag for the given issue.
    Owner: Nupur Garg

    orig_issues: list
        Issue objects with original tags.
    tagged_issues: list
        Issue objects with code produced tags.
    tag: str
        Function tag to test.
    jump_col: bool
        Compare JUMP column instead of FUNCTION (default: False).
    print_incorrect: bool
        Prints the incorrectly tagged lines (default: False).

    returns: None
    """
    total_missing = 0.0
    total_expected = 0.0
    total_extra = 0.0
    total_actual = 0.0

    print("=================================")
    print("============ Tag \'%s\' ============" %tag)
    print("=================================")
    for orig_issue, tagged_issue in zip(orig_issues, tagged_issues):
        if jump_col:
            expected_tags = orig_issue.tags_df[orig_issue.tags_df.jump != '0']
            actual_tags = tagged_issue.tags_df[tagged_issue.tags_df.jump != '0']
        else:
            expected_tags = orig_issue.tags_df[orig_issue.tags_df.function == tag]
            actual_tags = tagged_issue.tags_df[tagged_issue.tags_df.function == tag]

        expected_tags_idx = set(expected_tags.index.values)
        actual_tags_idx = set(actual_tags.index.values)

        missing_tags = expected_tags_idx - actual_tags_idx
        extra_tags = actual_tags_idx - expected_tags_idx

        total_missing += len(missing_tags)
        total_expected += len(expected_tags)

        total_extra += len(extra_tags)
        total_actual += len(actual_tags)

        if print_incorrect:
            print("----------- %s -----------" %orig_issue.filename)
            if missing_tags:
                print("\t\t----------- Missing -----------")
                diff = tagged_issue.tags_df.loc[list(missing_tags)][["text", "function", "jump"]]
                diff.sort_index(inplace=True)
                print(diff)
            if extra_tags:
                print("\t\t----------- Extra -----------")
                diff = orig_issue.tags_df.loc[list(extra_tags)][["text", "function", "jump"]]
                diff.sort_index(inplace=True)
                print(diff)

    if total_expected > 0 and total_actual > 0:
        recall = (total_expected - total_missing) / total_expected
        precision = (total_actual - total_extra) / total_actual
        print("\nrecall \'%s\': %.3f" %(tag, recall))
        print("precision \'%s\': %.3f\n" %(tag, precision))


def split_training_test(data, percent=0.75):
    """
    Splits the data into training and test.

    data: list
        List of data made of ({features}: truth) tuples.
    percent: int
        Percentage of training vs test data.

    returns: (obj, obj)
    """
    shuffle(data)
    split = int(len(data) * percent)
    training = data[:split]
    test = data[split:]
    return training, test


def create_features_for_ranges(feature_name, variable, ranges):
    """
    Generate features based on a range.

    feature_name: str
        Name of feature.
    variable: int
        Value of variable.
    ranges: list
        Ranges to check variable on.
    """
    features = {'%s_<_%.2f' %(feature_name, ranges[0]): variable < ranges[0]}
    if len(ranges) > 1:
        features['%s_>=_%.2f' %(feature_name, ranges[-1])] = variable >= ranges[-1]
        for min_range, max_range in zip(ranges, ranges[1:]):
            feature = '%s_%.2f_to_%.2f' %(feature_name, min_range, max_range)
            features[feature] = variable >= min_range and variable < max_range
    return features


def _print_statistics(classifier, test, score, stats, debug):
    """
    Prints statistics for a given classifier and test set.
    Owner: Nupur Garg

    classifier: obj
        Classifier.
    test: list
        Test data.
    stats: bool
        Whether to print summary statistics.
    debug: bool
        Whether to debug.

    returns: None
    """
    if debug:
        print('__Result__\t\t__Actual__')
        for features, actual in test:
            result = classifier.classify(features)
            print('%s\t\t%s' %(result, actual))
    if stats:
        print('Score: %.4f' %score)
        if not isinstance(classifier, nltk.DecisionTreeClassifier):
            classifier.show_most_informative_features(30)
            print("")


def create_naive_bayes_classifier(training, test, stats=True, debug=False):
    """
    Creates a Naive Bayes classifier. Returns the classifier and score.
    Owner: Nupur Garg

    classifier: obj
        Classifier.
    test: list
        Test data.
    stats: bool
        Whether to print summary statistics (default: True).
    debug: bool
        Whether to debug (default: False).

    returns: (obj, int)
    """
    classifier = nltk.NaiveBayesClassifier.train(training)
    score = nltk.classify.accuracy(classifier, test)

    _print_statistics(classifier, test, score, stats, debug)
    return classifier, score


def create_classifier(issues, classifier_func, features_func, tags,
                      filename, path=_DEFAULT_CLASSIFIER_PATH, stats=True, debug=False):
    """
    Creates a classifier based on the classifier function and features function
    provided and stores it in a filename.
    Owner: Nupur Garg

    issues: list
        Issues to test on.
    classifier_func: func
        Function that generates the classifier.
    features_func: func
        Function that generates the features.
    tags: List
        Function tags to create classifier for.
    filename: str
        Name of pickle file.
    path: str
        Path to pickle file.
    stats: bool
        Whether to print summary statistics (default: True).
    debug: bool
        Whether to debug (default: False).

    returns: None
    """
    tagged_data = []
    other_data = []
    features = []

    # Split data into tagged with tags and other tags.
    for issue in issues:
        matches = issue.tags_df.function.isin(tags)
        tagged_data.extend(issue.tags_df.loc[matches].values)
        other_data.extend(issue.tags_df.loc[np.logical_not(matches)].values)

    # Generate tagged and other features.
    tagged_df = pd.DataFrame(tagged_data, columns=Issue.COLUMNS)
    other_df = pd.DataFrame(other_data, columns=Issue.COLUMNS)
    for index, row in tagged_df.iterrows():
        if not pd.isnull(row.text) and row.text.strip():
            features.append((features_func(row), True))
    for index, row in other_df.iterrows():
        if not pd.isnull(row.text) and row.text.strip():
            features.append((features_func(row), False))

    # Generate classifier.
    training, test = split_training_test(features)
    classifier, score = classifier_func(training, test, stats=stats, debug=debug)

    # Stores classifier.
    full_filename = os.path.join(os.path.abspath(path), filename)
    pfile = open(full_filename, "wb")
    pickle.dump(classifier, pfile)


# ===========================================
# ================= METRICS =================
# ===========================================


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
        tags.extend(["B", "AT", "N", "CT", "CN", "OT", "PH", "MH", "BQA", "BQN"])

    for tag in tags:
        issue.tags_df.function.replace(tag, "JNK", inplace=True)
    return issue


def _function_accuracy(expected_funcs, actual_funcs):
    length = len(expected_funcs)
    matches = 0
    for expected, actual in zip(expected_funcs, actual_funcs):
        if expected == actual:
            matches += 1
    return (matches / length, length - matches)


def _jump_accuracy(expected_jumps, actual_jumps):
    actual_jump_count = 0
    matches = 0
    for expected, actual in zip(expected_jumps, actual_jumps):
        if isinstance(expected, int) and expected != 0:
            actual_jump_count += 1
            if expected == actual:
                matches += 1
    accuracy = matches / actual_jump_count if actual_jump_count > 0 else 1
    return (accuracy, actual_jump_count - matches)


def compute_function_metric(original_issues, tagged_issues):
    """
    Computes the average accuracy of the function tagging, with all junk items
    labeled as JNK.
    """
    original_issues_jnk_tag = [tag_junk(issue, replace_all=True) for issue in original_issues]
    tagged_issues_jnk_tag = [tag_junk(issue, replace_all=True) for issue in tagged_issues]
    accuracies = []

    for original_issue, tagged_issue in zip(original_issues_jnk_tag, tagged_issues_jnk_tag):
        original_vector = original_issue.tags_df["function"].tolist()
        tagged_vector = tagged_issue.tags_df["function"].tolist()
        accuracy, num_misses = _function_accuracy(original_vector, tagged_vector)
        accuracies.append(accuracy)

    avg_accuracy = sum(accuracies) / len(accuracies)
    return avg_accuracy


def compute_jump_metric(original_issues, tagged_issues):
    """
    Computes the average accuracy of the jump tagging.
    """
    accuracies = []

    for original_issue, tagged_issue in zip(original_issues, tagged_issues):
        original_vector = original_issue.tags_df["jump"].tolist()
        tagged_vector = tagged_issue.tags_df["jump"].tolist()
        accuracy, num_misses = _jump_accuracy(original_vector, tagged_vector)
        accuracies.append(accuracy)

    return sum(accuracies) / len(accuracies)