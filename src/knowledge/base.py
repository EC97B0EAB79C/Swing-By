
import os
import glob
import logging

import pandas
import numpy as np

from src.knowledge.knowledge import Knowledge

from src.llm_api.open import OpenAI

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, db_path, note_directory):
        self.db_path = db_path
        self.note_directory = note_directory
        # self._load_file_list()
        self._load_db()


    def _load_db(self):
        try:
            self.db = pandas.read_hdf(self.db_path, key="knowledge")
            logger.debug(f"Loaded {len(self.db.index)} entries from DB")
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
            logger.info("Creating new DB")
            self.db = pandas.DataFrame(columns=[
                "key", 
                "title", 
                "keywords", 
                "file_name", "file_hash"])

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

    def qna(self, query):
        query_embedding = OpenAI.create_embedding([query])[0]
        related = self.vector_search("embedding_body", query_embedding)
        example = "## Related\n"
        for i, row in related.iterrows():
            example += f" ### {row['title']}\n"
            example += f"{self._load_note(row['key']).body}\n"

        answer = OpenAI.answer(query, example)
        print(answer)

            
    def _load_note(self, key):
        #TODO: file location
        if self.notes.get(key):
            return self.notes[key]
        else:
            note = Knowledge(key)
            self.notes[key] = note
            return note

    #TODO Integrate with current KnowledgeBase
    # def append_article_db(self, sbkey, title, author, year):
    #     logger.debug("Appending article to DB")
    #     new_df = pandas.DataFrame.from_dict([{
    #         "key": sbkey,
    #         "title": title,
    #         "author": author,
    #         "year": year
    #     }])
    #     if type(self.article_db) != pandas.DataFrame:
    #         self.article_db = new_df
    #         return
    #     self.article_db = pandas.concat([self.article_db, new_df]).drop_duplicates(subset='key', keep='last').reset_index(drop=True)
    #     logger.debug(f"Appended article to DB")