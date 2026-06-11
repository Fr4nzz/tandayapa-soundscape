#!/usr/bin/env python3
"""Export Perch frog/insect detections in the webapp's Detection[] format.

Reads outputs/perch_audiomoth_detections/window_scores.csv and merges contiguous
hit windows (prob >= --hit) into detection segments, so the main React webapp can
show Perch frog/insect detections via a BirdNET/Perch source toggle. Birds are
not produced (Perch has no bird head).

Metadata (habitat/recorder/moth/spacing) is reused from the BirdNET web JSON
(outputs/web/day*.json) keyed by audio file, with a filename-based fallback.

Output: outputs/web/perch.json  (a single Detection[] array, same shape as dayN.json)

Usage: python build_perch_detections.py [--hit 0.5] [--max-gap 1]
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
WEB = ROOT / "outputs" / "web"
OUT = WEB / "perch.json"

TS = re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})")


def file_start(fname: str):
    m = TS.search(fname)
    if not m:
        return None
    y, mo, d, hh, mm, ss = (int(x) for x in m.groups())
    return y, mo, d, hh, mm, ss


def fmt_time(y, mo, d, hh, mm, ss, offset_s):
    total = ((hh * 60 + mm) * 60 + ss) + int(offset_s)
    day_carry, rem = divmod(total, 86400)
    hh2 = rem // 3600; mm2 = (rem % 3600) // 60; ss2 = rem % 60
    # ignore day_carry rollover for label simplicity (clips are short)
    return f"{y:04d}-{mo:02d}-{d:02d} {hh2:02d}:{mm2:02d}:{ss2:02d}", hh2


def load_bird_meta():
    """audio -> {habitat, recorder, moth, spacing} from BirdNET web JSON."""
    meta = {}
    for p in sorted(WEB.glob("day*.json")):
        try:
            for det in json.load(open(p)):
                a = det.get("audio")
                if a and a not in meta:
                    meta[a] = {k: det.get(k) for k in ("habitat", "recorder", "moth", "spacing")}
        except Exception:
            continue
    return meta


def fallback_meta(device: str):
    hab = "forest" if device[:1].upper() == "F" else "pasture" if device[:1].upper() == "P" else "?"
    rec = device[:2].upper() if len(device) >= 2 else device  # e.g. F1501_A05 -> "F1"
    moth = device.split("_")[-1] if "_" in device else ""
    return {"habitat": hab, "recorder": rec, "moth": moth, "spacing": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hit", type=float, default=0.5)
    ap.add_argument("--max-gap", type=int, default=1, help="merge across up to N missed windows")
    args = ap.parse_args()
    if not SCORES.exists():
        raise SystemExit(f"no scores at {SCORES}")

    bird_meta = load_bird_meta()

    # gather hit windows per (file, group)
    wins = defaultdict(list)  # (file, group) -> list[(start, end, prob)]
    with SCORES.open(newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                s = float(row["start_s"]); e = float(row["end_s"])
                fr = float(row["frog_prob"]); ins = float(row["insect_prob"])
            except (KeyError, ValueError):
                continue
            f = row["file"]
            if fr >= args.hit:
                wins[(f, "frog")].append((s, e, fr))
            if ins >= args.hit:
                wins[(f, "insect")].append((s, e, ins))

    dets = []
    win_s = 5.0
    for (f, group), ws in wins.items():
        ws.sort()
        device = f.split("/", 1)[0]
        meta = bird_meta.get("/" + f) or fallback_meta(device)
        fs = file_start(Path(f).name)
        # merge contiguous windows into segments
        segs = []
        cur = None
        for (s, e, p) in ws:
            if cur and s <= cur[1] + args.max_gap * win_s + 0.01:
                cur[1] = max(cur[1], e); cur[2] = max(cur[2], p)
            else:
                if cur: segs.append(cur)
                cur = [s, e, p]
        if cur: segs.append(cur)
        for (s, e, p) in segs:
            if fs:
                time, hour = fmt_time(*fs, s)
                day = f"{fs[0]:04d}-{fs[1]:02d}-{fs[2]:02d}"
            else:
                time, hour, day = "", 0, ""
            dets.append({
                "id": f"perch-{group}-{f}-{int(s)}",
                "day": day, "group": group, "audio": "/" + f,
                "start": round(s, 1), "end": round(e, 1),
                "species": f"Perch {group} (no species)",
                "common": f"Perch {group} detection",
                "conf": round(p, 3),
                "habitat": meta.get("habitat") or "?",
                "recorder": meta.get("recorder") or device[:2],
                "moth": meta.get("moth") or "",
                "time": time, "hour": hour,
                "daynight": "night" if (hour < 6 or hour >= 18) else "day",
                "spacing": meta.get("spacing") or 0,
            })

    dets.sort(key=lambda d: -d["conf"])
    OUT.write_text(json.dumps(dets))
    nf = sum(1 for d in dets if d["group"] == "frog")
    print(f"wrote {OUT}: {len(dets)} Perch detections ({nf} frog, {len(dets)-nf} insect)")


if __name__ == "__main__":
    main()
