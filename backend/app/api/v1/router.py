"""Aggregate all v1 API routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, events, health, org, rbac, users

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(admin.router)
api_router.include_router(events.router)
api_router.include_router(org.router)
api_router.include_router(rbac.router)
api_router.include_router(users.router)
