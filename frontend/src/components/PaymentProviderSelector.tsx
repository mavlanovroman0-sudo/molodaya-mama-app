import React from 'react';
import { Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import { useTranslation } from '../hooks/useTranslation';
import type { PaymentProviderId, PaymentProviderInfo } from '../types/subscription';
import { providerLabelKey } from '../utils/paymentProviders';

const PROVIDER_ICONS: Record<PaymentProviderId, string> = {
  yookassa: '💳',
  rustore: '🛒',
  tbank: '🏦',
};

type Props = {
  providers: PaymentProviderInfo[];
  selected: PaymentProviderId;
  onSelect: (id: PaymentProviderId) => void;
  disabled?: boolean;
};

export function PaymentProviderSelector({ providers, selected, onSelect, disabled }: Props) {
  const { t } = useTranslation();

  if (providers.length <= 1) {
    return null;
  }

  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>{t('subscription.payment_method')}</Text>
      <View style={styles.row}>
        {providers.map((provider) => {
          const active = provider.id === selected;
          return (
            <Pressable
              key={provider.id}
              style={[styles.chip, active && styles.chipActive, disabled && styles.disabled]}
              onPress={() => onSelect(provider.id)}
              disabled={disabled}
              accessibilityRole="radio"
              accessibilityState={{ selected: active }}
              accessibilityLabel={t(providerLabelKey(provider.id))}
            >
              <Text style={styles.icon}>{PROVIDER_ICONS[provider.id]}</Text>
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {t(providerLabelKey(provider.id))}
              </Text>
            </Pressable>
          );
        })}
      </View>
      {Platform.OS === 'web' ? (
        <Text style={styles.hint}>{t('subscription.card_hint')}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: '100%',
    maxWidth: 360,
    marginBottom: 16,
  },
  title: {
    fontSize: 15,
    fontWeight: '600',
    color: '#3D2C2E',
    marginBottom: 10,
  },
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E8E0DC',
    backgroundColor: '#fff',
    gap: 6,
  },
  chipActive: {
    borderColor: '#6C63FF',
    backgroundColor: '#F0EFFF',
  },
  chipText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4A4A4A',
  },
  chipTextActive: {
    color: '#6C63FF',
  },
  icon: {
    fontSize: 16,
  },
  hint: {
    marginTop: 8,
    fontSize: 12,
    color: '#7A6568',
    lineHeight: 16,
  },
  disabled: {
    opacity: 0.6,
  },
});
