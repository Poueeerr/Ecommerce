from uuid import UUID, uuid4

from domains.orders.schemas.orders_schemas import CreateOrder


class OrderFactory:
    @staticmethod
    def build_create(product_id: UUID | None = None, **overrides) -> CreateOrder:
        values = {
            "items": [{"product_id": product_id or uuid4(), "quantity": 3}],
        }
        values.update(overrides)
        return CreateOrder(**values)

    @staticmethod
    def build_user_context(**overrides) -> dict[str, str]:
        values = {
            "sub": str(uuid4()),
            "email": "user@example.com",
        }
        values.update(overrides)
        return values
