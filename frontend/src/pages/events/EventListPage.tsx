import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Table, Button, Badge, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { eventsApi } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import type { Event } from '@/types';

const statusVariant: Record<string, string> = {
  draft: 'secondary',
  active: 'success',
  completed: 'info',
  archived: 'dark',
};

export function EventListPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadEvents = () => {
    eventsApi.list().then((res) => {
      setEvents(res.data.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { loadEvents(); }, []);

  const nextStatus: Record<string, { target: string; label: string; variant: string }> = {
    draft: { target: 'active', label: t('events.activate'), variant: 'success' },
    active: { target: 'completed', label: t('events.complete'), variant: 'info' },
    completed: { target: 'archived', label: t('events.archive'), variant: 'dark' },
  };

  const handleStatusChange = async (eventId: string, newStatus: string) => {
    setError(null);
    try {
      await eventsApi.update(eventId, { status: newStatus });
      loadEvents();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Fehler beim Statuswechsel';
      setError(msg);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <Container className="py-4">
      {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{t('events.title')}</h2>
        <Button variant="primary" onClick={() => navigate('/events/new')}>
          {t('events.create')}
        </Button>
      </div>

      {events.length === 0 ? (
        <p className="text-muted">{t('events.noEvents')}</p>
      ) : (
        <Table striped hover responsive>
          <thead>
            <tr>
              <th>{t('events.name')}</th>
              <th>{t('events.startDate')}</th>
              <th>{t('events.endDate')}</th>
              <th>{t('events.status')}</th>
              <th>{t('events.modules')}</th>
              <th>{t('common.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td>
                  <Link to={`/events/${event.id}`}>{event.name}</Link>
                </td>
                <td>{event.start_date}</td>
                <td>{event.end_date}</td>
                <td>
                  <Badge bg={statusVariant[event.status] || 'secondary'}>
                    {t(`events.statuses.${event.status}`)}
                  </Badge>
                </td>
                <td>
                  {event.modules
                    ?.filter((m) => m.is_active)
                    .map((m) => m.module_key)
                    .join(', ') || '—'}
                </td>
                <td className="d-flex gap-1">
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={() => navigate(`/events/${event.id}/edit`)}
                  >
                    {t('common.edit')}
                  </Button>
                  {nextStatus[event.status] && (
                    <Button
                      variant={`outline-${nextStatus[event.status].variant}`}
                      size="sm"
                      onClick={() => handleStatusChange(event.id, nextStatus[event.status].target)}
                    >
                      {nextStatus[event.status].label}
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
}
