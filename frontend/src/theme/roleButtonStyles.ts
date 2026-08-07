import { StyleSheet } from 'react-native';

/** Компактные кнопки выбора роли и похожие CTA (60–70 × 200–250 px). */
export const ROLE_BUTTON_WIDTH = 240;
export const ROLE_BUTTON_HEIGHT = 64;

export const roleButtonStyles = StyleSheet.create({
  pressable: {
    width: ROLE_BUTTON_WIDTH,
    height: ROLE_BUTTON_HEIGHT,
    borderRadius: 14,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
  },
  gradient: {
    width: ROLE_BUTTON_WIDTH,
    height: ROLE_BUTTON_HEIGHT,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  label: {
    fontSize: 19,
    fontWeight: '700',
    color: '#FFFFFF',
    textAlign: 'center',
    letterSpacing: 0.2,
    textShadowColor: 'rgba(45, 28, 30, 0.35)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  stack: {
    alignItems: 'center',
    gap: 24,
  },
});
