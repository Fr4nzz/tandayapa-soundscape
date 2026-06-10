#!/usr/bin/env python3
"""Prepare the web-app detection data for the public GitHub Pages build.

Rewrites each detection's `audio` field from the old local WAV path
(`/F1501_A05/20260602_214000.WAV`) to the public Cloudflare R2 Opus URL
(`https://pub-...r2.dev/2026-06-02/forest_15m_p1_A05/20260602_214000.opus`),
using `data/metadata/deployments.csv` to map the old device folder to the new
`<date>/<folder>` location. Output goes to `webapp/public/data/` so Vite bundles
it into the build.

Run: python3 analysis/build_webapp_data.py
"""
from __future__ import annotations

import csv
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "outputs" / "web"
OUT = ROOT / "webapp" / "public" / "data"
META = ROOT / "data" / "metadata" / "deployments.csv"
R2 = "https://pub-72f1b338d806437e89811bcd5e8344b3.r2.dev"


def main():
    # old_dir -> "<date>/<folder>"
    loc = {}
    for r in csv.DictReader(open(META, encoding="utf-8")):
        parts = r["new_rel_path"].strip("/").split("/")   # data raw audio <date> <folder>
        loc[r["old_dir"]] = "/".join(parts[-2:])
    OUT.mkdir(parents=True, exist_ok=True)

    def to_r2(audio: str):
        m = re.match(r"^/([^/]+)/(.+)\.WAV$", audio, re.IGNORECASE)
        if not m:
            return None
        old_dir, name = m.group(1), m.group(2)
        if old_dir not in loc:
            return None
        return f"{R2}/{loc[old_dir]}/{name}.opus"

    total, rew, miss = 0, 0, set()
    for f in sorted(glob.glob(str(WEB / "*.json"))):
        data = json.load(open(f, encoding="utf-8"))
        if Path(f).name == "index.json":
            (OUT / "index.json").write_text(json.dumps(data), encoding="utf-8")
            continue
        for d in data:
            total += 1
            u = to_r2(d.get("audio", ""))
            if u:
                d["audio"] = u; rew += 1
            else:
                miss.add(d.get("audio", "")[:40])
        (OUT / Path(f).name).write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"detections: {total}; rewritten to R2: {rew}; unmapped audio prefixes: {len(miss)}")
    for m in list(miss)[:5]:
        print("  unmapped:", m)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
