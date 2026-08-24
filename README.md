<!-- pam:product-page:start -->
<div align="center">

# PAM Native Benchmarks

**Comparable mobile performance claims, measured on the same device.**

Versioned workloads and evidence contracts for comparing PAM Native, React Native, Flutter, and platform-native implementations.

[![Release](https://img.shields.io/github/v/release/push-in/pam-native-benchmarks?style=flat-square&label=stable)](https://github.com/push-in/pam-native-benchmarks/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/push-in/pam-native-benchmarks/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/push-in/pam-native-benchmarks/actions)
![PHP](https://img.shields.io/badge/PHP-8.5-777BB4?style=flat-square&logo=php&logoColor=white)
![License](https://img.shields.io/github/license/push-in/pam-native-benchmarks?style=flat-square)

**[Documentation](https://github.com/push-in/pam-native-benchmarks/tree/main/docs) · [Why this exists](#why-this-exists) · [What you can build](#what-you-can-build) · [Quick start](#quick-start) · [Issues](https://github.com/push-in/pam-native-benchmarks/issues)**

</div>

---

## Why this exists

Versioned workloads and evidence contracts for comparing PAM Native, React Native, Flutter, and platform-native implementations.

| | |
| --- | --- |
| **Role** | Benchmark laboratory |
| **Execution path** | Android Macrobenchmark · iOS XCTest metrics |
| **This repository owns** | Workload definitions, measurement protocol, budgets, and evidence format |
| **Boundary** | Results are device/build specific; this repository does not publish universal marketing numbers |

## What you can build

- Same-device startup and frame-time comparisons
- Detecting performance regressions before releases
- Publishing reproducible benchmark evidence instead of anecdotes

## Quick start

```bash
git clone https://github.com/push-in/pam-native-benchmarks.git
cd pam-native-benchmarks
./scripts/verify.sh
```

The **[PAM documentation](https://github.com/push-in/pam-native-benchmarks/tree/main/docs)** covers prerequisites, production setup, and the complete workflow. PAM projects keep normal manifests and lockfiles; product features stay in the package that owns them.
<!-- pam:product-page:end -->

Public, reproducible same-device evidence for PAM Native, React Native,
Flutter, and platform-native applications. This repository publishes the
comparison contract and verifier—not a predeclared winner. Results are emitted
only for measurements shared by every submitted framework report.

The comparison harness accepts React Native as the required public baseline and
optional Flutter and platform-native reports. A matrix is emitted only for
measurements present in every report, preventing selective claims:

```bash
python3 compare.py \
  --pam evidence/pam --react-native evidence/react-native \
  --flutter evidence/flutter --native evidence/platform-native \
  --output evidence/framework-matrix.md
```

The Android host contains a `:macrobenchmark` module with three identical,
automation-friendly scenarios:

1. cold startup from clean application state until `reportFullyDrawn()`;
2. 30 keyed property patches, including memory plus decode/mount trace sections;
3. repeated flings through 10,000 recycled rows.

Run Pam Native:

```bash
pam mobile benchmark path/to/project
```

The benchmark module is a separate instrumented application. Gradle installs
the minified `benchmark` target and its test APK together, so the measurement
never falls back to an already-running `.debug` application. The command fails
when the target cannot be installed or discovered.

Generate the startup Baseline Profile independently with:

```bash
pam mobile profile path/to/project
```

An equivalent React Native/New Architecture app must expose the accessibility
targets and payloads declared in `contract.json`. A Nitro comparison should add
the same native round-trip operation to both apps; Nitro Modules is not itself a
UI renderer, so its module-call latency must not be confused with list or
startup performance.

Compare the generated AndroidX JSON reports:

```bash
python3 compare.py \
  --pam results/pam \
  --react-native results/react-native \
  --output results/comparison.md
```

The comparison validates both reports against `contract.json` and refuses to
produce a table if either implementation omits a required scenario or metric.
It publishes every shared median, P50, P95, P99 and maximum supplied by
AndroidX, so tail-frame regressions cannot be hidden behind a good median.

Block a release when startup, mount, memory or tail-frame latency regresses:

```bash
python3 gate.py --report results/pam
```

The checked-in `budgets.json` is intentionally stricter than a generic
"benchmark completed" check: absent metrics fail, and list P95/P99 are gated
independently so a good median cannot hide visible jank.

Use the same physical device, release-like non-debuggable targets, a stable thermal
state and the same compilation mode. Keep raw JSON and Perfetto traces as CI
artifacts. Record APK/AAB size separately because it is a build artifact rather
than a runtime metric; the CI release gate reports it alongside these results.

The harness originated in
[`push-in/pam-native`](https://github.com/push-in/pam-native/tree/v0.7.0/benchmarks/mobile)
and is published independently so competitors can inspect, fork, reproduce,
and challenge every comparison.

`REFERENCE.md` records the latest physical-device Pam Native baseline and its
remaining tail-latency caveat.

## Verifiable evidence

Create and immediately verify an integrity manifest before publishing or
uploading a result directory:

```bash
python3 evidence.py results/pam 1
python3 evidence.py results/pam 1 --verify
```

The manifest hashes every AndroidX report, Perfetto trace, log, and other result
artifact recursively. It separately hashes `contract.json` and `budgets.json`,
so changing the benchmark scenario or its release limits invalidates existing
evidence. Suite IDs are sequential integers: `1` for a PAM baseline and `2` for
a framework comparison.
