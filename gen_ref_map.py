#!/usr/bin/env python

# Standard library imports
import logging
import re
import os


import pandas

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
    help="Path to the mote directory"
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
        self.paper_db = None
        self.ref_db = None
        self.load()

    def load(self):
        logger.debug("Loading DB")
        try:
            self.paper_db = pandas.read_hdf(DB_LOCATION, key="paper")
            self.ref_db = pandas.read_hdf(DB_LOCATION, key="ref")
            logger.debug(f"Loaded {len(self.paper_db.index)} entries from DB")
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
            exit(1)

    def save(self):
        logger.debug("Saving DB")
        try:
            with pandas.HDFStore(DB_LOCATION, mode='w') as store:
                store.put("paper", self.paper_db)
                store.put("ref", self.ref_db)
        except Exception as e:
            logger.error(f"Error saving DB: {e}")
            exit(1)
        logger.debug(f"Saved {len(self.paper_db.index)} entries to DB")

    def update(self, entry:dict):
        logger.debug(f"Updating entry: {entry['key']}")
        if entry['key'] in self.paper_db.index:
            self.paper_db.loc[entry['key']] = entry
            logger.debug(f"Updated entry with key: {entry['key']}")
        else:
            logger.error(f"Entry with key {entry['key']} not found in DB")

    def search(self, query):
        logger.debug(f"Searching for: {query}")
        result = self.paper_db.query(query)
        logger.debug(f"Found {len(result.index)} entries")
        return result


# ##
# # Reference Map
# class RelationMap:
#     #TODO Reference Map Related functions
#     def __init__(self, db):
#         self.db = db

#     def add_reference(self, from_key, to_key):
#         pass

#     def merge_keywords(self):
#         merge_list = self._get_merge_list()
#         self._modify_keywords(merge_list)

#     def _get_merge_list(self):
#         GPT_INSTRUCTIONS = """
# This GPT specializes in organizing keywords for academic purposes.
# It identifies related keywords that can be grouped or merged while respecting the academic significance of specific terms.
# Keywords with distinct meanings or relevance in academic contexts, such as 'physics_informed_learning,' are not merged into broader terms like 'machine_learning.'
# Instead, the system ensures that academically significant keywords retain their individuality.
# When merging is appropriate, it creates meaningful representative terms that align with academic conventions and clarity.
# It outputs the response in JSON format, where each key represents a chosen 'representative' keyword and the value is a list of related interchangeable keywords to merge under that representative keyword.
# Additionally, it can create new representative keywords when merging existing ones makes sense, such as combining related but distinct terms like 'continuous_time_models' and 'discrete_time_models' into 'time_models.'
# Keywords that do not require merging are excluded from the output, ensuring the results focus only on meaningful groupings.
# """
#         pass

#     def _modify_keywords(self, merge_list):
#         pass

#     def generate_citation(self):
#         pass

#     def _get_citation(self, key):
#         pass

##
# Update Notes
class NoteUpdater:
    def __init__(self, note_path):
        self.note_path = note_path
        with open(note_path, 'r') as f:
            self.note_lines = f.readlines()
        self.references = self._find_references()
        self.bibtex = self._find_bibtex()

    def _find_references(self):
        in_reference_section = False
        ref_start = 0
        ref_end = len(self.note_lines)
        
        for i, line in enumerate(self.note_lines):
            if "# references" in line.strip().lower():
                in_reference_section = True
                ref_start = i
                continue
            if in_reference_section and "#" in line.strip():
                ref_end = i

        if not in_reference_section:
            return []

        reference_text = "".join(self.note_lines[ref_start:ref_end])
        reference_list = re.findall(r"\[\[(.*?)\]\]", reference_text)
        return reference_list
    
    def _find_bibtex(self):
        in_bibtex_section = False
        bibtex_start = 0
        bibtex_end = len(self.note_lines)

        for i, line in enumerate(self.note_lines):
            if "# bibtex" in line.strip().lower():
                in_bibtex_section = True
                bibtex_start = i
                continue
            if in_bibtex_section and "#" in line.strip():
                bibtex_end = i
                break
        
        if not in_bibtex_section:
            return ""
        
        bibtex_text = "".join(self.note_lines[bibtex_start+1:bibtex_end])
        return bibtex_text

    def _create_reference_section(self, references):
        reference_section = "### References\n"
        for ref in references:
            reference_section += f"- [[{ref}]]\n"
        return reference_section + "\n"
    
    def _create_bibtex_section(self, bibtex):
        bibtex_section = "### Bibtex\n"
        bibtex_section += bibtex
        return bibtex_section + "\n"
    
    def _create_others_section(self):
        text = "## Others\n"
        text += self._create_reference_section(self.references)
        text += self._create_bibtex_section(self.bibtex)
        return text

    def update_note(self):
        #TODO Update note
        pass


##
# Test code
test = NoteUpdater(args.notebook)
print(test._create_others_section())