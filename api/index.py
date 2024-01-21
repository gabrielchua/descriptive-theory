"""
main.py
"""
import os
from typing import Optional

from flask import Flask
from openai import OpenAI
from pydantic import BaseModel, Field

DEFAULT_SYSTEM_MESSAGE = "You are a friendly doctor. "\
            "Please simplify the given medical report in plain English. "\
            "Explain the findings, and if they are not serious, "\
            "assure the patient. "\
            "Be succicnt, and do not use technical terms someone without a "\
            "medical or life science degree would not understand. "\
            "Never add emojis or code snippets. "

# Initialise fastapi and openai client
app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Model for the simplify-text endpoint
class SimplifyTextRequest(BaseModel):
    """
    Pydantic model for the request payload of the /simplify-text endpoint.
    It expects two fields:
    - text: A string representing the text to be simplified.
    - language: A string that must be either 'english' or 'chinese'.
    """
    text: str
    language: str = Field(pattern=r'^(english|chinese)$', default="english")

# GET endpoint to serve as a GET ping
@app.route("/")
def ping():
    """
    Endpoint to check if the server is running.
    GET request to this endpoint will return a JSON response with a message
    indicating the server is operational.

    Returns:
        JSON response with a server status message.
    """
    return {"code": 200,
            "message": "Server is up and running"
            }

# POST endpoint to simplify text
@app.route("/simplify-text")
def simplify_text(request: SimplifyTextRequest):
    """
    Endpoint to simplify the given text based on the specified language.
    It accepts a JSON payload conforming to the SimplifyTextRequest model.

    Args:
        request (SimplifyTextRequest): The request payload containing 'text' and 'language'.

    Returns:
        JSON response with the simplified text.
    """
    simplified_report = simplify(original_message=request.text,
                               language=request.language)  
    if simplified_report:
        simplified_text = "Hello - here is the report from today's visit: " + simplified_report
        return {"code": 200,
                "message": {"simplified_text": simplified_text}
                }
    return {"code": 500,
            "message": "Unexpected error."}

def simplify(original_message:str, language:str) -> Optional[str]:
    """
    Simplifies text
    """
    system_prompt = _generate_system_prompt(language)

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_message}
        ],
        temperature=0,
        seed=0
    )

    return response.choices[0].message.content

def _generate_system_prompt(language:str) -> str:
    """
    Generates system prompt
    """
    return DEFAULT_SYSTEM_MESSAGE + f"Please reply in {language}. "
