import { NavigationContainer, useFocusEffect } from '@react-navigation/native';
import { createNativeStackNavigator, type NativeStackScreenProps } from '@react-navigation/native-stack';
import { Image } from 'expo-image';
import { useCallback } from 'react';
import { Pressable, ScrollView, StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { HOST, TEXT, bench, common } from '../shared';

type StackParams = { Screen: { k: number } };
const Stack = createNativeStackNavigator<StackParams>();
const ROWS = Array.from({ length: 50 }, (_, j) => j);

function StackScreen({ navigation, route }: NativeStackScreenProps<StackParams, 'Screen'>) {
  const { k } = route.params;

  useFocusEffect(
    useCallback(() => {
      const id = requestAnimationFrame(() => bench('ready', { scenario: 'nav', k }));
      return () => cancelAnimationFrame(id);
    }, [k]),
  );

  return (
    <SafeAreaView style={common.screen}>
      <Text style={styles.title}>Screen {k}</Text>
      <Image source={`${HOST}/img/${k}.jpg`} style={styles.image} />
      <Pressable accessibilityLabel="next" accessibilityRole="button" onPress={() => navigation.push('Screen', { k: k + 1 })} style={styles.button}>
        <Text style={styles.buttonText}>next</Text>
      </Pressable>
      <ScrollView style={styles.scroll}>
        {ROWS.map((j) => (
          <Text key={j} style={styles.row}>Row {j}</Text>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

export default function NavScreen() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#FFFFFF' } }}>
        <Stack.Screen name="Screen" component={StackScreen} initialParams={{ k: 0 }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: 'bold', color: TEXT, margin: 16 },
  image: { width: '100%', height: 200 },
  button: { alignSelf: 'flex-start', margin: 16, paddingHorizontal: 16, paddingVertical: 10, backgroundColor: '#E5E7EB', borderRadius: 8 },
  buttonText: { fontSize: 16, color: TEXT },
  scroll: { flex: 1 },
  row: { fontSize: 16, color: TEXT, paddingHorizontal: 16, paddingVertical: 8 },
});
