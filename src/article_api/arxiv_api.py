import logging

import arxiv

from src.utils.text import TextUtils
from src.utils.warn import WarningProcessor

logger = logging.getLogger(__name__)

class ArxivQuery:
    client = arxiv.Client()

    @classmethod
    def _query(self, query):
        logger.debug(f"> Query: {query}")        
        search = arxiv.Search(query=query, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
        
        try:    
            logger.debug("> Sending arXiv API request")
            results = self.client.results(search)

            logger.debug("> Received arXiv API response")
            result = next(results)
        except Exception as e:
            logger.error(f"> Failed to query arXiv: {e}")
            return None

        return self._process(result)

    @staticmethod
    def _process(data,title=None):
        if data is None:
            return None
        result = {
            "title": data.title,
            "first_author": data.authors[0].name,
            "doi": data.doi,
            "summary": data.summary,
            "arxiv_id": data.entry_id.split('/')[-1]
        }

        if title is None:
            return result

        if TextUtils.same(title, result.title):
            return result

        if WarningProcessor.process_article_warning(False, "arXiv", title, result.title):
            return result

        return None        

    @classmethod
    def with_title(self, title, author):
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
        logger.debug("Getting data from arXiv by title/author")
        title = TextUtils.clean(title)
        author = TextUtils.clean(author)
        query = f"ti:{title} AND au:{author}"
        return self._query(query)

    
    @classmethod
    def with_doi(self, doi):
        """
        Query arXiv API with DOI

        Args:
            doi (str): DOI of the article

        """
        logger.warning("Querying arXiv with DOI is not supported")
        # logger.debug("Getting data from arXiv by DOI")
        # query = f"{doi}"
        # result = self._query(query)

        # if result:
        #     logger.debug(f"> Successfully fetched paper: {result.title}")
        #     return result.entry_id.split('/')[-1], result.summary, result.doi

        return None

if __name__ == "__main__":
    arxiv_id, summary, doi = ArxivQuery.with_title("Precipitation downscaling with spatiotemporal video diffusion", "Srivastava, Prakhar")
    print(arxiv_id, summary, doi)

    # arxiv_id, summary, doi = ArxivQuery.with_doi("10.2151/sola.2019-032")
    # print(arxiv_id, summary, doi)