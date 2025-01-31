# Standard library imports
import os
import logging
import json
# Third-party imports
import numpy as np
# OpenAI related
from openai import OpenAI

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
        """
        Extract keywords from text using

        Args:
            text (str): Text to extract keywords from
            n (int, optional): Number of keywords to extract. Defaults to 10.
            ratio (float, optional): Ratio of general keywords to specific keywords. Defaults to 0.4.

        Returns:
            list[str]: List of keywords extracted
        """

        logger.debug("> Creating keywords with OpenAI")
        GPT_INSTRUCTIONS = f"""
This GPT helps users generate a set of relevant keywords or tags based on the content of any note or text they provide.
It offers concise, descriptive, and relevant tags that help organize and retrieve similar notes or resources later.
The GPT will aim to provide up to {n} keywords, with 1 keyword acting as a category, {n*ratio} general tags applicable to a broad context, and {n - 1 - n*ratio} being more specific to the content of the note.
It avoids suggesting overly generic or redundant keywords unless necessary.
It will list the tags using underscores instead of spaces, ordered from the most general to the most specific.
Every tag will be lowercase.
Return the list in json format with key "keywords" for keyword list.
"""
        messages = [
            {"role":"system", "content": GPT_INSTRUCTIONS},
            {"role": "user", "content": text},
        ]
        json_data = self.request_for_json(KEYWORD_MODEL, messages)
        keywords = json_data["keywords"]

        logger.debug("> Created keywords")
        return keywords
    
    @classmethod
    def article_data_extraction(self, reference_list: list[str]) -> list[dict]:
        logger.debug("> Extracting article data with OpenAI")
        GPT_INSTRUCTIONS = """
This GPT specializes in parsing unstructured strings of academic references and extracting key components such as the first author's name (formatted as "last_name, first_name"), the title of the work, and the publication year.
It presents this information in a structured JSON format.
The JSON data must include the following fields: "title", "first_author", and "year".
Return entries in list with key "references".
Responses are concise, focused on accurately extracting and formatting the data, and handle common variations in citation styles.
"""
        messages = [
            {"role":"system", "content": GPT_INSTRUCTIONS},
            {"role": "user", "content": "\n".join(reference_list)},
        ]
        json_data = self.request_for_json(REFERECNCE_MODEL, messages)
        structured_references = json_data["references"]

        logger.debug("> Extracted article data")
        return structured_references

    @classmethod
    def summarize(self, text: str) -> str:
        logger.debug("> Summarizing text with OpenAI")
        GPT_INSTRUCTIONS = """
This GPT is designed to create a single sentence summary of the text user provides.
The summary must capture the core information and key concepts that would help match this text with related questions or documents.
Focus on preserving the main topic, key entities, and central arguments while including specific terminology from the original text.
Avoid including minor details, examples, or supporting evidence.
The summary should be concise yet informative enough to determine the text's relevance to other materials.
"""
        messages = [
            {"role":"system", "content": GPT_INSTRUCTIONS},
            {"role": "user", "content": text},
        ]
        summary = self.request_for_text(SUMMARIZE_MODEL, messages)

        logger.debug("> Summarized text")
        return summary
    
    @classmethod
    def analyze_error(self, error: str) -> dict:
        logger.debug("> Finding root cause of error with OpenAI")
        GPT_INSTRUCTIONS = """
This GPT is designed to Analyze the provided error logs, identify and extract the most relevant error that best explains the root cause of the failure.
Return only this error, its location and its complete traceback in the following JSON format: 
{"error_message": string, "location": string, "traceback": string}.
"""
        messages = [
            {"role":"system", "content": GPT_INSTRUCTIONS},
            {"role": "user", "content": error},
        ]
        json_data = self.request_for_json(ERROR_ANALYSIS_MODEL, messages)

        logger.debug("> Found root cause of error")
        return json_data
