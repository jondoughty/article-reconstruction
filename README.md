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

The fields which are decided as final output for the Article regeneration, are mentioned below as JSON. These fields will act as input to search module for indexing and searching. {Items commented still TBD}

```
{
  "articles": [
    {
      "id": "001",
      "article_date": "<DATE/PL>",
      "article_headline": "title/HL",
      "page_number": "<number/PL>",
      "author": "<BY LINE/BL>",
      "article_number": "<number>/PL",
      "article_text": "text/TXT",
      "link to article image": [
        {
          "id": "",
          "link": ""
        },
        {
          "id": "",
          "link": ""
        }
      ],
      "link to images in article": [ //TBD
        {
          "id": "",
          "link": ""
        },
        {
          "id": "",
          "link": ""
        }
      ],
      "article_subheading": "XYZ/TXT", //TBD
      "number of paragraphs": "3/TXT" //TBD
    }
  ]
}
```


## Running Search
- Run Elasticsearch:
    - Copy `search/elasticsearch2.2.0` folder to the server
    - Execute following command from  folder `./elasticsearch -d`
- Indexing:
    - `cd search/MD_Search`
    - `$python3 index.py <path to json_data>`
- Search: UI is hosted at `http://frank.ored.calpoly.edu/MD_Search/index.html`
