import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useTranslation } from '../hooks/useTranslation';

interface InviteBannerProps {
  onInvite: () => void;
  onDismiss: () => void;
}

export function InviteBanner({ onInvite, onDismiss }: InviteBannerProps) {
  const { t } = useTranslation();

  return (
    <View style={styles.banner}>
      <Text style={styles.text}>{t('invite.invite_banner_text')}</Text>
      <View style={styles.actions}>
        <Pressable style={styles.primaryBtn} onPress={onInvite}>
          <Text style={styles.primaryText}>{t('invite.invite_banner_button')}</Text>
        </Pressable>
        <Pressable onPress={onDismiss} hitSlop={8}>
          <Text style={styles.dismiss}>✕</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#FFF8E7',
    borderRadius: 12,
    padding: 14,
    marginHorizontal: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#F0E4C8',
  },
  text: {
    fontSize: 14,
    color: '#3D2C2E',
    marginBottom: 10,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  primaryBtn: {
    backgroundColor: '#D4919A',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  primaryText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  dismiss: {
    fontSize: 18,
    color: '#7A6568',
    paddingHorizontal: 8,
  },
});
