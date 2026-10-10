import uuid

from pydantic import BaseModel, ConfigDict


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaymentsSchema(_FromModel):
    id: uuid.UUID

class PaymentWebhook(BaseModel):
    provider_payment_id: str
    #Resto das informações retornadas pelo gateway