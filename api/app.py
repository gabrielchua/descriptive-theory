"""
main.py
"""
import os
from typing import Optional

from openai import OpenAI
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

GPT3 = "gpt-3.5-turbo-1106"
GPT4 = "gpt-4-1106-preview"

SIMPLIFY_SYSTEM_MESSAGE = "You are a friendly doctor. "\
            "Please simplify the given medical report in plain English. "\
            "Explain the findings, and if they are not serious, "\
            "assure the patient. "\
            "Be succicnt, and do not use technical terms someone without a "\
            "medical or life science degree would not understand. "\
            "Never add emojis or code snippets. "

GUARDRAIL_SYSTEM_MESSAGE = "Your goal is to classify if the given text is about medical matters. If yes, return 1. If no, return 0"

# Defining error in case of 503 from OpenAI
ERROR_503 = "OpenAI server is busy, try again later"

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
        return "Please only use this API to simplify medical text."
    original_text = request.text
    chosen_language = request.language
    return StreamingResponse(simplify_text(original_text, chosen_language), media_type="text/event-stream") 

def scan_input(prompt_to_check):
    """
    Scans input. Returns 0 if not medical related, and 1 otherwise.
    """
    response = client.chat.completions.create(
        model=GPT3,
        messages=[{"role": "system", "content": GUARDRAIL_SYSTEM_MESSAGE},
                  {"role": "user", "content": prompt_to_check}],
        temperature=0,
        seed=1,
        max_tokens=1,
        logit_bias={"15": 100,
                    "16": 100}
    )

    result = int(response.choices[0].message.content)

    return result
    
def simplify_text(original_message:str, language:str) -> Optional[str]:
    """
    Simplifies text
    """
    system_message = _generate_system_prompt(language)

    try:
        completion = client.chat.completions.create(
            model=GPT4,
            messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": original_message}],
            temperature=0,
            seed=1,
            stream=True
        )
    except Exception as e:
        print("Error in creating campaigns from openAI:", str(e))
        raise HTTPException(503, ERROR_503) from e
    try:
        for chunk in completion:
            current_content = chunk.choices[0].delta.content or ""
            yield current_content
    except Exception as e:
        print("OpenAI Response (Streaming) Error: " + str(e))
        raise HTTPException(503, ERROR_503) from e

def _generate_system_prompt(language:str) -> str:
    """
    Generates system prompt
    """
    return SIMPLIFY_SYSTEM_MESSAGE + f"Please reply in {language}. "
