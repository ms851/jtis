import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from 'react-oidc-context';
import { Header } from '@/components/layout/Header';
import { DashboardPage } from '@/pages/DashboardPage';
import { EventListPage } from '@/pages/events/EventListPage';
import { EventFormPage } from '@/pages/events/EventFormPage';
import { OrgSettingsPage } from '@/pages/org/OrgSettingsPage';
import { AdminDashboard } from '@/pages/admin/AdminDashboard';
import { CallbackPage } from '@/pages/auth/CallbackPage';
import { oidcConfig } from '@/services/auth';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <AuthProvider {...oidcConfig}>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/events" element={<EventListPage />} />
          <Route path="/events/new" element={<EventFormPage />} />
          <Route path="/events/:id/edit" element={<EventFormPage />} />
          <Route path="/org" element={<OrgSettingsPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/callback" element={<CallbackPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
