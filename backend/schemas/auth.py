from pydantic import BaseModel, EmailStr, Field, field_validator

from schemas.user import normalize_email


class LoginRequest(BaseModel):
    email: EmailStr
    # Only a sanity bound here; the password policy applies at registration.
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return normalize_email(value)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
