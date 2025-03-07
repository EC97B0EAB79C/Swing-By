
import os
import glob
import logging

import pandas
import numpy as np

from typing import Type
from pathlib import Path

import warnings
from tables.exceptions import PerformanceWarning

from src.utils.config import Config
from src.utils.file import FileUtils

from src.knowledge.knowledge import Knowledge
from src.knowledge.factory import KnowledgeFactory

from src.llm_api.open import OpenAPI

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore', category=PerformanceWarning)
warnings.simplefilter('ignore', category=PerformanceWarning)


class KnowledgeBase:
    def __init__(self, T: Type[Knowledge]):
        logger.debug(f"Initializing KnowledgeBase with {T}")
        print(f"SB: Loading KnowledgeBase")
        self.T = T
        self.db_path = os.path.join(Config.knowledgebase(), ".database", "db.h5")
        self.note_directory = Config.knowledgebase()
        self.notes = {}
        self.local_files = {Path(f).stem for f in glob.glob(os.path.join(self.note_directory, "*.md"))}
        self._load_db()

        self._process_files()

    ##
    # DB Related
    def _load_db(self):
        logger.debug(f"> Loading DB from {self.db_path}")
        try:
            self.db = pandas.read_hdf(self.db_path, key="knowledge")
            logger.debug(f"Loaded {len(self.db.index)} entries from DB")
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
            logger.info("Creating new DB")
            os.makedirs(os.path.join(Config.knowledgebase(), ".database"), exist_ok=True)
            self.db = pandas.DataFrame(columns=[
                "key", "hash", "updated", "keywords", "file_name"    
            ])
            self.save_db()

    def save_db(self):
        try:
            with pandas.HDFStore(self.db_path, mode='w') as store:
                store.put('knowledge', self.db)
        except Exception as e:
            logger.error(f"Error saving DB: {e}")
            exit()
        logger.info(f"> Saved {len(self.db.index)} entries to DB")

    def append_db_entry(self, entry):
        new_df = pandas.DataFrame.from_dict([entry])
        self.db = pandas.concat([self.db, new_df]).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
        logger.debug(f"> Appended to DB: {entry['key']}")

    def vector_search(self, key, vector, n=5):
        search_df = self.db.copy()
        search_df["distance"] = search_df[key].apply(lambda x: float('inf') if x is None else np.linalg.norm(x - vector))
        search_df = search_df.sort_values(by='distance', ascending=False)
        return search_df[:n]
    
    def get_entry(self, key):
        return self.db[self.db['key'] == key].iloc[0]
    
    def update_entry(self, key, entry):
        i = self.db[self.db['key'] == key].index[0]
        self.db.loc[i] = entry
        self.save_db()

    ##
    # LLM Related
    def _get_relevant_by_vector(self, query, n=5):
        query_embedding = OpenAPI.embedding([query])[0]
        embedding_keys = self.db.filter(regex="^embedding_").keys()

        related_rows = []
        for key in embedding_keys:
            related_rows.append(self.vector_search(key, query_embedding, n=5))
        
        if not related_rows:
            return pandas.DataFrame()
        related_df = pandas.concat(related_rows)
        related_df = related_df.drop_duplicates(subset='key', keep='last')
        related_df = related_df.sort_values('distance').head(n)
        related_df = related_df.reset_index(drop=True)
        return related_df
    
    def _get_relevant_by_keywords(self, query, n=5):
        query_keywords = OpenAPI.query_keyword_generation(query)
        keyword_matches = self.db[self.db['keywords'].apply(lambda x: sum(k in query_keywords for k in x) > 0)].copy()
        if keyword_matches.empty:
            return pandas.DataFrame()
        
        keyword_matches['match_count'] = keyword_matches['keywords'].apply(lambda x: sum(k in query_keywords for k in x))
        keyword_matches = keyword_matches.sort_values('match_count', ascending=False).head(n)
        keyword_matches = keyword_matches.drop('match_count', axis=1)
        return keyword_matches

    # TODO: Improve this function
    def _get_relevant(self, query):
        print(f"SB: > Getting relevant notes")
        if self.db.empty:
            return self.db

        related_rows = []
        # Related by vector search
        print("SB: > Getting related by vector")
        related_rows.append(self._get_relevant_by_vector(query))
        # # Related by keywords        
        # print("SB: > Getting related by keywords")
        # related_rows.append(self._get_relevant_by_keywords(query))

        related_df = pandas.concat(related_rows).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
        return related_df

    def qna(self, query):
        print("SB: Generating answer")
        related = self._get_relevant(query)

        token_count = 6000
        example = "Related\n"
        for i, row in related.iterrows():
            current_row = f"# {row['title'] if 'title' in row else row['key']}\n{self._load_note(row['key'], row['file_name']).body}\n\n"
            token_count -= len(current_row.split()) * 2 
            if token_count < 0:
                break
            print(f"SB: > Adding related note: {row['key']}")
            example += current_row

        answer = OpenAPI.qna(query, example)
        return answer

    ##
    # Knowledge Management Related
    def _load_note(self, key, file_name):
        file_path = os.path.join(self.note_directory, file_name)
        if self.notes.get(key):
            return self.notes[key]
        else:
            note = self.T(
                file_path,
                dict(self.db.loc[self.db['key'] == key].iloc[0]) if key in self.db['key'].values else None
                )
            self.notes[key] = note
            return note

    def _process_new_file(self, file_path):
        print(f"SB: > Processing new files: {file_path}")
        logger.debug(f"Processing new file: {file_path}")
        note = self.T(file_path, local_files = self.local_files)

        entry = note.db_entry()
        self.append_db_entry(entry)
        self.notes[note.key] = note
        self.save_db()

    def _process_existing_file(self, file_path):
        key = Path(file_path).stem
        entry = dict(self.get_entry(key))
        if FileUtils.calculate_hash(file_path) == entry["hash"]:
                logger.debug(f"Updating references: {file_path}")
                note =  self.T(file_path, entry, local_files = self.local_files)
        else:
            print(f"SB: > Processing updated files: {file_path}")
            logger.debug(f"Processing updated file: {file_path}")
            note = self.T(file_path, local_files = self.local_files)

        entry = note.db_entry()
        self.update_entry(key, entry)
        self.notes[note.key] = note

    def _process_files(self):
        note_files = set(os.path.basename(f) for f in glob.glob(os.path.join(self.note_directory, "*.md")))
        db_files = set(self.db["file_name"].tolist())

        for file in note_files:
            if file not in db_files:
                self._process_new_file(file)
            else:
                self._process_existing_file(file)
            self.local_files.add(file)
        #TODO: Improve existing reference update
