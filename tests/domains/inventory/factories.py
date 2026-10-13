from types import SimpleNamespace
from uuid import uuid4


class InventoryFactory:
    @staticmethod
    def build_model(**overrides) -> SimpleNamespace:
        values = {
            "id": uuid4(),
            "product_id": uuid4(),
            "total_quantity": 10,
            "reserved_quantity": 2,
        }
        values.update(overrides)
        return SimpleNamespace(**values)
