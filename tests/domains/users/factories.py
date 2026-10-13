from types import SimpleNamespace
from uuid import uuid4

from domains.users.schemas.users_schemas import UserLogin, UserRegister
from domains.users.users_enums import UserRole


class UserFactory:
    @staticmethod
    def build_register(**overrides) -> UserRegister:
        values = {
            "name": "Test User",
            "email": "user@example.com",
            "password": "password123",
        }
        values.update(overrides)
        return UserRegister(**values)

    @staticmethod
    def build_login(**overrides) -> UserLogin:
        values = {
            "email": "user@example.com",
            "password": "password123",
        }
        values.update(overrides)
        return UserLogin(**values)

    @staticmethod
    def build_model(**overrides) -> SimpleNamespace:
        values = {
            "id": uuid4(),
            "name": "Test User",
            "email": "user@example.com",
            "password": "password123",
            "role": UserRole.USER,
        }
        values.update(overrides)
        return SimpleNamespace(**values)
