from jose import jwt

from app.core.config import settings


def decode_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        options={
            "verify_signature": False,
        },
    )

    return payload