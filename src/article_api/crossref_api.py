import logging

# Query related
from crossref_commons.iteration import iterate_publications_as_json
from crossref_commons.retrieval import get_publication_as_json

from src.utils.text import TextUtils
from src.utils.warn import WarningProcessor

logger = logging.getLogger(__name__)

class CrossrefQuery:
    def _create_crossref_reference():
        pass

    @classmethod
    def with_title(self, title, author):
        """
        Query Crossref API with title and author

        Args:
            title (str): Title of the article
            author (str): Author of the article

        Return:
            doi (str): DOI of the article
            reference (str): Reference of the article
        """
        logger.debug("Getting data from Crossref by title/author")
        title = TextUtils.clean(title)
        author = TextUtils.clean(author)

        logger.debug(f"> Query: {title}")
        query = {"query.title": title, "query.author": author}

        logger.debug("> Sending Crossref API request")
        try:
            result = next(iterate_publications_as_json(max_results=1,queries=query))
            fetched = result["title"][0]
        except Exception as e:
            logger.error(f"> Failed to query Crossref: {str(e)}")
            return None, None
        
        if TextUtils.same(title, fetched):
            logger.debug(f"> Successfully fetched paper: {fetched}")
            return result.get("DOI"), result.get("reference")
        
        if WarningProcessor.process_article_warning(False, "Crossref", title, fetched):
            logger.debug(f"> Successfully fetched paper: {fetched}")
            return result.get("DOI"), result.get("reference")
        
        return None, None
    
    @classmethod
    def with_doi(self, doi):
        """
        Query Crossref API with DOI

        Args:
            doi (str): DOI of the article

        Return:
            doi (str): DOI of the article
            reference (str): Reference of the article
        """
        logger.debug("Getting data from Crossref by DOI")
        logger.debug(f"> Query: {doi}")

        logger.debug("> Sending Crossref API request")
        try:
            result = get_publication_as_json(doi)
            fetched = result["title"][0]
            logger.debug(f"> Successfully fetched paper: {fetched}")
            return doi,result.get("reference")
        except Exception as e:
            logger.error(f"> Failed to query Crossref: {str(e)}")
            return None, None


        
        