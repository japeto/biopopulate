# import dependencies
import typing
import json
import re
import time
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
# from api.core import logger
# from libs import tagger


base_url = "https://www.ebi.ac.uk/europepmc/webservices/"
annotations_url = "https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds?"


def get_annotations(identifier, annotation="disease", source="PMC"):
    try:
     with requests.get(f"{annotations_url}articleIds="
                       f"{identifier}&type={annotation}&format=JSON") as annotations:
        if source:
            annotations = requests.get(f"{annotations_url}articleIds="
                                       f"{source}%3A{identifier}&type={annotation}&format=JSON")
        if annotations.status_code == 200:
            try:
                response = json.loads(annotations.text)
                response = response[0] if len(response)>0 else None
            except Exception as exp:
                exp
            annotations = {"chemicals": [], "organisms": [], "gene_proteins": [],
                           "diseases": [], "gene_ontology": [], "proteins":[], "Drugs":[]}
            if not(response):
                return annotations
            response = response['annotations']
            for tag in response:
                key = tag['type'].lower().replace(" ", "_")
                val = tag['exact'].lower()
                try:
                    None if val in annotations[key] else annotations[key].append( val )
                except Exception as exp:
                    annotations[key]:[val]
            return annotations
    except:
        pass

def get_article(identifier, annotations=None) -> dict:
    try:
        with requests.get(f"{base_url}rest/{identifier}/fullTextXML") as response:
            full_xml = response.text
            article = {}
            try:
                root = ET.fromstring(full_xml)
                if not(root): return article
                article["title"] = root.findtext('.//article-title')
                elem = root.find('body')
                article["body"] =_iterate_get_text(elem) if elem else ""
            except Exception as e:
                time.sleep(150)
                print(e)
                pass
            tagged=_merge_textannotations(annotations, article)
            article['tagged'] = tagged
            return article
    except Exception as e:
        pass

def _iterate_get_text(elem):
    """
    get all inner text values of this element with special cares of
    1) ignoring not relevant nodes, e.g., xref, table
    2) making section/title texts identifiable by the sentence tokenizer
    Args:
        elem:
    Returns:
    """
    remove_tags = ['table']
    line_break_tags = ['sec', 'title']
    s = ''
    if elem.tag not in remove_tags:
        if elem.tag in line_break_tags and not (elem.text is None):
            s += f"\n{elem.text.strip()}\n" if not(elem.text is None) else ''
        else:
            s += f"{elem.text.strip()} " if not (elem.text is None) else ''
        for e in list(elem):
            ct = _iterate_get_text(e)
            s += (' ' + ct) if len(ct) > 0 else ''
    s += elem.tail.strip() + ' ' if elem.tail is not None else ''
    return s

def _merge_textannotations(annotations=None, article=None) -> str:
    if not(annotations):
        return article['body']
    tagged = article["body"].replace("\n", "<br/>") # remove jumps
    for key in annotations:
        for word in annotations[key]:
            tagged = re.sub(r'\b{}\b'.format(word), f"<{key}>{word}</{key}>", tagged)
    return tagged
