#!/usr/bin/env python3
"""Export the PROCESSED (pre-analysis) data to share with collaborators.

Bundles the two inputs every analysis in this project starts from:
  1. BirdNET (+ frog/insect) detections with timestamps and recorder metadata
  2. Acoustic indices (per recorder, and per recorder x diel period)

Detections keep ALL taxa — the three suspected false-positive frog taxa are NOT
removed here; instead a transparent `suspect_false_positive` flag marks them, so
collaborators see exactly what we excluded and why.

Output: data/processed/  (CSVs + README)
Run: .venv-perch/bin/python analysis/export_processed_data.py
"""
from __future__ import annotations

import csv
import datetime as dt
import glob
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "outputs" / "web"
ANALYSIS = ROOT / "outputs" / "analysis"
DLOG = ROOT / "data" / "raw" / "dataloggers"
OUT = ROOT / "data" / "processed"

# suspected BirdNET false positives (noise classified as these frog taxa)
EXCLUDED_FROGS = ["Pipa pipa", "Sachatamia orejuela", "Teratohyla pulveratum"]
DATE_DEPLOY = {"2026-06-02": "day1", "2026-06-03": "day2", "2026-06-04": "day3",
               "2026-06-05": "day4", "2026-06-06": "day5", "2026-06-07": "day6"}

COLUMNS = ["id", "datetime", "date", "deploy", "hour", "daynight", "habitat", "point",
           "point_num", "audiomoth_id", "spacing_m", "group", "species", "common_name",
           "confidence", "clip_start_s", "clip_end_s", "audio_file",
           "suspect_false_positive"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted(glob.glob(str(WEB / "day*.json"))):
        for d in json.load(open(f, encoding="utf-8")):
            recorder = d.get("recorder", "")          # e.g. F1 = forest point 1
            point_num = "".join(c for c in recorder if c.isdigit())
            rows.append({
                "id": d["id"], "datetime": d["time"], "date": d["day"],
                "deploy": DATE_DEPLOY.get(d["day"], ""), "hour": d["hour"],
                "daynight": d["daynight"], "habitat": d["habitat"],
                "point": recorder, "point_num": point_num,
                "audiomoth_id": d.get("moth", ""),        # e.g. A05
                "spacing_m": d.get("spacing", ""), "group": d["group"],
                "species": d["species"], "common_name": d.get("common", d["species"]),
                "confidence": d["conf"], "clip_start_s": d.get("start", ""),
                "clip_end_s": d.get("end", ""), "audio_file": d["audio"],
                "suspect_false_positive": "yes" if d["species"] in EXCLUDED_FROGS else "no",
            })
    rows.sort(key=lambda r: (r["datetime"], r["habitat"], r["point"]))
    det = OUT / "birdnet_detections.csv"
    with det.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)
    print(f"wrote {det}  ({len(rows)} detections, "
          f"{sum(r['suspect_false_positive']=='yes' for r in rows)} flagged false-positive)")

    # copy the acoustic-index tables (per recorder + diel)
    for src, dst in [("acoustic_indices.csv", "acoustic_indices_per_recorder.csv"),
                     ("diel_indices.csv", "acoustic_indices_by_diel.csv")]:
        s = ANALYSIS / src
        if s.exists():
            shutil.copy(s, OUT / dst); print(f"copied {dst}")

    export_dataloggers()

    (OUT / "README.md").write_text(README, encoding="utf-8")
    print(f"wrote {OUT/'README.md'}")


def export_dataloggers():
    """Tidy the two Kestrel DROP 2 logger files into one long-format CSV (study window)."""
    files = {"forest": DLOG / "datalogger_forest_KestrelDROP2_sn2867308.csv",
             "pasture": DLOG / "datalogger_pasture_KestrelDROP2_sn2867305.csv"}
    if not all(p.exists() for p in files.values()):
        print("  (datalogger files not found, skipping microclimate export)"); return
    rows = []
    for habitat, path in files.items():
        for row in csv.reader(open(path, encoding="utf-8")):
            try:
                t = dt.datetime.strptime(row[0], "%Y-%m-%d %I:%M:%S %p")
            except (ValueError, IndexError):
                continue
            if not (dt.datetime(2026, 6, 2, 12) <= t < dt.datetime(2026, 6, 9)):
                continue
            if len(row) < 6 or row[5] != "point":
                continue
            try:
                temp, rh, dew = float(row[1]), float(row[2]), float(row[4])
            except (ValueError, IndexError):
                continue
            h = t.hour
            daynight = "day" if 6 <= h < 18 else "night"
            rows.append([t.strftime("%Y-%m-%d %H:%M:%S"), t.strftime("%Y-%m-%d"), h,
                         daynight, habitat, round(temp, 1), round(rh, 1), round(dew, 1)])
    rows.sort(key=lambda r: (r[4], r[0]))
    out = OUT / "datalogger_microclimate.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["datetime", "date", "hour", "daynight", "habitat",
                    "temp_c", "rh_pct", "dew_point_c"])
        w.writerows(rows)
    print(f"wrote {out}  ({len(rows)} microclimate readings)")


README = """# Tandayapa recorder-spacing — processed data (pre-analysis)

These are the cleaned **inputs** used by the analyses (not the analysis results).

## Files

### `birdnet_detections.csv`
One row per acoustic detection (birds & insects from BirdNET; frogs from a frog
classifier). Columns:

| column | meaning |
|---|---|
| `id` | unique detection id |
| `datetime` | timestamp of the detection (local time) |
| `date`, `deploy`, `hour`, `daynight` | date, deployment block (day1–day6), hour (0–23), day/night |
| `habitat` | forest or pasture |
| `point`, `point_num` | transect point (`F1` = forest point 1) and its number (1–3) |
| `audiomoth_id` | which AudioMoth unit recorded it (e.g. `A05`) |
| `spacing_m` | recorder spacing that day (15, 30, or 60 m) |
| `group` | bird / frog / insect |
| `species`, `common_name` | detected taxon |
| `confidence` | classifier confidence 0–1 |
| `clip_start_s`, `clip_end_s` | seconds within the 2-min clip |
| `audio_file` | source WAV (path = `/<audiomoth_folder>/<YYYYMMDD_HHMMSS>.WAV`) |
| `suspect_false_positive` | `yes` for the 3 frog taxa we believe are noise misclassified (see below) |

**Suspected false-positive frog taxa (flagged, excluded from analysis):**
Pipa pipa, Sachatamia orejuela, Teratohyla pulveratum. After listening + spectrogram
review these were judged to be noise classified as frogs. They are kept here (flagged)
for transparency; set `suspect_false_positive == "no"` to reproduce the analysis set.
Insect detections were reviewed and kept (reliable).

### `acoustic_indices_per_recorder.csv`
One row per recorder: mean ACI, BI, ADI over a representative sample of its clips.

### `acoustic_indices_by_diel.csv`
One row per recorder × diel period (dawn/day/dusk/night): mean ACI, BI, ADI.

Indices: ACI = Acoustic Complexity Index, BI = Bioacoustic Index (2–8 kHz),
ADI = Acoustic Diversity Index. Computed with scikit-maad.

### `datalogger_microclimate.csv`
Tidied Kestrel DROP 2 readings (10-min interval) for the study window, one row per
reading: `datetime, date, hour, daynight, habitat, temp_c, rh_pct, dew_point_c`.
"""


if __name__ == "__main__":
    main()
