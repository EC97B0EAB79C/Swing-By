import os
import logging
import requests

from src.utils.text import TextUtils
from src.utils.warn import WarningProcessor

logger = logging.getLogger(__name__)

TOKEN = os.environ["ADS_API_KEY"]
API_ENDPOINT = "https://api.adsabs.harvard.edu/v1/search/query"

class AdsQuery:
    headers = {
        "Authorization": "Bearer " + TOKEN,
    }

    @classmethod
    def _query(self, query):
        logger.debug(f"> Query: {query}")
        params = {
            "q": query,
            "fl": "reference,doi,abstract,title,first_author,bibcode,year",
        }

        try:
            logger.debug("> Sending ADS API request")
            response = requests.get(API_ENDPOINT, headers=self.headers, params=params)
            response.raise_for_status()

            logger.debug("> Received ADS API response")
            if b"<!DOCTYPE html>" in response.content:
                raise requests.exceptions.RequestException("ADS is currently under maintenance")
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            if not docs:
                return None
            result = docs[0]
        except Exception as e:
            logger.error(f"> Failed to query ADS: {str(e)}")
            return None
        
        return result
    
    @classmethod
    def _extract_article_data(self, data, title=None):
        if data is None:
            return None, None, None, None

        fetched_title = TextUtils.get_first_string(data.get("title"))
        bibcode_references = data.get("reference", [])
        reference = [lambda x: self._bibcode_to_reference(x) for x in bibcode_references]
        bibcode = data.get("bibcode")
        doi = TextUtils.get_first_string(data.get("doi"))
        abstract = data.get("abstract")

        if title is None:
            logger.debug(f"> Successfully fetched paper: {fetched_title}")
            return bibcode, reference, doi, abstract

        if TextUtils.same(title, fetched_title):
            logger.debug(f"> Successfully fetched paper: {fetched_title}")
            return bibcode, reference, doi, abstract
        
        if WarningProcessor.process_article_warning(False, "ADS", title, fetched_title):
            logger.debug(f"> Successfully fetched paper: {fetched_title}")
            return bibcode, reference, doi, abstract
        
        return None, None, None, None
    
    @staticmethod
    def _extract_basic_data(data):
        if data is None:
            return None, None, None, None

        title = data.get("title")
        first_author = data.get("first_author")
        year = data.get("year")

        return title, first_author, year
    
    @classmethod
    def _bibcode_to_reference(self, bibcode):
        """
        Convert bibcode to reference

        Args:
            bibcode (str): Bibcode of the article

        """
        logger.debug(f"> Getting references from ADS by bibcode")
        query = f"bibcode:{bibcode}"
        result = self._query(query)
        result = self._extract_article_data(result)
        return {
            "title": result[0],
            "first_author": result[1],
            "year": result[2]
        }

    @classmethod
    def with_title(self, title, author):
        """
        Query ADS API with title and author

        Args:
            title (str): Title of the article
            author (str): Author of the article

        """
        logger.debug("Getting data from ADS by title/author")
        title = TextUtils.clean(title)
        query = f"title:'{title}' author:'{author}'"
        print(query)
        result = self._query(query)
        return self._extract_article_data(result, title)
        
    @classmethod
    def with_doi(self, doi):
        """
        Query ADS API with DOI

        Args:
            doi (str): DOI of the article

        """
        logger.debug("Getting data from ADS by DOI")
        query = f"doi:{doi}"
        result = self._query(query)
        return self._extract_article_data(result)
    
    @classmethod
    def with_arxiv(self, arxiv_id):
        """
        Query ADS API with arXiv ID

        Args:
            arxiv_id (str): arXiv ID of the article

        """
        logger.debug("Getting data from ADS by arXiv ID")
        query = f"arXiv:{arxiv_id}"
        result = self._query(query)
        return self._extract_article_data(result)
    
if __name__ == "__main__":
    print(AdsQuery.with_title(
        "Precipitation downscaling with spatiotemporal video diffusion", 
        "Srivastava, Prakhar"))