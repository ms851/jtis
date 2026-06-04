import { useTranslation } from 'react-i18next';
import { Container, Card, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

export function DashboardPage() {
  const { t } = useTranslation();

  return (
    <Container className="py-4">
      <h2>{t('nav.dashboard')}</h2>
      <p className="text-muted">{t('app.subtitle')}</p>
      <Row>
        <Col md={4} className="mb-3">
          <Card>
            <Card.Body>
              <Card.Title>{t('nav.events')}</Card.Title>
              <Card.Text>{t('events.title')}</Card.Text>
              <Link to="/events" className="btn btn-primary">
                {t('nav.events')}
              </Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-3">
          <Card>
            <Card.Body>
              <Card.Title>{t('nav.org')}</Card.Title>
              <Card.Text>{t('org.title')}</Card.Text>
              <Link to="/org" className="btn btn-primary">
                {t('nav.org')}
              </Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-3">
          <Card>
            <Card.Body>
              <Card.Title>{t('nav.admin')}</Card.Title>
              <Card.Text>{t('admin.title')}</Card.Text>
              <Link to="/admin" className="btn btn-primary">
                {t('nav.admin')}
              </Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}
