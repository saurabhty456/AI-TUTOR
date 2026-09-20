import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add the PostgreSQL connection URL to backend/.env."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    from app.models import CodeSubmission, Playlist, PlaylistProblem, Problem, ProblemExecutionSpec, ProblemReferenceSolution, ProblemTestCase, QuizResult, User

    try:
        Base.metadata.create_all(bind=engine)
        from sqlalchemy import inspect, text

        columns = {column["name"] for column in inspect(engine).get_columns("problem_test_cases")}
        with engine.begin() as connection:
            for name, definition in (
                ("category", "VARCHAR(40) NOT NULL DEFAULT 'custom'"),
                ("difficulty_level", "VARCHAR(20) NOT NULL DEFAULT 'medium'"),
                ("explanation", "VARCHAR(1000) NOT NULL DEFAULT ''"),
            ):
                if name not in columns:
                    if engine.dialect.name == "postgresql":
                        connection.execute(text(f"ALTER TABLE problem_test_cases ADD COLUMN IF NOT EXISTS {name} {definition}"))
                    else:
                        connection.execute(text(f"ALTER TABLE problem_test_cases ADD COLUMN {name} {definition}"))

            problem_columns = {column["name"] for column in inspect(engine).get_columns("problems")}
            if "canonical_key" not in problem_columns:
                connection.execute(text("ALTER TABLE problems ADD COLUMN canonical_key VARCHAR(1000)"))
                connection.execute(text("UPDATE problems SET canonical_key = LOWER(TRIM(TRAILING '/' FROM leetcode_url)) WHERE canonical_key IS NULL"))
                if engine.dialect.name == "postgresql":
                    connection.execute(text("ALTER TABLE problems ALTER COLUMN canonical_key SET NOT NULL"))
            if engine.dialect.name == "postgresql":
                connection.execute(text("ALTER TABLE problems ALTER COLUMN is_premium DROP NOT NULL"))
            spec_columns = {column["name"] for column in inspect(engine).get_columns("problem_execution_specs")}
            if "output_comparison" not in spec_columns:
                connection.execute(text("ALTER TABLE problem_execution_specs ADD COLUMN output_comparison VARCHAR(30) NOT NULL DEFAULT 'exact_json'"))
            connection.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_problem_canonical_key_idx ON problems (canonical_key)"
            ))

            connection.execute(text(
                """INSERT INTO playlist_problems (playlist_id, problem_id, position, frequency, acceptance_rate)
                   SELECT playlist_id, id, COALESCE(position, 1), frequency, acceptance_rate
                   FROM problems WHERE playlist_id IS NOT NULL
                   ON CONFLICT (playlist_id, problem_id) DO NOTHING"""
            ) if engine.dialect.name == "postgresql" else text(
                """INSERT OR IGNORE INTO playlist_problems (playlist_id, problem_id, position, frequency, acceptance_rate)
                   SELECT playlist_id, id, COALESCE(position, 1), frequency, acceptance_rate
                   FROM problems WHERE playlist_id IS NOT NULL"""
            ))
    except SQLAlchemyError as error:
        raise RuntimeError(
            "Unable to connect to PostgreSQL or initialize the database. "
            "Check DATABASE_URL and confirm PostgreSQL is running."
        ) from error
