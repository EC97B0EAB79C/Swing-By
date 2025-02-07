# knowledge_factory.py
from src.knowledge.knowledge import Knowledge
from src.knowledge.article import Article
from src.knowledge.debug_note import DebugNote

class KnowledgeFactory:
    @classmethod
    def create(cls, type_name):
        types = {
            "default": Knowledge,
            "article": Article,
            "debug": DebugNote
        }
        if type_name not in types:
            raise ValueError(f"Unknown knowledge type: {type_name}")
        return types[type_name]
