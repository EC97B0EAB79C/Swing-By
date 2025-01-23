# Standard library imports
import logging

# Third-party imports
import pandas
import numpy as np

# Internal imports
from src.utils.file import FileUtils
from src.utils.text import TextUtils
from src.utils.md import MarkdownUtils
from src.llm_api.open import OpenAPI

from src.article_api.article_api import ArticleAPI

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


def unstructured_reference_to_sbkey(reference_list):
    logger.debug(f"Creating SBKey from unstructured reference:\n> {len(reference_list)} entries")
    structured_references = OpenAPI.article_data_extraction(reference_list)
    sbkey_list = [TextUtils.generate_sbkey(ref["title"], ref["first_author"], ref["year"]) for ref in structured_references]

    logger.debug(f"> Created {len(sbkey_list)} SBKeys")
    return sbkey_list

##
# Data processing
from datetime import datetime

def generate_key(metadata):
    return TextUtils.generate_sbkey(metadata["title"], TextUtils.get_first_string(metadata["author"]), metadata["year"])

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


##
# Processing article
if __name__ == "__main__":
    args = setup_parser()

    DB = PaperDB()

    # Process input file

    if args.article:
        note = Article(args.filename)
    else:
        note = Knowledge(args.filename)
    note.metadata["key"] = generate_key(note.metadata)

    query_title = note.metadata.get("title") or note.metadata.get("name") or note.file_name

    data = {}
    if args.article:
        data = ArticleAPI.get_data(
            query_title, 
            TextUtils.get_author(note.metadata["author"]), 
            note.metadata["year"])

    query_summary = data.get("summary") or data.get("ads_abstract")

    # Create embeddings
    embeddings = create_embedding(
        {
            "title": query_title,
            "summary": query_summary,
            "body": note.body
        }
    )

    # Create keywords
    keyword_example = None
    if type(DB.paper_db) == pandas.DataFrame:
        keyword_example = get_keyword_example(embeddings)
    note.create_keywords(keyword_example)
    keywords = note.metadata["keywords"]


    if args.keyword_only:
        for keyword in keywords:
            print(f"- {keyword}")
        exit()

    # Write MD file
    note.metadata["keywords"] = keywords
    md_content = MarkdownUtils.create_md_text(
        note.md_metadata(), 
        note.body)
    FileUtils.write_file(args.filename, md_content)

    # Add entry to DB
    DB.append_paper_db(
        note.db_entry(embeddings)
    )
    DB.save()

    print(f"Created data for {note.metadata["key"]}")