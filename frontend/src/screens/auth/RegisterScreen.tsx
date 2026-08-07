import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { AuthBackground } from '../../components/AuthBackground';
import { api } from '../../services/api';
import { useTranslation } from '../../hooks/useTranslation';
import { colors, formStyles } from '../../theme/formStyles';
import type { AuthStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'Register'>;

export function RegisterScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [submitting, setSubmitting] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleRegister = async () => {
    if (!name.trim() || !email.trim() || !password) {
      Alert.alert(t('auth.fill_all_fields'));
      return;
    }
    if (password.length < 8) {
      Alert.alert(t('auth.registration_failed'), t('auth.password_min_length'));
      return;
    }
    try {
      setSubmitting(true);
      await api.post('/api/v1/auth/register', {
        email: email.trim(),
        password,
        display_name: name.trim(),
      });
      Alert.alert(t('auth.registration_ok'), '', [
        { text: 'OK', onPress: () => navigation.navigate('Login') },
      ]);
    } catch (e) {
      Alert.alert(t('auth.registration_failed'), e instanceof Error ? e.message : '');
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
            onPress={() => navigation.navigate('Login')}
            style={styles.linkWrap}
            accessibilityRole="button"
            accessibilityLabel={t('auth.already_have_account')}
          >
            <Text style={styles.link}>{t('auth.already_have_account')}</Text>
          </Pressable>

          <View style={styles.legalRow}>
            <Text style={styles.legalText}>{t('legal.accept_prefix')} </Text>
            <Pressable onPress={() => navigation.navigate('PrivacyPolicy')}>
              <Text style={styles.legalLink}>{t('legal.privacy_link')}</Text>
            </Pressable>
            <Text style={styles.legalText}> {t('legal.and')} </Text>
            <Pressable onPress={() => navigation.navigate('Terms')}>
              <Text style={styles.legalLink}>{t('legal.terms_link')}</Text>
            </Pressable>
          </View>
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
  legalRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginTop: 16,
    paddingHorizontal: 4,
  },
  legalText: {
    fontSize: 12,
    color: colors.textMuted,
    lineHeight: 18,
  },
  legalLink: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
    textDecorationLine: 'underline',
    lineHeight: 18,
  },
});
