"""Application configuration via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General
    env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    app_name: str = "JTIS"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://jtis:jtis_secret@postgres:5432/jtis"
    database_url_sync: str = "postgresql://jtis:jtis_secret@postgres:5432/jtis"

    # Keycloak
    keycloak_url: str = "http://keycloak:8080"
    keycloak_realm: str = "jtis"
    keycloak_client_id: str = "jtis-backend"
    keycloak_client_secret: str = "change-me"
    keycloak_hostname: str = ""  # External hostname e.g. 87.106.31.213:8080

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # CORS
    backend_cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Impersonation
    impersonation_timeout_minutes: int = 60

    # GDPR
    default_data_retention_days: int = 365

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    return Settings()
