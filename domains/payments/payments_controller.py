from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import require_admin, auth_guard
from core.database import get_db
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.services.payments_service import PaymentsService

router = APIRouter()


def get_payments_service(db: AsyncSession = Depends(get_db)) -> PaymentsService:
    return PaymentsService(
        PaymentsRepository(db),
    )

@router.get("/")
def route_check():
    return {"message": "Payments"}

