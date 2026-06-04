"""Shared test fixtures."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import CurrentUser, get_current_user
from app.main import app

settings = get_settings()

# Use sync engine for tests
TEST_DB_URL = settings.database_url_sync
if "localhost" not in TEST_DB_URL and "127.0.0.1" not in TEST_DB_URL:
    TEST_DB_URL = "sqlite:///./test.db"

TENANT_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())


def make_test_user(
    is_admin: bool = False,
    tenant_id: str | None = TENANT_ID,
) -> CurrentUser:
    payload = {
        "sub": USER_ID,
        "email": "test@jtis.local",
        "preferred_username": "testuser",
        "name": "Test User",
        "tenant_id": tenant_id,
        "realm_access": {
            "roles": ["platform_admin"] if is_admin else ["viewer"],
        },
        "permissions": [
            "events:read",
            "events:write",
            "events:admin",
            "org:read",
            "org:write",
            "org:admin",
            "rbac:read",
            "rbac:write",
            "helpers:read",
            "helpers:write",
        ],
    }
    return CurrentUser(payload)


@pytest.fixture
def test_user():
    return make_test_user()


@pytest.fixture
def admin_user():
    return make_test_user(is_admin=True)


@pytest.fixture
def client(test_user):
    """Test client with mocked auth."""

    app.dependency_overrides[get_current_user] = lambda: test_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(admin_user):
    """Test client with admin auth."""

    app.dependency_overrides[get_current_user] = lambda: admin_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
