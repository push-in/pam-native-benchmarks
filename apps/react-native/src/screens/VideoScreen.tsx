import { useVideoPlayer, VideoView } from 'expo-video';
import { useRef } from 'react';
import { StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { HOST, bench, common } from '../shared';

export default function VideoScreen() {
  const player = useVideoPlayer(`${HOST}/video.mp4`, (p) => {
    p.loop = true;
    p.muted = true;
    p.play();
  });
  const logged = useRef(false);

  return (
    <SafeAreaView style={common.screen}>
      <VideoView
        player={player}
        nativeControls={false}
        contentFit="contain"
        style={styles.video}
        onFirstFrameRender={() => {
          if (logged.current) return;
          logged.current = true;
          bench('ready', { scenario: 'video' });
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  video: { width: '100%', aspectRatio: 16 / 9 },
});
