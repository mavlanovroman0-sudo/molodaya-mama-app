/**
 * Модуль локализации
 * Автоопределение языка по IP (бэкенд) + Accept-Language (браузер)
 * Ручная смена сохраняется в AsyncStorage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';
import { Platform } from 'react-native';
import locales from './locales.json';

export type AppLanguage = 'ru' | 'kk' | 'uz' | 'tg' | 'ka' | 'ky';

const STORAGE_KEY = '@homeease/language';
const AUTO_DETECT_KEY = '@homeease/auto_detect_language';
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8001';

type LocaleData = Record<string, unknown>;

let currentLang: AppLanguage = 'ru';
let autoDetect = true;
const languageListeners = new Set<() => void>();

export const LANGUAGE_OPTIONS: { id: AppLanguage; nativeName: string }[] = [
  { id: 'ru', nativeName: 'Русский' },
  { id: 'kk', nativeName: 'Қазақша' },
  { id: 'uz', nativeName: 'Oʻzbekcha' },
  { id: 'tg', nativeName: 'Тоҷикӣ' },
  { id: 'ka', nativeName: 'ქართული' },
  { id: 'ky', nativeName: 'Кыргызча' },
];

function notifyLanguageListeners() {
  languageListeners.forEach((fn) => fn());
  if (Platform.OS === 'web' && typeof document !== 'undefined') {
    document.documentElement.lang = currentLang;
  }
}

export function subscribeLanguage(listener: () => void): () => void {
  languageListeners.add(listener);
  return () => {
    languageListeners.delete(listener);
  };
}

function getNested(obj: LocaleData, path: string): string {
  const keys = path.split('.');
  let cur: unknown = obj;
  for (const k of keys) {
    if (cur && typeof cur === 'object' && k in (cur as object)) {
      cur = (cur as LocaleData)[k];
    } else {
      return path;
    }
  }
  return typeof cur === 'string' ? cur : path;
}

export function t(key: string, lang?: AppLanguage): string {
  const l = lang || currentLang;
  const data = (locales as Record<string, LocaleData>)[l] || locales.ru;
  const val = getNested(data, key);
  if (val === key && l !== 'ru') {
    return getNested(locales.ru as LocaleData, key);
  }
  return val;
}

export function getCurrentLanguage(): AppLanguage {
  return currentLang;
}

export async function setLanguage(lang: AppLanguage, persist = true): Promise<void> {
  currentLang = lang;
  if (persist) {
    await AsyncStorage.setItem(STORAGE_KEY, lang);
  }
  notifyLanguageListeners();
}

export async function setAutoDetect(enabled: boolean): Promise<void> {
  autoDetect = enabled;
  await AsyncStorage.setItem(AUTO_DETECT_KEY, enabled ? '1' : '0');
}

export async function loadSavedLanguage(): Promise<void> {
  const saved = await AsyncStorage.getItem(STORAGE_KEY);
  const auto = await AsyncStorage.getItem(AUTO_DETECT_KEY);
  if (auto !== null) autoDetect = auto === '1';
  if (saved && !autoDetect) {
    currentLang = saved as AppLanguage;
  }
}

/** Автоопределение через API (IP + GPS на мобильном / Geolocation API на web) */
export async function detectAndApplyLanguage(): Promise<AppLanguage> {
  if (!autoDetect) return currentLang;

  let latitude: number | undefined;
  let longitude: number | undefined;

  try {
    if (Platform.OS === 'web' && typeof navigator !== 'undefined' && navigator.geolocation) {
      const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
      });
      latitude = pos.coords.latitude;
      longitude = pos.coords.longitude;
    } else {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        latitude = loc.coords.latitude;
        longitude = loc.coords.longitude;
      }
    }
  } catch {
    // GPS недоступен — fallback на IP
  }

  const acceptLanguage =
    Platform.OS === 'web' && typeof navigator !== 'undefined'
      ? navigator.language
      : undefined;

  try {
    const resp = await fetch(`${API_URL}/api/v1/geo/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(acceptLanguage ? { 'Accept-Language': acceptLanguage } : {}) },
      body: JSON.stringify({ latitude, longitude, accept_language: acceptLanguage }),
    });
    if (resp.ok) {
      const data = await resp.json();
      currentLang = data.language as AppLanguage;
      await AsyncStorage.setItem(STORAGE_KEY, currentLang);
      notifyLanguageListeners();
      return currentLang;
    }
  } catch {
    // офлайн — оставляем сохранённый язык
  }

  return currentLang;
}

export async function initI18n(): Promise<AppLanguage> {
  await loadSavedLanguage();
  return detectAndApplyLanguage();
}
