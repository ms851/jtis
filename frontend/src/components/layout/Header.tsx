import { useTranslation } from 'react-i18next';
import { Navbar, Nav, Container, NavDropdown, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';
import { useEffect, useState } from 'react';
import { useSidebar } from '@/contexts/SidebarContext';
import { manualLoginRedirect } from '@/services/auth';

function getInitialTheme(): 'light' | 'dark' {
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') return stored;
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
  return 'light';
}

export function Header() {
  const { t, i18n } = useTranslation();
  const auth = useAuth();
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme);
  const { toggleSidebar } = useSidebar();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const handleLogin = async () => {
    try {
      await auth.signinRedirect();
    } catch (e) {
      console.warn('OIDC signinRedirect failed, using manual redirect:', e);
      manualLoginRedirect();
    }
  };

  return (
    <Navbar expand="lg" sticky="top" className="top-header">
      <Container fluid>
        {auth.isAuthenticated && (
          <Button
            variant="link"
            onClick={toggleSidebar}
            className="sidebar-toggle me-2"
            aria-label="Toggle sidebar"
          >
            ☰
          </Button>
        )}
        <Navbar.Brand as={Link} to="/">
          {t('app.title')}
        </Navbar.Brand>
        <Nav className="ms-auto align-items-center">
          <Button
            variant="link"
            onClick={toggleTheme}
            className="nav-link theme-toggle"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </Button>
          <NavDropdown title={t('nav.language')} id="lang-dropdown" align="end">
            <NavDropdown.Item onClick={() => changeLanguage('de')}>
              🇩🇪 Deutsch
            </NavDropdown.Item>
            <NavDropdown.Item onClick={() => changeLanguage('en')}>
              🇬🇧 English
            </NavDropdown.Item>
          </NavDropdown>
          {auth.isAuthenticated ? (
            <Nav.Link onClick={() => auth.removeUser()} className="ms-2">
              {t('nav.logout')} ({auth.user?.profile?.preferred_username})
            </Nav.Link>
          ) : (
            <Nav.Link onClick={handleLogin} className="ms-2">
              {t('nav.login')}
            </Nav.Link>
          )}
        </Nav>
      </Container>
    </Navbar>
  );
}
