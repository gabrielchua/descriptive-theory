"""
ping.py
"""
from sanic import Sanic
from sanic.response import json

# Initialise fastapi and openai client
app = Sanic("simply")

# GET endpoint to serve as a GET ping
@app.get("/ping")
async def ping(request):
    """
    Endpoint to check if the server is running.
    GET request to this endpoint will return a JSON response with a message
    indicating the server is operational.

    Returns:
        JSON response with a server status message.
    """
    return json({"code": 200,
            "message": "Server is up and running"
            })
