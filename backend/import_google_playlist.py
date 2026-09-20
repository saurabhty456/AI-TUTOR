import csv
from pathlib import Path

from sqlalchemy import delete, select

from app.database import SessionLocal, initialize_database
from app.models import Playlist, PlaylistProblem, Problem


ROOT = Path(__file__).resolve().parents[1]
COMPANIES = {"google", "amazon", "microsoft", "meta", "apple", "netflix", "adobe", "uber", "linkedin", "goldman-sachs"}


def percentage(value: str) -> float:
    return float(value.strip().removesuffix("%"))


def canonical_key(url: str) -> str:
    return url.strip().lower().rstrip("/")


def import_company_playlist(company: str) -> int:
    initialize_database()
    csv_path = ROOT / "leetcode-companywise-interview-questions" / company / "all.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing company CSV: {csv_path}")
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    ranked_rows = sorted(
        rows,
        key=lambda row: (-percentage(row["Frequency %"]), int(row["ID"])),
    )[:50]

    company_name = "Goldman Sachs" if company == "goldman-sachs" else company.title()
    with SessionLocal() as db:
        playlist = db.scalar(select(Playlist).where(Playlist.slug == company))
        if playlist is None:
            playlist = Playlist(
                name=f"{company_name} Interview Questions",
                slug=company,
                company_name=company_name,
                description=f"Top {company_name} interview questions ranked by reported frequency.",
            )
            db.add(playlist)
            db.flush()
        else:
            playlist.name = f"{company_name} Interview Questions"
            playlist.company_name = company_name
            playlist.description = f"Top {company_name} interview questions ranked by reported frequency."

        selected_keys = {canonical_key(row["URL"]) for row in ranked_rows}
        db.execute(delete(PlaylistProblem).where(PlaylistProblem.playlist_id == playlist.id))

        for position, row in enumerate(ranked_rows, start=1):
            leetcode_id = int(row["ID"])
            key = canonical_key(row["URL"])
            problem = db.scalar(select(Problem).where(Problem.canonical_key == key))
            if problem is None:
                # Legacy columns remain populated until their destructive removal migration.
                problem = Problem(playlist_id=playlist.id, leetcode_id=leetcode_id, canonical_key=key, position=position)
                db.add(problem)

            problem.title = row["Title"].strip()
            problem.leetcode_url = row["URL"].strip()
            problem.difficulty = row["Difficulty"].strip()
            problem.acceptance_rate = percentage(row["Acceptance %"])
            problem.frequency = percentage(row["Frequency %"])
            problem.is_premium = None
            if problem.playlist_id is None:
                problem.playlist_id = playlist.id
            if problem.position is None:
                problem.position = position
            db.add(PlaylistProblem(
                playlist_id=playlist.id,
                problem=problem,
                position=position,
                frequency=problem.frequency,
                acceptance_rate=problem.acceptance_rate,
            ))

        db.commit()

    return len(ranked_rows)


def import_google_playlist() -> int:
    return import_company_playlist("google")


def import_all_company_playlists() -> dict[str, int]:
    return {company: import_company_playlist(company) for company in sorted(COMPANIES)}


if __name__ == "__main__":
    imported = import_all_company_playlists()
    print(f"Imported company playlists: {imported}")