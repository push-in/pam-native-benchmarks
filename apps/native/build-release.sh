#!/usr/bin/env bash
# Builds the signed (debug keystore) release APK into dist/native-release.apk.
set -euo pipefail
cd "$(dirname "$0")"
LOCK="$(cd ../.. && pwd)/.build.lock"
if [[ ! -f local.properties && -z "${ANDROID_HOME:-}" ]]; then
  echo "sdk.dir=$HOME/Android/Sdk" > local.properties
fi
flock "$LOCK" bash -c '
  rc=0
  ./gradlew --max-workers=3 -Dorg.gradle.jvmargs=-Xmx2g \
    -Pkotlin.compiler.execution.strategy=in-process :app:assembleRelease || rc=$?
  ./gradlew --stop >/dev/null || true
  exit $rc
'
mkdir -p dist
cp app/build/outputs/apk/release/app-release.apk dist/native-release.apk
ls -l dist/native-release.apk
