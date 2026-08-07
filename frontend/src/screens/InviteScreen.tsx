import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTranslation } from '../hooks/useTranslation';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';
import { shareReferralLink } from '../utils/share';
import type { MainStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<MainStackParamList, 'Invite'>;

interface Stats {
  referral_code: string;
  invited_count: number;
  tokens_earned: number;
}

export function InviteScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<Stats | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<Stats>('/api/v1/referral/stats', { token });
      setStats(data);
    } catch {
      setStats({ referral_code: '—', invited_count: 0, tokens_earned: 0 });
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  const handleShare = async () => {
    if (!stats?.referral_code) return;
    const text = t('invite.invite_text');
    await shareReferralLink(stats.referral_code, text);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#D4919A" />
        <Text style={styles.loadingText}>{t('auth.loading')}</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Pressable style={styles.back} onPress={() => navigation.goBack()}>
        <Text style={styles.backText}>← {t('common.switch_role')}</Text>
      </Pressable>

      <Text style={styles.title}>{t('invite.invite_friends')}</Text>
      <Text style={styles.hint}>{t('invite.invite_hint')}</Text>

      <View style={styles.codeBox}>
        <Text style={styles.codeLabel}>{t('invite.invite_code')}</Text>
        <Text style={styles.code}>{stats?.referral_code}</Text>
      </View>

      <Pressable style={styles.shareBtn} onPress={handleShare}>
        <Text style={styles.shareBtnText}>{t('invite.share_link')}</Text>
      </Pressable>

      <View style={styles.statsCard}>
        <Text style={styles.statsTitle}>{t('invite.referral_stats')}</Text>
        <Text style={styles.statRow}>
          👥 {stats?.invited_count ?? 0}
        </Text>
        <Text style={styles.statRow}>
          🪙 {stats?.tokens_earned ?? 0} — {t('invite.referral_bonus')}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F4F0',
  },
  loadingText: {
    marginTop: 12,
    color: '#7A6568',
  },
  container: {
    padding: 24,
    paddingTop: 56,
    backgroundColor: '#F8F4F0',
    flexGrow: 1,
  },
  back: {
    marginBottom: 16,
  },
  backText: {
    color: '#7A6568',
    fontSize: 15,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#3D2C2E',
    marginBottom: 8,
  },
  hint: {
    fontSize: 15,
    color: '#7A6568',
    marginBottom: 24,
    lineHeight: 22,
  },
  codeBox: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E8E0DC',
  },
  codeLabel: {
    fontSize: 13,
    color: '#7A6568',
    marginBottom: 8,
  },
  code: {
    fontSize: 32,
    fontWeight: '700',
    letterSpacing: 4,
    color: '#D4919A',
  },
  shareBtn: {
    backgroundColor: '#7EB8DA',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 24,
  },
  shareBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  statsCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E8E0DC',
  },
  statsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#3D2C2E',
  },
  statRow: {
    fontSize: 15,
    color: '#5C4A4D',
    marginBottom: 6,
  },
});
