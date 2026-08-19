import React from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';
import type { NavigationProp, ParamListBase } from '@react-navigation/native';
import type { NativeStackNavigationOptions } from '@react-navigation/native-stack';
import { t } from '../i18n';
import { navTheme } from '../theme/navigationTheme';
import { uiFontStyle } from '../theme/fonts';

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
  Legal: 'legal.combined_title',
  Paywall: 'subscription.title',
  Instruction: 'common.instruction_title',
  Language: 'common.change_language',
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
};

export function BackButton({ navigation }: BackButtonProps) {
  return (
    <Pressable
      onPress={() => goBackOrRoleSelect(navigation)}
      style={styles.backBtn}
      hitSlop={16}
      accessibilityRole="button"
      accessibilityLabel={t('common.back')}
    >
      <Text style={styles.backArrow}>←</Text>
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
    headerBackVisible: false,
    headerTitleStyle: {
      ...uiFontStyle,
      fontWeight: '600',
      fontSize: 17,
      color: navTheme.headerTint,
    },
    title: getScreenTitle(routeName),
    headerLeft: showBack
      ? () => <BackButton navigation={navigation} />
      : undefined,
    headerLeftContainerStyle: { paddingLeft: 4, minWidth: 44 },
  };
}

const styles = StyleSheet.create({
  backBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    justifyContent: 'center',
    minWidth: 40,
    minHeight: 40,
  },
  backArrow: {
    color: navTheme.headerTint,
    fontSize: 28,
    lineHeight: 32,
    fontWeight: '600',
    includeFontPadding: false,
  },
});
