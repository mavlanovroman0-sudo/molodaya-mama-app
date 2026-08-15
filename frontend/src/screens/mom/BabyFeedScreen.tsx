import React, { useCallback } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useTranslation } from '../../hooks/useTranslation';
import { ErrorState } from '../../components/ErrorState';
import { useApiList } from '../../hooks/useApiList';
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';
import { BabyAlarmPanel } from '../../components/BabyAlarmPanel';

type Feed = {
  id: string;
  baby_name: string;
  feed_type: string;
  volume_ml: number | null;
  duration_minutes: number | null;
  feed_time: string | null;
};

export function BabyFeedScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [feedType, setFeedType] = React.useState<'breast' | 'formula'>('breast');
  const [duration, setDuration] = React.useState('15');

  const loader = useCallback(async () => {
    if (!token) return [];
    return api.get<Feed[]>('/api/v1/baby/feeds', { token });
  }, [token]);

  const { data: feeds, loading, refreshing, error, reload, refresh } = useApiList(loader, !!token);

  const addFeed = async () => {
    if (!token) return;
    try {
      await api.post(
        '/api/v1/baby/feeds',
        {
          feed_type: feedType,
          duration_minutes: parseInt(duration, 10) || 15,
          volume_ml: feedType === 'formula' ? 120 : null,
        },
        { token }
      );
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

  if (error && feeds.length === 0) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.feeding')}</Text>
      <View style={styles.typeRow}>
        {(['breast', 'formula'] as const).map((ft) => (
          <Pressable
            key={ft}
            style={[styles.chip, feedType === ft && styles.chipActive]}
            onPress={() => setFeedType(ft)}
          >
            <Text style={[styles.chipText, feedType === ft && styles.chipTextActive]}>
              {t(`screens.feed_${ft}`)}
            </Text>
          </Pressable>
        ))}
      </View>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={duration}
        onChangeText={setDuration}
        placeholder={t('screens.duration_min')}
      />
      <Pressable style={styles.bigBtn} onPress={addFeed}>
        <Text style={styles.bigBtnText}>+ {t('screens.add_feed')}</Text>
      </Pressable>
      <BabyAlarmPanel kind="feeding" />
      <FlatList
        data={feeds}
        keyExtractor={(f) => f.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#7EB8DA" />}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{t(`screens.feed_${item.feed_type}`)}</Text>
            <Text style={styles.cardMeta}>
              {item.duration_minutes} {t('screens.min')}
              {item.volume_ml ? ` · ${item.volume_ml} ml` : ''}
            </Text>
            <Text style={styles.time}>{item.feed_time?.slice(0, 16).replace('T', ' ')}</Text>
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
  typeRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: '#fff' },
  chipActive: { backgroundColor: '#7EB8DA' },
  chipText: { color: '#7A6568' },
  chipTextActive: { color: '#fff' },
  input: { backgroundColor: '#fff', borderRadius: 10, padding: 12, marginBottom: 12 },
  bigBtn: { backgroundColor: '#7EB8DA', padding: 16, borderRadius: 12, alignItems: 'center', marginBottom: 16 },
  bigBtnText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8 },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  cardMeta: { fontSize: 13, color: '#7A6568', marginTop: 4 },
  time: { fontSize: 11, color: '#AAA', marginTop: 4 },
});
