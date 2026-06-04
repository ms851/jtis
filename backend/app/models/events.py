"""Event models: Events, EventModules."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TenantMixin


class Event(BaseModel, TenantMixin):
    """Veranstaltungen."""

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    organization: Mapped[Organization] = relationship(  # noqa: F821
        back_populates="events",
        foreign_keys=[TenantMixin.tenant_id],
        primaryjoin="Event.tenant_id == Organization.id",
    )
    modules: Mapped[list[EventModule]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class EventModule(BaseModel, TenantMixin):
    """Activated modules per event."""

    __tablename__ = "event_modules"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    module_key: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    event: Mapped[Event] = relationship(back_populates="modules")
