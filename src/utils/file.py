
class FileUtils:
    @staticmethod
    def read_lines(file_path: str) -> list[str]:
        with open(file_path, 'r') as f:
            return f.readlines()
        
    @staticmethod
    def write(file_path: str, content: str):
        with open(file_path, 'w') as f:
            f.write(content)