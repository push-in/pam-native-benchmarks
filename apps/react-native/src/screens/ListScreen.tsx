import { FlashList } from '@shopify/flash-list';
import { memo, useCallback, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { GREY, PALETTE, TEXT, bench, common, lcg } from '../shared';
import { WORDS } from '../words';

const COUNT = 10_000;
const DATA = Array.from({ length: COUNT }, (_, i) => i);

function cardBody(i: number): string {
  const next = lcg(42 + i);
  const sentences: string[] = [];
  for (let s = 0; s < (i % 4) + 1; s++) {
    const words: string[] = [];
    for (let w = 0; w < 8; w++) words.push(WORDS[next() % WORDS.length]);
    const sentence = words.join(' ');
    sentences.push(sentence.charAt(0).toUpperCase() + sentence.slice(1) + '.');
  }
  return sentences.join(' ');
}

const CompactRow = memo(function CompactRow({ i }: { i: number }) {
  return (
    <View style={styles.compact}>
      <Text style={styles.title}>Item {i}</Text>
      <Text style={styles.subtitle}>Subtitle for item {i}</Text>
    </View>
  );
});

const AvatarRow = memo(function AvatarRow({ i }: { i: number }) {
  return (
    <View style={styles.avatarRow}>
      <View style={[styles.avatar, { backgroundColor: PALETTE[i % 8] }]}>
        <Text style={styles.initials}>I{i % 10}</Text>
      </View>
      <View style={styles.texts}>
        <Text style={styles.title}>Item {i}</Text>
        <Text style={styles.subtitle}>Subtitle for item {i}</Text>
      </View>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>{i % 100}</Text>
      </View>
    </View>
  );
});

const CardRow = memo(function CardRow({ i }: { i: number }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>Card {i}</Text>
      <Text style={styles.body}>{cardBody(i)}</Text>
    </View>
  );
});

function renderItem({ item }: { item: number }) {
  const type = item % 3;
  if (type === 0) return <CompactRow i={item} />;
  if (type === 1) return <AvatarRow i={item} />;
  return <CardRow i={item} />;
}

export default function ListScreen() {
  const [loaded, setLoaded] = useState(false);
  const onLoad = useCallback(() => {
    if (loaded) return;
    setLoaded(true);
    bench('ready', { scenario: 'list' });
  }, [loaded]);

  return (
    <SafeAreaView style={common.screen}>
      <FlashList
        data={DATA}
        renderItem={renderItem}
        keyExtractor={String}
        getItemType={(item) => item % 3}
        onLoad={onLoad}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  compact: { height: 64, paddingHorizontal: 16, justifyContent: 'center' },
  avatarRow: { height: 72, paddingHorizontal: 16, flexDirection: 'row', alignItems: 'center' },
  avatar: { width: 48, height: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  initials: { color: '#FFFFFF', fontWeight: 'bold' },
  texts: { flex: 1 },
  badge: { backgroundColor: '#EEF2FF', borderRadius: 999, paddingHorizontal: 10, paddingVertical: 2 },
  badgeText: { color: TEXT, fontSize: 13 },
  card: { marginVertical: 8, marginHorizontal: 16, padding: 16, borderRadius: 12, backgroundColor: '#F3F4F6' },
  title: { fontSize: 16, fontWeight: 'bold', color: TEXT },
  subtitle: { fontSize: 13, color: GREY },
  body: { fontSize: 14, color: TEXT, marginTop: 4 },
});
