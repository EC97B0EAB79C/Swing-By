# Standard library imports

# Third-party imports

from src.utils.text_utils import TextUtils

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
