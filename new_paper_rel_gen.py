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


##
# DB related
# Entries: 
# - paper: title, author, year, doi, keywords, filename, 
#       title_embedding, summary_embedding, body_embedding
# - ref: 
import pandas

# load existing DB
paper_db = None
ref_db = None
def load_db():
    try:
        paper_db = pandas.read_hdf(DB_LOCATION, key='paper')
        ref_db = pandas.read_hdf(DB_LOCATION, key='ref')
        logger.debug(f"Loaded {len(paper_db.index)} entries from DB")
    except:
        if input(DB_WARNING_TEXT) != 'y':
            logger.fatal("\033[31mABORTED\033[0m")
            exit()

# Save DB
def save_db():
    try:
        paper_db.to_hdf(DB_LOCATION, key='paper', mode='w')
        ref_db.to_hdf(DB_LOCATION, key='ref', mode='w')
    except Exception as e: 
        logger.error("Error when saving to DB")
        logger.error(e)
        exit()
    logger.info(f"Saved {len(paper_db.index)} entries to DB")