#!/usr/bin/env bash
# One command: build the three apps in release, boot (or reuse) a device,
# measure every scenario and write the Native | PAM | RN scoreboard.
#
#   suite/bench.sh                      # own emulator (AVD PamBench_API_36), x86_64
#   suite/bench.sh --serial <adb-id>    # existing device (arm64 phones: ABI=arm64-v8a)
#   suite/bench.sh --skip-build --only list,like --quick
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
serial=""
skip_build=0
abi=${ABI:-x86_64}
avd=${AVD:-PamBench_API_36}
port=${EMULATOR_PORT:-5590}
extra=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --serial) serial=$2; shift 2 ;;
        --skip-build) skip_build=1; shift ;;
        *) extra+=("$1"); shift ;;
    esac
done

lock="${root}/.build.lock"
if [[ ${skip_build} -eq 0 ]]; then
    "${root}/apps/native/build-release.sh"
    ABI="${abi}" "${root}/apps/pam/build-release.sh"
    "${root}/apps/react-native/build-release.sh" "${abi}"
fi

python3 "${root}/suite/server.py" &
server_pid=$!
started_emulator=0
cleanup() {
    kill "${server_pid}" 2>/dev/null || true
    if [[ ${started_emulator} -eq 1 ]]; then
        adb -s "${serial}" emu kill >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

if [[ -z ${serial} ]]; then
    serial="emulator-${port}"
    if ! adb devices | grep -q "^${serial}\s*device"; then
        setsid nohup "${ANDROID_HOME:-$HOME/Android/Sdk}/emulator/emulator" -avd "${avd}" -port "${port}" \
            -no-snapshot -no-boot-anim -no-audio -no-window -gpu host >/tmp/pam-bench-emulator.log 2>&1 &
        started_emulator=1
        adb -s "${serial}" wait-for-device
        until [[ $(adb -s "${serial}" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r') == 1 ]]; do sleep 2; done
        sleep 20
    fi
fi

id=$(date +%Y%m%d-%H%M%S)
out="${root}/suite/results/${id}"
python3 "${root}/suite/run.py" --serial "${serial}" --out "${out}" \
    --apk "native=${root}/apps/native/dist/native-release.apk" \
    --apk "pam=${root}/apps/pam/dist/pam-release-${abi}.apk" \
    --apk "rn=${root}/apps/react-native/dist/rn-release-${abi}.apk" \
    "${extra[@]}"
echo "Scoreboard: ${out}/scoreboard.md"
