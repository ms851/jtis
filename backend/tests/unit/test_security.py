"""Unit tests for security module."""


from app.core.security import CurrentUser


class TestCurrentUser:
    def test_basic_user(self):
        payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "preferred_username": "testuser",
            "name": "Test User",
            "tenant_id": "tenant-abc",
            "realm_access": {"roles": ["viewer"]},
        }
        user = CurrentUser(payload)
        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.tenant_id == "tenant-abc"
        assert not user.is_platform_admin
        assert not user.is_impersonated

    def test_admin_user(self):
        payload = {
            "sub": "admin-123",
            "email": "admin@example.com",
            "realm_access": {"roles": ["platform_admin", "viewer"]},
        }
        user = CurrentUser(payload)
        assert user.is_platform_admin

    def test_impersonated_user(self):
        payload = {
            "sub": "user-123",
            "email": "user@example.com",
            "realm_access": {"roles": ["viewer"]},
            "impersonator": "admin-456",
        }
        user = CurrentUser(payload)
        assert user.is_impersonated
        assert user.impersonator == "admin-456"

    def test_no_tenant(self):
        payload = {
            "sub": "user-123",
            "email": "user@example.com",
            "realm_access": {"roles": []},
        }
        user = CurrentUser(payload)
        assert user.tenant_id is None
