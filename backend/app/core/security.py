from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from jose import JWTError, jwk, jwt

from app.core.config import settings


logger = logging.getLogger(__name__)

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
    logger.warning("[auth-debug] verify_supabase_jwt: token_len=%s", len(token or ""))

    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        logger.exception("[auth-debug] failed to read unverified JWT header")
        raise JWTError("Invalid JWT header") from exc

    try:
        claims = jwt.get_unverified_claims(token)
    except JWTError as exc:
        logger.exception("[auth-debug] failed to read unverified JWT claims")
        raise JWTError("Invalid JWT claims") from exc

    logger.warning("[auth-debug] header=%s", header)
    logger.warning("[auth-debug] claims=%s", claims)

    algorithm = header.get("alg")
    logger.warning("[auth-debug] alg=%s", algorithm)
    if algorithm not in {"RS256", "ES256"}:
        logger.warning("[auth-debug] rejected: unsupported algorithm")
        raise JWTError("Unsupported JWT algorithm")

    key_id = header.get("kid")
    logger.warning("[auth-debug] kid=%s", key_id)
    if not key_id:
        logger.warning("[auth-debug] rejected: missing kid")
        raise JWTError("Missing JWT key id")

    jwks = await _get_supabase_jwks()
    logger.warning("[auth-debug] jwks_url=%s", _supabase_jwks_url())
    logger.warning(
        "[auth-debug] jwks_key_ids=%s",
        [key.get("kid") for key in jwks.get("keys", []) if isinstance(key, dict)],
    )
    key_data = next(
        (key for key in jwks.get("keys", []) if key.get("kid") == key_id),
        None,
    )

    if not key_data:
        logger.warning("[auth-debug] rejected: signing key not found for kid=%s", key_id)
        raise JWTError("Signing key not found")

    public_key = jwk.construct(key_data)
    pem = public_key.to_pem().decode("utf-8")

    issuer = _supabase_auth_issuer()
    audience = "authenticated"
    exp = claims.get("exp")
    now = datetime.now(timezone.utc).timestamp()
    logger.warning("[auth-debug] issuer_expected=%s", issuer)
    logger.warning("[auth-debug] audience_expected=%s", audience)
    logger.warning("[auth-debug] exp_claim=%s", exp)
    logger.warning("[auth-debug] now_epoch=%s", now)
    if isinstance(exp, (int, float)):
        logger.warning("[auth-debug] exp_delta_seconds=%s", float(exp) - now)

    try:
        decoded = jwt.decode(
            token,
            pem,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
        )
        logger.warning("[auth-debug] decode_success=true")
        logger.warning("[auth-debug] decoded_claims=%s", decoded)
        return decoded
    except JWTError as exc:
        logger.exception(
            "[auth-debug] jwt.decode failed: alg=%s iss=%s aud=%s kid=%s",
            algorithm,
            issuer,
            audience,
            key_id,
        )
        raise