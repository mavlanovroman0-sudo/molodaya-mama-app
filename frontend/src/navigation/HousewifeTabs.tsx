import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTranslation } from '../hooks/useTranslation';
import { HousewifeDashboard } from '../screens/dashboards/HousewifeDashboard';
import { ShoppingListsScreen } from '../screens/housewife/ShoppingListsScreen';
import { BarterScreen } from '../screens/housewife/BarterScreen';
import { SmartHomeScreen } from '../screens/housewife/SmartHomeScreen';
import { ReportScreen } from '../screens/housewife/ReportScreen';
import { ProfileScreen } from '../screens/ProfileScreen';
import { SubscriptionScreen } from '../screens/SubscriptionScreen';
import { InviteScreen } from '../screens/InviteScreen';
import { PrivacyPolicyScreen } from '../screens/PrivacyPolicyScreen';
import { TermsScreen } from '../screens/TermsScreen';
import { createStackHeaderOptions } from './headerOptions';
import { createTabNavigatorScreenOptions, tabIcon } from './tabScreenOptions';
import type { HousewifeTabParamList, ProfileStackParamList } from './types';

const Tab = createBottomTabNavigator<HousewifeTabParamList>();
const ProfileStack = createNativeStackNavigator<ProfileStackParamList>();

function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator
      screenOptions={({ navigation, route }) =>
        createStackHeaderOptions(navigation, route.name)
      }
    >
      <ProfileStack.Screen name="Profile" component={ProfileScreen} />
      <ProfileStack.Screen name="Invite" component={InviteScreen} />
      <ProfileStack.Screen name="Subscription" component={SubscriptionScreen} />
      <ProfileStack.Screen name="PrivacyPolicy" component={PrivacyPolicyScreen} />
      <ProfileStack.Screen name="Terms" component={TermsScreen} />
    </ProfileStack.Navigator>
  );
}

export function HousewifeTabs() {
  const { t } = useTranslation();

  return (
    <Tab.Navigator
      screenOptions={({ navigation, route }) =>
        createTabNavigatorScreenOptions(navigation, route.name)
      }
    >
      <Tab.Screen
        name="Home"
        component={HousewifeDashboard}
        options={{
          tabBarLabel: t('tabs.home'),
          tabBarIcon: tabIcon('home-outline', 'home'),
        }}
      />
      <Tab.Screen
        name="Shopping"
        component={ShoppingListsScreen}
        options={{
          tabBarLabel: t('tabs.shopping'),
          tabBarIcon: tabIcon('cart-outline', 'cart'),
        }}
      />
      <Tab.Screen
        name="Barter"
        component={BarterScreen}
        options={{
          tabBarLabel: t('tabs.barter'),
          tabBarIcon: tabIcon('swap-horizontal-outline', 'swap-horizontal'),
        }}
      />
      <Tab.Screen
        name="SmartHome"
        component={SmartHomeScreen}
        options={{
          tabBarLabel: t('tabs.smart_home'),
          tabBarIcon: tabIcon('bulb-outline', 'bulb'),
        }}
      />
      <Tab.Screen
        name="Report"
        component={ReportScreen}
        options={{
          tabBarLabel: 'Отчёт',
          tabBarIcon: tabIcon('bar-chart-outline', 'bar-chart'),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStackNavigator}
        options={{
          headerShown: false,
          tabBarLabel: t('tabs.profile'),
          tabBarIcon: tabIcon('person-outline', 'person'),
        }}
      />
    </Tab.Navigator>
  );
}
