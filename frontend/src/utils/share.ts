import { Share, Platform, Alert } from 'react-native';

const APP_LINK = 'https://homeease.app';

export async function shareReferralLink(code: string, message: string): Promise<void> {
  const text = message.replace('{code}', code).replace('{link}', `${APP_LINK}/ref/${code}`);
  try {
    await Share.share({
      message: text,
      url: Platform.OS === 'ios' ? `${APP_LINK}/ref/${code}` : undefined,
      title: 'HomeEase',
    });
  } catch {
    /* user cancelled */
  }
}

export async function shareAchievement(message: string): Promise<void> {
  try {
    await Share.share({ message, title: 'HomeEase' });
  } catch {
    /* cancelled */
  }
}

export function showShareToast(message: string): void {
  if (Platform.OS === 'android') {
    const { ToastAndroid } = require('react-native');
    ToastAndroid.show(message, ToastAndroid.SHORT);
  } else {
    Alert.alert('HomeEase', message);
  }
}

export { APP_LINK };
