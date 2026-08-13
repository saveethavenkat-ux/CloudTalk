import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Find the CloudTalk project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is not configured. "
        "Check your CloudTalk/.env file."
    )

client = Groq(api_key=api_key)


def get_ai_response(messages):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are CloudTalk, a helpful and friendly AI assistant. "
                    "Give clear, accurate and concise answers."
                ),
            },
            *messages,
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content