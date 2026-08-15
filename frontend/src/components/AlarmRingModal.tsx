import React, { useSyncExternalStore } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import {
  ALARM_BODIES,
  ALARM_TITLES,
  getRingingAlarm,
  stopAlarmSound,
  subscribeRinging,
} from '../services/babyAlarms';
import { t } from '../i18n';

export function AlarmRingModal() {
  const alarm = useSyncExternalStore(subscribeRinging, getRingingAlarm, getRingingAlarm);
  if (!alarm) return null;

  return (
    <Modal visible transparent animationType="fade" onRequestClose={stopAlarmSound}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.emoji}>⏰</Text>
          <Text style={styles.title}>{ALARM_TITLES[alarm.kind]}</Text>
          <Text style={styles.body}>{ALARM_BODIES[alarm.kind]}</Text>
          <Pressable style={styles.stop} onPress={stopAlarmSound} accessibilityRole="button">
            <Text style={styles.stopText}>{t('alarm.stop')}</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(20, 10, 12, 0.72)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 28,
    width: '100%',
    maxWidth: 360,
    alignItems: 'center',
  },
  emoji: { fontSize: 48, marginBottom: 8 },
  title: { fontSize: 32, fontWeight: '800', color: '#3D2C2E', textAlign: 'center' },
  body: { fontSize: 16, color: '#7A6568', textAlign: 'center', marginTop: 8, marginBottom: 20 },
  stop: {
    backgroundColor: '#C47A84',
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 24,
    width: '100%',
    alignItems: 'center',
  },
  stopText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
