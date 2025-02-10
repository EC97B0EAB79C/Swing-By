import os
import logging
from datetime import datetime
from pathlib import Path

from src.utils.file import FileUtils
from src.utils.md import MarkdownUtils

from src.llm_api.open import OpenAPI

logger = logging.getLogger(__name__)

class Knowledge:
    ##
    # Initialize the Knowledge class
    def __init__(
            self, 
            file_name,
            db_entry:dict=None,
            ):
        logger.debug(f"Initializing Knowledge object with {file_name}")
        self.file_name = file_name
        self._load_file()
        self.key = Path(file_name).stem

        if db_entry is not None:
            logger.debug("> Loading database entry")
            self.metadata.update(db_entry)
            self.key = db_entry.get("key")
        else:
            logger.debug("> Generating new entry")
            self._generate_entry()
        
    def _load_file(self):
        logger.debug("> Loading file")
        note_lines = FileUtils.read_lines(self.file_name)
        self.metadata, self.body = MarkdownUtils.extract_yaml(note_lines)
        self.hash = FileUtils.calculate_hash(self.file_name)
        self._extract_data()

    def _extract_data(self):
        pass

    def _generate_entry(self):
        self.create_embeddings()
        self.create_keywords()
        self.metadata["summary"] = OpenAPI.summarize(self.body)

    ##
    # Create keywords
    def create_keywords(self, example=None, payload=None):
        logger.debug("> Creating keywords")
        query = self._create_payload(example, payload)
        self.metadata["keywords"] = OpenAPI.document_keyword_extraction(query)
        #TODO: Error handling?

    def _create_payload(self, example, payload=None):
        query = ""
        query += self._create_example_query(example)
        query += self._create_contents_query(payload)

        return query
    
    def _create_example_query(self, example):
        if example is None:
            return ""
        
        query = "\n\nExamples:\n"
        for e in example:
            query += f"- {e}\n"
        query += "---\n\n"

        return query
    
    def _create_contents_query(self, payload):
        if payload is not None:
            return payload
        
        query = f"title: {self.metadata.get('title')}\n"
        query += f"body:\n{self.body}\n"

        return query

    ##
    # Create embeddings
    def create_embeddings(self, additional_data=[]):
        logger.debug("> Creating embeddings")
        text = [
            self.metadata.get("title", self.key),
            self.body
        ] + additional_data

        try:
            embeddings = OpenAPI.embedding(text)
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            for t in text:
                logger.error(t)
            exit(1)

        self.metadata["embedding_title"] = embeddings[0]
        self.metadata["embedding_body"] = embeddings[1]

        return embeddings[:2]
    
    ##
    # Create entries and metadata
    def embedding_dict(self):
        return {
            "embedding_title": self.metadata.get("embedding_title"),
            "embedding_body": self.metadata.get("embedding_body")
        }

    def db_entry(self):
        result = {}
        result["key"] = self.key
        result["hash"] = self.hash

        result["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["keywords"] = self.metadata.get("keywords")
        result["file_name"] = os.path.basename(self.file_name)
        for k, v in self.embedding_dict().items():
            result[k] = v
        
        return result

    def md_metadata(self):
        result = {}
        result["key"] = self.key
        result["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["created"] = self.metadata.get("created") or result["updated"]
        result["tags"] = self.metadata.get("keywords")

        return result
    
    def fetch_data(self):
        pass
