import React from 'react';
import { ScrollView, StyleSheet, Text } from 'react-native';
import { useTranslation } from '../hooks/useTranslation';

export function LegalScreen() {
  const { t } = useTranslation();
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{t('legal.privacy_title')}</Text>
      <Text style={styles.body}>{t('legal.privacy_body')}</Text>
      <Text style={[styles.title, styles.secondTitle]}>{t('legal.terms_title')}</Text>
      <Text style={styles.body}>{t('legal.terms_body')}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0' },
  content: { padding: 24, paddingTop: 8, paddingBottom: 40 },
  title: { fontSize: 22, fontWeight: '700', color: '#3D2C2E', marginBottom: 16 },
  secondTitle: { marginTop: 28 },
  body: { fontSize: 15, lineHeight: 22, color: '#3D2C2E' },
});
