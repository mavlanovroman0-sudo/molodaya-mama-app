import React from 'react';
import {
  ImageBackground,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import type { ImageSourcePropType } from 'react-native';
import { AppIcon } from './AppIcon';
import { uiFontStyle } from '../theme/fonts';

export type DashboardGridItem = {
  icon: string;
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
                    <AppIcon name={item.icon} size={34} color="#FFFFFF" />
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
  },
  grid: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingBottom: 12,
    gap: 28,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'flex-start',
    gap: 22,
  },
  rowCentered: {
    justifyContent: 'center',
  },
  item: {
    width: 88,
    alignItems: 'center',
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.7)',
    overflow: 'visible',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.35,
    shadowRadius: 4,
    elevation: 4,
  },
  label: {
    ...uiFontStyle,
    marginTop: 6,
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
    textAlign: 'center',
    includeFontPadding: false,
    maxWidth: 88,
    textShadowColor: 'rgba(0, 0, 0, 0.85)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
    backgroundColor: 'rgba(0, 0, 0, 0.35)',
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
    overflow: 'hidden',
  },
});
