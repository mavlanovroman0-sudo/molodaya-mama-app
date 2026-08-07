import React from 'react';
import {
  ImageBackground,
  Pressable,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { ImageSourcePropType } from 'react-native';

export type DashboardHotspot = {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  x: number;
  y: number;
  onPress: () => void;
};

type Props = {
  source: ImageSourcePropType;
  hotspots: DashboardHotspot[];
};

export function DashboardHotspots({ source, hotspots }: Props) {
  const { width, height } = useWindowDimensions();

  return (
    <View style={styles.root}>
      <ImageBackground source={source} style={styles.bg} resizeMode="cover">
        <View style={styles.dim} />
        {hotspots.map((spot) => {
          const left = (spot.x / 100) * width - 36;
          const top = (spot.y / 100) * height - 36;
          return (
            <Pressable
              key={`${spot.icon}-${spot.label}`}
              style={[styles.hotspot, { left, top, opacity: 0.85 }]}
              onPress={spot.onPress}
              accessibilityRole="button"
              accessibilityLabel={spot.label}
            >
              <View style={styles.iconCircle}>
                <Ionicons name={spot.icon} size={48} color="#FFFFFF" style={styles.iconShadow} />
              </View>
              <Text style={styles.label} numberOfLines={2}>
                {spot.label}
              </Text>
            </Pressable>
          );
        })}
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, width: '100%', height: '100%' },
  bg: { flex: 1, width: '100%', height: '100%' },
  dim: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.08)',
  },
  hotspot: {
    position: 'absolute',
    width: 72,
    alignItems: 'center',
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.45)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.35,
    shadowRadius: 4,
    elevation: 4,
  },
  iconShadow: {
    textShadowColor: 'rgba(0, 0, 0, 0.45)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
  },
  label: {
    marginTop: 4,
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
    textAlign: 'center',
    textShadowColor: 'rgba(0,0,0,0.6)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
    maxWidth: 88,
  },
});
