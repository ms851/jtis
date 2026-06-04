import { Alert, Button, Container } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

interface Props {
  userName: string;
  orgName: string;
  onEnd: () => void;
}

export function ImpersonationBanner({ userName, orgName, onEnd }: Props) {
  const { t } = useTranslation();

  return (
    <Alert variant="warning" className="mb-0 rounded-0 text-center">
      <Container>
        <strong>
          {t('admin.impersonation.banner', { user: userName, org: orgName })}
        </strong>
        <Button
          variant="outline-dark"
          size="sm"
          className="ms-3"
          onClick={onEnd}
        >
          {t('admin.impersonation.end')}
        </Button>
      </Container>
    </Alert>
  );
}
