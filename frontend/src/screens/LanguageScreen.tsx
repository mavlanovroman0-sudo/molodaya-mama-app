import React, { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { LANGUAGE_OPTIONS } from '../i18n';
import { useTranslation } from '../hooks/useTranslation';
import { applyUserLanguage } from '../services/language';
import { colors } from '../theme/formStyles';

export function LanguageScreen() {
  const { t, lang } = useTranslation();
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState('');

  const onPick = async (id: (typeof LANGUAGE_OPTIONS)[number]['id']) => {
    if (saving) return;
    setError('');
    setSaving(id);
    try {
      await applyUserLanguage(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.error_generic'));
    } finally {
      setSaving(null);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('common.change_language')}</Text>
      {LANGUAGE_OPTIONS.map((option) => {
        const selected = option.id === lang;
        return (
          <Pressable
            key={option.id}
            style={[styles.row, selected && styles.rowSelected]}
            onPress={() => onPick(option.id)}
            accessibilityRole="button"
            accessibilityLabel={option.nativeName}
            accessibilityState={{ selected }}
          >
            <Text style={[styles.label, selected && styles.labelSelected]}>{option.nativeName}</Text>
            {saving === option.id ? (
              <ActivityIndicator color={colors.primary} />
            ) : selected ? (
              <Text style={styles.mark}>✓</Text>
            ) : null}
          </Pressable>
        );
      })}
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 24,
  },
  title: {
    fontFamily: 'Arial, "Segoe UI", sans-serif',
    fontSize: 22,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: 16,
  },
  row: {
    minHeight: 52,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.white,
    paddingHorizontal: 16,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  rowSelected: {
    borderColor: colors.primary,
    backgroundColor: '#FFF0F6',
  },
  label: {
    fontFamily: 'Arial, "Segoe UI", sans-serif',
    fontSize: 17,
    color: colors.textDark,
    fontWeight: '600',
  },
  labelSelected: {
    color: colors.primary,
  },
  mark: {
    fontSize: 18,
    color: colors.primary,
    fontWeight: '700',
  },
  error: {
    marginTop: 12,
    color: '#C44',
    fontSize: 14,
    textAlign: 'center',
  },
});
