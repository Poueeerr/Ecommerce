from decimal import Decimal

from pydantic import BaseModel, Field


class MercadoPagoItem(BaseModel):
    id: str
    title: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    currency_id: str = "BRL"


class MercadoPagoPayer(BaseModel):
    email: str


class MercadoPagoPreference(BaseModel):
    items: list[MercadoPagoItem]
    payer: MercadoPagoPayer
    external_reference: str
    notification_url: str