
from src.knowledge.knowledge import Knowledge

from src.utils.md import MarkdownUtils

from src.llm_api.open import OpenAPI

class DebugNote(Knowledge):
    ##
    # Initialize the Debug class
    def __init__(
            self,
            file_name,
            db_entry = None
            ):
        self.issue_body = ""
        super().__init__(
            file_name,
            db_entry
        )
        self.key = self.metadata.get("ID")

    def _extract_data(self):
        self.issue_body, _, _ = MarkdownUtils.extract_section(self.body, "Issue")
        self.debug_body, _, _ = MarkdownUtils.extract_section(self.body, "Debug Process")
        self.solution_body, _, _ = MarkdownUtils.extract_section(self.body, "Solution")
        
    def _generate_entry(self):
        error_detail = OpenAPI.analyze_error(self.issue_body)
        self.error_message = error_detail["error_message"]
        self.error_location = error_detail["location"]
        self.error_traceback = error_detail["traceback"]
        super()._generate_entry()
        
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
    def embedding_dict(self):
        return super().embedding_dict() | {
            "embedding_error_message": self.metadata.get("embedding_error_message"),
            "embedding_error_traceback": self.metadata.get("embedding_error_traceback"),
        }

    def db_entry(self):
        result =  super().db_entry()

        result["status"] = self.metadata.get("status")
        result["version"] = self.metadata.get("version")
        # Error message
        result["error_message"] = self.error_message
        result["error_location"] = self.error_location

        return result

    def md_metadata(self):
        result =  super().md_metadata()

        result["status"] = self.metadata.get("status")
        result["version"] = self.metadata.get("version")
        result["tags"] = result["tags"] + [result["status"], result["version"]]

        return result