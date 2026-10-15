#!/usr/bin/env python3
"""Merge runs of the same device into one raw.json.

  python3 suite/merge.py out.json base/raw.json [override/raw.json ...]

Later files override earlier ones per app and scenario (e.g. a re-measured
idle/battery window), so a scoreboard can combine a full run with targeted
re-runs taken on the same device.
"""
import json
import sys
from pathlib import Path

out, *sources = sys.argv[1:]
merged: dict = {"apps": {}, "sources": []}
for source in sources:
    raw = json.loads(Path(source).read_text())
    merged["device"] = raw.get("device", merged.get("device"))
    merged["quick"] = merged.get("quick", False) or raw.get("quick", False)
    merged["sources"].append(source)
    for app, scenarios in raw.get("apps", {}).items():
        merged["apps"].setdefault(app, {}).update(
            {k: v for k, v in scenarios.items() if not (isinstance(v, dict) and "error" in v)}
        )
Path(out).write_text(json.dumps(merged, indent=2))
