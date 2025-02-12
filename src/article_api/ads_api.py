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
    def _query(cls, query, get_references=False):
        logger.debug(f"> Query: {query}")
        params = {
            "q": query,
            "fl": "reference,doi,abstract,title,first_author,bibcode,year",
        }

        try:
            logger.debug("> Sending API request")
            response = requests.get(API_ENDPOINT, headers=cls.headers, params=params)
            response.raise_for_status()

            logger.debug("> Received API response")
            if b"<!DOCTYPE html>" in response.content:
                raise requests.exceptions.RequestException("ADS is currently under maintenance")
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            if not docs:
                raise requests.exceptions.RequestException("No results found")
            result = docs[0]

        except Exception as e:
            logger.error(f"> Failed to query: {str(e)}")
            return None
        
        return cls._process(result, get_references=get_references)
    
    @classmethod
    def _process(cls, data, title=None, get_references=False):
        if data is None:
            return None
        result = {
            "title": TextUtils.get_first_string(data.get("title")),
            "first_author": data.get("first_author"),
            "year": data.get("year"),

            "bibcode": data.get("bibcode"),
            "doi": TextUtils.get_first_string(data.get("doi")),
            "abstract": data.get("abstract")
        }
        if get_references:
            result["reference"] = [cls.with_bibcode(x, get_references=False) for x in data.get("reference", [])]

        logger.debug(f"> Result: {result["title"]}")

        if title is None:
            return result
        
        if TextUtils.same(title, result["title"]):
            return result
        
        if WarningProcessor.process_article_warning(False, "ADS", title, result["title"]):
            return result
        
        return None

    @classmethod
    def with_title(cls, title, author, get_references=True):
        """
        Query ADS API with title and author

        Args:
            title (str): Title of the article
            author (str): Author of the article

        """
        logger.debug("Getting data by title/author")
        title = TextUtils.clean(title)
        query = f"title:\"{title}\""
        if author:
            query += f" author:\"{author}\""
        return cls._query(query, get_references=get_references)
        
    @classmethod
    def with_doi(cls, doi, get_references=True):
        """
        Query ADS API with DOI

        Args:
            doi (str): DOI of the article

        """
        logger.debug("Getting data by DOI")
        query = f"doi:{doi}"
        return cls._query(query, get_references=get_references)
    
    @classmethod
    def with_bibcode(cls, bibcode, get_references=True):
        """
        Query ADS API with bibcode

        Args:
            bibcode (str): Bibcode of the article

        """
        logger.debug("Getting data by bibcode")
        query = f"bibcode:{bibcode}"
        return cls._query(query, get_references=get_references)
    
    @classmethod
    def with_arxiv(cls, arxiv_id, get_references=True):
        """
        Query ADS API with arXiv ID

        Args:
            arxiv_id (str): arXiv ID of the article

        """
        logger.debug("Getting data by arXiv ID")
        query = f"arXiv:{arxiv_id}"
        return cls._query(query, get_references=get_references)
