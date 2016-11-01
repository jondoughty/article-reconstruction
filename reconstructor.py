# reconstructor.py
# Jon Doughty

import glob
import sys
import json

from tagger.basetagger import *
import tagger.pubtagger as pbt
import tagger.hltagger as hlt
import tagger.bltagger as blt
import tagger.junktagger as jkt
import tagger.txttagger as ttt
import tagger.jumptagger as jpt
import tagger.articlenumtagger as ant


def main():
    # set panda options
    set_pd_options()

    # get all csv files in tagged_data directory
    paths = glob.glob("tagged_data/*.csv")

    # set columns for csv file
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]

    # create empty DataFrame
    tmp_df = pd.DataFrame()

    # create Issue object
    issue_obj = Issue(tmp_df)

    # call respective tag functions
    taggers = [pbt.tag, hlt.tag, blt.tag, jkt.tag, ttt.tag, jpt.tag, ant.tag]

    for tag in taggers:
        issue_obj = tag(issue_obj)

    # load csv
    # for path in paths:
    #     issue = pd.read_csv(path, header=2, names=columns)
    #     construct_tagged(issue)


def construct_tagged(issue):
    '''Reconstruct all articles of a single issue from a manually tagged csv
       file.'''
    article_nums = issue[(issue.article.notnull()) &
                         (issue.article != 0)].article.unique()
    articles = []
    for n in article_nums:
        article = issue[issue.article == n]
        if len(article) > 0:
            check_article(article)
            headline = get_headline(article)
            author = get_byline(article)
            text = get_text(article)
            pages = get_pages(article)
            article_number = int(article.article.values[0])
            article_data = {"article_date": "today",
                            "article_headline": headline, "page_number": pages,
                            "author": author, "article_number": n,
                            "article_text": text}
        articles.append(pd.Series(article_data))
    issue_df = pd.DataFrame(articles, index = range(1, len(articles) + 1))
    issue_df.index.name = "id"
    # print(issue_df)
    json_dump(issue_df)


def json_dump(issue_df):
    '''Dump an entire issue to json.'''
    tmp = issue_df.to_dict('records')
    print (json.dumps(tmp, indent=4))


def check_article(article):
    '''Assertions to confirm the article is tagged as expected'''
    # check correct paragraph ordering
    paragraph_nums = article.paragraph[article.paragraph != 0].unique().tolist()
    lst = list(range(1, len(paragraph_nums) + 1))
    if paragraph_nums != lst:
        article_num = article.article.unique()[0]
        print ('Paragraph numbering for article {} appears incorrect,'\
               ' please check.'.format(article_num))
        print ('paragraph numbering used: ', paragraph_nums)
        print ('paragraphs should be: ', lst)
        print ('\n')


def get_text(article):
    '''Return joined article text.'''
    # sort article by paragraph numbering before join
    article.sort_values(by='paragraph', ascending=True)

    # reconstruct text in order.
    return " ".join(article[article.function == "TXT"].text.values)


def get_headline(article):
    '''Extract headline from article.'''
    try:
        headline = article[article.function == "HL"].text.values[0]
    except:
        headline = None

    return headline


def get_byline(article):
    '''Extract author from article.'''
    try:
        byline = article[article.function == "BL"].text.values[0]
        match = re.match("[Bb][Yy]\s+(.*)", byline)
        author = match.group(1) if match else byline
    except:
        author = None
    return author


def get_pages(article):
    '''Extract pages from article.'''
    try:
        pages = list(map(int, article.page.unique()))
    except Exception as e:
        print ('Page exception: ', e)
        pages = None
    return pages


def set_pd_options():
    '''Set option for pandas.'''
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)


# def find_date(issue, max_error = 5):
#     dows = "|".join(calendar.day_name)
#     months = "|".join(calendar.month_name)[1:]
#     fmt_str = "(?:\s*({0})\s*.\s*({1})\s*([1-3]*[0-9]+)\s*.\s*" + \
#               "((?:19|20)[0-9]{{2}})\s*){{e<{2}}}"
#     pattern = regex.compile(fmt_str.format(dows, months, max_error),
#                             flags = regex.ENHANCEMATCH)
#     best_match = None
#     best_counts = sys.maxsize
#     for _, row in issue[issue.function == "PI"].iterrows():
#         match = regex.search(pattern, row.text, concurrent = True)
#         if match:
#             if best_match is None or match.fuzzy_counts < best_counts:
#                 best_match = match
#                 best_counts = match.fuzzy_counts
#     dow = edit_match(match.group(1), calendar.day_name)
#     month = edit_match(match.group(2), calendar.month_name)
#     day = edit_match(match.group(3), map(str, range(1, 32)))
#     year = edit_match(match.group(4), map(str, range(1901, 2021)))
#     return dow, month, day, year


# def edit_match(match, candidates):
#     return min(candidates,
#                key = lambda candidate: distance.edit_distance(match, candidate))


if __name__ == "__main__":
    main()
