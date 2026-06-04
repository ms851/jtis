export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface SingleResponse<T> {
  data: T;
}

export interface Event {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  start_date: string;
  end_date: string;
  timezone: string;
  status: string;
  settings: Record<string, unknown> | null;
  modules: EventModule[];
  created_at: string;
  updated_at: string;
}

export interface EventModule {
  id: string;
  event_id: string;
  module_key: string;
  is_active: boolean;
  config: Record<string, unknown> | null;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  contact_email: string | null;
  address: Record<string, unknown> | null;
  settings: Record<string, unknown> | null;
  logo_url: string | null;
  subscription_plan_id: string | null;
  subscription_status: string;
  subscription_valid_until: string | null;
  is_suspended: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  display_name: string | null;
  keycloak_id: string | null;
  preferred_language: string;
  created_at: string;
}

export interface OrgMember {
  id: string;
  user_id: string;
  tenant_id: string;
  role: string;
  invitation_email: string | null;
  invitation_status: string;
  created_at: string;
  user?: User;
}

export interface Role {
  id: string;
  tenant_id: string;
  name: string;
  slug: string;
  description: string | null;
  is_system: boolean;
  permissions: Permission[];
  created_at: string;
}

export interface Permission {
  id: string;
  codename: string;
  description: string | null;
  module: string;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  slug: string;
  price_monthly: number | null;
  price_yearly: number | null;
  max_events: number | null;
  is_active: boolean;
}

export interface AuditLog {
  id: string;
  actor_user_id: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  details: Record<string, unknown> | null;
  is_impersonated: boolean;
  created_at: string;
}
