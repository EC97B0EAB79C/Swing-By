#!/usr/bin/env python


##
# Global parameters
import os
import logging

# Global Parameters
N = 10
RATIO = 0.4
DB_LOCATION = "./test/test_db.h5"
# DB_LOCATION = os.environ.get("PAPER_REL_DB")


# Warning Messages
KEYWORD_WARNING_TEXT = f"\033[33mWARNING\033[0m: There is error in number of keywords.\n\tDo you want to proceed? (y/N): "
DB_WARNING_TEXT = f"\033[33mWARNING\033[0m: Error when loading DB.\n\tDo you want to create new DB at '{DB_LOCATION}'? (y/N): "
ARXIV_WARNING_TEXT = """\033[33mWARNING\033[0m: Fetched paper might be not correct
\tQuery: {query}
\tFetched: {fetched}
\tDo you want to use fetched paper? (y/N):"""

##
# Argement Parser
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


##
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

##
# DB related
# Entries: 
# - paper: title, author, year, bibtex_key, doi, keywords, filename, 
#       title_embedding, summary_embedding, body_embedding
# - ref: doi, referenced_at
import pandas

paper_db = None
ref_db = None
def load_db():
    logger.debug("Loading DB")
    try:
        paper_db = pandas.read_hdf(DB_LOCATION, key='paper')
        ref_db = pandas.read_hdf(DB_LOCATION, key='ref')
        logger.debug(f"Loaded {len(paper_db.index)} entries from DB")
    except:
        if input(DB_WARNING_TEXT) != 'y':
            logger.fatal("\033[31mABORTED\033[0m")
            exit()

def save_db():
    logger.debug("Saving DB")
    try:
        paper_db.to_hdf(DB_LOCATION, key='paper', mode='w')
        ref_db.to_hdf(DB_LOCATION, key='ref', mode='w')
    except Exception as e: 
        logger.error("Error when saving to DB")
        logger.error(e)
        exit()
    logger.info(f"Saved {len(paper_db.index)} entries to DB")


##
# File read/write
def read_file(path):
    logger.debug(f"Reading file: {path}")
    with open(path, 'r') as file:
        markdown = file.readlines()
    return markdown

def write_file(path, data):
    logger.debug(f"Writing file: {path}")
    with open(path, 'w') as file:
        file.write(data)


##
# Process file
import yaml
import re
import bibtexparser

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
            'year' : fields_dict['year'].value
        }
    except:
        logger.debug("> No BibTeX entry found")
        return None


##
# Get data from arxiv
import arxiv

arxiv_client = arxiv.Client()

def query_arxiv(title, author):
    logger.debug("Getting data from arXiv")
    clean_title = clean_text(title)
    clean_author = clean_text(author)
    
    search = arxiv.Search(
        query = f"{clean_title} AND {clean_author}",
        max_results = 1,
        sort_by = arxiv.SortCriterion.Relevance
    )
    logger.debug("> Sent arXiv API request")
    results = arxiv_client.results(search)
    logger.debug("> Recieved arXiv API responce")
    try:
        result = next(results)
    except:
        logger.debug(f"> Failed to fetch from arXiv: {title}")
        return None, None

    fetched = result.title
    if not same_text(title, fetched):
        if input(ARXIV_WARNING_TEXT.format(query=title, fetched=fetched)) != 'y':
            logger.info("\033[33mSkipped\033[0m summary")
            return None, None
        
    return result.summary, result.doi



##
# Test Code
load_db()
markdown = read_file(args.filename)
metadata_yaml, body = extract_yaml(markdown)
metadata_bibtex = extract_bibtex(body)
metadata = metadata_yaml | metadata_bibtex
summary, doi = query_arxiv(metadata["title"], metadata["author"][0])
print(summary)
print(doi)