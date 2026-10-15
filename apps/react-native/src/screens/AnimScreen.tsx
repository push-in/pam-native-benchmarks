import { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import Animated, { Easing, useAnimatedStyle, useSharedValue, withRepeat, withTiming } from 'react-native-reanimated';
import { SafeAreaView } from 'react-native-safe-area-context';

import { common, useReady } from '../shared';

export default function AnimScreen() {
  const rotation = useSharedValue(0);
  const translateX = useSharedValue(0);

  useEffect(() => {
    rotation.value = withRepeat(withTiming(360, { duration: 1000, easing: Easing.linear }), -1, false);
    translateX.value = withRepeat(withTiming(150, { duration: 1000, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, [rotation, translateX]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }, { rotate: `${rotation.value}deg` }],
  }));

  useReady('anim');

  return (
    <SafeAreaView style={[common.screen, styles.pad]}>
      <View>
        <Animated.View style={[styles.square, animatedStyle]} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  pad: { padding: 16 },
  square: { width: 100, height: 100, backgroundColor: '#3B82F6' },
});
