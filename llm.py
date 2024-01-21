"""
llm.py
"""
import os
from typing import Optional
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

DEFAULT_SYSTEM_MESSAGE = "You are a friendly doctor. "\
            "Your task is to simplify the given medical report for the patient by "\
            "writing it in plain English. "\
            "Explain the significance of the findings, and if they are not serious or common, "\
            "assure the patient. "\
            "Be succicnt, and do not use technical terms that someone without a "\
            "medical or life science degree would not understand. "\
            "Never add emojis or code snippets. "

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
