#!/usr/bin/env python

##
# Global parameters
import os
import numpy as np

N = 10
RATIO = 0.4
DB_LOCATION = os.environ.get("PAPER_REL_DB")
KEYWORD_WARNING_TEXT = f"\033[33mWARNING\033[0m: There is error in number of keywords.\n\tDo you want to proceed? (y/N): "
DB_WARNING_TEXT = f"\033[33mWARNING\033[0m: Error when loading DB.\n\tDo you want to create new DB at '{DB_LOCATION}'? (y/N): "

##
# Argement Parser
import re
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
    '-b',
    '--bibtex',
    action='store_true',
    help='Extract metatdata from bibtex entry codeblock'
    )
parser.add_argument(
    '-vs',
    '--vector-store',
    action='store_true',
    help='Creates embedding vector of the text.'
    )
parser.add_argument(
    '--keyword-only',
    action='store_true',
    help='Only prints keywords and exits.'
    )
args = parser.parse_args()

if args.vector_store and (not DB_LOCATION):
    print("Environment variable 'PAPER_REL_DB' should be set to use vector storage.")
    print("\033[31mABORTED\033[0m")
    exit(1)

##
# Read file
import yaml
with open(args.filename, 'r') as file:
    markdown = file.readlines()

# Extract Markdown file metadata
def extract_metadata(markdown):
    while markdown[0].strip() =='':
        markdown = markdown[1:]
    if '---' not in markdown[0].strip():
        return {}, ''.join(markdown)

    markdown = markdown[1:]
    for idx, line in enumerate(markdown):
        if '---' in line.strip():
            metadata_end = idx
            break

    metadata_text = ''.join(markdown[:metadata_end])
    metadata = yaml.safe_load(metadata_text)

    return metadata, ''.join(markdown[metadata_end+1:])

# Extract BibTeX metadata
import bibtexparser

def bibtex_2_dict(bibtex):
    fields_dict = bibtex.fields_dict
    data = {}
    data["key"] = bibtex.key
    data["title"] = fields_dict['title'].value
    data["author"] = fields_dict['author'].value.split(' and ')
    data["year"] = fields_dict['year'].value
    return data

def extract_bibtex_entries(markdown_text):
    pattern = r'```BibTeX(.*?)```'
    match = re.findall(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
    entry = bibtexparser.parse_string(match[0])
    return bibtex_2_dict(entry.entries[0])

##
# Get summary
import re
import arxiv
from difflib import SequenceMatcher

ARXIV_WARNING_TEXT = """\033[33mWARNING\033[0m: Fetched paper might be not correct
\tQuery: {query}
\tFetched: {fetched}
\tDo you want to use fetched paper? (y/N):"""

arxiv_client = arxiv.Client()

def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9]+", ' ', text).lower()

def get_summary(title, author):
    clean_title = clean_text(title)
    clean_author = clean_text(author[0])
    
    search = arxiv.Search(
        query = f"{clean_title} AND {clean_author}",
        max_results = 1,
        sort_by = arxiv.SortCriterion.Relevance
    )
    results = arxiv_client.results(search)
    result = next(results)

    fetched = result.title
    clean_fetched = clean_text(result.title)
    if SequenceMatcher(None, clean_title, clean_fetched).ratio() < 0.99:
        if input(ARXIV_WARNING_TEXT.format(query=title, fetched=fetched)) != 'y':
            print("\033[33mSkipped\033[0m")
            return None
    return result.summary

##
# OpenAI
import os
from openai import OpenAI
endpoint = "https://models.inference.ai.azure.com"
token = os.environ["GITHUB_TOKEN"]
client = OpenAI(base_url=endpoint, api_key=token)

# OpenAI Embedding
def embedding(text: list[str]): 
    embedding_model_name = "text-embedding-3-small"
    embedding_response = client.embeddings.create(
        input = text,
        model = embedding_model_name,
    )

    embeddings = []
    for data in embedding_response.data:
        embeddings.append(np.array(data.embedding))
    
    return embeddings

# OpenAI Keyword Extraction
import json

