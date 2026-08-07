import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { navTheme } from '../theme/navigationTheme';

type Props = {
  name: keyof typeof Ionicons.glyphMap;
  color: string;
  focused: boolean;
};

export function TabBarIcon({ name, color, focused }: Props) {
  const scale = useRef(new Animated.Value(focused ? 1.1 : 1)).current;

  useEffect(() => {
    Animated.spring(scale, {
      toValue: focused ? 1.12 : 1,
      friction: 6,
      useNativeDriver: true,
    }).start();
  }, [focused, scale]);

  return (
    <Animated.View style={[styles.wrap, { transform: [{ scale }] }]}>
      <Ionicons name={name} size={navTheme.iconSize} color={color} />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    alignItems: 'center',
    justifyContent: 'center',
  },
});
