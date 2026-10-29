import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .config import settings

_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(_header)) -> None:
    # Fail closed: without API_KEY in .env the API serves no data (never open by mistake).
    if not settings.api_key:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "API_KEY is not configured in .env"
        )
    if not key or not secrets.compare_digest(key, settings.api_key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid X-API-Key")
