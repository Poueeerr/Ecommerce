import uuid

from pydantic import BaseModel, ConfigDict


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaymentsSchema(_FromModel):
    id: uuid.UUID


class PaymentWebhookData(BaseModel):
    id: str


class PaymentWebhook(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | int | None = None
    type: str
    action: str | None = None
    data: PaymentWebhookData