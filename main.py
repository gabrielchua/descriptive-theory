"""
main.py
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from llm import simplify

app = FastAPI()

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
async def ping():
    """
    Endpoint to check if the server is running.
    GET request to this endpoint will return a JSON response with a message
    indicating the server is operational.

    Returns:
        JSON response with a server status message.
    """
    return {"message": "Server is up and running"}

# POST endpoint to simplify text
@app.post("/simplify-text")
async def simplify_text(request: SimplifyTextRequest):
    """
    Endpoint to simplify the given text based on the specified language.
    It accepts a JSON payload conforming to the SimplifyTextRequest model.

    Args:
        request (SimplifyTextRequest): The request payload containing 'text' and 'language'.

    Returns:
        JSON response with the simplified text.
    """
    simplified_text = simplify(original_message=request.text,
                               language=request.language)
    return {"simplified-text": simplified_text}
