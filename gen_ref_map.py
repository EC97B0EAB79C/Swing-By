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
    #TODO DB Related functions
    def __init__(self):
        self.path = DB_LOCATION
        self.df = None

    def load(self):
        pass

    def save(self):
        pass

    def update(self, entry):
        pass

    def search(self, query):
        pass


##
# Reference Map
class RelationMap:
    #TODO Reference Map Related functions
    def __init__(self, db):
        self.db = db

    def add_reference(self, from_key, to_key):
        pass

    def merge_keywords(self):
        merge_list = self._get_merge_list()
        self._modify_keywords(merge_list)

    def _get_merge_list(self):
        pass

    def _modify_keywords(self, merge_list):
        pass

    def generate_citation(self):
        pass

    def _get_citation(self, key):
        pass

##
# Update Notes
#TODO Adding reference to notes
def _find_reference_section(note):
    body_before = ""
    body_after = ""
    reference_list = []
    pass
    return body_before, reference_list, body_after


def _create_reference_section(note, references):
    reference_section = ""
    pass
    return reference_section

def update_note(entry, references):
    pass

