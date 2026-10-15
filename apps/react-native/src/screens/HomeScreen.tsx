import { StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { TEXT, common, useReady } from '../shared';

export default function HomeScreen() {
  useReady('home');
  return (
    <SafeAreaView style={[common.screen, styles.pad]}>
      <Text style={styles.title}>Bench</Text>
      <Text style={styles.line}>Line 1</Text>
      <Text style={styles.line}>Line 2</Text>
      <Text style={styles.line}>Line 3</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  pad: { padding: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: TEXT, marginBottom: 8 },
  line: { fontSize: 16, color: TEXT },
});
