
import re

class TextUtils:
    @staticmethod
    def clean(text):
        return re.sub(r"[^a-zA-Z0-9]+", ' ', text).lower().strip()

    @classmethod
    def same(self, text1, text2):
        return self.clean(text1) == self.clean(text2)
    
