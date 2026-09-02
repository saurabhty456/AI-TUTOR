import os
import json
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Please add it to your .env file."
    )


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="CodeTutor API",
    description="AI Programming Tutor and Quiz API",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# AI TUTOR INSTRUCTIONS
# =========================================================

TUTOR_INSTRUCTIONS = """
You are an expert programming tutor.

Your goal is to help students understand programming concepts clearly.

Follow these rules:

1. Explain concepts simply and clearly.
2. Assume the student is a beginner unless they indicate otherwise.
3. Keep normal answers concise: around 200-400 words.
4. For simple follow-up questions, answer directly instead of repeating
   the previous explanation.
5. Use examples only when they improve understanding.
6. For algorithms, mention time and space complexity briefly.
7. For debugging, explain the problem and show corrected code when useful.
8. For coding problems, explain the approach before the solution.
9. Use Markdown for headings, lists, and code blocks.
10. Do not repeat information that has already been explained in the
    conversation.
"""


# =========================================================
# QUIZ GENERATION INSTRUCTIONS
# =========================================================

QUIZ_INSTRUCTIONS = """
You are an expert programming quiz generator for a polished learning platform.
Generate accurate multiple-choice questions for the requested topic and difficulty.

STRICT RULES:
1. Return ONLY valid JSON.
2. Do NOT include Markdown fences around the JSON.
3. Generate exactly the requested number of questions.
4. Every question must have exactly 4 options.
5. There must be exactly ONE correct option.
6. correctIndex must be 0, 1, 2, or 3.
7. Keep questions clear, beginner-friendly, and professionally written.
8. Avoid ambiguous or trick questions.
9. Avoid duplicate questions.
10. Each option must be distinct and plausible.
11. Keep explanations short and helpful.
12. If a question includes code, put the code in a separate fenced Markdown code block inside the question string. Never write code inline in a paragraph.
13. Example format for a code question:
   "question": "What is the output of the following Python code?\n\n```python\nprint(\"Hello\")\n```"
14. Keep text concise and readable. Do not generate extra commentary outside the JSON.

Return EXACTLY this JSON structure:
{
  "questions": [
    {
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctIndex": 1,
      "explanation": "Short explanation of why the answer is correct."
    }
  ]
}
"""


# =========================================================
# DATA MODELS
# =========================================================

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    number_of_questions: int = 5


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correctIndex: int
    explanation: str


class QuizResponse(BaseModel):
    topic: str
    difficulty: str
    number_of_questions: int
    questions: list[QuizQuestion]


# =========================================================
# HOME ROUTE
# =========================================================

@app.get("/")
def home():
    return {
        "message": "CodeTutor API is running!"
    }


# =========================================================
# CHAT ROUTE
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    conversation = []

    for message in request.history:
        conversation.append(
            {
                "role": message.role,
                "parts": [
                    {
                        "text": message.content
                    }
                ]
            }
        )

    conversation.append(
        {
            "role": "user",
            "parts": [
                {
                    "text": request.message
                }
            ]
        }
    )

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=TUTOR_INSTRUCTIONS
            )
        )

        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="Gemini returned an empty response."
            )

        return {
            "message": request.message,
            "answer": response.text
        }

    except HTTPException:
        raise

    except Exception as error:

        print("Chat error:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to generate tutor response."
        )


# =========================================================
# QUIZ GENERATION
# =========================================================

