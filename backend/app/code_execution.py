from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass


MAX_CODE_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 64 * 1024
EXECUTION_TIMEOUT_SECONDS = 3
DOCKER_IMAGE = os.getenv("CODE_RUNNER_DOCKER_IMAGE", "python:3.12-slim")


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    stdout: str
    stderr: str
    execution_time_ms: int


class CodeExecutor:
    def run(self, code: str, language: str, stdin: str = "") -> ExecutionResult:
        raise NotImplementedError


class DockerPythonExecutor(CodeExecutor):
    def run(self, code: str, language: str, stdin: str = "") -> ExecutionResult:
        if language != "python":
            return ExecutionResult("error", "", "Only Python is supported.", 0)

        code_size = len(code.encode("utf-8"))
        if code_size > MAX_CODE_BYTES:
            return ExecutionResult("error", "", "Code size exceeds the allowed limit.", 0)

        docker_path = shutil.which("docker")
        if docker_path is None:
            return ExecutionResult(
                "error",
                "",
                "Secure code execution is unavailable. Install Docker and the configured runner image.",
                0,
            )

        container_name = f"codetutor-run-{uuid.uuid4().hex}"
        started_at = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="codetutor-run-") as workdir:
            source_path = os.path.join(workdir, "main.py")
            with open(source_path, "w", encoding="utf-8", newline="\n") as source_file:
                source_file.write(code)

            command = [
                docker_path,
                "run",
                "--rm",
                "--name",
                container_name,
                "--network",
                "none",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=16m",
                "--memory",
                "128m",
                "--cpus",
                "0.5",
                "--pids-limit",
                "64",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--user",
                "65534:65534",
                "--mount",
                f"type=bind,source={workdir},target=/runner,readonly",
                DOCKER_IMAGE,
                "python",
                "-I",
                "-S",
                "/runner/main.py",
            ]
            if stdin:
                command.insert(command.index(DOCKER_IMAGE), "-i")

            try:
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={"PATH": os.environ.get("PATH", "")},
                )
            except OSError:
                return ExecutionResult(
                    "error",
                    "",
                    "Secure code execution is unavailable. Docker could not start the sandbox.",
                    0,
                )

            stdout_buffer: list[bytes] = []
            stderr_buffer: list[bytes] = []
            output_limit_hit = threading.Event()

            def drain(pipe, buffer: list[bytes]) -> None:
                total = 0
                while True:
                    chunk = pipe.read(4096)
                    if not chunk:
                        return
                    remaining = MAX_OUTPUT_BYTES - total
                    if remaining > 0:
                        buffer.append(chunk[:remaining])
                        total += len(chunk[:remaining])
                    if total >= MAX_OUTPUT_BYTES:
                        output_limit_hit.set()

            stdout_thread = threading.Thread(target=drain, args=(process.stdout, stdout_buffer), daemon=True)
            stderr_thread = threading.Thread(target=drain, args=(process.stderr, stderr_buffer), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            try:
                if stdin:
                    process.stdin.write(stdin.encode("utf-8"))
                    process.stdin.close()
                process.wait(timeout=EXECUTION_TIMEOUT_SECONDS)
            except (BrokenPipeError, OSError):
                process.kill()
                process.wait()
                self._remove_container(docker_path, container_name)
                return ExecutionResult(
                    "error",
                    "",
                    "The secure sandbox could not accept the submitted code.",
                    self._elapsed_ms(started_at),
                )
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                self._remove_container(docker_path, container_name)
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                return ExecutionResult(
                    "timeout",
                    self._decode(stdout_buffer),
                    "Execution timed out and was terminated.",
                    self._elapsed_ms(started_at),
                )
            finally:
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)

            stdout = self._decode(stdout_buffer)
            stderr = self._decode(stderr_buffer)
            if process.returncode == 125:
                return ExecutionResult(
                    "error",
                    "",
                    "The secure sandbox could not start. Check Docker and the configured runner image.",
                    self._elapsed_ms(started_at),
                )
            if output_limit_hit.is_set():
                stderr = "Output exceeded the allowed limit and was truncated."
                return ExecutionResult("error", stdout, stderr, self._elapsed_ms(started_at))

            return ExecutionResult(
                "success" if process.returncode == 0 else "error",
                stdout,
                stderr,
                self._elapsed_ms(started_at),
            )

    @staticmethod
    def _decode(chunks: list[bytes]) -> str:
        return b"".join(chunks).decode("utf-8", errors="replace")

    @staticmethod
    def _elapsed_ms(started_at: float) -> int:
        return round((time.perf_counter() - started_at) * 1000)

    @staticmethod
    def _remove_container(docker_path: str, container_name: str) -> None:
        try:
            subprocess.run(
                [docker_path, "rm", "--force", container_name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass


code_executor: CodeExecutor = DockerPythonExecutor()