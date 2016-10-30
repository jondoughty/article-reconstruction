# junktagger.py
# Nupur Garg

import copy

from basetagger import *


def tag(issue):
    issue = copy.deepcopy(issue)
    return issue


def main():
    issues = get_issues(clear_columns=[''], clear_tags=None)
    print([str(issue) for issue in issues])


if __name__ == "__main__":
    main()
