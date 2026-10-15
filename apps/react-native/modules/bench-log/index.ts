import { requireNativeModule } from 'expo-modules-core';

type BenchLogNative = { log(message: string): void };

const native = requireNativeModule<BenchLogNative>('BenchLog');

/** One logcat line with tag BENCH: `<event> key=value ...`. */
export function bench(event: string, fields: Record<string, string | number> = {}): void {
  let line = event;
  for (const key in fields) {
    line += ` ${key}=${fields[key]}`;
  }
  native.log(line);
}
