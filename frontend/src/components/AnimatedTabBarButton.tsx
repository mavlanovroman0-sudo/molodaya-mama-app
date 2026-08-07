import React from 'react';
import { Pressable, StyleSheet, type PressableProps } from 'react-native';
import { navTheme } from '../theme/navigationTheme';

type Props = PressableProps & {
  accessibilityState?: { selected?: boolean };
};

/** Подложка для активной вкладки таб-бара. */
export function AnimatedTabBarButton({ children, style, accessibilityState, ...rest }: Props) {
  const focused = accessibilityState?.selected;

  return (
    <Pressable style={[styles.btn, style, focused && styles.btnActive]} {...rest}>
      {children}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 14,
    marginHorizontal: 2,
    marginVertical: 4,
  },
  btnActive: {
    backgroundColor: navTheme.tabActiveBg,
  },
});
