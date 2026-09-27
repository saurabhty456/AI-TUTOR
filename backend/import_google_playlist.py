import csv
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from sqlalchemy import delete, select

from app.database import SessionLocal, initialize_database
from app.models import Playlist, PlaylistProblem, Problem


DATASET_ROOT = Path(__file__).resolve().parents[1] / "leetcode-companywise-interview-questions"
COMPANIES = (
    ("Google", "google"),
    ("Amazon", "amazon"),
    ("Microsoft", "microsoft"),
    ("Meta", "meta"),
    ("Apple", "apple"),
    ("Netflix", "netflix"),
    ("Adobe", "adobe"),
    ("Uber", "uber"),
    ("LinkedIn", "linkedin"),
    ("Goldman Sachs", "goldman-sachs"),
)


@dataclass(frozen=True)
class Question:
    leetcode_id: int
    canonical_key: str
    title: str
    leetcode_url: str
    difficulty: str
    acceptance_rate: float
    frequency: float
    is_premium: bool | None


def percentage(value: str) -> float:
    return float(value.strip().removesuffix("%"))


def canonical_problem_key(url: str) -> str:
    parsed = urlsplit(url.strip())
    if not parsed.scheme or not parsed.netloc or not parsed.path:
        raise ValueError(f"Invalid LeetCode problem URL: {url!r}")
    return f"{parsed.scheme.casefold()}://{parsed.netloc.casefold()}{parsed.path.rstrip('/').casefold()}"


def premium_status(row: dict[str, str]) -> bool | None:
    for column in ("Premium", "Is Premium", "is_premium"):
        value = (row.get(column) or "").strip().casefold()
        if value in {"true", "yes", "1", "premium"}:
            return True
        if value in {"false", "no", "0", "free"}:
            return False
    return None


def load_ranked_questions(csv_path: Path) -> list[Question]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        rows = csv.DictReader(csv_file)
        questions = []
        for row in rows:
            try:
                leetcode_id = int(row.get("ID", "").strip())
                leetcode_url = row.get("URL", "").strip()
                title = row.get("Title", "").strip()
                difficulty = row.get("Difficulty", "").strip()
                acceptance_rate = percentage(row.get("Acceptance %", ""))
                frequency = percentage(row.get("Frequency %", ""))
                canonical_key = canonical_problem_key(leetcode_url)
            except (AttributeError, ValueError):
                continue

            if not title or not difficulty:
                continue

            questions.append(
                Question(
                    leetcode_id=leetcode_id,
                    canonical_key=canonical_key,
                    title=title,
                    leetcode_url=leetcode_url,
                    difficulty=difficulty,
                    acceptance_rate=acceptance_rate,
                    frequency=frequency,
                    is_premium=premium_status(row),
                )
            )

    questions.sort(key=lambda question: (-question.frequency, question.leetcode_id))
    unique_questions = {question.canonical_key: question for question in reversed(questions)}
    ranked_unique_questions = sorted(
        unique_questions.values(),
        key=lambda question: (-question.frequency, question.leetcode_id),
    )
    return ranked_unique_questions[:50]


def import_company_playlists(
    companies: tuple[tuple[str, str], ...] = COMPANIES,
) -> dict[str, int]:
    initialize_database()
    summary: dict[str, int] = {}

    with SessionLocal() as db:
        for company_name, slug in companies:
            questions = load_ranked_questions(DATASET_ROOT / slug / "all.csv")
            playlist = db.scalar(select(Playlist).where(Playlist.slug == slug))
            if playlist is None:
                playlist = Playlist(
                    name=f"{company_name} Interview Questions",
                    slug=slug,
                    company_name=company_name,
                    description=f"Top {company_name} interview questions ranked by reported frequency.",
                )
                db.add(playlist)
                db.flush()
            else:
                playlist.name = f"{company_name} Interview Questions"
                playlist.company_name = company_name
                playlist.description = (
                    f"Top {company_name} interview questions ranked by reported frequency."
                )

            selected_problem_ids = set()
            for position, question in enumerate(questions, start=1):
                problem = db.scalar(
                    select(Problem).where(Problem.canonical_key == question.canonical_key)
                )
                if problem is None:
                    problem = Problem(
                        leetcode_id=question.leetcode_id,
                        canonical_key=question.canonical_key,
                        title=question.title,
                        leetcode_url=question.leetcode_url,
                        difficulty=question.difficulty,
                        is_premium=question.is_premium,
                    )
                    db.add(problem)
                    db.flush()
                else:
                    problem.leetcode_id = question.leetcode_id
                    problem.title = question.title
                    problem.leetcode_url = question.leetcode_url
                    problem.difficulty = question.difficulty
                    if question.is_premium is not None:
                        problem.is_premium = question.is_premium

                selected_problem_ids.add(problem.id)
                membership = db.scalar(
                    select(PlaylistProblem).where(
                        PlaylistProblem.playlist_id == playlist.id,
                        PlaylistProblem.problem_id == problem.id,
                    )
                )
                if membership is None:
                    membership = PlaylistProblem(
                        playlist_id=playlist.id,
                        problem_id=problem.id,
                        position=position,
                        frequency=question.frequency,
                        acceptance_rate=question.acceptance_rate,
                    )
                    db.add(membership)
                else:
                    membership.position = position
                    membership.frequency = question.frequency
                    membership.acceptance_rate = question.acceptance_rate

            db.flush()
            stale_memberships = delete(PlaylistProblem).where(
                PlaylistProblem.playlist_id == playlist.id
            )
            if selected_problem_ids:
                stale_memberships = stale_memberships.where(
                    PlaylistProblem.problem_id.not_in(selected_problem_ids)
                )
            db.execute(stale_memberships)
            summary[company_name] = len(questions)

        db.commit()

    return summary


def import_google_playlist() -> int:
    return import_company_playlists((("Google", "google"),))["Google"]


if __name__ == "__main__":
    for company_name, imported_count in import_company_playlists().items():
        print(f"{company_name}: {imported_count}")