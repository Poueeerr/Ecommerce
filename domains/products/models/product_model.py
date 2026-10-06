from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from domains.inventory.models.inventory_model import InventoryModel
from domains.orders.models.order_item_model import OrderItemsModel
from domains.products.products_enums import ProductType


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    product_name: Mapped[str]
    product_price: Mapped[float]
    product_type: Mapped[ProductType] = mapped_column(
        Enum(
            ProductType,
            native_enum=False,  
            values_callable=lambda enum: [m.value for m in enum], 
        ),
        default=ProductType.GENERIC,
    )
    product_description: Mapped[str]
    order_items: Mapped[list[OrderItemsModel]] = relationship(
        back_populates="product"
    )
    inventory: Mapped[list["InventoryModel"]] = relationship(
        back_populates="product"
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
