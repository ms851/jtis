"""Organization settings endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.core import Organization, OrganizationMember, User
from app.schemas.base import SingleResponse
from app.schemas.core import (
    OrganizationRead,
    OrganizationUpdate,
    OrgMemberCreate,
    OrgMemberRead,
    OrgMemberWithUser,
)

router = APIRouter(prefix="/org", tags=["organization"])


@router.get("", response_model=SingleResponse[OrganizationRead])
async def get_organization(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(Organization).where(
            Organization.id == uuid.UUID(user.tenant_id),
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(404, "Organization not found")
    return SingleResponse(data=OrganizationRead.model_validate(org))


@router.patch("", response_model=SingleResponse[OrganizationRead])
async def update_organization(
    body: OrganizationUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(Organization).where(
            Organization.id == uuid.UUID(user.tenant_id),
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(404, "Organization not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(org, k, v)
    org.updated_by = uuid.UUID(user.id)
    await db.flush()
    await db.refresh(org)
    return SingleResponse(data=OrganizationRead.model_validate(org))


# --- Members ---
@router.get("/members", response_model=list[OrgMemberWithUser])
async def list_members(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.tenant_id == uuid.UUID(user.tenant_id),
            OrganizationMember.deleted_at.is_(None),
        )
    )
    members = result.scalars().all()

    out = []
    for m in members:
        user_q = await db.execute(select(User).where(User.id == m.user_id))
        u = user_q.scalar_one_or_none()
        data = OrgMemberRead.model_validate(m).model_dump()
        data["user"] = u
        out.append(OrgMemberWithUser(**data))
    return out


@router.post(
    "/members",
    response_model=OrgMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    body: OrgMemberCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invite a user by email. Creates user stub if needed."""
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    # Find or create user
    result = await db.execute(
        select(User).where(User.email == body.email)
    )
    target_user = result.scalar_one_or_none()
    if not target_user:
        target_user = User(email=body.email, display_name=body.email)
        db.add(target_user)
        await db.flush()

    # Check duplicate
    existing = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.tenant_id == uuid.UUID(user.tenant_id),
            OrganizationMember.user_id == target_user.id,
            OrganizationMember.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "User is already a member")

    member = OrganizationMember(
        tenant_id=uuid.UUID(user.tenant_id),
        user_id=target_user.id,
        role=body.role,
        invitation_email=body.email,
        invitation_status="pending",
        created_by=uuid.UUID(user.id),
    )
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return OrgMemberRead.model_validate(member)


@router.patch("/members/{member_id}", response_model=OrgMemberRead)
async def update_member_role(
    member_id: uuid.UUID,
    role: str = Query(...),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.id == member_id,
            OrganizationMember.tenant_id == uuid.UUID(user.tenant_id),
            OrganizationMember.deleted_at.is_(None),
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "Member not found")
    member.role = role
    await db.flush()
    await db.refresh(member)
    return OrgMemberRead.model_validate(member)


@router.delete(
    "/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    member_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.id == member_id,
            OrganizationMember.tenant_id == uuid.UUID(user.tenant_id),
            OrganizationMember.deleted_at.is_(None),
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "Member not found")
    from datetime import datetime
    member.deleted_at = datetime.utcnow()
    await db.flush()
