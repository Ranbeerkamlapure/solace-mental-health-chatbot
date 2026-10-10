"""Registration and authentication logic."""
import secrets

from pymongo.errors import DuplicateKeyError

from core.security import hash_password, verify_password
from database import users_collection
from models.user import new_user_document, user_to_public, utcnow
from schemas.user import UserCreate, UserPublic, normalize_email


class DuplicateEmailError(Exception):
    """An account with this email already exists."""


class InvalidCredentialsError(Exception):
    """Wrong email or password (deliberately does not say which)."""


# Verified against when the email is unknown, so "unknown email" and
# "wrong password" take similar time and can't be told apart by timing.
_DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def register_user(data: UserCreate) -> UserPublic:
    email = normalize_email(data.email)
    document = new_user_document(
        username=data.username,
        email=email,
        password_hash=hash_password(data.password),
    )
    try:
        result = users_collection.insert_one(document)
    except DuplicateKeyError:
        raise DuplicateEmailError from None

    document["_id"] = result.inserted_id
    return user_to_public(document)


def authenticate_user(email: str, password: str) -> dict:
    """Return the user document on success, else raise InvalidCredentialsError."""
    user = users_collection.find_one({"email": normalize_email(email)})

    stored_hash = user.get("password_hash") if user else None
    if not user or not stored_hash:
        verify_password(password, _DUMMY_HASH)
        raise InvalidCredentialsError

    if not verify_password(password, stored_hash) or not user.get("is_active", False):
        raise InvalidCredentialsError

    now = utcnow()
    users_collection.update_one({"_id": user["_id"]}, {"$set": {"last_login_at": now}})
    user["last_login_at"] = now
    return user
