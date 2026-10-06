import bcrypt
from anyio import to_thread
from sqlalchemy.ext.asyncio import AsyncSession

from core.jwt_handler import JwtHandler
from domains.users.models import UsersModel
from domains.users.repositories.users_auth_repository import UsersAuthRepository
from domains.users.schemas.users_schemas import Token, UserLogin, UserRegister
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import EmailAlreadyRegistered, InvalidCredentials, UserNotFound


class UsersAuthService:
    def __init__(
        self,
        db: AsyncSession,
        users_auth_repository: UsersAuthRepository,
        jwt_handler: JwtHandler,
    ):
        self.db = db
        self.users_auth_repository = users_auth_repository
        self.jwt_handler = jwt_handler

    async def register(self, user_data: UserRegister, valid_admin: bool = False) -> None:
        if await self.user_exists(user_data.email):
            raise EmailAlreadyRegistered
        role = UserRole.ADMIN if valid_admin else UserRole.USER

        user = UsersModel(
            name=user_data.name,
            email=user_data.email,
            password=await self._encrypt_password(user_data.password),
            role=role,
        )
        try:
            await self.users_auth_repository.create_user(user)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

    async def login(self, user_data: UserLogin) -> Token:
        user = await self.users_auth_repository.find_by_email(user_data.email)
        if user is None or not await self._check_password(user_data.password, user.password):
            raise InvalidCredentials

        return Token(
            access_token=self.jwt_handler.create_access_token(
                str(user.id), email=user.email, name=user.name, role=user.role
            ),
            expires_in=self.jwt_handler.expires_in_seconds,
        )

    async def user_exists(self, email: str) -> bool:
        return await self.users_auth_repository.find_by_email(email) is not None

    async def user_by_email(self, email: str) -> UsersModel:
        user = await self.users_auth_repository.find_by_email(email)
        if user is None:
            raise UserNotFound
        return user


    @staticmethod
    async def _encrypt_password(password: str) -> str:
        hashed_password = await to_thread.run_sync(
            bcrypt.hashpw,
            password.encode("utf-8"),
            bcrypt.gensalt(),
        )

        return hashed_password.decode("utf-8")

    @staticmethod
    async def _check_password(
        password: str,
        hashed_password: str,
    ) -> bool:
        return await to_thread.run_sync(
            bcrypt.checkpw,
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
