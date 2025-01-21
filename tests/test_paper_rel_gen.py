import pytest

from paper_rel_gen import *

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
        data = {
            "title": title,
            "author": author,
            "year": year
        }
        assert generate_key(data) == expected
