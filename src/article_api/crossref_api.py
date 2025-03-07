import logging

# Query related
from crossref_commons.iteration import iterate_publications_as_json
from crossref_commons.retrieval import get_publication_as_json

from src.utils.text import TextUtils
from src.utils.warn import WarningProcessor

logger = logging.getLogger(__name__)

class CrossrefQuery:

    @staticmethod
    def _process(data, title=None, get_references=False):
        if data is None:
            return None
        result = {
            "title": TextUtils.get_first_string(data.get("title")),
            "first_author": TextUtils.get_author(data.get("author")),
            "year": data.get("issued").get("date-parts")[0][0],
            
            "doi": TextUtils.get_first_string(data.get("DOI")),
            "abstract": data.get("abstract")
        }
        if get_references:
            result["reference"] = data.get("reference")

        logger.debug(f"> Result: {result["title"]}")

        if title is None:
            return result
        
        if TextUtils.same(title, result["title"]):
            return result
        
        if WarningProcessor.process_article_warning(False, "Crossref", title, result["title"]):
            return result
        
        return None
        

    @classmethod
    def with_title(cls, title, author, get_references=True):
        """
        Query Crossref API with title and author

        Args:
            title (str): Title of the article
            author (str): Author of the article

        Return:
            doi (str): DOI of the article
            reference (str): Reference of the article
        """
        logger.debug("Getting data by title/author")
        title = TextUtils.clean(title)

        logger.debug(f"> Query: {title}")
        query = {"query.title": title}
        if author:
            query["query.author"] = author

        logger.debug("> Sending API request")
        try:
            result = next(iterate_publications_as_json(max_results=1,queries=query))
        except Exception as e:
            logger.error(f"> Failed to query: {str(e)}")
            return None
        
        return cls._process(result, title, get_references=get_references)
    

    @classmethod
    def with_doi(cls, doi, get_references=True):
        """
        Query Crossref API with DOI

        Args:
            doi (str): DOI of the article

        Return:
            doi (str): DOI of the article
            reference (str): Reference of the article
        """
        logger.debug("Getting data by DOI")
        logger.debug(f"> Query: {doi}")

        logger.debug("> Sending API request")
        try:
            result = get_publication_as_json(doi)
        except Exception as e:
            logger.error(f"> Failed to query: {str(e)}")
            return None
        
        return cls._process(result, get_references=get_references)
