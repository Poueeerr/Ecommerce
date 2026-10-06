from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.users.models import UsersModel


class UsersAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_email(self, email: str) -> UsersModel | None:
        return await self.db.scalar(select(UsersModel).where(UsersModel.email == email))

    async def create_user(self, user: UsersModel) -> UsersModel:
        self.db.add(user)
        await self.db.flush()
        return user
