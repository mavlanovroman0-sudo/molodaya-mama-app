import React, { useCallback, useEffect, useState } from 'react';
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
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';

type ListRow = { id: string; name: string; items_count: number };
type ItemRow = { id: string; name: string; quantity: number; unit: string | null; is_bought: boolean };

export function ShoppingListsScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [lists, setLists] = useState<ListRow[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [items, setItems] = useState<ItemRow[]>([]);
  const [newListName, setNewListName] = useState('');
  const [newItemName, setNewItemName] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLists = useCallback(async () => {
    if (!token) return;
    const data = await api.get<ListRow[]>('/api/v1/shopping/lists', { token });
    setLists(data);
  }, [token]);

  const loadItems = useCallback(
    async (listId: string) => {
      if (!token) return;
      const data = await api.get<ItemRow[]>(`/api/v1/shopping/items/${listId}`, { token });
      setItems(data);
    },
    [token]
  );

  const reload = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      await loadLists();
      if (selectedId) await loadItems(selectedId);
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.error_generic'));
    }
  }, [token, loadLists, loadItems, selectedId, t]);

  useEffect(() => {
    (async () => {
      try {
        await reload();
      } finally {
        setLoading(false);
      }
    })();
  }, [reload]);

  const onRefresh = async () => {
    setRefreshing(true);
    await reload();
    setRefreshing(false);
  };

  const createList = async () => {
    if (!token || !newListName.trim()) return;
    try {
      await api.post('/api/v1/shopping/lists', { name: newListName.trim() }, { token });
      setNewListName('');
      await reload();
    } catch (e) {
      Alert.alert(t('common.error_title'), e instanceof Error ? e.message : '');
    }
  };

  const addItem = async () => {
    if (!token || !selectedId || !newItemName.trim()) return;
    try {
      await api.post('/api/v1/shopping/items', { list_id: selectedId, name: newItemName.trim() }, { token });
      setNewItemName('');
      await loadItems(selectedId);
      await loadLists();
    } catch (e) {
      Alert.alert(t('common.error_title'), e instanceof Error ? e.message : '');
    }
  };

  const toggleBought = async (item: ItemRow) => {
    if (!token) return;
    try {
      await api.put(`/api/v1/shopping/items/${item.id}`, { is_bought: !item.is_bought }, { token });
      if (selectedId) await loadItems(selectedId);
    } catch (e) {
      Alert.alert(t('common.error_title'), e instanceof Error ? e.message : '');
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#D4919A" />
      </View>
    );
  }

  if (error && lists.length === 0 && !selectedId) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  const refreshControl = <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#D4919A" />;

  if (selectedId) {
    const listName = lists.find((l) => l.id === selectedId)?.name || '';
    return (
      <View style={styles.container}>
        <Pressable onPress={() => setSelectedId(null)}>
          <Text style={styles.back}>← {listName}</Text>
        </Pressable>
        <View style={styles.row}>
          <TextInput
            style={styles.input}
            placeholder={t('screens.shopping_item_placeholder')}
            value={newItemName}
            onChangeText={setNewItemName}
          />
          <Pressable style={styles.addBtn} onPress={addItem}>
            <Text style={styles.addBtnText}>+</Text>
          </Pressable>
        </View>
        <FlatList
          data={items}
          keyExtractor={(i) => i.id}
          refreshControl={refreshControl}
          renderItem={({ item }) => (
            <Pressable style={styles.itemRow} onPress={() => toggleBought(item)}>
              <Text style={[styles.itemText, item.is_bought && styles.bought]}>
                {item.is_bought ? '✓ ' : '○ '}
                {item.name}
                {item.quantity ? ` (${item.quantity}${item.unit ? ` ${item.unit}` : ''})` : ''}
              </Text>
            </Pressable>
          )}
          ListEmptyComponent={error ? <ErrorState message={error} onRetry={reload} /> : undefined}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.shopping')}</Text>
      <View style={styles.row}>
        <TextInput
          style={styles.input}
          placeholder={t('screens.shopping_list_placeholder')}
          value={newListName}
          onChangeText={setNewListName}
        />
        <Pressable style={styles.addBtn} onPress={createList}>
          <Text style={styles.addBtnText}>+</Text>
        </Pressable>
      </View>
      <FlatList
        data={lists}
        keyExtractor={(l) => l.id}
        refreshControl={refreshControl}
        renderItem={({ item }) => (
          <Pressable
            style={styles.listCard}
            onPress={() => {
              setSelectedId(item.id);
              loadItems(item.id);
            }}
          >
            <Text style={styles.listTitle}>{item.name}</Text>
            <Text style={styles.listMeta}>
              {item.items_count} {t('screens.items')}
            </Text>
          </Pressable>
        )}
        ListEmptyComponent={
          error ? (
            <ErrorState message={error} onRetry={reload} />
          ) : (
            <Text style={styles.empty}>{t('screens.empty_list')}</Text>
          )
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 16 },
  row: { flexDirection: 'row', marginBottom: 12 },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginRight: 8,
  },
  addBtn: { backgroundColor: '#D4919A', borderRadius: 10, width: 44, justifyContent: 'center', alignItems: 'center' },
  addBtnText: { color: '#fff', fontSize: 22, fontWeight: '700' },
  listCard: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 10 },
  listTitle: { fontSize: 17, fontWeight: '600', color: '#3D2C2E' },
  listMeta: { fontSize: 13, color: '#7A6568', marginTop: 4 },
  back: { fontSize: 16, color: '#D4919A', marginBottom: 12 },
  itemRow: { backgroundColor: '#fff', borderRadius: 10, padding: 14, marginBottom: 8 },
  itemText: { fontSize: 16, color: '#3D2C2E' },
  bought: { textDecorationLine: 'line-through', color: '#AAA' },
  empty: { textAlign: 'center', color: '#7A6568', marginTop: 40 },
});
