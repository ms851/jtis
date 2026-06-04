import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Inject auth token
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}

// Accept-Language interceptor
api.interceptors.request.use((config) => {
  const lang = localStorage.getItem('i18nextLng') || 'de';
  config.headers['Accept-Language'] = lang;
  return config;
});

// --- Events ---
export const eventsApi = {
  list: (params?: { limit?: number; offset?: number; status?: string }) =>
    api.get('/events', { params }),
  get: (id: string) => api.get(`/events/${id}`),
  create: (data: Record<string, unknown>) => api.post('/events', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/events/${id}`, data),
  delete: (id: string) => api.delete(`/events/${id}`),
  setModules: (id: string, modules: Record<string, unknown>[]) =>
    api.put(`/events/${id}/modules`, modules),
};

// --- Organization ---
export const orgApi = {
  get: () => api.get('/org'),
  update: (data: Record<string, unknown>) => api.patch('/org', data),
  listMembers: () => api.get('/org/members'),
  inviteMember: (data: { email: string; role: string }) =>
    api.post('/org/members', data),
  updateMemberRole: (id: string, role: string) =>
    api.patch(`/org/members/${id}`, null, { params: { role } }),
  removeMember: (id: string) => api.delete(`/org/members/${id}`),
};

// --- Admin ---
export const adminApi = {
  listTenants: (params?: { limit?: number; offset?: number }) =>
    api.get('/admin/tenants', { params }),
  createTenant: (data: Record<string, unknown>) =>
    api.post('/admin/tenants', data),
  updateTenant: (id: string, data: Record<string, unknown>) =>
    api.patch(`/admin/tenants/${id}`, data),
  suspendTenant: (id: string, reason?: string) =>
    api.post(`/admin/tenants/${id}/suspend`, null, { params: { reason } }),
  unsuspendTenant: (id: string) =>
    api.post(`/admin/tenants/${id}/unsuspend`),
  listPlans: () => api.get('/admin/plans'),
  createPlan: (data: Record<string, unknown>) =>
    api.post('/admin/plans', data),
  getAuditLog: (params?: { limit?: number; offset?: number }) =>
    api.get('/admin/audit-log', { params }),
  startImpersonation: (data: { target_user_id: string; reason?: string }) =>
    api.post('/admin/impersonate', data),
  endImpersonation: (id: string) =>
    api.post('/admin/impersonate/end', null, { params: { impersonation_id: id } }),
};

// --- RBAC ---
export const rbacApi = {
  listPermissions: () => api.get('/rbac/permissions'),
  listRoles: () => api.get('/rbac/roles'),
  createRole: (data: Record<string, unknown>) => api.post('/rbac/roles', data),
  updateRole: (id: string, data: Record<string, unknown>) =>
    api.patch(`/rbac/roles/${id}`, data),
  deleteRole: (id: string) => api.delete(`/rbac/roles/${id}`),
  assignRole: (data: Record<string, unknown>) =>
    api.post('/rbac/assignments', data),
};

// --- Users / GDPR ---
export const usersApi = {
  me: () => api.get('/users/me'),
  dataExport: () => api.get('/users/me/data-export'),
  listConsents: () => api.get('/users/me/consents'),
  grantConsent: (data: { consent_type: string; granted: boolean }) =>
    api.post('/users/me/consents', data),
};

// --- Health ---
export const healthApi = {
  check: () => api.get('/health'),
};

export default api;
