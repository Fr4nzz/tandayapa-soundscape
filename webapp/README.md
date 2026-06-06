# Tandayapa Soundscape — web app

A React + Vite app to browse, filter, and **verify** BirdNET (and frog) detections:
play each call while a playhead sweeps a magma spectrogram, with confidence shown.
Multi-day, multi-taxon; audio streams from this PC's original WAVs over the LAN.

## Data flow (decoupled)
The R/Python pipelines stay the data layer. `export_web_data.R` reads each
`outputs/<day>/birdnet_detections.csv` (+ range filter) and `frog_detections.csv`,
and writes `outputs/web/<day>.json` + `outputs/web/index.json`. The app fetches those.

```
Rscript export_web_data.R          # whenever detections change (new day / taxon / threshold)
```

## Run it

**Share over LAN (recommended):**
```
cd webapp && npm install   # once
npm run build              # -> webapp/dist (static)
```
Then from the repo root, double-click **`serve_webapp.bat`** (serves the app + data +
audio over the LAN and opens it). Viewers need nothing installed.

**Develop (hot reload):** run the Python server once (`serve_webapp.bat` or
`python -m http.server 8000`), then in another terminal `cd webapp && npm run dev`.
Vite proxies `/outputs` and the audio folders to the Python server, so data + audio
resolve while you edit. Open the printed `localhost:5173` URL.

## Filters / sorts
Day · taxon (bird/frog) · species search · habitat · recorder · day-night · minimum
hour · minimum confidence; sort by confidence / time / species.

## Adding a day
Add the day's devices + window to `tandayapa_common.R`, run the pipeline for it
(`run_birdnet_day1.R` with `TANDAYAPA_DAY`), then `Rscript export_web_data.R` and
reload — the new day appears in the Day filter automatically.

## Notes
- Offline-ready: fonts (Fraunces, JetBrains Mono) are bundled; wavesurfer is npm.
- The app is served at `/webapp/dist/`; data at `/outputs/web/`; audio at `/<folder>/<file>.WAV`
  — all from the same Python server root.
