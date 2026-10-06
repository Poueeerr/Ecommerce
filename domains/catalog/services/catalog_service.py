
from collections.abc import Sequence

from domains.catalog.catalog_enums import ProductType
from domains.catalog.catalog_exceptions import CatalogNotFound, ProductInvalidType
from domains.catalog.models.catalog_model import CatalogModel
from domains.catalog.repositories.catalog_repository import CatalogRepository
from domains.catalog.schemas.catalog_schemas import CatalogProduct, CatalogRegister


class CatalogService:
    def __init__(
        self,
        catalog_repository: CatalogRepository,
    ):
        self.catalog_repository = catalog_repository

    async def register_product(self, product_data: CatalogRegister) -> None:
        product = CatalogModel(
            product_name=product_data.product_name,
            product_type=product_data.product_type,
            product_price=product_data.product_price,
            product_description=product_data.product_description,
        )

        await self.catalog_repository.register_product(product)

    async def get_all(self) -> Sequence[CatalogProduct]:
        return await self.catalog_repository.get_all()

    async def get_by_category(self, category, offset, limit) -> Sequence[CatalogProduct]:
        if category and category not in ProductType:
            raise ProductInvalidType()
        products = await self.catalog_repository.get_by_category(category, offset, limit)
        if not products:
            raise CatalogNotFound
        return products