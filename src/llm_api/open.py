# Standard library imports
import os
import logging
import json
# Third-party imports
import numpy as np
# OpenAI related
from openai import OpenAI

from src.llm_api.prompts import *

# Global variables
TOKEN = os.environ["GITHUB_TOKEN"]
API_ENDPOINT = "https://models.inference.ai.azure.com"
logger = logging.getLogger(__name__)

# OpenAI models
EMBEDDING_MODEL = "text-embedding-3-small"
KEYWORD_MODEL = "gpt-4o-mini"
REFERECNCE_MODEL = "gpt-4o-mini"
SUMMARIZE_MODEL = "gpt-4o-mini"
ERROR_ANALYSIS_MODEL = "gpt-4o-mini"
QNA_MODEL = "gpt-4o-mini"

class OpenAPI:
    client = OpenAI(base_url=API_ENDPOINT, api_key=TOKEN)

    @classmethod
    def request_for_json(self, model, messages):
        logger.debug("> Sending OpenAI completion API request")
        completion = self.client.beta.chat.completions.parse(
            model = model,
            messages = messages,
            response_format = { "type": "json_object" }
        )

        logger.debug("> Recieved OpenAI completion API responce")
        logger.debug(f"> {completion.usage}")
        chat_response = completion.choices[0].message
        json_data = json.loads(chat_response.content)

        return json_data
    
    @classmethod
    def request_for_text(self, model, messages):
        logger.debug("> Sending OpenAI completion API request")
        completion = self.client.beta.chat.completions.parse(
            model = model,
            messages = messages,
        )

        logger.debug("> Recieved OpenAI completion API responce")
        logger.debug(f"> {completion.usage}")
        chat_response = completion.choices[0].message
        text_data = chat_response.content

        return text_data

    @classmethod
    def qna(self, query: str, example:str ) -> dict:
        logger.debug("> Finding answer with OpenAI")
        messages = [
            {"role":"system", "content": QNA_PROMPT},
            {"role": "user", "content": example},
            {"role": "user", "content": query},
        ]
        answer = self.request_for_json(QNA_MODEL, messages)

        logger.debug("> Found answer")
        return answer



    @classmethod
    def embedding(self, text: list[str]) -> list[np.array]:
        logger.debug("> Embedding texts with OpenAI")
        logger.debug("> Sending OpenAI embedding API request")
        embedding_response = self.client.embeddings.create(
            input = text,
            model = EMBEDDING_MODEL,
        )

        logger.debug("> Recieved OpenAI embedding API responce")
        logger.debug(f"> {embedding_response.usage}")
        embeddings = []
        for data in embedding_response.data:
            embeddings.append(np.array(data.embedding))
        
        logger.debug("> Created embedding vector")
        return embeddings

    @classmethod
    def keyword_extraction(self, text, n=10, ratio=0.4) -> list[str]:
        logger.debug("> Creating keywords with OpenAI")
        messages = [
            {"role":"system", "content": DOCUMENT_KEYWORD_GENERATION_PROMPT.format(n, n*ratio, n*(1-ratio))},
            {"role": "user", "content": text},
        ]
        json_data = self.request_for_json(KEYWORD_MODEL, messages)
        keywords = json_data["keywords"]

        logger.debug("> Created keywords")
        return keywords
    
    @classmethod
    def article_data_extraction(self, reference_list: list[str]) -> list[dict]:
        logger.debug("> Extracting article data with OpenAI")
        messages = [
            {"role":"system", "content": REFERENCE_PARSE_PROMPT},
            {"role": "user", "content": "\n".join(reference_list)},
        ]
        json_data = self.request_for_json(REFERECNCE_MODEL, messages)
        structured_references = json_data["references"]

        logger.debug("> Extracted article data")
        return structured_references

    @classmethod
    def summarize(self, text: str) -> str:
        logger.debug("> Summarizing text with OpenAI")
        messages = [
            {"role":"system", "content": SUMMARIZE_PROMPT},
            {"role": "user", "content": text},
        ]
        summary = self.request_for_text(SUMMARIZE_MODEL, messages)

        logger.debug("> Summarized text")
        return summary
    
    @classmethod
    def analyze_error(self, error: str) -> dict:
        logger.debug("> Finding root cause of error with OpenAI")
        messages = [
            {"role":"system", "content": ERROR_ANALYSIS_PROMPT},
            {"role": "user", "content": error},
        ]
        json_data = self.request_for_json(ERROR_ANALYSIS_MODEL, messages)

        logger.debug("> Found root cause of error")
        return json_data
