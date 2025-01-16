import pytest

from src.article_api.arxiv_api import ArxivQuery
from src.article_api.crossref_api import CrossrefQuery
from src.article_api.ads_api import AdsQuery

class TestArxivQuery:
    @pytest.mark.parametrize("title, author, id", [
        ("Precipitation downscaling with spatiotemporal video diffusion",
         "Srivastava, Prakhar",
         "2312.06071v3")
    ])
    def test_with_title(self, title, author, id):
        arxiv_id, summary, doi = ArxivQuery.with_title(title, author)
        assert arxiv_id == id
        assert summary is not None

class TestCrossrefQuery:
    @pytest.mark.parametrize("title, author, doi", [
        ("A theoretical prediction of friction drag reduction in turbulent flow by superhydrophobic surfaces",
         "Fukagata, Koji",
         "10.1063/1.2205307")
    ])
    def test_with_title(self, title, author, doi):
        crossref_doi, reference = CrossrefQuery.with_title(title, author)
        assert crossref_doi == doi
        assert reference is not None

    @pytest.mark.parametrize("doi", [
        "10.1063/1.2205307"
    ])
    def test_with_doi(self, doi):
        crossref_doi, reference = CrossrefQuery.with_doi(doi)
        assert crossref_doi == doi
        assert reference is not None

class TestAdsQuery:
    @pytest.fixture
    def bibcode(self):
        return "2023arXiv231206071S"
    @pytest.fixture
    def title(self):
        return "Precipitation downscaling with spatiotemporal video diffusion"
    @pytest.fixture
    def author(self):
        return "Srivastava, Prakhar"
    @pytest.fixture
    def doi(self):
        return "10.48550/arXiv.2312.06071"
    @pytest.fixture
    def arxiv_id(self):
        return "2312.06071"
    
    def test_with_title(self, title, author, bibcode):
        q_bibcode, reference, doi, abstact = AdsQuery.with_title(title, author)
        assert q_bibcode == bibcode
        assert reference is not None
        assert doi is not None
        assert abstact is not None

    def test_with_doi(self, doi, bibcode):
        q_bibcode, reference, q_doi, abstact = AdsQuery.with_doi(doi)
        assert q_bibcode == bibcode
        assert reference is not None
        assert q_doi == doi
        assert abstact is not None

    def test_with_arxiv(self, arxiv_id, bibcode):
        q_bibcode, reference, doi, abstact = AdsQuery.with_arxiv(arxiv_id)
        assert q_bibcode == bibcode
        assert reference is not None
        assert doi is not None
        assert abstact is not None
