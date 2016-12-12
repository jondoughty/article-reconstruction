# reconstructor.py
# Jon Doughty

import argparse
import pandas as pd
import json
import glob
import sys
import re

from tagger.basetagger import *
import tagger.pubtagger as pbt
import tagger.hltagger as hlt
import tagger.bltagger as blt
import tagger.junktagger as jkt
import tagger.txttagger as ttt
import tagger.jumptagger as jpt
import tagger.articlenumtagger as ant

DEBUG = None

def main():
    global DEBUG

    # parse command line args.
    parser = setup_args()
    args = parser.parse_args()

    # set debug flag
    DEBUG = args.debug_flag

    # set panda options
    set_pd_options()

    #TODO set a global setting instead of just filetype so other code can use it
    # get type of file we are working with (csv for tagged data, txt for raw)
    file_type = '*.csv' if args.tagged_data else '*.txt'

    # get all files in specified directory
    paths = glob.glob(os.path.join(args.data_dir[0], file_type))
    #TODO remove
    #paths = glob.glob(os.path.join('./raw_data/*00003872*.txt'))

    # generate list of untagged Issues()
    issue_list = gen_issue_list(args, paths)

    if args.raw_data and args.coord:
        import ocrmerge
        ocrmerge.get_location_data(issue_list, image_dir="image_data", hocr_dir="hOCR_data")

    # dictionary for tagged issues
    issue_dict = gen_issue_dict(args, issue_list)

    # output all data to JSON - one JSON file per article
    json_dump(issue_dict)


def gen_issue_dict(args, issue_list):
    # taggers
    taggers = [pbt.tag, blt.tag, hlt.tag, jkt.tag, ttt.tag, jpt.tag, ant.tag]

    issue_dict = {}
    # if raw_data - call respective tag functions
    for (pub_info, issue_obj) in issue_list:
        if args.raw_data:
            for tag in taggers:
                issue_obj = tag(issue_obj)
                print (issue_obj.tags_df)
                print("num headlines:", len(issue_obj.tags_df[issue_obj.tags_df.function == "HL"]))
                input()

        # create a dataframe for the entire issue
        issue_df = construct_tagged(issue_obj, pub_info)

        tmp = issue_df.to_dict('records')
        issue_dict[pub_info] = tmp

    return issue_dict


def gen_issue_list(args, paths):
    issue_list = []

    # columns for data frames
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]

    # generate a list of Issue() objects to work with
    for path in paths:
        # strip publication information from file name
        pub_info = get_pub_info(path)

        if args.raw_data:
            # read in raw txt and convert to df
            df = gen_blank_df(path, columns)
            # Wrap df with in Issue()


        elif args.tagged_data:
            # read in the csv file and store as df
            df = pd.read_csv(path, header=2, names=columns)

        # TODO: add pub_info to Issue()
        issue = Issue(df, path)

        # Add to list with publication info
        issue_list.append((pub_info, issue))

    return issue_list


def gen_blank_df(txt_path, columns):
    '''Given the path for a single text file, create a data frame for that
       contains its text in the text column.'''
    # create an empty data frame
    df = pd.DataFrame(columns=columns)

    # gata data in lines variable
    with open(txt_path, 'r', encoding="utf-8") as file_in:
        lines = [line.rstrip("\n") for line in file_in.readlines()]

    df['text'] = lines

    # print (df)
    return df


def get_pub_info(file_name):
    '''Use RE to extract the publication info from a path.
       Info has numerical format XXXX-XX-XXX'''
    pub_info = None

    match = re.search('\d{4}-\d{2}-\d{3}', file_name)
    if match:
        # print (match.group(0))
        pub_info = match.group(0)

    return pub_info


