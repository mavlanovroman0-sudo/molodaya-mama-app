/**
 * Sentry для Expo / React Native.
 * Инициализация только при EXPO_PUBLIC_SENTRY_DSN (не в Jest).
 */

import type { ComponentType } from 'react';
import Constants from 'expo-constants';
import type { NavigationContainerRef, ParamListBase } from '@react-navigation/native';

type SentryModule = typeof import('@sentry/react-native');

let sentryModule: SentryModule | null = null;
let navigationIntegration: ReturnType<SentryModule['reactNavigationIntegration']> | null = null;

function resolveDsn(): string {
  return (
    process.env.EXPO_PUBLIC_SENTRY_DSN ||
    (Constants.expoConfig?.extra as { sentryDsn?: string } | undefined)?.sentryDsn ||
    ''
  );
}

export function initSentry(): boolean {
  if (process.env.NODE_ENV === 'test') {
    return false;
  }

  const dsn = resolveDsn();
  if (!dsn) {
    return false;
  }

  sentryModule = require('@sentry/react-native') as SentryModule;

  navigationIntegration = sentryModule.reactNavigationIntegration({
    enableTimeToInitialDisplay: Constants.appOwnership !== 'expo',
  });

  sentryModule.init({
    dsn,
    debug: __DEV__,
    tracesSampleRate: 0.2,
    integrations: [navigationIntegration],
    enableNativeFramesTracking: Constants.appOwnership !== 'expo',
  });

  return true;
}

export function registerNavigationContainer(
  ref: NavigationContainerRef<ParamListBase> | null
): void {
  navigationIntegration?.registerNavigationContainer(ref);
}

export function wrapWithSentry<P extends object>(component: ComponentType<P>): ComponentType<P> {
  if (!sentryModule) {
    return component;
  }
  return sentryModule.wrap(component);
}
