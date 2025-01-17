
import re

class TextUtils:
    @staticmethod
    def clean(text):
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
        if None:
            return ""
        if ',' in value:
            return value.split(',')[0].strip()
        else:
            return value.split(' ')[-1].strip()