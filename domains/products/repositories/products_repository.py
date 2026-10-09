from collections.abc import Sequence
from datetime import datetime, UTC
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.products.models.product_model import ProductModel
from domains.products.products_enums import ProductType


class ProductsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_product(self, product: ProductModel) -> ProductModel:
        self.db.add(product)
        await self.db.flush()
        return product

    async def get_all(self) -> Sequence[ProductModel]:
        result = await self.db.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.inventory))
            .where(ProductModel.deleted_at.is_(None))
        )
        return result.scalars().all()

    async def get_by_category(self, category: ProductType, offset: int, limit: int) -> Sequence[ProductModel]:
        query = select(ProductModel).options(selectinload(ProductModel.inventory))

        if category:
            query = query.where(ProductModel.product_type == category)

        query = query.where(ProductModel.deleted_at.is_(None))

        query = query.order_by(ProductModel.created_at, ProductModel.id)
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, id: uuid.UUID) -> ProductModel:
        query = (
            select(ProductModel)
            .options(selectinload(ProductModel.inventory))
            .where(ProductModel.id == id, ProductModel.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def save_update(self, product: ProductModel) -> ProductModel:
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def soft_delete(self, product: ProductModel) -> ProductModel:
        product.deleted_at = datetime.now(UTC)
        await self.db.commit()
        return product