# app/utils/llm_api.py
import requests
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def llm_response(api_key, model_name, query):
    """Generates response using Google Gemini API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": query}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.ok:
            response_json = response.json()
            if 'candidates' in response_json and response_json['candidates']:
                return response_json['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception("No candidates found in the response.")
        else:
            raise Exception(f"Error: {response.status_code}\n{response.text}")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")