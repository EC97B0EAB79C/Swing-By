#!/usr/bin/env python

# Standard library imports
import logging
import os
import re

# Third-party imports
import bibtexparser
import pandas
import yaml
import arxiv
from crossref_commons.iteration import iterate_publications_as_json
from crossref_commons.retrieval import get_publication_as_json
import requests

# Global Parameters
N = 10
RATIO = 0.4
# DB_LOCATION = os.environ.get("PAPER_REL_DB")
DB_LOCATION = "./test/test.h5"
TOKEN = os.environ["GITHUB_TOKEN"]
ADS_API_KEY = os.environ["ADS_API_KEY"]


# Warning Messages
KEYWORD_WARNING_TEXT = """\033[33mWARNING\033[0m: There is error in number of keywords.
\tCreated ({count}): {keywords}
\tDo you want to proceed? (y/N): """
DB_WARNING_TEXT = f"\033[33mWARNING\033[0m: Error when loading DB.\n\tDo you want to create new DB at '{DB_LOCATION}'? (y/N): "
QUERY_WARNING_TEXT = """\033[33mWARNING\033[0m: Fetched paper might be not correct ({service})
\tQuery: {query}
\tFetched: {fetched}
\tDo you want to use fetched paper? (y/N):"""
REF_WARNING_TEXT = f"\033[33mWARNING\033[0m: Failed to fetch references.\n\tDo you want to proceed? (y/N): "
def process_warning(message, abort = False):
    user_continue = input(message) == 'y'
    if abort and not user_continue:
        logger.fatal("\033[31mABORTED\033[0m")
        exit(1)
    return user_continue
        

##
# Set up argument parser and logging
import argparse
parser = argparse.ArgumentParser(
    prog='paper_rel_gen',
    description='Processes markdown notes with BibTeX to add metadata to paper notes.'
    )
parser.add_argument(
    'filename',
    help='Markdown file to process.'
    )
parser.add_argument(
    '--keyword-only',
    action='store_true',
    help='Only prints keywords without updating DB or file.'
    )
parser.add_argument(
    '--article',
    '-a',
    action='store_true',
    help='Query arXiv and Crossref for article.'
    )
parser.add_argument(
    '--debug', 
    action='store_true', 
    help='Enable debug mode'
    )
args = parser.parse_args()

# Check if global variabble is set for DB
if (not args.keyword_only) and (not DB_LOCATION):
    logging.error("Environment variable 'PAPER_REL_DB' should be set to use vector storage.")
    logging.error("\033[31mABORTED\033[0m")
    exit(1)

# Set logger
level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level)


##
# Utils
def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9]+", ' ', text).lower()

from difflib import SequenceMatcher
def same_text(text1, text2):
    clean_text1 = clean_text(text1)
    clean_text2 = clean_text(text2)
    return SequenceMatcher(None, clean_text1, clean_text2).ratio() > 0.99

def check_title(title1, title2, message, abort=False):
    if same_text(title1, title2):
        return True
    return process_warning(message, abort)


##
# DB
# PaperDB: key, title, author, year, bibtex_key, doi, bibcode, keywords, filename, 
#       title_embedding, summary_embedding, body_embedding
# RefDB: key, doi_ref, bibcode_ref
class PaperDB:
    def __init__(self):
        self.paper_db = None
        self.ref_db = pandas.DataFrame(columns=['doi', 'doi_ref', 'bibcode_ref'])

    def load(self):
        logger.debug("Loading DB")
        try:
            self.paper_db = pandas.read_hdf(DB_LOCATION, key='paper')
            self.ref_db = pandas.read_hdf(DB_LOCATION, key='ref')
            logger.debug(f"Loaded {len(self.paper_db.index)} entries from DB")
        except Exception as e:
            logger.error(e)
            process_warning(DB_WARNING_TEXT, abort=True)

    def save(self):
        logger.debug("Saving DB")
        try:
            with pandas.HDFStore(DB_LOCATION, mode='w') as store:
                store.put('paper', self.paper_db)
                store.put('ref', self.ref_db)
        except Exception as e:
            logger.error("Error when saving to DB")
            logger.error(e)
            exit()
        logger.info(f"Saved {len(self.paper_db.index)} entries to DB")

    def append_entry(self, entry):
        new_df = pandas.DataFrame.from_dict([entry])
        if type(self.paper_db) != pandas.DataFrame:
            self.paper_db = new_df
            return
        self.paper_db = self.paper_db.set_index('key').combine_first(new_df.set_index('key')).reset_index()


