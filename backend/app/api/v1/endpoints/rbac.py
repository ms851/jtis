"""RBAC endpoints: Roles, Permissions, Assignments."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.rbac import Permission, Role, RolePermission, UserEventRole
from app.schemas.rbac import (
    PermissionRead,
    RoleCreate,
    RoleRead,
    RoleUpdate,
    UserEventRoleCreate,
    UserEventRoleRead,
)

router = APIRouter(prefix="/rbac", tags=["rbac"])


@router.get("/permissions", response_model=list[PermissionRead])
async def list_permissions(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Permission).order_by(Permission.module))
    return [PermissionRead.model_validate(p) for p in result.scalars().all()]


@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
        .where(
            Role.tenant_id == uuid.UUID(user.tenant_id),
            Role.deleted_at.is_(None),
        )
    )
    roles = result.scalars().all()
    out = []
    for r in roles:
        data = RoleRead.model_validate(r)
        data.permissions = [
            PermissionRead.model_validate(rp.permission) for rp in r.permissions
        ]
        out.append(data)
    return out


@router.post(
    "/roles",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    body: RoleCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    role = Role(
        tenant_id=uuid.UUID(user.tenant_id),
        name=body.name,
        slug=body.slug,
        description=body.description,
        created_by=uuid.UUID(user.id),
    )
    db.add(role)
    await db.flush()

    for perm_id in body.permission_ids:
        rp = RolePermission(role_id=role.id, permission_id=perm_id)
        db.add(rp)
    await db.flush()

    return RoleRead(
        id=role.id,
        tenant_id=role.tenant_id,
        name=role.name,
        slug=role.slug,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        permissions=[],
    )


@router.patch("/roles/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(Role).where(
            Role.id == role_id,
            Role.tenant_id == uuid.UUID(user.tenant_id),
            Role.deleted_at.is_(None),
        )
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")
    if role.is_system:
        raise HTTPException(400, "Cannot modify system roles")

    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description

    if body.permission_ids is not None:
        # Replace permissions
        existing = await db.execute(
            select(RolePermission).where(RolePermission.role_id == role_id)
        )
        for rp in existing.scalars().all():
            await db.delete(rp)
        for perm_id in body.permission_ids:
            rp = RolePermission(role_id=role.id, permission_id=perm_id)
            db.add(rp)

    await db.flush()
    return RoleRead(
        id=role.id,
        tenant_id=role.tenant_id,
        name=role.name,
        slug=role.slug,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        permissions=[],
    )


@router.delete(
    "/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_role(
    role_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    result = await db.execute(
        select(Role).where(
            Role.id == role_id,
            Role.tenant_id == uuid.UUID(user.tenant_id),
            Role.deleted_at.is_(None),
        )
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")
    if role.is_system:
        raise HTTPException(400, "Cannot delete system roles")
    from datetime import datetime
    role.deleted_at = datetime.utcnow()
    await db.flush()


# --- User Event Roles ---
@router.post(
    "/assignments",
    response_model=UserEventRoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def assign_role(
    body: UserEventRoleCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")
    assignment = UserEventRole(
        tenant_id=uuid.UUID(user.tenant_id),
        user_id=body.user_id,
        event_id=body.event_id,
        role_id=body.role_id,
        created_by=uuid.UUID(user.id),
    )
    db.add(assignment)
    await db.flush()
    return UserEventRoleRead.model_validate(assignment)
