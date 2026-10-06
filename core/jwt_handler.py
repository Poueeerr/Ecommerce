from datetime import UTC, datetime, timedelta

import jwt

from core.config import settings


class JwtHandler:
    @property
    def expires_in_seconds(self) -> int:
        return settings.jwt_expire_in * 60

    def create_access_token(self, subject: str, **claims) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(seconds=self.expires_in_seconds),
            **claims,
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def validate_access_token(self, token: str) -> dict:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
