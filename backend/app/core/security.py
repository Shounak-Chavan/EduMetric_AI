from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
from jose import JWTError, jwk, jwt

from app.core.config import settings


_JWKS_CACHE: dict[str, Any] | None = None
_JWKS_CACHE_EXPIRES_AT = 0.0
_JWKS_CACHE_TTL_SECONDS = 300.0
_JWKS_LOCK = asyncio.Lock()


def _supabase_auth_issuer() -> str:
    return f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"


def _supabase_jwks_url() -> str:
    return f"{_supabase_auth_issuer()}/.well-known/jwks.json"


async def _get_supabase_jwks() -> dict[str, Any]:
    global _JWKS_CACHE
    global _JWKS_CACHE_EXPIRES_AT

    now = time.monotonic()
    if _JWKS_CACHE is not None and now < _JWKS_CACHE_EXPIRES_AT:
        return _JWKS_CACHE

    async with _JWKS_LOCK:
        now = time.monotonic()
        if _JWKS_CACHE is not None and now < _JWKS_CACHE_EXPIRES_AT:
            return _JWKS_CACHE

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(_supabase_jwks_url())
            response.raise_for_status()

        _JWKS_CACHE = response.json()
        _JWKS_CACHE_EXPIRES_AT = now + _JWKS_CACHE_TTL_SECONDS
        return _JWKS_CACHE


async def verify_supabase_jwt(token: str) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise JWTError("Invalid JWT header") from exc

    algorithm = header.get("alg")
    if algorithm != "RS256":
        raise JWTError("Unsupported JWT algorithm")

    key_id = header.get("kid")
    if not key_id:
        raise JWTError("Missing JWT key id")

    jwks = await _get_supabase_jwks()
    key_data = next(
        (key for key in jwks.get("keys", []) if key.get("kid") == key_id),
        None,
    )

    if not key_data:
        raise JWTError("Signing key not found")

    public_key = jwk.construct(key_data)

    return jwt.decode(
        token,
        public_key.to_pem().decode("utf-8"),
        algorithms=["RS256"],
        audience="authenticated",
        issuer=_supabase_auth_issuer(),
    )