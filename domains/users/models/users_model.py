import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from domains.users.users_enums import UserRole

if TYPE_CHECKING:
    from domains.orders.models.orders_model import OrdersModel


class UsersModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            native_enum=False,  
            values_callable=lambda enum: [m.value for m in enum], 
        ),
        default=UserRole.USER,
    )
    orders: Mapped[list["OrdersModel"]] = relationship(back_populates="user")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
