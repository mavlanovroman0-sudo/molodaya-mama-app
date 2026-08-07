import React, { useEffect } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SubscriptionScreen } from '../screens/SubscriptionScreen';
import { useSubscription } from '../hooks/useSubscription';
import { ErrorState } from '../components/ErrorState';
import { MainStackNavigator } from './MainStack';
import { createStackHeaderOptions } from './headerOptions';
import type { SubscriptionGateParamList } from './types';

const Stack = createNativeStackNavigator<SubscriptionGateParamList & { Paywall: undefined }>();

function SubscriptionGateInner() {
  const { status, loading, error, refresh } = useSubscription();

  useEffect(() => {
    const interval = setInterval(refresh, 30000);
    return () => clearInterval(interval);
  }, [refresh]);

  if (loading && !status) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color="#6C63FF" />
      </View>
    );
  }

  if (error && !status) {
    return <ErrorState message={error} onRetry={refresh} />;
  }

  if (!status) {
    return <ErrorState onRetry={refresh} />;
  }

  if (!status.has_access) {
    return (
      <Stack.Navigator>
        <Stack.Screen
          name="Paywall"
          component={SubscriptionScreen}
          options={({ navigation }) => createStackHeaderOptions(navigation, 'Paywall')}
        />
      </Stack.Navigator>
    );
  }

  return <MainStackNavigator />;
}

export function SubscriptionGateNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Gate" component={SubscriptionGateInner} />
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  loader: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F4F0',
  },
});
