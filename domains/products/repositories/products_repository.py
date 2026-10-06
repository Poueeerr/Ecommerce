from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.products.models.product_model import ProductModel


class ProductsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_product(self, product: ProductModel) -> ProductModel:
        self.db.add(product)
        await self.db.flush()
        return product

    async def get_all(self) -> Sequence[ProductModel]:
        result = await self.db.execute(
            select(ProductModel).options(selectinload(ProductModel.inventory))
        )
        return result.scalars().all()

    async def get_by_category(self, category, offset, limit) -> Sequence[ProductModel]:
        query = select(ProductModel).options(selectinload(ProductModel.inventory))

        if category:
            query = query.where(ProductModel.product_type == category)

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
