# libntc.py
# Non-Text Content Library
# Daniel Kauffman

import glob
import string

import pandas as pd

import basetagger


def run_tests(tag_str, tag_fun, content_tags = []):
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
    paths = glob.glob("tagged_data/*.csv")
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]
    content_tags += ["TXT"]
    tps = []
    fps = []
    fns = []
    for path in paths[:2]:
        tags_df = pd.read_csv(path, header = 2, names = columns)
        tags_df = tags_df.dropna(how = "all")
        issue = basetagger.Issue(tags_df)
        actual = issue.tags_df.function.rename("actual")
        issue = tag_fun(issue)
        issue.tags_df = issue.tags_df.join(actual)
        tps.append(issue.tags_df[(issue.tags_df.actual == tag_str) &
                                 (issue.tags_df.function == tag_str)])
        fps.append(issue.tags_df[(issue.tags_df.actual.isin(content_tags)) &
                                 (issue.tags_df.function == tag_str)])
        fns.append(issue.tags_df[(issue.tags_df.actual == tag_str) &
                                 (issue.tags_df.function != tag_str)])
    tps = pd.concat(tps)
    fps = pd.concat(fps)
    fns = pd.concat(fns)
    print("\n\nTrue Positives:")
    print(tps)
    print("\n\nFalse Positives:")
    print(fps)
    print("\n\nFalse Negatives:")
    print(fns)
    print("\n\n\n")
    print("Precision", len(tps) / (len(tps) + len(fps)))
    print("Recall", len(tps) / (len(tps) + len(fns)))


def remove_punctuation(text):
    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    return text.translate(table).strip().upper()


