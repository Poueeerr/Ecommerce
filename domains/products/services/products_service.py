import uuid
from collections.abc import Sequence

from domains.products.models.product_model import ProductModel
from domains.products.products_enums import ProductType
from domains.products.products_exceptions import ProductInvalidType, ProductNotFound
from domains.products.repositories.products_repository import ProductsRepository
from domains.products.schemas.products_schemas import ProductCreate, ProductUpdate


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

    async def get_by_category(
        self,
        category,
        offset,
        limit,
        min_price=None,
        max_price=None,
    ) -> Sequence[ProductModel]:
        if category and category not in ProductType:
            raise ProductInvalidType()
        products = await self.products_repository.get_by_category(
            category,
            offset,
            limit,
            min_price,
            max_price,
        )
        if not products:
            raise ProductNotFound
        return products

    async def edit_product(
        self, product_data: ProductUpdate, product_id: uuid.UUID
    ) -> ProductModel:
        product = await self.products_repository.get_by_id(product_id)

        if not product:
            raise ProductNotFound(f"Product for id: {product_id} not found")

        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        return await self.products_repository.save_update(product)

    async def delete_product(self, product_id: uuid.UUID) -> None:
        product = await self.products_repository.get_by_id(product_id)

        if not product:
            raise ProductNotFound(f"Product for id: {product_id} not found")

        await self.products_repository.soft_delete(product)
