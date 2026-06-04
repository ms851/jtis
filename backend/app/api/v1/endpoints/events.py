"""Event endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.events import Event, EventModule
from app.schemas.base import PaginatedResponse, PaginationMeta, SingleResponse
from app.schemas.events import (
    EventCreate,
    EventModuleCreate,
    EventModuleRead,
    EventRead,
    EventUpdate,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=PaginatedResponse[EventRead])
async def list_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    base = select(Event).where(
        Event.tenant_id == uuid.UUID(user.tenant_id),
        Event.deleted_at.is_(None),
    )
    if status_filter:
        base = base.where(Event.status == status_filter)

    total_q = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total = total_q.scalar() or 0

    q = await db.execute(
        base.options(selectinload(Event.modules))
        .order_by(Event.start_date.desc())
        .limit(limit)
        .offset(offset)
    )
    events = q.scalars().all()
    pages = (total + limit - 1) // limit if limit else 1
    return PaginatedResponse(
        data=[EventRead.model_validate(e) for e in events],
        meta=PaginationMeta(
            page=(offset // limit) + 1, limit=limit, total=total, pages=pages
        ),
    )


@router.post(
    "",
    response_model=SingleResponse[EventRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    body: EventCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    event = Event(
        tenant_id=uuid.UUID(user.tenant_id),
        name=body.name,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        timezone=body.timezone,
        status=body.status,
        settings=body.settings,
        created_by=uuid.UUID(user.id),
    )
    db.add(event)
    await db.flush()

    for mod in body.modules:
        em = EventModule(
            tenant_id=uuid.UUID(user.tenant_id),
            event_id=event.id,
            module_key=mod.module_key,
            is_active=mod.is_active,
            config=mod.config,
        )
        db.add(em)
    await db.flush()

    # Reload with modules
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.modules))
        .where(Event.id == event.id)
    )
    event = result.scalar_one()
    return SingleResponse(data=EventRead.model_validate(event))


@router.get("/{event_id}", response_model=SingleResponse[EventRead])
async def get_event(
    event_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    result = await db.execute(
        select(Event)
        .options(selectinload(Event.modules))
        .where(
            Event.id == event_id,
            Event.tenant_id == uuid.UUID(user.tenant_id),
            Event.deleted_at.is_(None),
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(404, "Event not found")
    return SingleResponse(data=EventRead.model_validate(event))


@router.patch(
    "/{event_id}", response_model=SingleResponse[EventRead]
)
async def update_event(
    event_id: uuid.UUID,
    body: EventUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    result = await db.execute(
        select(Event)
        .options(selectinload(Event.modules))
        .where(
            Event.id == event_id,
            Event.tenant_id == uuid.UUID(user.tenant_id),
            Event.deleted_at.is_(None),
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(404, "Event not found")

    # Validate status transitions
    update_data = body.model_dump(exclude_unset=True)
    if "status" in update_data:
        valid_transitions = {
            "draft": {"active"},
            "active": {"completed"},
            "completed": {"archived"},
            "archived": set(),
        }
        if update_data["status"] not in valid_transitions.get(
            event.status, set()
        ):
            raise HTTPException(
                400,
                f"Cannot transition from '{event.status}' to "
                f"'{update_data['status']}'",
            )

    for k, v in update_data.items():
        setattr(event, k, v)
    event.updated_by = uuid.UUID(user.id)
    await db.flush()
    return SingleResponse(data=EventRead.model_validate(event))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    result = await db.execute(
        select(Event).where(
            Event.id == event_id,
            Event.tenant_id == uuid.UUID(user.tenant_id),
            Event.deleted_at.is_(None),
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(404, "Event not found")
    from datetime import datetime

    event.deleted_at = datetime.utcnow()
    await db.flush()


# --- Module activation ---
@router.put(
    "/{event_id}/modules",
    response_model=list[EventModuleRead],
)
async def set_event_modules(
    event_id: uuid.UUID,
    modules: list[EventModuleCreate],
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.tenant_id:
        raise HTTPException(400, "No tenant context")

    # Verify event
    result = await db.execute(
        select(Event).where(
            Event.id == event_id,
            Event.tenant_id == uuid.UUID(user.tenant_id),
            Event.deleted_at.is_(None),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Event not found")

    # Delete existing modules
    existing = await db.execute(
        select(EventModule).where(EventModule.event_id == event_id)
    )
    for em in existing.scalars().all():
        await db.delete(em)

    # Create new
    new_modules = []
    for mod in modules:
        em = EventModule(
            tenant_id=uuid.UUID(user.tenant_id),
            event_id=event_id,
            module_key=mod.module_key,
            is_active=mod.is_active,
            config=mod.config,
        )
        db.add(em)
        new_modules.append(em)

    await db.flush()
    return [EventModuleRead.model_validate(m) for m in new_modules]
