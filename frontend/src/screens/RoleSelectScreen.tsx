import React, { useEffect, useRef } from 'react';
import {
  Animated,
  ImageBackground,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from '../hooks/useTranslation';
import { images } from '../theme/assets';

export type RoleId = 'housewife' | 'young_mom';

const BTN_W = 220;
const BTN_H = 84;
const READABLE_FONT = Platform.OS === 'web' ? 'Arial, "Segoe UI", sans-serif' : undefined;

function ensureReadableWebFont() {
  if (Platform.OS !== 'web' || typeof document === 'undefined') return;
  if (document.getElementById('molodaya-mama-base-font')) return;
  const style = document.createElement('style');
  style.id = 'molodaya-mama-base-font';
  style.textContent =
    'html, body, #root { font-family: Arial, "Segoe UI", sans-serif !important; }';
  document.head.appendChild(style);
}

interface RoleCardProps {
  label: string;
  gradient: [string, string];
  onPress: () => void;
  delay: number;
}

function RoleCard({ label, gradient, onPress, delay }: RoleCardProps) {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 500, delay, useNativeDriver: true }).start();
  }, [fadeAnim, delay]);

  return (
    <Animated.View style={{ opacity: fadeAnim, transform: [{ scale: scaleAnim }] }}>
      <Pressable
        onPress={onPress}
        onPressIn={() => Animated.spring(scaleAnim, { toValue: 0.97, useNativeDriver: true }).start()}
        onPressOut={() => Animated.spring(scaleAnim, { toValue: 1, friction: 4, useNativeDriver: true }).start()}
        style={styles.roleBtn}
        accessibilityRole="button"
        accessibilityLabel={label}
      >
        <LinearGradient colors={gradient} style={styles.roleGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}>
          <Text style={styles.roleLabel} numberOfLines={2}>
            {label}
          </Text>
        </LinearGradient>
      </Pressable>
    </Animated.View>
  );
}

interface RoleSelectScreenProps {
  onSelectRole: (role: RoleId) => void;
  onOpenInvite?: () => void;
  onOpenInstruction?: () => void;
  onOpenTariffs?: () => void;
  onOpenLanguage?: () => void;
  onExit?: () => void;
}

export function RoleSelectScreen({
  onSelectRole,
  onOpenInvite,
  onOpenInstruction,
  onOpenTariffs,
  onOpenLanguage,
  onExit,
}: RoleSelectScreenProps) {
  const titleAnim = useRef(new Animated.Value(0)).current;
  const { t } = useTranslation();

  useEffect(() => {
    ensureReadableWebFont();
    Animated.timing(titleAnim, { toValue: 1, duration: 700, useNativeDriver: true }).start();
  }, [titleAnim]);

  return (
    <ImageBackground source={images.authBg} style={styles.screen} resizeMode="cover">
      <View style={styles.overlay} />
      <Animated.View style={[styles.header, { opacity: titleAnim }]}>
        <Text style={styles.appTitle}>молодая мама</Text>
        <View style={styles.buttonsRow}>
          <RoleCard
            label={t('roles.experienced_mom')}
            gradient={['#D4919A', '#C47A84']}
            onPress={() => onSelectRole('housewife')}
            delay={150}
          />
          <RoleCard
            label={t('roles.young_mom')}
            gradient={['#7EB8DA', '#5FA3CC']}
            onPress={() => onSelectRole('young_mom')}
            delay={300}
          />
          {onExit ? (
            <Pressable
              style={styles.exitBtn}
              onPress={onExit}
              accessibilityRole="button"
              accessibilityLabel={t('common.exit')}
            >
              <Ionicons name="log-out-outline" size={22} color="#FFFFFF" />
              <Text style={styles.exitLabel}>{t('common.exit')}</Text>
            </Pressable>
          ) : null}
        </View>
        {onOpenInstruction ? (
          <Pressable
            onPress={onOpenInstruction}
            style={styles.instructionBtn}
            accessibilityRole="button"
            accessibilityLabel={t('common.instruction')}
          >
            <Text style={styles.instructionText}>{t('common.instruction')}</Text>
          </Pressable>
        ) : null}
        {onOpenLanguage ? (
          <Pressable
            onPress={onOpenLanguage}
            style={styles.instructionBtn}
            accessibilityRole="button"
            accessibilityLabel={t('common.change_language')}
          >
            <Text style={styles.instructionText}>{t('common.change_language')}</Text>
          </Pressable>
        ) : null}
      </Animated.View>

      {onOpenInvite || onOpenTariffs ? (
        <View style={styles.topRight}>
          {onOpenTariffs ? (
            <Pressable
              onPress={onOpenTariffs}
              style={styles.tariffsBtn}
              accessibilityRole="link"
              accessibilityLabel={t('common.tariffs')}
            >
              <Text style={styles.tariffsText}>{t('common.tariffs')}</Text>
            </Pressable>
          ) : null}
          {onOpenInvite ? (
            <Pressable style={styles.inviteBtn} onPress={onOpenInvite}>
              <Text style={styles.inviteBtnText}>{t('invite.invite_friends')}</Text>
            </Pressable>
          ) : null}
        </View>
      ) : null}
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, width: '100%', height: '100%' },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.25)',
  },
  header: {
    paddingTop: 48,
    paddingHorizontal: 24,
    alignItems: 'flex-start',
  },
  appTitle: {
    fontFamily: READABLE_FONT,
    fontSize: 42,
    fontWeight: '700',
    color: '#3D2C2E',
    letterSpacing: 0.3,
    lineHeight: 50,
    textShadowColor: 'rgba(255,255,255,0.85)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
  },
  buttonsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 14,
    marginTop: 28,
  },
  roleBtn: {
    width: BTN_W,
    height: BTN_H,
    borderRadius: 14,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
  },
  roleGradient: {
    width: BTN_W,
    height: BTN_H,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 12,
  },
  roleLabel: {
    fontFamily: READABLE_FONT,
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
    textAlign: 'center',
    textShadowColor: 'rgba(45, 28, 30, 0.35)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  exitBtn: {
    width: BTN_W,
    height: BTN_H,
    borderRadius: 14,
    backgroundColor: 'rgba(136, 136, 136, 0.75)',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingHorizontal: 8,
  },
  exitLabel: {
    fontFamily: READABLE_FONT,
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  inviteBtn: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.75)',
  },
  inviteBtnText: {
    fontFamily: READABLE_FONT,
    fontSize: 13,
    color: '#4A4A4A',
    fontWeight: '600',
  },
  topRight: {
    position: 'absolute',
    right: 20,
    top: 48,
    alignItems: 'flex-end',
  },
  tariffsBtn: {
    paddingVertical: 6,
    paddingHorizontal: 4,
    marginBottom: 8,
  },
  tariffsText: {
    fontFamily: READABLE_FONT,
    fontSize: 13,
    color: '#4A4A4A',
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  instructionBtn: {
    marginTop: 18,
    paddingVertical: 8,
    paddingRight: 12,
    alignSelf: 'flex-start',
  },
  instructionText: {
    fontFamily: READABLE_FONT,
    fontSize: 20,
    color: '#3D2C2E',
    textDecorationLine: 'underline',
  },
});
