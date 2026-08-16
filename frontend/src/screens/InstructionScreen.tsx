import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useTranslation } from '../hooks/useTranslation';
import { getInstruction } from '../i18n/instructionLocales';

export function InstructionScreen() {
  const { t, lang } = useTranslation();
  const pack = getInstruction(lang);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.lead}>{pack.lead}</Text>
      {pack.chapters.map((chapter) => (
        <View key={chapter.title} style={styles.chapter}>
          <Text style={styles.chapterTitle}>{chapter.title}</Text>
          <Text style={styles.intro}>{chapter.intro}</Text>
          {chapter.features.map((feature, index) => (
            <View key={`${chapter.title}-${feature.name}`} style={styles.card}>
              <Text style={styles.featureName}>
                {index + 1}. {feature.name}
              </Text>
              <Text style={styles.label}>{t('common.how_label')}</Text>
              <Text style={styles.body}>{feature.how}</Text>
              <Text style={styles.label}>{t('common.result_label')}</Text>
              <Text style={styles.body}>{feature.result}</Text>
              <Text style={styles.labelHelp}>{t('common.help_label')}</Text>
              <Text style={styles.body}>{feature.help}</Text>
            </View>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}

const READABLE = 'Arial, "Segoe UI", sans-serif';

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0' },
  content: { padding: 20, paddingBottom: 40 },
  lead: {
    fontFamily: READABLE,
    fontSize: 15,
    lineHeight: 22,
    color: '#7A6568',
    marginBottom: 20,
  },
  chapter: { marginBottom: 8 },
  chapterTitle: {
    fontFamily: READABLE,
    fontSize: 22,
    fontWeight: '700',
    color: '#3D2C2E',
    marginBottom: 10,
  },
  intro: {
    fontFamily: READABLE,
    fontSize: 15,
    lineHeight: 22,
    color: '#3D2C2E',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
  },
  featureName: {
    fontFamily: READABLE,
    fontSize: 17,
    fontWeight: '700',
    color: '#3D2C2E',
    marginBottom: 10,
  },
  label: {
    fontFamily: READABLE,
    fontSize: 12,
    fontWeight: '700',
    color: '#C47A84',
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: 4,
    marginTop: 6,
  },
  labelHelp: {
    fontFamily: READABLE,
    fontSize: 12,
    fontWeight: '700',
    color: '#5FA3CC',
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: 4,
    marginTop: 6,
  },
  body: {
    fontFamily: READABLE,
    fontSize: 15,
    lineHeight: 22,
    color: '#3D2C2E',
  },
});
