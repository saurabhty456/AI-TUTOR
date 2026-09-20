import unittest

from sqlalchemy import select

from app.code_judge import build_harness, judge_submission, run_problem_code
from app.code_execution import code_executor
from app.database import SessionLocal
from app.models import Problem, ProblemExecutionSpec


CORRECT_SOLUTION = """def twoSum(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return [seen[complement], index]
        seen[value] = index
    return []
"""
WRONG_SOLUTION = """def twoSum(nums, target):
    return []
"""
RUNTIME_ERROR = """def twoSum(nums, target):
    raise RuntimeError('intentional test error')
"""
TIMEOUT = """def twoSum(nums, target):
    while True:
        pass
"""


class FunctionHarnessRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SessionLocal() as db:
            cls.problem = db.scalar(select(Problem).where(Problem.leetcode_id == 1))
            if cls.problem is None or cls.problem.execution_spec is None:
                raise unittest.SkipTest("Google Two Sum execution fixtures are not seeded")
            cls.spec = db.scalar(
                select(ProblemExecutionSpec).where(
                    ProblemExecutionSpec.problem_id == cls.problem.id,
                    ProblemExecutionSpec.language == "python",
                )
            )
            cls.test_cases = list(cls.problem.test_cases)

    def test_harness_uses_configured_function_name(self):
        harness = build_harness("def twoSum(nums, target):\n    return []", self.spec)
        self.assertIn("_codetutor_result = twoSum(", harness)
        self.assertNotIn("_codetutor_result = solution(", harness)

    def test_starter_code_executes_without_name_error(self):
        sample = next(test_case for test_case in self.test_cases if test_case.is_sample)
        result = run_problem_code(code_executor, self.spec.starter_code, "python", self.spec, sample.input_data)
        self.assertNotEqual(result.status, "runtime_error")
        self.assertNotIn("NameError", result.stderr)

    def test_correct_solution_is_accepted(self):
        result = judge_submission(code_executor, CORRECT_SOLUTION, "python", self.spec, self.test_cases)
        self.assertEqual((result.status, result.passed, result.total), ("accepted", 8, 8))

    def test_wrong_solution_is_rejected(self):
        result = judge_submission(code_executor, WRONG_SOLUTION, "python", self.spec, self.test_cases)
        self.assertEqual(result.status, "wrong_answer")

    def test_runtime_error_is_classified(self):
        result = judge_submission(code_executor, RUNTIME_ERROR, "python", self.spec, self.test_cases)
        self.assertEqual(result.status, "runtime_error")

    def test_infinite_loop_times_out(self):
        result = judge_submission(code_executor, TIMEOUT, "python", self.spec, self.test_cases)
        self.assertEqual(result.status, "timeout")


if __name__ == "__main__":
    unittest.main()
