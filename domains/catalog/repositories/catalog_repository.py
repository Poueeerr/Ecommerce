from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.catalog.models.catalog_model import CatalogModel


class CatalogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_product(self, product: CatalogModel) -> CatalogModel:
        try:
            self.db.add(product)
            await self.db.commit()
            await self.db.refresh(product)
            return product
        except Exception:
            await self.db.rollback()
            raise

    async def get_all(self) -> Sequence[CatalogModel]:
        result = await self.db.execute(select(CatalogModel))
        return result.scalars().all()

    async def get_by_category(self, category, offset, limit) -> Sequence[CatalogModel]:
        query = select(CatalogModel)

        if category:
            query = query.where(CatalogModel.product_type == category)

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()