import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useTranslation } from '../../hooks/useTranslation';
import { colors } from '../../theme/formStyles';

export function BabyHealthScreen() {
  const { t } = useTranslation();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.emoji}>❤️</Text>
      <Text style={styles.title}>{t('tabs.health')}</Text>
      <Text style={styles.subtitle}>{t('screens.health_welcome')}</Text>
      <View style={styles.card}>
        <Text style={styles.cardText}>{t('screens.health_hint')}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, alignItems: 'center' },
  emoji: { fontSize: 48, marginBottom: 8 },
  title: { fontSize: 24, fontWeight: '700', color: colors.textDark },
  subtitle: { fontSize: 15, color: colors.textGray, marginTop: 8, textAlign: 'center' },
  card: {
    marginTop: 24,
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 20,
    width: '100%',
    maxWidth: 420,
  },
  cardText: { fontSize: 15, color: colors.textGray, lineHeight: 22 },
});
