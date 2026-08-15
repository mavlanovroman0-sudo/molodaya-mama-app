import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';

export type AlarmKind = 'feeding' | 'sleep' | 'diaper';

export type BabyAlarm = {
  id: string;
  kind: AlarmKind;
  hour: number;
  minute: number;
  enabled: boolean;
};

const STORAGE_KEY = '@homeease/baby-alarms';
const CHANNEL_ID = 'baby-alarms';

export const ALARM_TITLES: Record<AlarmKind, string> = {
  feeding: 'Пора кормить',
  sleep: 'Пора спать',
  diaper: 'Подгузник',
};

export const ALARM_BODIES: Record<AlarmKind, string> = {
  feeding: 'Время кормления малыша',
  sleep: 'Пора укладывать малыша спать',
  diaper: 'Пора сменить подгузник',
};

let cache: BabyAlarm[] | null = null;
let ringing: BabyAlarm | null = null;
const ringListeners = new Set<() => void>();
const firedKeys = new Set<string>();
let watcherTimer: ReturnType<typeof setInterval> | null = null;
let sirenTimer: ReturnType<typeof setInterval> | null = null;
let audioCtx: { close: () => Promise<void> } | null = null;

function notifyRingListeners() {
  ringListeners.forEach((cb) => cb());
}

export function pad2(n: number): string {
  return String(n).padStart(2, '0');
}

export function formatAlarmTime(hour: number, minute: number): string {
  return `${pad2(hour)}:${pad2(minute)}`;
}

export function wrapHour(hour: number): number {
  return ((hour % 24) + 24) % 24;
}

export function wrapMinute(minute: number): number {
  return ((minute % 60) + 60) % 60;
}

export function matchesNow(alarm: BabyAlarm, now: Date): boolean {
  return alarm.enabled && now.getHours() === alarm.hour && now.getMinutes() === alarm.minute;
}

export function fireKey(alarm: BabyAlarm, now: Date): string {
  return `${alarm.id}-${now.getFullYear()}-${now.getMonth()}-${now.getDate()}-${now.getHours()}-${now.getMinutes()}`;
}

export function getRingingAlarm(): BabyAlarm | null {
  return ringing;
}

export function subscribeRinging(cb: () => void): () => void {
  ringListeners.add(cb);
  return () => {
    ringListeners.delete(cb);
  };
}

async function loadAll(): Promise<BabyAlarm[]> {
  if (cache) return cache;
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    cache = raw ? (JSON.parse(raw) as BabyAlarm[]) : [];
  } catch {
    cache = [];
  }
  return cache;
}

async function saveAll(alarms: BabyAlarm[]): Promise<void> {
  cache = alarms;
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(alarms));
}

export async function listAlarms(kind?: AlarmKind): Promise<BabyAlarm[]> {
  const all = await loadAll();
  const sorted = [...all].sort((a, b) => a.hour * 60 + a.minute - (b.hour * 60 + b.minute));
  return kind ? sorted.filter((a) => a.kind === kind) : sorted;
}

function notificationId(id: string): string {
  return `baby-alarm-${id}`;
}

function dailyTrigger(hour: number, minute: number): Notifications.NotificationTriggerInput {
  const types = (
    Notifications as {
      SchedulableTriggerInputTypes?: { DAILY?: string };
    }
  ).SchedulableTriggerInputTypes;
  if (types?.DAILY) {
    return {
      type: types.DAILY,
      hour,
      minute,
      channelId: CHANNEL_ID,
    } as Notifications.NotificationTriggerInput;
  }
  return {
    hour,
    minute,
    repeats: true,
    channelId: CHANNEL_ID,
  } as Notifications.NotificationTriggerInput;
}

export async function ensureAlarmPermissions(): Promise<boolean> {
  if (Platform.OS === 'web') {
    if (typeof Notification === 'undefined') return false;
    if (Notification.permission === 'granted') return true;
    const result = await Notification.requestPermission();
    return result === 'granted';
  }
  const existing = await Notifications.getPermissionsAsync();
  let status = existing.status;
  if (status !== 'granted') {
    const asked = await Notifications.requestPermissionsAsync();
    status = asked.status;
  }
  return status === 'granted';
}

export async function ensureAlarmChannel(): Promise<void> {
  if (Platform.OS !== 'android') return;
  await Notifications.setNotificationChannelAsync(CHANNEL_ID, {
    name: 'Будильник малыша',
    importance: Notifications.AndroidImportance.MAX,
    vibrationPattern: [0, 500, 250, 500, 250, 500],
    enableVibrate: true,
    sound: 'default',
    lockscreenVisibility: Notifications.AndroidNotificationVisibility.PUBLIC,
  });
}

async function scheduleNative(alarm: BabyAlarm): Promise<void> {
  if (Platform.OS === 'web') return;
  try {
    await Notifications.cancelScheduledNotificationAsync(notificationId(alarm.id));
    if (!alarm.enabled) return;
    await Notifications.scheduleNotificationAsync({
      identifier: notificationId(alarm.id),
      content: {
        title: ALARM_TITLES[alarm.kind],
        body: ALARM_BODIES[alarm.kind],
        sound: 'default',
        priority: Notifications.AndroidNotificationPriority.MAX,
        vibrate: [0, 500, 250, 500, 250, 500],
        sticky: true,
        data: { alarmId: alarm.id, kind: alarm.kind },
      },
      trigger: dailyTrigger(alarm.hour, alarm.minute),
    });
  } catch {
    /* scheduling is best-effort */
  }
}

