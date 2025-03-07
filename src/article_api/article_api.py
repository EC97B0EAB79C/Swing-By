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
    def get_data(cls, title, author):
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
            "author": author,
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

        logger.debug(f"Start data collection for {data['title']}")
        data = cls._get_data(data)
        data = cls._get_missing_data(data)
        data["key"] = TextUtils.generate_sbkey(
            data["title"],
            data["first_author"],
            data["year"]
        )

        logger.debug(f"Generating reference keys for {data['title']}")
        data["ref"] = cls.generate_sbkey(
            (data["crossref_reference"] or []) + (data["ads_reference"] or [])
            )

        logger.debug(f"Data collection complete for {data['title']}")
        return data

    @classmethod
    def _get_data(cls, data):
        logger.debug(f"Getting data with title for {data['title']}")
        title = data["title"]
        author = data["first_author"]

        result = ArxivQuery.with_title(title, author)
        data = cls._merge_arxiv_data(data, result)

        result = CrossrefQuery.with_title(title, author)
        data = cls._merge_crossref_data(data, result)

        result = AdsQuery.with_title(title, author)
        data = cls._merge_ads_data(data, result)

        return data

    @classmethod
    def _get_missing_data(cls, data):
        logger.debug(f"Getting missing data for {data['title']}")
        data = cls._get_missing_crossref_data(data)
        data = cls._get_missing_ads_data(data)

        return data

    @classmethod
    def _get_missing_crossref_data(cls, data):
        if data["crossref_reference"] is not None:
            return data
        
        if data["arxiv_doi"] is not None:
            result = CrossrefQuery.with_doi(data["arxiv_doi"])
            data = cls._merge_crossref_data(data, result)

            if data["crossref_reference"] is not None:
                return data
        
        if data["ads_bibcode"] is not None:
            result = CrossrefQuery.with_doi(data["ads_doi"])
            data = cls._merge_crossref_data(data, result)

            if data["crossref_reference"] is not None:
                return data
            
        return data
    
    @classmethod
    def _get_missing_ads_data(cls, data):
        if data["ads_reference"] is not None:
            return data
        
        if data["arxiv_id"] is not None:
            result = AdsQuery.with_arxiv(data["arxiv_id"])
            data = cls._merge_ads_data(data, result)

            if data["ads_reference"] is not None:
                return data
        
        if data["crossref_doi"] is not None:
            result = AdsQuery.with_doi(data["crossref_doi"])
            data = cls._merge_ads_data(data, result)

            if data["ads_reference"] is not None:
                return data
        
        if data["arxiv_doi"] is not None:
            result = AdsQuery.with_doi(data["arxiv_doi"])
            data = cls._merge_ads_data(data, result)

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
    def get_basic_data(cls, 
                       title:str=None, 
                       first_author:str=None, 
                       doi:str=None,
                       bibcode=None):
        data = {
            "title": title,
            "first_author": first_author,
            "year": None,
        }

        logger.debug(f"Start basic data collection for {data['title']}")
        data = cls._get_basic_doi(data, doi)
        if cls._verify_basic_data(data):
            return data
        
        data = cls._get_basic_bibcode(data, bibcode)
        if cls._verify_basic_data(data):
            return data

        data = cls._get_basic_title(data, title, first_author)
        if cls._verify_basic_data(data):
            return data

        return None

    @staticmethod
    def _verify_basic_data(data):
        return data and data["title"] and data["first_author"] and data["year"]

    @classmethod
    def _get_basic_doi(cls, data, doi):
        if doi is None:
            return data
        
        result = CrossrefQuery.with_doi(doi, get_references=False)
        data = DictUtils.merge(data, result)
        if cls._verify_basic_data(data):
            return data


        result = AdsQuery.with_doi(doi, get_references=False)
        data = DictUtils.merge(data, result)
        if cls._verify_basic_data(data):
            return data
        
        return data
        
    @classmethod
    def _get_basic_bibcode(cls, data, bibcode):
        if bibcode is None:
            return data
        
        result = AdsQuery.with_bibcode(bibcode, get_references=False)
        data = DictUtils.merge(data, result)
        if cls._verify_basic_data(data):
            return data

        return data
    
    @classmethod
    def _get_basic_title(cls, data, title, first_author):
        if title is None:
            return data
        
        result = AdsQuery.with_title(title, first_author, get_references=False)
        data = DictUtils.merge(data, result)
        if cls._verify_basic_data(data):
            return data

        result = CrossrefQuery.with_title(title, first_author, get_references=False)
        data = DictUtils.merge(data, result)
        if cls._verify_basic_data(data):
            return data

        return data


    @staticmethod
    def get_basic_data_with_unstructured(unstructured_data):
        return OpenAPI.reference_parse(unstructured_data)

    ##
    # Generating SBKey
    @classmethod
    def generate_sbkey(cls, data):
        result = []
        if not isinstance(data, list):
            return cls._dict_to_sbkey(data)

        structured, unstructured = cls._filter_unstructured(data)
        if len(unstructured) > 0:
            unstructured = OpenAPI.reference_parse(unstructured)

        result = cls._list_to_sbkey(
            structured + unstructured
            )
        

        return result
    
    @classmethod
    def _filter_unstructured(cls, data):
        structured = []
        unstructured = []
        for data_entry in data:
            if not data_entry:
                continue
            if "unstructured" in data_entry:
                unstructured.append(data_entry["unstructured"])
                continue
            structured.append(data_entry)

        return structured, unstructured
    
    @classmethod
    def _list_to_sbkey(cls, data):
        result = []
        for data_entry in data:
            sbkey = cls._dict_to_sbkey(data_entry)
            if sbkey:
                result.append(sbkey)

        return result
                
    @classmethod
    def _dict_to_sbkey(cls, data):
        if "unstructured" in data:
            data = cls.get_basic_data_with_unstructured(data["unstructured"])

        data["title"] = data.pop("article-title") if "article-title" in data else data.get("title")
        data["title"] = (
            data.get("title") or data.get("article-title") or data.get("series-title")
        )


        if "author" in data and "first_author" not in data:
            data["first_author"] = TextUtils.get_author(
                TextUtils.get_first_string(data["author"])
            )
        
        required_fields = {"title", "first_author", "year"}

        for field in required_fields:
            if data.get(field) is None:
               data.pop(field, None) 

        if not required_fields.issubset(data):
            data = cls.get_basic_data(
                data.get("title"),
                data.get("first_author"),
                data.get("doi"),
                data.get("bibcode")
            )


        if not data or "title" not in data:
            return None

        return TextUtils.generate_sbkey(
            data["title"],
            data["first_author"],
            data["year"]
        )