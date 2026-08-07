import { useCallback, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BANNER_DISMISSED_KEY = '@homeease/invite_banner_dismissed';
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

export function useInviteBanner(showFromRemote: boolean) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    (async () => {
      if (!showFromRemote) {
        setVisible(false);
        return;
      }
      const raw = await AsyncStorage.getItem(BANNER_DISMISSED_KEY);
      if (!raw) {
        setVisible(true);
        return;
      }
      const last = parseInt(raw, 10);
      if (Date.now() - last >= SEVEN_DAYS_MS) {
        setVisible(true);
      }
    })();
  }, [showFromRemote]);

  const dismiss = useCallback(async () => {
    await AsyncStorage.setItem(BANNER_DISMISSED_KEY, String(Date.now()));
    setVisible(false);
  }, []);

  return { visible, dismiss };
}

const FIRST_TASK_KEY = '@homeease/first_task_done';

export async function markFirstTaskDone(): Promise<boolean> {
  const done = await AsyncStorage.getItem(FIRST_TASK_KEY);
  if (done) return false;
  await AsyncStorage.setItem(FIRST_TASK_KEY, '1');
  return true;
}

export function useFirstTaskSharePrompt(onPrompt: () => void) {
  useEffect(() => {
    markFirstTaskDone().then((isFirst) => {
      if (isFirst) onPrompt();
    });
  }, [onPrompt]);
}
