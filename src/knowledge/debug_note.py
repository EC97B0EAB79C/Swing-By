
from src.knowledge.knowledge import Knowledge

from src.utils.md import MarkdownUtils

from src.llm_api.open import OpenAI

class DebugNote(Knowledge):
    ##
    # Initialize the Debug class
    def __init__(self,
                 file_name,
                 ):
        super().__init__(
            file_name,
        )
        self._extract_data()
        #TODO
        self.metadata["key"] = "TODO"

    def _extract_data(self):
        self.issue_body, _, _ = MarkdownUtils.extract_section(self.body, "Issue")
        self.debug_body, _, _ = MarkdownUtils.extract_section(self.body, "Debug Process")
        self.solution_body, _, _ = MarkdownUtils.extract_section(self.body, "Solution")
        
        summary = OpenAI.summarize(self.issue_body)
        self.error_message = summary["error_message"]
        self.error_location = summary["location"]
        self.error_traceback = summary["traceback"]
    
    ##
    # Create keywords
    def create_keywords(self, example=None):
        payload = ""

        payload += "\n## Core Error: \n"
        payload += f"error_message: {self.error_message}\n"
        payload += f"error_location: {self.error_location}\n"
        payload += f"error_traceback: \n```\n{self.error_traceback}\n```\n"

        payload += "\n## Debug Process: \n"
        payload += f"{self.debug_body}\n"

        payload += "\n## Solution: \n"
        payload += f"{self.solution_body}\n"

        super().create_keywords(example, payload)

    ##
    # Create embeddings
    def create_embeddings(self):
        text = [
            self.error_message,
            self.error_traceback,
        ]
        result = super().create_embeddings(text)
        self.metadata["embedding_error_message"] = result[0]
        self.metadata["embedding_error_traceback"] = result[1]

    ##
    # Create entries and metadata
    def db_entry(self, embeddings):
        result =  super().db_entry(embeddings)
        # Error message
        result["error_message"] = self.error_message
        result["error_location"] = self.error_location

        return result
