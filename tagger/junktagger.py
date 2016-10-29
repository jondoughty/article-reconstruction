# junktagger.py
# Nupur Garg

from basetagger import *


def tag(issue):
    return issue


def main():
    issues = get_issues(folder='tagged_data',
                              clear_columns=[''])


if __name__ == "__main__":
    main()
