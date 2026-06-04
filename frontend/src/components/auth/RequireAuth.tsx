import { useAuth } from 'react-oidc-context';
import { useTranslation } from 'react-i18next';
import { Container, Alert, Button, Spinner } from 'react-bootstrap';

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const { t } = useTranslation();

  if (auth.isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" role="status" />
        <p className="mt-3">{t('common.loading')}</p>
      </Container>
    );
  }

  if (!auth.isAuthenticated) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="warning">
          <Alert.Heading>{t('auth.loginRequired')}</Alert.Heading>
          <p>{t('auth.loginDescription', 'Bitte melden Sie sich an, um JTIS zu nutzen.')}</p>
          <Button
            variant="primary"
            size="lg"
            onClick={() => auth.signinRedirect()}
          >
            {t('nav.login')}
          </Button>
        </Alert>
      </Container>
    );
  }

  return <>{children}</>;
}
