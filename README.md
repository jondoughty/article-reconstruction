# article-reconstruction

## Running Taggers

  Junk Tagger     python3 -m tagger.junktagger      Ads, classifiers, BQT
  Text Tagger     python3 -m tagger.txttagger       TXT

## Tag Information

  Labeled

    TXT     Article text            txttagger.py
    B       Blank line              junktagger.py
    N       Unidentifiable          junktagger.py
    AT      Advertisement text      junktagger.py
    OT      Other                   junktagger.py
    CN      Comic strip title       junktagger.py
    CT      Comic strip text        junktagger.py
    MH      Masthead                junktagger.py
    PH      Photo caption           junktagger.py

  Not Labeled

    PI      Publication info
    SH      Section heading
    HL      Headline
    BL      Byline
    NP      Nameplate
    ME      Meta directives
    BQT     Block quote text
    BQN     Block quote name

## Setup

  pip3 install pyenchant

## Tesseract Output Format (hOCR)
See the **/examples** directory for an hOCR file and the image it came from. See [the hOCR spec](https://kba.github.io/hocr-spec/1.2/) for more info. Note that Tesseract may use an older version of the spec.

## Article Reconstructor Output Format

- The fields which are decided as final output for the Article regeneration, are mentioned below as JSON. These fields will act as input to search module for indexing and searching. {Items commented still TBD}
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

