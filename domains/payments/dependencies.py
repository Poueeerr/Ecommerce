from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.services.payments_service import PaymentsService


def get_payments_service(db: AsyncSession = Depends(get_db)) -> PaymentsService:
    return PaymentsService(PaymentsRepository(db))
