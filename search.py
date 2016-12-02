import sys
from os import listdir
from os.path import isfile, join
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import cgi
import json
import requests

def indexData(directory, url):
    all_files = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
    for file_name in all_files:
        with open(file_name, 'r') as content_file:
            content = content_file.read()
            r = requests.post(url, data=content.encode(encoding='utf-8'))
            #print(r.status_code, r.reason)  # HTTP
    print("Indexing Done")

def createIndex(url, settings):
    d = requests.delete(url)
    r = requests.post(url, data=settings.encode(encoding='utf-8'))
    #print(r.status_code, r.reason)

def search(url):
    print(url)
    r = requests.get(url)
    #print(r.status_code, r.reason)
    print("Result: ", r.content)

def main(argv):

    if (len(argv) < 4):
        print("Usage : Python ES.py data_dir url settings_file")
        #python ES.py /NLP/Project_ArticleR/json_output http://localhost:9200/sample/ /NLP/Project_ArticleR/Mapping.txt
        return

    data_dir = argv[1]
    url = argv[2]
    settings_file = argv[3]
    with open(settings_file, 'r') as settings_f:
        settings = settings_f.read()

    createIndex(url, settings)
    indexData(data_dir, url + "/article_search")

    while (True):
        x = input("Type the search query('q' to quit): ")
        if x == 'q':
            break
        search(url + "_search?q=article_text:" + x)

if __name__ == "__main__":
    main(sys.argv)
