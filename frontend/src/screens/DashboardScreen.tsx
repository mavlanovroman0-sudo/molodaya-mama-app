import React from 'react';
import {
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { t } from '../i18n';
import { useAppStore } from '../store/appStore';

interface DashboardScreenProps {
  onSwitchRole: () => void;
}

export function DashboardScreen({ onSwitchRole }: DashboardScreenProps) {
  const { activeRole, features, tokenBalance, district } = useAppStore();

  const roleLabel =
    activeRole === 'housewife' ? t('roles.housewife') : t('roles.young_mom');

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>{roleLabel}</Text>
          {district ? <Text style={styles.district}>📍 {district}</Text> : null}
        </View>
        <View style={styles.tokens}>
          <Text style={styles.tokenLabel}>🪙 {tokenBalance}</Text>
        </View>
      </View>

      <Pressable style={styles.switchBtn} onPress={onSwitchRole}>
        <Text style={styles.switchText}>{t('common.switch_role')}</Text>
      </Pressable>

      <FlatList
        data={features}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.grid}
        renderItem={({ item }) => (
          <Pressable style={styles.featureCard}>
            <Text style={styles.featureIcon}>{iconFor(item.icon)}</Text>
            <Text style={styles.featureTitle} numberOfLines={2}>
              {t(item.title_key)}
            </Text>
          </Pressable>
        )}
      />
    </View>
  );
}

function iconFor(icon: string): string {
  const map: Record<string, string> = {
    search: '🔍',
    wallet: '💰',
    'credit-card': '💳',
    mic: '🎤',
    camera: '📷',
    heart: '❤️',
    map: '🗺️',
    bluetooth: '🔴',
    truck: '🚚',
    home: '🏠',
    car: '🚗',
    moon: '🌙',
    baby: '👶',
    alarm: '⏰',
    calculator: '🧮',
    video: '📹',
    book: '📖',
    users: '👥',
    list: '📋',
    trophy: '🏆',
    calendar: '📅',
    compass: '🧭',
    refresh: '♻️',
    hand: '✋',
    thermometer: '🌡️',
    smile: '😊',
  };
  return map[icon] || '✨';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F4F0',
    paddingTop: 56,
    paddingHorizontal: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '700',
    color: '#3D2C2E',
  },
  district: {
    fontSize: 14,
    color: '#7A6568',
    marginTop: 4,
  },
  tokens: {
    backgroundColor: '#fff',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  tokenLabel: {
    fontSize: 14,
    fontWeight: '600',
  },
  switchBtn: {
    alignSelf: 'flex-start',
    marginBottom: 16,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#E8E0DC',
    borderRadius: 20,
  },
  switchText: {
    fontSize: 14,
    color: '#5C4A4D',
  },
  grid: {
    paddingBottom: 32,
  },
  featureCard: {
    flex: 1,
    margin: 6,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    minHeight: 110,
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 4,
    maxWidth: '48%',
  },
  featureIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  featureTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#3D2C2E',
  },
});
