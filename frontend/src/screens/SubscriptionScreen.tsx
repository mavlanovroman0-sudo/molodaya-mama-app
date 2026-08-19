import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Linking,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { PaymentProviderSelector } from '../components/PaymentProviderSelector';
import { ErrorState } from '../components/ErrorState';
import { useTranslation } from '../hooks/useTranslation';
import { useSubscription } from '../hooks/useSubscription';
import type { ProfileStackParamList } from '../navigation/types';
import { ROLE_BUTTON_WIDTH } from '../theme/roleButtonStyles';
import { colors } from '../theme/formStyles';
import type { PaymentProviderId, SubscriptionPlan } from '../types/subscription';
import {
  defaultProviderId,
  filterProvidersForPlatform,
} from '../utils/paymentProviders';

type Props = {
  onAccessGranted?: () => void;
};

function showPayAlert(title: string, body?: string) {
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    window.alert(body ? `${title}\n${body}` : title);
    return;
  }
  Alert.alert(title, body);
}

function formatEndDate(iso: string | null | undefined, locale: string): string | null {
  if (!iso) return null;
  try {
    return new Date(iso).toLocaleDateString(locale, {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return null;
  }
}

export function SubscriptionScreen({ onAccessGranted }: Props) {
  const { t, lang } = useTranslation();
  const navigation = useNavigation<NativeStackNavigationProp<ProfileStackParamList>>();
  const { status, prices, loading, error, checkout, cancel, refresh } = useSubscription();
  const [busy, setBusy] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan>('monthly');
  const [selectedProvider, setSelectedProvider] = useState<PaymentProviderId>('yookassa');
  const [polling, setPolling] = useState(false);

  const displayPricing = prices ?? status?.pricing;
  const vatIncluded = prices?.vat_included ?? status?.vat_included ?? false;

  const providers = useMemo(
    () =>
      filterProvidersForPlatform(
        prices?.available_providers ?? status?.available_providers ?? []
      ),
    [prices?.available_providers, status?.available_providers]
  );

  useEffect(() => {
    if (providers.length) {
      setSelectedProvider(defaultProviderId(providers));
    }
  }, [providers]);

  useEffect(() => {
    if (status?.has_access && onAccessGranted) {
      onAccessGranted();
    }
  }, [status?.has_access, onAccessGranted]);

  useEffect(() => {
    if (!polling) return undefined;
    const timer = setInterval(() => {
      refresh();
    }, 5000);
    const stop = setTimeout(() => setPolling(false), 180000);
    return () => {
      clearInterval(timer);
      clearTimeout(stop);
    };
  }, [polling, refresh]);

  useEffect(() => {
    if (polling && status?.status === 'active' && status.plan !== 'trial') {
      setPolling(false);
    }
  }, [polling, status?.status, status?.plan]);

  if (loading && !status) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#FF69B4" />
      </View>
    );
  }

  if (error && !status) {
    return <ErrorState message={error} onRetry={refresh} />;
  }

  if (!status) {
    return <ErrorState onRetry={refresh} />;
  }

  const locale = lang === 'ru' ? 'ru-RU' : lang;
  const endDateLabel = formatEndDate(status.end_date || status.trial_end, locale);
  const showTrialBanner =
    status.status === 'trialing' || (!status.trial_used && status.status === 'expired');
  const isPaidActive =
    status.status === 'active' && status.plan !== 'trial' && status.plan !== null;
  const showCheckout = !isPaidActive;
  const selectedPrice =
    selectedPlan === 'monthly' ? displayPricing?.monthly : displayPricing?.yearly;

  const statusLabel =
    status.status === 'trialing'
      ? t('subscription.status_trial')
      : status.status === 'active'
        ? t('subscription.status_active')
        : status.status === 'canceled'
          ? t('subscription.status_canceled')
          : t('subscription.status_expired');

  const handleSubscribe = async () => {
    setBusy(true);
    try {
      const result = await checkout(selectedPlan, selectedProvider);
      if (result.checkout_url) {
        setPolling(true);
        if (Platform.OS === 'web' && typeof window !== 'undefined') {
          window.location.assign(result.checkout_url);
          return;
        }
        await Linking.openURL(result.checkout_url);
        showPayAlert(t('subscription.checkout_opened'), t('subscription.checkout_hint'));
      }
    } catch (e) {
      showPayAlert(t('subscription.error'), e instanceof Error ? e.message : '');
    } finally {
      setBusy(false);
    }
  };

  const handleCancel = async () => {
    Alert.alert(t('subscription.cancel_confirm_title'), t('subscription.cancel_confirm_body'), [
      { text: t('subscription.cancel_no'), style: 'cancel' },
      {
        text: t('subscription.cancel_yes'),
        style: 'destructive',
        onPress: async () => {
          try {
            await cancel();
            Alert.alert(t('subscription.cancelled'));
          } catch (e) {
            Alert.alert(t('subscription.error'), e instanceof Error ? e.message : '');
          }
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.emoji}>✨</Text>
      <Text style={styles.title}>{t('subscription.title')}</Text>
      <Text style={styles.subtitle}>{t('subscription.subtitle')}</Text>

      {showTrialBanner ? (
        <View style={styles.trialBanner}>
          <Text style={styles.trialBannerText}>
            {t('subscription.trial_banner', { days: String(status.trial_days) })}
          </Text>
        </View>
      ) : null}

      <View style={styles.card}>
        <Text style={styles.cardLabel}>{t('subscription.current_status')}</Text>
        <Text style={styles.cardValue}>{statusLabel}</Text>
        {endDateLabel ? (
          <Text style={styles.endDate}>
            {t('subscription.end_date', { date: endDateLabel })}
          </Text>
        ) : null}
        {status.has_access ? (
          <Text style={styles.days}>
            {t('subscription.days_left', { count: String(status.days_remaining) })}
          </Text>
        ) : null}
      </View>

      {showCheckout && displayPricing ? (
        <>
          <Text style={styles.section}>{t('subscription.choose_plan')}</Text>

          <View style={styles.planRow}>
            <Pressable
              style={[styles.planOption, selectedPlan === 'monthly' && styles.planOptionActive]}
              onPress={() => setSelectedPlan('monthly')}
              disabled={busy}
              accessibilityRole="radio"
              accessibilityState={{ selected: selectedPlan === 'monthly' }}
            >
              <Text
                style={[
                  styles.planOptionTitle,
                  selectedPlan === 'monthly' && styles.planOptionTitleActive,
                ]}
              >
                {t('subscription.plan_month')}
              </Text>
              <Text
                style={[
                  styles.planOptionPrice,
                  selectedPlan === 'monthly' && styles.planOptionPriceActive,
                ]}
              >
                {displayPricing.monthly}
              </Text>
            </Pressable>

            <Pressable
              style={[styles.planOption, selectedPlan === 'yearly' && styles.planOptionActive]}
              onPress={() => setSelectedPlan('yearly')}
              disabled={busy}
              accessibilityRole="radio"
              accessibilityState={{ selected: selectedPlan === 'yearly' }}
            >
              <Text
                style={[
                  styles.planOptionTitle,
                  selectedPlan === 'yearly' && styles.planOptionTitleActive,
                ]}
              >
                {t('subscription.plan_year')}
              </Text>
              <Text
                style={[
                  styles.planOptionPrice,
                  selectedPlan === 'yearly' && styles.planOptionPriceActive,
                ]}
              >
                {displayPricing.yearly}
              </Text>
              <Text style={styles.saveBadge}>{t('subscription.yearly_save')}</Text>
            </Pressable>
          </View>

          <PaymentProviderSelector
            providers={providers}
            selected={selectedProvider}
            onSelect={setSelectedProvider}
            disabled={busy}
          />

          <View style={styles.totalCard}>
            <Text style={styles.totalLabel}>
              {t('subscription.selected_total', { price: selectedPrice ?? '' })}
            </Text>
            {vatIncluded ? (
              <Text style={styles.vat}>{t('subscription.vat_included')}</Text>
            ) : null}
          </View>

          <Pressable
            style={[styles.subscribeBtn, busy && styles.disabled]}
            onPress={handleSubscribe}
            disabled={busy || !selectedPrice}
            accessibilityRole="button"
            accessibilityLabel={t('subscription.subscribe')}
          >
            {busy ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.subscribeBtnText}>{t('subscription.subscribe')}</Text>
            )}
          </Pressable>
        </>
      ) : null}

      <View style={styles.legalRow}>
        <Pressable onPress={() => navigation.navigate('PrivacyPolicy')}>
          <Text style={styles.legalLink}>{t('legal.privacy_title')}</Text>
        </Pressable>
        <Text style={styles.legalSep}> · </Text>
        <Pressable onPress={() => navigation.navigate('Terms')}>
          <Text style={styles.legalLink}>{t('legal.terms_title')}</Text>
        </Pressable>
      </View>

      {status.can_cancel ? (
        <Pressable style={styles.cancelBtn} onPress={handleCancel}>
          <Text style={styles.cancelText}>{t('subscription.cancel')}</Text>
        </Pressable>
      ) : null}

      <Pressable style={styles.refreshBtn} onPress={refresh} disabled={loading}>
        {loading ? (
          <ActivityIndicator size="small" color="#7EB8DA" />
        ) : (
          <Text style={styles.refreshText}>{t('subscription.refresh')}</Text>
        )}
      </Pressable>

      {polling ? (
        <Text style={styles.pollingHint}>{t('subscription.polling_hint')}</Text>
      ) : null}

      <Text style={styles.footnote}>
        {t('subscription.trial_info', { days: String(status.trial_days) })}
      </Text>

      <View style={styles.cardsBox}>
        <Text style={styles.cardsHeading}>{t('subscription.cards_heading')}</Text>
        <Text style={styles.cardsBody}>{t('subscription.cards_body')}</Text>
      </View>

      <Text style={styles.otherCountriesNote}>{t('subscription.other_countries_note')}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0' },
  content: { padding: 24, paddingTop: 8, alignItems: 'center', paddingBottom: 40 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F8F4F0' },
  emoji: { fontSize: 48, marginBottom: 8 },
  title: { fontSize: 26, fontWeight: '700', color: '#3D2C2E', textAlign: 'center' },
  subtitle: { fontSize: 15, color: '#7A6568', textAlign: 'center', marginBottom: 16 },
  trialBanner: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 16,
    marginBottom: 16,
    width: '100%',
    maxWidth: 360,
  },
  trialBannerText: {
    color: '#2E7D32',
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 20,
    width: '100%',
    maxWidth: 360,
    marginBottom: 20,
  },
  cardLabel: { fontSize: 13, color: '#7A6568' },
  cardValue: { fontSize: 20, fontWeight: '700', color: '#3D2C2E', marginTop: 4 },
  endDate: { fontSize: 14, color: '#4A4A4A', marginTop: 6 },
  days: { fontSize: 14, color: '#FF69B4', marginTop: 8, fontWeight: '600' },
  section: {
    fontSize: 16,
    fontWeight: '600',
    alignSelf: 'flex-start',
    marginBottom: 12,
    width: '100%',
    maxWidth: 360,
    color: '#3D2C2E',
  },
  planRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
    width: '100%',
    maxWidth: 360,
  },
  planOption: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 14,
    borderWidth: 2,
    borderColor: '#E8E0DC',
    paddingVertical: 14,
    paddingHorizontal: 12,
    alignItems: 'center',
    minHeight: 88,
    justifyContent: 'center',
  },
  planOptionActive: {
    borderColor: '#FF69B4',
    backgroundColor: '#F0EFFF',
  },
  planOptionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#4A4A4A',
  },
  planOptionTitleActive: {
    color: '#FF69B4',
  },
  planOptionPrice: {
    fontSize: 18,
    fontWeight: '700',
    color: '#3D2C2E',
    marginTop: 4,
  },
  planOptionPriceActive: {
    color: '#FF69B4',
  },
  saveBadge: {
    fontSize: 11,
    color: '#2E7D32',
    marginTop: 4,
    fontWeight: '600',
  },
  totalCard: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  totalLabel: {
    fontSize: 17,
    fontWeight: '700',
    color: '#3D2C2E',
    textAlign: 'center',
  },
  vat: {
    fontSize: 12,
    color: '#7A6568',
    textAlign: 'center',
    marginTop: 4,
  },
  subscribeBtn: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    height: 56,
    width: ROLE_BUTTON_WIDTH,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  subscribeBtnText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '700',
  },
  legalRow: { flexDirection: 'row', marginTop: 8, marginBottom: 8 },
  legalLink: { color: '#7A6568', fontSize: 12, textDecorationLine: 'underline' },
  legalSep: { color: '#7A6568', fontSize: 12 },
  cancelBtn: { marginTop: 12, padding: 12 },
  cancelText: { color: '#C44', fontSize: 15, fontWeight: '600' },
  refreshBtn: { marginTop: 4, padding: 12, minHeight: 44, justifyContent: 'center' },
  refreshText: { color: '#7EB8DA', fontSize: 15, fontWeight: '600' },
  pollingHint: {
    fontSize: 13,
    color: '#FF69B4',
    textAlign: 'center',
    marginTop: 8,
    maxWidth: 320,
  },
  footnote: { fontSize: 12, color: '#7A6568', textAlign: 'center', marginTop: 16, maxWidth: 360 },
  cardsBox: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    marginTop: 16,
  },
  cardsHeading: {
    fontSize: 15,
    fontWeight: '700',
    color: '#3D2C2E',
    marginBottom: 8,
    textAlign: 'center',
  },
  cardsBody: {
    fontSize: 13,
    lineHeight: 20,
    color: '#4A4A4A',
    textAlign: 'left',
  },
  otherCountriesNote: {
    fontSize: 13,
    lineHeight: 20,
    color: '#7A6568',
    textAlign: 'center',
    marginTop: 18,
    maxWidth: 360,
  },
  disabled: { opacity: 0.6 },
});
