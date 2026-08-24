import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


TUTOR_INSTRUCTIONS = """
You are an expert programming tutor.

Your goal is to help students understand programming concepts clearly.

Follow these rules:

1. Explain concepts simply and clearly.
2. Assume the student is a beginner unless they indicate otherwise.
3. Keep normal answers concise: around 200-400 words.
4. For simple follow-up questions, answer directly instead of repeating the previous explanation.
5. Use examples only when they improve understanding.
6. For algorithms, mention time and space complexity briefly.
7. For debugging, explain the problem and show corrected code when useful.
8. For coding problems, explain the approach before the solution.
9. Use Markdown for headings, lists, and code blocks.
10. Do not repeat information that has already been explained in the conversation.
"""


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


@app.get("/")
def home():
    return {
        "message": "AI Tutor API is running!"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    conversation = []

    for message in request.history:
        conversation.append(
            {
                "role": message.role,
                "parts": [{"text": message.content}]
            }
        )

    conversation.append(
        {
            "role": "user",
            "parts": [{"text": request.message}]
        }
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=conversation,
        config=types.GenerateContentConfig(
            system_instruction=TUTOR_INSTRUCTIONS
        )
    )

    return {
        "message": request.message,
        "answer": response.text
    }