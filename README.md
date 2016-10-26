# article-reconstruction


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

