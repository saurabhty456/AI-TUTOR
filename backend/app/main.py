import os
import json
import re
import base64
import hashlib
import hmac
import random
import re
import secrets
import time
from datetime import datetime, timezone
from decimal import Decimal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from sqlalchemy import create_engine, func, select, text as sql_text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.database import get_db, initialize_database
from app.interview_content import SQL_QUESTION_BANK, SYSTEM_DESIGN_QUESTIONS
from app.models import (
    Interview,
    InterviewAnswer,
    InterviewQuestion,
    InterviewResult,
    Playlist,
    PlaylistProblem,
    Problem,
    QuizResult,
    User,
)


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


class InterviewAnswerInput(BaseModel):
    question_id: int
    answer_text: str = Field(default="", max_length=20000)
    self_reported_result: str | None = Field(default=None, max_length=50)


class InterviewAnswersRequest(BaseModel):
    answers: list[InterviewAnswerInput] = Field(max_length=4)


class SQLExecutionRequest(BaseModel):
    query: str = Field(min_length=1, max_length=20000)


class InterviewEvaluation(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    dsa_feedback: str
    sql_feedback: str
    system_design_feedback: str
    strengths: list[str]
    improvements: list[str]
    final_feedback: str


class PlaylistSummaryResponse(BaseModel):
    id: int
    name: str
    slug: str
    company_name: str
    description: str
    total_problems: int


class ProblemResponse(BaseModel):
    id: int
    playlist_id: int
    leetcode_id: int
    title: str
    leetcode_url: str
    difficulty: str
    acceptance_rate: float
    frequency: float
    is_premium: bool | None
    position: int


class ProblemNavigationResponse(BaseModel):
    id: int
    title: str
    position: int


class ProblemDetailResponse(ProblemResponse):
    playlist_name: str
    playlist_slug: str
    company_name: str
    previous_problem: ProblemNavigationResponse | None = None
    next_problem: ProblemNavigationResponse | None = None


class PlaylistDetailResponse(PlaylistSummaryResponse):
    problems: list[ProblemResponse]


# =========================================================
# HOME ROUTE
# =========================================================

@app.get("/")
def home():
    return {
        "message": "CodeTutor API is running!"
    }


@app.get("/playlists", response_model=list[PlaylistSummaryResponse])
def get_playlists(db: Session = Depends(get_db)):
    playlists = db.scalars(select(Playlist).order_by(Playlist.name)).all()
    return [
        PlaylistSummaryResponse(
            id=playlist.id,
            name=playlist.name,
            slug=playlist.slug,
            company_name=playlist.company_name,
            description=playlist.description,
            total_problems=len(playlist.problem_links),
        )
        for playlist in playlists
    ]


@app.get("/playlists/{slug}", response_model=PlaylistDetailResponse)
def get_playlist(slug: str, db: Session = Depends(get_db)):
    playlist = db.scalar(select(Playlist).where(Playlist.slug == slug))
    if playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found.")

    return PlaylistDetailResponse(
        id=playlist.id,
        name=playlist.name,
        slug=playlist.slug,
        company_name=playlist.company_name,
        description=playlist.description,
        total_problems=len(playlist.problem_links),
        problems=[
            ProblemResponse(
                id=link.problem.id,
                playlist_id=playlist.id,
                leetcode_id=link.problem.leetcode_id,
                title=link.problem.title,
                leetcode_url=link.problem.leetcode_url,
                difficulty=link.problem.difficulty,
                acceptance_rate=link.acceptance_rate,
                frequency=link.frequency,
                is_premium=link.problem.is_premium,
                position=link.position,
            )
            for link in playlist.problem_links
        ],
    )


@app.get("/problems/{problem_id}", response_model=ProblemDetailResponse)
def get_problem(
    problem_id: int,
    playlist_slug: str | None = None,
    db: Session = Depends(get_db),
):
    problem = db.scalar(select(Problem).where(Problem.id == problem_id))
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found.")

    membership_query = select(PlaylistProblem).where(
        PlaylistProblem.problem_id == problem.id
    )
    if playlist_slug is not None:
        membership_query = membership_query.join(Playlist).where(Playlist.slug == playlist_slug)
    membership = db.scalars(
        membership_query.order_by(PlaylistProblem.playlist_id, PlaylistProblem.position)
    ).first()
    if membership is None:
        raise HTTPException(status_code=404, detail="Problem is not in that playlist.")

    playlist = membership.playlist
    previous_problem = db.scalar(
        select(PlaylistProblem).where(
            PlaylistProblem.playlist_id == membership.playlist_id,
            PlaylistProblem.position == membership.position - 1,
        )
    )
    next_problem = db.scalar(
        select(PlaylistProblem).where(
            PlaylistProblem.playlist_id == membership.playlist_id,
            PlaylistProblem.position == membership.position + 1,
        )
    )

    def navigation(problem_link: PlaylistProblem | None):
        if problem_link is None:
            return None
        return ProblemNavigationResponse(
            id=problem_link.problem.id,
            title=problem_link.problem.title,
            position=problem_link.position,
        )

    return ProblemDetailResponse(
        id=problem.id,
        playlist_id=membership.playlist_id,
        leetcode_id=problem.leetcode_id,
        title=problem.title,
        leetcode_url=problem.leetcode_url,
        difficulty=problem.difficulty,
        acceptance_rate=membership.acceptance_rate,
        frequency=membership.frequency,
        is_premium=problem.is_premium,
        position=membership.position,
        playlist_name=playlist.name,
        playlist_slug=playlist.slug,
        company_name=playlist.company_name,
        previous_problem=navigation(previous_problem),
        next_problem=navigation(next_problem),
    )


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
# INTERVIEW PREPARATION
# =========================================================

def _load_interview(db: Session, interview_id: int, user_id: int) -> Interview:
    interview = db.scalar(
        select(Interview).where(
            Interview.id == interview_id,
            Interview.user_id == user_id,
        )
    )
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found.")
    return interview


def _public_question_details(question: InterviewQuestion) -> dict:
    details = json.loads(question.details_json)
    if question.kind != "sql":
        return details
    return {
        "difficulty": details["difficulty"],
        "dialect": "PostgreSQL",
        "tables": [
            {
                "name": table["name"],
                "columns": table["columns"],
                "sample_rows": table["visible"],
            }
            for table in details["tables"]
        ],
        "expected_output": details["expected_visible"],
        "execution_enabled": bool(os.getenv("INTERVIEW_SANDBOX_DATABASE_URL")),
    }


def _serialize_interview(interview: Interview) -> dict:
    return {
        "id": interview.id,
        "status": interview.status,
        "created_at": interview.created_at.isoformat(),
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
        "questions": [
            {
                "id": question.id,
                "position": question.position,
                "kind": question.kind,
                "prompt": question.prompt,
                "details": _public_question_details(question),
                "answer": {
                    "answer_text": question.answer.answer_text,
                    "self_reported_result": question.answer.self_reported_result,
                    "sql_execution": json.loads(question.answer.execution_json)
                    if question.answer.execution_json
                    else None,
                }
                if question.answer
                else None,
            }
            for question in interview.questions
        ],
    }


def _save_interview_answers(
    db: Session,
    interview: Interview,
    answers: list[InterviewAnswerInput],
) -> None:
    questions_by_id = {question.id: question for question in interview.questions}
    if len({answer.question_id for answer in answers}) != len(answers):
        raise HTTPException(status_code=400, detail="Each question can be answered only once.")
    for item in answers:
        question = questions_by_id.get(item.question_id)
        if question is None:
            raise HTTPException(status_code=400, detail="An answer does not belong to this interview.")
        answer = question.answer
        if answer is None:
            answer = InterviewAnswer(question_id=question.id)
            db.add(answer)
            question.answer = answer
        answer.answer_text = item.answer_text.strip()
        if item.self_reported_result is not None and item.self_reported_result not in {
            "Solved",
            "Partially solved",
            "Could not solve",
        }:
            raise HTTPException(status_code=400, detail="Choose a valid self-reported result.")
        answer.self_reported_result = item.self_reported_result
    db.commit()


def _same_database(first_url: str, second_url: str) -> bool:
    first = make_url(first_url)
    second = make_url(second_url)
    return (
        (first.host or "localhost").lower(),
        first.port or 5432,
        first.database,
    ) == (
        (second.host or "localhost").lower(),
        second.port or 5432,
        second.database,
    )


def _normalized_sql_value(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _canonical_rows(rows: list[dict]) -> list[str]:
    return sorted(
        json.dumps(row, sort_keys=True, separators=(",", ":"), default=str)
        for row in rows
    )


def _run_sql_fixture(sandbox_url: str, tables: list[dict], fixture: str, query: str) -> list[dict]:
    engine = create_engine(sandbox_url, poolclass=NullPool, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as connection:
            with connection.begin():
                for table in tables:
                    name = table["name"]
                    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
                        raise RuntimeError("Invalid sandbox fixture table name.")
                    columns = table["columns"]
                    definitions = []
                    for column_name, column_type in columns:
                        if not re.fullmatch(r"[a-z_][a-z0-9_]*", column_name):
                            raise RuntimeError("Invalid sandbox fixture column name.")
                        if column_type not in {"INTEGER", "TEXT", "NUMERIC", "DATE"}:
                            raise RuntimeError("Invalid sandbox fixture column type.")
                        definitions.append(f'"{column_name}" {column_type}')
                    connection.exec_driver_sql(
                        f'CREATE TEMPORARY TABLE "{name}" ({", ".join(definitions)}) '
                        "ON COMMIT PRESERVE ROWS"
                    )
                    fixture_rows = table[fixture]
                    if fixture_rows:
                        column_names = [column[0] for column in columns]
                        bind_names = [f"v{index}" for index in range(len(columns))]
                        placeholders = ", ".join(f":{name}" for name in bind_names)
                        quoted_columns = ", ".join(f'"{name}"' for name in column_names)
                        insert_sql = (
                            f'INSERT INTO "{name}" '
                            f"({quoted_columns}) "
                            f"VALUES ({placeholders})"
                        )
                        connection.execute(
                            sql_text(insert_sql),
                            [dict(zip(bind_names, row)) for row in fixture_rows],
                        )
            with connection.begin():
                connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                connection.exec_driver_sql("SET LOCAL statement_timeout = '2500ms'")
                connection.exec_driver_sql("SET LOCAL lock_timeout = '500ms'")
                result = connection.exec_driver_sql(query)
                return [
                    {key: _normalized_sql_value(value) for key, value in row._mapping.items()}
                    for row in result
                ]
    finally:
        engine.dispose()


def _store_sql_execution(answer: InterviewAnswer, execution: dict) -> None:
    answer.answer_text = execution.get("query", answer.answer_text)
    answer.execution_json = json.dumps(execution, default=str)


@app.post("/interviews/start")
def start_interview(
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    problems = db.scalars(
        select(Problem)
        .where(Problem.difficulty.in_(["Medium", "Hard"]))
        .order_by(func.random())
        .limit(2)
    ).all()
    if len(problems) < 2:
        problems = db.scalars(select(Problem).order_by(func.random()).limit(2)).all()
    if len(problems) < 2:
        raise HTTPException(status_code=503, detail="At least two DSA problems are required to start an interview.")

    sql_question = random.choice(SQL_QUESTION_BANK)
    interview = Interview(user_id=user.id)
    interview.questions = [
        InterviewQuestion(
            position=1,
            kind="dsa",
            prompt="Explain your approach, correctness, and time and space complexity.",
            details_json=json.dumps({
                "title": problems[0].title,
                "difficulty": problems[0].difficulty,
                "leetcode_url": problems[0].leetcode_url,
            }),
        ),
        InterviewQuestion(
            position=2,
            kind="dsa",
            prompt="Explain your approach, correctness, and time and space complexity.",
            details_json=json.dumps({
                "title": problems[1].title,
                "difficulty": problems[1].difficulty,
                "leetcode_url": problems[1].leetcode_url,
            }),
        ),
        InterviewQuestion(
            position=3,
            kind="sql",
            prompt=sql_question["prompt"],
            details_json=json.dumps({**sql_question, "difficulty": "Medium / Hard"}),
        ),
        InterviewQuestion(
            position=4,
            kind="system_design",
            prompt=random.choice(SYSTEM_DESIGN_QUESTIONS),
            details_json="{}",
        ),
    ]
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return _serialize_interview(interview)


@app.get("/interviews/history")
def get_interview_history(
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    interviews = db.scalars(
        select(Interview)
        .where(Interview.user_id == user.id)
        .order_by(Interview.created_at.desc())
    ).all()
    return [
        {
            "id": interview.id,
            "status": interview.status,
            "created_at": interview.created_at.isoformat(),
            "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            "overall_score": interview.result.overall_score if interview.result else None,
        }
        for interview in interviews
    ]


@app.get("/interviews/{interview_id}")
def get_interview(
    interview_id: int,
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    interview = _load_interview(db, interview_id, user.id)
    return _serialize_interview(interview)


@app.post("/interviews/{interview_id}/answers")
def save_interview_answers(
    interview_id: int,
    request: InterviewAnswersRequest,
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    interview = _load_interview(db, interview_id, user.id)
    if interview.status == "completed":
        raise HTTPException(status_code=409, detail="A completed interview cannot be changed.")
    _save_interview_answers(db, interview, request.answers)
    return {"saved": True}


@app.post("/interviews/{interview_id}/questions/{question_id}/execute-sql")
def execute_interview_sql(
    interview_id: int,
    question_id: int,
    request: SQLExecutionRequest,
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    interview = _load_interview(db, interview_id, user.id)
    if interview.status == "completed":
        raise HTTPException(status_code=409, detail="A completed interview cannot be changed.")
    question = next((item for item in interview.questions if item.id == question_id), None)
    if question is None or question.kind != "sql":
        raise HTTPException(status_code=404, detail="SQL question not found.")
    sandbox_url = os.getenv("INTERVIEW_SANDBOX_DATABASE_URL")
    if not sandbox_url:
        raise HTTPException(
            status_code=503,
            detail="SQL execution is unavailable until an isolated INTERVIEW_SANDBOX_DATABASE_URL is configured.",
        )
    if _same_database(sandbox_url, os.environ["DATABASE_URL"]):
        raise HTTPException(status_code=503, detail="The SQL sandbox must use a separate database from the application.")

    query = request.query.strip()
    statement = query[:-1].rstrip() if query.endswith(";") else query
    if ";" in statement or not re.match(r"(?is)^(select|with)\b", statement):
        raise HTTPException(status_code=400, detail="Run exactly one SELECT or WITH query.")
    details = json.loads(question.details_json)
    try:
        visible_output = _run_sql_fixture(sandbox_url, details["tables"], "visible", statement)
        hidden_output = _run_sql_fixture(sandbox_url, details["tables"], "hidden", statement)
        visible_passed = _canonical_rows(visible_output) == _canonical_rows(details["expected_visible"])
        hidden_passed = _canonical_rows(hidden_output) == _canonical_rows(details["expected_hidden"])
        execution = {
            "query": statement,
            "correct": visible_passed and hidden_passed,
            "visible_passed": visible_passed,
            "hidden_passed": hidden_passed,
            "hidden_tests_total": 1,
            "visible_output": visible_output,
            "error": None,
        }
    except Exception as error:
        if hasattr(error, "orig") and error.orig is not None:
            message = str(error.orig)
        else:
            message = str(error)
        execution = {
            "query": statement,
            "correct": False,
            "visible_passed": False,
            "hidden_passed": False,
            "hidden_tests_total": 1,
            "visible_output": [],
            "error": message[:1000],
        }

    answer = question.answer
    if answer is None:
        answer = InterviewAnswer(question_id=question.id)
        db.add(answer)
        question.answer = answer
    _store_sql_execution(answer, execution)
    db.commit()
    return {key: value for key, value in execution.items() if key != "query"}


@app.post("/interviews/{interview_id}/evaluate")
def evaluate_interview(
    interview_id: int,
    request: InterviewAnswersRequest,
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    interview = _load_interview(db, interview_id, user.id)
    if interview.result:
        return _serialize_interview_result(interview)
    if len(request.answers) != 4:
        raise HTTPException(status_code=400, detail="Submit all four interview answers before evaluation.")
    _save_interview_answers(db, interview, request.answers)

    answer_context = []
    for question in interview.questions:
        answer = question.answer
        answer_context.append({
            "position": question.position,
            "type": question.kind,
            "prompt": question.prompt,
            "details": _public_question_details(question),
            "answer": answer.answer_text if answer else "",
            "self_reported_result": answer.self_reported_result if answer else None,
            "sql_execution": json.loads(answer.execution_json)
            if answer and answer.execution_json
            else None,
        })
    evaluation_prompt = (
        "Evaluate this complete technical interview fairly and constructively. "
        "Do not claim DSA code was executed; DSA answers are explanations and self-reports. "
        "For SQL, weigh actual visible and hidden test results heavily when available; "
        "if execution was unavailable, say so and evaluate the written query cautiously. "
        "Assess system design requirements, architecture, APIs, database choice, scalability, "
        "caching, reliability/failure handling, and trade-offs. Return concise specific feedback.\n\n"
        + json.dumps(answer_context, ensure_ascii=False)
    )
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=evaluation_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InterviewEvaluation,
                temperature=0.2,
                max_output_tokens=2500,
            ),
        )
        if response.parsed is not None:
            evaluation = InterviewEvaluation.model_validate(response.parsed)
        else:
            evaluation = InterviewEvaluation.model_validate(json.loads(response.text or "{}"))
    except Exception as error:
        print("Interview evaluation error:", error)
        raise HTTPException(status_code=502, detail="AI evaluation could not be completed. Your answers have been saved; please try again.")

    result = InterviewResult(
        overall_score=round(evaluation.overall_score, 1),
        dsa_feedback=evaluation.dsa_feedback,
        sql_feedback=evaluation.sql_feedback,
        system_design_feedback=evaluation.system_design_feedback,
        strengths_json=json.dumps(evaluation.strengths),
        improvements_json=json.dumps(evaluation.improvements),
        final_feedback=evaluation.final_feedback,
    )
    interview.result = result
    interview.status = "completed"
    interview.completed_at = datetime.now(timezone.utc)
    db.add(result)
    db.commit()
    return _serialize_interview_result(interview)


def _serialize_interview_result(interview: Interview) -> dict:
    result = interview.result
    if result is None:
        raise HTTPException(status_code=404, detail="Interview result not found.")
    return {
        "interview_id": interview.id,
        "overall_score": result.overall_score,
        "dsa_feedback": result.dsa_feedback,
        "sql_feedback": result.sql_feedback,
        "system_design_feedback": result.system_design_feedback,
        "strengths": json.loads(result.strengths_json),
        "improvements": json.loads(result.improvements_json),
        "final_feedback": result.final_feedback,
        "evaluated_at": result.evaluated_at.isoformat(),
        "ai_generated": True,
        "questions": [
            {
                "position": question.position,
                "kind": question.kind,
                "prompt": question.prompt,
                "title": json.loads(question.details_json).get("title"),
                "answer_text": question.answer.answer_text if question.answer else "",
                "self_reported_result": question.answer.self_reported_result
                if question.answer
                else None,
                "sql_execution": json.loads(question.answer.execution_json)
                if question.answer and question.answer.execution_json
                else None,
            }
            for question in interview.questions
        ],
    }


@app.get("/interviews/{interview_id}/result")
def get_interview_result(
    interview_id: int,
    user: AuthUser = Depends(current_user),
    db: Session = Depends(get_db),
):
    interview = _load_interview(db, interview_id, user.id)
    return _serialize_interview_result(interview)


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