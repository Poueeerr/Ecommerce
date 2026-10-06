import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from domains.products.products_enums import ProductType


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    product_name: str
    product_type: ProductType
    product_price: float = Field(gt=0)
    product_description: str


class ProductRegister(ProductCreate):
    quantity: int = Field(ge=0)

class Product(_FromModel):
    id: uuid.UUID
    product_name: str
    product_type: ProductType
    product_price: float
    product_description: str
    stock_quantity: int
    created_at: datetime
    updated_at: datetime

class PaginatedProduct(BaseModel):
    products: list[Product]
    len_products: int
    next_offset: int | None = None
