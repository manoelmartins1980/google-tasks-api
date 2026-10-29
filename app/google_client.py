"""OAuth credentials and Google Tasks API client."""

from functools import lru_cache

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import SCOPES, settings


def run_oauth_flow() -> Credentials:
    """Open the browser to authorize the Google account and save the token."""
    flow = InstalledAppFlow.from_client_secrets_file(str(settings.google_credentials_file), SCOPES)
    creds = flow.run_local_server(port=0)
    _save(creds)
    return creds


def load_credentials() -> Credentials:
    token_file = settings.google_token_file
    if not token_file.exists():
        raise RuntimeError("Token not found. Run `python -m scripts.authorize` first.")
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _save(creds)
        else:
            raise RuntimeError("Invalid token. Run `python -m scripts.authorize` again.")
    return creds


def _save(creds: Credentials) -> None:
    settings.google_token_file.parent.mkdir(parents=True, exist_ok=True)
    settings.google_token_file.write_text(creds.to_json(), encoding="utf-8")


@lru_cache
def _service():
    return build("tasks", "v1", credentials=load_credentials(), cache_discovery=False)


def tasks_service():
    """FastAPI dependency: return the client, refreshing the token if it expired."""
    svc = _service()
    creds = svc._http.credentials
    if not creds.valid:
        _service.cache_clear()
        svc = _service()
    return svc
