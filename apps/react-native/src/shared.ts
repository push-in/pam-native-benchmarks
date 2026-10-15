import { useEffect } from 'react';
import { StyleSheet } from 'react-native';

export { bench } from '../modules/bench-log';
import { bench } from '../modules/bench-log';

export const HOST = 'https://127.0.0.1:8099';
export const TEXT = '#111827';
export const GREY = '#6B7280';
export const PALETTE = ['#EF4444', '#F97316', '#EAB308', '#22C55E', '#06B6D4', '#3B82F6', '#8B5CF6', '#EC4899'];

/** LCG from the contract: x = (x * 1103515245 + 12345) mod 2^31. next() advances, then returns x. */
export function lcg(seed: number): () => number {
  let x = seed;
  return () => {
    x = (Math.imul(x, 1103515245) + 12345) & 0x7fffffff;
    return x;
  };
}

/** Logs `ready scenario=<id>` after the first frame that shows the committed content. */
export function useReady(scenario: string, when = true, extra?: Record<string, string | number>): void {
  useEffect(() => {
    if (!when) return;
    const id = requestAnimationFrame(() => bench('ready', { scenario, ...extra }));
    return () => cancelAnimationFrame(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [when]);
}

export const common = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#FFFFFF' },
  text: { color: TEXT },
});
