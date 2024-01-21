"""
main.py
"""
from fastapi import FastAPI

app = FastAPI()

# Endpoint to serve the JSON data
@app.get("/")
async def hello_world():
    """
    Returns hello world
    """
    return "hello there"
