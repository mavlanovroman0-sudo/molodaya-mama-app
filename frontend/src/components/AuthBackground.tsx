import React from 'react';
import {
  ImageBackground,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  View,
  type ViewStyle,
} from 'react-native';
import { images } from '../theme/assets';

type Props = {
  children: React.ReactNode;
  keyboard?: boolean;
  contentStyle?: ViewStyle;
};

export function AuthBackground({ children, keyboard, contentStyle }: Props) {
  const body = (
    <ImageBackground source={images.authBg} style={styles.bg} resizeMode="cover">
      <View style={styles.overlay} />
      <View style={[styles.content, contentStyle]}>{children}</View>
    </ImageBackground>
  );

  if (keyboard) {
    return (
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {body}
      </KeyboardAvoidingView>
    );
  }

  return <View style={styles.flex}>{body}</View>;
}

const styles = StyleSheet.create({
  flex: { flex: 1, width: '100%', height: '100%' },
  bg: { flex: 1, width: '100%', height: '100%' },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(248, 244, 240, 0.35)',
  },
  content: {
    flex: 1,
  },
});
