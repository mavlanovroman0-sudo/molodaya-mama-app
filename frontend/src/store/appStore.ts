import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { AppLanguage } from '../i18n';

export type UserRole = 'housewife' | 'young_mom';

interface DashboardFeature {
  id: string;
  title_key: string;
  icon: string;
  route: string;
}

interface AppState {
  token: string | null;
  activeRole: UserRole | null;
  clearRole: () => void;
  language: AppLanguage;
  district: string | null;
  tokenBalance: number;
  features: DashboardFeature[];
  isOffline: boolean;
  authInitialRoute: 'Login' | 'Register';
  subscriptionRefreshNonce: number;
  setToken: (token: string | null) => void;
  setRole: (role: UserRole | null) => void;
  setLanguage: (lang: AppLanguage) => void;
  setDashboard: (data: { features: DashboardFeature[]; token_balance: number; shared_data: { district?: string } }) => void;
  setOffline: (v: boolean) => void;
  setAuthInitialRoute: (route: 'Login' | 'Register') => void;
  requestSubscriptionRefresh: () => void;
  hydrate: () => Promise<void>;
  persistCache: () => Promise<void>;
}

const CACHE_KEY = '@homeease/cache';

export const useAppStore = create<AppState>((set, get) => ({
  token: null,
  activeRole: null,
  language: 'ru',
  district: null,
  tokenBalance: 0,
  features: [],
  isOffline: false,
  authInitialRoute: 'Login' as const,
  subscriptionRefreshNonce: 0,

  setToken: (token) => {
    set({ token });
    if (token) AsyncStorage.setItem('token', token);
    else AsyncStorage.removeItem('token');
  },

  setRole: (role) => {
    set({ activeRole: role });
    if (role) AsyncStorage.setItem('@homeease/role', role);
    else AsyncStorage.removeItem('@homeease/role');
  },

  clearRole: () => set({ activeRole: null }),

  setLanguage: (language) => set({ language }),

  setDashboard: (data) =>
    set({
      features: data.features,
      tokenBalance: data.token_balance,
      district: data.shared_data?.district ?? null,
    }),

  setOffline: (isOffline) => set({ isOffline }),

  setAuthInitialRoute: (authInitialRoute) => set({ authInitialRoute }),

  requestSubscriptionRefresh: () =>
    set((state) => ({ subscriptionRefreshNonce: state.subscriptionRefreshNonce + 1 })),

  hydrate: async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      if (storedToken) set({ token: storedToken });

      const raw = await AsyncStorage.getItem(CACHE_KEY);
      if (raw) {
        const cached = JSON.parse(raw);
        set({
          activeRole: cached.activeRole ?? null,
          features: cached.features ?? [],
          tokenBalance: cached.tokenBalance ?? 0,
          district: cached.district ?? null,
        });
      }
      const role = await AsyncStorage.getItem('@homeease/role');
      if (role) set({ activeRole: role as UserRole });
    } catch {
      /* ignore */
    }
  },

  persistCache: async () => {
    const { activeRole, features, tokenBalance, district } = get();
    await AsyncStorage.setItem(
      CACHE_KEY,
      JSON.stringify({ activeRole, features, tokenBalance, district })
    );
  },
}));
