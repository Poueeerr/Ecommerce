from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.jwt_handler import JwtHandler
from domains.users.users_exceptions import InvalidToken

jwt_handler = JwtHandler()
security_scheme = HTTPBearer()


async def auth_guard(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
) -> dict:
    try:
        return jwt_handler.validate_access_token(credentials.credentials)
    except jwt.InvalidTokenError as exc: 
        raise InvalidToken from exc
