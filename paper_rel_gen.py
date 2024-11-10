#!/usr/bin/env python


##
# Global parameters
import os
import logging

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
ref_db = pandas.DataFrame(columns=['doi', 'ref'])
def load_db():
    global paper_db, ref_db
    logger.debug("Loading DB")
    try:
        paper_db = pandas.read_hdf(DB_LOCATION, key='paper')
        ref_db = pandas.read_hdf(DB_LOCATION, key='ref')
        logger.debug(f"Loaded {len(paper_db.index)} entries from DB")
    except Exception as e:
        logger.error(e)
        process_warning(DB_WARNING_TEXT, abort=True)

def save_db():
    global paper_db, ref_db
    logger.debug("Saving DB")
    try:
        with pandas.HDFStore(DB_LOCATION, mode='w') as store:
            store.put('paper', paper_db)
            store.put('ref', ref_db)
    except Exception as e: 
        logger.error("Error when saving to DB")
        logger.error(e)
        exit()
    logger.info(f"Saved {len(paper_db.index)} entries to DB")

def append_entry(entry):
    global paper_db, ref_db
    new_df = pandas.DataFrame.from_dict([entry])
    if type(paper_db) != pandas.DataFrame:
        paper_db = new_df
        return
    paper_db = paper_db.set_index('key').combine_first(new_df.set_index('key')).reset_index()

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
            'year' : int(fields_dict['year'].value)
        }
    except:
        logger.debug("> No BibTeX entry found")
        return {}


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
        return None, None, None,

    fetched = result.title
    if not same_text(title, fetched):
        if not process_warning(
            QUERY_WARNING_TEXT.format(service = "arXiv", query=title, fetched=fetched)
        ):
            logger.info("\033[33mSkipped\033[0m summary")
            return None, None, None
        
    return result.summary, result.doi, result.entry_id


##
# Get data from Crossref
from crossref_commons.iteration import iterate_publications_as_json
from crossref_commons.retrieval import get_publication_as_json

def query_crossref_title(title, author=None, check=False):
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
    logger.debug(f"> Fetched: {result.get("DOI")}")

    return result.get("DOI"), result.get("reference")
    
def query_crossref_doi(doi):
    logger.debug(f"> Query: {doi}")
    try:
        result = get_publication_as_json(doi)
        return result.get("reference")
    except:
        logger.error("> Failed to query Crossref")
        return None

def get_doi(title, author):
    if not title:
        return None
    doi, _ = query_crossref_title(title, author)
    return doi

def query_crossref(title, author, doi=None):
    logger.debug("Getting data from Crossref")
    result = query_crossref_title(title, author, True)

    doi = doi or result[0]
    if doi is None:
        return None, None
    
    ref = result[1] or query_crossref_doi(doi)
    if not ref:
        return doi, None

    ref_doi = []
    for r in ref:
        if r.get("DOI"):
            ref_doi.append(r.get("DOI"))
        else:
            ref_doi.append(get_doi(r.get("article-title"), r.get("author")))

    return doi, [i for i in ref_doi if i is not None]


##
# Get data from ADS
import requests

ADS_ENDPOINT = "https://api.adsabs.harvard.edu/v1/search/query"

