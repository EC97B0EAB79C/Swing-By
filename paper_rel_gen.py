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

# OpenAI Embedding
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

embedding_model_name = "text-embedding-3-small"
client = EmbeddingsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
)

response = client.embed(
    input=[markdown],
    model=embedding_model_name
)


# OpenAI Keyword Extraction

