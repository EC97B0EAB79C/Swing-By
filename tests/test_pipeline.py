import pytest
from src.paper_rel_gen import *

def test_test():
    assert 1==1


def test_extract_yaml():
    test_data=[
        "---",
        "test_entry: 'The quick brown fox jumps over the lazy dog'"
        "---"
    ]

    result = extract_yaml(test_data)

    assert result == {"test_entry": "The quick brown fox jumps over the lazy dog"}