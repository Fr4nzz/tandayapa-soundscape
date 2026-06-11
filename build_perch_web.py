#!/usr/bin/env python3
"""Export Perch frog/insect scores to web JSON for the BirdNET-vs-Perch viewer.

Reads outputs/perch_audiomoth_detections/window_scores.csv (from
run_perch_detectors.py) and writes outputs/web/perch_files.json — one entry per
AudioMoth recording with aggregate frog/insect scores plus the top-scoring 5s
windows (for the per-file timeline / clip playback). Safe to re-run as inference
grows.

Per-file granularity keeps the comparison reviewable (~2.5k files) and surfaces
how often Perch flags frog/insect activity vs BirdNET's species-level detections.

Audio URLs mirror BirdNET web data: "/<device>/<file>.WAV" served from repo root.

Usage: python build_perch_web.py [--top-windows 15] [--hit 0.5]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCORES = ROOT / "outputs" / "perch_audiomoth_detections" / "window_scores.csv"
OUT = ROOT / "outputs" / "web" / "perch_files.json"

TS = re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})")


def parse_day_time(fname: str):
    m = TS.search(fname)
    if not m:
        return None, None
    y, mo, d, hh, mm, ss = m.groups()
    return f"{y}-{mo}-{d}", f"{hh}:{mm}:{ss}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-windows", type=int, default=15,
                    help="how many top windows (by max prob) to embed per file")
    ap.add_argument("--hit", type=float, default=0.5, help="hit threshold")
    args = ap.parse_args()

    if not SCORES.exists():
        raise SystemExit(f"no scores yet at {SCORES}")

    # Accumulate per-file stats in one streaming pass.
    agg: dict[str, dict] = {}
    windows: dict[str, list] = defaultdict(list)
    n_total = 0
    with SCORES.open(newline="") as fh:
        for row in csv.DictReader(fh):
            n_total += 1
            try:
                frog = float(row["frog_prob"]); insect = float(row["insect_prob"])
                start = float(row["start_s"]); end = float(row["end_s"])
            except (KeyError, ValueError):
                continue
            f = row["file"]
            a = agg.get(f)
            if a is None:
                day, tod = parse_day_time(Path(f).name)
                a = agg[f] = {
                    "audio": "/" + f, "device": row.get("device", f.split("/", 1)[0]),
                    "day": day, "tod": tod, "n": 0,
                    "frog_max": 0.0, "insect_max": 0.0,
                    "frog_sum": 0.0, "insect_sum": 0.0,
                    "frog_hits": 0, "insect_hits": 0,
                }
            a["n"] += 1
            a["frog_max"] = max(a["frog_max"], frog)
            a["insect_max"] = max(a["insect_max"], insect)
            a["frog_sum"] += frog; a["insect_sum"] += insect
            if frog >= args.hit: a["frog_hits"] += 1
            if insect >= args.hit: a["insect_hits"] += 1
            windows[f].append((round(start, 1), round(end, 1), round(frog, 3), round(insect, 3)))

    files = []
    for f, a in agg.items():
        n = a["n"] or 1
        # keep the top-N windows by the stronger of the two scores
        w = sorted(windows[f], key=lambda x: max(x[2], x[3]), reverse=True)[:args.top_windows]
        w.sort(key=lambda x: x[0])  # chronological for the timeline
        files.append({
            "audio": a["audio"], "device": a["device"], "day": a["day"], "tod": a["tod"],
            "n": a["n"],
            "frog_max": round(a["frog_max"], 3), "insect_max": round(a["insect_max"], 3),
            "frog_mean": round(a["frog_sum"] / n, 3), "insect_mean": round(a["insect_sum"] / n, 3),
            "frog_hits": a["frog_hits"], "insect_hits": a["insect_hits"],
            "windows": [{"s": s, "e": e, "f": fr, "i": ins} for (s, e, fr, ins) in w],
        })
    files.sort(key=lambda x: x["frog_max"], reverse=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    meta = {"n_files": len(files), "n_windows": n_total, "hit": args.hit}
    OUT.write_text(json.dumps({"meta": meta, "files": files}))
    print(f"wrote {OUT}  ({len(files)} files / {n_total} windows)")


if __name__ == "__main__":
    main()
