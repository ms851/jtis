"""Schemas for Organizations, Users, Subscriptions."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


# --- Subscription Plans ---
class SubscriptionPlanBase(BaseModel):
    name: str
    slug: str
    price_monthly: float | None = None
    price_yearly: float | None = None
    max_events: int | None = None
    max_helpers: int | None = None
    max_storage_mb: int | None = None
    enabled_modules: dict | None = None
    is_active: bool = True


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanRead(SubscriptionPlanBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Organizations ---
class OrganizationBase(BaseModel):
    name: str
    slug: str
    contact_email: str | None = None
    address: dict | None = None
    settings: dict | None = None


class OrganizationCreate(OrganizationBase):
    subscription_plan_id: uuid.UUID | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    contact_email: str | None = None
    address: dict | None = None
    settings: dict | None = None
    logo_url: str | None = None


class OrganizationRead(OrganizationBase):
    id: uuid.UUID
    logo_url: str | None = None
    subscription_plan_id: uuid.UUID | None = None
    subscription_status: str
    subscription_valid_until: datetime | None = None
    is_suspended: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Users ---
class UserBase(BaseModel):
    email: EmailStr
    display_name: str | None = None
    phone: str | None = None
    preferred_language: str = "de"


class UserCreate(UserBase):
    keycloak_id: uuid.UUID | None = None


class UserRead(UserBase):
    id: uuid.UUID
    keycloak_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Organization Members ---
class OrgMemberBase(BaseModel):
    role: str = "viewer"


class OrgMemberCreate(OrgMemberBase):
    email: EmailStr


class OrgMemberRead(OrgMemberBase):
    id: uuid.UUID
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    invitation_email: str | None = None
    invitation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgMemberWithUser(OrgMemberRead):
    user: UserRead | None = None


# --- Impersonation ---
class ImpersonationStart(BaseModel):
    target_user_id: uuid.UUID
    reason: str | None = None


class ImpersonationLogRead(BaseModel):
    id: uuid.UUID
    admin_user_id: uuid.UUID
    target_user_id: uuid.UUID
    tenant_id: uuid.UUID
    started_at: datetime
    ended_at: datetime | None = None
    reason: str | None = None
    actions_count: int

    model_config = {"from_attributes": True}


# --- Audit Log ---
class AuditLogRead(BaseModel):
    id: uuid.UUID
    actor_user_id: uuid.UUID | None = None
    action: str
    target_type: str | None = None
    target_id: uuid.UUID | None = None
    details: dict | None = None
    ip_address: str | None = None
    is_impersonated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Consent ---
class ConsentCreate(BaseModel):
    consent_type: str
    granted: bool


class ConsentRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    consent_type: str
    granted: bool
    granted_at: datetime
    revoked_at: datetime | None = None

    model_config = {"from_attributes": True}
