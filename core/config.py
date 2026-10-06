from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USER: str = "ecommerce"
    POSTGRES_PASSWORD: str = "ecommerce"
    POSTGRES_DB: str = "ecommerce"
    POSTGRES_PORT: int = 5432

    jwt_secret_key: str = Field(
        default="change-me",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "jwt_secret_key"),
    )
    jwt_expire_in: int = Field(
        default=30,
        validation_alias=AliasChoices("JWT_EXPIRE_IN", "jwt_expire_in"),
    )
    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "jwt_algorithm"),
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sqlalchemy_url_sync(self) -> str:
        return self.sqlalchemy_url.replace("postgresql+asyncpg", "postgresql+psycopg")


settings = Settings()