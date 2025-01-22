
import os
import pytest

from src.knowledge.knowledge import Knowledge
from src.knowledge.article import Article

class TestKnowledge:
    @pytest.fixture
    def file_name(self):
        return "tests/data/article.md"
    @pytest.fixture
    def test_field(self):
        return "test value"
    @pytest.fixture
    def created(self):
        return "2025-01-10 17:27:06"

    def test_knowledge_init(self, file_name, test_field):
        knowledge = Knowledge(file_name)
        assert knowledge.metadata is not None
        assert knowledge.body is not None

        assert knowledge.metadata["test_field"] == test_field

    def test_knowledge_db_entry(self, file_name):
        knowledge = Knowledge(file_name)
        knowledge.metadata["keywords"] = ["test_tag"]
        embeddings = {"emb_test": "value" ,"emb_test2": "value2"}
        result = knowledge.db_entry(embeddings)
        assert result is not None
        #TODO adding key
        # assert result["key"] is not None
        assert result["keywords"] is not None
        assert result["file_name"] == os.path.basename(file_name)
        for k, v in embeddings.items():
            assert result[k] == v

    def test_knowledge_md_metadata(self, file_name, created):
        knowledge = Knowledge(file_name)
        knowledge.metadata["keywords"] = ["test_tag"]
        result = knowledge.md_metadata()
        assert result is not None
        #TODO adding key
        # assert result["key"] is not None
        assert result["updated"] is not None
        assert result["created"] == created
        assert result["tags"] is not None

class TestArticle:
    @pytest.fixture
    def file_name(self):
        return "tests/data/article.md"
    @pytest.fixture
    def test_field(self):
        return "test value"
    @pytest.fixture
    def title(self):
        return "A theoretical prediction of friction drag reduction in turbulent flow by superhydrophobic surfaces"
    @pytest.fixture
    def first_author(self):
        return "Fukagata, Koji"
    @pytest.fixture
    def year(self):
        return "2006"

    def test_article_init(self, 
                          file_name, 
                          test_field,
                          title,
                          first_author,
                          year
                          ):
        article = Article(file_name)
        assert article.metadata is not None
        assert article.body is not None

        assert article.metadata["test_field"] == test_field
        assert article.metadata["title"] == title
        assert article.metadata["author"][0] == first_author
        assert str(article.metadata["year"]) == year

    def test_article_db_entry(self, file_name, title, first_author, year):
        article = Article(file_name)
        embeddings = {"emb_test": "value" ,"emb_test2": "value2"}
        article.metadata["keywords"] = ["test_tag"]
        result = article.db_entry(embeddings)
        assert result is not None
        # Inherited from Knowledge
        #TODO adding key
        # assert result["key"] is not None
        assert result["keywords"] is not None
        assert result["file_name"] == os.path.basename(file_name)
        for k, v in embeddings.items():
            assert result[k] == v

        # New fields
        #TODO adding arxiv_id, bibcode, doi
        assert result["title"] == title
        assert result["author"][0] == first_author
        assert str(result["year"]) == year

        #TODO adding ref, cited_by

    def test_article_md_metadata(self, file_name, title, first_author, year):
        article = Article(file_name)
        article.metadata["keywords"] = ["test_tag"]
        result = article.md_metadata()
        assert result is not None
        # Inherited from Knowledge
        #TODO adding key
        # assert result["key"] is not None
        assert result["updated"] is not None
        assert result["created"] is not None
        assert result["tags"] is not None

        # New fields
        assert result["title"] == title
        assert result["author"][0] == first_author
        assert str(result["year"]) == year
        assert result["category"] is not None
        assert result["tags"][0] == "Paper"

        #TODO adding category, tags