##
# File read/write
def read_file_lines(path):
    logger.debug(f"Reading file: {path}")
    with open(path, 'r') as file:
        lines = file.readlines()
    return lines

def write_file(path, data):
    logger.debug(f"Writing file: {path}")
    with open(path, 'w') as file:
        file.write(data)


##
# Process file
def extract_yaml(markdown: list[str]):
    logger.debug("Extracting yaml metadata")
    while markdown[0].strip() =='':
        markdown = markdown[1:]
    if '---' not in markdown[0].strip():
        return {}, ''.join(markdown)

    markdown = markdown[1:]
    for idx, line in enumerate(markdown):
        if '---' in line.strip():
            yaml_end = idx
            break

    yaml_text = ''.join(markdown[:yaml_end])
    metadata = yaml.safe_load(yaml_text)

    return metadata, ''.join(markdown[yaml_end+1:])

def extract_bibtex(body: str):
    logger.debug("Extracting BibTeX metadata")
    pattern = r'```BibTeX(.*?)```'
    match = re.findall(pattern, body, re.DOTALL | re.IGNORECASE)

    try:
        entry = bibtexparser.parse_string(match[0]).entries[0]
        fields_dict = entry.fields_dict

        return {
            'bibtex_key': entry.key,
            'title': fields_dict['title'].value,
            'author': fields_dict['author'].value.split(' and '),
            'year' : int(fields_dict['year'].value)
        }
    except:
        logger.debug("> No BibTeX entry found")
        return {}


##
# Query arXiv
arxiv_client = arxiv.Client()

def process_arxiv_result(results, title):
    try:
        result = next(results)
    except:
        logger.debug(f"> Failed to fetch from arXiv")
        return None, None, None
    
    fetched = result.title
    if not check_title(
        title,
        fetched,
        QUERY_WARNING_TEXT.format(service = "arXiv", query=title, fetched=fetched)
    ):
        logger.info("\033[33mSkipped\033[0m summary")
        return None, None, None
    
    logger.debug(f"> Successfully fetched paper: {fetched}")
    return result.entry_id, result.summary, result.doi

def _fetch_arxiv_data(query_str, title):
    logger.debug(f"Querying arXiv with query={query_str}")

    search = arxiv.Search(
        query = query_str,
        max_results = 1,
        sort_by = arxiv.SortCriterion.Relevance
    )
    logger.debug("> Sent arXiv API request")
    results = arxiv_client.results(search)
    logger.debug("> Received arXiv API response")
    return process_arxiv_result(results, title)

def query_arxiv_title(title, author):
    logger.debug("Getting data from arXiv by title/author")
    q = f"{clean_text(title)} AND {clean_text(author)}"

    return _fetch_arxiv_data(q, title)

def query_arxiv_doi(doi, title):
    logger.debug(f"Getting data from arXiv for DOI: {doi}")
    q = f"{doi}"

    return _fetch_arxiv_data(q, title)


##
# Query Crossref
def send_crossref_request(title, author=None, check=False):
    logger.debug(f"> Query: {title}")
    query = {"query.title": clean_text(title)}
    if author:
        query["query.author"] = author.split(',')[0]
    try:
        result = next(iterate_publications_as_json(max_results=1,queries=query))
        fetched = result["title"][0]
    except:
        logger.error("> Failed to query Crossref")
        return None, None
    
    if not same_text(title, fetched):
        if not check:
            logger.info("\033[33mSkipped\033[0m reference DOI")
            return None, None
        if not process_warning(
            QUERY_WARNING_TEXT.format(service = "Crossref", query=title, fetched=fetched)
        ):
            logger.info("\033[33mSkipped\033[0m reference")
            return None, None
    
    return result.get("DOI"), result.get("reference")

