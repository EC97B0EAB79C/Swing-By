import pytest

from src.utils.md import MarkdownUtils
from src.utils.text import TextUtils

class TestMarkdownUtils:
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
  title={Article Name for Testing BibTex Extraction},
  author={Test, Author1 and Testing, Author2 and Another, Test3},
  journal={Test Case Journal},
  year={2099}
}
```
"""

    def test_extract_yaml(self, yaml_test_data):
        metadata, body = MarkdownUtils.extract_yaml(yaml_test_data)

        assert metadata["test_entry"] == "The quick brown fox jumps over the lazy dog"
        assert len(body) != 0

    def test_extract_bibtex(self, bibtex_test_data):


        result = MarkdownUtils.extract_bibtex(bibtex_test_data)
        expected_result = {
                    "title": "Article Name for Testing BibTex Extraction",
                    "author": ["Test, Author1", "Testing, Author2", "Another, Test3"],
                    "year": 2099,
                    "bibtex_key": "test2099article"
                }
        assert result == expected_result

class TestTextUtils:
    @pytest.mark.parametrize("input_text, expected", [
        # Basic cases
        ("Hello, World!", "hello world"),
        ("a!b@c#1$2%3", "a b c 1 2 3"),
        ("test-case_example", "test case example"),
    ])
    def test_clean(self, input_text, expected):
        assert TextUtils.clean(input_text) == expected

    def test_same(self):
        assert TextUtils.same("Test, text!", "test text")
        assert not TextUtils.same("Test, text!", "another test text")