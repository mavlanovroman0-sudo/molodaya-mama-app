import React, { useEffect, useRef, useState } from 'react';

import { ActivityIndicator, Alert, StyleSheet, View } from 'react-native';

import { NavigationContainer } from '@react-navigation/native';

import type { NavigationContainerRef, ParamListBase } from '@react-navigation/native';

import * as Linking from 'expo-linking';

import { initI18n, t } from './src/i18n';

import { useAppStore } from './src/store/appStore';

import { loadStoredToken } from './src/hooks/useAuth';

import { usePushNotifications } from './src/hooks/usePushNotifications';

import { AuthStackNavigator } from './src/navigation/AuthStack';

import { SubscriptionGateNavigator } from './src/navigation/SubscriptionGate';

import { ErrorBoundary } from './src/components/ErrorBoundary';

import { api, initApiAuth } from './src/services/api';

import { initSentry, registerNavigationContainer, wrapWithSentry } from './src/services/sentry';



initSentry();



function AppContent() {

  usePushNotifications();

  return <SubscriptionGateNavigator />;

}



function parsePaymentId(url: string): string | null {

  const parsed = Linking.parse(url);

  const q = parsed.queryParams || {};

  return (

    (q.payment_id as string) ||

    (q.paymentId as string) ||

    (q.purchase_id as string) ||

    (q.orderId as string) ||

    (q.session_id as string) ||

    null

  );

}



function isSubscriptionSuccessUrl(url: string): boolean {

  const parsed = Linking.parse(url);

  const path = (parsed.path || '').toLowerCase();

  const hostname = (parsed.hostname || '').toLowerCase();



  return (

    path.includes('subscription/success') ||

    path.includes('payment/success') ||

    (hostname === 'payment' && path === 'success') ||

    url.startsWith('homeease://payment/success') ||

    url.startsWith('homeease://subscription/success') ||

    url.includes('rustore-pay')

  );

}



function isSubscriptionCancelUrl(url: string): boolean {

  const parsed = Linking.parse(url);

  const path = (parsed.path || '').toLowerCase();

  const hostname = (parsed.hostname || '').toLowerCase();



  return (

    path.includes('subscription/cancel') ||

    path.includes('payment/cancel') ||

    (hostname === 'payment' && path === 'cancel') ||

    url.startsWith('homeease://payment/cancel') ||

    url.startsWith('homeease://subscription/cancel')

  );

}



function App() {

  const [ready, setReady] = useState(false);

  const { token, setToken, hydrate, requestSubscriptionRefresh } = useAppStore();

  const navigationRef = useRef<NavigationContainerRef<ParamListBase>>(null);



  const handleDeepLink = async (url: string | null) => {

    if (!url || !token) return;



    if (isSubscriptionSuccessUrl(url)) {

      const paymentId = parsePaymentId(url);

      try {

        if (paymentId) {

          await api.post('/api/v1/subscription/verify', { payment_id: paymentId }, { token });

        }

        requestSubscriptionRefresh();

        Alert.alert('HomeEase', t('subscription.payment_success'));

      } catch {

        requestSubscriptionRefresh();

        Alert.alert('HomeEase', t('subscription.checkout_hint'));

      }

    } else if (isSubscriptionCancelUrl(url)) {

      Alert.alert('HomeEase', t('subscription.payment_cancelled'));

    }

  };



  useEffect(() => {

    initApiAuth();

    (async () => {

      await hydrate();

      const stored = await loadStoredToken();

      if (stored) setToken(stored);

      await initI18n();

      setReady(true);

    })();

  }, [hydrate, setToken]);



  useEffect(() => {

    if (!ready) return;

    Linking.getInitialURL().then(handleDeepLink);

    const sub = Linking.addEventListener('url', ({ url }) => {

      handleDeepLink(url);

    });

    return () => sub.remove();

  }, [ready, token]);



  if (!ready) {

    return (

      <View style={styles.loader}>

        <ActivityIndicator size="large" color="#D4919A" />

      </View>

    );

  }



  return (

    <ErrorBoundary>

      <NavigationContainer

        ref={navigationRef}

        onReady={() => registerNavigationContainer(navigationRef.current)}

      >

        {token ? <AppContent /> : <AuthStackNavigator />}

      </NavigationContainer>

    </ErrorBoundary>

  );

}



export default wrapWithSentry(App);



const styles = StyleSheet.create({

  loader: {

    flex: 1,

    justifyContent: 'center',

    alignItems: 'center',

    backgroundColor: '#F8F4F0',

  },

});


