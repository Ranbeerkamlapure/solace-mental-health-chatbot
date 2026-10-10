"""Password hashing (Argon2id) and JWT access tokens."""
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET

# argon2-cffi's PasswordHasher uses Argon2id by default.
_password_hasher = PasswordHasher()

_ACCESS_TOKEN_TYPE = "access"
_CLOCK_SKEW_LEEWAY_SECONDS = 10


class TokenError(Exception):
    """Raised when a JWT is invalid, expired, or of the wrong type."""


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return _password_hasher.verify(hashed_password, password)
    except (VerificationError, InvalidHashError):
        # VerifyMismatchError is a subclass of VerificationError.
        return False


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": _ACCESS_TOKEN_TYPE,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Return the verified payload, or raise TokenError."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp"]},
            leeway=_CLOCK_SKEW_LEEWAY_SECONDS,
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    if payload.get("type") != _ACCESS_TOKEN_TYPE:
        raise TokenError("Wrong token type")
    if not isinstance(payload.get("sub"), str) or not payload["sub"]:
        raise TokenError("Invalid subject")
    return payload
