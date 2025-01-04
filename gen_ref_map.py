#!/usr/bin/env python

# Standard library imports
import argparse
import logging
import re
import os
import glob

import pandas

# Global variables
# DB_LOCATION = os.environ.get("DB_LOCATION")
DB_LOCATION = "test/test.h5"

##
# Set up argument parser and logging
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


##
# Update Notes
class Note:
    def __init__(self, note_path, db_entry=None):
        self.note_path = note_path
        self.db_entry = db_entry
        with open(note_path, 'r') as f:
            self.note_lines = f.readlines()
        self.references = self._find_references()
        self.bibtex = self._find_bibtex()
        self.others_end = self._find_others()
        self._merge_references()

    def _merge_references(self):
        if not self.db_entry:
            return
        db_references = self.db_entry['ref']
        self.references = list(set().union(self.references, db_references))
        self.references.sort()

    def _find_others(self):
        in_others_section = False
        others_end = len(self.note_lines)

        for i, line in enumerate(self.note_lines):
            if "# others" in line.strip().lower():
                in_others_section = True
                continue
            if in_others_section and "#" in line.strip():
                others_end = i
                break
        return others_end if in_others_section else None

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

        self.note_lines = self.note_lines[:ref_start] + self.note_lines[ref_end:]

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

        self.note_lines = self.note_lines[:bibtex_start] + self.note_lines[bibtex_end:]

        return bibtex_text

    def _create_reference_section(self, exsitng_references=None):
        reference_section = "### References\n"
        undiscovered_section = "#### Undiscovered\n"

        for ref in self.references:
            if ref in exsitng_references:
                reference_section += f"- [[{ref}]]\n"
            else:
                undiscovered_section += f"- [[{ref}]]\n"
        return reference_section.rstrip() + "\n" + undiscovered_section.rstrip() + "\n\n"
    
    def _create_bibtex_section(self, bibtex):
        bibtex_section = "### Bibtex\n"
        bibtex_section += bibtex
        return bibtex_section.rstrip() + "\n\n"
    
    def _create_others_content(self, existing_references=None):
        text = self._create_bibtex_section(self.bibtex)
        text += self._create_reference_section(existing_references)
        return text

    def update_note(self, existing_references=None):
        contents = ""
        if self.others_end:
            contents = "".join(self.note_lines[:self.others_end])
        else:
            contents = "".join(self.note_lines).rstrip()
            contents += "\n\n## Others\n"
        contents += self._create_others_content(existing_references)
        if self.others_end:
            contents += "".join(self.note_lines[self.others_end:])

        with open(self.note_path, 'w') as f:
            f.write(contents)

##
# Notebook
class Notebook:
    def __init__(self, path, db):
        self.path = path
        self.db = db
        self.notes = self._get_notes()
        self.keys = self._get_keys()
        pass

    def _get_notes(self):
        file_list = glob.glob(f"{self.path}/*.md")
        logger.debug(f"Found {len(file_list)} notes")

        notes = []
        for file in file_list:
            references = db.search(f"key == '{file[:-3]}'")
            if references.empty:
                logger.debug(f"No entry found for the given key: {file[:-3]}")
                continue

            logger.debug(f"Processing note: {file}")
            notes.append(Note(file, references.iloc[0].to_dict()))

        return notes

    def _get_keys(self):
        pass

    def process_notes(self):
        for note in self.notes:
            self._update_note_content(note)
            self._update_note_citation(note)

    def _update_note_content(self, note):
        note.update_note()
        pass

    def _update_note_citation(self,note):
        #TODO: update citation in the cite DB
        pass


if __name__ == "__main__":
    db = PaperDB()
    notebook = Notebook(args.notebook, db)
    notebook.process_notes()
    logger.info("Done")