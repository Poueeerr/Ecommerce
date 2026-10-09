from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from domains.users.schemas.users_schemas import UserLogin, UserRegister
from domains.users.services.users_auth_service import UsersAuthService
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    UserNotFound,
)


def make_service(repository=None):
    repository = repository or SimpleNamespace(
        find_by_email=AsyncMock(),
        create_user=AsyncMock(),
    )
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    jwt_handler = SimpleNamespace(
        create_access_token=lambda *args, **kwargs: "token",
        expires_in_seconds=1800,
    )
    return UsersAuthService(db, repository, jwt_handler), repository, db


@pytest.mark.asyncio
async def test_register_hashes_password_and_commits():
    service, repository, db = make_service()
    repository.find_by_email.return_value = None
    user_data = UserRegister(
        name="Admin",
        email="admin@example.com",
        password="password123",
    )

    await service.register(user_data, valid_admin=True)

    user = repository.create_user.call_args.args[0]
    assert user.email == user_data.email
    assert user.password != user_data.password
    assert user.role == UserRole.ADMIN
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_rejects_existing_email():
    service, repository, db = make_service()
    repository.find_by_email.return_value = object()
    user_data = UserRegister(
        name="User",
        email="user@example.com",
        password="password123",
    )

    with pytest.raises(EmailAlreadyRegistered):
        await service.register(user_data)

    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_login_returns_token_for_valid_credentials():
    service, repository, _ = make_service()
    password = await service._encrypt_password("password123")
    repository.find_by_email.return_value = SimpleNamespace(
        id="user-id",
        email="user@example.com",
        name="User",
        password=password,
        role=UserRole.USER,
    )

    token = await service.login(UserLogin(email="user@example.com", password="password123"))

    assert token.access_token == "token"
    assert token.token_type == "bearer"
    assert token.expires_in == 1800


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials():
    service, repository, _ = make_service()
    repository.find_by_email.return_value = None

    with pytest.raises(InvalidCredentials):
        await service.login(UserLogin(email="user@example.com", password="wrongpass"))


@pytest.mark.asyncio
async def test_user_by_email_rejects_unknown_user():
    service, repository, _ = make_service()
    repository.find_by_email.return_value = None

    with pytest.raises(UserNotFound):
        await service.user_by_email("unknown@example.com")
