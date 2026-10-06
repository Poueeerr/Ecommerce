
from collections.abc import Sequence

from domains.products.products_enums import ProductType
from domains.products.products_exceptions import ProductNotFound, ProductInvalidType
from domains.products.models.product_model import ProductModel
from domains.products.repositories.products_repository import ProductsRepository
from domains.products.schemas.products_schemas import ProductCreate


class ProductsService:
    def __init__(
        self,
        products_repository: ProductsRepository,
    ):
        self.products_repository = products_repository

    async def register_product(self, product_data: ProductCreate) -> ProductModel:
        product = ProductModel(
            product_name=product_data.product_name,
            product_type=product_data.product_type,
            product_price=product_data.product_price,
            product_description=product_data.product_description,
        )

        return await self.products_repository.register_product(product)

    async def get_all(self) -> Sequence[ProductModel]:
        return await self.products_repository.get_all()

    async def get_by_category(self, category, offset, limit) -> Sequence[ProductModel]:
        if category and category not in ProductType:
            raise ProductInvalidType()
        products = await self.products_repository.get_by_category(category, offset, limit)
        if not products:
            raise ProductNotFound
        return products