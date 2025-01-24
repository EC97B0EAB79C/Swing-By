import os
from datetime import datetime

from src.utils.file import FileUtils
from src.utils.md import MarkdownUtils

from src.llm_api.open import OpenAPI

class Knowledge:
    ##
    # Initialize the Knowledge class
    def __init__(self, 
                 file_name,
                 
                 ):
        self.file_name = file_name
        self._load_file()
        
    def _load_file(self):
        note_lines = FileUtils.read_lines(self.file_name)
        self.metadata, self.body = MarkdownUtils.extract_yaml(note_lines)

    ##
    # Create keywords
    def create_keywords(self, example=None, payload=None):
        query = self._create_payload(example, payload)
        self.metadata["keywords"] = OpenAPI.keyword_extraction(query)
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
    def create_embeddings(self, additional_data):
        text = [
            self.metadata.get("title"),
            self.body
        ] + additional_data

        embeddings = OpenAPI.create_embedding(text)

        self.metadata["embedding_title"] = embeddings[0]
        self.metadata["embedding_body"] = embeddings[1]

        return embeddings[:2]
    
    ##
    # Create entries and metadata
    def db_entry(self, embeddings):
        result = {}
        result["key"] = self.metadata.get("key")
        result["keywords"] = self.metadata.get("keywords")
        result["file_name"] = os.path.basename(self.file_name)
        for k, v in embeddings.items():
            result[k] = v
        
        return result

    def md_metadata(self):
        result = {}
        result["key"] = self.metadata.get("key")
        result["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["created"] = self.metadata.get("created") or result["updated"]
        result["tags"] = self.metadata.get("keywords")

        return result
    
    def fetch_data(self):
        pass
