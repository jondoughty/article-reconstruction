import sys
import re
from os import listdir
from os.path import isfile, join
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import cgi
import json
import requests
import demjson
import html
import string

def search(url):
    r = requests.get(url)
    return r.content

def main(argv):

    url = "http://localhost:9200/sample/"
    search_st = argv[1]
    filter_str = argv[2]

    if (filter_str == 'headline'):
        search_filter = "article_headline"
    elif (filter_str == 'publication'):
        search_filter = "publication"
    elif (filter_str == 'author'):
        search_filter = "author"
    else:
        search_filter = "article_text"

    search_str = re.escape(search_st)
    content = search(url + "_search?q=" + search_filter + ":\"" + search_str + "\"&size=1")
    result = {}
    result = demjson.decode(content)
    headline = None
    article = None
    publication = None
    article_number = None
    page_number = None
    author = None
    article_date = None
    for i in result.keys():
        if i == "hits" and result["hits"]:
            for j in result["hits"].keys():
                if j == "hits" and result["hits"]["hits"]:
                    for val in result["hits"]["hits"]:
                        for k in val.keys():
                            headline = val["_source"]["article_headline"]
                            article  = val["_source"]["article_text"]
                            publication  = val["_source"]["publication"]
                            article_number = val["_source"]["article_number"]
                            page_number = val["_source"]["page_number"]
                            author = val["_source"]["author"]
                            article_date = val["_source"]["article_date"]
    if(headline == None):
        result = {}
        content = search(url + "_search?q=" + search_filter + ":" + search_str + "&size=1")
        result = demjson.decode(content)
        for i in result.keys():
            if i == "hits" and result["hits"]:
                for j in result["hits"].keys():
                    if j == "hits" and result["hits"]["hits"]:
                        for val in result["hits"]["hits"]:
                            for k in val.keys():
                                headline = val["_source"]["article_headline"]
                                article  = val["_source"]["article_text"]
                                publication  = val["_source"]["publication"]
                                article_number = val["_source"]["article_number"]
                                page_number = val["_source"]["page_number"]
                                author = val["_source"]["author"]
                                article_date = val["_source"]["article_date"]
   
    test_head = ''
    if not (headline is None):
    	for d in headline:
            if re.match('[a-zA-Z0-9 ]',d) or d in string.punctuation:
                test_head += d
    if(test_head == ''):
        print(headline)
    else:	
    	print(test_head)
    
    print(publication)
    test = ''
    if not (article is None):
    	for c in article:
            if re.match('[a-zA-Z0-9 ]',c) or c in string.punctuation:
                test += c
    if(test == ''):
        print(article)
    else:	
    	print(test)
    
    print(article_number)
    print(page_number)
    
    test_author = ''
    if not (author is None):
    	for e in author:
            if re.match('[a-zA-Z0-9 ]',e) or e in string.punctuation:
                test_author += e
    if(test_author == ''):
        print(author)
    else:	
    	print(test_author)
    
    print(article_date)

if __name__ == "__main__":
    main(sys.argv)

