from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import auth_guard, require_admin
from core.database import get_db
from core.jwt_handler import JwtHandler
from domains.users.repositories.users_auth_repository import UsersAuthRepository
from domains.users.schemas.users_schemas import (
    Token,
    UserLogin,
    UserProfile,
    UserRegister,
)
from domains.users.services.users_auth_service import UsersAuthService

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> UsersAuthService:
    return UsersAuthService(db, UsersAuthRepository(db), JwtHandler())


@router.get("/")
def route_check():
    return {"message": "User route"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    auth_service: UsersAuthService = Depends(get_auth_service),
) -> None:
    await auth_service.register(user_data)


@router.post("/login")
async def login_user(
    user_data: UserLogin,
    auth_service: UsersAuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(user_data)


@router.post("/register/admin", status_code=status.HTTP_201_CREATED)
async def register_admin(
    user_data: UserRegister,
    _admin: Annotated[dict, Depends(require_admin)],
    auth_service: UsersAuthService = Depends(get_auth_service),
) -> None:
    await auth_service.register(user_data, valid_admin=True)


@router.get("/me")
def get_profile(current_user: Annotated[dict, Depends(auth_guard)]) -> UserProfile:
    return current_user
