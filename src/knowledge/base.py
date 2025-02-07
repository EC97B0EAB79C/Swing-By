
import os
import glob
import logging

import pandas
import numpy as np

from typing import Type

from src.utils.config import Config
from src.utils.file import FileUtils

from src.knowledge.knowledge import Knowledge
from src.knowledge.factory import KnowledgeFactory

from src.llm_api.open import OpenAPI

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, T: Type[Knowledge]):
        self.T = T
        self.db_path = os.path.join(Config.knowledgebase(), ".database", "db.h5")
        self.note_directory = Config.knowledgebase()
        self.notes = {}
        self._load_db()

        self._process_new_files()

    ##
    # DB Related
    def _load_db(self):
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

    def save_db(self):
        try:
            with pandas.HDFStore(self.db_path, mode='w') as store:
                store.put('knowledge', self.db)
        except Exception as e:
            logger.error(f"Error saving DB: {e}")
            exit()
        logger.info(f"Saved {len(self.db.index)} entries to DB")

    def append_db_entry(self, entry):
        new_df = pandas.DataFrame.from_dict([entry])
        self.db = pandas.concat([self.db, new_df]).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
        logger.debug(f"Appended to DB: {entry['key']}")

    def vector_search(self, key, vector, n=5):
        search_df = self.db.copy()
        search_df["distance"] = search_df[key].apply(lambda x: np.linalg.norm(x - vector))
        search_df = search_df.sort_values(by='distance', ascending=False)
        return search_df[:n]

    ##
    # LLM Related
    def _get_relevant(self, query):
        # Related by vector search
        query_embedding = OpenAPI.embedding([query])[0]
        embedding_keys = self.db.filter(regex="^embedding_").keys()

        related_rows = []
        for key in embedding_keys:
            related_rows.append(self.vector_search(key, query_embedding, n=5))
        
        # Related by keywords        
        query_keywords = OpenAPI.query_keyword_generation(query)
        keyword_matches = self.db[self.db['keywords'].apply(lambda x: any(k in query_keywords for k in x))]
        if not keyword_matches.empty:
            related_rows.append(keyword_matches)

        related_df = pandas.concat(related_rows).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
        return related_df

    def qna(self, query):
        related = self._get_relevant(query)

        example = "Related\n"
        for i, row in related.iterrows():
            example += f" # {row['title'] if 'title' in row else row['key']}\n"
            example += f"{self._load_note(row['key'], row['file_name']).body}\n"

        answer = OpenAPI.qna(query, example)
        return answer

    ##
    # Knowledge Management Related
    def _load_note(self, key, file_name):
        file_path = os.path.join(self.note_directory, file_name)
        if self.notes.get(key):
            return self.notes[key]
        else:
            note = self.T(file_path)
            self.notes[key] = note
            return note

    def _new_files(self):
        db_files = set(self.db["file_name"].tolist())
        note_files = set(os.path.basename(f) for f in glob.glob(os.path.join(self.note_directory, "*.md")))
        new = note_files - db_files
        return [os.path.join(self.note_directory, f) for f in new]

    def _process_new_files(self):
        for file_path in self._new_files():
            logger.debug(f"Processing new file: {file_path}")
            note = self.T(file_path)
            note.create_embeddings()
            note.create_keywords()

            entry = note.db_entry()
            self.append_db_entry(entry)
            self.notes[note.key] = note

    def process_updated_files(self):
        for i, row in self.db.iterrows():
            file_path = os.path.join(self.note_directory, row["file_name"])
            if FileUtils.calculate_hash(file_path) == row["hash"]:
                continue
            logger.debug(f"Processing updated file: {file_path}")
            note = self.T(file_path)
            note.create_embeddings()
            note.create_keywords()

            entry = note.db_entry()
            self.db.loc[i] = entry
            self.notes[note.key] = note


if __name__ == "__main__":
    kb = KnowledgeBase(
        KnowledgeFactory.create(Config.type())
    )
    kb.process_updated_files()
    kb.save_db()
    # result = (kb.qna("What did Guibas, John propoesd at 2021?"))
    result = (kb.qna("What are some developments in deep learning?"))
    print(result["answer"])
    for idx, ref in enumerate(result["references"]):
        print(f"- [{idx+1}] {ref}")