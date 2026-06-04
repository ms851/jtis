"""Initial schema with RLS.

Revision ID: 001_initial
Revises: None
Create Date: 2026-06-04
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- subscription_plans ---
    op.create_table(
        "subscription_plans",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("price_monthly", sa.Numeric(10, 2)),
        sa.Column("price_yearly", sa.Numeric(10, 2)),
        sa.Column("max_events", sa.Integer),
        sa.Column("max_helpers", sa.Integer),
        sa.Column("max_storage_mb", sa.Integer),
        sa.Column("enabled_modules", JSONB),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- organizations ---
    op.create_table(
        "organizations",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("address", JSONB),
        sa.Column("logo_url", sa.Text),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("settings", JSONB),
        sa.Column("subscription_plan_id", UUID, sa.ForeignKey("subscription_plans.id")),
        sa.Column("subscription_status", sa.String(20), server_default="trial"),
        sa.Column("subscription_valid_until", sa.DateTime(timezone=True)),
        sa.Column("is_suspended", sa.Boolean, server_default="false"),
        sa.Column("suspended_reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("keycloak_id", UUID, unique=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("preferred_language", sa.String(5), server_default="de"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    # --- organization_members ---
    op.create_table(
        "organization_members",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id"), nullable=False, index=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(50), server_default="viewer"),
        sa.Column("invitation_email", sa.String(255)),
        sa.Column("invitation_status", sa.String(20), server_default="accepted"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    # --- permissions ---
    op.create_table(
        "permissions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("codename", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("is_system", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_role_tenant_slug"),
    )

    # --- role_permissions ---
    op.create_table(
        "role_permissions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("role_id", UUID, sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", UUID, sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    # --- user_event_roles ---
    op.create_table(
        "user_event_roles",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id"), nullable=False, index=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("event_id", UUID, nullable=True),
        sa.Column("role_id", UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "user_id", "event_id", "role_id", name="uq_user_event_role"),
    )

    # --- events ---
    op.create_table(
        "events",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("settings", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    # Add FK on user_event_roles.event_id now that events table exists
    op.create_foreign_key(
        "fk_user_event_roles_event_id",
        "user_event_roles",
        "events",
        ["event_id"],
        ["id"],
    )

    # --- event_modules ---
    op.create_table(
        "event_modules",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id"), nullable=False, index=True),
        sa.Column("event_id", UUID, sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_key", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("config", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", UUID),
        sa.Column("updated_by", UUID),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    # --- impersonation_log ---
    op.create_table(
        "impersonation_log",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("admin_user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.Text),
        sa.Column("actions_count", sa.Integer, server_default="0"),
    )

    # --- platform_audit_log ---
    op.create_table(
        "platform_audit_log",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("actor_user_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50)),
        sa.Column("target_id", UUID),
        sa.Column("details", JSONB),
        sa.Column("ip_address", INET),
        sa.Column("is_impersonated", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- consents (GDPR) ---
    op.create_table(
        "consents",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tenant_id", UUID, sa.ForeignKey("organizations.id")),
        sa.Column("consent_type", sa.String(100), nullable=False),
        sa.Column("granted", sa.Boolean, nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("ip_address", INET),
    )

    # --- Row-Level Security Policies ---
    tenant_tables = [
        "organization_members", "roles", "user_event_roles",
        "events", "event_modules",
    ]
    for table in tenant_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
        )

    # --- Seed default permissions ---
    op.execute("""
        INSERT INTO permissions (id, codename, description, module) VALUES
        (gen_random_uuid(), 'events:read', 'View events', 'events'),
        (gen_random_uuid(), 'events:write', 'Create/edit events', 'events'),
        (gen_random_uuid(), 'events:admin', 'Full event management', 'events'),
        (gen_random_uuid(), 'helpers:read', 'View helpers', 'helpers'),
        (gen_random_uuid(), 'helpers:write', 'Manage helpers', 'helpers'),
        (gen_random_uuid(), 'helpers:admin', 'Full helper management', 'helpers'),
        (gen_random_uuid(), 'transport:read', 'View transport', 'transport'),
        (gen_random_uuid(), 'transport:write', 'Manage transport', 'transport'),
        (gen_random_uuid(), 'transport:admin', 'Full transport management', 'transport'),
        (gen_random_uuid(), 'venue:read', 'View venues', 'venue'),
        (gen_random_uuid(), 'venue:write', 'Manage venues', 'venue'),
        (gen_random_uuid(), 'venue:admin', 'Full venue management', 'venue'),
        (gen_random_uuid(), 'org:read', 'View org settings', 'org'),
        (gen_random_uuid(), 'org:write', 'Manage org settings', 'org'),
        (gen_random_uuid(), 'org:admin', 'Full org management', 'org'),
        (gen_random_uuid(), 'rbac:read', 'View roles/permissions', 'rbac'),
        (gen_random_uuid(), 'rbac:write', 'Manage roles', 'rbac'),
        (gen_random_uuid(), 'rbac:admin', 'Full RBAC management', 'rbac'),
        (gen_random_uuid(), 'finance:read', 'View finances', 'finance'),
        (gen_random_uuid(), 'finance:write', 'Manage finances', 'finance'),
        (gen_random_uuid(), 'communication:read', 'View communications', 'communication'),
        (gen_random_uuid(), 'communication:write', 'Send communications', 'communication')
    """)


def downgrade() -> None:
    tables = [
        "consents", "platform_audit_log", "impersonation_log",
        "event_modules", "events", "user_event_roles",
        "role_permissions", "roles", "permissions",
        "organization_members", "users", "organizations",
        "subscription_plans",
    ]
    for t in tables:
        op.drop_table(t)
