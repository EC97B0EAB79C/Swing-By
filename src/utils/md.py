
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
    def extract_code_blocks(body: str):
        pattern = r'```(.*?)```'
        matches = re.findall(pattern, body, re.DOTALL | re.IGNORECASE)
        return matches

    @staticmethod
    def extract_section(body: str, section_name: str):
        body = body.split('\n')
        in_section = False
        section_level = 0
        section_start = 0
        section_end = len(body)
        
        for i, line in enumerate(body):
            if line.strip() == "":
                continue
            if f"# {section_name}".lower() in line.strip().lower():
                in_section = True
                section_level = line.split()[0].count('#')
                section_start = i
                continue
            if in_section and line.strip().split()[0].count('#') == section_level:
                section_end = i
                break

        if not in_section:
            return None, None, None

        section_text = '\n'.join(body[section_start+1:section_end])

        return section_text, section_start, section_end

    @staticmethod
    def create_md_text(metadata: dict, body: str):
        md_text = ""
        if metadata:
            md_text += "---\n"
            md_text += yaml.dump(metadata, default_flow_style=False)
            md_text += "---\n\n"
        md_text += body

        return md_text
    
    @staticmethod
    def create_others_section(others:str, contents:dict = None):
        text = "## Others\n"
        text += others.strip()
        for key, value in contents.items():
            text += f"\n\n### {key}\n"
            text += value

        return text