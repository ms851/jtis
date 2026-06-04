"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.base import PaginationParams
from app.schemas.events import EventBase, EventCreate


class TestEventSchemas:
    def test_valid_event(self):
        event = EventBase(
            name="Test Turnier",
            start_date="2026-07-01",
            end_date="2026-07-03",
            timezone="Europe/Berlin",
        )
        assert event.name == "Test Turnier"
        assert event.status == "draft"

    def test_invalid_timezone(self):
        with pytest.raises(ValidationError) as exc_info:
            EventBase(
                name="Test",
                start_date="2026-07-01",
                end_date="2026-07-03",
                timezone="Invalid/Zone",
            )
        assert "timezone" in str(exc_info.value).lower()

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            EventBase(
                name="Test",
                start_date="2026-07-01",
                end_date="2026-07-03",
                timezone="Europe/Berlin",
                status="invalid",
            )

    def test_event_create_with_modules(self):
        event = EventCreate(
            name="Turnier mit Modulen",
            start_date="2026-07-01",
            end_date="2026-07-03",
            timezone="Europe/Berlin",
            modules=[
                {"module_key": "helpers", "is_active": True},
                {"module_key": "transport", "is_active": False},
            ],
        )
        assert len(event.modules) == 2
        assert event.modules[0].module_key == "helpers"


class TestPagination:
    def test_defaults(self):
        p = PaginationParams()
        assert p.limit == 20
        assert p.offset == 0
        assert p.page == 1

    def test_page_calculation(self):
        p = PaginationParams(limit=10, offset=30)
        assert p.page == 4
