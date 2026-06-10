#!/usr/bin/env python3
"""Acoustic indices (ACI, BI, ADI) per recorder AND per diel period.

Same indices as compute_acoustic_indices.py, but each recording is binned by its
time of day (from the AudioMoth filename timestamp YYYYMMDD_HHMMSS.WAV) into
dawn / day / dusk / night, then averaged within each (recorder, diel) cell. This
feeds the diel analysis the friends' report asks for ("what happens during dawn
and dusk?", "comparison between dawn, day, dusk, and night").

Tandayapa sits on the equator (~0° lat), so sunrise ≈ 06:10 and sunset ≈ 18:10
year-round. Bins:
  dawn  05:00–08:00   (dawn chorus)
  day   08:00–16:00
  dusk  16:00–19:00
  night 19:00–05:00

Output: outputs/analysis/diel_indices.csv
Run: .venv-perch/bin/python analysis/compute_diel_indices.py [--per-bin 8]
"""
from __future__ import annotations

import argparse
import csv
import re
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "data" / "audiomoths"
OUT = ROOT / "outputs" / "analysis" / "diel_indices.csv"

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
DAY_SPACING = {"day1": 15, "day2": 30, "day3": 60, "day4": 15, "day5": 30, "day6": 60}
DIEL_ORDER = ["dawn", "day", "dusk", "night"]
_TS = re.compile(r"(\d{8})_(\d{6})")


def diel_of(path: str):
    """Return diel period from the filename timestamp, or None if unparseable."""
    m = _TS.search(Path(path).name)
    if not m:
        return None
    h = int(m.group(2)[:2])
    if 5 <= h < 8:
        return "dawn"
    if 8 <= h < 16:
        return "day"
    if 16 <= h < 19:
        return "dusk"
    return "night"


def indices_for_file(path: str):
    try:
        from maad import sound, features
        s, fs = sound.load(path)
        Sxx, tn, fn, ext = sound.spectrogram(s, fs, mode="amplitude")
        _, _, aci = features.acoustic_complexity_index(Sxx)
        bi = features.bioacoustics_index(Sxx, fn, flim=(2000, 8000))
        adi = features.acoustic_diversity_index(Sxx, fn, fmax=10000)
        return float(aci), float(bi), float(adi)
    except Exception:
        return None


def sample_per_bin(device: str, n: int):
    """Up to n files per diel bin, evenly spaced in time within the bin."""
    d = AUDIO / device
    files = sorted(str(p) for p in d.glob("*.WAV")) or sorted(str(p) for p in d.glob("*.wav"))
    by_bin = defaultdict(list)
    for f in files:
        b = diel_of(f)
        if b:
            by_bin[b].append(f)
    picked = []
    for b, fs in by_bin.items():
        if len(fs) <= n:
            picked += [(b, f) for f in fs]
        else:
            idx = np.linspace(0, len(fs) - 1, n).round().astype(int)
            picked += [(b, fs[i]) for i in sorted(set(idx))]
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-bin", type=int, default=8)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    tasks = []  # (device, diel, path)
    for dev in DEVICES:
        for b, f in sample_per_bin(dev, args.per_bin):
            tasks.append((dev, b, f))
    print(f"computing diel indices on {len(tasks)} files ({len(DEVICES)} recorders, "
          f"≤{args.per_bin}/bin) with {args.workers} workers ...", flush=True)

    acc = defaultdict(list)  # (device, diel) -> [(aci,bi,adi), ...]
    paths = [t[2] for t in tasks]
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for (dev, b, _), val in zip(tasks, ex.map(indices_for_file, paths, chunksize=4)):
            if val is not None:
                acc[(dev, b)].append(val)
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(tasks)}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["device", "deploy", "habitat", "point", "spacing", "diel", "n_files", "ACI", "BI", "ADI"])
        for dev, (deploy, habitat, point) in DEVICES.items():
            for b in DIEL_ORDER:
                vals = np.array(acc.get((dev, b), []))
                if len(vals) == 0:
                    continue
                aci, bi, adi = vals.mean(axis=0)
                w.writerow([dev, deploy, habitat, point, DAY_SPACING[deploy], b, len(vals),
                            round(aci, 2), round(bi, 4), round(adi, 4)])
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
