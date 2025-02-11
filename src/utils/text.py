
import re
from difflib import SequenceMatcher

class TextUtils:
    @staticmethod
    def clean(text):
        if text is None:
            return ""
        return ' '.join(re.sub(r"[^a-zA-Z0-9]+", ' ', text).split()).lower()

    @classmethod
    def similar(self, text1, text2, threshold=0.8):
        text1 = self.clean(text1)
        text2 = self.clean(text2)
        return SequenceMatcher(None, text1, text2).ratio() > threshold

    @classmethod
    def same(self, text1, text2):
        return self.clean(text1) == self.clean(text2)
    
    @staticmethod
    def get_first_string(value):
        if isinstance(value, list):
            return value[0]
        if isinstance(value, str):
            return value
        return ""

    @staticmethod
    def get_last_name(value):
        if value is None:
            return None
        if ',' in value:
            return value.split(',')[0].strip()
        else:
            return value.split(' ')[-1].strip()

    @classmethod
    def get_author(self, value):
        if isinstance(value,list):
            return self.get_author(value[0])
        
        if isinstance(value, dict):
            if 'family' in value:
                return value['family'] + ', ' + value.get('given', '')
            else:
                return value['name']
        
        if isinstance(value, str):
            return value
        return ""

    @staticmethod
    def format_entry(string, length):
        return string.lower().ljust(length,".")[:length].replace(" ", ".")
    
    @classmethod
    def generate_sbkey(self, title, author, year):
        author_last_name = self.get_last_name(author)
        author_last_name = self.format_entry(author_last_name, 6)

        year = str(year)
        year = year if year.isdigit() else "."
        year = self.format_entry(year, 4)

        title_words = self.clean(title).split()
        title_first_word = self.format_entry(title_words[0], 6)
        title_first_char = self.format_entry(''.join([word[0] for word in title_words]), 16)
        
        sbkey = f"{author_last_name}{year}{title_first_word}{title_first_char}"

        return sbkey

    @staticmethod
    def trim_lines(text, start, end):
        text = text.strip("\n")
        trimmed = text[start:end].strip()
        retained = text[:start] + text[end:]
        return trimmed, retained


if __name__ == "__main__":
    args = {
        "title": 
            "",
        "author": 
            "",
        "year": 0000
    }

    print(TextUtils.generate_sbkey(**args))