def setup_args():
    parser = argparse.ArgumentParser(description='Article reconstruction \
    driver script to call and amalgamate results from various taggers.')

    parser.add_argument('--debug',
                    action='store_true',
                    dest='debug_flag',
                    help='Enable for debugging information.')

    mut_exc = parser.add_mutually_exclusive_group(required=True)

    mut_exc.add_argument('--tagged',
                    # metavar='STUB',
                    action='store_true',
                    dest='tagged_data',
                    help='Flag to indicate training.')

    mut_exc.add_argument('--raw',
                    # metavar='STUB',
                    action='store_true',
                    dest='raw_data',
                    help='Flag to indicate testing.')

    #TODO this really should be made only valid when --raw is also given
    parser.add_argument('--coord',
                    action='store_true',
                    dest='coord',
                    help='Flag to use coordinate data (experimental)')


    req = parser.add_argument_group('required arguments')

    req.add_argument('--data',
                    required=True,
                    metavar='DATA_DIR',
                    type=str,
                    nargs=1,
                    dest='data_dir',
                    help='Directory which contains data for training or \
                    testing')
    return parser



def construct_tagged(issue_obj, pub_info):
    '''Reconstruct all articles of a single issue from a manually tagged csv
       file. Add to issue_dict.'''
    # get the tagged df from the Issue()
    issue = issue_obj.tags_df

    # get the article numbers
    article_nums = issue[(issue.article.notnull()) &
                         (issue.article != 0)].article.unique()
    articles = []
    for n in article_nums:
        article = issue[issue.article == n]
        if len(article) > 0:
            if DEBUG: check_article(article)
            headline = get_headline(article)
            author = get_byline(article)
            text = get_text(article)
            pages = get_pages(article)
            article_number = str(article.article.values[0])
            num_paragraphs = get_num_paragraphs(article)
            subheading = get_subheading(article)
            id_num = get_id()
            article_data = {"id": id_num,
                            "publication" : pub_info,
                            "article_date": "today",
                            "article_headline": headline,
                            "page_number": pages,
                            "author": author,
                            "article_number": article_number,
                            "article_text": text,
                            "article_subheading": subheading,
                            "number_of_paragraphs":num_paragraphs,
                            "link_image": [],
                            "link_article": []}

        articles.append(pd.Series(article_data))

    issue_df = pd.DataFrame(articles, index=range(1, len(articles) + 1))
    issue_df.index.name = "id"

    # print (issue_df)
    # input()

    return issue_df


def json_dump(issue_dict):
    '''Dump an entire issue to JSON, creating a separate JSON file for
       each article.'''
    # TODO: add command line argument to specify a directory output
    directory = "json_output/"

    # issue_dict is a dictionary of {pub_info : [articles]}
    for key, articles in issue_dict.items():
        for article in articles:
            article_num = article['article_number']
            file_name = directory + key + "_" + article_num + '.json'
            with open(file_name, 'w') as json_out:
                json.dump(article, json_out, indent=4, ensure_ascii=False)


id_count = 0
def get_id():
    # TODO: will need to persist the last ID number used for creating
    # additional JSON output.
    global id_count
    id_count += 1
    return str(id_count)


def get_subheading(article):
    return None


def get_num_paragraphs(article):
    paragraph_nums = article.paragraph[article.paragraph != 0].unique().tolist()
    return str(len(paragraph_nums))


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
    except Exception as e:
        if DEBUG: print ('Headline exception: ', e)
        headline = None

    return headline


def get_byline(article):
    '''Extract author from article.'''
    try:
        # byline = article[article.function == "BL"].text.values[0]
        author = article[article.function == "BL"].text.values[0]
        # match = re.match("[Bb][Yy]\s+(.*)", byline)
        # author = match.group(1) if match else byline
    except Exception as e:
        if DEBUG: print ('Byline exception: ', e)
        author = None

    return author


def get_pages(article):
    '''Extract pages from article.'''
    try:
        pages = str(list(map(int, article.page.unique()))).strip('[]')
    except Exception as e:
        if DEBUG: print ('Page exception: ', e)
        pages = None

    return pages


def set_pd_options():
    '''Set option for pandas.'''
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)


if __name__ == "__main__":
    main()
