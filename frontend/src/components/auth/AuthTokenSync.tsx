import { useEffect } from 'react';
import { useAuth } from 'react-oidc-context';
import { setAuthToken } from '@/services/api';

/**
 * Syncs the OIDC access token into the axios API client.
 * Must be rendered inside <AuthProvider>.
 */
export function AuthTokenSync() {
  const auth = useAuth();

  useEffect(() => {
    setAuthToken(auth.user?.access_token ?? null);
  }, [auth.user?.access_token]);

  return null;
}
