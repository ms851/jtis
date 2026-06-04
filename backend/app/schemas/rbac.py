"""Schemas for RBAC."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class PermissionRead(BaseModel):
    id: uuid.UUID
    codename: str
    description: str | None = None
    module: str

    model_config = {"from_attributes": True}


class RoleBase(BaseModel):
    name: str
    slug: str
    description: str | None = None


class RoleCreate(RoleBase):
    permission_ids: list[uuid.UUID] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permission_ids: list[uuid.UUID] | None = None


class RoleRead(RoleBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    is_system: bool
    created_at: datetime
    permissions: list[PermissionRead] = []

    model_config = {"from_attributes": True}


class UserEventRoleCreate(BaseModel):
    user_id: uuid.UUID
    event_id: uuid.UUID | None = None
    role_id: uuid.UUID


class UserEventRoleRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID | None = None
    role_id: uuid.UUID
    tenant_id: uuid.UUID

    model_config = {"from_attributes": True}
