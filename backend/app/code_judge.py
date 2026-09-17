from __future__ import annotations

import time
from dataclasses import dataclass

from app.code_execution import CodeExecutor, ExecutionResult
from app.models import ProblemTestCase


@dataclass(frozen=True)
class JudgedTestCase:
    position: int
    is_sample: bool
    passed: bool
    input_data: str | None
    expected_output: str | None
    actual_output: str | None
    error: str | None


@dataclass(frozen=True)
class JudgeResult:
    status: str
    passed: int
    total: int
    execution_time_ms: int
    test_cases: list[JudgedTestCase]


def normalize_output(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.strip().splitlines())


def build_harness(code: str) -> str:
    return f"""{code}

import json as _codetutor_json

_codetutor_payload = _codetutor_json.loads(input())
_codetutor_result = solution(
    *_codetutor_payload.get("args", []),
    **_codetutor_payload.get("kwargs", {{}}),
)
print(_codetutor_json.dumps(_codetutor_result, separators=(",", ":")))
"""


def judge_submission(
    executor: CodeExecutor,
    code: str,
    language: str,
    test_cases: list[ProblemTestCase],
) -> JudgeResult:
    started_at = time.perf_counter()
    results: list[JudgedTestCase] = []
    passed_count = 0

    for test_case in test_cases:
        execution: ExecutionResult = executor.run(
            build_harness(code),
            language,
            stdin=f"{test_case.input_data}\n",
        )

        if execution.status == "timeout":
            results.append(
                JudgedTestCase(
                    position=test_case.position,
                    is_sample=test_case.is_sample,
                    passed=False,
                    input_data=test_case.input_data if test_case.is_sample else None,
                    expected_output=test_case.expected_output if test_case.is_sample else None,
                    actual_output=None,
                    error="Time limit exceeded.",
                )
            )
            return JudgeResult("timeout", passed_count, len(test_cases), _elapsed_ms(started_at), results)

        if execution.status != "success":
            results.append(
                JudgedTestCase(
                    position=test_case.position,
                    is_sample=test_case.is_sample,
                    passed=False,
                    input_data=test_case.input_data if test_case.is_sample else None,
                    expected_output=test_case.expected_output if test_case.is_sample else None,
                    actual_output=execution.stdout if test_case.is_sample else None,
                    error=(execution.stderr or "Runtime error.") if test_case.is_sample else "Hidden test failed.",
                )
            )
            return JudgeResult("runtime_error", passed_count, len(test_cases), _elapsed_ms(started_at), results)

        passed = normalize_output(execution.stdout) == normalize_output(test_case.expected_output)
        if passed:
            passed_count += 1

        results.append(
            JudgedTestCase(
                position=test_case.position,
                is_sample=test_case.is_sample,
                passed=passed,
                input_data=test_case.input_data if test_case.is_sample else None,
                expected_output=test_case.expected_output if test_case.is_sample else None,
                actual_output=execution.stdout if test_case.is_sample else None,
                error=None if passed or test_case.is_sample else "Hidden test failed.",
            )
        )

        if not passed:
            return JudgeResult("wrong_answer", passed_count, len(test_cases), _elapsed_ms(started_at), results)

    return JudgeResult("accepted", passed_count, len(test_cases), _elapsed_ms(started_at), results)


def _elapsed_ms(started_at: float) -> int:
    return round((time.perf_counter() - started_at) * 1000)
