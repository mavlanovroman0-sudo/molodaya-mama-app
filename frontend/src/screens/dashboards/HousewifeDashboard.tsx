import React, { useMemo } from 'react';
import type { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { DashboardIconGrid } from '../../components/DashboardIconGrid';
import { useTranslation } from '../../hooks/useTranslation';
import type { HousewifeTabParamList } from '../../navigation/types';
import { images } from '../../theme/assets';

type Props = BottomTabScreenProps<HousewifeTabParamList, 'Home'>;

export function HousewifeDashboard({ navigation }: Props) {
  const { t } = useTranslation();

  const rows = useMemo(
    () => [
      [
        {
          icon: 'list-outline' as const,
          label: t('tabs.shopping'),
          onPress: () => navigation.navigate('Shopping'),
        },
        {
          icon: 'swap-horizontal-outline' as const,
          label: t('tabs.barter'),
          onPress: () => navigation.navigate('Barter'),
        },
        {
          icon: 'checkbox-outline' as const,
          label: t('tabs.tasks'),
          onPress: () => navigation.navigate('Report'),
        },
      ],
      [
        {
          icon: 'home-outline' as const,
          label: t('tabs.smart_home'),
          onPress: () => navigation.navigate('SmartHome'),
        },
        {
          icon: 'stats-chart-outline' as const,
          label: t('tabs.report'),
          onPress: () => navigation.navigate('Report'),
        },
      ],
    ],
    [navigation, t]
  );

  return <DashboardIconGrid source={images.housewifeBg} rows={rows} />;
}
