"""Autoriza a conta Google uma vez e grava secrets/token.json.

Uso (na pasta do projeto, com o .venv ativo):
    python -m scripts.authorize
"""

from app.config import settings
from app.google_client import run_oauth_flow

if __name__ == "__main__":
    if not settings.google_credentials_file.exists():
        raise SystemExit(f"Coloque o client OAuth em {settings.google_credentials_file}")
    run_oauth_flow()
    print(f"Token salvo em {settings.google_token_file}")
