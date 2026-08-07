import React, { useMemo } from 'react';
import type { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { DashboardIconGrid } from '../../components/DashboardIconGrid';
import { useTranslation } from '../../hooks/useTranslation';
import type { MomTabParamList } from '../../navigation/types';
import { images } from '../../theme/assets';

type Props = BottomTabScreenProps<MomTabParamList, 'Home'>;

export function YoungMomDashboard({ navigation }: Props) {
  const { t } = useTranslation();

  const rows = useMemo(
    () => [
      [
        {
          icon: 'nutrition-outline' as const,
          label: t('tabs.feeding'),
          onPress: () => navigation.navigate('Feeding'),
        },
        {
          icon: 'bed-outline' as const,
          label: t('tabs.sleep'),
          onPress: () => navigation.navigate('Sleep'),
        },
        {
          icon: 'water-outline' as const,
          label: t('tabs.diapers'),
          onPress: () => navigation.navigate('Diapers'),
        },
      ],
      [
        {
          icon: 'checkbox-outline' as const,
          label: t('tabs.checklist'),
          onPress: () => navigation.navigate('Checklist'),
        },
        {
          icon: 'people-outline' as const,
          label: t('tabs.nanny'),
          onPress: () => navigation.navigate('Nanny'),
        },
        {
          icon: 'heart-outline' as const,
          label: t('tabs.health'),
          onPress: () => navigation.navigate('Health'),
        },
      ],
    ],
    [navigation, t]
  );

  return <DashboardIconGrid source={images.youngMomBg} rows={rows} />;
}
