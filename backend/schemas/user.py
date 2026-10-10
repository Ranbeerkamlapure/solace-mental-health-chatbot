import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints, field_validator

Username = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
]

# Max length also protects the server from very expensive hashing of huge inputs.
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserCreate(BaseModel):
    username: Username
    email: EmailStr
    password: Password

    @field_validator("username")
    @classmethod
    def collapse_whitespace(cls, value: str) -> str:
        return re.sub(r"\s+", " ", value)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return normalize_email(value)


class UserPublic(BaseModel):
    """Safe user representation. Must never contain password data."""

    id: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime
