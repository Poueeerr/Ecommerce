import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from domains.catalog.catalog_enums import ProductType


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CatalogRegister(_FromModel):
    product_name: str
    product_type: ProductType
    product_price: float
    product_description: str


class CatalogProduct(CatalogRegister):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class PaginatedProduct(BaseModel):
    products: list[CatalogProduct]
    len_products: int
    next_offset: int | None = None
