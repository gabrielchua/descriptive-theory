"""
main.py
"""
import os
from typing import Optional

from sanic import Sanic
from sanic.response import json
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
app = Sanic("simply")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# # Model for the simplify-text endpoint
# class SimplifyTextRequest(BaseModel):
#     """
#     Pydantic model for the request payload of the /simplify-text endpoint.
#     It expects two fields:
#     - text: A string representing the text to be simplified.
#     - language: A string that must be either 'english' or 'chinese'.
#     """
#     text: str
#     language: str = Field(pattern=r'^(english|chinese)$', default="english")

# POST endpoint to simplify text
@app.post("/simplify")
def simplify(request):
    """
    Endpoint to simplify the given text based on the specified language.
    It accepts a JSON payload conforming to the SimplifyTextRequest model.

    Args:
        request (SimplifyTextRequest): The request payload containing 'text' and 'language'.

    Returns:
        JSON response with the simplified text.
    """
    payload = request.json
    simplified_report = _simplify_text(original_message=payload["text"],
                                       language=payload["language"])
    if simplified_report:
        simplified_text = "Hello - here is the report from today's visit: " + simplified_report
        return json({"code": 200,
                "message": {"simplified_text": simplified_text}
                })
    return json({"code": 500,
            "message": "Unexpected error."})

def _simplify_text(original_message:str, language:str) -> Optional[str]:
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
