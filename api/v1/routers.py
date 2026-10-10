# api/v1/router.py
from fastapi import APIRouter

from domains.health.health_controller import router as health_controller
from domains.inventory.inventory_controller import router as inventory_controller
from domains.orders.orders_controller import router as orders_controller
from domains.payments.payments_controller import router as payments_controller
from domains.payments.payments_webhooks import router as payments_webhooks
from domains.products.products_controller import router as products_controller
from domains.users.users_controller import router as users_controller

router = APIRouter()

router.include_router(health_controller, tags=["health"])
router.include_router(users_controller, prefix="/users", tags=["users"])
router.include_router(products_controller, prefix="/products", tags=["products"])
router.include_router(orders_controller, prefix="/orders", tags=["orders"])
router.include_router(payments_controller, prefix="/payments", tags=["payments"])
router.include_router(payments_webhooks, prefix="/payments", tags=["payment-webhooks"])
router.include_router(inventory_controller, prefix="/inventory", tags=["inventory"])
