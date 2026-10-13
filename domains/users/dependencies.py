from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_handler import JwtHandler
from domains.users.repositories.users_auth_repository import UsersAuthRepository
from domains.users.services.users_auth_service import UsersAuthService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> UsersAuthService:
    return UsersAuthService(db, UsersAuthRepository(db), JwtHandler())
