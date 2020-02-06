# -*- coding: utf-8 -*-
# @Author: Jefferson Amado
# @Date:   2019-04-18 13:35:13
"""
This script accesses the European PMC API with queries written inside the
'data' dictionary. Output is a tab-delimited list of information from these publications.
tagged in the comment as [MODIFY THIS]:
    pay attention to these values when editing this script
API documentation at: https://europepmc.org/RestfulWebService#!/Europe32PMC32Articles32RESTful32API
"""
import requests
import json
import time
import datetime
from pprint import  pprint
import asyncio

# Euro PMC API url
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
URL_SEARCH = URL + "/search?"

def get_papers_by_keyword(keywords, offset=0, limit = 20, custom_params=None,
                          o_access="Y", database = "pubmed", ordering=None):
    # check if there is an outbound network first
    keywords = " OR ".join(keywords.split(","))
    data = {
        "query": "{} AND OPEN_ACCESS:{}".format(keywords, o_access),
        "resultType": "lite", "synonymn": "",
        "cursorMark": "*",
        "pageSize": "1000",  # valid page size 1-1000 only
        "sort": "", "format": "json",
        "callback": "", "email": "",
    }
    data = custom_params if custom_params else data
    response = _request_all_results(data)
    response = {"{}".format(pub['id']): pub for pub in response}
    return response

def _request_query(data, cursor_mark='%2A'):
    data["cursorMark"] = cursor_mark
    try:
        with requests.get(URL_SEARCH, params=data) as response:
            output = json.loads(response.text[1:-1]) # remove start and end parenthesis
            return output
        # else:
            # print(f"An error occurred. {response.status_code}")
    except requests.exceptions.ConnectionError as cnt:
        print("\nA connection error occured. Check your network.")

def _request_all_results(data, verbose=False):
    cursor_mark = '*'
    done = False
    results = []
    count = 0
    # try:
    while not done:
        try:
            with requests.get(URL_SEARCH, params=data) as response:
                page_result = json.loads(response.text[1:-1]) # remove start and end parenthesis
                results.extend(page_result['resultList']['result'])
                done = cursor_mark == page_result['nextCursorMark']
                cursor_mark = page_result['nextCursorMark']
                data["cursorMark"]= page_result['nextCursorMark']
                if len(results) > 9000: done= True
                print("No. results: {}".format(len(results)))
        except Exception as e:
            time.sleep(150)
            print("wait, ")

    return results

def documents2str(results):
    hits = results["resultList"]["result"]
    infos = ["isOpenAccess", "citedByCount",
            "id", "pmcid", "pmid",
            "authorString",
            "title", "journalTitle",
            "pubYear", "journalVolume",
            "pageInfo", "doi"]
    output = ""
    for hit in hits:
        for info in infos:
            try:
                output = output + str(hit[info])
            except KeyError:
                pass
        output = output +"\n"
    return output

def to_file(results, outf_name="records", format="txt"):
    hits = results["resultList"]["result"]
    infos = ["isOpenAccess", "citedByCount",
            "id", "pmcid", "pmid",
            "authorString",
            "title", "journalTitle",
            "pubYear", "journalVolume",
            "pageInfo", "doi"]
    outf_name = "{}.{}".format(outf_name, format)
    with open(outf_name, "a", encoding="utf-8") as outf:
        if format != "txt":
            print(results, file=outf)
            return

        print(";".join(infos), file=outf)
        for hit in hits:
            ret_infos = []
            for info in infos:
                try:
                    ret_infos.append(str(hit[info]))
                except KeyError:
                    ret_infos.append("")
            print(";".join(ret_infos), file=outf)
    print("Output written in {}".format(outf_name))

