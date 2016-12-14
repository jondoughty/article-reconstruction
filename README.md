# article-reconstruction


## Contributors

    Aditya Budhwar
    Jon Doughty
    Vivian Fong
    Nupur Garg
    Daniel Kauffman
    Brandon Livitski


## Setup

  - Python 3
  - Pip 3
  - `pip3 install pyenchant`
  - `pip3 install pandas`
  - `pip3 install regex`
  - `pip3 install scipy`
  - `pip3 install sklearn`
  - `pip3 install fuzzywuzzy`
  - `pip3 install numpy`


## Running the Reconstructor

### With tagged data

    $ python3 reconstructor.py --tagged --data TAGGED_DATA_DIR

### With raw data

    $ python3 reconstructor.py --raw --data RAW_DATA_DIR

### To run calculations on raw data (data output to metrics.txt)

    $ python3 reconstructor.py --metrics --raw --data RAW_DATA_DIR

### For help with reconstructor.py

    $ python3 reconstructor.py --help


## Running Taggers

    Publication Tagger        python3 -m tagger.pubtagger
    Byline Tagger             python3 -m tagger.bltagger
    Headline Tagger           python3 -m tagger.hltagger
    Junk Tagger               python3 -m tagger.junktagger
    Text Tagger               python3 -m tagger.txttagger
    Jump Tagger               python3 -m tagger.pubtagger
    Article Number Tagger     python3 -m tagger.articlenumtagger


## Tag Information

    PI      Publication info        pubtagger.py
    BL      Byline                  bltagger.py
    HL      Headline                hltagger.py
    TXT     Article text            txttagger.py
    B       Blank line              junktagger.py
    N       Unidentifiable          junktagger.py
    AT      Advertisement text      junktagger.py
    OT      Other                   junktagger.py
    CN      Comic strip title       junktagger.py
    CT      Comic strip text        junktagger.py
    MH      Masthead                junktagger.py
    PH      Photo caption           junktagger.py
    BQN     Block quote name        junktagger.py
    BQA     Block quote author      junktagger.py
    BQT     Block quote text        junktagger.py
    SH      Section heading         junktagger.py
    ME      Meta directives         jumptagger.py
    NP      Nameplate               Incomplete


## Tesseract Output Format (hOCR)

See the `/examples` directory for an hOCR file and the image it came from. See [the hOCR spec](https://kba.github.io/hocr-spec/1.2/) for more info. Note that Tesseract may use an older version of the spec.


## Article Reconstructor Output Format

The JSON data output from Article Reconstructor used by Search Engine had the following fields for indexing and searching:

```
{
    "article_date": "<DATE/PL>",
    "id": "<number>",
    "page_number": "<number>",
    "article_headline": "<headline/HL>",
    "article_text": "<text/TXT>",
    "article_number": "<number/NUM>",
    "publication": "<publication/PUB>",
    "author": <ByLine/BL>,
    "number_of_paragraphs": "<number>",
    "article_subheading": "<string>",
    "link_article": [
		{
          "id": "",
          "link": ""
		}
	],
	"link_image": [
		{
          "id": "",
          "link": ""
		}
	]    
}
```


## Running Search
- Run Elasticsearch:
    - Copy `search/elasticsearch2.2.0` folder to the server
    - `cd search/elasticsearch2.2.0` (on server)
    - `./elasticsearch -d`
- Indexing:
    - `cd search/MD_Search`
    - `python3 index.py <path to json_data>`
- Search: UI is hosted at [http://frank.ored.calpoly.edu/MDSearch/index.html](http://frank.ored.calpoly.edu/MDSearch/index.html)
