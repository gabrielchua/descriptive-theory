"""
main.py
"""
import os
from typing import Optional

from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel, Field

SIMPLIFY_SYSTEM_MESSAGE = "You are a friendly doctor. "\
            "Please simplify the given medical report in plain English. "\
            "Explain the findings, and if they are not serious, "\
            "assure the patient. "\
            "Be succicnt, and do not use technical terms someone without a "\
            "medical or life science degree would not understand. "\
            "Never add emojis or code snippets. "

GUARDRAIL_SYSTEM_MESSAGE = "Your goal is to classify if the given text is about medical matters. If yes, return 1. If no, return 0"


# Initialise clients
app = FastAPI()
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

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
@app.get("/")
@app.get("/ping")
async def ping():
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
@app.post("/simplify")
async def simplify(request: SimplifyTextRequest):
    """
    Endpoint to simplify the given text based on the specified language.
    It accepts a JSON payload conforming to the SimplifyTextRequest model.

    Args:
        request (SimplifyTextRequest): The request payload containing 'text' and 'language'.

    Returns:
        JSON response with the simplified text.
    """
    if not scan_input(request.text):
        return {"code": 490,
            "message": "Please only use this API to simplify medical text."
            }
    simplified_report = simplify_text(original_message=request.text,
                               language=request.language)
    if simplified_report:
        simplified_text = simplified_report
        return {"code": 200,
                "message": {"simplified_text": simplified_text}
                }
    return {"code": 500,
            "message": "Unexpected error."
            }
  
def scan_input(prompt_to_check):
    """
    Scans input. Returns 0 if not medical related, and 1 otherwise.
    """
    result = int(_binary_classifier(GUARDRAIL_SYSTEM_MESSAGE, prompt_to_check))
    return result
    
def simplify_text(original_message:str, language:str) -> Optional[str]:
    """
    Simplifies text
    """
    system_message = _generate_system_prompt(language)

    response = _chat_completion(model="gpt-4-1106-preview",
                                system_message=system_message, 
                                prompt=original_message)
    
    return response

def _generate_system_prompt(language:str) -> str:
    """
    Generates system prompt
    """
    return SIMPLIFY_SYSTEM_MESSAGE + f"Please reply in {language}. "

def _chat_completion(model:str, system_message:str, prompt:str, max_tokens=None, logit_bias=None):
    """
    Helper function for chat completion
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "seed": 0
    }
    
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    
    if logit_bias is not None:
        payload["logit_bias"] = logit_bias

    print(payload)
    completion = client.chat.completions.create(**payload)
    print(completion)
    return completion.choices[0].message.content

def _binary_classifier(system_message, prompt):
    """
    Helper function to do binary classification
    """
    return _chat_completion("gpt-3.5-turbo-1106", system_message, prompt, max_tokens=1, logit_bias={"15": 100, "16": 100})
