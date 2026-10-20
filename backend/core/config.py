"""Application configuration, read from environment variables (and .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

_ALLOWED_JWT_ALGORITHMS = {"HS256", "HS384", "HS512"}


def _require(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            "Copy backend/.env.example to backend/.env and set it."
        )
    return value


MONGODB_URI: str = _require("MONGODB_URI")
MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "Solace")

JWT_SECRET: str = _require("JWT_SECRET")
if len(JWT_SECRET) < 32:
    raise RuntimeError(
        "JWT_SECRET must be at least 32 characters. Generate one with: "
        'python -c "import secrets; print(secrets.token_urlsafe(48))"'
    )

JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256").strip()
if JWT_ALGORITHM not in _ALLOWED_JWT_ALGORITHMS:
    raise RuntimeError(
        f"JWT_ALGORITHM must be one of {sorted(_ALLOWED_JWT_ALGORITHMS)}."
    )

try:
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
except ValueError:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer.") from None
if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0.")

CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

# Optional. When set, chat replies come from Groq. Crisis phrases still use the fixed reply.
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b"