def create_crossref_reference(reference):
    if not reference:
        return None
    for r in reference:
        if not r.get("article-title"):
            continue
        if r.get("DOI"):
            yield r.get("DOI")
        else:
            doi, _ = send_crossref_request(r.get("article-title"), r.get("author"))
            if doi:
                yield doi

def query_crossref_title(title, author=None):
    logger.debug("Getting data from Crossref")
    doi, reference = send_crossref_request(title, author, check=False)
    return doi, list(create_crossref_reference(reference))

def query_crossref_doi(doi, title):
    logger.debug("Getting data from Crossref")
    try:
        result = get_publication_as_json(doi)
        return doi, list(create_crossref_reference(result.get("reference")))
    except:
        logger.error("> Failed to query Crossref")
        return None, None
    

##
# Query ADS
ADS_ENDPOINT = "https://api.adsabs.harvard.edu/v1/search/query"

def _fetch_ads_data(query_str, title):
    logger.debug(f"Querying ADS with query={query_str}")

    headers = {
        "Authorization": f"Bearer {ADS_API_KEY}"
    }
    params = {
        "q": query_str,
        "fl": "reference,bibcode,doi,abstract,title"
    }

    try:
        response = requests.get(ADS_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        docs = data.get('response', {}).get('docs', [])
        if not docs:
            return None, None, None, None

        first_doc = docs[0]
        fetched_title = first_doc.get('title')

        if not check_title(
            title, 
            fetched_title, 
            QUERY_WARNING_TEXT.format(service="ADS", query=title, fetched=fetched_title)
        ):
            logger.info("\033[33mSkipped\033[0m reference")
            return None, None, None, None

        references = first_doc.get('reference', [])
        bibcode = first_doc.get('bibcode')
        doi = first_doc.get('doi')
        abstract = first_doc.get('abstract')

        return doi, abstract, references, bibcode

    except requests.exceptions.RequestException as e:
        logger.error(f"> Failed to query ADS: {str(e)}")
        return None, None, None, None

def query_ads_title(title, author=None):
    logger.debug("Getting data from ADS by title/author")
    q = f"{clean_text(title)}"
    if author:
        q += f" AND {clean_text(author)}"

    return _fetch_ads_data(q, title)

def query_ads_arxiv(title, arxiv_id):
    logger.debug(f"Getting data from ADS for arXiv: {arxiv_id}")
    q = f"arXiv:{arxiv_id}"
    
    return _fetch_ads_data(q, title)

def query_ads_doi(title, doi):
    logger.debug(f"Getting data from ADS for DOI: {doi}")
    q = f"doi:{doi}"

    return _fetch_ads_data(q, title)

##
# Process Article
def process_article(title, authors):
    data = {}
    result = query_arxiv_title(title, authors[0])
    data.update(
        {
            "arxiv_id": result[0],
            "summary": result[1],
            "arxiv_doi": result[2],
        }
    )
    
    result = query_crossref_title(title, authors[0])
    data.update(
        {
            "crossref_doi": result[0],
            "crossref_reference": result[1],
        }
    )
    
    result = query_ads_title(title, authors[0])
    data.update(
        {
            "ads_doi": result[0],
            "ads_abstract": result[1],
            "ads_reference": result[2],
            "ads_bibcode": result[3],
        }
    )

    if (not data["arxiv_id"]):
        if data["crossref_doi"]:
            result = query_arxiv_doi(data["crossref_doi"], title)
            data.update(
                {
                    "arxiv_id": result[0],
                    "summary": result[1],
                    "arxiv_doi": result[2],
                }
            )
        #TODO 
        
        

    print(data)
    

process_article(
    "Deep residual learning for image recognition",
    ["He, Kaiming"]
)
