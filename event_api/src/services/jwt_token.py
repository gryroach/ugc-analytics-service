import logging

import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials is None:
            return {"auth_type": "not authenticated"}
        return self.parse_token(credentials.credentials)

    @staticmethod
    def parse_token(jwt_token: str) -> dict:
        try:
            data = jwt.decode(
                jwt_token,
                settings.jwt_public_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False},
            )
            return {"auth_type": "verified", **data}
        except jwt.exceptions.PyJWTError:
            return {"auth_type": "not verified"}
