# Framework suite: Native | PAM Native | React Native

Three functionally identical Android apps, each written the idiomatic way for
its stack. The harness (`suite/run.py`) builds them in release, installs them on
one device, drives every scenario with the same adb input and computes the
ratios `PAM/Native` (overhead, target <= 1.1x) and `RN/PAM` (advantage).

| App | Path | applicationId | Stack |
| --- | --- | --- | --- |
| Native | `apps/native` | `dev.bench.native` | Kotlin, Views + RecyclerView, Coil 3, Media3, OkHttp |
| PAM | `apps/pam` | `dev.bench.pam` | PAM Native (latest published), PHP components |
| RN | `apps/react-native` | `dev.bench.rn` | RN 0.85 New Arch + Hermes, Expo 56 modules, FlashList v2, Reanimated 4, expo-image, Gesture Handler, react-navigation native-stack, expo-video |

Before measuring, `run.py` launches each screen (`home`, `list`, `grid`, `like`, `filter`) once per
app without measuring: what a fresh install fills once (compiled templates and opcodes, bundle and
image disk caches) is not counted as a cold start, for any app.

The PAM list scenarios (`list`, `grid`, `like`, `filter`) are written the common way, as
templates with `p-for` (`apps/pam/src/Templates`). `run.py --pam-api builder` opens the same
scenarios through the PHP builder API (`?api=builder`, `apps/pam/src/Screens`) to measure both paths.

## Run

```bash
suite/bench.sh                       # builds the 3 apps in release, boots AVD PamBench_API_36, measures all
suite/bench.sh --skip-build --only list,like --quick
suite/bench.sh --serial <adb id>     # an existing device (ABI=arm64-v8a for phones)
python3 suite/scoreboard.py <raw.json> [out.md] [--candidate other/raw.json]
```

Results land in `suite/results/<timestamp>/` (`raw.json`, `scoreboard.md`).

## How it measures

- One device, one app at a time; each app is installed fresh and compiled
  `cmd package compile -m speed` (same ART state for all three).
- Cold start: `am force-stop` + `drop_caches`, `am start -W` (TTID =
  `TotalTime`), TTFD = the app's `ready` log plus the frames that follow it
  until the content settles (`gfxinfo framestats`).
- Touch/key → pixel: raw evdev events written to the touchscreen/keyboard
  (`/dev/input`), a `BENCHT` log marker right before the UP/key event, and the
  last `FrameCompleted` of the frame burst that follows it.
- Frames: `dumpsys gfxinfo` (p50/p90/p95/p99, jank). CPU: `utime+stime` of the
  app process. Wakeups: voluntary + involuntary context switches of the app's
  threads. Memory: `dumpsys meminfo` PSS. Battery: `batterystats` estimated
  mAh per UID (estimates; zero when below the reporting threshold).
- Network: bytes served by `suite/server.py` (HTTPS, test CA in `tls/`).
- Emulator numbers carry host-load noise (±30% on CPU-bound runs): compare
  ratios from the same run, repeat A/B alternately for small deltas.

## Common rules

- Release build, R8/minify on, non-debuggable, `<profileable android:shell="true"/>`,
  x86_64 ABI for the emulator (arm64-v8a for phones). The asset server speaks
  HTTPS with the test CA `suite/tls/bench-ca.pem`; every app trusts it through
  its network security config (`<trust-anchors>`: system + that CA), no
  cleartext.
- Launch: `adb shell am start -W -n <pkg>/<launcher activity> -a android.intent.action.VIEW -d 'bench://<scenario>?<params>'`.
  The app reads the scenario from the launch intent data URI. No URI → `home`.
  Every app must also react to the URI on a cold start (that is the only path the harness uses).
- Asset server on the host, reachable on the device at `https://127.0.0.1:8099`
  (`adb reverse tcp:8099 tcp:8099`):
  - `/img/{i}.jpg`, i = 0..499, 480x480 JPEG;
  - `/video.mp4`, 1280x720 H.264, 30 fps;
  - `/feed.json` (50 posts, `ETag` + `Cache-Control: no-cache`);
  - `/compute.json` (~5 MB array of objects).
