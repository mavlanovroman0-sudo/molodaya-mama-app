/**
 * Expo configuration for HomeEase 2.0.
 *
 * Идентификаторы приложения (замените перед публикацией в магазины):
 *   android.package      — com.homeease.app  → ваш уникальный package name
 *   ios.bundleIdentifier   — com.homeease.app  → ваш Bundle ID в Apple Developer
 *
 * Deep links (схема homeease://):
 *   homeease://payment/success?payment_id=...
 *   homeease://payment/cancel
 *   homeease://subscription/success
 *   homeease://subscription/cancel
 */
module.exports = {
  expo: {
    name: 'HomeEase',
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
      // Заглушка — замените на финальный package перед RuStore / Google Play
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
            { scheme: 'https', host: 'homeease.app', pathPrefix: '/subscription' },
          ],
          category: ['BROWSABLE', 'DEFAULT'],
        },
      ],
    },
    ios: {
      // Заглушка — замените на финальный Bundle ID перед App Store
      bundleIdentifier: 'com.homeease.app',
      associatedDomains: ['applinks:homeease.app'],
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
