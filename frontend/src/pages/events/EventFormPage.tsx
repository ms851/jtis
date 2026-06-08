import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Form, Button, Row, Col, Card } from 'react-bootstrap';
import { useNavigate, useParams } from 'react-router-dom';
import { eventsApi } from '@/services/api';
import type { Event } from '@/types';

const AVAILABLE_MODULES = [
  { key: 'helpers', label: 'Helfer-/Personalplanung' },
  { key: 'venue', label: 'Venue-Management' },
  { key: 'transport', label: 'Transport-Management' },
  { key: 'communication', label: 'Kommunikation' },
  { key: 'tasks', label: 'Aufgabenmanagement' },
  { key: 'finance', label: 'Finanz-Controlling' },
  { key: 'hotel', label: 'Hotel-/Unterkunftsmanagement' },
];

export function EventFormPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;

  const [form, setForm] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    timezone: 'Europe/Berlin',
    status: 'draft',
  });
  const [activeModules, setActiveModules] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEdit && id) {
      eventsApi.get(id).then((res) => {
        const e: Event = res.data.data;
        setForm({
          name: e.name,
          description: e.description || '',
          start_date: e.start_date,
          end_date: e.end_date,
          timezone: e.timezone,
          status: e.status,
        });
        const mods: Record<string, boolean> = {};
        e.modules?.forEach((m) => {
          mods[m.module_key] = m.is_active;
        });
        setActiveModules(mods);
      });
    }
  }, [id, isEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const modules = Object.entries(activeModules)
        .filter(([_, active]) => active)
        .map(([key]) => ({ module_key: key, is_active: true }));

      if (isEdit && id) {
        await eventsApi.update(id, form);
        await eventsApi.setModules(id, modules);
      } else {
        await eventsApi.create({ ...form, modules });
      }
      navigate('/events');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Fehler beim Speichern';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Container className="py-4">
      <h2>{isEdit ? t('events.edit') : t('events.create')}</h2>
      {error && <div className="alert alert-danger" role="alert">{error}</div>}
      <Form onSubmit={handleSubmit}>
        <Row>
          <Col md={8}>
            <Card className="mb-3">
              <Card.Body>
                <Form.Group className="mb-3">
                  <Form.Label>{t('events.name')}</Form.Label>
                  <Form.Control
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>{t('events.description')}</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
                    }
                  />
                </Form.Group>
                <Row>
                  <Col>
                    <Form.Group className="mb-3">
                      <Form.Label>{t('events.startDate')}</Form.Label>
                      <Form.Control
                        type="date"
                        required
                        value={form.start_date}
                        onChange={(e) =>
                          setForm({ ...form, start_date: e.target.value })
                        }
                      />
                    </Form.Group>
                  </Col>
                  <Col>
                    <Form.Group className="mb-3">
                      <Form.Label>{t('events.endDate')}</Form.Label>
                      <Form.Control
                        type="date"
                        required
                        value={form.end_date}
                        onChange={(e) =>
                          setForm({ ...form, end_date: e.target.value })
                        }
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group className="mb-3">
                  <Form.Label>{t('events.timezone')}</Form.Label>
                  <Form.Control
                    required
                    value={form.timezone}
                    onChange={(e) =>
                      setForm({ ...form, timezone: e.target.value })
                    }
                  />
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card>
              <Card.Header>{t('events.modules')}</Card.Header>
              <Card.Body>
                {AVAILABLE_MODULES.map((mod) => (
                  <Form.Check
                    key={mod.key}
                    type="switch"
                    label={mod.label}
                    checked={!!activeModules[mod.key]}
                    onChange={(e) =>
                      setActiveModules({
                        ...activeModules,
                        [mod.key]: e.target.checked,
                      })
                    }
                    className="mb-2"
                  />
                ))}
              </Card.Body>
            </Card>
          </Col>
        </Row>
        <div className="mt-3">
          <Button type="submit" variant="primary" className="me-2" disabled={saving}>
            {saving ? t('common.loading', 'Speichern...') : t('common.save')}
          </Button>
          <Button variant="secondary" onClick={() => navigate('/events')}>
            {t('common.cancel')}
          </Button>
        </div>
      </Form>
    </Container>
  );
}
