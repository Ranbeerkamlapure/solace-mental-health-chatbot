"""FastAPI dependencies."""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.security import TokenError, decode_access_token
from database import users_collection

# auto_error=False so we always return our own 401 (not the framework default).
_bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """Resolve the authenticated user from the Bearer token, or raise 401."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = ObjectId(payload["sub"])
    except (TokenError, InvalidId, TypeError):
        raise _unauthorized() from None

    user = users_collection.find_one({"_id": user_id})
    if user is None or not user.get("is_active", False):
        raise _unauthorized()
    return user
