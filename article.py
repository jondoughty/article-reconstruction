import csv
import glob
import re

import pandas as pd


def main():
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
    paths = glob.glob("tagged_data/*.csv")
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]
    issue = pd.read_csv(paths[0], header = None, names = columns)
    article_nums = issue[(issue.article.notnull()) &
                         (issue.article != 0)].article.unique()
    articles = []
    print(article_nums)
    for n in article_nums:
        article = issue[issue.article == n]
        if len(article) > 0:
            paragraph_nums = article.paragraph[article.paragraph != 0].unique().tolist()
            assert(paragraph_nums == list(range(1, len(paragraph_nums) + 1)))
            try:
                headline = article[article.function == "HL"].text.values[0]
            except:
                headline = None
            try:
                byline = article[article.function == "BL"].text.values[0]
                match = re.match("[Bb][Yy]\s+(.*)", byline)
                author = match.group(1) if match else byline
            except:
                author = None
            pages = list(map(int, article.page.unique()))
            article_number = int(article.article.values[0])
            text = " ".join(article[article.function == "TXT"].text.values)
            article_data = {"article_date": "today",
                            "article_headline": headline, "page_number": pages,
                            "author": author, "article_number": n,
                            "article_text": text}
        articles.append(pd.Series(article_data))
    issue_df = pd.DataFrame(articles, index = range(1, len(articles) + 1))
    issue_df.index.name = "id"
    print(issue_df)


if __name__ == "__main__":
    main()
