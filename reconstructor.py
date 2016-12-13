# reconstructor.py
# Jon Doughty

from fuzzywuzzy import fuzz
import argparse
import pandas as pd
import json
import re
import glob
import sys

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

    # get type of file we are working with (csv for tagged data, txt for raw)
    file_type = '*.csv' if args.tagged_data else '*.txt'

    # get all files in specified directory
    paths = glob.glob(os.path.join(args.data_dir[0], file_type))

    # columns for data frames
    columns = ["page", "article", "function", "paragraph", "jump", "ad", "text"]

    # generate list of untagged Issues()
    issue_list = gen_issue_list(args, paths, columns)

    # add supplemental coordinate data from tesseract
    if args.raw_data and args.coord:
        import ocrmerge
        ocrmerge.get_location_data(issue_list,
                                   image_dir="image_data",
                                   hocr_dir="hOCR_data")


    # If running raw data, tag all data with taggers and return in list
    if args.raw_data:
        tagged_issue_objs = run_taggers(issue_list)

    # if running metrics, don't output to JSON, output results of metrics.
    if args.metric_flag:
        run_metrics(tagged_issue_objs, columns)
        sys.exit(0)

    # create dictionary for tagged issues
    issue_dict = gen_issue_dict(issue_list)

    # output all data to JSON - one JSON file per article
    json_dump(issue_dict)


def run_taggers(issue_list):
    # taggers
    taggers = [pbt.tag, blt.tag, hlt.tag, jkt.tag, ttt.tag, jpt.tag, ant.tag]

    tagged_results = []

    for (pub_info, issue_obj) in issue_list:
        for tag in taggers:
            issue_obj = tag(issue_obj)
        if DEBUG:
            print (issue_obj.tags_df)
            input('Dataframe output above for debugging. Press any key to \
                   continue')

        # add tagged issue to results
        tagged_results.append((pub_info, issue_obj))

    return tagged_results


def gen_issue_dict(args, issue_list):
    issue_dict = {}
    for (pub_info, issue_obj) in issue_list:
        issue_df = construct_tagged(issue_obj, pub_info)

        issue_dict[pub_info] = issue_df.to_dict('records')

    return issue_dict


