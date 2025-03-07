import pytest
import numpy as np

from src.llm_api.open import OpenAPI

class TestOpenAPI:
    @pytest.fixture
    def query(self):
        return "What is vector search?"
    
    @pytest.fixture
    def test_file(self):
        return "tests/data/article.md"

    @pytest.fixture
    def test_error_log(self):
        return """
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "module_3.py", line 27, in function_b
  File "module_1.py", line 15, in function_a
  File "module_4.py", line 38, in function_c
  File "module_2.py", line 22, in function_a
  File "module_5.py", line 43, in function_b
  File "module_3.py", line 19, in function_c
KeyError: Key not found in dictionary
"""

    @pytest.fixture
    def test_reference(self):
        return "Smithson, J. B., & Rodriguez, M. K. (2024). The impact of artificial sleep patterns on cognitive development in adolescents. Journal of Neural Development, 45(3), 234-251."

    def test_embedding(self, test_error_log):
        result = OpenAPI.embedding([test_error_log])
        assert len(result[0]) == 1536

    def test_qna(self, query):
        result = OpenAPI.qna(query)
        assert len(result["answer"]) != 0

    def test_query_keyword_generation(self, query):
        result = OpenAPI.query_keyword_generation(query)
        assert len(result) != 0

    def test_document_keyword_extraction(self, test_file, n=10):
        with open(test_file, "r") as f:
            text = f.read()
        result = OpenAPI.document_keyword_extraction(text)
        assert len(result) == 10

    def test_reference_parse(self, test_reference):
        result = OpenAPI.reference_parse([test_reference])[0]

        assert result["title"] == "The impact of artificial sleep patterns on cognitive development in adolescents"
        assert result["year"] == 2024
        assert result["first_author"].split(",")[0] == "Smithson"

    def test_summarize(self, test_file):
        with open(test_file, "r") as f:
            text = f.read()
        result = OpenAPI.summarize(text)
        assert len(result) != 0

    def test_analyze_error(self, test_error_log):
        result = OpenAPI.analyze_error(test_error_log)
        assert result["error_message"] not in ["", None]
        assert result["location"] not in ["", None]
        assert result["traceback"] not in ["", None]