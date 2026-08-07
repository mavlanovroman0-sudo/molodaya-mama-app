import React, { useCallback } from 'react';
import {
  ActivityIndicator,
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

type Item = { id: string; item_name: string; age_months: number; is_bought: boolean };

const DEFAULT_ITEMS: Record<number, string[]> = {
  0: ['Кроватка', 'Пелёнки', 'Бутылочки'],
  3: ['Погремушка', 'Развивающий коврик'],
  6: ['Прикорм', 'Стульчик для кормления'],
  12: ['Ходунки', 'Развивающие книги'],
};

export function BabyChecklistScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [ageMonths, setAgeMonths] = React.useState('0');
  const [newItem, setNewItem] = React.useState('');

  const loader = useCallback(async () => {
    if (!token) return [];
    return api.get<Item[]>('/api/v1/baby/checklist', { token });
  }, [token]);

  const { data: items, loading, refreshing, error, reload, refresh } = useApiList(loader, !!token);

  const seedByAge = async () => {
    if (!token) return;
    const age = parseInt(ageMonths, 10) || 0;
    const names = DEFAULT_ITEMS[age] || DEFAULT_ITEMS[0];
    for (const name of names) {
      await api.post('/api/v1/baby/checklist', { age_months: age, item_name: name }, { token });
    }
    await reload();
  };

  const addItem = async () => {
    if (!token || !newItem.trim()) return;
    await api.post(
      '/api/v1/baby/checklist',
      { age_months: parseInt(ageMonths, 10) || 0, item_name: newItem.trim() },
      { token }
    );
    setNewItem('');
    await reload();
  };

  const toggle = async (item: Item) => {
    if (!token) return;
    await api.put(`/api/v1/baby/checklist/${item.id}`, { is_bought: !item.is_bought }, { token });
    await reload();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#7EB8DA" />
      </View>
    );
  }

  if (error && items.length === 0) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.checklist')}</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder={t('screens.age_months')}
        value={ageMonths}
        onChangeText={setAgeMonths}
      />
      <Pressable style={styles.seedBtn} onPress={seedByAge}>
        <Text style={styles.seedText}>{t('screens.seed_checklist')}</Text>
      </Pressable>
      <View style={styles.row}>
        <TextInput style={styles.inputFlex} placeholder={t('screens.item_name')} value={newItem} onChangeText={setNewItem} />
        <Pressable style={styles.addBtn} onPress={addItem}>
          <Text style={styles.addBtnText}>+</Text>
        </Pressable>
      </View>
      <FlatList
        data={items}
        keyExtractor={(i) => i.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#7EB8DA" />}
        renderItem={({ item }) => (
          <Pressable style={styles.card} onPress={() => toggle(item)}>
            <Text style={[styles.cardTitle, item.is_bought && styles.bought]}>
              {item.is_bought ? '✓ ' : '○ '}
              {item.item_name} ({item.age_months} {t('screens.mo')})
            </Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 12 },
  input: { backgroundColor: '#fff', borderRadius: 10, padding: 12, marginBottom: 8 },
  seedBtn: { backgroundColor: '#E8F4FA', padding: 10, borderRadius: 10, marginBottom: 12, alignItems: 'center' },
  seedText: { color: '#3D6B8E', fontWeight: '600' },
  row: { flexDirection: 'row', marginBottom: 12 },
  inputFlex: { flex: 1, backgroundColor: '#fff', borderRadius: 10, padding: 12, marginRight: 8 },
  addBtn: { backgroundColor: '#7EB8DA', borderRadius: 10, width: 44, justifyContent: 'center', alignItems: 'center' },
  addBtnText: { color: '#fff', fontSize: 22 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8 },
  cardTitle: { fontSize: 16, color: '#3D2C2E' },
  bought: { textDecorationLine: 'line-through', color: '#AAA' },
});
