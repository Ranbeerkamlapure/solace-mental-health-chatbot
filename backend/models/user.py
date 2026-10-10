"""MongoDB `users` document helpers."""
from datetime import datetime, timezone

from schemas.user import UserPublic


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_user_document(username: str, email: str, password_hash: str) -> dict:
    now = utcnow()
    return {
        "username": username,
        "email": email,  # already normalized to lowercase
        "password_hash": password_hash,
        "role": "user",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,  # set on first successful login
    }


def user_to_public(doc: dict) -> UserPublic:
    """Convert a stored document to the safe public shape (no password data)."""
    return UserPublic(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"],
        role=doc.get("role", "user"),
        created_at=doc["created_at"],
    )