- Logging: one logcat line per event with tag `BENCH`, message
  `<event> key=value key=value` (e.g. `ready scenario=list`). Emit
  `ready scenario=<id>` once the first content of the scenario is on screen
  (after the first frame that shows it, not before data arrives).
- Interactive elements expose the given accessibility label / content
  description (RN: `accessibilityLabel`, Native: `contentDescription`,
  PAM: accessibility label) so the harness can find them with `uiautomator dump`.
- No press ripple/highlight/opacity feedback on interactive elements (so the
  first frame after a tap is the frame of the state change).
- White background `#FFFFFF`, text `#111827`, default system font. Status bar
  and nav bar insets respected (content not under system bars).
- Deterministic data: LCG `x = (x * 1103515245 + 12345) mod 2^31`, seed `42`.
  `WORDS` = the 64 words in `suite/words.txt` (one per line, bundled in each app
  or inlined as a constant).

## Scenarios (URI host)

1. `home` — static screen: title "Bench" (28sp bold) and three body lines
   "Line 1".."Line 3". Used for cold start (TTID/TTFD), idle 60 s / 10 min and
   background 10 min. Nothing may tick, poll or animate.
2. `list` — vertically scrolling virtualized list (RN FlashList v2, Native
   RecyclerView with 3 view types, PAM VirtualizedList) of 10,000 items,
   item `i` type `i % 3`:
   - 0 compact row, 64dp: title `Item {i}` 16sp bold + subtitle `Subtitle for item {i}` 13sp grey;
   - 1 avatar row, 72dp: 48dp circle with color `PALETTE[i % 8]` and the
     initials `I{i%10}` in white, two texts as above, right-aligned pill badge
     with `{i % 100}` (bg `#EEF2FF`, radius 999);
   - 2 card, variable height: margin 8/16, padding 16, radius 12, bg
     `#F3F4F6`, title `Card {i}` + body = `(i % 4) + 1` sentences, sentence
     `k` = 8 words picked with the LCG over `WORDS`, capitalized, ending in `.`.
     The LCG is seeded with `42 + i` per card (so recycling is stable).
   `PALETTE = #EF4444 #F97316 #EAB308 #22C55E #06B6D4 #3B82F6 #8B5CF6 #EC4899`.
3. `grid` — 3-column virtualized grid of 500 square images
   `https://127.0.0.1:8099/img/{i}.jpg`, 2dp gaps, cells sized to screen width/3
   (RN FlashList numColumns + expo-image, Native GridLayoutManager + Coil,
   PAM VirtualGrid + Image). Images decoded at cell size (each framework's
   default downsampling for the view size). Default memory + disk cache.
4. `like` — virtualized list of 200 rows, row `i`: title `Post {i}`, below it a
   text button `♡ {likes}` (likes = `i * 7 % 50`) with accessibility label
   `like-{i}`. Tapping toggles liked: label becomes `♥ {likes+1}` and the row
   background becomes `#FFE4E6`. State lives in the screen (RN: `useState` of a
   Set/Record + memoized row component keyed by id; Native: adapter
   `notifyItemChanged(i, payload)`; PAM: component state). Log
   `like i={i} liked={0|1}` from the handler. RN additionally counts component
   renders (a module counter incremented in each component render body) and
   logs `rerender count={n}` in a `useEffect` after each like commit (n = renders
   since the previous like). Native logs `rerender count=1` (one bound
   ViewHolder). PAM logs whatever its renderer telemetry reports for the patch
   (nodes, bytes) as `rerender count={nodes} bytes={bytes}` if available.
5. `filter` — a TextInput (label `filter-input`, placeholder `Filter`) above
   a virtualized list of 10,000 rows `Name {i} {word}` (word = `WORDS[lcg]`),
   and a counter text `{n} results`. The input hides its caret (RN `caretHidden`, Native `isCursorVisible = false`, PAM equivalent) so cursor blinking does not produce frames. Every text change filters synchronously
   (case-insensitive substring, no debounce) and re-renders the list.
