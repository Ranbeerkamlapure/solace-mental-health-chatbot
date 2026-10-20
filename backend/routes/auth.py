from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_user
from core.security import create_access_token
from models.user import user_to_public
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import ProfileUpdate, UserCreate, UserPublic
from services.auth_service import (
    DuplicateEmailError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
    update_username,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    try:
        return register_user(user)
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    try:
        user = authenticate_user(credentials.email, credentials.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    return TokenResponse(access_token=create_access_token(str(user["_id"])))


@router.get("/me", response_model=UserPublic)
def me(current_user: dict = Depends(get_current_user)):
    return user_to_public(current_user)


@router.patch("/me", response_model=UserPublic)
def update_me(body: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    return update_username(current_user["_id"], body.username)
