"""Authorize the Google account once and write secrets/token.json.

Usage (from the project folder, with the .venv active):
    python -m scripts.authorize
"""

from app.config import settings
from app.google_client import run_oauth_flow

if __name__ == "__main__":
    if not settings.google_credentials_file.exists():
        raise SystemExit(f"Put the OAuth client in {settings.google_credentials_file}")
    run_oauth_flow()
    print(f"Token saved to {settings.google_token_file}")
