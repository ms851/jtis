"""SaaS Administration endpoints (platform_admin only)."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, require_platform_admin
from app.models.core import (
    ImpersonationLog,
    Organization,
    PlatformAuditLog,
    SubscriptionPlan,
    User,
)
from app.schemas.base import PaginatedResponse, PaginationMeta, SingleResponse
from app.schemas.core import (
    AuditLogRead,
    ImpersonationStart,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    SubscriptionPlanCreate,
    SubscriptionPlanRead,
)

router = APIRouter(prefix="/admin", tags=["admin"])


async def _log_action(
    db: AsyncSession,
    user: CurrentUser,
    action: str,
    target_type: str | None = None,
    target_id: uuid.UUID | None = None,
    details: dict | None = None,
    request: Request | None = None,
) -> None:
    ip = None
    if request and request.client:
        ip = request.client.host
    log = PlatformAuditLog(
        actor_user_id=uuid.UUID(user.id) if user.id else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        ip_address=ip,
        is_impersonated=user.is_impersonated,
    )
    db.add(log)


# --- Tenants ---
@router.get("/tenants", response_model=PaginatedResponse[OrganizationRead])
async def list_tenants(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    total_q = await db.execute(
        select(func.count()).select_from(Organization).where(
            Organization.deleted_at.is_(None)
        )
    )
    total = total_q.scalar() or 0
    q = await db.execute(
        select(Organization)
        .where(Organization.deleted_at.is_(None))
        .order_by(Organization.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    orgs = q.scalars().all()
    pages = (total + limit - 1) // limit if limit else 1
    return PaginatedResponse(
        data=[OrganizationRead.model_validate(o) for o in orgs],
        meta=PaginationMeta(
            page=(offset // limit) + 1, limit=limit, total=total, pages=pages
        ),
    )


@router.post(
    "/tenants",
    response_model=SingleResponse[OrganizationRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant(
    body: OrganizationCreate,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    org = Organization(
        **body.model_dump(),
        created_by=uuid.UUID(admin.id),
    )
    db.add(org)
    await db.flush()
    await _log_action(
        db, admin, "tenant.create", "organization", org.id, request=request
    )
    return SingleResponse(data=OrganizationRead.model_validate(org))


@router.patch(
    "/tenants/{tenant_id}",
    response_model=SingleResponse[OrganizationRead],
)
async def update_tenant(
    tenant_id: uuid.UUID,
    body: OrganizationUpdate,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Organization).where(
            Organization.id == tenant_id,
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")
    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(org, k, v)
    org.updated_by = uuid.UUID(admin.id)
    await db.flush()
    await _log_action(
        db,
        admin,
        "tenant.update",
        "organization",
        org.id,
        details=update_data,
        request=request,
    )
    return SingleResponse(data=OrganizationRead.model_validate(org))


@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: uuid.UUID,
    request: Request,
    reason: str = Query(None),
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Organization).where(
            Organization.id == tenant_id,
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")
    org.is_suspended = True
    org.suspended_reason = reason
    await db.flush()
    await _log_action(
        db,
        admin,
        "tenant.suspend",
        "organization",
        org.id,
        details={"reason": reason},
        request=request,
    )
    return {"message": "Tenant suspended"}


@router.post("/tenants/{tenant_id}/unsuspend")
async def unsuspend_tenant(
    tenant_id: uuid.UUID,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Organization).where(
            Organization.id == tenant_id,
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")
    org.is_suspended = False
    org.suspended_reason = None
    await db.flush()
    await _log_action(
        db, admin, "tenant.unsuspend", "organization", org.id, request=request
    )
    return {"message": "Tenant unsuspended"}


# --- Subscription Plans ---
@router.get("/plans", response_model=PaginatedResponse[SubscriptionPlanRead])
async def list_plans(
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(select(SubscriptionPlan))
    plans = q.scalars().all()
    return PaginatedResponse(
        data=[SubscriptionPlanRead.model_validate(p) for p in plans],
        meta=PaginationMeta(
            page=1, limit=100, total=len(plans), pages=1
        ),
    )


@router.post(
    "/plans",
    response_model=SingleResponse[SubscriptionPlanRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    body: SubscriptionPlanCreate,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    plan = SubscriptionPlan(**body.model_dump())
    db.add(plan)
    await db.flush()
    await _log_action(
        db, admin, "plan.create", "subscription_plan", plan.id, request=request
    )
    return SingleResponse(data=SubscriptionPlanRead.model_validate(plan))


# --- Audit Log ---
@router.get("/audit-log", response_model=PaginatedResponse[AuditLogRead])
async def get_audit_log(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    total_q = await db.execute(
        select(func.count()).select_from(PlatformAuditLog)
    )
    total = total_q.scalar() or 0
    q = await db.execute(
        select(PlatformAuditLog)
        .order_by(PlatformAuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = q.scalars().all()
    pages = (total + limit - 1) // limit if limit else 1
    return PaginatedResponse(
        data=[AuditLogRead.model_validate(entry) for entry in logs],
        meta=PaginationMeta(
            page=(offset // limit) + 1, limit=limit, total=total, pages=pages
        ),
    )


# --- Impersonation ---
@router.post("/impersonate")
async def start_impersonation(
    body: ImpersonationStart,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    # Verify target user exists
    target = await db.execute(
        select(User).where(User.id == body.target_user_id)
    )
    if not target.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Target user not found")

    log = ImpersonationLog(
        admin_user_id=uuid.UUID(admin.id),
        target_user_id=body.target_user_id,
        tenant_id=uuid.UUID(admin.tenant_id) if admin.tenant_id else uuid.uuid4(),
        reason=body.reason,
    )
    db.add(log)
    await db.flush()
    await _log_action(
        db,
        admin,
        "impersonation.start",
        "user",
        body.target_user_id,
        details={"reason": body.reason},
        request=request,
    )
    return {
        "message": "Impersonation started",
        "impersonation_id": str(log.id),
        "note": "Use Keycloak token exchange to get impersonated token",
    }


@router.post("/impersonate/end")
async def end_impersonation(
    impersonation_id: uuid.UUID = Query(...),
    request: Request = None,
    admin: CurrentUser = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImpersonationLog).where(
            ImpersonationLog.id == impersonation_id,
            ImpersonationLog.ended_at.is_(None),
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(
            status_code=404,
            detail="Active impersonation not found",
        )
    log.ended_at = datetime.utcnow()
    await db.flush()
    await _log_action(
        db,
        admin,
        "impersonation.end",
        "user",
        log.target_user_id,
        request=request,
    )
    return {"message": "Impersonation ended"}
