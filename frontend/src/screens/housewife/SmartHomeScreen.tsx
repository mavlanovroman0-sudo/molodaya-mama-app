import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useTranslation } from '../../hooks/useTranslation';
import { ErrorState } from '../../components/ErrorState';
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';

type Device = { id: string; name: string; device_type: string; is_on: boolean; value: number | null };
type Scenario = { id: string; name: string; actions: { device_id: string; action: string }[] };

export function SmartHomeScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [devices, setDevices] = useState<Device[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [newName, setNewName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const [devs, scs] = await Promise.all([
        api.get<Device[]>('/api/v1/devices', { token }),
        api.get<Scenario[]>('/api/v1/scenarios', { token }),
      ]);
      setDevices(devs);
      setScenarios(scs);
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.error_generic'));
    }
  }, [token, t]);

  useEffect(() => {
    (async () => {
      try {
        await load();
      } finally {
        setLoading(false);
      }
    })();
  }, [load]);

  const addDevice = async () => {
    if (!token || !newName.trim()) return;
    await api.post('/api/v1/devices', { name: newName.trim(), device_type: 'light' }, { token });
    setNewName('');
    await load();
  };

  const toggleDevice = async (dev: Device) => {
    if (!token) return;
    await api.put(`/api/v1/devices/${dev.id}`, { is_on: !dev.is_on }, { token });
    await load();
  };

  const runScenario = async (id: string) => {
    if (!token) return;
    await api.post(`/api/v1/scenarios/${id}/run`, undefined, { token });
    await load();
  };

  const createScenario = async () => {
    if (!token || devices.length === 0) return;
    const actions = devices.map((d) => ({ device_id: d.id, action: 'on' }));
    await api.post('/api/v1/scenarios', { name: t('screens.all_on'), actions }, { token });
    await load();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#D4919A" />
      </View>
    );
  }

  if (error && devices.length === 0) {
    return <ErrorState message={error} onRetry={load} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.smart_home')}</Text>
      <View style={styles.row}>
        <TextInput style={styles.input} placeholder={t('screens.device_name')} value={newName} onChangeText={setNewName} />
        <Pressable style={styles.addBtn} onPress={addDevice}>
          <Text style={styles.addBtnText}>+</Text>
        </Pressable>
      </View>
      <FlatList
        data={devices}
        keyExtractor={(d) => d.id}
        ListHeaderComponent={<Text style={styles.section}>{t('screens.devices')}</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.name}</Text>
            <Text style={styles.cardMeta}>{item.device_type}</Text>
            <Switch value={item.is_on} onValueChange={() => toggleDevice(item)} />
          </View>
        )}
        ListFooterComponent={
          <>
            <Text style={styles.section}>{t('screens.scenarios')}</Text>
            <Pressable style={styles.scBtn} onPress={createScenario}>
              <Text style={styles.scBtnText}>{t('screens.create_all_on')}</Text>
            </Pressable>
            {scenarios.map((s) => (
              <Pressable key={s.id} style={styles.card} onPress={() => runScenario(s.id)}>
                <Text style={styles.cardTitle}>▶ {s.name}</Text>
              </Pressable>
            ))}
          </>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 12 },
  section: { fontSize: 16, fontWeight: '600', marginVertical: 10, color: '#3D2C2E' },
  row: { flexDirection: 'row', marginBottom: 12 },
  input: { flex: 1, backgroundColor: '#fff', borderRadius: 10, padding: 12, marginRight: 8 },
  addBtn: { backgroundColor: '#D4919A', borderRadius: 10, width: 44, justifyContent: 'center', alignItems: 'center' },
  addBtnText: { color: '#fff', fontSize: 22 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8 },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  cardMeta: { fontSize: 12, color: '#7A6568' },
  scBtn: { backgroundColor: '#7EB8DA', padding: 12, borderRadius: 10, marginBottom: 8, alignItems: 'center' },
  scBtnText: { color: '#fff', fontWeight: '600' },
});
