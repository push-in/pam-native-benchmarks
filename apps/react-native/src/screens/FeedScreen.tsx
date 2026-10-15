import { FlashList } from '@shopify/flash-list';
import { Image } from 'expo-image';
import { memo, useEffect, useRef, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { HOST, TEXT, bench, common } from '../shared';

type RawPost = { id?: number | string; title?: string; body?: string; image?: string; imageUrl?: string; image_url?: string };
type Post = { id: string; title: string; body: string; image: string };

function normalize(json: unknown): Post[] {
  const list = (Array.isArray(json) ? json : (json as { posts?: RawPost[] })?.posts ?? []) as RawPost[];
  return list.map((p, i) => {
    const image = p.image ?? p.imageUrl ?? p.image_url ?? `/img/${i}.jpg`;
    return {
      id: String(p.id ?? i),
      title: p.title ?? '',
      body: p.body ?? '',
      image: image.startsWith('http') ? image : `${HOST}${image.startsWith('/') ? '' : '/'}${image}`,
    };
  });
}

const PostItem = memo(function PostItem({ post }: { post: Post }) {
  return (
    <View style={styles.post}>
      <Image source={post.image} recyclingKey={post.image} style={styles.image} />
      <Text style={styles.title}>{post.title}</Text>
      <Text style={styles.body}>{post.body}</Text>
    </View>
  );
});

export default function FeedScreen() {
  const [posts, setPosts] = useState<Post[] | null>(null);
  const logged = useRef(false);

  useEffect(() => {
    let alive = true;
    fetch(`${HOST}/feed.json`)
      .then((res) => res.json())
      .then((json) => alive && setPosts(normalize(json)))
      .catch((e) => bench('error', { scenario: 'feed', message: String(e).replace(/\s+/g, '_') }));
    return () => {
      alive = false;
    };
  }, []);

  return (
    <SafeAreaView style={common.screen}>
      {posts ? (
        <FlashList
          data={posts}
          keyExtractor={(p) => p.id}
          renderItem={({ item }) => <PostItem post={item} />}
          onLoad={() => {
            if (logged.current) return;
            logged.current = true;
            // RN fetch goes through OkHttp's 10 MB HTTP cache; a 304 revalidation is
            // invisible to JS, so the idiomatic stack can only report "network".
            requestAnimationFrame(() => bench('ready', { scenario: 'feed', source: 'network' }));
          }}
        />
      ) : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  post: { paddingBottom: 16 },
  image: { width: '100%', aspectRatio: 1 },
  title: { fontSize: 16, fontWeight: 'bold', color: TEXT, marginHorizontal: 16, marginTop: 8 },
  body: { fontSize: 14, color: TEXT, marginHorizontal: 16, marginTop: 4 },
});
