from decimal import Decimal
import uuid

from domains.inventory.inventory_exceptions import InventoryNotFound, InsufficientStock
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.orders.models.order_item_model import OrderItemsModel
from domains.orders.models.orders_model import OrdersModel
from domains.orders.orders_enums import OrderStatus
from domains.orders.repository.orders_repository import OrdersRepository
from domains.orders.schemas.orders_schemas import CreateOrder
from domains.products.products_exceptions import ProductNotFound
from domains.products.repositories.products_repository import ProductsRepository
from sqlalchemy.ext.asyncio import AsyncSession


class OrdersService:
    def __init__(self, db: AsyncSession, orders_repository: OrdersRepository, products_repository: ProductsRepository, inventory_repository : InventoryRepository):
        self.db = db
        self.orders_repository = orders_repository
        self.inventory_repository = inventory_repository
        self.products_repository = products_repository

    async def create_order(self, order_data: CreateOrder, current_user: dict) -> OrdersModel:
        async with self.db.begin():

            order = OrdersModel(
                user_id=uuid.UUID(current_user["sub"]),
                total=Decimal("0"),
                status=OrderStatus.PAYMENT_PENDING,
            )

            total=Decimal("0") 

            for item_data in order_data.items:
                product = await self.products_repository.get_by_id(item_data.product_id)

                if product is None:
                    raise ProductNotFound() 

                product_inventory = await self.inventory_repository.get_item_by_product_id(product.id)

                if product_inventory is None:
                    raise InventoryNotFound() 

                available_stock = product_inventory.quantity - product_inventory.reserved_quantity
                if available_stock < item_data.quantity:
                    raise InsufficientStock()

                item_price_total = product.product_price * item_data.quantity
                total += item_price_total

                product_inventory.reserved_quantity += item_data.quantity
                
                order.order_items.append(
                    OrderItemsModel(
                        product_id=product.id,
                        quantity=item_data.quantity,
                        unit_price=product.product_price
                    )
                )
            order.total = total
            
            await self.orders_repository.save_order(order)
            return order