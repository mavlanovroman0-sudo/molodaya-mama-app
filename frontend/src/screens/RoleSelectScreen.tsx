import React, { useEffect, useRef } from 'react';
import {
  Animated,
  ImageBackground,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { t } from '../i18n';
import { images } from '../theme/assets';

export type RoleId = 'housewife' | 'young_mom';

const BTN_W = 120;
const BTN_H = 50;

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
          <Text style={styles.roleLabel} numberOfLines={1}>
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
  onExit?: () => void;
}

export function RoleSelectScreen({ onSelectRole, onOpenInvite, onExit }: RoleSelectScreenProps) {
  const titleAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(titleAnim, { toValue: 1, duration: 700, useNativeDriver: true }).start();
  }, [titleAnim]);

  const experiencedMomLabel = `👩‍🍳 ${t('roles.experienced_mom')}`;
  const momLabel = `👶 ${t('roles.young_mom')}`;

  return (
    <ImageBackground source={images.authBg} style={styles.screen} resizeMode="cover">
      <View style={styles.overlay} />
      <Animated.View style={[styles.header, { opacity: titleAnim }]}>
        <Text style={styles.appTitle}>{t('app.title')}</Text>
        <Text style={styles.subtitle}>{t('app.subtitle')}</Text>
      </Animated.View>

      <View style={styles.bottomBar}>
        <RoleCard
          label={experiencedMomLabel}
          gradient={['#D4919A', '#C47A84']}
          onPress={() => onSelectRole('housewife')}
          delay={150}
        />
        <RoleCard
          label={momLabel}
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
            <Ionicons name="log-out-outline" size={18} color="#FFFFFF" style={styles.exitIcon} />
            <Text style={styles.exitLabel}>{t('common.exit')}</Text>
          </Pressable>
        ) : null}
      </View>

      {onOpenInvite ? (
        <Pressable style={styles.inviteBtn} onPress={onOpenInvite}>
          <Text style={styles.inviteBtnText}>{t('invite.invite_friends')}</Text>
        </Pressable>
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
    paddingTop: 56,
    paddingHorizontal: 24,
    alignItems: 'flex-start',
  },
  appTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#3D2C2E',
    letterSpacing: -0.5,
    textShadowColor: 'rgba(255,255,255,0.8)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#4A4A4A',
    marginTop: 8,
    lineHeight: 22,
  },
  bottomBar: {
    position: 'absolute',
    left: 20,
    bottom: 20,
    flexDirection: 'row',
    gap: 10,
  },
  roleBtn: {
    width: BTN_W,
    height: BTN_H,
    borderRadius: 12,
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
    paddingHorizontal: 10,
  },
  roleLabel: {
    fontSize: 13,
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
    borderRadius: 12,
    backgroundColor: 'rgba(136, 136, 136, 0.75)',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    paddingHorizontal: 6,
  },
  exitIcon: {
    marginRight: 2,
  },
  exitLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  inviteBtn: {
    position: 'absolute',
    right: 20,
    top: 48,
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.75)',
  },
  inviteBtnText: {
    fontSize: 13,
    color: '#4A4A4A',
    fontWeight: '600',
  },
});
