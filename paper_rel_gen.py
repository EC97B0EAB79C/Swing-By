#!/usr/bin/env python

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
    '-i',
    '--ignore-bibtex',
    action='store_true'
    )
args = parser.parse_args()


##
# Read file
with open(args.filename, 'r') as file:
    markdown = file.read()

##
# OpenAI
import os
from openai import OpenAI
endpoint = "https://models.inference.ai.azure.com"
token = os.environ["GITHUB_TOKEN"]

OpenAI Embedding
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

embedding_model_name = "text-embedding-3-small"
client = EmbeddingsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
)

embedding_response = client.embed(
    input=[markdown],
    model=embedding_model_name
)


# OpenAI Keyword Extraction
from pydantic import BaseModel

chat_model_name = "gpt-4o-mini"
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

GPT_INSTRUCTIONS = """
This GPT helps users generate a set of relevant keywords or tags based on the content of any note or text they provide. It offers concise, descriptive, and relevant tags that help organize and retrieve similar notes or resources later. The GPT will aim to provide up to 8 keywords, with 3 of them being general tags applicable to a broad context, and 5 being more specific to the content of the note. It avoids suggesting overly generic or redundant keywords unless necessary. It will list the tags using underscores instead of spaces, ordered from the most general to the most specific. Every tag will be lowercase.
Return the list in json format with key "keywords".
"""

messages = [
    {"role":"system", "content": GPT_INSTRUCTIONS},
    {"role": "user", "content": markdown},
]

completion = client.beta.chat.completions.parse(
    model = chat_model_name,
    messages = messages,
    response_format = { "type": "json_object" }
)

chat_response = completion.choices[0].message

import json
keywords = json.loads(chat_response.content)["keywords"]

