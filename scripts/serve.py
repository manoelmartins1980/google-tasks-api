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
    sys.stdout = sys.stderr = open(log_dir / "api.log", "a", encoding="utf-8", buffering=1)
    uvicorn.run("app.main:app", host=settings.host, port=settings.port)
