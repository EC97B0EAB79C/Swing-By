
from src.knowledge.knowledge import Knowledge
from src.utils.md import MarkdownUtils

class Article(Knowledge):
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