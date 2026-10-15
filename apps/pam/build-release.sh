#!/usr/bin/env bash
# Release-optimized benchmark APK (R8, non-debuggable, baseline profile,
# <profileable shell="true"/>) for the x86_64 emulator, copied to
# dist/pam-release-x86_64.apk. ABI override: ABI=arm64-v8a ./build-release.sh
set -euo pipefail

cd "$(dirname "$0")"
ABI="${ABI:-x86_64}"
LOCK="$(cd ../.. && pwd)/.build.lock"
GRADLE_HOME="${PAM_NATIVE_GRADLE_HOME:-${GRADLE_USER_HOME:-${XDG_CACHE_HOME:-$HOME/.cache}/pam-native/gradle}}"

# Low-RAM host: bounded daemon heap and workers.
export GRADLE_OPTS="${GRADLE_OPTS:-} -Dorg.gradle.jvmargs=-Xmx2560m -Dorg.gradle.workers.max=3"

daemons() { pgrep -f 'org.gradle.launcher.daemon.bootstrap.GradleDaemon' | sort || true; }

before="$(daemons)"
stop_own_daemons() {
    # Stop only the Gradle daemons this build started.
    comm -13 <(printf '%s\n' "$before") <(daemons) | while read -r pid; do
        [ -n "$pid" ] && kill "$pid" 2>/dev/null || true
    done
}
trap stop_own_daemons EXIT

# The local plugin is a Composer path package installed as a copy: refresh it.
rsync -a --delete packages/localhost-cleartext/ vendor/bench/localhost-cleartext/

flock "$LOCK" pam build . --benchmark --abi "$ABI"

name="$(php -r 'echo json_decode(file_get_contents("pam-native.json"), true)["name"];')"
version="$(php -r 'echo json_decode(file_get_contents("pam-native.json"), true)["versionName"];')"
apk="dist/${name}-${version}-android-benchmark.apk"
[ -f "$apk" ] || { echo "missing $apk" >&2; exit 1; }
cp "$apk" "dist/pam-release-${ABI}.apk"
echo "dist/pam-release-${ABI}.apk ($(du -h "dist/pam-release-${ABI}.apk" | cut -f1))"
