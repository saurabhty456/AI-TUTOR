import json

from sqlalchemy import select

from app.database import SessionLocal, initialize_database
from app.models import Problem, ProblemTestCase


TEST_CASES = [
    ({"args": [[2, 7, 11, 15], 9], "kwargs": {}}, [0, 1], True),
    ({"args": [[3, 2, 4], 6], "kwargs": {}}, [1, 2], True),
    ({"args": [[3, 3], 6], "kwargs": {}}, [0, 1], False),
    ({"args": [[1, 5, 8, 12], 13], "kwargs": {}}, [0, 3], False),
    ({"args": [[10, 20, 30, 40], 70], "kwargs": {}}, [2, 3], False),
]


def seed_google_two_sum_test_cases() -> int:
    initialize_database()
    with SessionLocal() as db:
        problem = db.scalar(select(Problem).where(Problem.leetcode_id == 1))
        if problem is None:
            raise RuntimeError("Google Two Sum is not imported; run the Google importer first.")

        if problem.test_cases:
            return len(problem.test_cases)

        for position, (input_data, expected_output, is_sample) in enumerate(TEST_CASES, start=1):
            db.add(
                ProblemTestCase(
                    problem_id=problem.id,
                    input_data=json.dumps(input_data, separators=(",", ":")),
                    expected_output=json.dumps(expected_output, separators=(",", ":")),
                    is_sample=is_sample,
                    position=position,
                )
            )
        db.commit()
        return len(TEST_CASES)


if __name__ == "__main__":
    print(f"Seeded {seed_google_two_sum_test_cases()} CodeTutor-authored Google Two Sum test cases.")
