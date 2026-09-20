import json

from sqlalchemy import delete, select

from app.database import SessionLocal, initialize_database
from app.models import Problem, ProblemExecutionSpec, ProblemReferenceSolution, ProblemTestCase


TEST_CASES = [
    ({"args": [[2, 7, 11, 15], 9], "kwargs": {}}, [0, 1], "normal", "Pair appears at the beginning.", True),
    ({"args": [[3, 2, 4], 6], "kwargs": {}}, [1, 2], "normal", "The complement appears later.", True),
    ({"args": [[3, 3], 6], "kwargs": {}}, [0, 1], "duplicate_values", "Equal values may form the pair.", False),
    ({"args": [[-3, 4, 3, 90], 0], "kwargs": {}}, [0, 2], "mixed_signs", "Negative and positive values can cancel.", False),
    ({"args": [[0, 4, 3, 0], 0], "kwargs": {}}, [0, 3], "zero_values", "Zero is a valid value and target.", False),
    ({"args": [[1, 2], 100], "kwargs": {}}, [], "no_solution", "No pair sums to the target.", False),
    ({"args": [[1, 5, 8, 12], 13], "kwargs": {}}, [1, 2], "multiple_solutions", "The reference solution returns the first pair found by its scan order.", False),
    ({"args": [[-1000000, 1000000, 4], 0], "kwargs": {}}, [0, 1], "large_values", "Large magnitudes must remain exact.", False),
]


def seed_google_two_sum_test_cases() -> int:
    initialize_database()
    with SessionLocal() as db:
        problem = db.scalar(select(Problem).where(Problem.leetcode_id == 1))
        if problem is None:
            raise RuntimeError("Google Two Sum is not imported; run the Google importer first.")

        spec = db.scalar(select(ProblemExecutionSpec).where(ProblemExecutionSpec.problem_id == problem.id))
        if spec is None:
            spec = ProblemExecutionSpec(
                problem_id=problem.id,
                language="python",
                execution_type="function",
                function_name="twoSum",
                starter_code="def twoSum(nums, target):\n    return []",
                input_format="JSON object with args: [nums, target]",
                output_format="JSON array of two indices",
            )
            db.add(spec)
        else:
            spec.function_name = "twoSum"
            spec.starter_code = "def twoSum(nums, target):\n    return []"
        reference = db.scalar(select(ProblemReferenceSolution).where(ProblemReferenceSolution.problem_id == problem.id, ProblemReferenceSolution.language == "python"))
        if reference is None:
            db.add(ProblemReferenceSolution(
                problem_id=problem.id,
                language="python",
                source_code="def solution(nums, target):\n    seen = {}\n    for index, value in enumerate(nums):\n        complement = target - value\n        if complement in seen:\n            return [seen[complement], index]\n        seen[value] = index\n    return []",
            ))

        db.execute(delete(ProblemTestCase).where(ProblemTestCase.problem_id == problem.id))

        for position, (input_data, expected_output, category, explanation, is_sample) in enumerate(TEST_CASES, start=1):
            db.add(
                ProblemTestCase(
                    problem_id=problem.id,
                    input_data=json.dumps(input_data, separators=(",", ":")),
                    expected_output=json.dumps(expected_output, separators=(",", ":")),
                    category=category,
                    difficulty_level="medium" if category in {"multiple_solutions", "no_solution"} else "easy",
                    explanation=explanation,
                    is_sample=is_sample,
                    position=position,
                )
            )
        db.commit()
        return len(TEST_CASES)


if __name__ == "__main__":
    print(f"Seeded {seed_google_two_sum_test_cases()} CodeTutor-authored Google Two Sum test cases.")
