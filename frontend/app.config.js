/**
 * Expo configuration.
 *
 * Deep links:
 *   homeease://payment/success?payment_id=...
 *   homeease://payment/cancel
 */
module.exports = {
  expo: {
    name: 'молодая мама',
    slug: 'homeease',
    version: '2.0.0',
    orientation: 'portrait',
    icon: './assets/icon.png',
    scheme: 'homeease',
    userInterfaceStyle: 'light',
    splash: {
      image: './assets/splash.png',
      resizeMode: 'contain',
      backgroundColor: '#F8F4F0',
    },
    android: {
      package: 'com.homeease.app',
      adaptiveIcon: {
        foregroundImage: './assets/adaptive-icon.png',
        backgroundColor: '#F8F4F0',
      },
      intentFilters: [
        {
          action: 'VIEW',
          autoVerify: true,
          data: [
            { scheme: 'homeease' },
            { scheme: 'https', host: 'my-molodaya-mama.ru', pathPrefix: '/subscription' },
          ],
          category: ['BROWSABLE', 'DEFAULT'],
        },
      ],
    },
    ios: {
      bundleIdentifier: 'com.homeease.app',
      associatedDomains: ['applinks:my-molodaya-mama.ru'],
    },
    web: {
      bundler: 'metro',
      output: 'single',
    },
    plugins: ['expo-location', 'expo-notifications', 'expo-asset', 'expo-font'],
    extra: {
      eas: {
        projectId: 'REPLACE_WITH_EAS_PROJECT_ID',
      },
    },
  },
};
