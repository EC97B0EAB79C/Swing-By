import pytest

from src.utils.md import MarkdownUtils
from src.utils.text import TextUtils
from src.utils.file import FileUtils

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
    
    @pytest.fixture
    def bibtex_dict(self):
        return {
            "title": "Article Name for Testing BibTex Extraction",
            "author": ["Test, Author1", "Testing, Author2", "Another, Test3"],
            "year": 2099,
            "bibtex_key": "test2099article"
        }

    def test_extract_yaml(self, yaml_test_data):
        metadata, body = MarkdownUtils.extract_yaml(yaml_test_data)

        assert metadata["test_entry"] == "The quick brown fox jumps over the lazy dog"
        assert len(body) != 0

    def test_extract_bibtex(self, bibtex_test_data, bibtex_dict):
        result = MarkdownUtils.extract_bibtex(bibtex_test_data)
        assert result == bibtex_dict

    #TODO
    def test_extract_code_blocks(self):
        pass
    
    #TODO
    def test_extract_section(self):
        pass

    def test_create_md_text(self, bibtex_dict):
        md_text = MarkdownUtils.create_md_text(bibtex_dict, "This is a test")
        assert md_text.startswith("---\n")
        assert md_text.endswith("\nThis is a test")

class TestTextUtils:
    @pytest.mark.parametrize("input_text, expected", [
        # Basic cases
        ("Hello, World!", "hello world"),
        ("a!b@c#1$2%3", "a b c 1 2 3"),
        ("test-case_example", "test case example"),
    ])
    def test_clean(self, input_text, expected):
        assert TextUtils.clean(input_text) == expected

    @pytest.mark.parametrize("text1, text2, expected", [
        ("Test, text!", "test text", True),
        ("This is a test for text similarity", "This is test for text similarity", True),
        ("Test, text!", "another test text", False),
    ])
    def test_similar(self, text1, text2, expected):
        assert TextUtils.similar(text1, text2) == expected

    @pytest.mark.parametrize("text1, text2, expected", [
        ("Test, text!", "test text", True),
        ("Test, text!", "another test text", False),
    ])
    def test_same(self, text1, text2, expected):
        assert TextUtils.same(text1, text2) == expected
        
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
        assert TextUtils.generate_sbkey(title, author, year) == expected

    #TODO
    def test_trim_lines(self):
        pass


class TestFileUtils:
    @pytest.mark.parametrize("file_path, expected", [
        ("tests/data/article.md", "231093aa25d7131244b1f70d4e1d7acfb79ceed6551242b374dfe17fd5ce6943d833ef405a10e262a69157ca40be5a3d59ab006e951bba259bf7d831d18cdc96"),
    ])
    def test_calculate_hash(self, file_path, expected):
        assert FileUtils.calculate_hash(file_path) == expected