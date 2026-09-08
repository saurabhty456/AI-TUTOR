import os
import json
import re
import base64
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db, initialize_database
from app.models import QuizResult, User


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
# AUTHENTICATION
# =========================================================

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN_SECONDS = 60 * 60 * 24 * 7


initialize_database()


class AuthSignupRequest(BaseModel):
    name: str
    email: str
    password: str


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class AuthUser(BaseModel):
    id: int
    name: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: AuthUser


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )
    return "scrypt${}${}".format(
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived_key).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, encoded_salt, encoded_key = stored_hash.split("$", 2)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected_key = base64.urlsafe_b64decode(encoded_key.encode("ascii"))
        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
        )
        return hmac.compare_digest(actual_key, expected_key)
    except (ValueError, TypeError):
        return False


def encode_jwt(user_id: int) -> str:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Authentication is not configured on the server.",
        )

    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + JWT_EXPIRES_IN_SECONDS,
    }

    def encode_part(value: dict) -> str:
        return base64.urlsafe_b64encode(
            json.dumps(value, separators=(",", ":")).encode("utf-8")
        ).rstrip(b"=").decode("ascii")

    encoded_header = encode_part(header)
    encoded_payload = encode_part(payload)
    unsigned_token = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        unsigned_token.encode("ascii"),
        hashlib.sha256,
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode(
        "ascii"
    )
    return f"{unsigned_token}.{encoded_signature}"


def decode_jwt(token: str) -> int:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Authentication is not configured on the server.",
        )

    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        unsigned_token = f"{encoded_header}.{encoded_payload}"
        expected_signature = hmac.new(
            JWT_SECRET.encode("utf-8"),
            unsigned_token.encode("ascii"),
            hashlib.sha256,
        ).digest()
        actual_signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )

        if not hmac.compare_digest(actual_signature, expected_signature):
            raise ValueError("Invalid signature")

        payload = json.loads(
            base64.urlsafe_b64decode(
                encoded_payload + "=" * (-len(encoded_payload) % 4)
            )
        )
        if int(payload["exp"]) <= int(time.time()):
            raise ValueError("Expired token")
        return int(payload["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please log in again.",
        )


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication is required.",
        )

    user_id = decode_jwt(authorization[7:])
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="User account not found.")
    return AuthUser(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
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


class QuizResultCreate(BaseModel):
    topic: str
    difficulty: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    unanswered_questions: int
    score_percentage: float
    time_limit: int


class QuizResultResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    difficulty: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    unanswered_questions: int
    score_percentage: float
    time_limit: int
    completed_at: datetime


# =========================================================
# HOME ROUTE
# =========================================================

@app.get("/")
def home():
    return {
        "message": "CodeTutor API is running!"
    }


# =========================================================
# AUTH ROUTES
# =========================================================

@app.post("/auth/signup", response_model=AuthResponse)
def signup(request: AuthSignupRequest, db: Session = Depends(get_db)):
    name = request.name.strip()
    email = normalize_email(request.email)

    if not name:
        raise HTTPException(status_code=400, detail="Name is required.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long.",
        )

    created_at = datetime.now(timezone.utc).isoformat()
    try:
        user_record = User(
            name=name,
            email=email,
            password_hash=hash_password(request.password),
            created_at=created_at,
        )
        db.add(user_record)
        db.commit()
        db.refresh(user_record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = AuthUser(
        id=user_record.id,
        name=name,
        email=email,
        created_at=created_at,
    )
    return AuthResponse(
        access_token=encode_jwt(user.id),
        token_type="bearer",
        user=user,
    )


@app.post("/auth/login", response_model=AuthResponse)
def login(request: AuthLoginRequest, db: Session = Depends(get_db)):
    email = normalize_email(request.email)
    user_record = db.scalar(select(User).where(User.email == email))

    if user_record is None or not verify_password(
        request.password, user_record.password_hash
    ):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    user = AuthUser(
        id=user_record.id,
        name=user_record.name,
        email=user_record.email,
        created_at=user_record.created_at,
    )
    return AuthResponse(
        access_token=encode_jwt(user.id),
        token_type="bearer",
        user=user,
    )


@app.get("/auth/me", response_model=AuthUser)
def me(user: AuthUser = Depends(current_user)):
    return user


# =========================================================
# QUIZ RESULTS
# =========================================================

@app.post("/quiz/results", response_model=QuizResultResponse)
def create_quiz_result(
    request: QuizResultCreate,
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    topic = request.topic.strip()
    difficulty = request.difficulty.strip().title()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required.")

    if difficulty not in {"Easy", "Medium", "Hard"}:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be Easy, Medium, or Hard.",
        )

    total_questions = request.total_questions
    correct_answers = request.correct_answers
    wrong_answers = request.wrong_answers
    unanswered_questions = request.unanswered_questions
    score_percentage = float(request.score_percentage)
    time_limit = request.time_limit

    if total_questions <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total questions must be greater than zero.",
        )

    if correct_answers < 0 or wrong_answers < 0 or unanswered_questions < 0:
        raise HTTPException(
            status_code=400,
            detail="Question counts cannot be negative.",
        )

    if correct_answers + wrong_answers + unanswered_questions != total_questions:
        raise HTTPException(
            status_code=400,
            detail="Correct, wrong, and unanswered totals must add up to the total number of questions.",
        )

    if not 0 <= score_percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Score percentage must be between 0 and 100.",
        )

    if time_limit < 0:
        raise HTTPException(
            status_code=400,
            detail="Time limit cannot be negative.",
        )

    try:
        quiz_result = QuizResult(
            user_id=user.id,
            topic=topic,
            difficulty=difficulty,
            total_questions=total_questions,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            unanswered_questions=unanswered_questions,
            score_percentage=round(score_percentage, 2),
            time_limit=time_limit,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(quiz_result)
        db.commit()
        db.refresh(quiz_result)
        return quiz_result
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Unable to save your quiz result right now.",
        )
    except Exception as error:
        db.rollback()
        print("Quiz result save error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to save your quiz result right now.",
        )


