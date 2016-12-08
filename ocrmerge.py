#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Daniel Moore

from alignment.sequence import Sequence, GAP_ELEMENT
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner
from distutils.spawn import find_executable
import glob
import os
import re
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

def run_tesseract(img_path, out_hocr_path):

    if not find_executable("tesseract"):
        raise Exception("'tesseract.exe' not found on PATH")

    #Example:
    #tesseract ..\image_data\ua-nws_00000991_001.tif -l eng out hocr
    subprocess.run(["tesseract", img_path, re.sub(r"\.hocr$", "", hocr_path), "-l", "eng", "hocr"]);

def get_location_data(issue_list, image_dir, txt_dir, hocr_dir):
    print("Starting get_location_data()")
    # TODO what if tesseract's ocr is *REALLY* bad?
    # maybe do a single global match score between the two to see
    vocab = Vocabulary()
    print(issue_list)
    for (pub_info, issue) in issue_list:
        print("Iterating through issue ", pub_info)

        abbyy_line_idx_to_bbox_info = {}
        abbyy_lines = open(issue.filename, encoding="utf-8").readlines()

        images_glob = os.path.join(image_dir, issue.get_issue_id() + "*.tif")
        nodes = []
        for (img_path) in glob.glob(images_glob).sort():
            str_img_idx = re.search(r"_(\d{3})\.tif$", img_path).group(1)
            hocr_path = os.path.join(hocr_dir, "tess_" + issue.get_issue_id() + "_" + str_img_idx + ".hocr")

            run_tesseract(img_path, hocr_path)

            hocr_tree = ET.parse(hocr_path)
            tree_root = hocr_tree.getroot()
            raw_nodes = tree_root.findall(r".//*[@class='ocrx_word']")
            for node in raw_nodes:
                nodes.append(Word(node))


        # Map t_page idx to nodes idx for letters that begin words
        t_page_idx_to_node_idx = {}
        i = 0
        t_page = ""
        for j, node in enumerate(nodes):
            t_page_idx_to_node_idx[i] = j
            i += len(node.text)
            t_page += node.text

        #TODO maybe the whole rest of the function could be done encoded?
        t_page_encoded = vocab.encodeSequence(t_page)
        scoring = SimpleScoring(2, -1)
        aligner = GlobalSequenceAligner(scoring, -2)

        # TODO maybe do a check here that t_page matches tree_root.itertext()

        for l_num, a_line in abbyy_lines:
            #TODO filter alignment quality here
            start, align_t, align_a = alignment(a_line, t_page, t_page_encoded, vocab, aligner)

            # Map t_align idx to t_page idx
            t_align_idx_to_t_page_idx = {}
            i = start
            for j in range(len(align_t)):
                if (align_t[j] != GAP_ELEMENT):
                    t_align_idx_to_t_page_idx[j] = i
                    # this second if line is going to throw off my Java...
                    i+=1

            a_idx_to_bbox = {}
            #TODO handle start < 0
            i = start
            for j in range(len(align_a)):
                # If this character is at the beginning of a word
                if t_align_idx_to_t_page_idx[i] in t_page_idx_to_node_idx:
                    for k in range(len(t_page_idx_to_node_idx[t_align_idx_to_t_page_idx[i]].text)):
                        if align_a[j+k] != GAP_ELEMENT:
                            a_idx_to_bbox[j+k] = t_page_idx_to_node_idx[t_align_idx_to_t_page_idx[i]].bbox.values
                            break
            #TODO or just add to the dataframe?
            #TODO what if there was no data returned
            abbyy_line_idx_to_bbox_info[l_num] = a_idx_to_bbox.items()
            print(abbyy_line_idx_to_bbox_info[0])

#TODO make sure the gap character is set right, see sequence.py
#start, align_t, align_a = alignment(a_line, t_page)
def align(first, second, second_encoded, aligner):
    first_encoded = vocab.encodeSequence(first)
    score, encodeds = aligner.align(first_encoded, second_encoded, backtrace=True)
    alignment = vocab.decodeSequenceAlignment(encodeds[0])
    firstSequence = alignment.first
    secondSequence = alignment.second
    align_t = secondSequence
    align_a = firstSequence
    start = alignment.firstOffset
    return (start, align_t, align_a)


if __name__ == "__main__":
    get_location_data(*sys.argv[1:])


