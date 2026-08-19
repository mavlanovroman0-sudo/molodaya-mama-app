import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { RegisterScreen } from '../screens/auth/RegisterScreen';
import { PrivacyPolicyScreen } from '../screens/PrivacyPolicyScreen';
import { TermsScreen } from '../screens/TermsScreen';
import { LegalScreen } from '../screens/LegalScreen';
import { LanguageScreen } from '../screens/LanguageScreen';
import { createStackHeaderOptions } from './headerOptions';
import { useAppStore } from '../store/appStore';
import type { AuthStackParamList } from './types';

const Stack = createNativeStackNavigator<AuthStackParamList>();

export function AuthStackNavigator() {
  const authInitialRoute = useAppStore((s) => s.authInitialRoute);

  return (
    <Stack.Navigator
      initialRouteName={authInitialRoute}
      screenOptions={({ navigation, route }) =>
        createStackHeaderOptions(navigation, route.name, route.name !== 'Login')
      }
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="PrivacyPolicy" component={PrivacyPolicyScreen} />
      <Stack.Screen name="Terms" component={TermsScreen} />
      <Stack.Screen name="Legal" component={LegalScreen} />
      <Stack.Screen name="Language" component={LanguageScreen} />
    </Stack.Navigator>
  );
}
