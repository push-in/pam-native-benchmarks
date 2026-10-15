import { FlashList } from '@shopify/flash-list';
import { Image } from 'expo-image';
import { memo, useCallback, useRef } from 'react';
import { StyleSheet, View, useWindowDimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { HOST, bench, common } from '../shared';

const DATA = Array.from({ length: 500 }, (_, i) => i);

const Cell = memo(function Cell({ i, size, onDisplay }: { i: number; size: number; onDisplay?: () => void }) {
  const uri = `${HOST}/img/${i}.jpg`;
  return (
    <View style={{ width: size, height: size, padding: 1 }}>
      <Image source={uri} recyclingKey={uri} style={styles.image} onDisplay={onDisplay} />
    </View>
  );
});

export default function GridScreen() {
  const { width } = useWindowDimensions();
  const size = width / 3;
  const logged = useRef(false);
  const onFirstDisplay = useCallback(() => {
    if (logged.current) return;
    logged.current = true;
    requestAnimationFrame(() => bench('ready', { scenario: 'grid' }));
  }, []);

  return (
    <SafeAreaView style={common.screen}>
      <FlashList
        data={DATA}
        numColumns={3}
        keyExtractor={String}
        renderItem={({ item }) => <Cell i={item} size={size} onDisplay={onFirstDisplay} />}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  image: { flex: 1 },
});
