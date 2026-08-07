import { useCallback, useEffect, useState } from 'react';
import { getCurrentLanguage, t as translate, type AppLanguage } from '../i18n';

/** Хук-обёртка над i18n (аналог react-i18next useTranslation). */
export function useTranslation() {
  const [lang, setLang] = useState<AppLanguage>(getCurrentLanguage());

  useEffect(() => {
    const id = setInterval(() => {
      const current = getCurrentLanguage();
      setLang((prev) => (prev !== current ? current : prev));
    }, 500);
    return () => clearInterval(id);
  }, []);

  const t = useCallback(
    (key: string, params?: Record<string, string>) => {
      let s = translate(key, lang);
      if (params) {
        for (const [k, v] of Object.entries(params)) {
          s = s.replace(`{${k}}`, v);
        }
      }
      return s;
    },
    [lang]
  );

  return { t, lang };
}
