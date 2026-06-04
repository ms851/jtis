import { useTranslation } from 'react-i18next';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';

export function Header() {
  const { t, i18n } = useTranslation();
  const auth = useAuth();
  

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container>
        <Navbar.Brand as={Link} to="/">
          {t('app.title')}
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/events">
              {t('nav.events')}
            </Nav.Link>
            <Nav.Link as={Link} to="/org">
              {t('nav.org')}
            </Nav.Link>
            <Nav.Link as={Link} to="/admin">
              {t('nav.admin')}
            </Nav.Link>
          </Nav>
          <Nav>
            <NavDropdown title={t('nav.language')} id="lang-dropdown">
              <NavDropdown.Item onClick={() => changeLanguage('de')}>
                🇩🇪 Deutsch
              </NavDropdown.Item>
              <NavDropdown.Item onClick={() => changeLanguage('en')}>
                🇬🇧 English
              </NavDropdown.Item>
            </NavDropdown>
            {auth.isAuthenticated ? (
              <Nav.Link onClick={() => auth.removeUser()}>
                {t('nav.logout')} ({auth.user?.profile?.preferred_username})
              </Nav.Link>
            ) : (
              <Nav.Link onClick={() => auth.signinRedirect()}>
                {t('nav.login')}
              </Nav.Link>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
