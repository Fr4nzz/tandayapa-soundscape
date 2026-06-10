#!/usr/bin/env python3
"""One-off migration: build the deployment metadata and reorganize raw data.

Creates the single source of truth `data/metadata/deployments.csv` and moves the
raw inputs into a readable, GitHub-friendly layout:

    data/raw/audio/<YYYY-MM-DD>/<habitat>_<spacing>m_p<point>_<audiomoth>/*.WAV
    data/raw/audio/_unused/<original_dir>/        (failed / backup / duplicate recorders)
    data/raw/gps/ , data/raw/dataloggers/ , data/raw/models/

`deployments.csv` columns:
    deployment_id, date, deploy, habitat, spacing_m, point, audiomoth,
    old_dir, new_rel_path, n_wav, status, notes

Moves are within the same filesystem (fast, reversible via old_dir). Re-running is
safe: already-moved dirs are skipped.

Run: .venv-perch/bin/python analysis/00_build_metadata_and_reorganize.py
"""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO_OLD = ROOT / "data" / "audiomoths"
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"

# deploy -> (date, spacing)
DEPLOY = {
    "day1": ("2026-06-02", 15), "day2": ("2026-06-03", 30), "day3": ("2026-06-04", 60),
    "day4": ("2026-06-05", 15), "day5": ("2026-06-06", 30), "day6": ("2026-06-07", 60),
}
# the 29 analysed recorders: old_dir -> (deploy, habitat, point)
DEVICES = {
    "F1501_A05": ("day1", "forest", 1), "F1502_A06": ("day1", "forest", 2), "F1503_A08": ("day1", "forest", 3),
    "P1501_A04": ("day1", "pasture", 1), "P1502_A01": ("day1", "pasture", 2), "P1503_A02": ("day1", "pasture", 3),
    "F3001_A01": ("day2", "forest", 1), "F3002_A05": ("day2", "forest", 2), "F3003_A07": ("day2", "forest", 3),
    "P3001_A06": ("day2", "pasture", 1), "P3002_A04": ("day2", "pasture", 2),
    "F6002_A03": ("day3", "forest", 2), "F6003_A05": ("day3", "forest", 3), "P6002_A02": ("day3", "pasture", 2),
    "F1501_A07": ("day4", "forest", 1), "F1502_A01": ("day4", "forest", 2),
    "P1501_A02": ("day4", "pasture", 1), "P1502_A05": ("day4", "pasture", 2), "P1503_A03": ("day4", "pasture", 3),
    "F3001_A02": ("day5", "forest", 1), "F3002_A03": ("day5", "forest", 2), "F3003_A01": ("day5", "forest", 3),
    "P3001_A05": ("day5", "pasture", 1), "P3002_A04_6julio": ("day5", "pasture", 2), "P3003_A06": ("day5", "pasture", 3),
    "F6002_A05": ("day6", "forest", 2), "F6003_A06": ("day6", "forest", 3),
    "P6001_A02": ("day6", "pasture", 1), "P6003_A01": ("day6", "pasture", 3),
}
# recorders NOT used in analysis (failed / backup / duplicate) -> note
UNUSED = {
    "F1502_A04": "backup/duplicate forest 15 m p2 (not used in analysis)",
    "P3003_A03_didnt work": "recorder failed (no usable data)",
    "P6003_A07_7Jun": "backup/extra pasture recorder (not used in analysis)",
}


def audiomoth_of(old_dir: str) -> str:
    # device dirs look like  F1501_A05  or  P3002_A04_6julio
    parts = old_dir.split("_")
    for p in parts:
        if p.startswith("A") and p[1:].isdigit():
            return p
    return parts[1] if len(parts) > 1 else ""


def move_dir(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return "exists"
    shutil.move(str(src), str(dst))
    return "moved"


def main():
    META.mkdir(parents=True, exist_ok=True)
    rows = []

    # --- analysed recorders -> clean structure ---
    for old, (deploy, habitat, point) in DEVICES.items():
        date, spacing = DEPLOY[deploy]
        unit = audiomoth_of(old)
        dep_id = f"{date}_{habitat}_{spacing}m_p{point}"
        folder = f"{habitat}_{spacing}m_p{point}_{unit}"
        new_rel = f"data/raw/audio/{date}/{folder}"
        src = AUDIO_OLD / old
        n_wav = len(list(src.glob("*.WAV"))) if src.exists() else len(list((RAW / "audio" / date / folder).glob("*.WAV")))
        if src.exists():
            move_dir(src, RAW / "audio" / date / folder)
        rows.append(dict(deployment_id=dep_id, date=date, deploy=deploy, habitat=habitat,
                         spacing_m=spacing, point=point, audiomoth=unit, old_dir=old,
                         new_rel_path=new_rel, n_wav=n_wav, status="analysed", notes=""))

    # --- unused / failed recorders -> _unused/ ---
    for old, note in UNUSED.items():
        src = AUDIO_OLD / old
        safe = old.replace(" ", "_")
        new_rel = f"data/raw/audio/_unused/{safe}"
        n_wav = len(list(src.glob("*.WAV"))) if src.exists() else len(list((RAW / "audio" / "_unused" / safe).glob("*.WAV")))
        if src.exists():
            move_dir(src, RAW / "audio" / "_unused" / safe)
        rows.append(dict(deployment_id="", date="", deploy="", habitat="", spacing_m="",
                         point="", audiomoth=audiomoth_of(old), old_dir=old,
                         new_rel_path=new_rel, n_wav=n_wav, status="unused", notes=note))

    # --- other raw inputs ---
    (RAW / "gps").mkdir(parents=True, exist_ok=True)
    gps = ROOT / "data" / "tandayapa_gps_waypoints.csv"
    if gps.exists():
        shutil.copy(gps, RAW / "gps" / "tandayapa_gps_waypoints.csv")
    dl_src = ROOT / "data" / "dataloggers"
    if dl_src.exists() and not (RAW / "dataloggers").exists():
        shutil.copytree(dl_src, RAW / "dataloggers")
    # BirdNET / classifier models, if present alongside the audio
    for cand in [AUDIO_OLD / "models", ROOT / "data" / "models", AUDIO_OLD / "reference"]:
        if cand.exists():
            dst = RAW / "models" / cand.name
            if not dst.exists():
                shutil.copytree(cand, dst)

    # --- write metadata ---
    cols = ["deployment_id", "date", "deploy", "habitat", "spacing_m", "point",
            "audiomoth", "old_dir", "new_rel_path", "n_wav", "status", "notes"]
    out = META / "deployments.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    a = sum(r["status"] == "analysed" for r in rows); u = sum(r["status"] == "unused" for r in rows)
    print(f"wrote {out}: {a} analysed + {u} unused recorders, "
          f"{sum(int(r['n_wav']) for r in rows)} WAVs total")


if __name__ == "__main__":
    main()