@app.post("/quiz/generate")
def generate_quiz(request: QuizRequest):

    # -----------------------------------------------------
    # Validate topic
    # -----------------------------------------------------

    topic = request.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic is required."
        )

    # -----------------------------------------------------
    # Validate difficulty
    # -----------------------------------------------------

    difficulty = request.difficulty.lower().strip()

    allowed_difficulties = {
        "easy",
        "medium",
        "hard",
    }

    if difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be easy, medium, or hard."
        )

    # -----------------------------------------------------
    # Validate number of questions
    # -----------------------------------------------------

    number_of_questions = request.number_of_questions

    if number_of_questions < 1 or number_of_questions > 15:
        raise HTTPException(
            status_code=400,
            detail="Number of questions must be between 1 and 15."
        )

    # -----------------------------------------------------
    # Gemini prompt
    # -----------------------------------------------------

    prompt = f"""
Generate exactly {number_of_questions} concise beginner-friendly multiple-choice questions on {topic} at {difficulty} difficulty.

Rules:
- Exactly {number_of_questions} questions
- Each question must have exactly 4 options
- correctIndex must be 0, 1, 2, or 3
- Keep wording brief and clear
- Keep each explanation to 1-2 short sentences
- If code is needed, use a fenced Markdown code block in the question string
- Return valid JSON only matching the schema
"""

    # -----------------------------------------------------
    # Call Gemini using structured JSON output
    # -----------------------------------------------------

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=QUIZ_INSTRUCTIONS,
                response_mime_type="application/json",
                response_schema=QuizResponse,
                thinking_config=types.ThinkingConfig(
                    thinking_level="MINIMAL"
                ),
                temperature=0.2,
                max_output_tokens=5000,
            ),
        )

        if response.parsed is not None:
            quiz_data = QuizResponse.model_validate(response.parsed)
        else:
            raw_text = (response.text or "").strip()

            if not raw_text:
                raise HTTPException(
                    status_code=500,
                    detail="Gemini returned an empty quiz."
                )

            cleaned_text = raw_text
            if cleaned_text.startswith("```"):
                cleaned_text = re.sub(
                    r"^```(?:json)?\s*",
                    "",
                    cleaned_text,
                    flags=re.IGNORECASE,
                )
                cleaned_text = re.sub(
                    r"\s*```$",
                    "",
                    cleaned_text,
                    flags=re.IGNORECASE | re.DOTALL,
                ).strip()

            if not cleaned_text.startswith("{"):
                match = re.search(r"\{.*\}", cleaned_text, flags=re.DOTALL)
                if match:
                    cleaned_text = match.group(0)

            try:
                quiz_data = QuizResponse.model_validate(json.loads(cleaned_text))
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                print("Invalid Gemini JSON:", error)
                print("Gemini response:", raw_text)
                raise HTTPException(
                    status_code=500,
                    detail="Gemini returned invalid quiz data."
                )

        if len(quiz_data.questions) != number_of_questions:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Gemini returned "
                    f"{len(quiz_data.questions)} questions instead of "
                    f"{number_of_questions}."
                )
            )

        validated_questions = []

        for index, question in enumerate(quiz_data.questions):
            if not question.question.strip():
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Question {index + 1} "
                        "is missing question text."
                    )
                )

            if len(question.options) != 4:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Question {index + 1} "
                        "must have exactly 4 options."
                    )
                )

            cleaned_options = []
            for option in question.options:
                if not option.strip():
                    raise HTTPException(
                        status_code=500,
                        detail=(
                            f"Question {index + 1} "
                            "contains an invalid option."
                        )
                    )
                cleaned_options.append(option.strip())

            if len(set(option.lower() for option in cleaned_options)) != 4:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Question {index + 1} "
                        "contains duplicate options."
                    )
                )

            if question.correctIndex not in [0, 1, 2, 3]:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Question {index + 1} "
                        "has an invalid correctIndex."
                    )
                )

            if not question.explanation.strip():
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Question {index + 1} "
                        "is missing an explanation."
                    )
                )

            validated_questions.append(
                {
                    "question": question.question.strip(),
                    "options": cleaned_options,
                    "correctIndex": question.correctIndex,
                    "explanation": question.explanation.strip(),
                }
            )

        return {
            "topic": topic,
            "difficulty": difficulty,
            "number_of_questions": number_of_questions,
            "questions": validated_questions,
        }

    # -----------------------------------------------------
    # Known FastAPI errors
    # -----------------------------------------------------

    except HTTPException:
        raise

    # -----------------------------------------------------
    # Unexpected errors
    # -----------------------------------------------------

    except Exception as error:

        print("Quiz generation error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to generate quiz right now."
        )