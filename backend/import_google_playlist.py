import csv
from pathlib import Path

from sqlalchemy import delete, select

from app.database import SessionLocal, initialize_database
from app.models import Playlist, Problem


CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "leetcode-companywise-interview-questions"
    / "google"
    / "all.csv"
)


def percentage(value: str) -> float:
    return float(value.strip().removesuffix("%"))


def import_google_playlist() -> int:
    initialize_database()

    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    ranked_rows = sorted(
        rows,
        key=lambda row: (-percentage(row["Frequency %"]), int(row["ID"])),
    )[:50]

    with SessionLocal() as db:
        playlist = db.scalar(select(Playlist).where(Playlist.slug == "google"))
        if playlist is None:
            playlist = Playlist(
                name="Google Interview Questions",
                slug="google",
                company_name="Google",
                description="Top Google interview questions ranked by reported frequency.",
            )
            db.add(playlist)
            db.flush()
        else:
            playlist.name = "Google Interview Questions"
            playlist.company_name = "Google"
            playlist.description = "Top Google interview questions ranked by reported frequency."

        selected_ids = {int(row["ID"]) for row in ranked_rows}
        db.execute(
            delete(Problem).where(
                Problem.playlist_id == playlist.id,
                Problem.leetcode_id.not_in(selected_ids),
            )
        )

        for position, row in enumerate(ranked_rows, start=1):
            leetcode_id = int(row["ID"])
            problem = db.scalar(
                select(Problem).where(
                    Problem.playlist_id == playlist.id,
                    Problem.leetcode_id == leetcode_id,
                )
            )
            if problem is None:
                problem = Problem(playlist_id=playlist.id, leetcode_id=leetcode_id)
                db.add(problem)

            problem.title = row["Title"].strip()
            problem.leetcode_url = row["URL"].strip()
            problem.difficulty = row["Difficulty"].strip()
            problem.acceptance_rate = percentage(row["Acceptance %"])
            problem.frequency = percentage(row["Frequency %"])
            problem.is_premium = False
            problem.position = position

        db.commit()

    return len(ranked_rows)


if __name__ == "__main__":
    imported_count = import_google_playlist()
    print(f"Imported {imported_count} Google problems into the google playlist.")