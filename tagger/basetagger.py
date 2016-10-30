# basetagger.py

import pandas as pd
import numpy as np
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
    """

    COLUMNS = ["page", "article", "function", "paragraph", "jump", "ad", "text"]

    def __init__(self, tags_df):
        self.tags_df = tags_df
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
    Gets all the Issue objects from the folder.
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

    # Get test files in the folder.
    foldername = os.path.abspath(folder)
    for filename in os.listdir(foldername):
        full_filename = os.path.join(foldername, filename)
        if os.path.isfile(full_filename) and "csv" in filename:
            files.append(full_filename)

    # Create issue objects from the test files.
    for csv_file in files:
        issue = Issue(Issue.generate_tags_df(csv_file))

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
        issues.append(issue)

    return issues