def keyword_extraction(text: str, example = None) -> list[str]:
    chat_model_name = "gpt-4o-mini" 

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

    completion = client.beta.chat.completions.parse(
        model = chat_model_name,
        messages = messages,
        response_format = { "type": "json_object" }
    )

    chat_response = completion.choices[0].message
    json_data = json.loads(chat_response.content)

    keywords = json_data["keywords"]

    try:
        assert len(keywords) == 10
    except:
        print(f"\033[33mWARNING\033[0m: created keywords({keywords})")
        if input(KEYWORD_WARNING_TEXT) == 'y':
            return keywords
        print("\033[31mABORTED\033[0m")
        exit()

    return keywords


##
# DB
import pandas

old_df = None
try:
    old_df = pandas.read_hdf(DB_LOCATION, key='df')
    print(f"Loaded {len(old_df.index)} entries")
except:
    if input(DB_WARNING_TEXT) != 'y':
        print("\033[31mABORTED\033[0m")
        exit()

def save_db(df):
    try:
        df.to_hdf(DB_LOCATION, key='df', mode='w')
    except Exception as e: 
        print("Error when saving to DB")
        print(e)
        exit()
    print(f"Saved {len(df.index)} entries")

def append_db(new_entry):
    new_df = pandas.DataFrame.from_dict(new_entry)
    
    if type(old_df) != pandas.DataFrame:
        save_db(new_df)
        return
    save_db(
        old_df.set_index('key').combine_first(new_df.set_index('key')).reset_index()
    )

##
# Processing

# Process metadata
from datetime import datetime

metadata, body = extract_metadata(markdown)
metadata["updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Add metadata from bibtex
if args.bibtex:
    data = extract_bibtex_entries(body)

    metadata["key"] = data["key"]
    metadata["title"] = data["title"]
    metadata["author"] = data["author"]
    metadata["year"] = int(data["year"])

# Get summary
summary = get_summary(metadata["title"], metadata["author"])

# Get embeddings
embed_text = [metadata["title"], body]
if summary:
    embed_text.append(summary)
embeddings = embedding(embed_text)

keyword_example = set()
if type(old_df) == pandas.DataFrame:
    similarity_df = old_df.copy()

    similarity_df["similarity"] = similarity_df["embedding_title"].apply(lambda x: np.linalg.norm(x-embeddings[0]))
    similarity_df = similarity_df.sort_values(by='similarity', ascending=False)
    for _, row in similarity_df[:3].iterrows():
        keyword_example.add(f"'{row["title"]}': {", ".join(row["tags"])}")
        
    similarity_df["similarity"] = similarity_df["embedding_body"].apply(lambda x: np.linalg.norm(x-embeddings[1]))
    similarity_df = similarity_df.sort_values(by='similarity', ascending=False)
    for _, row in similarity_df[:3].iterrows():
        keyword_example.add(f"'{row["title"]}': {", ".join(row["tags"])}")
    
    if summary and ("embedding_summary" in similarity_df.columns):
        similarity_df["similarity"] = similarity_df["embedding_summary"].apply(lambda x: np.linalg.norm(x-embeddings[2]))
        similarity_df = similarity_df.sort_values(by='similarity', ascending=False)
        for _, row in similarity_df[:3].iterrows():
            keyword_example.add(f"'{row["title"]}': {", ".join(row["tags"])}")
    
    keyword_example = list(keyword_example)

# Create keywords
keyword_payload=f"""
title: {metadata["title"]}
summary:
{summary}

note:
{body}
"""
keywords = keyword_extraction(keyword_payload, keyword_example)

# If keyword only mode
if args.keyword_only:
    for keyword in keywords:
        print(f"- {keyword}")
    exit()

metadata["tags"] = ["Paper"] + keywords
metadata["category"] = keywords[0]


# Add entry to vector store
if args.vector_store:
    entry = {}
    entry["key"] = metadata["key"]
    entry["title"] = metadata["title"]
    entry["category"] = metadata["category"]
    entry["year"] = metadata["year"]
    entry["tags"] = keywords
    entry["embedding_title"] = np.array(embeddings[0])
    entry["embedding_body"] = np.array(embeddings[1])
    if summary:
        entry["embedding_summary"] = np.array(embeddings[2])
    
    # print(entry)
    append_db([entry])

# Add matadata to Markdown
with open(f"{args.filename}", 'w') as file:
    file.write("---\n")
    file.write(yaml.dump(metadata, default_flow_style=False))
    file.write("---\n")
    file.write(body)

