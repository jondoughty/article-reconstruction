# basetagger.py

import pandas as pd
import numpy as np
import copy
import os


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

    def apply(self, col, func):
        # Applies function to column col.
        self.tags_df[col] = self.tags_df.apply(lambda row: func(row), axis=1)

    def print_rows(self, rows):
        # Prints the rows with the given index of the DataFrame.
        print(self.tags_df.iloc[rows])

    def to_csv(self, filename):
        # Prints the DataFrame to a file.
        self.tags_df.to_csv(filename)


def check_tags_exist(issue, tags):
    """
    Determines if issue.tags_df has been tagged with the tags.
    Owner: Nupur Garg
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


def print_accuracy_tag(orig_issues, tagged_issues, tag, print_incorrect=False):
    """
    Prints the accuracy of the function tag for the given issue.

    orig_issues: list
        Issue objects with original tags.
    tagged_issues: list
        Issue objects with code produced tags.
    tag: str
        Function tag to test.
    print_incorrect: bool
        Prints the incorrectly tagged lines (default: False).
    """
    total_missing = 0.0
    total_tags = 0.0

    print("=================================")
    print("============ Tag \'%s\' ============" %tag)
    print("=================================\n")
    for orig_issue, tagged_issue in zip(orig_issues, tagged_issues):
        expected_tags = orig_issue.tags_df[orig_issue.tags_df.function == tag]
        expected_tags_idx = set(expected_tags.index.values)

        actual_tags = tagged_issue.tags_df[tagged_issue.tags_df.function == tag]
        actual_tags_idx = set(actual_tags.index.values)

        missing_tags = expected_tags_idx - actual_tags_idx
        extra_tags = actual_tags_idx - expected_tags_idx

        total_missing += len(missing_tags)
        total_tags = len(expected_tags)

        if print_incorrect:
            print("----------- %s -----------" %orig_issue.filename)
            if missing_tags:
                print("\t\t----------- Missing -----------")
                print(expected_tags.loc[list(missing_tags)].text)
            if extra_tags:
                print("\t\t----------- Extra -----------")
                print(actual_tags.loc[list(extra_tags)].text)

    if total_tags > 0:
        accuracy = (total_tags - total_missing) / total_tags
        print("accuracy of %s: %.3f\n" %(tag, accuracy))
