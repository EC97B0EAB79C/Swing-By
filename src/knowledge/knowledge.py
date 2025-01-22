import os
from datetime import datetime

from src.utils.file import FileUtils
from src.utils.md import MarkdownUtils

class Knowledge:
    def __init__(self, 
                 file_name,
                 
                 ):
        self.file_name = file_name
        self._load_file()
        
    def _load_file(self):
        note_lines = FileUtils.read_lines(self.file_name)
        self.metadata, self.body = MarkdownUtils.extract_yaml(note_lines)

    def db_entry(self, embeddings):
        result = {}
        result["key"] = self.metadata.get("key")
        result["keywords"] = self.metadata.get("keywords")
        result["file_name"] = os.path.basename(self.file_name)
        for k, v in embeddings.items():
            result[k] = v
        
        return result

    def md_metadata(self):
        result = {}
        result["key"] = self.metadata.get("key")
        result["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["created"] = self.metadata.get("created") or result["updated"]
        result["tags"] = self.metadata.get("keywords")

        return result