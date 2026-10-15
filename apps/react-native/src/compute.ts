import { HOST, bench, lcg } from './shared';
import { sha256Hex } from './sha256';
import { WORDS } from './words';

function median(values: number[]): number {
  const s = [...values].sort((a, b) => a - b);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

function run(op: string, fn: () => string | number): void {
  const times: number[] = [];
  let check: string | number = '';
  for (let r = 0; r < 5; r++) {
    const t0 = performance.now();
    check = fn();
    times.push(performance.now() - t0);
  }
  bench('compute', { op, ms: median(times).toFixed(3), check });
}

function utf8Length(s: string): number {
  let n = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    if (c < 0x80) n += 1;
    else if (c < 0x800) n += 2;
    else if (c >= 0xd800 && c <= 0xdbff) { n += 4; i++; }
    else n += 3;
  }
  return n;
}

function buildDocs(): string[] {
  const next = lcg(42);
  const docs: string[] = new Array(100_000);
  for (let d = 0; d < 100_000; d++) {
    const words: string[] = [];
    for (let w = 0; w < 8; w++) words.push(WORDS[next() % 64]);
    docs[d] = words.join(' ').toLowerCase();
  }
  return docs;
}

function searchQuery(docs: string[]): number {
  let hits = 0;
  for (let q = 0; q < 100; q++) {
    const a = WORDS[q % 64].toLowerCase();
    const b = WORDS[(q * 7 + 3) % 64].toLowerCase();
    hits += docs.filter((d) => d.includes(a) && d.includes(b)).length;
  }
  return hits;
}

type Rec = { name: string; n: number };

function buildRecords(): Rec[] {
  const next = lcg(42);
  const recs: Rec[] = new Array(100_000);
  for (let i = 0; i < 100_000; i++) {
    recs[i] = { name: `${WORDS[next() % 64]} ${WORDS[next() % 64]}`, n: next() % 100_000 };
  }
  return recs;
}

type Item = { id: number; v: number };

function buildDiffLists(): [Item[], Item[]] {
  const a: Item[] = [];
  const b: Item[] = [];
  for (let i = 0; i < 100_000; i++) {
    a.push({ id: i, v: i });
    if (i % 250 === 0) continue; // multiples of 250 removed
    b.push({ id: i, v: i % 100 === 0 ? i + 1 : i }); // remaining multiples of 100 changed
  }
  for (let id = 100_000; id < 100_400; id++) b.push({ id, v: id });
  return [a, b];
}

function diff(a: Item[], b: Item[]): string {
  const before = new Map<number, number>();
  for (const it of a) before.set(it.id, it.v);
  let ins = 0;
  let chg = 0;
  let kept = 0;
  for (const it of b) {
    const v = before.get(it.id);
    if (v === undefined) ins++;
    else {
      kept++;
      if (v !== it.v) chg++;
    }
  }
  return `${ins}/${a.length - kept}/${chg}`;
}

export async function runCompute(): Promise<void> {
  let docs: string[] = [];
  run('search_build', () => (docs = buildDocs()).length);
  run('search_query', () => searchQuery(docs));
  docs = [];

  const text = await (await fetch(`${HOST}/compute.json`)).text();
  let parsed: unknown[] = [];
  run('json_parse', () => (parsed = JSON.parse(text) as unknown[]).length);
  run('json_stringify', () => utf8Length(JSON.stringify(parsed)));
  parsed = [];

  const records = buildRecords();
  run('sort', () => {
    const sorted = records.slice().sort((x, y) => (x.name < y.name ? -1 : x.name > y.name ? 1 : x.n - y.n));
    return sorted[0].n;
  });

  const buf = new Uint8Array(10 * 1024 * 1024);
  for (let i = 0; i < buf.length; i++) buf[i] = i & 0xff;
  run('sha256', () => sha256Hex(buf).slice(0, 8));

  const [a, b] = buildDiffLists();
  run('diff', () => diff(a, b));

  bench('compute done');
}
