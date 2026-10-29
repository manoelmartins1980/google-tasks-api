"""Start the API for daily use (no reload), writing output to logs/api.log.

Used by the scheduled task (pythonw, no console). Manual use:
    python -m scripts.serve
"""

import sys

import uvicorn

from app.config import PROJECT_DIR, settings

if __name__ == "__main__":
    log_dir = PROJECT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    # pythonw has no stdout/stderr; without this, Uvicorn's logging fails on startup
    # stays open for the whole life of the process, hence no `with`
    log = open(log_dir / "api.log", "a", encoding="utf-8", buffering=1)  # noqa: SIM115
    sys.stdout = sys.stderr = log
    uvicorn.run("app.main:app", host=settings.host, port=settings.port)
