# Tandayapa recorder-spacing — processed data (pre-analysis)

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
