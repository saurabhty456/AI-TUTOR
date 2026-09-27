import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine, inspect, text, update
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
    from app.models import Playlist, PlaylistProblem, Problem, QuizResult, User

    try:
        Base.metadata.create_all(bind=engine)
        migrate_legacy_problem_relationships()
    except SQLAlchemyError as error:
        raise RuntimeError(
            "Unable to connect to PostgreSQL or initialize the database. "
            "Check DATABASE_URL and confirm PostgreSQL is running."
        ) from error


def migrate_legacy_problem_relationships() -> None:
    inspector = inspect(engine)
    if "problems" not in inspector.get_table_names():
        return

    problem_columns = {column["name"]: column for column in inspector.get_columns("problems")}
    legacy_columns = {"playlist_id", "frequency", "position", "acceptance_rate"}
    has_legacy_relationship = legacy_columns.issubset(problem_columns)
    dependent_columns = [
        (table_name, column_name)
        for table_name in inspector.get_table_names()
        if table_name not in {"problems", "playlist_problems"}
        for foreign_key in inspector.get_foreign_keys(table_name)
        if foreign_key.get("referred_table") == "problems"
        for column_name in foreign_key["constrained_columns"]
    ]

    with engine.begin() as connection:
        needs_key_backfill = "canonical_key" not in problem_columns
        if needs_key_backfill:
            connection.execute(text("ALTER TABLE problems ADD COLUMN canonical_key VARCHAR(1000)"))

        if not needs_key_backfill:
            needs_key_backfill = bool(
                connection.execute(
                    text(
                        "SELECT EXISTS (SELECT 1 FROM problems "
                        "WHERE canonical_key IS NULL OR canonical_key = '')"
                    )
                ).scalar()
            )

        if needs_key_backfill:
            connection.execute(text("DROP INDEX IF EXISTS uq_problem_canonical_key_idx"))
            connection.execute(
                text(
                    "UPDATE problems SET canonical_key = lower(regexp_replace("
                    "split_part(trim(leetcode_url), '?', 1), '/+$', '', 'g'))"
                )
            )

        if has_legacy_relationship:
            connection.execute(
                text(
                    "INSERT INTO playlist_problems "
                    "(playlist_id, problem_id, position, frequency, acceptance_rate) "
                    "SELECT playlist_id, id, position, frequency, acceptance_rate "
                    "FROM problems WHERE playlist_id IS NOT NULL "
                    "ON CONFLICT (playlist_id, problem_id) DO NOTHING"
                )
            )

        duplicate_groups = connection.execute(
            text(
                "SELECT canonical_key, array_agg(id ORDER BY id) AS problem_ids "
                "FROM problems WHERE canonical_key IS NOT NULL "
                "GROUP BY canonical_key HAVING count(*) > 1"
            )
        ).all()
        for _, problem_ids in duplicate_groups:
            canonical_id = problem_ids[0]
            for duplicate_id in problem_ids[1:]:
                connection.execute(
                    text(
                        "DELETE FROM playlist_problems duplicate_link "
                        "USING playlist_problems canonical_link "
                        "WHERE duplicate_link.problem_id = :duplicate_id "
                        "AND canonical_link.problem_id = :canonical_id "
                        "AND duplicate_link.playlist_id = canonical_link.playlist_id"
                    ),
                    {"duplicate_id": duplicate_id, "canonical_id": canonical_id},
                )
                connection.execute(
                    text(
                        "UPDATE playlist_problems SET problem_id = :canonical_id "
                        "WHERE problem_id = :duplicate_id"
                    ),
                    {"duplicate_id": duplicate_id, "canonical_id": canonical_id},
                )
                connection.execute(
                    text(
                        "UPDATE problems AS canonical SET is_premium = duplicate.is_premium "
                        "FROM problems AS duplicate "
                        "WHERE canonical.id = :canonical_id "
                        "AND duplicate.id = :duplicate_id "
                        "AND canonical.is_premium IS NULL "
                        "AND duplicate.is_premium IS NOT NULL"
                    ),
                    {"duplicate_id": duplicate_id, "canonical_id": canonical_id},
                )

                for table_name, column_name in dependent_columns:
                    table = Table(table_name, MetaData(), autoload_with=connection)
                    connection.execute(
                        update(table)
                        .where(table.c[column_name] == duplicate_id)
                        .values({column_name: canonical_id})
                    )

                connection.execute(
                    text("DELETE FROM problems WHERE id = :duplicate_id"),
                    {"duplicate_id": duplicate_id},
                )

        connection.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS uq_problem_canonical_key_idx "
                 "ON problems (canonical_key)")
        )
        connection.execute(text("ALTER TABLE problems ALTER COLUMN canonical_key SET NOT NULL"))

        if has_legacy_relationship:
            for column_name, column in problem_columns.items():
                if column_name in legacy_columns and not column["nullable"]:
                    connection.execute(
                        text(f"ALTER TABLE problems ALTER COLUMN {column_name} DROP NOT NULL")
                    )
