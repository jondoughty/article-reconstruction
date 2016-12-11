#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Daniel Moore

from alignment_dhm.sequence import Sequence, GAP_ELEMENT
from alignment_dhm.vocabulary import Vocabulary
from alignment_dhm.sequencealigner import SimpleScoring, GlobalSequenceAligner
from distutils.spawn import find_executable
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


class BBox:
    def __init__(self, values):
        self.values = values

class Word:
    def __init__(self, text, titleAttribute, pageNum):
        self.text=text

        self._rawProperties = titleAttribute

        self._propertyMap = {}
        for propString in self._rawProperties.split(";"):
            items = propString.split()
            self._propertyMap[items[0]] = items[1:]

        self.bbox = BBox(self._propertyMap["bbox"])
        self.confidence = self._propertyMap["x_wconf"][0]
        self.pageNum = pageNum

class LocationData:
    def __init__(self, words, pageNum, tessText):
        self.words = words
        self.pageNum = pageNum
        self.tessText = tessText

    #def __str__(self):
    #    return "".join([
    #        "{ nodes:", self.nodes, \
    #        ", pageNum:", self.pageNum, \
    #        ", tessText:", self.tessText, "}"])
    def __repr__(self):
        #This can't be the right way to concat strings and ints
        return "".join(["{ number of nodes:", str(len(self.nodes)), \
                ", pageNum:", str(self.pageNum), \
                ", length of text:", str(len(self.tessText))])

def run_tesseract(img_path, out_hocr_path):

    if not find_executable("tesseract"):
        raise Exception("'tesseract.exe' not found on PATH")

    #Example:
    #tesseract ..\image_data\ua-nws_00000991_001.tif -l eng out hocr
    #print("Running tesseract on", img_path)
    subprocess.run(["tesseract", img_path, re.sub(r"\.hocr$", "", out_hocr_path), "-l", "eng", "hocr"]);
    #print("tesseract complete")

def get_tess_nodes(img_path, hocr_path, imgNum):

    #Skip tesseract if already run because image and tesseract settings
    #unlikely to change
    if not os.path.isfile(hocr_path):
        run_tesseract(img_path, hocr_path)

    hocr_tree = ET.parse(hocr_path)
    tree_root = hocr_tree.getroot()
    raw_nodes = tree_root.findall(r".//*[@class='ocrx_word']")

    #text = ""
    #for it in tree_root.itertext():
    #    text += it

    #strippedText = ""
    #for line in text.split("\n"):
    #    if (line.strip() != ""):
    #        strippedText = " ".join([strippedText, line.strip()])

    nodes = []
    strippedText = ""
    for node in raw_nodes:
        #TODO remove whitespace?
        wordText = ""
        #print(node)
        for childNodeText in node.itertext():
            wordText = " ".join([wordText, childNodeText.strip()]).strip()
            #print(childNodeText)
        if (wordText != ""):
            nodes.append(Word(wordText, node.get("title"), imgNum))
            #print("".join(["word", wordText, "fffff"]))
            strippedText = " ".join([strippedText, wordText])
    #print ("Blurb:", strippedText)
    return nodes, strippedText


def get_location_data(issue_list, image_dir, hocr_dir):
    #print("Starting get_location_data()")
    # TODO what if tesseract's ocr is *REALLY* bad?
    # maybe do a single global match score between the two to see
    vocab = Vocabulary()
    #print(issue_list)
    for (pub_info, issue) in issue_list:
        #print("Iterating through issue", pub_info)

        abbyy_line_idx_to_bbox_info = {}
        abbyy_lines = open(issue.filename, encoding="utf-8").readlines()

        nodes = []
        images_glob = os.path.join(image_dir, "*" + issue.get_issue_id() + "*.tif")
        #images_glob = os.path.join(image_dir, "*00003872*.tif")
        image_paths = glob.glob(images_glob)
        #print(image_paths)
        t_pages = ""
        pageData = {}
        for (img_path) in image_paths:
            str_img_idx = re.match(r"^.*_(\d{3})\.tif$", img_path).group(1)
            hocr_path = os.path.join(hocr_dir, "tess_" + issue.get_issue_id() + "_" + str_img_idx + ".hocr")
            words, pageText = get_tess_nodes(img_path, hocr_path, str_img_idx)
            pageData[str_img_idx] = LocationData(nodes, str_img_idx, pageText)
            t_pages = "".join([t_pages, pageText])
            nodes += words

        #TODO do this by individual pages
        #TODO use page number
        issue.tess_words = words
        print(words)