async function cancelNative(id: string): Promise<void> {
  if (Platform.OS === 'web') return;
  await Notifications.cancelScheduledNotificationAsync(notificationId(id)).catch(() => undefined);
}

export async function addAlarm(kind: AlarmKind, hour: number, minute: number): Promise<BabyAlarm> {
  const allowed = await ensureAlarmPermissions();
  if (!allowed && Platform.OS !== 'web') {
    throw new Error('NO_PERMISSION');
  }
  const alarm: BabyAlarm = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    kind,
    hour: wrapHour(hour),
    minute: wrapMinute(minute),
    enabled: true,
  };
  const all = await loadAll();
  await saveAll([...all, alarm]);
  await scheduleNative(alarm);
  return alarm;
}

export async function updateAlarm(
  id: string,
  patch: Partial<Pick<BabyAlarm, 'hour' | 'minute' | 'enabled'>>
): Promise<BabyAlarm | null> {
  const all = await loadAll();
  const index = all.findIndex((a) => a.id === id);
  if (index < 0) return null;
  const next: BabyAlarm = {
    ...all[index],
    ...patch,
    hour: patch.hour !== undefined ? wrapHour(patch.hour) : all[index].hour,
    minute: patch.minute !== undefined ? wrapMinute(patch.minute) : all[index].minute,
  };
  const copy = [...all];
  copy[index] = next;
  await saveAll(copy);
  await scheduleNative(next);
  return next;
}

export async function removeAlarm(id: string): Promise<void> {
  const all = await loadAll();
  await saveAll(all.filter((a) => a.id !== id));
  await cancelNative(id);
  if (ringing?.id === id) {
    stopAlarmSound();
  }
}

function startSiren(): void {
  stopSirenOnly();
  if (Platform.OS !== 'web' || typeof window === 'undefined') return;
  const AudioContextCtor =
    window.AudioContext ||
    (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AudioContextCtor) return;
  const ctx = new AudioContextCtor();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = 'square';
  osc.frequency.value = 880;
  gain.gain.value = 0.28;
  osc.connect(gain);
  gain.connect(ctx.destination);
  void ctx.resume();
  osc.start();
  let high = true;
  sirenTimer = setInterval(() => {
    high = !high;
    osc.frequency.setValueAtTime(high ? 980 : 620, ctx.currentTime);
  }, 280);
  audioCtx = {
    close: async () => {
      try {
        osc.stop();
      } catch {
        /* already stopped */
      }
      await ctx.close();
    },
  };
}

function stopSirenOnly(): void {
  if (sirenTimer) {
    clearInterval(sirenTimer);
    sirenTimer = null;
  }
  if (audioCtx) {
    void audioCtx.close();
    audioCtx = null;
  }
}

export function stopAlarmSound(): void {
  stopSirenOnly();
  ringing = null;
  notifyRingListeners();
}

function showWebNotification(alarm: BabyAlarm): void {
  if (Platform.OS !== 'web' || typeof Notification === 'undefined') return;
  if (Notification.permission !== 'granted') return;
  try {
    const n = new Notification(ALARM_TITLES[alarm.kind], {
      body: ALARM_BODIES[alarm.kind],
      tag: notificationId(alarm.id),
      requireInteraction: true,
    });
    n.onclick = () => {
      window.focus();
      n.close();
    };
  } catch {
    /* ignore */
  }
}

export function triggerAlarm(alarm: BabyAlarm): void {
  ringing = alarm;
  notifyRingListeners();
  startSiren();
  showWebNotification(alarm);
}

export async function rescheduleAllAlarms(): Promise<void> {
  const all = await loadAll();
  for (const alarm of all) {
    await scheduleNative(alarm);
  }
}

async function tickWatcher(): Promise<void> {
  const now = new Date();
  const all = await loadAll();
  for (const alarm of all) {
    if (!matchesNow(alarm, now)) continue;
    const key = fireKey(alarm, now);
    if (firedKeys.has(key)) continue;
    firedKeys.add(key);
    triggerAlarm(alarm);
  }
}

export async function startBabyAlarmRuntime(): Promise<() => void> {
  await ensureAlarmChannel();
  await rescheduleAllAlarms();
  if (watcherTimer) clearInterval(watcherTimer);
  watcherTimer = setInterval(() => {
    void tickWatcher();
  }, 8000);
  void tickWatcher();

  let received: { remove: () => void } | undefined;
  let response: { remove: () => void } | undefined;
  try {
    received = Notifications.addNotificationReceivedListener((notification) => {
      const data = notification.request.content.data as { alarmId?: string; kind?: AlarmKind };
      if (!data?.alarmId) return;
      void loadAll().then((all) => {
        const found = all.find((a) => a.id === data.alarmId);
        if (found) triggerAlarm(found);
      });
    });
    response = Notifications.addNotificationResponseReceivedListener((event) => {
      const data = event.notification.request.content.data as { alarmId?: string };
      if (!data?.alarmId) return;
      void loadAll().then((all) => {
        const found = all.find((a) => a.id === data.alarmId);
        if (found) triggerAlarm(found);
      });
    });
  } catch {
    /* web / unsupported */
  }

  return () => {
    if (watcherTimer) {
      clearInterval(watcherTimer);
      watcherTimer = null;
    }
    received?.remove();
    response?.remove();
    stopAlarmSound();
  };
}
