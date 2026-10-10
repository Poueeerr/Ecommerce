from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from core.database import get_db
from domains.payments.payments_controller import get_payments_service
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.schemas.payments_schema import PaymentWebhook
from domains.payments.services.payments_service import PaymentsService

router = APIRouter()

def get_payments_service(db: AsyncSession = Depends(get_db)) -> PaymentsService:
    return PaymentsService(
        PaymentsRepository(db),
    )

@router.post("/webhook/payment-update")
async def payment_update(
    payment_update_data: PaymentWebhook,
    payments_service: PaymentsService = Depends(get_payments_service),
):
    # Verificar o webhook, atualizar o pagamento e a ordem e criar o shipping.
    return {"message": "Payment atualizado"}
