#!/usr/bin/env python3
"""Compose the published framework scoreboard from several same-device runs.

  python3 suite/compose.py --native-rn RUN [--native-rn RUN ...] \
      --pam-base RUN --pam-cand RUN [--pam-base-extra RUN] [--pam-cand-extra RUN] \
      --label "PAM 1.44 cand." --out scoreboard.md

Every RUN is a raw.json written by run.py on the same device. Later runs
override earlier ones per app and scenario (targeted re-measurements).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import scoreboard


def load(paths: list[str]) -> dict:
    merged: dict = {"apps": {}}
    for path in paths:
        raw = json.loads(Path(path).read_text())
        merged["device"] = raw.get("device", merged.get("device"))
        for app, scenarios in raw.get("apps", {}).items():
            merged["apps"].setdefault(app, {}).update(
                {k: v for k, v in scenarios.items() if not (isinstance(v, dict) and "error" in v)}
            )
    return merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--native-rn", action="append", default=[])
    ap.add_argument("--pam-base", action="append", default=[])
    ap.add_argument("--pam-cand", action="append", default=[])
    ap.add_argument("--label", default="PAM cand.")
    ap.add_argument("--base-label", default="PAM base")
    ap.add_argument("--out")
    a = ap.parse_args()
    others = load(a.native_rn)
    base = load(a.pam_base)
    cand = load(a.pam_cand)
    raw = {"device": others.get("device"), "apps": {
        "native": others["apps"].get("native", {}),
        "rn": others["apps"].get("rn", {}),
        "pam": base["apps"].get("pam", {}),
    }}
    md = scoreboard.render(raw, {"apps": {"pam": cand["apps"].get("pam", {})}}, a.label)
    md = md.replace("| PAM 1.41.0 |", f"| {a.base_label} |")
    if a.out:
        Path(a.out).write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
