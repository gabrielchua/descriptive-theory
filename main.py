from fastapi import FastAPI
from pydantic import BaseModel

import uvicorn

import json
from typing import Any

app = FastAPI()

# Assuming 'nobelprize-laureate.json' is in the same directory as this script
json_file_path = 'nobelprize-laureate.json'

# Endpoint to serve the JSON data
@app.get("/")
async def read_laureates():
    return "hello world"