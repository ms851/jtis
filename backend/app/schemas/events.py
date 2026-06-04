"""Schemas for Events and EventModules."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class EventModuleBase(BaseModel):
    module_key: str
    is_active: bool = True
    config: dict | None = None


class EventModuleCreate(EventModuleBase):
    pass


class EventModuleRead(EventModuleBase):
    id: uuid.UUID
    event_id: uuid.UUID

    model_config = {"from_attributes": True}


class EventBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    timezone: str
    status: str = "draft"
    settings: dict | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"draft", "active", "completed", "archived"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        import zoneinfo

        try:
            zoneinfo.ZoneInfo(v)
        except (KeyError, Exception):
            raise ValueError(f"Invalid timezone: {v}")
        return v


class EventCreate(EventBase):
    modules: list[EventModuleCreate] = []


class EventUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    timezone: str | None = None
    status: str | None = None
    settings: dict | None = None


class EventRead(EventBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    modules: list[EventModuleRead] = []

    model_config = {"from_attributes": True}
