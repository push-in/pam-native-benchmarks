#!/usr/bin/env python3
"""Same-device framework suite: Native | PAM Native | React Native.

Drives every scenario of SCENARIOS.md through adb with identical input on one
device, one app at a time, and writes raw.json plus a scoreboard.

  python3 suite/run.py --serial emulator-5590 --out suite/results/<id> \
      --apk native=apps/native/dist/native-release.apk \
      --apk pam=apps/pam/dist/pam-release-x86_64.apk \
      --apk rn=apps/react-native/dist/rn-release-x86_64.apk \
      [--only list,like] [--quick]

`--quick` shortens the long idle/background windows (for smoke runs only; the
scoreboard marks them).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PKGS = {"native": "dev.bench.native", "pam": "dev.bench.pam", "rn": "dev.bench.rn"}
SERVER = "https://127.0.0.1:8099"
import ssl as _ssl
_CTX = _ssl.create_default_context(cafile=str(Path(__file__).with_name("tls") / "bench-ca.pem"))
HZ = 100  # USER_HZ on Android kernels


class Device:
    def __init__(self, serial: str):
        self.serial = serial
        self.touch = None
        self._touch_primary = False
        self.keyboard = None
        self.size = (1080, 2400)

    def sh(self, cmd: str, timeout: float = 120, check: bool = False) -> str:
        r = subprocess.run(["adb", "-s", self.serial, "shell", cmd], capture_output=True, text=True, timeout=timeout)
        if check and r.returncode != 0:
            raise RuntimeError(f"adb shell {cmd!r} failed: {r.stderr.strip()}")
        return r.stdout

    def adb(self, *args: str, timeout: float = 600) -> str:
        r = subprocess.run(["adb", "-s", self.serial, *args], capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError(f"adb {' '.join(args)} failed: {r.stderr.strip()} {r.stdout.strip()}")
        return r.stdout

    # ---------- setup ----------
    def setup(self) -> dict:
        try:
            self.adb("root", timeout=30)
            time.sleep(2)
            self.adb("wait-for-device", timeout=60)
        except Exception:
            pass
        self.root = self.sh("id -u").strip() == "0"
        self.sh("svc power stayon true; settings put system screen_off_timeout 2147483647; "
                "input keyevent 224; wm dismiss-keyguard; cmd statusbar collapse; "
                "settings put secure stylus_handwriting_enabled 0; settings put secure show_ime_with_hard_keyboard 0")
        self.adb("reverse", "tcp:8099", "tcp:8099")
        m = re.search(r"(\d+)x(\d+)", self.sh("wm size"))
        if m:
            self.size = (int(m.group(1)), int(m.group(2)))
        self._find_input_devices()
        props = {k: self.sh(f"getprop {k}").strip() for k in
                 ("ro.product.model", "ro.build.version.release", "ro.build.version.sdk", "ro.product.cpu.abi",
                  "ro.kernel.qemu", "ro.boot.qemu")}
        props["root"] = self.root
        props["size"] = self.size
        props["refresh_hz"] = self._refresh_rate()
        return props

    def _refresh_rate(self) -> float:
        m = re.search(r"refreshRate[= ]+([\d.]+)", self.sh("dumpsys display | grep -m1 -o 'refreshRate[= ][0-9.]*'"))
        return float(m.group(1)) if m else 60.0

    def _find_input_devices(self) -> None:
        out = self.sh("getevent -pl")
        blocks = re.split(r"\nadd device \d+: ", "\n" + out)
        for b in blocks:
            if not b.strip():
                continue
            path = b.split("\n", 1)[0].strip()
            name = (re.search(r'name:\s*"([^"]*)"', b) or re.search(r"()", "")).group(1)
            if "ABS_MT_POSITION_X" in b and (self.touch is None or name.endswith("_multi_touch_1")
                                             or name.endswith("touch_0")):
                mx = re.search(r"ABS_MT_POSITION_X\s*:.*max (\d+)", b)
                my = re.search(r"ABS_MT_POSITION_Y\s*:.*max (\d+)", b)
                if self.touch is None or not self._touch_primary:
                    self.touch = (path, int(mx.group(1)), int(my.group(1)))
                    self._touch_primary = name.endswith("_multi_touch_1") or name.endswith("touch_0")
            if "KEY_Q " in b and "KEY_A " in b and self.keyboard is None:
                self.keyboard = path

    # ---------- clocks / input ----------
    def mono_now(self) -> float:
        out = self.sh("cat /proc/uptime")
        return float(out.split()[0])

    def _marker_ts(self, tag: str) -> float:
        out = self.sh(f"logcat -d -v monotonic -s BENCHT:I | grep ' {tag}$' | tail -1")
        m = re.match(r"\s*([\d.]+)", out)
        if not m:
            raise RuntimeError(f"marker {tag} not found")
        return float(m.group(1))

    @staticmethod
    def _events(evts) -> str:
        import struct
        raw = b"".join(struct.pack("<qqHHi", 0, 0, t, c, v & 0xFFFFFFFF if v < 0 else v) if v >= 0
                       else struct.pack("<qqHHI", 0, 0, t, c, v & 0xFFFFFFFF) for t, c, v in evts)
        return "".join(f"\\x{b:02x}" for b in raw)

    def _write_events(self, dev: str, evts, marker: str | None = None) -> None:
        pre = f"log -t BENCHT {marker}; " if marker else ""
        self.sh(f"{pre}printf '{self._events(evts)}' > {dev}")

    def tap(self, x: int, y: int, tag: str | None = None) -> float | None:
        """Tap by writing raw evdev events; a monotonic marker is logged right before the UP write."""
        if not self.touch:
            self.sh(f"input tap {x} {y}")
            return None
        dev, mx, my = self.touch
        ax = int(x * (mx + 1) / self.size[0])
        ay = int(y * (my + 1) / self.size[1])
        self._write_events(dev, [(3, 47, 0), (3, 57, 7), (3, 55, 0), (3, 53, ax), (3, 54, ay), (3, 58, 50), (3, 48, 5), (0, 0, 0)])
        time.sleep(0.05)
        self._write_events(dev, [(3, 47, 0), (3, 57, -1), (0, 0, 0)], tag)
        return self._marker_ts(tag) if tag else None

    LINUX_KEYS = {c: k for c, k in zip("qwertyuiopasdfghjklzxcvbnm",
                                        [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 30, 31, 32, 33, 34, 35, 36, 37, 38,
                                         44, 45, 46, 47, 48, 49, 50])}

    def key(self, ch: str, tag: str) -> float:
        code = self.LINUX_KEYS[ch]
        if not self.keyboard:
            andro = 29 + ord(ch) - ord("a")
            self.sh(f"log -t BENCHT {tag}; input keyevent {andro}")
        else:
            self._write_events(self.keyboard, [(1, code, 1), (0, 0, 0), (1, code, 0), (0, 0, 0)], tag)
        return self._marker_ts(tag)

    def swipe(self, x1, y1, x2, y2, ms):
        self.sh(f"input swipe {x1} {y1} {x2} {y2} {ms}")

    # ---------- app control ----------
    def activity(self, pkg: str) -> str:
        out = self.sh(f"cmd package resolve-activity --brief -c android.intent.category.LAUNCHER {pkg}").strip().splitlines()
        return out[-1].strip()

    def install(self, apk: str) -> None:
        self.adb("install", "-r", "-d", apk, timeout=600)

    def uninstall(self, pkg: str) -> None:
        subprocess.run(["adb", "-s", self.serial, "uninstall", pkg], capture_output=True, timeout=120)

    def pid(self, pkg: str) -> int | None:
        out = self.sh(f"pidof {pkg}").strip().split()
        return int(out[0]) if out else None

    def drop_caches(self) -> None:
        if self.root:
            self.sh("sync; echo 3 > /proc/sys/vm/drop_caches")


def lines_bench(dev: Device) -> list[tuple[float, str]]:
    out = dev.sh("logcat -d -v monotonic")
    res = []
    for line in out.splitlines():
        if ("BENCH" not in line and "PamPHP" not in line) or "BENCHT" in line:
            continue
        m = re.match(r"\s*([\d.]+)\s+\d+\s+\d+\s+\w\s+(\S+?)\s*:\s?(.*)$", line)
        if not m:
            continue
        tag, msg = m.group(2), m.group(3)
        if tag in ("BENCH", "PamPHP"):
            res.append((float(m.group(1)), msg.strip()))
        elif "BENCH " in msg:
            res.append((float(m.group(1)), msg.split("BENCH ", 1)[1].strip()))
    return res


def kv(msg: str) -> dict:
    return dict(p.split("=", 1) for p in msg.split()[1:] if "=" in p)


def wait_log(dev: Device, pred, timeout: float = 30) -> tuple[float, str] | None:
    end = time.time() + timeout
    while time.time() < end:
        for ts, msg in lines_bench(dev):
            if pred(msg):
                return ts, msg
        time.sleep(0.25)
    return None


# PAM screens of the list scenarios: "template" (p-for, the default routes)
# or "builder" (PHP builder API, `?api=builder`).
PAM_API = "template"
LIST_SCENARIOS = ("list", "grid", "like", "filter")


class App:
    def __init__(self, dev: Device, name: str):
        self.dev = dev
        self.name = name
        self.pkg = PKGS[name]
        self.act = dev.activity(self.pkg)

    def launch(self, uri: str, cold: bool = True, ready: str | None = None, timeout: float = 40):
        d = self.dev
        if cold:
            d.sh(f"am force-stop {self.pkg}")
            time.sleep(0.5)
        if self.name == "pam" and PAM_API != "template":
            host = uri.split("://", 1)[-1].split("?", 1)[0]
            if host in LIST_SCENARIOS:
                uri += ("&" if "?" in uri else "?") + f"api={PAM_API}"
        d.sh("logcat -c")
        d.sh("log -t BENCHT start")
        t0 = d._marker_ts("start")
        out = d.sh(f"am start -W -n {self.act} -a android.intent.action.VIEW -d '{uri}'", timeout=60)
        ttid = re.search(r"TotalTime: (\d+)", out)
        r = None
        settled = None
        if ready:
            r = wait_log(d, lambda m: m.startswith("ready") and f"scenario={ready}" in m, timeout)
            if r:
                # The app's ready log can precede the pixels (async native mount):
                # count until the last frame of the burst that follows it.
                time.sleep(2.5)
                settled = burst_latency_ms(self.framestats(), r[0], gap_ms=1500)
        return {
            "ttid_ms": int(ttid.group(1)) if ttid else None,
            "ready_log_ms": round((r[0] - t0) * 1000, 1) if r else None,
            "ready_ms": round((r[0] - t0) * 1000 + (settled or 0), 1) if r else None,
            "ready_msg": r[1] if r else None,
        }

    def proc_cpu(self) -> dict:
        pid = self.dev.pid(self.pkg)
        if not pid:
            return {"ticks": 0, "ctxt": 0, "threads": 0}
        stat = self.dev.sh(f"cat /proc/{pid}/stat").split(")")[-1].split()
        ticks = int(stat[11]) + int(stat[12])
        out = self.dev.sh(f"cd /proc/{pid}/task && for t in *; do echo $t $(grep -hE '^(voluntary|nonvoluntary)_ctxt_switches' $t/status 2>/dev/null | awk '{{s+=$2}} END {{print s+0}}'); done")
        per_thread = {}
        for line in out.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                per_thread[int(parts[0])] = int(parts[1])
        return {"pid": pid, "ticks": ticks, "ctxt": sum(per_thread.values()), "threads": len(per_thread),
                "per_thread": per_thread}

    def mem(self) -> dict:
        out = self.dev.sh(f"dumpsys meminfo {self.pkg}")
        res = {}
        for key, rx in (("pss_kb", r"TOTAL PSS:\s+(\d+)"), ("rss_kb", r"TOTAL RSS:\s+(\d+)"),
                        ("java_kb", r"Java Heap:\s+(\d+)"), ("native_kb", r"Native Heap:\s+(\d+)"),
                        ("graphics_kb", r"Graphics:\s+(\d+)"), ("code_kb", r"Code:\s+(\d+)")):
            m = re.search(rx, out)
            res[key] = int(m.group(1)) if m else None
        if res["pss_kb"] is None:
            m = re.search(r"TOTAL\s+(\d+)", out)
            res["pss_kb"] = int(m.group(1)) if m else None
        return res

    def gfx_reset(self):
        self.dev.sh(f"dumpsys gfxinfo {self.pkg} reset")

    def gfx(self) -> dict:
        out = self.dev.sh(f"dumpsys gfxinfo {self.pkg}")
        res = {}
        for key, rx in (("frames", r"Total frames rendered: (\d+)"), ("janky", r"Janky frames: (\d+)"),
                        ("janky_legacy", r"Janky frames \(legacy\): (\d+)"),
                        ("p50_ms", r"50th percentile: (\d+)ms"), ("p90_ms", r"90th percentile: (\d+)ms"),
                        ("p95_ms", r"95th percentile: (\d+)ms"), ("p99_ms", r"99th percentile: (\d+)ms"),
                        ("missed_vsync", r"Number Missed Vsync: (\d+)"),
                        ("slow_ui", r"Number Slow UI thread: (\d+)")):
            m = re.search(rx, out)
            res[key] = int(m.group(1)) if m else None
        if res.get("frames"):
            res["janky_pct"] = round(100 * (res["janky"] or 0) / res["frames"], 2)
        return res

    def framestats(self) -> list[dict]:
        out = self.dev.sh(f"dumpsys gfxinfo {self.pkg} framestats")
        rows = []
        if "---PROFILEDATA---" not in out:
            return rows
        for block in out.split("---PROFILEDATA---")[1::2]:
            lines = [l for l in block.strip().splitlines() if l.strip()]
            if not lines:
                continue
            hdr = lines[0].strip().rstrip(",").split(",")
            for l in lines[1:]:
                vals = l.strip().rstrip(",").split(",")
                if len(vals) != len(hdr):
                    continue
                try:
                    row = dict(zip(hdr, map(int, vals)))
                except ValueError:
                    continue
                if row.get("Flags", 0) == 0:
                    rows.append(row)
        return rows

    def find(self, label: str) -> tuple[int, int] | None:
        for _ in range(3):
            self.dev.sh("uiautomator dump /sdcard/ui.xml >/dev/null 2>&1", timeout=60)
            xml = self.dev.sh("cat /sdcard/ui.xml")
            try:
                root = ET.fromstring(xml[xml.find("<"):])
            except ET.ParseError:
                time.sleep(1)
                continue
            for n in root.iter("node"):
                if n.get("content-desc") == label or n.get("text") == label or n.get("resource-id", "").endswith(label):
                    m = re.findall(r"\d+", n.get("bounds", ""))
                    if len(m) == 4:
                        x1, y1, x2, y2 = map(int, m)
                        return (x1 + x2) // 2, (y1 + y2) // 2
            time.sleep(1)
        return None

    def uid(self) -> str | None:
        m = re.search(r"(?:userId|appId)=(\d+)", self.dev.sh(f"dumpsys package {self.pkg} | grep -m1 -E 'userId=|appId='"))
        if not m:
            return None
        n = int(m.group(1))
        return f"u0a{n - 10000}"


def ctxt_delta(c0: dict, c1: dict) -> int:
    """Context switches of the threads alive at the end (new threads count fully);
    a thread that exited mid-window cannot make the total negative."""
    before = c0.get("per_thread", {})
    return sum(max(0, n - before.get(tid, 0)) for tid, n in c1.get("per_thread", {}).items())


def burst_latency_ms(frames: list[dict], t0: float, gap_ms: float = 300) -> float | None:
    """Last frame of the burst that follows t0 (monotonic seconds)."""
    t0n = int(t0 * 1e9)
    done = sorted(f["FrameCompleted"] for f in frames if f.get("FrameCompleted", 0) > t0n)
    if not done:
        return None
    last = done[0]
    for v in done[1:]:
        if v - last > gap_ms * 1e6:
            break
        last = v
    return round((last - t0n) / 1e6, 1)


def server_reset():
    urllib.request.urlopen(urllib.request.Request(SERVER + "/__reset", method="POST"), timeout=5, context=_CTX).read()


def server_stats() -> dict:
    return json.loads(urllib.request.urlopen(SERVER + "/__stats", timeout=5, context=_CTX).read())


def pct(values, p):
    if not values:
        return None
    v = sorted(values)
    k = min(len(v) - 1, max(0, int(round(p / 100 * (len(v) - 1)))))
    return v[k]


# ---------------- scenarios ----------------

def sc_cold_start(app: App, quick: bool) -> dict:
    ttid, ready = [], []
    for _ in range(3 if quick else 10):
        app.dev.drop_caches()
        time.sleep(1)
        r = app.launch("bench://home", ready="home")
        if r["ttid_ms"] is not None:
            ttid.append(r["ttid_ms"])
        if r["ready_ms"] is not None:
            ready.append(r["ready_ms"])
        time.sleep(1.5)
    return {"ttid_ms_median": statistics.median(ttid) if ttid else None, "ttid_ms_p90": pct(ttid, 90),
            "ttfd_ms_median": statistics.median(ready) if ready else None, "samples": len(ttid)}


def _flings(app: App, n: int, down: bool = True):
    w, h = app.dev.size
    x = w // 2
    for _ in range(n):
        if down:
            app.dev.swipe(x, int(h * 0.8), x, int(h * 0.25), 120)
        else:
            app.dev.swipe(x, int(h * 0.25), x, int(h * 0.8), 120)
        time.sleep(0.9)


def _scroll_run(app: App, scenario: str, down: int, up: int) -> dict:
    r = app.launch(f"bench://{scenario}", ready=scenario)
    time.sleep(3)
    app.gfx_reset()
    c0, t0 = app.proc_cpu(), time.time()
    _flings(app, down, True)
    _flings(app, up, False)
    time.sleep(1)
    c1, t1 = app.proc_cpu(), time.time()
    g = app.gfx()
    m = app.mem()
    cpu_ms = (c1["ticks"] - c0["ticks"]) * 1000 / HZ
    return {**g, "cpu_ms": cpu_ms, "cpu_pct": round(100 * cpu_ms / 1000 / (t1 - t0), 1),
            "ctxt": ctxt_delta(c0, c1), **m, "ready_ms": r["ready_ms"]}


def sc_list(app: App, quick: bool) -> dict:
    return _scroll_run(app, "list", 20, 5)


def sc_grid(app: App, quick: bool) -> dict:
    server_reset()
    res = _scroll_run(app, "grid", 14, 4)
    res["net_bytes"] = server_stats()["bytes"]
    return res


def sc_like(app: App, quick: bool) -> dict:
    app.launch("bench://like", ready="like")
    time.sleep(2)
    targets = {}
    for i in range(1, 6):
        p = app.find(f"like-{i}")
        if p:
            targets[i] = p
    if not targets:
        return {"error": "like-N targets not found in accessibility tree"}
    lat, cpu, rer = [], [], []
    seq = list(targets.items()) * 2
    for n, (i, (x, y)) in enumerate(seq):
        # No gfxinfo reset per tap: frames are selected by the tap's
        # monotonic marker, and a reset while a frame is in flight drops the
        # following frames' stats on some apps (PAM lost every tap but the first).
        app.dev.sh("logcat -c")
        c0 = app.proc_cpu()
        t0 = app.dev.tap(x, y, f"like{n}")
        time.sleep(1.5)
        c1 = app.proc_cpu()
        lt = burst_latency_ms(app.framestats(), t0) if t0 else None
        if lt is not None:
            lat.append(lt)
        cpu.append((c1["ticks"] - c0["ticks"]) * 1000 / HZ)
        for _, msg in lines_bench(app.dev):
            if msg.startswith("rerender"):
                rer.append(kv(msg))
    nodes = [float(r["count"]) for r in rer if "count" in r]
    byts = [float(r["bytes"]) for r in rer if "bytes" in r]
    return {"touch_to_pixel_ms_median": statistics.median(lat) if lat else None,
            "touch_to_pixel_ms_p90": pct(lat, 90), "cpu_ms_per_tap": statistics.median(cpu),
            "rerender_nodes_median": statistics.median(nodes) if nodes else None,
            "rerender_bytes_median": statistics.median(byts) if byts else None, "taps": len(seq)}


def sc_filter(app: App, quick: bool) -> dict:
    app.launch("bench://filter", ready="filter")
    time.sleep(2)
    p = app.find("filter-input")
    if not p:
        return {"error": "filter-input not found"}
    app.dev.tap(*p)
    time.sleep(2.5)
    if app.dev.keyboard:  # leave touch mode with a no-op key so the first measured key is a plain keystroke
        app.dev._write_events(app.dev.keyboard, [(1, 42, 1), (0, 0, 0), (1, 42, 0), (0, 0, 0)])
        time.sleep(1.5)
    lat, cpu = [], []
    app.gfx_reset()
    for n, ch in enumerate("limaz"):
        c0 = app.proc_cpu()
        t0 = app.dev.key(ch, f"key{n}")
        time.sleep(1.5)
        c1 = app.proc_cpu()
        lt = burst_latency_ms(app.framestats(), t0)
        if lt is not None:
            lat.append(lt)
        cpu.append((c1["ticks"] - c0["ticks"]) * 1000 / HZ)
    res = [kv(m) for _, m in lines_bench(app.dev) if m.startswith("filter")]
    return {"key_to_pixel_ms_median": statistics.median(lat) if lat else None, "key_to_pixel_ms_p90": pct(lat, 90),
            "key_to_pixel_ms_all": lat, "cpu_ms_per_key": statistics.median(cpu), "app_logs": res[-3:]}


def _window(app: App, seconds: float, background: bool = False, battery: bool = False) -> dict:
    d = app.dev
    if battery:
        d.sh("dumpsys batterystats --reset; dumpsys battery unplug")
    app.gfx_reset()
    c0, t0 = app.proc_cpu(), time.time()
    time.sleep(seconds)
    c1, t1 = app.proc_cpu(), time.time()
    g = app.gfx()
    m = app.mem()
    res = {}
    if battery:
        uid = app.uid()
        out = d.sh(f"dumpsys batterystats --charged {app.pkg}")
        mah = None
        if uid:
            mm = re.search(rf"UID {uid}: ([\d.]+)", out) or re.search(rf"Uid {uid}: ([\d.]+)", out)
            # batterystats omits UIDs whose estimated drain rounds to zero.
            mah = float(mm.group(1)) if mm else (0.0 if "Estimated power use" in out else None)
        wl = re.findall(r"Wake lock .*?: (\d+)ms", out)
        res["mah"] = mah
        d.sh("dumpsys battery reset")
    dt = t1 - t0
    cpu_ms = (c1["ticks"] - c0["ticks"]) * 1000 / HZ
    if c1.get("pid") != c0.get("pid"):
        res["process_restarted"] = True
    return {**res, "seconds": round(dt, 1), "cpu_ms": cpu_ms, "cpu_pct": round(100 * cpu_ms / 1000 / dt, 3),
            "wakeups_per_min": round(ctxt_delta(c0, c1) * 60 / dt, 1), "threads": c1["threads"],
            "frames": g.get("frames"), **m}


def sc_idle60(app: App, quick: bool) -> dict:
    app.launch("bench://home", ready="home")
    time.sleep(5)
    return _window(app, 20 if quick else 60)


def sc_idle600(app: App, quick: bool) -> dict:
    app.launch("bench://home", ready="home")
    time.sleep(5)
    return _window(app, 60 if quick else 600, battery=True)


def sc_bg600(app: App, quick: bool) -> dict:
    app.launch("bench://home", ready="home")
    time.sleep(5)
    app.dev.sh("input keyevent 3")
    time.sleep(5)
    res = _window(app, 60 if quick else 600, battery=True)
    return res


def sc_anim(app: App, quick: bool) -> dict:
    app.launch("bench://anim", ready="anim")
    time.sleep(3)
    return _window(app, 20 if quick else 60) | {"gfx": app.gfx()}


def sc_video(app: App, quick: bool) -> dict:
    server_reset()
    app.launch("bench://video", ready="video")
    time.sleep(4)
    d = app.dev
    codec_pids = [l.split()[1] for l in d.sh("ps -A -o USER,PID,NAME").splitlines()
                  if re.search(r"codec|media\.swcodec|c2", l)]

    def codec_ticks():
        tot = 0
        for p in codec_pids:
            st = d.sh(f"cat /proc/{p}/stat 2>/dev/null").split(")")[-1].split()
            if len(st) > 13:
                tot += int(st[11]) + int(st[12])
        return tot

    k0, t0 = codec_ticks(), time.time()
    res = _window(app, 20 if quick else 60)
    k1 = codec_ticks()
    res["codec_cpu_pct"] = round(100 * (k1 - k0) / HZ / (time.time() - t0), 1)
    pid = app.dev.pid(app.pkg)
    codecs = d.sh("dumpsys media.resource_manager")
    res["decoders"] = len(re.findall(rf"pid\(?[:= ]?\s*{pid}\)?.*?(?:codec|Codec)", codecs)) if pid else None
    res["decoder_threads"] = int(d.sh(f"ls /proc/{pid}/task 2>/dev/null | while read t; do cat /proc/{pid}/task/$t/comm; done | grep -ci codec").strip() or 0) if pid else None
    res["net_bytes"] = server_stats()["bytes"]
    return res


def sc_nav(app: App, quick: bool) -> dict:
    r = app.launch("bench://nav", ready="nav")
    time.sleep(2)
    p = app.find("next")
    if not p:
        return {"error": "next button not found"}
    pss, push_ms = [app.mem()["pss_kb"]], []
    for cycle in range(2 if quick else 3):
        for k in range(1, 21):
            app.dev.sh("logcat -c")
            t0 = app.dev.tap(*p, tag=f"n{cycle}_{k}")
            r = wait_log(app.dev, lambda m: m.startswith("ready") and "scenario=nav" in m and f"k={k}" in m.split(), 10)
            if r and t0:
                push_ms.append(round((r[0] - t0) * 1000, 1))
            time.sleep(0.4)
        peak = app.mem()["pss_kb"]
        for _ in range(20):
            app.dev.sh("input keyevent 4")
            time.sleep(0.5)
        time.sleep(2)
        pss.append(app.mem()["pss_kb"])
    return {"pss_kb_start": pss[0], "pss_kb_after_cycles": pss[1:], "pss_kb_peak_last": peak,
            "pss_growth_kb_cycle1_to_last": pss[-1] - pss[1], "push_to_ready_ms_median": statistics.median(push_ms) if push_ms else None,
            "push_to_ready_ms_p90": pct(push_ms, 90), "pushes": len(push_ms)}


def sc_feed(app: App, quick: bool) -> dict:
    d = app.dev
    d.sh(f"pm clear {app.pkg}")
    server_reset()
    r1 = app.launch("bench://feed", ready="feed")
    time.sleep(5)
    s1 = server_stats()
    server_reset()
    r2 = app.launch("bench://feed", ready="feed")
    time.sleep(5)
    s2 = server_stats()
    return {"first_bytes": s1["bytes"], "first_requests": s1["requests"], "first_ready_ms": r1["ready_ms"],
            "reopen_bytes": s2["bytes"], "reopen_requests": s2["requests"], "reopen_304": s2["not_modified"],
            "reopen_ready_ms": r2["ready_ms"], "reopen_source": r2["ready_msg"]}


def sc_compute(app: App, quick: bool) -> dict:
    app.launch("bench://compute", ready="compute", timeout=60)
    done = wait_log(app.dev, lambda m: m.startswith("compute done"), 600)
    ops = {}
    for _, msg in lines_bench(app.dev):
        if msg.startswith("compute op="):
            k = kv(msg)
            ops[k["op"]] = {"ms": float(k["ms"]), "check": k.get("check")}
    return {"ops": ops, "complete": done is not None}


def sc_state(app: App, quick: bool) -> dict:
    app.launch("bench://state?n=0", ready="state")
    time.sleep(4)
    m0 = app.mem()
    r = app.launch("bench://state?n=100000", ready="state", timeout=120)
    time.sleep(4)
    m1 = app.mem()
    return {"pss_kb_n0": m0["pss_kb"], "pss_kb_n100k": m1["pss_kb"],
            "delta_kb": (m1["pss_kb"] or 0) - (m0["pss_kb"] or 0), "build_ready_ms": r["ready_ms"],
            "native_kb_delta": (m1["native_kb"] or 0) - (m0["native_kb"] or 0),
            "java_kb_delta": (m1["java_kb"] or 0) - (m0["java_kb"] or 0)}


SCENARIOS = {
    "cold_start": sc_cold_start, "list": sc_list, "grid": sc_grid, "like": sc_like, "filter": sc_filter,
    "anim": sc_anim, "idle60": sc_idle60, "nav": sc_nav, "video": sc_video, "feed": sc_feed,
    "compute": sc_compute, "state": sc_state, "idle600": sc_idle600, "bg600": sc_bg600,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--apk", action="append", default=[], help="name=path")
    ap.add_argument("--only", default="")
    ap.add_argument("--apps", default="native,pam,rn")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--no-install", action="store_true")
    ap.add_argument("--pam-api", choices=["template", "builder"], default="template",
                    help="PAM list screens: template p-for (default) or the PHP builder API")
    a = ap.parse_args()
    globals()["PAM_API"] = a.pam_api
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / "raw.json"
    raw = json.loads(raw_path.read_text()) if raw_path.exists() else {"apps": {}}
    dev = Device(a.serial)
    raw["device"] = dev.setup()
    raw["quick"] = a.quick
    raw["pam_api"] = a.pam_api
    apks = dict(x.split("=", 1) for x in a.apk)
    only = [s for s in a.only.split(",") if s] or list(SCENARIOS)
    for name in a.apps.split(","):
        entry = raw["apps"].setdefault(name, {})
        if name in apks:
            entry["apk_bytes"] = Path(apks[name]).stat().st_size
            entry["apk"] = apks[name]
            if not a.no_install:
                dev.uninstall(PKGS[name])
                dev.install(apks[name])
        # Same ART state for every app: full AOT, as after background dexopt
        # with a complete profile (an adb install would otherwise start
        # interpreted/JIT and penalize whichever app has more Kotlin/Java).
        dev.sh(f"cmd package compile -m speed -f {PKGS[name]}", timeout=600)
        entry["art_compiler_filter"] = "speed"
        app = App(dev, name)
        # One unmeasured launch of each screen first, for every app: what a
        # fresh install fills once (PAM's compiled-template and opcode
        # caches, RN's bundle cache, Coil/expo-image disk caches are reset by
        # the scenarios that measure them) is not counted as a cold start.
        for warm in ("home", "list", "grid", "like", "filter"):
            app.launch(f"bench://{warm}", ready=warm, timeout=20)
        dev.sh(f"am force-stop {PKGS[name]}")
        entry["warmed"] = True
        for sc in only:
            print(f"[{name}] {sc} ...", flush=True)
            t = time.time()
            try:
                entry[sc] = SCENARIOS[sc](app, a.quick)
            except Exception as e:  # keep going, record the failure
                entry[sc] = {"error": f"{type(e).__name__}: {e}"}
            print(f"[{name}] {sc} {round(time.time() - t)}s -> {json.dumps(entry[sc])[:400]}", flush=True)
            raw_path.write_text(json.dumps(raw, indent=2))
        dev.sh(f"am force-stop {PKGS[name]}")
    raw_path.write_text(json.dumps(raw, indent=2))
    subprocess.run([sys.executable, str(Path(__file__).with_name("scoreboard.py")), str(raw_path),
                    str(out / "scoreboard.md")], check=False)


if __name__ == "__main__":
    main()
