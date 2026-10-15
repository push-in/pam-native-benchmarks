import { useEffect, useState } from 'react';
import { StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { runCompute } from '../compute';
import { TEXT, bench, common } from '../shared';

export default function ComputeScreen() {
  const [status, setStatus] = useState('Running…');

  useEffect(() => {
    // After the first frame: log ready, then run the operations.
    const id = requestAnimationFrame(() => {
      bench('ready', { scenario: 'compute' });
      setTimeout(() => {
        runCompute().then(
          () => setStatus('Done'),
          (e) => {
            bench('error', { scenario: 'compute', message: String(e).replace(/\s+/g, '_') });
            setStatus('Error');
          },
        );
      }, 0);
    });
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <SafeAreaView style={[common.screen, styles.pad]}>
      <Text style={styles.text}>Compute: {status}</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  pad: { padding: 16 },
  text: { fontSize: 18, color: TEXT },
});
