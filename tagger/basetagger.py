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
        date = None
        edition = None


def check_tag_exists(issue, tags):
    """
    Determines if issue.tags_df has been tagged with the tags.
    Owner: Nupur Garg
    """
    unique_tags = issue.tags_df.tags_df.unique()
    return set(tags).issubset(unique_tags)


def get_issues(folder, clear_columns):
    """
    Gets all the Issue objects from the folder. Clears the columns in
    clear_columns in tags_df for each Issue.
    Owner: Nupur Garg
    """
    folder_name = os.path.abspath(folder)
    print(folder_name)
    pass
