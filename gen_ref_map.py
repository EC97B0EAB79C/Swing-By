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
        GPT_INSTRUCTIONS = """
This GPT specializes in organizing keywords for academic purposes.
It identifies related keywords that can be grouped or merged while respecting the academic significance of specific terms.
Keywords with distinct meanings or relevance in academic contexts, such as 'physics_informed_learning,' are not merged into broader terms like 'machine_learning.'
Instead, the system ensures that academically significant keywords retain their individuality.
When merging is appropriate, it creates meaningful representative terms that align with academic conventions and clarity.
It outputs the response in JSON format, where each key represents a chosen 'representative' keyword and the value is a list of related interchangeable keywords to merge under that representative keyword.
Additionally, it can create new representative keywords when merging existing ones makes sense, such as combining related but distinct terms like 'continuous_time_models' and 'discrete_time_models' into 'time_models.'
Keywords that do not require merging are excluded from the output, ensuring the results focus only on meaningful groupings.
"""
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

