from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_DIR / ".env", extra="ignore")

    # Key required in the X-API-Key header. Empty = data routes answer 503 (fails closed).
    api_key: str = ""
    google_credentials_file: Path = PROJECT_DIR / "secrets" / "credentials.json"
    google_token_file: Path = PROJECT_DIR / "secrets" / "token.json"
    host: str = "127.0.0.1"
    port: int = 8001


settings = Settings()

SCOPES = ["https://www.googleapis.com/auth/tasks"]
