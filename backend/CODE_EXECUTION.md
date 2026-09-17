# Code execution

Phase 5D executes Python only inside Docker. The FastAPI process never imports or runs submitted code.

The runner uses a fixed Docker command with:

- no network access
- a read-only root filesystem
- a small writable, non-executable `/tmp`
- dropped Linux capabilities and `no-new-privileges`
- an unprivileged user
- memory, CPU, process-count, timeout, code-size, and output-size limits
- no application files, database files, or environment secrets mounted into the container

Docker must already be installed and running. The configured image must be available locally; the application does not pull images at request time. Set `CODE_RUNNER_DOCKER_IMAGE` in `backend/.env` if using an approved, pinned local image.

When Docker is unavailable, `/code/run` fails closed with a controlled error response. It does not fall back to Windows or in-process Python execution.