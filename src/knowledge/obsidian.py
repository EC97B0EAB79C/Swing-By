import logging
import re

from src.knowledge.article import Article

from src.utils.md import MarkdownUtils
from src.utils.text import TextUtils
from src.utils.md import MarkdownUtils

logger = logging.getLogger(__name__)

class ObsidianNote(Article):
    ##
    # Initialize the ObsidianNote class
    def __init__(
            self,
            file_name,
            db_entry = None
            ):
        super().__init__(
            file_name,
            db_entry
        )

    ##
    # Create embeddings
    def create_embeddings(self):
        logger.warning("ObsidianNote does not support embeddings")
        pass

    def embedding_dict(self):
        logger.warning("ObsidianNote does not support embeddings")
        return {}

    ##
    # MD
    def update_file(self, known_list=[]):
        metadata = self.md_metadata()
        self._modify_section(known_list)

        md_text = MarkdownUtils.create_md_text(metadata, self.body)

    def _modify_section(self, known_list=[]):
        body = self.body.strip("\n")
        sections = {
            "References": "",
            "Bibtex": ""
        }

        sections["Bibtex"], s, e = MarkdownUtils.extract_section(body, "Bibtex")
        body = body[:s] + body[e:]

        references_section, s, e = MarkdownUtils.extract_section(body, "References")
        body = body[:s] + body[e:]
        references = self._merge_references(references_section, self.metadata.get("ref", []))
        sections["References"] = self._create_reference_section(references, known_list)

        others_section, s, e = MarkdownUtils.extract_section(body, "Others")
        body = body[:s] + body[e:]

        body += MarkdownUtils.create_others_section(others_section, sections)

        self.body = body

    def _merge_references(self, reference_body, new_references):
        reference_list = re.findall(r"\[\[.*?\]\]", reference_body)
        references = self._create_wikilink_dict(new_references) | self._create_wikilink_dict(reference_list)
        references = dict(sorted(references.items()))

        return references

    def _create_wikilink_dict(self, wikilinks):
        result = {}
        for wikilink in wikilinks:
            key = wikilink.split("|")[0].split("/")[-1]
            result[key] = wikilink
        
        return result
    
    def _create_reference_section(self, references, know_list=[]):
        reference_section = ""
        undiscovered_section = "#### Undiscovered\n"

        for key, value in references:
            if key in know_list:
                reference_section += f"- [[{value}]]\n"
            else:
                undiscovered_section += f"- [[{value}]]\n"

        return reference_section.rstrip() + "\n\n" + undiscovered_section.rstrip()
