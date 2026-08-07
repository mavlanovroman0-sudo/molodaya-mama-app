import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTranslation } from '../hooks/useTranslation';
import { YoungMomDashboard } from '../screens/dashboards/YoungMomDashboard';
import { BabyFeedScreen } from '../screens/mom/BabyFeedScreen';
import { BabySleepScreen } from '../screens/mom/BabySleepScreen';
import { BabyDiaperScreen } from '../screens/mom/BabyDiaperScreen';
import { BabyChecklistScreen } from '../screens/mom/BabyChecklistScreen';
import { BabyHealthScreen } from '../screens/mom/BabyHealthScreen';
import { NannyScreen } from '../screens/mom/NannyScreen';
import { ProfileScreen } from '../screens/ProfileScreen';
import { SubscriptionScreen } from '../screens/SubscriptionScreen';
import { InviteScreen } from '../screens/InviteScreen';
import { PrivacyPolicyScreen } from '../screens/PrivacyPolicyScreen';
import { TermsScreen } from '../screens/TermsScreen';
import { createStackHeaderOptions } from './headerOptions';
import { createTabNavigatorScreenOptions, tabIcon } from './tabScreenOptions';
import type { MomTabParamList, ProfileStackParamList } from './types';

const Tab = createBottomTabNavigator<MomTabParamList>();
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

export function MomTabs() {
  const { t } = useTranslation();

  return (
    <Tab.Navigator
      screenOptions={({ navigation, route }) =>
        createTabNavigatorScreenOptions(navigation, route.name)
      }
    >
      <Tab.Screen
        name="Home"
        component={YoungMomDashboard}
        options={{
          tabBarLabel: t('tabs.home'),
          tabBarIcon: tabIcon('home-outline', 'home'),
        }}
      />
      <Tab.Screen
        name="Feeding"
        component={BabyFeedScreen}
        options={{
          tabBarLabel: t('tabs.feeding'),
          tabBarIcon: tabIcon('nutrition-outline', 'nutrition'),
        }}
      />
      <Tab.Screen
        name="Sleep"
        component={BabySleepScreen}
        options={{
          tabBarLabel: t('tabs.sleep'),
          tabBarIcon: tabIcon('moon-outline', 'moon'),
        }}
      />
      <Tab.Screen
        name="Diapers"
        component={BabyDiaperScreen}
        options={{
          tabBarLabel: t('tabs.diapers'),
          tabBarIcon: tabIcon('water-outline', 'water'),
        }}
      />
      <Tab.Screen
        name="Checklist"
        component={BabyChecklistScreen}
        options={{
          tabBarLabel: t('tabs.checklist'),
          tabBarIcon: tabIcon('checkbox-outline', 'checkbox'),
        }}
      />
      <Tab.Screen
        name="Nanny"
        component={NannyScreen}
        options={{
          tabBarLabel: t('tabs.nanny'),
          tabBarIcon: tabIcon('people-outline', 'people'),
        }}
      />
      <Tab.Screen
        name="Health"
        component={BabyHealthScreen}
        options={{
          tabBarButton: () => null,
          tabBarLabel: t('tabs.health'),
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
