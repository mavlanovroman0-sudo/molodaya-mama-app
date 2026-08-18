import React from 'react';
import { Image, Platform, type ImageSourcePropType, type StyleProp, type ImageStyle } from 'react-native';

const ICONS: Record<string, ImageSourcePropType> = {
  'list-outline': require('../../assets/icons/list.png'),
  list: require('../../assets/icons/list.png'),
  'swap-horizontal-outline': require('../../assets/icons/swap.png'),
  'swap-horizontal': require('../../assets/icons/swap.png'),
  'bar-chart-outline': require('../../assets/icons/chart.png'),
  'bar-chart': require('../../assets/icons/chart.png'),
  'stats-chart-outline': require('../../assets/icons/chart.png'),
  'home-outline': require('../../assets/icons/home.png'),
  home: require('../../assets/icons/home.png'),
  'nutrition-outline': require('../../assets/icons/apple.png'),
  nutrition: require('../../assets/icons/apple.png'),
  'bed-outline': require('../../assets/icons/bed.png'),
  bed: require('../../assets/icons/bed.png'),
  'water-outline': require('../../assets/icons/water.png'),
  water: require('../../assets/icons/water.png'),
  'checkbox-outline': require('../../assets/icons/checkbox.png'),
  checkbox: require('../../assets/icons/checkbox.png'),
  'people-outline': require('../../assets/icons/people.png'),
  people: require('../../assets/icons/people.png'),
  'heart-outline': require('../../assets/icons/heart.png'),
  heart: require('../../assets/icons/heart.png'),
  'cart-outline': require('../../assets/icons/cart.png'),
  cart: require('../../assets/icons/cart.png'),
  'bulb-outline': require('../../assets/icons/bulb.png'),
  bulb: require('../../assets/icons/bulb.png'),
  'person-outline': require('../../assets/icons/person.png'),
  person: require('../../assets/icons/person.png'),
  'moon-outline': require('../../assets/icons/moon.png'),
  moon: require('../../assets/icons/moon.png'),
  'log-out-outline': require('../../assets/icons/logout.png'),
};

export type AppIconName = keyof typeof ICONS;

type Props = {
  name: string;
  size: number;
  color: string;
  style?: StyleProp<ImageStyle>;
};

export function AppIcon({ name, size, color, style }: Props) {
  const source = ICONS[name] ?? ICONS.home;
  // На сайте tintColor через SVG-фильтр часто делает картинку невидимой
  // (пустые кружки). Иконки уже белые — на вебе показываем их как есть.
  const tintColor = Platform.OS === 'web' ? undefined : color;
  return (
    <Image
      source={source}
      tintColor={tintColor}
      style={[{ width: size, height: size }, style]}
      resizeMode="contain"
    />
  );
}
