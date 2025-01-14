import pytest
from src.paper_rel_gen import *

def test_test():
    assert 1==1


def test_extract_yaml():
    test_data=[
        "---",
        "test_entry: 'The quick brown fox jumps over the lazy dog'",
        "---",
        "",
        "This is a test"
    ]

    metadata, body = extract_yaml(test_data)

    assert metadata["test_entry"] == "The quick brown fox jumps over the lazy dog"
    assert len(body) != 0