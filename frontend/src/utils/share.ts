import { Share, Platform, Alert } from 'react-native';

const APP_LINK = 'https://my-molodaya-mama.ru';
const APP_NAME = 'молодая мама';

export async function shareReferralLink(code: string, message: string): Promise<void> {
  const text = message.replace('{code}', code).replace('{link}', `${APP_LINK}/ref/${code}`);
  try {
    await Share.share({
      message: text,
      url: Platform.OS === 'ios' ? `${APP_LINK}/ref/${code}` : undefined,
      title: APP_NAME,
    });
  } catch {
    /* user cancelled */
  }
}

export async function shareAchievement(message: string): Promise<void> {
  try {
    await Share.share({ message, title: APP_NAME });
  } catch {
    /* cancelled */
  }
}

export function showShareToast(message: string): void {
  if (Platform.OS === 'android') {
    const { ToastAndroid } = require('react-native');
    ToastAndroid.show(message, ToastAndroid.SHORT);
  } else {
    Alert.alert(APP_NAME, message);
  }
}

export { APP_LINK };
