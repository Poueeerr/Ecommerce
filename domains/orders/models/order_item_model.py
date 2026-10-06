import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from domains.orders.models.orders_model import OrdersModel
    from domains.products.models.product_model import ProductModel


class OrderItemsModel(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    quantity: Mapped[int]
    unit_price: Mapped[int]
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["OrdersModel"] = relationship(back_populates="order_items")
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    product: Mapped["ProductModel"] = relationship(back_populates="order_items")