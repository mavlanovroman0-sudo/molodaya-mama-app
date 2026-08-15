import React, { useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { AuthBackground } from '../../components/AuthBackground';
import { useAuth } from '../../hooks/useAuth';
import { useTranslation } from '../../hooks/useTranslation';
import { colors, formStyles } from '../../theme/formStyles';
import type { AuthStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'Login'>;

export function LoginScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    setError('');
    if (!email.trim() || !password) {
      setError(t('auth.fill_all_fields'));
      return;
    }
    try {
      await login(email.trim(), password);
    } catch (e) {
      setError(e instanceof Error ? e.message : t('auth.login_failed'));
    }
  };

  return (
    <AuthBackground keyboard>
      <View style={styles.inner}>
        <View style={styles.formCard}>
          <Text style={styles.title}>{t('auth.welcome_back')}</Text>

          <Text style={styles.label}>{t('auth.email')}</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            placeholder={t('auth.email')}
            placeholderTextColor={colors.textMuted}
          />

          <Text style={styles.label}>{t('auth.password')}</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoComplete="password"
            placeholder={t('auth.password')}
            placeholderTextColor={colors.textMuted}
          />

          {error ? <Text style={styles.errorText}>{error}</Text> : null}

          <Pressable
            style={[formStyles.primaryButton, loading && formStyles.primaryButtonDisabled]}
            onPress={handleLogin}
            disabled={loading}
            accessibilityRole="button"
            accessibilityLabel={t('auth.login')}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={formStyles.primaryButtonText}>{t('auth.login')}</Text>
            )}
          </Pressable>

        <Pressable
          onPress={() => navigation.navigate('Register')}
          style={[formStyles.secondaryButton, styles.registerBtn]}
          accessibilityRole="button"
          accessibilityLabel={t('auth.register')}
        >
          <Text style={formStyles.secondaryButtonText}>{t('auth.register')}</Text>
        </Pressable>

        <Pressable
          onPress={() => navigation.navigate('Register')}
          style={styles.linkWrap}
          accessibilityRole="button"
          accessibilityLabel={t('auth.no_account')}
        >
          <Text style={styles.link}>{t('auth.no_account')}</Text>
        </Pressable>
        <Pressable
          onPress={() => navigation.navigate('Language')}
          style={styles.linkWrap}
          accessibilityRole="button"
          accessibilityLabel={t('common.change_language')}
        >
          <Text style={styles.link}>{t('common.change_language')}</Text>
        </Pressable>
        </View>
      </View>
    </AuthBackground>
  );
}

const styles = StyleSheet.create({
  inner: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  formCard: {
    maxWidth: 420,
    width: '100%',
    alignSelf: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.82)',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.6)',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: 24,
    textAlign: 'center',
  },
  label: {
    ...formStyles.label,
  },
  input: {
    ...formStyles.input,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  errorText: {
    color: '#C44',
    fontSize: 14,
    marginBottom: 12,
    textAlign: 'center',
  },
  linkWrap: {
    marginTop: 16,
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
  },
  registerBtn: {
    marginTop: 12,
  },
  link: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: '500',
  },
});
