import React from 'react';
import type { BottomTabNavigationOptions } from '@react-navigation/bottom-tabs';
import type { NavigationProp, ParamListBase } from '@react-navigation/native';
import { AnimatedTabBarButton } from '../components/AnimatedTabBarButton';
import { TabBarIcon } from '../components/TabBarIcon';
import { tabBarOptions } from '../theme/formStyles';
import { createStackHeaderOptions } from './headerOptions';

export function createTabNavigatorScreenOptions(
  navigation: NavigationProp<ParamListBase>,
  routeName: string
): BottomTabNavigationOptions {
  return {
    ...tabBarOptions,
    ...createStackHeaderOptions(navigation, routeName),
    tabBarButton: (props) => <AnimatedTabBarButton {...props} />,
  };
}

export function tabIcon(
  outline: React.ComponentProps<typeof TabBarIcon>['name'],
  filled: React.ComponentProps<typeof TabBarIcon>['name']
) {
  return ({ color, focused }: { color: string; focused: boolean }) => (
    <TabBarIcon name={focused ? filled : outline} color={color} focused={focused} />
  );
}
