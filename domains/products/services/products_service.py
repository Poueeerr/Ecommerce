
from collections.abc import Sequence

from domains.inventory.models.inventory_model import InventoryModel
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.products.products_enums import ProductType
from domains.products.products_exceptions import ProductNotFound, ProductInvalidType
from domains.products.models.product_model import ProductModel
from domains.products.repositories.products_repository import ProductsRepository
from domains.products.schemas.products_schemas import Product, ProductRegister


class ProductsService:
    def __init__(
        self,
        products_repository: ProductsRepository,
        inventory_repository: InventoryRepository,
    ):
        self.products_repository = products_repository
        self.inventory_repository = inventory_repository
        
    async def register_product(self, product_data: ProductRegister) -> None:
        product = ProductModel(
            product_name=product_data.product_name,
            product_type=product_data.product_type,
            product_price=product_data.product_price,
            product_description=product_data.product_description,
        )

        result = await self.products_repository.register_product(product)
        inventory = InventoryModel(
            product_id=result.id,
            quantity=product_data.quantity,
            reserved_quantity=0,
        )
        await self.inventory_repository.register_inventory(inventory)

    async def get_all(self) -> Sequence[Product]:
        return await self.products_repository.get_all()

    async def get_by_category(self, category, offset, limit) -> Sequence[Product]:
        if category and category not in ProductType:
            raise ProductInvalidType()
        products = await self.products_repository.get_by_category(category, offset, limit)
        if not products:
            raise ProductNotFound
        return products