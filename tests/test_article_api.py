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
        result = ArxivQuery.with_title(title, author)
        assert result["title"].lower() == title.lower()
        assert result["arxiv_id"] == id
        assert result["summary"] is not None
        assert isinstance(result["first_author"], str)

class TestCrossrefQuery:
    @pytest.mark.parametrize("title, author, doi", [
        ("A theoretical prediction of friction drag reduction in turbulent flow by superhydrophobic surfaces",
         "Fukagata, Koji",
         "10.1063/1.2205307")
    ])
    def test_with_title(self, title, author, doi):
        result = CrossrefQuery.with_title(title, author)
        assert result["doi"] == doi
        assert result["reference"] is not None 
        assert isinstance(result["first_author"], str)
        assert result["title"] is not None
        assert result["year"] is not None
        assert result["abstract"] is not None

    @pytest.mark.parametrize("doi", [
        "10.1063/1.2205307"
    ])
    def test_with_doi(self, doi):
        result = CrossrefQuery.with_doi(doi)
        assert result["doi"] == doi
        assert result["reference"] is not None
        assert isinstance(result["first_author"], str)
        assert result["title"] is not None
        assert result["year"] is not None
        assert result["abstract"] is not None

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
    
    def test_with_title(self, title, author, bibcode, doi):
        result = AdsQuery.with_title(title, author)
        assert result["bibcode"] == bibcode
        assert result["reference"] is not None
        assert result["doi"] == doi
        assert result["abstract"] is not None
        assert result["first_author"] == author

    def test_with_doi(self, doi, bibcode, author):
        result = AdsQuery.with_doi(doi)
        assert result["bibcode"] == bibcode
        assert result["reference"] is not None
        assert result["doi"] == doi
        assert result["abstract"] is not None
        assert result["first_author"] == author


    def test_with_arxiv(self, arxiv_id, bibcode, doi, author):
        result = AdsQuery.with_arxiv(arxiv_id)
        assert result["bibcode"] == bibcode
        assert result["reference"] is not None
        assert result["doi"] == doi
        assert result["abstract"] is not None
        assert result["first_author"] == author

    def test_bibcode_to_reference(self, bibcode, author, title):
        result = AdsQuery._bibcode_to_reference(bibcode)
        assert result["title"].lower() == title.lower()
        assert result["first_author"] == author
        assert result["year"] is not None
        assert result.get("reference") is None