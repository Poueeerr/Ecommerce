from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.orders.repositories.orders_repository import OrdersRepository
from domains.payments.adapters.mercadopago import MercadoPagoAdapter
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.services.payments_service import PaymentsService


def get_payments_service(
    session: AsyncSession = Depends(get_db),
) -> PaymentsService:
    payments_repository = PaymentsRepository(session)
    orders_repository = OrdersRepository(session)
    payment_adapter = MercadoPagoAdapter()

    return PaymentsService(
        session=session,
        payments_repository=payments_repository,
        orders_repository=orders_repository,
        payment_adapter=payment_adapter,
    )