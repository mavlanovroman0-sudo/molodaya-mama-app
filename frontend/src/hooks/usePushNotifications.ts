import { useEffect } from 'react';
import { Alert, Platform } from 'react-native';
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (Platform.OS === 'web') {
    return null;
  }

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;
  if (existing !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') {
    return null;
  }

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const tokenData = await Notifications.getExpoPushTokenAsync(
    projectId ? { projectId } : undefined
  );
  return tokenData.data;
}

export function usePushNotifications() {
  const token = useAppStore((s) => s.token);

  useEffect(() => {
    if (!token) return;

    (async () => {
      try {
        const pushToken = await registerForPushNotifications();
        if (pushToken) {
          await api.post('/api/v1/notifications/register', { expo_push_token: pushToken }, { token });
        }
      } catch {
        // push optional in dev
      }
    })();

    const sub = Notifications.addNotificationReceivedListener((notification) => {
      const data = notification.request.content.data as { alarmId?: string } | undefined;
      if (data?.alarmId) return;
      const title = notification.request.content.title || 'молодая мама';
      const body = notification.request.content.body || '';
      Alert.alert(title, body);
    });

    return () => sub.remove();
  }, [token]);
}
