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

type Props = NativeStackScreenProps<AuthStackParamList, 'Register'>;

export function RegisterScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const { register } = useAuth();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleRegister = async () => {
    setError('');
    if (!name.trim() || !email.trim() || !password) {
      setError(t('auth.fill_all_fields'));
      return;
    }
    if (password.length < 8) {
      setError(t('auth.password_min_length'));
      return;
    }
    try {
      setSubmitting(true);
      await register(email.trim(), password, name.trim());
    } catch (e) {
      const raw = e instanceof Error ? e.message : '';
      if (/network request failed/i.test(raw) || /failed to fetch/i.test(raw)) {
        setError('Нет связи с сайтом. Выключите VPN и проверьте интернет.');
      } else {
        setError(raw || t('auth.registration_failed'));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthBackground keyboard>
      <View style={styles.inner}>
        <View style={styles.formCard}>
          <Text style={styles.title}>{t('auth.create_account')}</Text>

          <Text style={styles.label}>{t('auth.name')}</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            autoComplete="name"
            placeholder={t('auth.name')}
            placeholderTextColor={colors.textMuted}
          />

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
            autoComplete="new-password"
            placeholder={t('auth.password')}
            placeholderTextColor={colors.textMuted}
          />

          {error ? <Text style={styles.errorText}>{error}</Text> : null}

          <Pressable
            style={[formStyles.primaryButton, submitting && formStyles.primaryButtonDisabled]}
            onPress={handleRegister}
            disabled={submitting}
            accessibilityRole="button"
            accessibilityLabel={t('auth.register')}
          >
            {submitting ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={formStyles.primaryButtonText}>{t('auth.register')}</Text>
            )}
          </Pressable>

          <Pressable
            onPress={() => navigation.navigate('Legal')}
            style={styles.legalLinkWrap}
            accessibilityRole="link"
            accessibilityLabel={t('legal.combined_link')}
          >
            <Text style={styles.legalLink}>{t('legal.combined_link')}</Text>
          </Pressable>
          <Text style={styles.legalNotice}>{t('legal.register_agree')}</Text>

          <Pressable
            onPress={() => navigation.navigate('Language')}
            style={styles.linkWrap}
            accessibilityRole="button"
            accessibilityLabel={t('common.change_language')}
          >
            <Text style={styles.link}>{t('common.change_language')}</Text>
          </Pressable>

          <Pressable
            onPress={() => navigation.navigate('Login')}
            style={styles.linkWrap}
            accessibilityRole="button"
            accessibilityLabel={t('auth.already_have_account')}
          >
            <Text style={styles.link}>{t('auth.already_have_account')}</Text>
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
    marginTop: 24,
    alignItems: 'center',
    minHeight: 50,
    justifyContent: 'center',
  },
  link: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: '500',
  },
  legalLinkWrap: {
    marginTop: 16,
    alignItems: 'center',
    minHeight: 36,
    justifyContent: 'center',
  },
  legalLink: {
    fontSize: 15,
    color: '#1565C0',
    fontWeight: '600',
    textDecorationLine: 'underline',
    lineHeight: 20,
  },
  legalNotice: {
    marginTop: 8,
    fontSize: 12,
    color: colors.textMuted,
    lineHeight: 18,
    textAlign: 'center',
    paddingHorizontal: 4,
  },
});
