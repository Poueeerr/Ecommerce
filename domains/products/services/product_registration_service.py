from sqlalchemy.ext.asyncio import AsyncSession

from domains.inventory.services.inventory_service import InventoryService
from domains.products.models.product_model import ProductModel
from domains.products.schemas.products_schemas import ProductCreate, ProductRegister
from domains.products.services.products_service import ProductsService


class ProductRegistrationService:
    def __init__(
        self,
        db: AsyncSession,
        products_service: ProductsService,
        inventory_service: InventoryService,
    ):
        self.db = db
        self.products_service = products_service
        self.inventory_service = inventory_service

    async def register(self, product_data: ProductRegister) -> ProductModel:
        try:
            product = await self.products_service.register_product(
                ProductCreate(**product_data.model_dump(exclude={"quantity"}))
            )
            await self.inventory_service.register_for_product(
                product.id,
                product_data.quantity,
            )
            await self.db.commit()
            return product
        except Exception:
            await self.db.rollback()
            raise
