import { useEffect, useState } from 'react';
import { Linking, StatusBar } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import AnimScreen from './screens/AnimScreen';
import ComputeScreen from './screens/ComputeScreen';
import FeedScreen from './screens/FeedScreen';
import FilterScreen from './screens/FilterScreen';
import GridScreen from './screens/GridScreen';
import HomeScreen from './screens/HomeScreen';
import LikeScreen from './screens/LikeScreen';
import ListScreen from './screens/ListScreen';
import NavScreen from './screens/NavScreen';
import StateScreen from './screens/StateScreen';
import VideoScreen from './screens/VideoScreen';

type Route = { scenario: string; params: Record<string, string>; url: string };

function parse(url: string | null): Route {
  const match = url ? /^bench:\/\/([^/?#]*)\/?(?:\?([^#]*))?/.exec(url) : null;
  const params: Record<string, string> = {};
  for (const pair of (match?.[2] ?? '').split('&')) {
    if (!pair) continue;
    const [k, v = ''] = pair.split('=');
    params[decodeURIComponent(k)] = decodeURIComponent(v);
  }
  return { scenario: match?.[1] || 'home', params, url: url ?? '' };
}

function Scenario({ route }: { route: Route }) {
  switch (route.scenario) {
    case 'list': return <ListScreen />;
    case 'grid': return <GridScreen />;
    case 'like': return <LikeScreen />;
    case 'filter': return <FilterScreen />;
    case 'anim': return <AnimScreen />;
    case 'nav': return <NavScreen />;
    case 'video': return <VideoScreen />;
    case 'feed': return <FeedScreen />;
    case 'compute': return <ComputeScreen />;
    case 'state': return <StateScreen n={Number(route.params.n ?? 0) || 0} />;
    default: return <HomeScreen />;
  }
}

export default function App() {
  const [route, setRoute] = useState<Route | null>(null);

  useEffect(() => {
    let alive = true;
    Linking.getInitialURL().then((url) => alive && setRoute(parse(url)), () => alive && setRoute(parse(null)));
    const sub = Linking.addEventListener('url', ({ url }) => setRoute(parse(url)));
    return () => {
      alive = false;
      sub.remove();
    };
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1, backgroundColor: '#FFFFFF' }}>
      <SafeAreaProvider>
        <StatusBar barStyle="dark-content" backgroundColor="transparent" translucent />
        {route ? <Scenario key={route.url} route={route} /> : null}
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
