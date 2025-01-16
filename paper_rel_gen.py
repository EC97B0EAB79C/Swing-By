# Standard library imports
import logging
import os
import re

# Third-party imports
import bibtexparser
import pandas
import yaml
import json
import numpy as np
import requests

# Internal imports
from src.utils.file import FileUtils
from src.utils.text import TextUtils
from src.utils.md import MarkdownUtils
from src.llm_api.open import OpenAPI

from src.article_api.arxiv_api import ArxivQuery
from src.article_api.crossref_api import CrossrefQuery

# Global Parameters
N = 10
RATIO = 0.4
# DB_LOCATION = os.environ.get("PAPER_REL_DB")
DB_LOCATION = "./test/new_db.h5"
ADS_API_KEY = os.environ["ADS_API_KEY"]

logging.basicConfig()
logger = logging.getLogger(__name__)

# Warning Messages
EMBEDDING_WARNING_TEXT = """\033[33mWARNING\033[0m: There is error in number of embedding.
\tCreated ({count})
\tDo you want to proceed? (y/N): """
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
    if args.script:
        return False
    user_continue = input(message) == 'y'
    if abort and not user_continue:
        logger.fatal("\033[31mABORTED\033[0m")
        exit(1)
    return user_continue
        

##
# Set up argument parser and logging
import argparse
def setup_parser():
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
    parser.add_argument(
        '--script',
        '-s',
        action='store_true',
        help='Run in script mode, select "N" for all warnings.'
        )
    args = parser.parse_args()

    # Check if global variabble is set for DB
    if (not args.keyword_only) and (not DB_LOCATION):
        logging.error("Environment variable 'PAPER_REL_DB' should be set to use vector storage.")
        logging.error("\033[31mABORTED\033[0m")
        exit(1)
        
    # Set logger
    level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(level)

    return args

##
# Utils
def check_title(title1, title2, message, abort=False):
    if TextUtils.same(title1, title2):
        return True
    return process_warning(message, abort)

