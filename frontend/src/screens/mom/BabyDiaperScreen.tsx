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
import { BabyAlarmPanel } from '../../components/BabyAlarmPanel';

type Diaper = { id: string; diaper_type: string; change_time: string | null };

export function BabyDiaperScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [dtype, setDtype] = React.useState<'wet' | 'dirty' | 'both'>('wet');

  const loader = useCallback(async () => {
    if (!token) return [];
    return api.get<Diaper[]>('/api/v1/baby/diapers', { token });
  }, [token]);

  const { data: diapers, loading, refreshing, error, reload, refresh } = useApiList(loader, !!token);

  const addDiaper = async () => {
    if (!token) return;
    try {
      await api.post('/api/v1/baby/diapers', { diaper_type: dtype }, { token });
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

  if (error && diapers.length === 0) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.diapers')}</Text>
      <View style={styles.typeRow}>
        {(['wet', 'dirty', 'both'] as const).map((dt) => (
          <Pressable
            key={dt}
            style={[styles.chip, dtype === dt && styles.chipActive]}
            onPress={() => setDtype(dt)}
          >
            <Text style={[styles.chipText, dtype === dt && styles.chipTextActive]}>
              {t(`screens.diaper_${dt}`)}
            </Text>
          </Pressable>
        ))}
      </View>
      <Pressable style={styles.bigBtn} onPress={addDiaper}>
        <Text style={styles.bigBtnText}>+ {t('screens.add_diaper')}</Text>
      </Pressable>
      <BabyAlarmPanel kind="diaper" />
      <FlatList
        data={diapers}
        keyExtractor={(d) => d.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#7EB8DA" />}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{t(`screens.diaper_${item.diaper_type}`)}</Text>
            <Text style={styles.time}>{item.change_time?.slice(0, 16).replace('T', ' ')}</Text>
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
  chip: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, backgroundColor: '#fff' },
  chipActive: { backgroundColor: '#7EB8DA' },
  chipText: { color: '#7A6568' },
  chipTextActive: { color: '#fff' },
  bigBtn: { backgroundColor: '#7EB8DA', padding: 16, borderRadius: 12, alignItems: 'center', marginBottom: 16 },
  bigBtnText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8 },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  time: { fontSize: 11, color: '#AAA', marginTop: 4 },
});
