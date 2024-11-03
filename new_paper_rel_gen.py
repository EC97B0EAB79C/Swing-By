#!/usr/bin/env python

##
# Global parameters
import os
import logging

# Global Parameters
N = 10
RATIO = 0.4
DB_LOCATION = os.environ.get("PAPER_REL_DB")
# Warning Messages
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
parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode'
    )
args = parser.parse_args()
# Check if global variabble is set for DB
if args.vector_store and (not DB_LOCATION):
    logging.error("Environment variable 'PAPER_REL_DB' should be set to use vector storage.")
    logging.error("\033[31mABORTED\033[0m")
    exit(1)

##
# Set logger
level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level)

