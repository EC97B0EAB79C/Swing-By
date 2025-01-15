
import re

class TextUtils:
    @staticmethod
    def clean(self, text):
        return re.sub(r"[^a-zA-Z0-9]+", ' ', text).lower()

    @staticmethod
    def same(self, text1, text2):
        return self.clean_text(text1) == self.clean_text(text2)
    
