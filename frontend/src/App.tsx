import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from 'react-oidc-context';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { SidebarProvider } from '@/contexts/SidebarContext';
import { RequireAuth } from '@/components/auth/RequireAuth';
import { DashboardPage } from '@/pages/DashboardPage';
import { EventListPage } from '@/pages/events/EventListPage';
import { EventFormPage } from '@/pages/events/EventFormPage';
import { OrgSettingsPage } from '@/pages/org/OrgSettingsPage';
import { AdminDashboard } from '@/pages/admin/AdminDashboard';
import { CallbackPage } from '@/pages/auth/CallbackPage';
import { oidcConfig } from '@/services/auth';
import '@/scss/main.scss';

function App() {
  return (
    <AuthProvider {...oidcConfig}>
      <BrowserRouter>
        <SidebarProvider>
          <Header />
          <div className="app-layout">
            <Sidebar />
            <main className="app-content">
              <Routes>
                <Route path="/callback" element={<CallbackPage />} />
                <Route path="/" element={<RequireAuth><DashboardPage /></RequireAuth>} />
                <Route path="/events" element={<RequireAuth><EventListPage /></RequireAuth>} />
                <Route path="/events/new" element={<RequireAuth><EventFormPage /></RequireAuth>} />
                <Route path="/events/:id/edit" element={<RequireAuth><EventFormPage /></RequireAuth>} />
                <Route path="/org" element={<RequireAuth><OrgSettingsPage /></RequireAuth>} />
                <Route path="/admin" element={<RequireAuth><AdminDashboard /></RequireAuth>} />
              </Routes>
            </main>
          </div>
        </SidebarProvider>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
