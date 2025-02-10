
from src.article_api.article_api import ArticleAPI

from src.knowledge.knowledge import Knowledge

from src.utils.md import MarkdownUtils
from src.utils.text import TextUtils

#TODO Article API
class Article(Knowledge):
    ##
    # Initialize the Article class
    def __init__(
            self,
            file_name,
            db_entry = None
            ):
        super().__init__(
            file_name,
            db_entry
        )

    def _generate_entry(self):
        self._extract_bibtex_data()
        self._query_article_data()
        super()._generate_entry()

    def _extract_bibtex_data(self):
        bibtex_metadata = MarkdownUtils.extract_bibtex(self.body)
        self.metadata.update(bibtex_metadata)

    def _query_article_data(self):
        data = ArticleAPI.get_data(
            self.metadata.get("title"),
            self.metadata.get("author"),
        )
        self.metadata.update(data)
        self.key = self.metadata.get("key")

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
        summary = self.summary()
        if summary is None:
            super().create_embeddings()
            return
            
        result = super().create_embeddings([summary]) 
        self.metadata["embedding_summary"] = result[0]  

    ##
    # Create entries and metadata
    def embedding_dict(self):
        return super().embedding_dict() | {
            "embedding_summary": self.metadata.get("embedding_summary"),
        }

    def db_entry(self):
        result =  super().db_entry()
        # Keys
        result["arxiv_id"] = self.metadata.get("arxiv_id")
        result["bibcode"] = self.metadata.get("bibcode")
        result["doi"] = self.metadata.get("crossref_doi") or self.metadata.get("ads_doi") or self.metadata.get("arxiv_doi")

        # Data
        result["title"] = self.metadata.get("title")
        result["author"] = self.metadata.get("author")
        result["year"] = self.metadata.get("year")

        # References
        result["ref"] = self.metadata.get("ref")
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
