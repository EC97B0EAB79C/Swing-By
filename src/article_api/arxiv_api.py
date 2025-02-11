import logging

import arxiv

from src.utils.text import TextUtils
from src.utils.warn import WarningProcessor

logger = logging.getLogger(__name__)

class ArxivQuery:
    client = arxiv.Client()

    @classmethod
    def _query(cls, query, title=None):
        logger.debug(f"> Query: {query}")        
        search = arxiv.Search(query=query, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
        
        try:    
            logger.debug("> Sending API request")
            results = cls.client.results(search)

            logger.debug("> Received API response")
            result = next(results)
        except Exception as e:
            logger.error(f"> Failed to query: {e}")
            return None

        return cls._process(result, title)


    @staticmethod
    def _process(data,title=None):
        if data is None:
            return None
        result = {
            "title": data.title,
            "first_author": data.authors[0].name,

            "arxiv_id": data.entry_id.split('/')[-1],
            "doi": data.doi,
            "summary": data.summary
        }

        logger.debug(f"> Result: {result["title"]}")

        if title is None:
            return result

        if TextUtils.same(title, result["title"]):
            return result

        if WarningProcessor.process_article_warning(False, "arXiv", title, result["title"]):
            return result

        return None        


    @classmethod
    def with_title(cls, title, author):
        """
        Query arXiv API with title and author

        Args:
            title (str): Title of the article
            author (str): Author of the article

        Return:
            arxiv_id (str): arXiv ID of the article
            summary (str): Summary of the article
            doi (str): DOI of the article
        """
        logger.debug("Getting data by title/author")
        title = TextUtils.clean(title)
        query = f"ti:{title}"
        if author:
            query += f" AND au:{author}"
        return cls._query(query, title)
