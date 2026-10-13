from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from domains.products.products_enums import ProductType
from domains.products.schemas.products_schemas import ProductCreate, ProductRegister


class ProductFactory:
    @staticmethod
    def build_create(**overrides) -> ProductCreate:
        values = {
            "product_name": "Test Product",
            "product_type": ProductType.GENERIC,
            "product_price": Decimal("12.50"),
            "product_description": "Product for tests",
        }
        values.update(overrides)
        return ProductCreate(**values)

    @staticmethod
    def build_register(**overrides) -> ProductRegister:
        values = {
            **ProductFactory.build_create().model_dump(),
            "quantity": 10,
        }
        values.update(overrides)
        return ProductRegister(**values)

    @staticmethod
    def build_model(**overrides) -> SimpleNamespace:
        values = {
            "id": uuid4(),
            "product_name": "Test Product",
            "product_type": ProductType.GENERIC,
            "product_price": Decimal("12.50"),
            "product_description": "Product for tests",
        }
        values.update(overrides)
        return SimpleNamespace(**values)
