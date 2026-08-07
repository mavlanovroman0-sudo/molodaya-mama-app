import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import { API_PATHS } from '../services/apiPaths';
import { useAppStore } from '../store/appStore';
import type {
  CheckoutResult,
  PaymentProviderId,
  SubscriptionPlan,
  SubscriptionPrices,
  SubscriptionStatus,
} from '../types/subscription';

export type { SubscriptionStatus, PaymentProviderId, SubscriptionPlan, SubscriptionPrices };

export function useSubscription() {
  const token = useAppStore((s) => s.token);
  const refreshNonce = useAppStore((s) => s.subscriptionRefreshNonce);
  const [status, setStatus] = useState<SubscriptionStatus | null>(null);
  const [prices, setPrices] = useState<SubscriptionPrices | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!token) {
      setStatus(null);
      setPrices(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [statusRes, pricesRes] = await Promise.allSettled([
        api.get<SubscriptionStatus>(API_PATHS.subscription.status, { token }),
        api.get<SubscriptionPrices>(API_PATHS.subscription.prices, { token }),
      ]);

      if (statusRes.status === 'fulfilled') {
        setStatus(statusRes.value);
      } else {
        throw statusRes.reason;
      }

      if (pricesRes.status === 'fulfilled') {
        setPrices(pricesRes.value);
      } else {
        setPrices(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    refresh();
  }, [refresh, refreshNonce]);

  const checkout = useCallback(
    async (plan: SubscriptionPlan, provider: PaymentProviderId): Promise<CheckoutResult> => {
      if (!token) throw new Error('Not authenticated');
      return api.post<CheckoutResult>(
        API_PATHS.subscription.checkout,
        { plan, provider },
        { token }
      );
    },
    [token]
  );

  const verify = useCallback(
    async (paymentId: string) => {
      if (!token) return null;
      const result = await api.post<{ verified: boolean; subscription: SubscriptionStatus }>(
        API_PATHS.subscription.verify,
        { payment_id: paymentId },
        { token }
      );
      if (result.subscription) {
        setStatus(result.subscription);
      }
      return result;
    },
    [token]
  );

  const cancel = useCallback(async () => {
    if (!token) return;
    await api.post(API_PATHS.subscription.cancel, undefined, { token });
    await refresh();
  }, [token, refresh]);

  return { status, prices, loading, error, refresh, checkout, verify, cancel };
}
