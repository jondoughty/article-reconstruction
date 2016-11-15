#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import xml.etree.ElementTree as ET


class BBox:
    def __init__(self, values):
        self.values = values

class Word:
    def __init__(self, xmlNode):
        self.text=""
        #TODO check if this actually iterates over everything, in order
        for childNodeText in xmlNode.itertext():
            self.text += childNodeText

        self._rawProperties = xmlNode.get("title")

        self._propertyMap = {}
        for propString in self._rawProperties.split(";"):
            items = propString.split()
            self._propertyMap[items[0]] = items[1:]

        self.bbox = BBox(self._propertyMap["bbox"])
        self.confidence = self._propertyMap["x_wconf"][0]

def main():
    ART_HOME=os.getcwd()
    NUM_WORDS=5
    #TODO validate arguments
    #TODO usage?
    hOCRFilePath = sys.argv[1]
    abbyyFilePath = sys.argv[2]

    hOCRTree = ET.parse(hOCRFilePath)

     #I don't know if i can handle the lack of camel case here...twitch...
    treeRoot = hOCRTree.getroot()

    # nodes = treeRoot.findall(".//*[@class='ocr_line']")
    # All descendants of "ocrx_word" elements
    #nodes = treeRoot.findall(".//*[@class='ocrx_word']//*")

    # TODO check for meta ocr-capabilities (ocrx_word vs ocr_word)
    # TODO if that doesn't work, look at actual tags
    # TODO Maybe we should find lines first so that we can preserve the association
    # between words and the line bbox
    nodes = treeRoot.findall(".//*[@class='ocrx_word']")

#1 find all ocrx_word elements
#2 for each
#3    get title -> get bbox
#4    get all child elements
#5    for each
#6      get child nodes 
#
#      node.itertext?
#      node.tail?

    print("Nodes found:", len(nodes))

    hocrLines = []
    i = 0
    phraseLength = 3
    while i < len(nodes):
        j = 0
        while j < phraseLength & i + j < len(nodes):
            hocrLines += nodes[i + j]
            j+=1
        i+=phraseLength

    for node in nodes:
        w = Word(node)
        print(w.text, w.bbox.values)

    abbyyLines = open(abbyyFilePath, encoding="utf-8").readlines()

    #for line in abbyyLines:
        #print(line)


if __name__ == "__main__":
    main()


