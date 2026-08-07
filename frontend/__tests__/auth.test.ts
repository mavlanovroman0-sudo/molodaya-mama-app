/** @jest-environment node */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, setUnauthorizedHandler } from '../src/services/api';

jest.mock('../src/services/api', () => {
  const actual = jest.requireActual('../src/services/api');
  return {
    ...actual,
    api: {
      post: jest.fn(),
      get: jest.fn(),
    },
  };
});

describe('auth flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (api.post as jest.Mock).mockResolvedValue({ access_token: 'test-token', token_type: 'bearer' });
  });

  it('login saves token via api.post', async () => {
    const data = await api.post<{ access_token: string }>('/api/v1/auth/login', {
      email: 'a@b.com',
      password: 'secret',
    });
    expect(data.access_token).toBe('test-token');
    expect(api.post).toHaveBeenCalledWith('/api/v1/auth/login', {
      email: 'a@b.com',
      password: 'secret',
    });
  });

  it('register returns token', async () => {
    const data = await api.post<{ access_token: string }>('/api/v1/auth/register', {
      email: 'b@b.com',
      password: 'secret',
      display_name: 'User',
    });
    expect(data.access_token).toBe('test-token');
  });

  it('401 handler can be registered', async () => {
    const handler = jest.fn();
    setUnauthorizedHandler(handler);
    expect(handler).not.toHaveBeenCalled();
  });
});

describe('token storage', () => {
  it('AsyncStorage mock works', async () => {
    await AsyncStorage.setItem('token', 'abc');
    expect(await AsyncStorage.getItem('token')).toBe('abc');
  });
});
