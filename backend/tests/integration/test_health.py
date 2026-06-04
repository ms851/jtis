"""Integration tests for health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


class TestHealth:
    def test_health_check(self):
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "jtis-backend"
