import logging
import re

from src.knowledge.article import Article

from src.utils.md import MarkdownUtils
from src.utils.file import FileUtils
from src.utils.text import TextUtils

logger = logging.getLogger(__name__)

class ObsidianNote(Article):
    ##
    # Initialize the ObsidianNote class
    def __init__(
            self,
            *args,
            local_files = []
            ):
        super().__init__(
            *args
        )
        self.update_file(local_files)

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
        FileUtils.write(self.file_name, md_text)
        self.hash = FileUtils.calculate_hash(self.file_name)

    def _modify_section(self, known_list=[]):
        body = self.body
        sections = {
            "References": "",
            "Bibtex": ""
        }

        sections["Bibtex"], s, e = MarkdownUtils.extract_section(body, "Bibtex")
        _, body = TextUtils.trim_lines(body, s, e)

        references_section, s, e = MarkdownUtils.extract_section(body, "References")
        _, body = TextUtils.trim_lines(body, s, e)
        references = self._merge_references(references_section, self.metadata.get("ref", []))
        sections["References"] = self._create_reference_section(references, known_list)

        others_section, s, e = MarkdownUtils.extract_section(body, "Others")
        _, body = TextUtils.trim_lines(body, s, e)

        body = body.strip() + "\n\n"
        body += MarkdownUtils.create_others_section(others_section or "", sections)

        self.body = body

    def _merge_references(self, reference_body, new_references):
        references = self._create_wikilink_dict(new_references)
        if reference_body:
            reference_list = re.findall(r"\[\[(.*?)\]\]", reference_body)
            references = references | self._create_wikilink_dict(reference_list)
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
        
        for key, value in references.items():
            if key in know_list:
                reference_section += f"- [[{value}]]\n"
            else:
                undiscovered_section += f"- [[{value}]]\n"

        return reference_section.rstrip() + "\n\n" + undiscovered_section.rstrip()
