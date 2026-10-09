import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from domains.payments.payments_enums import PaymentsStatus

if TYPE_CHECKING:
    from domains.orders.models.orders_model import OrdersModel
    from domains.users.models.users_model import UsersModel


class PaymentsModel(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["OrdersModel"] = relationship(back_populates="payments")

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped["UsersModel"] = relationship(back_populates="payments")

    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    status: Mapped[PaymentsStatus] = mapped_column(
        Enum(
            PaymentsStatus,
            native_enum=False,
            values_callable=lambda enum: [m.value for m in enum],
        ),
        default=PaymentsStatus.PENDING,
    )

    provider_payment_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
