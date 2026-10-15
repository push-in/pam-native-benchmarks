import { FlashList } from '@shopify/flash-list';
import { memo, useMemo, useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { GREY, TEXT, common, lcg, useReady } from '../shared';
import { WORDS } from '../words';

type Row = { id: number; label: string; lower: string };

function buildRows(): Row[] {
  const next = lcg(42);
  const rows: Row[] = [];
  for (let i = 0; i < 10_000; i++) {
    const label = `Name ${i} ${WORDS[next() % WORDS.length]}`;
    rows.push({ id: i, label, lower: label.toLowerCase() });
  }
  return rows;
}

const FilterRow = memo(function FilterRow({ label }: { label: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
});

export default function FilterScreen() {
  const [rows] = useState(buildRows);
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    return q ? rows.filter((r) => r.lower.includes(q)) : rows;
  }, [rows, query]);

  useReady('filter');

  return (
    <SafeAreaView style={common.screen}>
      <TextInput
        accessibilityLabel="filter-input"
        placeholder="Filter"
        placeholderTextColor={GREY}
        value={query}
        onChangeText={setQuery}
        caretHidden
        autoCorrect={false}
        autoCapitalize="none"
        style={styles.input}
      />
      <Text style={styles.count}>{filtered.length} results</Text>
      <FlashList
        data={filtered}
        keyExtractor={(r) => String(r.id)}
        renderItem={({ item }) => <FilterRow label={item.label} />}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  input: { marginHorizontal: 16, marginTop: 8, paddingHorizontal: 12, height: 44, borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, color: TEXT, fontSize: 16 },
  count: { marginHorizontal: 16, marginVertical: 8, color: GREY, fontSize: 13 },
  row: { height: 48, paddingHorizontal: 16, justifyContent: 'center' },
  label: { fontSize: 16, color: TEXT },
});
