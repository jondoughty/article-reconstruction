import pandas as pd
import numpy as np


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
   pass
