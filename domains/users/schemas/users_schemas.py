import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from domains.users.users_enums import UserRole


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserLogin):
    name: str
    password: str = Field(min_length=8, max_length=100)


class UserProfile(_FromModel):
    name: str
    email: EmailStr
    role: UserRole


class UserResponse(UserProfile):
    id: uuid.UUID
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
