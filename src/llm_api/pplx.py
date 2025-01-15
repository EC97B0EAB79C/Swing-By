# Standard library imports
import os
import logging
import json
import requests

# Global variables
TOKEN = os.environ["PPLX_API_KEY"]
API_ENDPOINT = "https://api.perplexity.ai/chat/completions"
logger = logging.getLogger(__name__)

# Perplexity models
COMPLETION_MODEL = "llama-3.1-sonar-small-128k-online"

class PerplexityAPI:
    headers = {
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/json"
    }

    @classmethod
    def completion(self, messages: list[dict]):
        logger.debug("> Sending Perplexity completion API request")
        INSTRUCTIONS = f"""
Be precise and concise.
"""
        system_message = [{  
            "role": "system",
            "content": INSTRUCTIONS
        }]
        payload = {
            "model": COMPLETION_MODEL,
            "messages": system_message + messages,
            "return_images": False,
            "stream": False,
        }

        try:
            response = requests.request("POST", API_ENDPOINT, json=payload, headers=self.headers)
            response.raise_for_status()

            logger.debug("> Recieved Perplexity completion API responce")
            data = response.json()
            logger.debug(f"> {data['usage']}")

            return data
        
        except Exception as e:
            logger.error(f"Failed to complete request: {e}")
            return None


if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "What is a banana?"
        }
    ]

    data = PerplexityAPI.completion(messages)
    if data:
        print(data["choices"][0]["message"]["content"])
        for idx, citation in enumerate(data["citations"]):
            print(f"- [{idx+1}]. {citation}")

        print(data["usage"])