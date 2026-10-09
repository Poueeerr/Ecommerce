import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from domains.products.schemas.products_schemas import Product


class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class InventorySchema(_FromModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product: Product
    total_quantity: int
    reserved_quantity: int
    created_at: datetime
    updated_at: datetime
