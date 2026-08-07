import { StyleSheet } from 'react-native';
import { navTheme } from './navigationTheme';

export const colors = {
  primary: '#FF69B4',
  primaryHousewife: '#FF69B4',
  primaryMom: '#FF69B4',
  background: '#F8F4F0',
  textDark: '#3D2C2E',
  textGray: '#4A4A4A',
  textMuted: '#7A6568',
  border: '#E8E0DC',
  white: '#FFFFFF',
  headerPink: navTheme.headerBg,
};

export const formStyles = StyleSheet.create({
  label: {
    fontSize: 14,
    color: colors.textGray,
    marginBottom: 6,
    fontWeight: '500',
  },
  input: {
    backgroundColor: colors.white,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textDark,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
  },
  primaryButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  primaryButtonDisabled: {
    opacity: 0.7,
  },
  secondaryButton: {
    backgroundColor: colors.white,
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.primary,
    marginTop: 8,
  },
  secondaryButtonText: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: '600',
  },
});

export const tabBarOptions = {
  tabBarLabelStyle: {
    fontSize: 11,
    fontWeight: '600' as const,
    marginBottom: 2,
  },
  tabBarActiveTintColor: navTheme.tabActive,
  tabBarInactiveTintColor: navTheme.tabInactive,
  tabBarStyle: {
    height: 68,
    paddingBottom: 8,
    paddingTop: 6,
    backgroundColor: navTheme.tabBarBg,
    borderTopColor: '#FF69B4',
    borderTopWidth: 1,
  },
};
