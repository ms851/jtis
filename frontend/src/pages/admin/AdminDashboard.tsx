import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Tabs,
  Tab,
  Table,
  Button,
  Badge,
  Modal,
  Form,
  Row,
  Col,
  Alert,
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
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [showTenantModal, setShowTenantModal] = useState(false);
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [tenantForm, setTenantForm] = useState({ name: '', slug: '', contact_email: '' });
  const [planForm, setPlanForm] = useState({
    name: '', slug: '', price_monthly: '', price_yearly: '',
    max_events: '', max_helpers: '', max_storage_mb: '',
  });
  const [saving, setSaving] = useState(false);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      adminApi.listTenants(),
      adminApi.listPlans(),
      adminApi.getAuditLog(),
    ])
      .then(([tenantsRes, plansRes, auditRes]) => {
        setTenants(tenantsRes.data.data || []);
        setPlans(plansRes.data.data || []);
        setAuditLog(auditRes.data.data || []);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || 'Fehler beim Laden');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadData(); }, []);

  const handleSuspend = async (id: string) => {
    await adminApi.suspendTenant(id, 'Admin action');
    loadData();
  };

  const handleUnsuspend = async (id: string) => {
    await adminApi.unsuspendTenant(id);
    loadData();
  };

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminApi.createTenant(tenantForm);
      setShowTenantModal(false);
      setTenantForm({ name: '', slug: '', contact_email: '' });
      loadData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Fehler';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminApi.createPlan({
        name: planForm.name,
        slug: planForm.slug,
        price_monthly: planForm.price_monthly ? parseFloat(planForm.price_monthly) : null,
        price_yearly: planForm.price_yearly ? parseFloat(planForm.price_yearly) : null,
        max_events: planForm.max_events ? parseInt(planForm.max_events) : null,
        max_helpers: planForm.max_helpers ? parseInt(planForm.max_helpers) : null,
        max_storage_mb: planForm.max_storage_mb ? parseInt(planForm.max_storage_mb) : null,
        is_active: true,
      });
      setShowPlanModal(false);
      setPlanForm({ name: '', slug: '', price_monthly: '', price_yearly: '', max_events: '', max_helpers: '', max_storage_mb: '' });
      loadData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Fehler';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <Container className="py-4">
      <h2>{t('admin.title')}</h2>

      {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}

      <Tabs defaultActiveKey="tenants" className="mb-3">
        {/* --- Organisationen --- */}
        <Tab eventKey="tenants" title={t('admin.tenants')}>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="mb-0">{t('admin.tenants')}</h5>
            <Button variant="primary" onClick={() => setShowTenantModal(true)}>
              + {t('admin.createTenant')}
            </Button>
          </div>
          {tenants.length === 0 ? (
            <Alert variant="info">{t('common.noData')}</Alert>
          ) : (
            <Table striped hover responsive>
              <thead>
                <tr>
                  <th>{t('org.name')}</th>
                  <th>Slug</th>
                  <th>Status</th>
                  <th>Subscription</th>
                  <th>{t('org.email')}</th>
                  <th>{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((tenant) => (
                  <tr key={tenant.id}>
                    <td><strong>{tenant.name}</strong></td>
                    <td><code>{tenant.slug}</code></td>
                    <td>
                      {tenant.is_suspended ? (
                        <Badge bg="danger">Gesperrt</Badge>
                      ) : (
                        <Badge bg="success">Aktiv</Badge>
                      )}
                    </td>
                    <td>
                      <Badge bg="info">{tenant.subscription_status || 'trial'}</Badge>
                    </td>
                    <td>{tenant.contact_email || '—'}</td>
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
                      {' '}
                      <Button size="sm" variant="outline-secondary">
                        {t('common.edit')}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Tab>

        {/* --- Tarifmodelle --- */}
        <Tab eventKey="plans" title={t('admin.plans')}>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="mb-0">{t('admin.plans')}</h5>
            <Button variant="primary" onClick={() => setShowPlanModal(true)}>
              + {t('admin.createPlan', 'Tarif erstellen')}
            </Button>
          </div>
          {plans.length === 0 ? (
            <Alert variant="info">{t('common.noData')}</Alert>
          ) : (
            <Table striped responsive>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Slug</th>
                  <th>Monatlich</th>
                  <th>Jährlich</th>
                  <th>Max Events</th>
                  <th>Aktiv</th>
                  <th>{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {plans.map((plan) => (
                  <tr key={plan.id}>
                    <td><strong>{plan.name}</strong></td>
                    <td><code>{plan.slug}</code></td>
                    <td>{plan.price_monthly ? `€${plan.price_monthly}` : '—'}</td>
                    <td>{plan.price_yearly ? `€${plan.price_yearly}` : '—'}</td>
                    <td>{plan.max_events ?? '∞'}</td>
                    <td>
                      <Badge bg={plan.is_active ? 'success' : 'secondary'}>
                        {plan.is_active ? 'Ja' : 'Nein'}
                      </Badge>
                    </td>
                    <td>
                      <Button size="sm" variant="outline-secondary">
                        {t('common.edit')}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Tab>

        {/* --- Audit-Log --- */}
        <Tab eventKey="audit" title={t('admin.auditLog')}>
          <h5 className="mb-3">{t('admin.auditLog')}</h5>
          {auditLog.length === 0 ? (
            <Alert variant="info">{t('common.noData')}</Alert>
          ) : (
            <Table striped responsive size="sm">
              <thead>
                <tr>
                  <th>Zeitpunkt</th>
                  <th>Aktion</th>
                  <th>Ziel</th>
                  <th>Impersonated</th>
                </tr>
              </thead>
              <tbody>
                {auditLog.map((log) => (
                  <tr key={log.id}>
                    <td>{new Date(log.created_at).toLocaleString()}</td>
                    <td><code>{log.action}</code></td>
                    <td>
                      {log.target_type}
                      {log.target_id ? ` (${log.target_id.substring(0, 8)}…)` : ''}
                    </td>
                    <td>
                      {log.is_impersonated && <Badge bg="warning">Ja</Badge>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Tab>
      </Tabs>

      {/* --- Modal: Organisation anlegen --- */}
      <Modal show={showTenantModal} onHide={() => setShowTenantModal(false)} size="lg">
        <Form onSubmit={handleCreateTenant}>
          <Modal.Header closeButton>
            <Modal.Title>{t('admin.createTenant')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>{t('org.name')} *</Form.Label>
                  <Form.Control
                    required
                    value={tenantForm.name}
                    onChange={(e) => setTenantForm({ ...tenantForm, name: e.target.value })}
                    placeholder="z.B. Deutscher Judo-Bund"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Slug *</Form.Label>
                  <Form.Control
                    required
                    value={tenantForm.slug}
                    onChange={(e) => setTenantForm({ ...tenantForm, slug: e.target.value })}
                    placeholder="z.B. djb"
                  />
                  <Form.Text className="text-muted">URL-freundlicher Bezeichner (Kleinbuchstaben, keine Leerzeichen)</Form.Text>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>{t('org.email')}</Form.Label>
              <Form.Control
                type="email"
                value={tenantForm.contact_email}
                onChange={(e) => setTenantForm({ ...tenantForm, contact_email: e.target.value })}
                placeholder="info@example.org"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowTenantModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" type="submit" disabled={saving}>
              {saving ? t('common.loading') : t('common.create')}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* --- Modal: Tarif erstellen --- */}
      <Modal show={showPlanModal} onHide={() => setShowPlanModal(false)} size="lg">
        <Form onSubmit={handleCreatePlan}>
          <Modal.Header closeButton>
            <Modal.Title>Neuen Tarif erstellen</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Name *</Form.Label>
                  <Form.Control
                    required
                    value={planForm.name}
                    onChange={(e) => setPlanForm({ ...planForm, name: e.target.value })}
                    placeholder="z.B. Pro"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Slug *</Form.Label>
                  <Form.Control
                    required
                    value={planForm.slug}
                    onChange={(e) => setPlanForm({ ...planForm, slug: e.target.value })}
                    placeholder="z.B. pro"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Monatspreis (€)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    value={planForm.price_monthly}
                    onChange={(e) => setPlanForm({ ...planForm, price_monthly: e.target.value })}
                    placeholder="49.00"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Jahrespreis (€)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    value={planForm.price_yearly}
                    onChange={(e) => setPlanForm({ ...planForm, price_yearly: e.target.value })}
                    placeholder="499.00"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Max. Events</Form.Label>
                  <Form.Control
                    type="number"
                    value={planForm.max_events}
                    onChange={(e) => setPlanForm({ ...planForm, max_events: e.target.value })}
                    placeholder="∞ (leer = unbegrenzt)"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Max. Helfer/Event</Form.Label>
                  <Form.Control
                    type="number"
                    value={planForm.max_helpers}
                    onChange={(e) => setPlanForm({ ...planForm, max_helpers: e.target.value })}
                    placeholder="∞"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Max. Speicher (MB)</Form.Label>
                  <Form.Control
                    type="number"
                    value={planForm.max_storage_mb}
                    onChange={(e) => setPlanForm({ ...planForm, max_storage_mb: e.target.value })}
                    placeholder="1024"
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPlanModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" type="submit" disabled={saving}>
              {saving ? t('common.loading') : t('common.create')}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
}
