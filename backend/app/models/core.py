"""Core models: Organizations, Users, Subscriptions, Audit."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel, TenantMixin


class SubscriptionPlan(Base):
    """SaaS subscription plans."""

    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    price_monthly: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    price_yearly: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    max_events: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_helpers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_storage_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enabled_modules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )

    organizations: Mapped[list[Organization]] = relationship(
        back_populates="subscription_plan"
    )


class Organization(BaseModel):
    """Organizations (tenants)."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    address: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    subscription_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("subscription_plans.id"), nullable=True
    )
    subscription_status: Mapped[str] = mapped_column(
        String(20), default="trial"
    )
    subscription_valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    suspended_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    subscription_plan: Mapped[SubscriptionPlan | None] = relationship(
        back_populates="organizations"
    )
    members: Mapped[list[OrganizationMember]] = relationship(
        back_populates="organization"
    )
    events: Mapped[list] = relationship(
        "Event", back_populates="organization"
    )


class User(BaseModel):
    """Platform-wide users."""

    __tablename__ = "users"

    keycloak_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, unique=True, nullable=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    display_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_language: Mapped[str] = mapped_column(
        String(5), default="de"
    )

    memberships: Mapped[list[OrganizationMember]] = relationship(
        back_populates="user"
    )


class OrganizationMember(BaseModel, TenantMixin):
    """Organization membership (user ↔ org)."""

    __tablename__ = "organization_members"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="viewer")
    invitation_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    invitation_status: Mapped[str] = mapped_column(
        String(20), default="accepted"
    )

    organization: Mapped[Organization] = relationship(
        back_populates="members",
        foreign_keys=[TenantMixin.tenant_id],
        primaryjoin="OrganizationMember.tenant_id == Organization.id",
    )
    user: Mapped[User] = relationship(back_populates="memberships")


class ImpersonationLog(Base):
    """Impersonation audit log."""

    __tablename__ = "impersonation_log"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    target_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    actions_count: Mapped[int] = mapped_column(Integer, default=0)


class PlatformAuditLog(Base):
    """Platform-wide audit log."""

    __tablename__ = "platform_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    target_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    is_impersonated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )


class Consent(Base):
    """GDPR consent tracking."""

    __tablename__ = "consents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=True
    )
    consent_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
