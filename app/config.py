from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_DIR / ".env", extra="ignore")

    # Chave exigida no header X-API-Key. Vazia = rotas de dados respondem 503 (falha fechada).
    api_key: str = ""
    google_credentials_file: Path = PROJECT_DIR / "secrets" / "credentials.json"
    google_token_file: Path = PROJECT_DIR / "secrets" / "token.json"
    host: str = "127.0.0.1"
    port: int = 8001


settings = Settings()

SCOPES = ["https://www.googleapis.com/auth/tasks"]
