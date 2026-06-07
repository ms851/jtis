import { useTranslation } from 'react-i18next';
import { Nav } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';
import { useSidebar } from '@/contexts/SidebarContext';

export function Sidebar() {
  const { t } = useTranslation();
  const location = useLocation();
  const auth = useAuth();
  const { sidebarOpen } = useSidebar();

  if (!auth.isAuthenticated) return null;

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <aside className={`sidebar ${sidebarOpen ? 'sidebar--open' : 'sidebar--closed'}`}>
      <Nav className="flex-column">
        <Nav.Link
          as={Link}
          to="/"
          className={`sidebar-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          📊 {t('nav.dashboard')}
        </Nav.Link>
        <Nav.Link
          as={Link}
          to="/events"
          className={`sidebar-link ${isActive('/events') ? 'active' : ''}`}
        >
          🏆 {t('nav.events')}
        </Nav.Link>
        <Nav.Link
          as={Link}
          to="/org"
          className={`sidebar-link ${isActive('/org') ? 'active' : ''}`}
        >
          🏢 {t('nav.org')}
        </Nav.Link>
        <Nav.Link
          as={Link}
          to="/admin"
          className={`sidebar-link ${isActive('/admin') ? 'active' : ''}`}
        >
          ⚙️ {t('nav.admin')}
        </Nav.Link>
      </Nav>
    </aside>
  );
}
