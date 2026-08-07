import { useEffect, useState } from 'react';
import { API_URL } from '../services/api';

export type RemoteConfigValues = {
  show_invite_banner: boolean;
};

const DEFAULTS: RemoteConfigValues = {
  show_invite_banner: true,
};

/**
 * MVP Remote Config через API бэкенда.
 * Для production с нативным билдом можно заменить на @react-native-firebase/remote-config.
 */
export function useRemoteConfig() {
  const [config, setConfig] = useState<RemoteConfigValues>(DEFAULTS);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch(`${API_URL}/api/v1/config/remote`);
        if (resp.ok) {
          const data = await resp.json();
          setConfig({ ...DEFAULTS, ...data });
        }
      } catch {
        /* офлайн — дефолты */
      } finally {
        setReady(true);
      }
    })();
  }, []);

  return { config, ready, getBoolean: (key: keyof RemoteConfigValues) => Boolean(config[key]) };
}
