import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useTranslation } from '../hooks/useTranslation';
import { colors, formStyles } from '../theme/formStyles';

type Props = {
  message?: string;
  onRetry?: () => void;
};

export function ErrorState({ message, onRetry }: Props) {
  const { t } = useTranslation();
  return (
    <View style={styles.container}>
      <Text style={styles.emoji}>⚠️</Text>
      <Text style={styles.title}>{t('common.error_title')}</Text>
      <Text style={styles.message}>{message || t('common.error_generic')}</Text>
      {onRetry ? (
        <Pressable style={formStyles.primaryButton} onPress={onRetry} accessibilityLabel={t('common.retry')}>
          <Text style={formStyles.primaryButtonText}>{t('common.retry')}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: colors.background,
  },
  emoji: { fontSize: 40, marginBottom: 12 },
  title: { fontSize: 18, fontWeight: '700', color: '#3D2C2E', marginBottom: 8 },
  message: { fontSize: 14, color: colors.textMuted, textAlign: 'center', marginBottom: 20 },
});
