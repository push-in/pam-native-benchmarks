import { useState } from 'react';
import { StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { TEXT, common, useReady } from '../shared';

type UserRecord = { id: number; name: string; email: string; age: number; score: number; tags: string[] };

function build(n: number): UserRecord[] {
  const records: UserRecord[] = new Array(n);
  for (let i = 0; i < n; i++) {
    records[i] = {
      id: i,
      name: `User ${i}`,
      email: `user${i}@example.com`,
      age: i % 90,
      score: i * 0.5,
      tags: [`t${i % 7}`, `t${i % 11}`, `t${i % 13}`],
    };
  }
  return records;
}

export default function StateScreen({ n }: { n: number }) {
  const [records] = useState(() => build(n));
  useReady('state', true, { n });
  return (
    <SafeAreaView style={[common.screen, styles.pad]}>
      <Text style={styles.text}>{records.length} records</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  pad: { padding: 16 },
  text: { fontSize: 18, color: TEXT },
});
