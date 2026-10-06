from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.jwt_handler import JwtHandler
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import AdminRequired, InvalidToken

jwt_handler = JwtHandler()
security_scheme = HTTPBearer()


async def auth_guard(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
) -> dict:
    try:
        return jwt_handler.validate_access_token(credentials.credentials)
    except jwt.InvalidTokenError as exc:
        raise InvalidToken from exc


async def require_admin(
    current_user: Annotated[dict, Depends(auth_guard)],
) -> dict:
    if current_user["role"] != UserRole.ADMIN:
        raise AdminRequired
    return current_user
