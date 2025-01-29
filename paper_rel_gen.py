# Standard library imports
import logging

# Third-party imports
import pandas

# Internal imports
from src.utils.file import FileUtils
from src.utils.text import TextUtils
from src.utils.md import MarkdownUtils

from src.knowledge.base import KnowledgeBase
from src.knowledge.knowledge import Knowledge
from src.knowledge.article import Article

# Global Parameters
N = 10
RATIO = 0.4
# DB_LOCATION = os.environ.get("PAPER_REL_DB")
DB_LOCATION = "./test/new_db.h5"

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
# Data processing
def generate_key(metadata):
    return TextUtils.generate_sbkey(metadata["title"], TextUtils.get_first_string(metadata["author"]), metadata["year"])

def get_keyword_example(embeddings):
    logger.debug("Getting keyword examples")
    keys = set()
    keyword_example = set()
    
    for ent in ["embedding_title", "embedding_summary", "embedding_body"]:
        emb = embeddings.get(ent)
        if emb is None:
            continue
        result = DB.vector_search(ent, emb, 3)
        for _, row in result.iterrows():
            keyword_example.add(f"'{row["title"]}': {", ".join(row["keywords"])}")
            keys.add(row["key"])

    logger.debug(f"Related: {", ".join(keys) }")
    return list(keyword_example)


##
# Processing article
if __name__ == "__main__":
    args = setup_parser()
    DB = KnowledgeBase(DB_LOCATION, "./notes")

    # Process input file
    if args.article:
        note = Article(args.filename)
    else:
        note = Knowledge(args.filename)
    note.metadata["key"] = generate_key(note.metadata)

    note.fetch_data()

    # Create embeddings
    note.create_embeddings()
    embeddings = {
            "title": note.metadata.get("embedding_title"),
            "summary": note.metadata.get("embedding_summary"),
            "body": note.metadata.get("embedding_body"),
        }

    # Create keywords
    keyword_example = None
    if type(DB.db) == pandas.DataFrame:
        keyword_example = get_keyword_example(embeddings)
    note.create_keywords(keyword_example)
    keywords = note.metadata["keywords"]

    if args.keyword_only:
        for keyword in keywords:
            print(f"- {keyword}")
        exit()

    # Write MD file
    md_content = MarkdownUtils.create_md_text(
        note.md_metadata(), 
        note.body)
    FileUtils.write_file(args.filename, md_content)

    # Add entry to DB
    DB.append_db_entry(
        note.db_entry(embeddings)
    )
    DB.save_db()

    print(f"Created data for {note.metadata["key"]}")