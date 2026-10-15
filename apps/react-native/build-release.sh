#!/usr/bin/env bash
# Builds the release APK for the RN bench app.
# Usage: ./build-release.sh [x86_64|arm64-v8a]   -> dist/rn-release-<abi>.apk
set -euo pipefail

ABI="${1:-x86_64}"
case "$ABI" in x86_64|arm64-v8a) ;; *) echo "ABI must be x86_64 or arm64-v8a" >&2; exit 1 ;; esac

HERE="$(cd "$(dirname "$0")" && pwd)"
LOCK="$(cd "$HERE/../.." && pwd)/.build.lock"
cd "$HERE"

[ -d node_modules ] || npm install --prefer-offline --no-audit --no-fund
if [ ! -f android/app/build.gradle ] || [ app.json -nt android/app/build.gradle ] || [ plugins/withBenchRelease.js -nt android/app/build.gradle ]; then
  CI=1 node node_modules/expo/bin/cli prebuild --platform android --no-install
fi

mkdir -p dist
(
  flock 9
  cd android
  status=0
  NODE_ENV=production ./gradlew :app:assembleRelease \
    --max-workers=3 \
    -Dorg.gradle.jvmargs=-Xmx2560m \
    -Pkotlin.compiler.execution.strategy=in-process \
    -PreactNativeArchitectures="$ABI" || status=$?
  ./gradlew --stop >/dev/null 2>&1 || true
  exit $status
) 9>"$LOCK"

cp android/app/build/outputs/apk/release/app-release.apk "dist/rn-release-$ABI.apk"
ls -lh "dist/rn-release-$ABI.apk"
