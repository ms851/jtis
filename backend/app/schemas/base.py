"""Base Pydantic schemas for standard responses and pagination."""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class PaginatedResponse[T](BaseModel):
    data: list[T]
    meta: PaginationMeta


class SingleResponse[T](BaseModel):
    data: T


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class MessageResponse(BaseModel):
    message: str


class PaginationParams(BaseModel):
    limit: int = 20
    offset: int = 0

    @property
    def page(self) -> int:
        return (self.offset // self.limit) + 1 if self.limit else 1
