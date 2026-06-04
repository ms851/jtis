"""Unit tests for configuration."""

from app.core.config import Settings


class TestConfig:
    def test_defaults(self):
        s = Settings()
        assert s.app_name == "JTIS"
        assert s.api_v1_prefix == "/api/v1"
        assert s.impersonation_timeout_minutes == 60
        assert s.default_data_retention_days == 365

    def test_cors_origins(self):
        s = Settings()
        assert "http://localhost:5173" in s.backend_cors_origins