@app.get("/quiz/results", response_model=list[QuizResultResponse])
def get_quiz_results(
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    results = (
        db.execute(
            select(QuizResult)
            .where(QuizResult.user_id == user.id)
            .order_by(QuizResult.completed_at.desc())
        )
        .scalars()
        .all()
    )
    return results


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
Generate exactly {number_of_questions} concise multiple-choice questions on {topic} at {difficulty} difficulty.
Every question must have exactly 4 non-empty, distinct options, one correctIndex (0-3), and a short 1-2 sentence explanation.
If code is included, use a fenced Markdown code block in the question string.
Return only valid JSON matching the schema: exactly {number_of_questions} questions and no extra fields.
"""

    # -----------------------------------------------------
    # Call Gemini using structured JSON output
    # -----------------------------------------------------

    class InvalidQuizContent(Exception):
        pass

    def generate_response():
        return client.models.generate_content(
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

    def validate_response(response):
        try:
            if response.parsed is not None:
                quiz_data = QuizResponse.model_validate(response.parsed)
            else:
                raw_text = (response.text or "").strip()

                if not raw_text:
                    raise InvalidQuizContent("Gemini returned an empty quiz.")

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
                    match = re.search(
                        r"\{.*\}",
                        cleaned_text,
                        flags=re.DOTALL,
                    )
                    if match:
                        cleaned_text = match.group(0)

                quiz_data = QuizResponse.model_validate(
                    json.loads(cleaned_text)
                )

            if len(quiz_data.questions) != number_of_questions:
                raise InvalidQuizContent(
                    f"Gemini returned {len(quiz_data.questions)} questions "
                    f"instead of {number_of_questions}."
                )

            validated_questions = []

            for index, question in enumerate(quiz_data.questions):
                if not question.question.strip():
                    raise InvalidQuizContent(
                        f"Question {index + 1} is missing question text."
                    )

                if len(question.options) != 4:
                    raise InvalidQuizContent(
                        f"Question {index + 1} must have exactly 4 options."
                    )

                cleaned_options = []
                for option in question.options:
                    if not option.strip():
                        raise InvalidQuizContent(
                            f"Question {index + 1} contains an invalid option."
                        )
                    cleaned_options.append(option.strip())

                if len(
                    set(option.lower() for option in cleaned_options)
                ) != 4:
                    raise InvalidQuizContent(
                        f"Question {index + 1} contains duplicate options."
                    )

                if question.correctIndex not in [0, 1, 2, 3]:
                    raise InvalidQuizContent(
                        f"Question {index + 1} has an invalid correctIndex."
                    )

                if not question.explanation.strip():
                    raise InvalidQuizContent(
                        f"Question {index + 1} is missing an explanation."
                    )

                validated_questions.append(
                    {
                        "question": question.question.strip(),
                        "options": cleaned_options,
                        "correctIndex": question.correctIndex,
                        "explanation": question.explanation.strip(),
                    }
                )

            return validated_questions
        except InvalidQuizContent:
            raise
        except Exception as error:
            raise InvalidQuizContent(str(error)) from error

    try:
        response = generate_response()

        try:
            validated_questions = validate_response(response)
        except InvalidQuizContent as error:
            print("Quiz validation failed. Regenerating once without delay.")
            print("Quiz validation error:", error)
            response = generate_response()

            try:
                validated_questions = validate_response(response)
            except InvalidQuizContent as second_error:
                print("Quiz validation error:", second_error)
                raise HTTPException(
                    status_code=500,
                    detail="Unable to generate a valid quiz right now."
                ) from second_error

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