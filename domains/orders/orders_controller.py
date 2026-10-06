from typing import Annotated
from fastapi import APIRouter, Depends

from api.middlewares.auth_guard import auth_guard
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import AdminRequired

router = APIRouter()

def require_admin(current_user: Annotated[dict, Depends(auth_guard)]) -> dict:
    if current_user["role"] != UserRole.ADMIN:
        raise AdminRequired
    return current_user


@router.get("/")
def route_check():
    return {"message": "Orders route"}
