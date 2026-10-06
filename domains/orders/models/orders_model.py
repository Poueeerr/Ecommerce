import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from domains.orders.orders_enums import OrderStatus

if TYPE_CHECKING:
    from domains.orders.models.order_item_model import OrderItemsModel
    from domains.users.models.users_model import UsersModel


class OrdersModel(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    total: Mapped[float]
    user: Mapped["UsersModel"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItemsModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            native_enum=False,
            values_callable=lambda enum: [m.value for m in enum],
        ),
        default=OrderStatus.PAYMENT_PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
