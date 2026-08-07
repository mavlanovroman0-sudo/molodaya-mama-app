import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useTranslation } from '../../hooks/useTranslation';
import { ErrorState } from '../../components/ErrorState';
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';

type Task = { id: string; name: string; default_duration_minutes: number | null; default_rate: number | null };
type Report = { total_minutes: number; total_hours: number; total_money_saved: number; entries_count: number };

export function ReportScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [taskName, setTaskName] = useState('');
  const [duration, setDuration] = useState('30');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const [taskList, rep] = await Promise.all([
        api.get<Task[]>('/api/v1/tasks', { token }),
        api.get<Report>('/api/v1/task_logs/report', { token }),
      ]);
      setTasks(taskList);
      setReport(rep);
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

  const addTask = async () => {
    if (!token || !taskName.trim()) return;
    await api.post(
      '/api/v1/tasks',
      { name: taskName.trim(), default_duration_minutes: parseInt(duration, 10) || 30, default_rate: 500 },
      { token }
    );
    setTaskName('');
    await load();
  };

  const logTask = async (task: Task) => {
    if (!token) return;
    await api.post(
      '/api/v1/task_logs',
      {
        task_id: task.id,
        duration_minutes: task.default_duration_minutes || 30,
        rate: task.default_rate || 0,
      },
      { token }
    );
    Alert.alert(t('screens.saved'));
    await load();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#D4919A" />
      </View>
    );
  }

  if (error && !report) {
    return <ErrorState message={error} onRetry={load} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.report')}</Text>
      {report && (
        <View style={styles.stats}>
          <Text style={styles.statBig}>{report.total_hours} {t('screens.hours')}</Text>
          <Text style={styles.statSub}>
            {t('screens.invisible_salary')}: {report.total_money_saved} ₽
          </Text>
          <Text style={styles.statSub}>{report.entries_count} {t('screens.entries')}</Text>
        </View>
      )}
      <View style={styles.row}>
        <TextInput style={styles.input} placeholder={t('screens.task_name')} value={taskName} onChangeText={setTaskName} />
        <Pressable style={styles.addBtn} onPress={addTask}>
          <Text style={styles.addBtnText}>+</Text>
        </Pressable>
      </View>
      <FlatList
        data={tasks}
        keyExtractor={(t) => t.id}
        renderItem={({ item }) => (
          <Pressable style={styles.card} onPress={() => logTask(item)}>
            <Text style={styles.cardTitle}>{item.name}</Text>
            <Text style={styles.cardMeta}>
              {item.default_duration_minutes} {t('screens.min')} · {item.default_rate} ₽/ч
            </Text>
            <Text style={styles.logHint}>{t('screens.tap_to_log')}</Text>
          </Pressable>
        )}
        ListEmptyComponent={<Text style={styles.empty}>{t('screens.empty_list')}</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 12 },
  stats: { backgroundColor: '#D4919A', borderRadius: 14, padding: 20, marginBottom: 16 },
  statBig: { fontSize: 32, fontWeight: '700', color: '#fff' },
  statSub: { fontSize: 14, color: '#fff', marginTop: 4, opacity: 0.9 },
  row: { flexDirection: 'row', marginBottom: 12 },
  input: { flex: 1, backgroundColor: '#fff', borderRadius: 10, padding: 12, marginRight: 8 },
  addBtn: { backgroundColor: '#D4919A', borderRadius: 10, width: 44, justifyContent: 'center', alignItems: 'center' },
  addBtnText: { color: '#fff', fontSize: 22 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8 },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  cardMeta: { fontSize: 12, color: '#7A6568', marginTop: 4 },
  logHint: { fontSize: 11, color: '#D4919A', marginTop: 6 },
  empty: { textAlign: 'center', color: '#7A6568', marginTop: 20 },
});
