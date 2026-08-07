import React, { useCallback, useState } from 'react';

import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { RoleSelectScreen, type RoleId } from '../screens/RoleSelectScreen';

import { DashboardScreen } from '../screens/DashboardScreen';

import { InviteScreen } from '../screens/InviteScreen';

import { InviteBanner } from '../components/InviteBanner';

import { useRemoteConfig } from '../hooks/useRemoteConfig';

import { useInviteBanner } from '../hooks/useInviteBanner';

import { useAuth } from '../hooks/useAuth';

import { useAppStore } from '../store/appStore';

import { switchRole } from '../services/api';

import { HousewifeTabs } from './HousewifeTabs';

import { MomTabs } from './MomTabs';

import { createStackHeaderOptions } from './headerOptions';

import type { MainStackParamList } from './types';



const Stack = createNativeStackNavigator<MainStackParamList>();



const OFFLINE_FEATURES = {

  housewife: [

    { id: 'price_scout', title_key: 'features.price_scout', icon: 'search', route: '/housewife/price-scout' },

    { id: 'delivery', title_key: 'features.delivery', icon: 'truck', route: '/shared/delivery' },

    { id: 'smart_home', title_key: 'features.smart_home', icon: 'home', route: '/shared/smart-home' },

    { id: 'red_button', title_key: 'features.red_button', icon: 'bluetooth', route: '/housewife/red-button' },

  ],

  young_mom: [

    { id: 'feeding_tracker', title_key: 'features.feeding_tracker', icon: 'baby', route: '/mom/feeding' },

    { id: 'silence_mode', title_key: 'features.silence_mode', icon: 'moon', route: '/mom/silence' },

    { id: 'delivery', title_key: 'features.delivery', icon: 'truck', route: '/shared/delivery' },

    { id: 'nursery_climate', title_key: 'features.nursery_climate', icon: 'thermometer', route: '/mom/nursery' },

  ],

};



function RoleSelectRoute({

  navigation,

}: {

  navigation: { navigate: (name: keyof MainStackParamList) => void };

}) {

  const [transitioning, setTransitioning] = useState(false);

  const { token, setRole, setDashboard, setOffline, persistCache } = useAppStore();

  const { logout } = useAuth();

  const setAuthInitialRoute = useAppStore((s) => s.setAuthInitialRoute);

  const { getBoolean } = useRemoteConfig();

  const { visible: bannerVisible, dismiss: dismissBanner } = useInviteBanner(

    getBoolean('show_invite_banner')

  );



  const handleSelectRole = useCallback(

    async (role: RoleId) => {

      setTransitioning(true);

      setRole(role);



      try {

        if (token) {

          const data = await switchRole(token, role);

          setDashboard(data);

          setOffline(false);

        } else {

          setDashboard({

            features: OFFLINE_FEATURES[role],

            token_balance: 0,

            shared_data: {},

          });

          setOffline(true);

        }

      } catch {

        setDashboard({

          features: OFFLINE_FEATURES[role],

          token_balance: 0,

          shared_data: {},

        });

        setOffline(true);

      }



      await persistCache();

      setTransitioning(false);



      navigation.navigate(role === 'housewife' ? 'HousewifeApp' : 'MomApp');

    },

    [token, setRole, setDashboard, setOffline, persistCache, navigation]

  );

  const handleExit = useCallback(async () => {
    setAuthInitialRoute('Register');
    await logout();
  }, [logout, setAuthInitialRoute]);



  if (transitioning) {

    return (

      <View style={styles.loader}>

        <ActivityIndicator size="large" color="#7EB8DA" />

      </View>

    );

  }



  return (

    <View style={styles.wrapper}>

      {bannerVisible && (

        <InviteBanner

          onInvite={() => {

            dismissBanner();

            navigation.navigate('Invite');

          }}

          onDismiss={dismissBanner}

        />

      )}

      <RoleSelectScreen

        onSelectRole={handleSelectRole}

        onOpenInvite={() => navigation.navigate('Invite')}

        onExit={handleExit}

      />

    </View>

  );

}



function FeaturesDashboardRoute({ navigation }: { navigation: { goBack: () => void } }) {

  const setRole = useAppStore((s) => s.setRole);

  return (

    <DashboardScreen

      onSwitchRole={() => {

        setRole(null);

        navigation.goBack();

      }}

    />

  );

}



export function MainStackNavigator() {

  return (

    <Stack.Navigator

      screenOptions={({ navigation, route }) => {
        if (route.name === 'RoleSelect' || route.name === 'HousewifeApp' || route.name === 'MomApp') {
          return { headerShown: false };
        }
        return createStackHeaderOptions(navigation, route.name);
      }}
    >

      <Stack.Screen name="RoleSelect">

        {(props) => <RoleSelectRoute navigation={props.navigation} />}

      </Stack.Screen>

      <Stack.Screen name="HousewifeApp" component={HousewifeTabs} />

      <Stack.Screen name="MomApp" component={MomTabs} />

      <Stack.Screen name="FeaturesDashboard">

        {(props) => <FeaturesDashboardRoute navigation={props.navigation} />}

      </Stack.Screen>

      <Stack.Screen name="Invite" component={InviteScreen} />

    </Stack.Navigator>

  );

}



const styles = StyleSheet.create({

  wrapper: {

    flex: 1,

    backgroundColor: '#F8F4F0',

  },

  loader: {

    flex: 1,

    justifyContent: 'center',

    alignItems: 'center',

    backgroundColor: '#F8F4F0',

  },

});