6. `anim` — a 100dp square `#3B82F6` that rotates 360° per 1000 ms, linear,
   infinite, and moves translateX 0→150dp→0 per 2000 ms ease-in-out, infinite.
   RN: Reanimated 4 (`withRepeat(withTiming)`), Native: `ObjectAnimator`/
   `ValueAnimator`, PAM: its native-driven animation API (no PHP per frame).
7. `nav` — stack navigation. Root and every detail screen show `Screen {k}`
   (root k=0), a 200dp-high image `https://127.0.0.1:8099/img/{k}.jpg`, a
   button with label `next` that pushes screen `k+1`, and 50 text rows
   `Row {j}` in a ScrollView. Back = system back (`adb shell input keyevent 4`).
   RN: @react-navigation/native-stack; Native: Fragments with back stack;
   PAM: `Route::stack`. Log `ready scenario=nav k={k}` on each screen show.
8. `video` — one player, full width 16:9, `https://127.0.0.1:8099/video.mp4`,
   autoplay, loop, muted, no controls. RN: expo-video, Native: Media3
   ExoPlayer + PlayerView/SurfaceView, PAM: MediaPlayer.
9. `feed` — on open, GET `/feed.json` and render its 50 posts in a virtualized
   list: image 1:1 (full width), title, body. Use each stack's idiomatic data
   loading and caching (RN: `fetch` + `useEffect`/`useState` + expo-image
   default cache; Native: OkHttp with a 10 MB disk `Cache` + Coil default;
   PAM: whatever the framework provides idiomatically, e.g. HTTP client cache /
   persisted state). Log `ready scenario=feed source=<network|cache>`.
   The harness measures bytes served by the host server on first open and on
   reopen after `am force-stop`.
10. `compute` — runs, after the first frame, each operation 5 times and logs
    `compute op=<op> ms=<median float> check=<value>`, then `compute done`:
    - `search_build`: build the searchable representation of 100,000 docs,
      doc `d` = 8 words from `WORDS` via one LCG stream (seed 42) joined by
      spaces; `search_query`: run 100 queries (query q = the two words
      `WORDS[q % 64]` and `WORDS[(q * 7 + 3) % 64]`, AND semantics,
      case-insensitive substring/token match), `check` = total hits.
      Idiomatic baseline: lowercase array + `filter(includes)` (RN), Kotlin
      `filter { contains }` (Native), PHP `str_contains` (PAM). A framework
      indexed API (Rust) is reported as an extra op `search_query_indexed`.
    - `json_parse` / `json_stringify` of `/compute.json` (downloaded once,
      not timed), `check` = array length / output byte length.
    - `sort`: sort 100,000 records `{name: "<w1> <w2>", n}` built from one LCG
      stream seeded 42 (per record: w1 = WORDS[x1 % 64], w2 = WORDS[x2 % 64],
      n = x3 % 100000) by name then n; `check` = first record n.
    - `sha256`: SHA-256 of a 10 MiB buffer filled with `i & 0xFF`;
      `check` = first 8 hex chars. Idiomatic API of each stack
      (RN: expo-crypto if used by the app, else a JS implementation — say which).
    - `diff`: two keyed lists of 100,000 `{id, v}`; list B = A with every
      100th item's `v` changed, every 250th removed and 400 new ids appended;
      compute inserted/removed/changed counts; `check` = `ins/rem/chg`.
      A = `{id: i, v: i}` for i < 100000; B: ids multiple of 250 removed,
      remaining ids multiple of 100 get `v + 1`, ids 100000..100399 appended.
      Expected `400/400/800`.
    - `search_build` `check` = number of docs (100000).
11. `state` — `bench://state?n=<N>` builds N records
    `{id, name: "User {i}", email: "user{i}@example.com", age: i % 90,
    score: i * 0.5, tags: ["t{i%7}", "t{i%11}", "t{i%13}"]}` into app state
    (kept referenced by the screen) and shows `{N} records`; log
    `ready scenario=state n={N}`. Harness measures PSS at N=0 and N=100000.
