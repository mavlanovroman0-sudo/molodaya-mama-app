import React, { useCallback } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useTranslation } from '../../hooks/useTranslation';
import { ErrorState } from '../../components/ErrorState';
import { useApiList } from '../../hooks/useApiList';
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';

type Sleep = {
  id: string;
  start_time: string;
  end_time: string | null;
  quality: number | null;
};

export function BabySleepScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [activeStart, setActiveStart] = React.useState<string | null>(null);

  const loader = useCallback(async () => {
    if (!token) return [];
    return api.get<Sleep[]>('/api/v1/baby/sleep', { token });
  }, [token]);

  const { data: sleeps, loading, refreshing, error, reload, refresh } = useApiList(loader, !!token);

  const startSleep = async () => {
    if (!token) return;
    try {
      const now = new Date().toISOString();
      const res = await api.post<Sleep>('/api/v1/baby/sleep', { start_time: now }, { token });
      setActiveStart(res.id);
      Alert.alert(t('screens.sleep_started'));
      await reload();
    } catch (e) {
      Alert.alert(t('common.error_title'), e instanceof Error ? e.message : '');
    }
  };

  const endSleep = async () => {
    if (!token) return;
    try {
      if (!activeStart) {
        const open = sleeps.find((s) => !s.end_time);
        if (!open) return;
        await api.put(`/api/v1/baby/sleep/${open.id}`, { end_time: new Date().toISOString(), quality: 4 }, { token });
      } else {
        await api.put(
          `/api/v1/baby/sleep/${activeStart}`,
          { end_time: new Date().toISOString(), quality: 4 },
          { token }
        );
        setActiveStart(null);
      }
      Alert.alert(t('screens.saved'));
      await reload();
    } catch (e) {
      Alert.alert(t('common.error_title'), e instanceof Error ? e.message : '');
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#7EB8DA" />
      </View>
    );
  }

  if (error && sleeps.length === 0) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.sleep')}</Text>
      <View style={styles.row}>
        <Pressable style={styles.bigBtn} onPress={startSleep}>
          <Text style={styles.bigBtnText}>{t('screens.start_sleep')}</Text>
        </Pressable>
        <Pressable style={[styles.bigBtn, styles.endBtn]} onPress={endSleep}>
          <Text style={styles.bigBtnText}>{t('screens.end_sleep')}</Text>
        </Pressable>
      </View>
      <FlatList
        data={sleeps}
        keyExtractor={(s) => s.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#7EB8DA" />}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              {item.start_time?.slice(0, 16).replace('T', ' ')}
              {item.end_time ? ` → ${item.end_time.slice(11, 16)}` : ` (${t('screens.in_progress')})`}
            </Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 12 },
  row: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  bigBtn: { flex: 1, backgroundColor: '#7EB8DA', padding: 14, borderRadius: 12, alignItems: 'center' },
  endBtn: { backgroundColor: '#D4919A' },
  bigBtnText: { color: '#fff', fontWeight: '700' },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8 },
  cardTitle: { fontSize: 15, color: '#3D2C2E' },
});
