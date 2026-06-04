import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Card,
  Form,
  Button,
  Table,
  Row,
  Col,
  Modal,
} from 'react-bootstrap';
import { orgApi } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import type { Organization, OrgMember } from '@/types';

export function OrgSettingsPage() {
  const { t } = useTranslation();
  const [org, setOrg] = useState<Organization | null>(null);
  const [members, setMembers] = useState<OrgMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [inviteForm, setInviteForm] = useState({ email: '', role: 'viewer' });

  useEffect(() => {
    Promise.all([orgApi.get(), orgApi.listMembers()])
      .then(([orgRes, membersRes]) => {
        setOrg(orgRes.data.data);
        setMembers(membersRes.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleOrgSave = async () => {
    if (!org) return;
    await orgApi.update({
      name: org.name,
      contact_email: org.contact_email,
    });
  };

  const handleInvite = async () => {
    await orgApi.inviteMember(inviteForm);
    setShowInvite(false);
    const res = await orgApi.listMembers();
    setMembers(res.data);
  };

  if (loading) return <LoadingSpinner />;
  if (!org) return null;

  return (
    <Container className="py-4">
      <h2>{t('org.title')}</h2>
      <Row>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>{t('org.settings')}</Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>{t('org.name')}</Form.Label>
                <Form.Control
                  value={org.name}
                  onChange={(e) => setOrg({ ...org, name: e.target.value })}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>{t('org.email')}</Form.Label>
                <Form.Control
                  type="email"
                  value={org.contact_email || ''}
                  onChange={(e) =>
                    setOrg({ ...org, contact_email: e.target.value })
                  }
                />
              </Form.Group>
              <Button onClick={handleOrgSave}>{t('common.save')}</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header className="d-flex justify-content-between">
              {t('org.members')}
              <Button size="sm" onClick={() => setShowInvite(true)}>
                {t('org.inviteMember')}
              </Button>
            </Card.Header>
            <Card.Body>
              <Table size="sm">
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>{t('org.role')}</th>
                    <th>{t('common.actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {members.map((m) => (
                    <tr key={m.id}>
                      <td>{m.user?.email || m.invitation_email}</td>
                      <td>{m.role}</td>
                      <td>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={async () => {
                            await orgApi.removeMember(m.id);
                            setMembers(members.filter((x) => x.id !== m.id));
                          }}
                        >
                          {t('common.delete')}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Modal show={showInvite} onHide={() => setShowInvite(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{t('org.inviteMember')}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Email</Form.Label>
            <Form.Control
              type="email"
              value={inviteForm.email}
              onChange={(e) =>
                setInviteForm({ ...inviteForm, email: e.target.value })
              }
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>{t('org.role')}</Form.Label>
            <Form.Select
              value={inviteForm.role}
              onChange={(e) =>
                setInviteForm({ ...inviteForm, role: e.target.value })
              }
            >
              <option value="viewer">Viewer</option>
              <option value="org_admin">Org Admin</option>
              <option value="event_admin">Event Admin</option>
            </Form.Select>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowInvite(false)}>
            {t('common.cancel')}
          </Button>
          <Button onClick={handleInvite}>{t('common.confirm')}</Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}
