"""Integration tests for API structure and OpenAPI."""

from fastapi.testclient import TestClient

from app.main import app


class TestAPIStructure:
    def test_openapi_schema(self):
        with TestClient(app) as client:
            response = client.get("/openapi.json")
            assert response.status_code == 200
            schema = response.json()
            assert schema["info"]["title"] == "JTIS API"
            assert "/api/v1/health" in schema["paths"]
            assert "/api/v1/events" in schema["paths"]
            assert "/api/v1/admin/tenants" in schema["paths"]
            assert "/api/v1/org" in schema["paths"]
            assert "/api/v1/rbac/roles" in schema["paths"]
            assert "/api/v1/users/me" in schema["paths"]

    def test_docs_available(self):
        with TestClient(app) as client:
            response = client.get("/docs")
            assert response.status_code == 200

    def test_redoc_available(self):
        with TestClient(app) as client:
            response = client.get("/redoc")
            assert response.status_code == 200

    def test_unauthenticated_events(self):
        """Unauthenticated requests should get 401 or 403."""
        with TestClient(app) as client:
            response = client.get("/api/v1/events")
            assert response.status_code in (401, 403)

    def test_unauthenticated_admin(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/admin/tenants")
            assert response.status_code in (401, 403)

    def test_standard_error_format(self):
        """Unhandled routes return proper error."""
        with TestClient(app) as client:
            response = client.get("/api/v1/nonexistent")
            assert response.status_code in (404, 405)
