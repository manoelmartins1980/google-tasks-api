"""Inicia a API para uso diário (sem reload), com saída em logs/api.log.

Usado pela tarefa agendada (pythonw, sem console). Uso manual:
    python -m scripts.serve
"""

import sys

import uvicorn

from app.config import PROJECT_DIR, settings

if __name__ == "__main__":
    log_dir = PROJECT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    # pythonw não tem stdout/stderr; sem isto o logging do uvicorn falha ao iniciar
    # fica aberto durante toda a vida do processo, por isso sem `with`
    log = open(log_dir / "api.log", "a", encoding="utf-8", buffering=1)  # noqa: SIM115
    sys.stdout = sys.stderr = log
    uvicorn.run("app.main:app", host=settings.host, port=settings.port)
