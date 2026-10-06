import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from domains.products.products_enums import ProductType


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    product_name: str
    product_type: ProductType
    product_price: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=[99.90],
    )
    product_description: str


class ProductRegister(ProductCreate):
    quantity: int = Field(ge=0)

class Product(_FromModel):
    id: uuid.UUID
    product_name: str
    product_type: ProductType
    product_price: Decimal = Field(examples=[99.90])
    product_description: str
    stock_quantity: int
    created_at: datetime
    updated_at: datetime

class PaginatedProduct(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "products": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "product_name": "Creatina monohidratada",
                        "product_type": "creatine",
                        "product_price": 99.90,
                        "product_description": "Creatina pura",
                        "stock_quantity": 20,
                        "created_at": "2026-10-06T10:26:56.942Z",
                        "updated_at": "2026-10-06T10:26:56.942Z",
                    }
                ],
                "len_products": 1,
                "next_offset": 10,
            }
        }
    )
    products: list[Product]
    len_products: int
    next_offset: int | None = None