"""
        # Map t_pages idx to nodes idx for letters that begin nodes
        t_pages_idx_to_node_idx = {}
        i = 0
        j = 0
        #print(t_pages)
        #for j, node in enumerate(nodes):
        while i < len(t_pages) and j < len(nodes):
            #print("###", t_pages[i], "###", nodes[j].text[0], "###")
            if (t_pages[i] == nodes[j].text[0]):
                #print(i)
                #print(nodes[j].text)
                t_pages_idx_to_node_idx[i] = j
                #print(":::" + nodes[j].text + ":::")
                #print("---" + t_pages[i:len(nodes[j].text)+1] + "---")
                i += len(nodes[j].text)
                j += 1
            else:
                i += 1
        #print(i, ",", len(t_pages))
        assert(i == len(t_pages))


        #TODO maybe the whole rest of the function could be done encoded?
        t_pages_seq = Sequence(t_pages)
        t_pages_encoded = vocab.encodeSequence(t_pages_seq)
        scoring = SimpleScoring(2, -1)
        aligner = GlobalSequenceAligner(scoring, -2)

        # TODO maybe do a check here that t_pages matches tree_root.itertext()

        #print("tess_text:")
        #TODO fix
        for l_num, a_line in enumerate(abbyy_lines):
        #for l_num, a_line in enumerate(["iuifck vqwn"]):
        #for l_num, a_line in enumerate([r'afenfV01".xexvno.32Chondearfm;’GoooodJudgt’in,Danton-striations"Uaogood.ludgrnantlf’banofBtudantalvar']):
            #TODO filter alignment quality here
            #print("matching:================================================================")
            #print("a_line:", a_line)
            start, align_t, align_a = align(a_line, t_pages_seq, t_pages_encoded, vocab, aligner)

            #print("start:", start)
            #print("align_a:", align_a)
            #print("align_t:", align_t)
            # Map t_align idx to t_pages idx
            t_align_idx_to_t_pages_idx = {}
            i = start
            for j in range(len(align_t)):
                if (align_t[j] != GAP_ELEMENT):
                    t_align_idx_to_t_pages_idx[j] = i
                    # this second if line is going to throw off my Java...
                    i+=1

            a_idx_to_bbox = {}
            #TODO handle start < 0
            i = start
            for j in range(len(align_a)):
                # If this character is at the beginning of a word
                if t_align_idx_to_t_pages_idx[i] and t_align_idx_to_t_pages_idx[i] in t_pages_idx_to_node_idx:
                    for k in range(len(t_pages_idx_to_node_idx[t_align_idx_to_t_pages_idx[i]].text)):
                        if align_a[j+k] != GAP_ELEMENT:
                            a_idx_to_bbox[j+k] = t_pages_idx_to_node_idx[t_align_idx_to_t_pages_idx[i]].bbox.values
                            break
            #TODO or just add to the dataframe?
            #TODO what if there was no data returned
            abbyy_line_idx_to_bbox_info[l_num] = a_idx_to_bbox.items()
            #print(abbyy_line_idx_to_bbox_info[0])
    """

#TODO make sure the gap character is set right, see sequence.py
def align(first, second_seq, second_encoded, vocab, aligner):
    first_seq = Sequence(first)
    first_encoded = vocab.encodeSequence(first_seq)
    score, encodeds = aligner.align(first_encoded, second_encoded, backtrace=True)
    alignment = vocab.decodeSequenceAlignment(encodeds[0])
    #print("alignment:", alignment)
    firstSequence = alignment.first
    secondSequence = alignment.second
    align_t = secondSequence
    align_a = firstSequence
    start = encodeds[0].firstOffset
    return (start, align_t, align_a)


if __name__ == "__main__":
    get_location_data(*sys.argv[1:])


