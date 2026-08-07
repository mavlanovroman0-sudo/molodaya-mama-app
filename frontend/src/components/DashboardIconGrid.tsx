import React from 'react';
import {
  ImageBackground,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { ImageSourcePropType } from 'react-native';

export type DashboardGridItem = {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
};

type Props = {
  source: ImageSourcePropType;
  rows: DashboardGridItem[][];
};

export function DashboardIconGrid({ source, rows }: Props) {
  return (
    <View style={styles.root}>
      <ImageBackground
        source={source}
        style={styles.bg}
        resizeMode="cover"
      >
        <View style={styles.grid}>
          {rows.map((row, rowIndex) => (
            <View
              key={`row-${rowIndex}`}
              style={[styles.row, row.length < 3 && styles.rowCentered]}
            >
              {row.map((item) => (
                <Pressable
                  key={item.label}
                  style={styles.item}
                  onPress={item.onPress}
                  accessibilityRole="button"
                  accessibilityLabel={item.label}
                >
                  <View style={styles.iconCircle}>
                    <Ionicons name={item.icon} size={48} color="#FFFFFF" style={styles.iconShadow} />
                  </View>
                  <Text style={styles.label} numberOfLines={2}>
                    {item.label}
                  </Text>
                </Pressable>
              ))}
            </View>
          ))}
        </View>
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    width: '100%',
    height: '100%',
    backgroundColor: '#F8F4F0',
  },
  bg: {
    flex: 1,
    width: '100%',
    height: '100%',
    justifyContent: 'center',
  },
  bgImage: {
    resizeMode: 'cover',
  },
  grid: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 12,
    gap: 30,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'flex-start',
    gap: 20,
  },
  rowCentered: {
    justifyContent: 'center',
  },
  item: {
    width: 96,
    alignItems: 'center',
    opacity: 0.92,
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(0, 0, 0, 0.28)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.5)',
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
    marginTop: 6,
    fontSize: 12,
    fontWeight: '600',
    color: '#2D1C1E',
    textAlign: 'center',
    textShadowColor: 'rgba(255,255,255,0.85)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
    maxWidth: 92,
  },
});