def query_ads(arxiv_id):
    logger.debug("Getting data from ADS")
    
    headers = {
        "Authorization": f"Bearer {ADS_API_KEY}"
    }
    
    params = {
        "q": f"identifier:{arxiv_id}",
        "fl": "reference,bibcode"
    }
    
    try:
        response = requests.get(ADS_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        docs = data.get('response', {}).get('docs', [])
        
        if not docs:
            return None, None
            
        references = docs[0].get('reference', [])
        bibcode = docs[0].get('bibcode')
        return references, bibcode
        
    except requests.exceptions.RequestException as e:
        logger.error(f"> Failed to query ADS: {str(e)}")
        return None, None


##
# OpenAI API
from openai import OpenAI
import numpy as np
import json
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = chat_model_name = "gpt-4o-mini"

endpoint = "https://models.inference.ai.azure.com"
client = OpenAI(base_url=endpoint, api_key=TOKEN)

def embedding(text: list[str]):
    logger.debug("Embedding texts")
    logger.debug("> Sending OpenAI embedding API request")
    embedding_response = client.embeddings.create(
        input = text,
        model = EMBEDDING_MODEL,
    )
    logger.debug("> Recieved OpenAI embedding API responce")
    logger.debug(embedding_response.usage)

    embeddings = []
    for data in embedding_response.data:
        embeddings.append(np.array(data.embedding))
    
    logger.debug("Created embedding vector")
    return embeddings

def keyword_extraction(text: str, example = None) -> list[str]:
    logger.debug("Creating keywords")
    GPT_INSTRUCTIONS = f"""
This GPT helps users generate a set of relevant keywords or tags based on the content of any note or text they provide.
It offers concise, descriptive, and relevant tags that help organize and retrieve similar notes or resources later.
The GPT will aim to provide up to {N} keywords, with 1 keyword acting as a category, {N*RATIO} general tags applicable to a broad context, and {N - 1 - N*RATIO} being more specific to the content of the note.
It avoids suggesting overly generic or redundant keywords unless necessary.
It will list the tags using underscores instead of spaces, ordered from the most general to the most specific.
Every tag will be lowercase.
Return the list in json format with key "keywords" for keyword list.
"""
    if example:
        GPT_INSTRUCTIONS += "\n\nExamples:\n"
        for e in example:
            GPT_INSTRUCTIONS += f"{e}\n"
    
    messages = [
        {"role":"system", "content": GPT_INSTRUCTIONS},
        {"role": "user", "content": text},
    ]
    logger.debug("> Sending OpenAI completion API request")
    completion = client.beta.chat.completions.parse(
        model = chat_model_name,
        messages = messages,
        response_format = { "type": "json_object" }
    )
    logger.debug("Recieved OpenAI completion API responce")
    logger.debug(completion.usage)

    chat_response = completion.choices[0].message
    json_data = json.loads(chat_response.content)

    keywords = json_data["keywords"]

    try:
        assert len(keywords) == N
    except:
        if not process_warning(
            KEYWORD_WARNING_TEXT.format(count = N, keywords = keywords), 
            abort=True
            ):
            logger.fatal("\033[31mABORTED\033[0m")
            exit()

    return keywords


##
# Data processing
from datetime import datetime
def create_embedding(text:dict):
    logger.debug("Creating embeddings")
    text = {k: v for k, v in text.items() if v is not None}
    payload = list(text.values())
    embeddings = embedding(payload)

    return {f"embedding_{key}": embedding for key, embedding in zip(text.keys(), embeddings)}

def get_keyword_example(embeddings):
    logger.debug("Getting keyword examples")
    keys = set()
    keyword_example = set()
    similarity_df = paper_db.copy()
    
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
    keyword_payload = f"title: {title}\n"
    keyword_payload += f"summary:\n{summary}\n\n" if summary else ""
    keyword_payload += f"body:\n{body}"

    return keyword_extraction(keyword_payload, keyword_example)
    
def organize_db_entry(doi, arxiv_id, metadata, embeddings):
    logger.debug("Creating DB entry")
    entry = {}
    entry['key'] = metadata["key"]
    entry['doi'] = doi
    entry['arxiv_id'] = arxiv_id
    entry["title"] = metadata["title"]
    entry["author"] = metadata["author"]
    entry["year"] = metadata["year"]
    entry["category"] = metadata["category"]
    entry["keywords"] = metadata["keywords"]
    entry["embedding_title"] = embeddings.get("embedding_title", np.nan)
    entry["embedding_body"] = embeddings.get("embedding_body", np.nan)
    entry["embedding_summary"] = embeddings.get("embedding_summary", np.nan)
    
    return entry

def organize_md_metadata(metadata):
    logger.debug("Creating MD metadata")
    md_metadata = {}
    md_metadata["key"] = metadata["key"]
    md_metadata["title"] = metadata["title"]
    md_metadata["author"] = metadata["author"]
    md_metadata["year"] = metadata["year"]
    md_metadata["category"] = metadata["category"]
    md_metadata["tags"] = metadata["tags"]
    md_metadata["updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md_metadata["created"] = str(metadata["created"] or md_metadata["updated"])
    
    return md_metadata

def create_md_content(md_metadata, body):
    return f"""---
{yaml.dump(md_metadata, default_flow_style=False)}---
{body}"""

def append_reference(doi, ref_doi):
    global ref_db
    if doi is None or ref_doi is None:
        return
    for ref in ref_doi:
        logger.debug(f"> Adding relation '{ref}' <- '{doi}'")
        if doi in ref_db['doi'].values:
            ref_db.loc[ref_db['doi'] == ref, 'ref'].apply(lambda x: x.append(doi))
        else:
            new_row = pandas.DataFrame({'doi': [ref], 'ref': [[doi]]})
            ref_db = pandas.concat([ref_db, new_row], ignore_index=True)


##
# Test Code
load_db()

# Process input file
markdown = read_file(args.filename)
metadata_yaml, body = extract_yaml(markdown)
metadata_bibtex = extract_bibtex(body)
metadata = metadata_yaml | metadata_bibtex
metadata["key"] = ".".join(os.path.basename(args.filename).split('.')[:-1])

# Get summary
summary = None
id_arxiv = None
if args.article:
    summary, doi, id_arxiv = query_arxiv(metadata["title"], metadata["author"][0])

# Get references
ref_doi = None
if args.article:
    doi, ref_doi = query_crossref(metadata["title"], metadata["author"][0], doi)
    if not ref_doi:
        process_warning(REF_WARNING_TEXT, abort = True)

# Get ADS references
ads_ref = None
if args.article and id_arxiv:
    ads_ref, bibcode = query_ads(id_arxiv)
    if not ads_ref:
        process_warning(REF_WARNING_TEXT, abort = True)

# Create embeddings
embeddings = create_embedding(
    {
        "title": metadata["title"],
        "summary": summary,
        "body" : body
    }
)

# Create keywords
keyword_example = None
if type(paper_db) == pandas.DataFrame:
    keyword_example = get_keyword_example(embeddings)
keywords = create_keywords(metadata["title"], summary, body, keyword_example)
metadata["keywords"] = keywords
metadata["tags"] = ["Paper"] + keywords
metadata["category"] = keywords[0]

# If keyword only mode
if args.keyword_only:
    for keyword in keywords:
        print(f"- {keyword}")
    exit()

# Write MD file
md_metadata = organize_md_metadata(metadata)
md_content = create_md_content(md_metadata, body)
write_file(args.filename, md_content)

# Update references
append_reference(doi, ref_doi)

# Add entry to DB
new_entry = organize_db_entry(doi, id_arxiv, metadata, embeddings)
append_entry(new_entry)
save_db()