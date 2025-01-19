# Standard library imports
import logging

# Third-party imports

from src.utils.text import TextUtils

from src.article_api.arxiv_api import ArxivQuery
from src.article_api.crossref_api import CrossrefQuery
from src.article_api.ads_api import AdsQuery

from src.llm_api.open import OpenAPI

logger = logging.getLogger(__name__)

class Article:
    @classmethod
    def get_data(self, title, author):
        """
        Get article data from the database

        Args:
            title (str): Title of the article
            author (str): Author of the article

        Returns:
            dict: Article data
        """
        data = {
            "arxiv_id": None,
            "summary": None,
            "arxiv_doi": None,
            "crossref_doi": None,
            "crossref_reference": None,
            "ads_doi": None,
            "ads_abstract": None,
            "ads_reference": None,
            "ads_bibcode": None,
        }

    @staticmethod
    def _verify_data(data):
        return data and data["title"] and data["first_author"] and data["year"]

    @classmethod
    def get_basic_data(self, 
                       title:str=None, 
                       first_author:str=None, 
                       doi:str=None,
                       bibcode=None):
        data = {
            "title": title,
            "first_author": first_author,
            "year": None,
        }

        if doi:
            data = CrossrefQuery.with_doi(doi, get_references=False)
            if self._verify_data(data):
                return data

            data = AdsQuery.with_doi(doi, get_references=False)
            if self._verify_data(data):
                return data
        
        if bibcode:
            data = AdsQuery.with_bibcode(bibcode, get_references=False)
            if self._verify_data(data):
                return data

        if title:
            data = AdsQuery.with_title(title, first_author, get_references=False)
            if self._verify_data(data):
                return data
                
            data = CrossrefQuery.with_title(title, first_author, get_references=False)
            if self._verify_data(data):
                return data

                return data
        return None



    @staticmethod
    def get_basic_data_with_unstructured(unstructured_data):
        return OpenApi.article_data_extraction(unstructured_data)    


    # def get_basic_data_bulk(self, unstructured_list):
    #     return OpenApi.article_data_extraction(unstructured_list)