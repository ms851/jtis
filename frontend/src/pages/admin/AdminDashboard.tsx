import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Tabs,
  Tab,
  Table,
  Button,
  Badge,
  Card,
} from 'react-bootstrap';
import { adminApi } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import type { Organization, SubscriptionPlan, AuditLog } from '@/types';

export function AdminDashboard() {
  const { t } = useTranslation();
  const [tenants, setTenants] = useState<Organization[]>([]);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      adminApi.listTenants(),
      adminApi.listPlans(),
      adminApi.getAuditLog(),
    ])
      .then(([tenantsRes, plansRes, auditRes]) => {
        setTenants(tenantsRes.data.data);
        setPlans(plansRes.data.data);
        setAuditLog(auditRes.data.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleSuspend = async (id: string) => {
    await adminApi.suspendTenant(id, 'Admin action');
    const res = await adminApi.listTenants();
    setTenants(res.data.data);
  };

  const handleUnsuspend = async (id: string) => {
    await adminApi.unsuspendTenant(id);
    const res = await adminApi.listTenants();
    setTenants(res.data.data);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <Container className="py-4">
      <h2>{t('admin.title')}</h2>
      <Tabs defaultActiveKey="tenants" className="mb-3">
        <Tab eventKey="tenants" title={t('admin.tenants')}>
          <Table striped hover responsive>
            <thead>
              <tr>
                <th>{t('org.name')}</th>
                <th>Slug</th>
                <th>Status</th>
                <th>Subscription</th>
                <th>{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant) => (
                <tr key={tenant.id}>
                  <td>{tenant.name}</td>
                  <td>{tenant.slug}</td>
                  <td>
                    {tenant.is_suspended ? (
                      <Badge bg="danger">Suspended</Badge>
                    ) : (
                      <Badge bg="success">Active</Badge>
                    )}
                  </td>
                  <td>{tenant.subscription_status}</td>
                  <td>
                    {tenant.is_suspended ? (
                      <Button
                        size="sm"
                        variant="outline-success"
                        onClick={() => handleUnsuspend(tenant.id)}
                      >
                        {t('admin.unsuspend')}
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline-danger"
                        onClick={() => handleSuspend(tenant.id)}
                      >
                        {t('admin.suspend')}
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Tab>

        <Tab eventKey="plans" title={t('admin.plans')}>
          <Table striped responsive>
            <thead>
              <tr>
                <th>Name</th>
                <th>Monthly</th>
                <th>Yearly</th>
                <th>Max Events</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((plan) => (
                <tr key={plan.id}>
                  <td>{plan.name}</td>
                  <td>{plan.price_monthly ? `€${plan.price_monthly}` : '—'}</td>
                  <td>{plan.price_yearly ? `€${plan.price_yearly}` : '—'}</td>
                  <td>{plan.max_events ?? '∞'}</td>
                  <td>
                    <Badge bg={plan.is_active ? 'success' : 'secondary'}>
                      {plan.is_active ? 'Yes' : 'No'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Tab>

        <Tab eventKey="audit" title={t('admin.auditLog')}>
          <Table striped responsive size="sm">
            <thead>
              <tr>
                <th>Time</th>
                <th>Action</th>
                <th>Target</th>
                <th>Impersonated</th>
              </tr>
            </thead>
            <tbody>
              {auditLog.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.action}</td>
                  <td>
                    {log.target_type}
                    {log.target_id ? ` (${log.target_id.substring(0, 8)}…)` : ''}
                  </td>
                  <td>
                    {log.is_impersonated && <Badge bg="warning">Yes</Badge>}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Tab>
      </Tabs>
    </Container>
  );
}
