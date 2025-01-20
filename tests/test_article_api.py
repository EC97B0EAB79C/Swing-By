import pytest

from src.article_api.arxiv_api import ArxivQuery
from src.article_api.crossref_api import CrossrefQuery
from src.article_api.ads_api import AdsQuery
from src.article_api.article import Article

class TestArxivQuery:
    @pytest.mark.parametrize("title, author, id", [
        ("Precipitation downscaling with spatiotemporal video diffusion",
         "Srivastava, Prakhar",
         "2312.06071v3")
    ])
    def test_with_title(self, title, author, id):
        result = ArxivQuery.with_title(title, author)
        assert result is not None
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
        assert result is not None
        assert result["doi"] == doi
        assert result["reference"] is not None 
        assert result["first_author"] == author
        assert result["title"] is not None
        assert result["year"] is not None
        assert result["abstract"] is not None

    @pytest.mark.parametrize("doi", [
        "10.1063/1.2205307"
    ])
    def test_with_doi(self, doi):
        result = CrossrefQuery.with_doi(doi)
        assert result is not None
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
        assert result is not None
        assert result["bibcode"] == bibcode
        assert result["reference"] is not None
        assert result["doi"] == doi
        assert result["abstract"] is not None
        assert result["first_author"] == author

    def test_with_doi(self, doi, bibcode, author):
        result = AdsQuery.with_doi(doi)
        assert result is not None
        assert result["bibcode"] == bibcode
        assert result["reference"] is not None
        assert result["doi"] == doi
        assert result["abstract"] is not None
        assert result["first_author"] == author


    def test_with_arxiv(self, arxiv_id, bibcode, doi, author):
        result = AdsQuery.with_arxiv(arxiv_id)
        assert result is not None
        assert result["bibcode"] == bibcode
        assert result["reference"] is not None
        assert result["doi"] == doi
        assert result["abstract"] is not None
        assert result["first_author"] == author

    def test_bibcode_to_reference(self, bibcode, author, title):
        result = AdsQuery.with_bibcode(bibcode, False)
        assert result is not None
        assert result["title"].lower() == title.lower()
        assert result["first_author"] == author
        assert result["year"] is not None
        assert result.get("reference") is None

class TestBasicData:
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
    def bibcode(self):
        return "2023arXiv231206071S"
    @pytest.fixture
    def arxiv_id(self):
        return "2312.06071"
    @pytest.fixture
    def year(self):
        return 2023

    def test_get_basic_data_none(self):
        assert Article.get_basic_data() is None

    def test_get_basic_data_doi(self, doi, year):
        result = Article.get_basic_data(doi=doi)
        assert result is not None
        assert result["first_author"] is not None
        assert result["title"] is not None
        assert int(result["year"]) == year

    def test_get_basic_data_bibcode(self, bibcode, year):
        result = Article.get_basic_data(bibcode=bibcode)
        assert result is not None
        assert result["first_author"] is not None
        assert result["title"] is not None
        assert int(result["year"]) == year

    def test_get_basic_data_title(self, title, year):
        result = Article.get_basic_data(title=title)
        assert result is not None
        assert result["first_author"] is not None
        assert result["title"] is not None
        assert int(result["year"]) == year

    def test_get_basic_data_title_author(self, title, author, year):
        result = Article.get_basic_data(title=title, first_author=author)
        assert result is not None
        assert result["first_author"] is not None
        assert result["title"] is not None
        assert int(result["year"]) == year

    @pytest.mark.parametrize("unstructured", [
        ("Srivastava, P. (2023). Precipitation downscaling with spatiotemporal video diffusion."),
        ("Srivastava, Prakhar. \"Precipitation Downscaling with Spatiotemporal Video Diffusion.\" 2023."),
        ("P. Srivastava, \"Precipitation downscaling with spatiotemporal video diffusion,\" 2023."),
        ("Srivastava P. Precipitation downscaling with spatiotemporal video diffusion. 2023.")
    ])
    def test_get_basic_data_unstructured(self, unstructured, year):
        result = Article.get_basic_data_with_unstructured([unstructured])
        assert result is not None
        result = result[0]
        assert result["first_author"] is not None
        assert result["title"] is not None
        assert int(result["year"]) == year

class TestGetData:
    @pytest.mark.parametrize("title, author, data, notnull", [
        ("Precipitation downscaling with spatiotemporal video diffusion",
         "Srivastava, Prakhar",
         {'title': 'Precipitation downscaling with spatiotemporal video diffusion',
          'first_author': 'Srivastava, Prakhar',
          'year': '2023',
          'arxiv_id': '2312.06071v3',
          'ads_bibcode': '2023arXiv231206071S',
          'ads_doi': '10.48550/arXiv.2312.06071'},
          ["arxiv_summary", "ads_abstract", "ads_reference"]),
         ("A theoretical prediction of friction drag reduction in turbulent flow by superhydrophobic surfaces",
         "Fukagata, Koji",
         {'title': 'A theoretical prediction of friction drag reduction in turbulent flow by superhydrophobic surfaces',
          'first_author': 'Fukagata, Koji',
          'year': 2006,
          'arxiv_id': '2011.11911v2',
          'arxiv_doi': '10.1007/s00521-021-06633-z',
          'crossref_doi': '10.1063/1.2205307',
          'ads_bibcode': '2006PhFl...18e1703F',
          'ads_doi': '10.1063/1.2205307'},
         ["arxiv_summary", "crossref_abstract", "crossref_abstract", "ads_abstract", "ads_reference"])
    ])
    def test_get_data(self, title, author, data, notnull):
        result = Article.get_data(title, author)
        assert result is not None
        for key in data:
            assert result[key] == data[key]
        for key in notnull:
            assert result[key] is not None
        
        