import { FlashList } from '@shopify/flash-list';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { TEXT, bench, common, useReady } from '../shared';

const DATA = Array.from({ length: 200 }, (_, i) => i);

// Module-level render counter: incremented in every component render body.
let renders = 0;

const LikeRow = memo(function LikeRow({ id, liked, onToggle }: { id: number; liked: boolean; onToggle: (id: number) => void }) {
  renders++;
  const likes = (id * 7) % 50;
  return (
    <View style={[styles.row, liked && styles.likedRow]}>
      <Text style={styles.title}>Post {id}</Text>
      <Pressable accessibilityLabel={`like-${id}`} accessibilityRole="button" onPress={() => onToggle(id)} style={styles.button}>
        <Text style={styles.likeText}>{liked ? `♥ ${likes + 1}` : `♡ ${likes}`}</Text>
      </Pressable>
    </View>
  );
});

export default function LikeScreen() {
  renders++;
  const [liked, setLiked] = useState<Record<number, true>>({});
  const likedRef = useRef(liked);
  likedRef.current = liked;
  const rendersAtLike = useRef(-1);

  const onToggle = useCallback((id: number) => {
    const now = likedRef.current[id] !== true;
    bench('like', { i: id, liked: now ? 1 : 0 });
    rendersAtLike.current = renders;
    setLiked((prev) => {
      const next = { ...prev };
      if (now) next[id] = true;
      else delete next[id];
      return next;
    });
  }, []);

  // Runs after each like commit: renders since the previous like.
  useEffect(() => {
    if (rendersAtLike.current < 0) return;
    bench('rerender', { count: renders - rendersAtLike.current });
  }, [liked]);

  useReady('like');

  return (
    <SafeAreaView style={common.screen}>
      <FlashList
        data={DATA}
        keyExtractor={String}
        extraData={liked}
        renderItem={({ item }) => <LikeRow id={item} liked={liked[item] === true} onToggle={onToggle} />}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  row: { paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#FFFFFF' },
  likedRow: { backgroundColor: '#FFE4E6' },
  title: { fontSize: 16, fontWeight: 'bold', color: TEXT },
  button: { alignSelf: 'flex-start', paddingVertical: 6 },
  likeText: { fontSize: 15, color: TEXT },
});
