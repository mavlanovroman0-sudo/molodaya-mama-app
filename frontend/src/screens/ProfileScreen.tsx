import React from 'react';
import { CommonActions, useNavigation } from '@react-navigation/native';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../hooks/useAuth';
import { useAppStore } from '../store/appStore';
import { colors, formStyles } from '../theme/formStyles';
import type { ProfileStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<ProfileStackParamList, 'Profile'>;

export function ProfileScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const { logout } = useAuth();
  const rootNav = useNavigation();
  const tokenBalance = useAppStore((s) => s.tokenBalance);

  const switchRole = () => {
    useAppStore.getState().setRole(null);
    rootNav.dispatch(
      CommonActions.reset({
        index: 0,
        routes: [{ name: 'RoleSelect' }],
      })
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={formStyles.label}>{t('auth.name')}</Text>
        <Text style={styles.value}>—</Text>
        <Text style={formStyles.label}>{t('screens.token_balance')}</Text>
        <Text style={styles.value}>{tokenBalance}</Text>
      </View>
      <View style={styles.actions}>
        <Pressable
          style={[formStyles.primaryButton, styles.subscriptionBtn]}
          onPress={() => navigation.navigate('Subscription')}
          accessibilityLabel={t('subscription.plans')}
        >
          <Text style={formStyles.primaryButtonText}>{t('subscription.plans')}</Text>
        </Pressable>
        <Pressable
          style={[formStyles.secondaryButton, styles.gap]}
          onPress={() => navigation.navigate('Invite')}
          accessibilityLabel={t('invite.invite_friends')}
        >
          <Text style={formStyles.secondaryButtonText}>{t('invite.invite_friends')}</Text>
        </Pressable>
        <Pressable
          style={[formStyles.secondaryButton, styles.gap]}
          onPress={switchRole}
          accessibilityLabel={t('common.switch_role')}
        >
          <Text style={formStyles.secondaryButtonText}>{t('common.switch_role')}</Text>
        </Pressable>
        <Pressable
          style={[formStyles.secondaryButton, styles.gap]}
          onPress={() => navigation.navigate('Language')}
          accessibilityLabel={t('common.change_language')}
        >
          <Text style={formStyles.secondaryButtonText}>{t('common.change_language')}</Text>
        </Pressable>
      </View>
      <Pressable style={styles.link} onPress={() => navigation.navigate('PrivacyPolicy')}>
        <Text style={styles.linkText}>{t('legal.privacy_title')}</Text>
      </Pressable>
      <Pressable style={styles.link} onPress={() => navigation.navigate('Terms')}>
        <Text style={styles.linkText}>{t('legal.terms_title')}</Text>
      </Pressable>
      <Pressable style={styles.logout} onPress={logout} accessibilityLabel={t('screens.logout')}>
        <Text style={styles.logoutText}>{t('screens.logout')}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 24,
    paddingTop: 8,
    alignItems: 'center',
  },
  card: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 18,
    marginBottom: 16,
    width: '100%',
    maxWidth: 420,
  },
  actions: {
    width: '100%',
    maxWidth: 320,
  },
  subscriptionBtn: {
    minHeight: 54,
    shadowColor: '#FF69B4',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 3,
  },
  value: { fontSize: 18, fontWeight: '600', color: colors.textDark, marginBottom: 4 },
  gap: { marginTop: 10 },
  link: { padding: 12, alignItems: 'center', minHeight: 44, justifyContent: 'center' },
  linkText: { color: colors.primary, fontSize: 15, fontWeight: '600' },
  logout: { padding: 16, alignItems: 'center', marginTop: 20, minHeight: 50, justifyContent: 'center' },
  logoutText: { color: '#C44', fontSize: 15, fontWeight: '600' },
});
