from datetime import datetime
import uuid

from sqlalchemy import Enum, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from domains.catalog.catalog_enums import ProductType


class CatalogModel(Base):
    __tablename__ = "catalog"

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
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
