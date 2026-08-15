import { Platform } from 'react-native';
import {
  setAutoDetect,
  setLanguage,
  type AppLanguage,
} from '../i18n';
import { useAppStore } from '../store/appStore';
import { api } from './api';

export async function applyUserLanguage(lang: AppLanguage): Promise<void> {
  await setAutoDetect(false);
  await setLanguage(lang, true);
  useAppStore.getState().setLanguage(lang);
  if (Platform.OS === 'web' && typeof document !== 'undefined') {
    document.documentElement.lang = lang;
  }
  const token = useAppStore.getState().token;
  if (!token) return;
  await api.patch(
    '/api/v1/geo/language',
    { language: lang, auto_detect_language: false },
    { token }
  );
}
