"""User endpoints (including GDPR data export)."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.core import Consent, OrganizationMember, User
from app.schemas.base import SingleResponse
from app.schemas.core import ConsentCreate, ConsentRead, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=SingleResponse[UserRead])
async def get_current_user_profile(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.keycloak_id == uuid.UUID(user.id))
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(404, "User not found in DB")
    return SingleResponse(data=UserRead.model_validate(db_user))


@router.get("/me/data-export")
async def data_export(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GDPR Art. 20 — Export all personal data as JSON."""
    result = await db.execute(
        select(User).where(User.keycloak_id == uuid.UUID(user.id))
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(404, "User not found")

    # Collect user's data
    memberships_q = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == db_user.id,
            OrganizationMember.deleted_at.is_(None),
        )
    )
    memberships = memberships_q.scalars().all()

    consents_q = await db.execute(
        select(Consent).where(Consent.user_id == db_user.id)
    )
    consents = consents_q.scalars().all()

    return {
        "user": {
            "id": str(db_user.id),
            "email": db_user.email,
            "display_name": db_user.display_name,
            "phone": db_user.phone,
            "preferred_language": db_user.preferred_language,
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
        },
        "memberships": [
            {
                "organization_id": str(m.tenant_id),
                "role": m.role,
                "joined_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memberships
        ],
        "consents": [
            {
                "type": c.consent_type,
                "granted": c.granted,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
            }
            for c in consents
        ],
        "exported_at": datetime.utcnow().isoformat(),
    }


# --- Consents ---
@router.post("/me/consents", response_model=ConsentRead, status_code=201)
async def grant_consent(
    body: ConsentCreate,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.keycloak_id == uuid.UUID(user.id))
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(404, "User not found")

    ip = request.client.host if request.client else None
    consent = Consent(
        user_id=db_user.id,
        tenant_id=uuid.UUID(user.tenant_id) if user.tenant_id else None,
        consent_type=body.consent_type,
        granted=body.granted,
        ip_address=ip,
    )
    db.add(consent)
    await db.flush()
    return ConsentRead.model_validate(consent)


@router.get("/me/consents", response_model=list[ConsentRead])
async def list_consents(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.keycloak_id == uuid.UUID(user.id))
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(404, "User not found")

    consents_q = await db.execute(
        select(Consent).where(
            Consent.user_id == db_user.id,
            Consent.revoked_at.is_(None),
        )
    )
    return [ConsentRead.model_validate(c) for c in consents_q.scalars().all()]
