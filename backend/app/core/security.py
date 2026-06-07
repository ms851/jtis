"""Security utilities: JWT validation, Keycloak integration."""

from __future__ import annotations

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.database import current_tenant_id

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        url = (
            f"{settings.keycloak_url}/realms/"
            f"{settings.keycloak_realm}/protocol/openid-connect/certs"
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


def invalidate_jwks_cache() -> None:
    global _jwks_cache
    _jwks_cache = None


async def decode_token(token: str) -> dict:
    """Decode and validate a Keycloak JWT."""
    jwks = await _get_jwks()
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        ) from exc

    kid = unverified_header.get("kid")
    key = None
    for k in jwks.get("keys", []):
        if k["kid"] == kid:
            key = k
            break
    if key is None:
        # Maybe keys rotated – refetch once
        invalidate_jwks_cache()
        jwks = await _get_jwks()
        for k in jwks.get("keys", []):
            if k["kid"] == kid:
                key = k
                break
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find matching key",
        )

    # Build list of accepted issuers (internal Docker URL + external hostname)
    accepted_issuers = [
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}",
    ]
    if hasattr(settings, 'keycloak_hostname') and settings.keycloak_hostname:
        accepted_issuers.append(
            f"http://{settings.keycloak_hostname}/realms/{settings.keycloak_realm}"
        )

    # Build list of accepted audiences
    accepted_audiences = [settings.keycloak_client_id, "account"]

    last_error = None
    for issuer in accepted_issuers:
        for audience in accepted_audiences:
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=["RS256"],
                    audience=audience,
                    issuer=issuer,
                    options={"verify_aud": True, "verify_iss": True},
                )
                return payload
            except JWTError as exc:
                last_error = exc
                continue

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Token validation failed: {last_error}",
    )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {exc}",
        ) from exc

    return payload


class CurrentUser:
    """Represents the authenticated user from JWT claims."""

    def __init__(self, payload: dict) -> None:
        self.id: str = payload.get("sub", "")
        self.email: str = payload.get("email", "")
        self.name: str = payload.get("preferred_username", "")
        self.display_name: str = payload.get("name", "")
        self.tenant_id: str | None = payload.get("tenant_id")
        self.roles: list[str] = (
            payload.get("realm_access", {}).get("roles", [])
        )
        self.permissions: list[str] = payload.get("permissions", [])
        self.impersonator: str | None = payload.get("impersonator")
        self._payload = payload

    @property
    def is_platform_admin(self) -> bool:
        return "platform_admin" in self.roles

    @property
    def is_impersonated(self) -> bool:
        return self.impersonator is not None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = await decode_token(credentials.credentials)
    user = CurrentUser(payload)

    # Set tenant context
    if user.tenant_id:
        current_tenant_id.set(user.tenant_id)

    return user


def require_platform_admin(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required",
        )
    return user


def require_permission(permission: str):
    """Factory for permission-checking dependency."""

    async def _check(
        user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if user.is_platform_admin:
            return user
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return user

    return _check
