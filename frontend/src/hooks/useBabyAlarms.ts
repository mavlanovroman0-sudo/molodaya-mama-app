import { useCallback, useEffect, useState } from 'react';
import {
  addAlarm,
  listAlarms,
  removeAlarm,
  updateAlarm,
  type AlarmKind,
  type BabyAlarm,
} from '../services/babyAlarms';

export function useBabyAlarms(kind: AlarmKind) {
  const [alarms, setAlarms] = useState<BabyAlarm[]>([]);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    const rows = await listAlarms(kind);
    setAlarms(rows);
  }, [kind]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const create = useCallback(
    async (hour: number, minute: number) => {
      setError(null);
      try {
        await addAlarm(kind, hour, minute);
        await reload();
      } catch (e) {
        setError(e instanceof Error ? e.message : 'error');
        throw e;
      }
    },
    [kind, reload]
  );

  const toggle = useCallback(
    async (id: string, enabled: boolean) => {
      await updateAlarm(id, { enabled });
      await reload();
    },
    [reload]
  );

  const edit = useCallback(
    async (id: string, hour: number, minute: number) => {
      await updateAlarm(id, { hour, minute, enabled: true });
      await reload();
    },
    [reload]
  );

  const remove = useCallback(
    async (id: string) => {
      await removeAlarm(id);
      await reload();
    },
    [reload]
  );

  return { alarms, error, create, toggle, edit, remove, reload };
}
