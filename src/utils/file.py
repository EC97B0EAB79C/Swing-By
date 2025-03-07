
import hashlib

class FileUtils:
    @staticmethod
    def read_lines(file_path: str) -> list[str]:
        with open(file_path, 'r') as f:
            return f.readlines()
        
    @staticmethod
    def write(file_path: str, content: str):
        with open(file_path, 'w') as f:
            f.write(content)

    @staticmethod
    def calculate_hash(file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.blake2b(f.read()).hexdigest()