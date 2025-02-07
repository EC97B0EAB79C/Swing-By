
import os
import yaml

class Config:
    _instance = None
    _config = None
    _config_path = os.path.expanduser("~/.swing-by/config.yaml")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_config(cls):
        if cls._config is None:
            if not os.path.isfile(cls._config_path):
                raise FileNotFoundError(f"Config file not found: {cls._config_path}")
            
            with open(cls._config_path, 'r') as file:
                cls._config = yaml.safe_load(file) or {}
        
        return cls._config
    
    @classmethod
    def knowledgebase(cls):
        return os.path.expanduser(cls.load_config().get("knowledgebase"))
    
    @classmethod
    def llm_provider(cls):
        return cls.load_config().get("llm_provider")
    
    @classmethod
    def type(cls):
        return cls.load_config().get("type")
            
    @classmethod
    def llm_model(cls, model_name):
        return cls.load_config().get("llm_models").get(model_name)