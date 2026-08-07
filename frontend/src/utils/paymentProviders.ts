import { Platform } from 'react-native';
import type { PaymentProviderId, PaymentProviderInfo } from '../types/subscription';

export function filterProvidersForPlatform(
  providers: PaymentProviderInfo[]
): PaymentProviderInfo[] {
  const platform = Platform.OS === 'web' ? 'web' : Platform.OS;
  return providers.filter((p) => p.platforms.includes(platform));
}

export function defaultProviderId(providers: PaymentProviderInfo[]): PaymentProviderId {
  const yookassa = providers.find((p) => p.id === 'yookassa');
  if (yookassa) return 'yookassa';
  return (providers[0]?.id as PaymentProviderId) || 'yookassa';
}

export function providerLabelKey(id: PaymentProviderId): string {
  return `subscription.provider_${id}`;
}
