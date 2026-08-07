import { useCallback, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';

const TOKEN_KEY = 'token';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const setToken = useAppStore((s) => s.setToken);

  const login = useCallback(
    async (email: string, password: string): Promise<void> => {
      setLoading(true);
      try {
        const data = await api.post<TokenResponse>('/api/v1/auth/login', { email, password });
        await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
        useAppStore.getState().setAuthInitialRoute('Login');
        setToken(data.access_token);
      } finally {
        setLoading(false);
      }
    },
    [setToken]
  );

  const register = useCallback(
    async (email: string, password: string, name: string): Promise<void> => {
      setLoading(true);
      try {
        const data = await api.post<TokenResponse>('/api/v1/auth/register', {
          email,
          password,
          display_name: name,
        });
        await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
        useAppStore.getState().setAuthInitialRoute('Login');
        setToken(data.access_token);
      } finally {
        setLoading(false);
      }
    },
    [setToken]
  );

  const logout = useCallback(async (): Promise<void> => {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem('@homeease/role');
    setToken(null);
    useAppStore.getState().setRole(null);
  }, [setToken]);

  return { login, register, logout, loading };
}

export async function loadStoredToken(): Promise<string | null> {
  return AsyncStorage.getItem(TOKEN_KEY);
}

export { TOKEN_KEY };
