
import re

class TextUtils:
    @staticmethod
    def clean(text):
        if text is None:
            return ""
        return ' '.join(re.sub(r"[^a-zA-Z0-9]+", ' ', text).split()).lower()

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
                return value['family'] + ', ' + value['given']
            else:
                return value['name']
        
        if isinstance(value, str):
            return value
        return ""