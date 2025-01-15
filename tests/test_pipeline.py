import pytest
from src.paper_rel_gen import *

class TestDataExtraction:
    @pytest.fixture
    def yaml_test_data(self):
        return [
            "---",
            "test_entry: 'The quick brown fox jumps over the lazy dog'",
            "---",
            "",
            "This is a test"
        ]

    @pytest.fixture
    def bibtex_test_data(self):
        return """
```BibTeX
@article{test2099article,
  title={Article Name for Testing BiBTex Extraction},
  author={Test, Author1 and Testing, Author2 and Another, Test3},
  journal={Test Case Journal},
  year={2099}
}
```
"""

    def test_extract_yaml(self, yaml_test_data):
        metadata, body = extract_yaml(yaml_test_data)

        assert metadata["test_entry"] == "The quick brown fox jumps over the lazy dog"
        assert len(body) != 0

    def test_extract_bibtex(self, bibtex_test_data):


        result = extract_bibtex(bibtex_test_data)
        expected_result = {
                    "title": "Article Name for Testing BibTex Extraction",
                    "author": ["Test, Author1", "Testing, Author2", "Another, Test3"],
                    "year": "2099",
                    "journal": "Test Case Journal"
                }
        assert result == expected_result


class TestSBKeyGeneration:
    @pytest.mark.parametrize("title, author, year, expected", [
        (
            "The Test Title", 
            "Test, Author", 
            "2099", 
            "test..2099the...ttt............."
        ),
        (
            "LongerFirst a a a a a a a a a a a a a a a a a a a a", 
            "LongTest, Author", 
            2099, 
            "longte2099longerlaaaaaaaaaaaaaaa"
        )
    ])
    def test_key_generation(self, title, author, year, expected):
        assert generate_sbkey(title, author, year) == expected