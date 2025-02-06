# Standard library imports
import logging

# Third-party imports

from src.utils.text import TextUtils
from src.utils.dict import DictUtils

from src.article_api.arxiv_api import ArxivQuery
from src.article_api.crossref_api import CrossrefQuery
from src.article_api.ads_api import AdsQuery

from src.llm_api.open import OpenAPI

logger = logging.getLogger(__name__)

class ArticleAPI:
    ##
    # Getting Data
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
            "title": title,
            "first_author": TextUtils.get_first_string(author),
            "year": None,

            "arxiv_id": None,
            "arxiv_doi": None,
            "arxiv_summary": None,
            
            "crossref_doi": None,
            "crossref_abstract": None,
            "crossref_reference": None,
            
            "ads_bibcode": None,
            "ads_doi": None,
            "ads_abstract": None,
            "ads_reference": None
        }

        data = self._get_data(data)
        data = self._get_missing_data(data)

        #TODO Convert references to SBKeys
        return data

    @classmethod
    def _get_data(self, data):
        title = data["title"]
        author = data["first_author"]

        result = ArxivQuery.with_title(title, author)
        data = self._merge_arxiv_data(data, result)

        result = CrossrefQuery.with_title(title, author)
        data = self._merge_crossref_data(data, result)

        result = AdsQuery.with_title(title, author)
        data = self._merge_ads_data(data, result)

        return data

    @classmethod
    def _get_missing_data(self, data):
        data = self._get_missing_crossref_data(data)
        data = self._get_missing_ads_data(data)

        return data

    @classmethod
    def _get_missing_crossref_data(self, data):
        if data["crossref_reference"] is not None:
            return data
        
        if data["arxiv_doi"] is not None:
            result = CrossrefQuery.with_doi(data["arxiv_doi"])
            data = self._merge_crossref_data(data, result)

            if data["crossref_reference"] is not None:
                return data
        
        if data["ads_bibcode"] is not None:
            result = CrossrefQuery.with_doi(data["ads_doi"])
            data = self._merge_crossref_data(data, result)

            if data["crossref_reference"] is not None:
                return data
            
        return data
    
    @classmethod
    def _get_missing_ads_data(self, data):
        if data["ads_reference"] is not None:
            return data
        
        if data["arxiv_id"] is not None:
            result = AdsQuery.with_arxiv(data["arxiv_id"])
            data = self._merge_ads_data(data, result)

            if data["ads_reference"] is not None:
                return data
        
        if data["crossref_doi"] is not None:
            result = AdsQuery.with_doi(data["crossref_doi"])
            data = self._merge_ads_data(data, result)

            if data["ads_reference"] is not None:
                return data
        
        if data["arxiv_doi"] is not None:
            result = AdsQuery.with_doi(data["arxiv_doi"])
            data = self._merge_ads_data(data, result)

            if data["ads_reference"] is not None:
                return data
            
        return data
    
    @staticmethod
    def _merge_arxiv_data(data, result):
        if result is None:
            return data
        
        result["arxiv_doi"] = result.pop("doi")
        result["arxiv_summary"] = result.pop("summary")
        data = DictUtils.merge(data, result)

        return data

    @staticmethod
    def _merge_crossref_data(data, result):
        if result is None:
            return data
        
        result["crossref_doi"] = result.pop("doi")
        result["crossref_abstract"] = result.pop("abstract")
        result["crossref_reference"] = result.pop("reference")
        data = DictUtils.merge(data, result)

        return data
    
    @staticmethod
    def _merge_ads_data(data, result):
        if result is None:
            return data
        
        result["ads_bibcode"] = result.pop("bibcode")
        result["ads_doi"] = result.pop("doi")
        result["ads_abstract"] = result.pop("abstract")
        result["ads_reference"] = result.pop("reference")
        data = DictUtils.merge(data, result)

        return data

    ##
    # Getting Basic Data
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

        self._get_basic_doi(data, doi)
        if self._verify_basic_data(data):
            return data
        
        self._get_basic_bibcode(data, bibcode)
        if self._verify_basic_data(data):
            return data

        self._get_basic_title(data, title, first_author)
        if self._verify_basic_data(data):
            return data

        return None

    @staticmethod
    def _verify_basic_data(data):
        return data and data["title"] and data["first_author"] and data["year"]

    @classmethod
    def _get_basic_doi(self, data, doi):
        if doi is None:
            return data
        
        result = CrossrefQuery.with_doi(doi, get_references=False)
        data = DictUtils.merge(data, result)
        if self._verify_basic_data(data):
            return data


        result = AdsQuery.with_doi(doi, get_references=False)
        data = DictUtils.merge(data, result)
        if self._verify_basic_data(data):
            return data
        
        return data
        
    @classmethod
    def _get_basic_bibcode(self, data, bibcode):
        if bibcode is None:
            return data
        
        result = AdsQuery.with_bibcode(bibcode, get_references=False)
        data = DictUtils.merge(data, result)
        if self._verify_basic_data(data):
            return data

        return data
    
    @classmethod
    def _get_basic_title(self, data, title, first_author):
        if title is None:
            return data
        
        result = AdsQuery.with_title(title, first_author, get_references=False)
        data = DictUtils.merge(data, result)
        if self._verify_basic_data(data):
            return data

        result = CrossrefQuery.with_title(title, first_author, get_references=False)
        data = DictUtils.merge(data, result)
        if self._verify_basic_data(data):
            return data

        return data


    @staticmethod
    def get_basic_data_with_unstructured(unstructured_data):
        return OpenAPI.reference_parse(unstructured_data)
    
if __name__ == "__main__":
    data = [
        ("Precipitation downscaling with spatiotemporal video diffusion", "Srivastava, Prakhar"),
        ("A theoretical prediction of friction drag reduction in turbulent flow by superhydrophobic surfaces",
         "Fukagata, Koji")
    ]
    for title, author in data:
        print(ArticleAPI.get_data(title, author))
        print()