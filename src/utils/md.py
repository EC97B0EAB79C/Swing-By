
import yaml
import re
import bibtexparser

class MarkdownUtils:
    @staticmethod   
    def extract_yaml(markdown: list[str]):
        while markdown[0].strip() =='':
            markdown = markdown[1:]
        if '---' not in markdown[0].strip():
            return {}, ''.join(markdown)

        markdown = markdown[1:]
        for idx, line in enumerate(markdown):
            if '---' in line.strip():
                yaml_end = idx
                break

        yaml_text = ''.join(markdown[:yaml_end])
        metadata = yaml.safe_load(yaml_text)
        if metadata.get("author"):
            author = metadata["author"]
            metadata["author"] = author if isinstance(author, list) else [author]

        return metadata, ''.join(markdown[yaml_end+1:])
    
    @staticmethod
    def extract_bibtex(body: str):
        pattern = r'```BibTeX(.*?)```'
        match = re.findall(pattern, body, re.DOTALL | re.IGNORECASE)

        try:
            entry = bibtexparser.parse_string(match[0]).entries[0]
            fields_dict = entry.fields_dict
            bibtex = {
                'bibtex_key': entry.key,
                'title': fields_dict['title'].value,
                'author': fields_dict['author'].value.split(' and '),
                'year' : int(fields_dict['year'].value)
            }

            return bibtex
        except:
            return {}
        
    @staticmethod
    def create_md_text(metadata: dict, body: str):
        md_text = ""
        if metadata:
            md_text += "---\n"
            md_text += yaml.dump(metadata, default_flow_style=False)
            md_text += "---\n\n"
        md_text += body

        return md_text