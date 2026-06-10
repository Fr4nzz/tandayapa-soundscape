#!/usr/bin/env python3
"""Compute acoustic indices (ACI, BI, ADI) per recorder for the spacing study.

For each recorder-deployment we compute three standard soundscape indices on a
representative sample of its recordings and average them, giving one ACI/BI/ADI
value per recorder (parallel to the per-recorder species community). These feed
the index-based distance-decay analysis and the index-vs-biodiversity comparison.

Indices (scikit-maad):
  ACI = Acoustic Complexity Index   (temporal variability of intensity)
  BI  = Bioacoustic Index           (energy in the 2-8 kHz biological band)
  ADI = Acoustic Diversity Index    (evenness of energy across freq bands)

Output: outputs/analysis/acoustic_indices.csv
Run: .venv-perch/bin/python analysis/compute_acoustic_indices.py [--per-recorder 24]
"""
from __future__ import annotations

import argparse
import csv
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "data" / "audiomoths"
OUT = ROOT / "outputs" / "analysis" / "acoustic_indices.csv"

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


def indices_for_file(path: str):
    """Return (ACI, BI, ADI) for one WAV, or None on failure."""
    try:
        from maad import sound, features
        s, fs = sound.load(path)
        Sxx, tn, fn, ext = sound.spectrogram(s, fs, mode="amplitude")
        _, _, aci = features.acoustic_complexity_index(Sxx)          # ACI (total)
        bi = features.bioacoustics_index(Sxx, fn, flim=(2000, 8000))  # BI
        adi = features.acoustic_diversity_index(Sxx, fn, fmax=10000)  # ADI
        return float(aci), float(bi), float(adi)
    except Exception:
        return None


def sample_files(device: str, n: int):
    d = AUDIO / device
    files = sorted(str(p) for p in d.glob("*.WAV"))
    if not files:
        files = sorted(str(p) for p in d.glob("*.wav"))
    if len(files) <= n:
        return files
    idx = np.linspace(0, len(files) - 1, n).round().astype(int)
    return [files[i] for i in sorted(set(idx))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-recorder", type=int, default=24)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    tasks = []  # (device, path)
    for dev in DEVICES:
        for f in sample_files(dev, args.per_recorder):
            tasks.append((dev, f))
    print(f"computing indices on {len(tasks)} files ({len(DEVICES)} recorders, "
          f"~{args.per_recorder} each) with {args.workers} workers ...", flush=True)

    results = {dev: [] for dev in DEVICES}
    paths = [t[1] for t in tasks]
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for (dev, _), val in zip(tasks, ex.map(indices_for_file, paths, chunksize=4)):
            if val is not None:
                results[dev].append(val)
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(tasks)}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["device", "deploy", "habitat", "point", "spacing", "n_files", "ACI", "BI", "ADI"])
        for dev, (deploy, habitat, point) in DEVICES.items():
            vals = np.array(results[dev])
            if len(vals) == 0:
                continue
            aci, bi, adi = vals.mean(axis=0)
            w.writerow([dev, deploy, habitat, point, DAY_SPACING[deploy], len(vals),
                        round(aci, 2), round(bi, 4), round(adi, 4)])
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
