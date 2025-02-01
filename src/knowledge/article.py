
from src.article_api.article_api import ArticleAPI

from src.knowledge.knowledge import Knowledge

from src.utils.md import MarkdownUtils
from src.utils.text import TextUtils

class Article(Knowledge):
    ##
    # Initialize the Article class
    def __init__(self,
                 file_name,
                 ):
        super().__init__(
            file_name,
        )
        self._extract_data()

    def _extract_data(self):
        bibtex_metadata = MarkdownUtils.extract_bibtex(self.body)
        self.metadata.update(bibtex_metadata)

    ##
    # Create keywords
    def create_keywords(self, example=None):
        payload = f"title: {self.metadata.get('title')}\n"
        
        summary = self.summary()
        if summary:
            payload += f"summary:\n {summary}\n"
        payload += f"body:\n{self.body}\n"

        super().create_keywords(example, payload)

    ##
    # Create embeddings
    def create_embeddings(self):
        text = [
            self.summary(),
        ]
        result = super().create_embeddings(text) 
        self.metadata["embedding_summary"] = result[0]  

    ##
    # Create entries and metadata
    def db_entry(self, embeddings):
        result =  super().db_entry(embeddings)
        # Keys
        result["arxiv_id"] = self.metadata.get("arxiv_id")
        result["bibcode"] = self.metadata.get("bibcode")
        result["doi"] = self.metadata.get("crossref_doi") or self.metadata.get("ads_doi") or self.metadata.get("arxiv_doi")

        # Data
        result["title"] = self.metadata.get("title")
        result["author"] = self.metadata.get("author")
        result["year"] = self.metadata.get("year")

        # References
        result["ref"] = list(set().union(
            self.metadata.get("crossref_reference", []), 
            self.metadata.get("ads_reference", [])))
        result["cited_by"] = []

        return result
    
    def md_metadata(self):
        result =  super().md_metadata()

        # Data
        result["title"] = self.metadata.get("title")
        result["author"] = self.metadata.get("author")
        result["year"] = self.metadata.get("year")

        # Keywords
        result["category"] = result["tags"][0]
        result["tags"] = ["Paper"] + result["tags"]

        return result

    def summary(self):
        return self.metadata.get("arxiv_summary") or self.metadata.get("ads_abstract") or self.metadata.get("crossref_abstract")

    def fetch_data(self):
        super().fetch_data()

        data = ArticleAPI.get_data(
            self.metadata.get("title"), 
            TextUtils.get_author(self.metadata.get("author")), 
            self.metadata.get("year"))
        self.metadata.update(data)