def verify_entry(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return verify_entry(value[0])
    else:
        return ""

def _format_entry(string, length):
    return string.lower().ljust(length,".")[:length].replace(" ", ".")

def generate_sbkey(title, author, year):
    author_last_name = TextUtils.clean(author).split()[0] if author else "."
    author_last_name = _format_entry(author_last_name, 6)

    year = str(year)
    year = year if year.isdigit() else "."
    year = _format_entry(year, 4)

    title_words = TextUtils.clean(title).split()
    title_first_word = _format_entry(title_words[0], 6)
    title_first_char = _format_entry(''.join([word[0] for word in title_words]), 16)
    
    sbkey = f"{author_last_name}{year}{title_first_word}{title_first_char}"
    #TODO: Move this part to other
    # DB.append_article_db(sbkey, title, author, year)

    return sbkey

##
# DB
# PaperDB: key, title, author, year, bibtex_key, doi, bibcode, keywords, filename, 
#       title_embedding, summary_embedding, body_embedding
# RefDB: key, doi_ref, bibcode_ref
class PaperDB:
    def __init__(self):
        self.paper_db = None
        self.ref_db = pandas.DataFrame(columns=['doi', 'doi_ref', 'bibcode_ref'])
        self.article_db = None
        self.load()

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

    def append_paper_db(self, entry):
        logger.debug("Appending entry to DB")
        new_df = pandas.DataFrame.from_dict([entry])
        if type(self.paper_db) != pandas.DataFrame:
            self.paper_db = new_df
            return
        self.paper_db = pandas.concat([self.paper_db, new_df]).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
        logger.debug(f"Appended entry to DB")

    def append_article_db(self, sbkey, title, author, year):
        logger.debug("Appending article to DB")
        new_df = pandas.DataFrame.from_dict([{
            "key": sbkey,
            "title": title,
            "author": author,
            "year": year
        }])
        if type(self.article_db) != pandas.DataFrame:
            self.article_db = new_df
            return
        self.article_db = pandas.concat([self.article_db, new_df]).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
        logger.debug(f"Appended article to DB")


##
# Query arXiv
def query_arxiv_title(title, author):
    return ArxivQuery.with_title(title, author)

def query_arxiv_doi(doi):
    return ArxivQuery.with_doi(doi)


##
# Query Crossref
def _send_crossref_request(title, author=None, check=False):
    return CrossrefQuery.with_title(title, author)

def _create_crossref_reference(reference):
    unstructured_ref = []
    sbkey_list = []

    if not reference:
        return None
    for r in reference:
        if r.get("article-title"):
            sbkey_list.append(generate_sbkey(r.get("article-title"), r.get("author"), r.get("year")))
        elif r.get("unstructured"):
            unstructured_ref.append(r.get("unstructured"))

    if unstructured_ref:
        sbkey_list += unstructured_reference_to_sbkey(unstructured_ref)

    return sbkey_list or []

def query_crossref_title(title, author=None):
    logger.debug("Getting data from Crossref")
    doi, reference = _send_crossref_request(title, author, check=True)
    return doi, _create_crossref_reference(reference)

def query_crossref_doi(doi, title):
    logger.debug("Getting data from Crossref")
    doi, reference = CrossrefQuery.with_doi(doi)
    return doi, _create_crossref_reference(reference)

    

##
# Query ADS
ADS_ENDPOINT = "https://api.adsabs.harvard.edu/v1/search/query"

def _fetch_ads_data(query_str, title, reference=False):
    logger.debug(f"> Querying ADS with query={query_str}")

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
        if b"<!DOCTYPE html>" in response.content:
            raise requests.exceptions.RequestException("ADS is currently under maintenance")
        data = response.json()

        docs = data.get('response', {}).get('docs', [])
        if not docs:
            return None, None, None, None

        first_doc = docs[0]
        fetched = verify_entry(first_doc.get('title'))

        if not check_title(
            title, 
            fetched, 
            QUERY_WARNING_TEXT.format(service="ADS", query=title, fetched=fetched)
        ):
            logger.info("\033[33mSkipped\033[0m reference")
            return None, None, None, None

        bibcode_references = first_doc.get('reference', [])
        references = list(_bibcodes_to_sbkeys(bibcode_references))
        bibcode = first_doc.get('bibcode')
        doi = verify_entry(first_doc.get('doi'))
        abstract = first_doc.get('abstract')

        logger.debug(f"> Successfully fetched paper: {fetched}")
        return doi, abstract, references, bibcode

    except requests.exceptions.RequestException as e:
        logger.error(f"> Failed to query ADS: {str(e)}")
        return None, None, None, None

def _bibcode_to_sbkey(bibcode):
    logger.debug(f"> Creating SBKey from bibcode={bibcode}")

    headers = {
        "Authorization": f"Bearer {ADS_API_KEY}"
    }
    params = {
        "q": f"bibcode:{bibcode}",
        "fl": "title,first_author,year"
    }

    try:
        response = requests.get(ADS_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        if b"<!DOCTYPE html>" in response.content:
            raise requests.exceptions.RequestException("ADS is currently under maintenance")
        data = response.json()

        docs = data.get('response', {}).get('docs', [])
        if not docs:
            return None

        first_doc = docs[0]
        title = verify_entry(first_doc.get('title'))
        author = verify_entry(first_doc.get('first_author'))
        year = verify_entry(first_doc.get('year'))

        return generate_sbkey(title, author, year)

    except requests.exceptions.RequestException as e:
        logger.error(f"> Failed to query ADS: {str(e)}")
        return None

def _bibcodes_to_sbkeys(bibcodes):
    for bibcode in bibcodes:
        yield _bibcode_to_sbkey(bibcode)        

def query_ads_title(title, author=None):
    logger.debug("Getting data from ADS by title/author")
    q = f"{TextUtils.clean(title)}"
    if author:
        q += f" AND {TextUtils.clean(author)}"

    return _fetch_ads_data(q, title, reference=True)

def query_ads_arxiv(arxiv_id, title):
    logger.debug(f"Getting data from ADS for arXiv: {arxiv_id}")
    q = f"arXiv:{arxiv_id}"
    
    return _fetch_ads_data(q, title, reference=True)

def query_ads_doi(doi, title):
    logger.debug(f"Getting data from ADS for DOI: {doi}")
    q = f"doi:{doi}"

    return _fetch_ads_data(q, title, reference=True)


##
# Semantic Scholar API
#TODO


##
# Process Article
def process_article(title, author):
    data = {
        "arxiv_id": None,
        "summary": None,
        "arxiv_doi": None,
        "crossref_doi": None,
        "crossref_reference": None,
        "ads_doi": None,
        "ads_abstract": None,
        "ads_reference": None,
        "ads_bibcode": None,
    }

    _update_arxiv_title(data, title, author)
    _update_crossref_title(data, title, author)
    _update_ads_title(data, title, author)

    _fill_missing_arxiv_data(data, title)
    _fill_missing_crossref_data(data, title)
    _fill_missing_ads_data(data, title)

    return data

def _update_arxiv_title(data, title, author):
    arxiv_id, summary, arxiv_doi = query_arxiv_title(title, author)
    data["arxiv_id"] = arxiv_id
    data["summary"] = summary
    data["arxiv_doi"] = arxiv_doi

def _update_crossref_title(data, title, author):
    crossref_doi, crossref_reference = query_crossref_title(title, author)
    data["crossref_doi"] = crossref_doi
    data["crossref_reference"] = crossref_reference

def _update_ads_title(data, title, author):
    ads_doi, ads_abstract, ads_reference, ads_bibcode = query_ads_title(title, author)
    data["ads_doi"] = ads_doi
    data["ads_abstract"] = ads_abstract
    data["ads_reference"] = ads_reference
    data["ads_bibcode"] = ads_bibcode

def _fill_missing_arxiv_data(data, fallback_title):
    if data["arxiv_id"]:
        return

    if data["crossref_doi"]:
        arxiv_id, summary, arxiv_doi = query_arxiv_doi(data["crossref_doi"], fallback_title)
        if arxiv_id:
            data["arxiv_id"] = arxiv_id
            data["summary"] = summary
            data["arxiv_doi"] = arxiv_doi
            return

    if data["ads_doi"]:
        arxiv_id, summary, arxiv_doi = query_arxiv_doi(data["ads_doi"], fallback_title)
        if arxiv_id:
            data["arxiv_id"] = arxiv_id
            data["summary"] = summary
            data["arxiv_doi"] = arxiv_doi

def _fill_missing_crossref_data(data, fallback_title):
    if data["crossref_reference"]:
        return

    if data["arxiv_doi"]:
        crossref_doi, crossref_reference = query_crossref_doi(data["arxiv_doi"], fallback_title)
        if crossref_reference:
            data["crossref_doi"] = crossref_doi
            data["crossref_reference"] = crossref_reference
            return

    if data["ads_doi"]:
        crossref_doi, crossref_reference = query_crossref_doi(data["ads_doi"], fallback_title)
        if crossref_reference:
            data["crossref_doi"] = crossref_doi
            data["crossref_reference"] = crossref_reference

def _fill_missing_ads_data(data, fallback_title):
    if data["ads_bibcode"]:
        return

    if data["arxiv_doi"]:
        ads_doi, ads_abstract, ads_reference, ads_bibcode = query_ads_doi(data["arxiv_doi"], fallback_title)
        if ads_bibcode:
            data["ads_doi"] = ads_doi
            data["ads_abstract"] = ads_abstract
            data["ads_reference"] = ads_reference
            data["ads_bibcode"] = ads_bibcode
            return

    if data["crossref_doi"]:
        ads_doi, ads_abstract, ads_reference, ads_bibcode = query_ads_doi(data["crossref_doi"], fallback_title)
        if ads_bibcode:
            data["ads_doi"] = ads_doi
            data["ads_abstract"] = ads_abstract
            data["ads_reference"] = ads_reference
            data["ads_bibcode"] = ads_bibcode
            return

    if not data["ads_bibcode"] and data["arxiv_id"]:
        ads_doi, ads_abstract, ads_reference, ads_bibcode = query_ads_arxiv(data["arxiv_id"], fallback_title)
        if ads_bibcode:
            data["ads_doi"] = ads_doi
            data["ads_abstract"] = ads_abstract
            data["ads_reference"] = ads_reference
            data["ads_bibcode"] = ads_bibcode

def unstructured_reference_to_sbkey(reference_list):
    logger.debug(f"Creating SBKey from unstructured reference:\n> {len(reference_list)} entries")
    structured_references = OpenAPI.article_data_extraction(reference_list)
    sbkey_list = [generate_sbkey(ref["title"], ref["first_author"], ref["year"]) for ref in structured_references]

    logger.debug(f"> Created {len(sbkey_list)} SBKeys")
    return sbkey_list

##
# Data processing
from datetime import datetime

def generate_key(metadata):
    return generate_sbkey(metadata["title"], metadata["author"][0], metadata["year"])

def create_embedding(text:dict):
    logger.debug("Creating embeddings")
    text = {k: v for k, v in text.items() if v is not None}
    embeddings = OpenAPI.embedding(list(text.values()))

    logger.debug("> Created embeddings")
    return {
        f"embedding_{key}": embedding
        for key, embedding in zip(text.keys(), embeddings)
        }

def get_keyword_example(embeddings):
    logger.debug("Getting keyword examples")
    keys = set()
    keyword_example = set()
    similarity_df = DB.paper_db.copy()
    
    for ent in ["embedding_title", "embedding_summary", "embedding_body"]:
        emb = embeddings.get(ent)
        if emb is None:
            continue
        similarity_df["sim"] = similarity_df[ent].apply(lambda x: np.linalg.norm(x-emb))
        similarity_df = similarity_df.sort_values(by='sim', ascending=False)
        for _, row in similarity_df[:3].iterrows():
            keyword_example.add(f"'{row["title"]}': {", ".join(row["keywords"])}")
            keys.add(row["key"])


    logger.debug(f"Related: {", ".join(keys) }")
    return list(keyword_example)

def create_keywords(title, summary, body, keyword_example):
    logger.debug("Creating keywords")
    payload = ""
    if keyword_example:
        payload += "\n\nExamples:\n"
        for e in keyword_example:
            payload += f"{e}\n"
        payload += "---\n\n"

    payload = f"title: {title}\n"
    payload += f"summary:\n{summary}\n\n" if summary else ""
    payload += f"body:\n{body}"

    keywords = OpenAPI.keyword_extraction(payload, N, RATIO)

    try:
        assert len(keywords) == N
    except:
        if not process_warning(
            KEYWORD_WARNING_TEXT.format(count = N, keywords = keywords), 
            abort=True
            ):
            logger.fatal("\033[31mABORTED\033[0m")
            exit()

    logger.debug("> Created keywords")
    return keywords


def organize_db_entry(data, metadata, embeddings, keywords):
    logger.debug("Creating DB entry")
    entry = {}
    # Keys
    entry["arxiv_id"] = data["arxiv_id"]
    entry["bibcode"] = data["ads_bibcode"]
    entry["doi"] = data["arxiv_doi"] or data["crossref_doi"] or data["ads_doi"]
    entry["key"] = metadata["key"]
    entry["filename"] = os.path.basename(args.filename)

    # References
    entry["ref"] = list(set().union(data["crossref_reference"] or [], data["ads_reference"] or []))
    entry["cited_by"] = []

    # Metadata
    entry["title"] = metadata["title"]
    entry["author"] = metadata["author"]
    entry["year"] = metadata["year"]
    entry["keywords"] = keywords

    entry["embedding_title"] = embeddings.get("embedding_title", np.nan)
    entry["embedding_body"] = embeddings.get("embedding_body", np.nan)
    entry["embedding_summary"] = embeddings.get("embedding_summary", np.nan)
    
    return entry

def organize_md_metadata(data, metadata, keywords):
    logger.debug("Creating MD metadata")
    md_metadata = {}
    
    md_metadata["key"] = metadata["key"]
    md_metadata["updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md_metadata["created"] = str(data.get("created") or md_metadata["updated"])
    
    md_metadata["title"] = metadata["title"]
    md_metadata["author"] = metadata["author"]
    md_metadata["year"] = metadata["year"]
    md_metadata["tags"] = ["Paper"] + keywords
    md_metadata["category"] = keywords[0]

    return md_metadata

    # def append_reference(doi, ref_doi):
#     global ref_db
#     if doi is None or ref_doi is None:
#         return
#     for ref in ref_doi:
#         logger.debug(f"> Adding relation '{ref}' <- '{doi}'")
#         if doi in ref_db['doi'].values:
#             ref_db.loc[ref_db['doi'] == ref, 'ref'].apply(lambda x: x.append(doi))
#         else:
#             new_row = pandas.DataFrame({'doi': [ref], 'ref': [[doi]]})
#             ref_db = pandas.concat([ref_db, new_row], ignore_index=True)


##
# Processing article
if __name__ == "__main__":
    args = setup_parser()

    DB = PaperDB()

    # Process input file
    markdown = FileUtils.read_lines(args.filename)
    metadata_yaml, body = MarkdownUtils.extract_yaml(markdown)
    metadata_bibtex = MarkdownUtils.extract_bibtex(body)
    metadata = metadata_yaml | metadata_bibtex
    metadata["key"] = generate_key(metadata)

    query_title = metadata.get("title") or metadata.get("name") or args.filename

    data = {}
    if args.article:
        data = process_article(query_title, metadata["author"][0])

    query_summary = data.get("summary") or data.get("ads_abstract")

    # Create embeddings
    embeddings = create_embedding(
        {
            "title": query_title,
            "summary": query_summary,
            "body": body
        }
    )

    # Create keywords
    keyword_example = None
    if type(DB.paper_db) == pandas.DataFrame:
        keyword_example = get_keyword_example(embeddings)
    keywords = create_keywords(metadata["title"], query_summary, body, keyword_example)

    if args.keyword_only:
        for keyword in keywords:
            print(f"- {keyword}")
        exit()

    # Write MD file
    md_metadata = organize_md_metadata(data, metadata, keywords)
    md_content = MarkdownUtils.create_md_text(md_metadata, body)
    FileUtils.write_file(args.filename, md_content)

    # Add entry to DB
    new_entry = organize_db_entry(data, metadata, embeddings, keywords)
    DB.append_paper_db(new_entry)
    DB.save()

    print(f"Created data for {metadata["key"]}")