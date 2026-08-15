import React from 'react';
import { Pressable, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { NavigationProp, ParamListBase } from '@react-navigation/native';
import type { NativeStackNavigationOptions } from '@react-navigation/native-stack';
import { t } from '../i18n';
import { navTheme } from '../theme/navigationTheme';

const SCREEN_TITLE_KEYS: Record<string, string> = {
  Login: 'auth.login',
  Register: 'auth.register',
  Invite: 'invite.invite_friends',
  FeaturesDashboard: 'dashboard.open_features',
  Home: 'tabs.home',
  Shopping: 'tabs.shopping',
  Barter: 'tabs.barter',
  SmartHome: 'tabs.smart_home',
  Report: 'tabs.report',
  Feeding: 'tabs.feeding',
  Sleep: 'tabs.sleep',
  Diapers: 'tabs.diapers',
  Checklist: 'tabs.checklist',
  Nanny: 'tabs.nanny',
  Health: 'tabs.health',
  Profile: 'tabs.profile',
  Subscription: 'subscription.title',
  PrivacyPolicy: 'legal.privacy_title',
  Terms: 'legal.terms_title',
  Paywall: 'subscription.title',
  Instruction: 'common.instruction_title',
};

export function getScreenTitle(routeName: string): string {
  const key = SCREEN_TITLE_KEYS[routeName];
  return key ? t(key) : routeName;
}

/** Назад по стеку или к выбору роли с корневых вкладок. */
export function goBackOrRoleSelect(navigation: NavigationProp<ParamListBase>): void {
  if (navigation.canGoBack()) {
    navigation.goBack();
    return;
  }

  let current: NavigationProp<ParamListBase> | undefined = navigation;
  while (current) {
    const parent = current.getParent();
    if (!parent) break;

    const state = parent.getState();
    const activeRoute = state.routes[state.index]?.name;
    if (activeRoute === 'HousewifeApp' || activeRoute === 'MomApp') {
      parent.navigate('RoleSelect' as never);
      return;
    }

    if (parent.canGoBack()) {
      parent.goBack();
      return;
    }
    current = parent;
  }
}

type BackButtonProps = {
  navigation: NavigationProp<ParamListBase>;
  tintColor?: string;
};

export function BackButton({ navigation, tintColor = navTheme.headerTint }: BackButtonProps) {
  return (
    <Pressable
      onPress={() => goBackOrRoleSelect(navigation)}
      style={styles.backBtn}
      accessibilityRole="button"
      accessibilityLabel={t('common.back')}
    >
      <Ionicons name="arrow-back" size={24} color={tintColor} />
    </Pressable>
  );
}

export function createStackHeaderOptions(
  navigation: NavigationProp<ParamListBase>,
  routeName: string,
  showBack = true
): NativeStackNavigationOptions {
  return {
    headerShown: true,
    headerStyle: { backgroundColor: navTheme.headerBg },
    headerShadowVisible: false,
    headerTintColor: navTheme.headerTint,
    headerTitleStyle: { fontWeight: '600', fontSize: 17, color: navTheme.headerTint },
    title: getScreenTitle(routeName),
    headerLeft: showBack
      ? () => <BackButton navigation={navigation} />
      : undefined,
  };
}

const styles = StyleSheet.create({
  backBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginLeft: 4,
  },
});