def gen_issue_list(args, paths, columns):
    issue_list = []

    # generate a list of Issue() objects to work with
    for path in paths:
        # strip publication information from file name
        pub_info = get_pub_info(path)

        if args.raw_data:
            # read in raw txt and convert to df
            df = gen_blank_df(path, columns)

        elif args.tagged_data:
            # read in the csv file and store as df
            df = pd.read_csv(path, header=2, names=columns)

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

    parser.add_argument('--metrics',
                        action='store_true',
                        dest='metric_flag',
                        help='Enable to print metrics, comparing tagged data \
                              to performance on raw data.')

    mut_exc = parser.add_mutually_exclusive_group(required=True)

    mut_exc.add_argument('--tagged',
                        action='store_true',
                        dest='tagged_data',
                        help='Flag to indicate training.')

    mut_exc.add_argument('--raw',
                        action='store_true',
                        dest='raw_data',
                        help='Flag to indicate testing.')

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
            article_date = get_date(issue_obj)
            article_number = str(article.article.values[0])
            num_paragraphs = get_num_paragraphs(article)
            subheading = get_subheading(article)
            id_num = get_id()
            article_data = {"id": id_num,
                            "publication" : pub_info,
                            "article_date": article_date,
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
    # Add command line argument to specify a directory output
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
    global id_count
    id_count += 1
    return str(id_count)


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


def get_date(issue_obj):
    '''Look up the issue date in an external spreadsheet.'''
    # external spreadsheet
    file_name = 'newspaper_dates.csv'
    # read spreadsheet into dataframe
    date_df = pd.read_csv(file_name)
    # get name to lookup row
    ids = issue_obj.filename.split('-')
    try:
        name = ids[4] + '-' + ids[5].split('.')[0]
        row = date_df.loc[date_df['Identifier'] == name]
        art_date = row['pub_date'].values[0]
    except:
        if DEBUG: print ('Date exception: ', e)
        art_date = None

    return art_date


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


def run_metrics(issue_list, columns):
    results = []   # (pub_info, precision, recall)
    # get the tagged data files and create dfs
    tagged_paths = glob.glob('tagged_data/*.csv')

    for (pub_info, issue_obj) in issue_list:
        issue_obj = tag_junk(issue_obj)
        tagged_fname = None
        for tagged_path in tagged_paths:
            if pub_info in tagged_path:
                tagged_fname = tagged_path
                break

        # open the tagged path as a df
        tagged_df = pd.read_csv(tagged_fname,
                                skiprows=[0,1],
                                header=None,
                                names=columns)

        # convert tags to JNK
        tagged_issue = tag_junk(Issue(tagged_df), replace_nan=True)

        # pass the two dataframes to comparison function
        precision,recall = compare_dfs(issue_obj.tags_df, tagged_issue.tags_df)

        # add result to list for writing to file
        results.append((pub_info, precision, recall))

    # write results to file
    with open('metrics.txt', 'w') as file_out:
        total_prec = 0
        total_rec = 0
        for pub_info,precision,recall in results:
            total_prec += precision
            total_rec += recall
            file_out.write('{} {:03f} {:03f}\n'.format(pub_info,precision,recall))
        total_prec /= len(results)
        total_rec /= len(results)
        file_out.write('Average precision: {:03f}\n'.format(total_prec))
        file_out.write('Average recall: {:03f}\n'.format(total_rec))


def compare_dfs(raw_df, tagged_df):
    '''Compare dfs line by line looking at various components to see how
       accurate they are.'''
    # assert dataframes have the same number of rows
    assert len(raw_df.index) == len(tagged_df.index)

    true_pos = 0    # row tagged correctly
    false_pos = 0   # row tagged incorrectly
    false_negs = 0  # row not tagged

    # raw_df.to_csv('raw_df_tag_junk.csv', na_rep='NAN')
    # tagged_df.to_csv('tagd_df_tag_junk.csv' ,na_rep='NAN')
    for i in range(len(raw_df.index)):
        # assert a text match to continue
        raw_text = str(raw_df.loc[i,'text'])
        tagd_text = str(tagged_df.loc[i+1,'text'])
        if i < 20 and raw_text and tagd_text != 'nan':
            fuzz_ratio = fuzz.partial_ratio(raw_text, tagd_text)
            assert fuzz_ratio >= 50, "row {} - text not equal: ^{}^:^{}^\n\
                ratio: {}".format(i, raw_text, tagd_text, fuzz_ratio)

        # get the function tags
        raw_func_tag = raw_df.loc[i,'function']
        tagd_func_tag = tagged_df.loc[i+1,'function']

        # test to see results ignoring JNK
        # if tagd_func_tag != 'JNK':

        # if not tag for raw_func_tag, false negative
        if not raw_func_tag:
            false_negs += 1
            continue

        # check if tags match
        if raw_func_tag == tagd_func_tag:
            true_pos += 1
        else:
            false_pos += 1

    # double check we counted every row
    assert true_pos + false_pos + false_negs == len(raw_df.index), 'missing \
        counts of some data, true_pos {}, false_pos: {}, false_negs {}'\
        .format(true_pos, false_pos, false_negs)

    # print ('true pos: ', true_pos)
    # print ('false pos: ', false_pos)
    # print ('false negs: ', false_negs)
    # print ('total rows ', len(raw_df.index))

    precision = true_pos / (true_pos + false_pos)
    recall = true_pos / (true_pos + false_negs)
    # print ("Precision", precision)
    # print ("Recall", recall)

    return precision,recall


if __name__ == "__main__":
    main()
