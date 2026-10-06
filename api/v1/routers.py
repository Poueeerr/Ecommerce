# api/v1/router.py
from fastapi import APIRouter

from domains.products.products_controller import router as products_controller
from domains.health.health_controller import router as health_controller
from domains.users.users_controller import router as users_controller
from domains.orders.orders_controller import router as orders_controllers
from domains.inventory.inventory_controller import router as inventory_controller

router = APIRouter()
router.include_router(health_controller, tags=["health"])
router.include_router(users_controller, prefix="/users", tags=["users"])
router.include_router(products_controller, prefix="/products", tags=["products"])
router.include_router(orders_controllers, prefix="/orders", tags=["orders"])
router.include_router(inventory_controller, prefix="/inventory", tags=["inventory"])