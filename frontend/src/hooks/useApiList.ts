import { useCallback, useEffect, useState } from 'react';

export function useApiList<T>(loader: () => Promise<T[]>, enabled = true) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    setError(null);
    try {
      const result = await loader();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error');
    }
  }, [loader, enabled]);

  useEffect(() => {
    (async () => {
      await reload();
      setLoading(false);
    })();
  }, [reload]);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    await reload();
    setRefreshing(false);
  }, [reload]);

  return { data, setData, loading, refreshing, error, reload, refresh };
}
