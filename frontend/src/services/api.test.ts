import { describe, it, expect } from 'vitest';
import { setAuthToken } from './api';
import api from './api';

describe('API Client', () => {
  it('has correct base URL prefix', () => {
    expect(api.defaults.baseURL).toContain('/api/v1');
  });

  it('sets auth token', () => {
    setAuthToken('test-token');
    expect(api.defaults.headers.common['Authorization']).toBe(
      'Bearer test-token'
    );
  });

  it('clears auth token', () => {
    setAuthToken('test-token');
    setAuthToken(null);
    expect(api.defaults.headers.common['Authorization']).toBeUndefined();
  });
});
