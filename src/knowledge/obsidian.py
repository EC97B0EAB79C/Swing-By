
from src.knowledge.knowledge import Knowledge

class ObsidianNote(Knowledge):
    def __init__(
            self,
            file_name,
            db_entry = None
            ):
        super().__init__(
            file_name,
            db_entry
        )