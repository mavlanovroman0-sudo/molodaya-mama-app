import React, { useState } from 'react';
import { Alert, Pressable, StyleSheet, Switch, Text, View } from 'react-native';
import { useTranslation } from '../hooks/useTranslation';
import { useBabyAlarms } from '../hooks/useBabyAlarms';
import {
  formatAlarmTime,
  wrapHour,
  wrapMinute,
  type AlarmKind,
  type BabyAlarm,
} from '../services/babyAlarms';

type Props = {
  kind: AlarmKind;
};

function TimeStepper({
  hour,
  minute,
  onChange,
}: {
  hour: number;
  minute: number;
  onChange: (hour: number, minute: number) => void;
}) {
  return (
    <View style={styles.stepperRow}>
      <Stepper value={hour} pad onMinus={() => onChange(wrapHour(hour - 1), minute)} onPlus={() => onChange(wrapHour(hour + 1), minute)} />
      <Text style={styles.colon}>:</Text>
      <Stepper
        value={minute}
        pad
        onMinus={() => onChange(hour, wrapMinute(minute - 1))}
        onPlus={() => onChange(hour, wrapMinute(minute + 1))}
      />
    </View>
  );
}

function Stepper({
  value,
  pad,
  onMinus,
  onPlus,
}: {
  value: number;
  pad?: boolean;
  onMinus: () => void;
  onPlus: () => void;
}) {
  const label = pad ? String(value).padStart(2, '0') : String(value);
  return (
    <View style={styles.stepper}>
      <Pressable style={styles.stepBtn} onPress={onMinus} accessibilityRole="button">
        <Text style={styles.stepBtnText}>−</Text>
      </Pressable>
      <Text style={styles.stepValue}>{label}</Text>
      <Pressable style={styles.stepBtn} onPress={onPlus} accessibilityRole="button">
        <Text style={styles.stepBtnText}>+</Text>
      </Pressable>
    </View>
  );
}

export function BabyAlarmPanel({ kind }: Props) {
  const { t } = useTranslation();
  const { alarms, create, toggle, edit, remove } = useBabyAlarms(kind);
  const now = new Date();
  const [hour, setHour] = useState(now.getHours());
  const [minute, setMinute] = useState(now.getMinutes());
  const [editingId, setEditingId] = useState<string | null>(null);

  const onChangeTime = (nextHour: number, nextMinute: number) => {
    setHour(nextHour);
    setMinute(nextMinute);
  };

  const startEdit = (alarm: BabyAlarm) => {
    setEditingId(alarm.id);
    setHour(alarm.hour);
    setMinute(alarm.minute);
  };

  const save = async () => {
    try {
      if (editingId) {
        await edit(editingId, hour, minute);
        setEditingId(null);
      } else {
        await create(hour, minute);
      }
    } catch (e) {
      const msg = e instanceof Error && e.message === 'NO_PERMISSION' ? t('alarm.permission') : t('common.error_generic');
      Alert.alert(t('alarm.title'), msg);
    }
  };

  return (
    <View style={styles.card}>
      <Text style={styles.title}>{t('alarm.title')}</Text>
      <Text style={styles.hint}>{t('alarm.hint')}</Text>
      <TimeStepper hour={hour} minute={minute} onChange={onChangeTime} />
      <Pressable style={styles.addBtn} onPress={save} accessibilityRole="button">
        <Text style={styles.addBtnText}>{editingId ? t('alarm.save') : t('alarm.add')}</Text>
      </Pressable>
      {editingId ? (
        <Pressable onPress={() => setEditingId(null)}>
          <Text style={styles.cancelEdit}>{t('common.back')}</Text>
        </Pressable>
      ) : null}
      {alarms.length === 0 ? <Text style={styles.empty}>{t('alarm.empty')}</Text> : null}
      {alarms.map((alarm) => (
        <View key={alarm.id} style={styles.row}>
          <Text style={[styles.time, !alarm.enabled && styles.timeOff]}>{formatAlarmTime(alarm.hour, alarm.minute)}</Text>
          <Switch
            value={alarm.enabled}
            onValueChange={(value) => {
              void toggle(alarm.id, value);
            }}
            trackColor={{ false: '#D8D0CC', true: '#7EB8DA' }}
            thumbColor="#fff"
            accessibilityLabel={alarm.enabled ? t('alarm.on') : t('alarm.off')}
          />
          <Pressable onPress={() => startEdit(alarm)} style={styles.linkBtn}>
            <Text style={styles.link}>{t('alarm.edit')}</Text>
          </Pressable>
          <Pressable
            onPress={() => {
              void remove(alarm.id);
            }}
            style={styles.linkBtn}
          >
            <Text style={styles.delete}>{t('alarm.delete')}</Text>
          </Pressable>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 14,
    marginBottom: 16,
  },
  title: { fontSize: 18, fontWeight: '700', color: '#3D2C2E' },
  hint: { fontSize: 12, color: '#7A6568', marginTop: 4, marginBottom: 10, lineHeight: 16 },
  stepperRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginBottom: 10 },
  colon: { fontSize: 28, fontWeight: '700', color: '#3D2C2E', marginHorizontal: 6 },
  stepper: { flexDirection: 'row', alignItems: 'center' },
  stepBtn: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#E8F4FA',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepBtnText: { fontSize: 22, color: '#3D6B8E', fontWeight: '700' },
  stepValue: { fontSize: 28, fontWeight: '700', color: '#3D2C2E', width: 52, textAlign: 'center' },
  addBtn: {
    backgroundColor: '#7EB8DA',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  addBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  cancelEdit: { textAlign: 'center', color: '#7A6568', marginBottom: 8 },
  empty: { textAlign: 'center', color: '#7A6568', marginTop: 6 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#F0EAE6',
    gap: 8,
  },
  time: { fontSize: 22, fontWeight: '700', color: '#3D2C2E', width: 78 },
  timeOff: { color: '#AAA' },
  linkBtn: { paddingVertical: 6, paddingHorizontal: 4 },
  link: { color: '#5FA3CC', fontWeight: '600' },
  delete: { color: '#C44', fontWeight: '600' },
});
