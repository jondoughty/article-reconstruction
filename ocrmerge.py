# -*- coding: utf-8 -*-

import locale
import os
import sys
import xml.etree.ElementTree as ET


class BBox:
    def __init(self, parseMe):
        #TODO set member variables instead of string
        self.parseMe = parseMe


def main():
    ART_HOME=os.getcwd()
    #TODO validate arguments
    hOCRFilePath = sys.argv[1]
    abbyFilePath = sys.argv[2]

    hOCRTree = ET.parse(hOCRFilePath)

     #I don't know if i can handle the lack of camel case here...twitch...
    treeRoot = hOCRTree.getroot()

    # nodes = treeRoot.findall(".//*[@class='ocr_line']")
    # All descendants of "ocrx_word" elements
    #nodes = treeRoot.findall(".//*[@class='ocrx_word']//*")
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
    for node in nodes:
        #TODO bbox = BBox(node.get('title'))
        nodeText = ""
        #TODO check if this actually iterates over everything, in order
        for childText in node.itertext():
            nodeText += childText
        print(node.get('title'), nodeText)



if __name__ == "__main__":
    main()


