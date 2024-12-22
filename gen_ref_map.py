#!/usr/bin/env python

# Standard library imports
import logging
import os


# Global variables
DB_LOCATION = os.environ.get("DB_LOCATION")

##
# Set up argument parser and logging
import argparse
parser = argparse.ArgumentParser(
    prog='gen_ref_map',
    description='Generate reference map for acedemic papers'
)
parser.add_argument(
    'notebook',
    description="Path to the mote directory"
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="Print debug information"
)
args = parser.parse_args()

level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)


##
# DB
class PaperDB:
    def __init__(self):
        self.path = DB_LOCATION
        self.df = None

    def load(self):
        pass

    def save(self):
        pass

    def search(self, query):
        pass

class Connections:
    def __init__(self, db):
        self.references = {}
        self.db = db
        self._load()
        self._generate()

    def _load(self):
        pass

    def _generate(self):
        pass

    def get_references(self, entry):
        pass

    def get_citations(self, entry):
        pass


##
# Update Notes
def _find_reference_section(note):
    body_before = ""
    body_after = ""
    pass
    return body_before, body_after


def _create_reference_section(note, references):
    reference_section = ""
    pass
    return reference_section

def update_note(entry, references):
    pass

