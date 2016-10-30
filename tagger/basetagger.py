import pandas as pd
import numpy as np
import os


class Issue(object):
    """
    Represents a newspaper issue.

    tags_df: DataFrame
        Represents a tagged newspaper.
    date: str
        Date the issue was published.
    edition: (int, int)
        Represents (volume #, issue #).
    """

    def __init__(self, tags_df):
        self.tags_df = tags_df
        self.date = None
        self.edition = None

    def __str__(self):
        return '%s, %s' %(str(self.date), str(self.edition))


def check_tag_exists(issue, tags):
    """
    Determines if issue.tags_df has been tagged with the tags.
    Owner: Nupur Garg
    """
    unique_tags = issue.tags_df.tags_df.unique()
    return set(tags).issubset(unique_tags)


def get_issues(folder='tagged_data', clear_columns=None, clear_tags=None):
    """
    Gets all the Issue objects from the folder. Clears the columns in
    clear_columns in tags_df for each Issue.
    Owner: Nupur Garg
    """
    files = []
    issues = []
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]

    # Get test files in the folder.
    foldername = os.path.abspath(folder)
    for filename in os.listdir(foldername):
        full_filename = os.path.join(foldername, filename)
        if os.path.isfile(full_filename) and 'csv' in filename:
            files.append(full_filename)

    # Create issue objects from the test files.
    issues = [Issue(pd.read_csv(path, header=1, names=columns)) for path in files]

    # TODO: CLEAR COLUMNS
    # TODO: CLEAR TAGS
    
    return issues
