# api/v1/router.py
from fastapi import APIRouter

from domains.catalog.catalog_controller import router as catalog_controller
from domains.health.health_controller import router as health_controller
from domains.users.users_controller import router as users_controller

router = APIRouter()
router.include_router(health_controller, tags=["health"])
router.include_router(users_controller, prefix="/users", tags=["users"])
router.include_router(catalog_controller, prefix="/catalog", tags=["catalog"])
