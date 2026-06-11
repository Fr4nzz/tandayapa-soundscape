# Tandayapa Soundscape — recorder-spacing study

Passive acoustic monitoring (AudioMoth) at **Tandayapa Cloud Forest Station, Ecuador**, testing how
the **distance between recorders** changes the soundscape they capture, in **forest vs pasture**.
We analyse the data two ways — the **BirdNET species community** and three **acoustic indices**
(ACI, BI, ADI) — compare them, look at **diel** variation, and characterise the **microclimate** with
paired temperature/humidity loggers. Effect sizes (slopes with 95% CIs) are reported throughout, not
p-values, using **linear mixed models** with the deployment day as a random effect.

**Headline result:** the species community shows a real, threshold-robust **distance-decay in the open
pasture** (recorders sample more different communities as they move apart); in forest the trend is weak
and unresolved, and forest did **not** decay faster than pasture. The cheap acoustic indices **do not**
detect this spatial structure — so a biodiversity question about spacing needs species-level data, not
indices alone. The indices *do* cleanly capture the **dawn/day chorus** (BI) and the **forest's
buffered microclimate** (cooler, far more humid than the exposed pasture).

## 🌐 Live site (GitHub Pages — no install needed)

**▶ https://fr4nzz.github.io/tandayapa-soundscape/**

| Page | Link |
|---|---|
| 🏠 **Home** | <https://fr4nzz.github.io/tandayapa-soundscape/> |
| 📄 **Report** (methods, results & figures) | <https://fr4nzz.github.io/tandayapa-soundscape/reports/tandayapa_spacing_biodiversity_report.html> |
| 🎧 **Detection explorer** (browse & verify detections / recordings by ear + spectrogram) | <https://fr4nzz.github.io/tandayapa-soundscape/app/> |

The web app streams audio (Opus) from Cloudflare R2, so it works in any browser with nothing to host.

## Reproduce the analysis in RStudio

The report knits from the **processed data committed in this repo** (`data/processed/`), so you do
**not** need the raw audio.

1. **Clone** the repository:
   ```bash
   git clone https://github.com/Fr4nzz/tandayapa-soundscape.git
   cd tandayapa-soundscape
   ```
2. **Open the project** `tandayapa-soundscape.Rproj` in RStudio (File → Open Project).
3. **Install the R packages** (once):
   ```r
   install.packages(c("tidyverse", "vegan", "lme4", "lmerTest", "knitr", "rmarkdown"))
   ```
4. **Open** `reports/tandayapa_spacing_biodiversity_report.Rmd` and click **Knit** (or run
   `rmarkdown::render("reports/tandayapa_spacing_biodiversity_report.Rmd")`). It regenerates every
   table and figure from the processed CSVs.

## Repository layout

```
data/
  raw/                 # raw inputs — mostly NOT in git (see "Getting the raw data")
    audio/<date>/<habitat>_<spacing>m_p<point>_<audiomoth>/*.WAV   # ~27 GB, gitignored
    gps/               # GPS waypoints (in git)
    dataloggers/       # Kestrel DROP 2 temperature/humidity loggers (in git)
    models/            # BirdNET / frog classifier models (gitignored)
  metadata/
    deployments.csv    # single source of truth: one row per recorder-deployment
  processed/           # analysis-ready CSVs (in git) — see data/processed/README.md
analysis/              # Python + R scripts (indices, detections, reorganization, export)
reports/               # the R Markdown report + rendered HTML
webapp/                # React app to browse/verify detections (optional)
```

`data/metadata/deployments.csv` maps every recorder to its date, habitat, spacing, transect point and
AudioMoth unit, and keeps the original folder name so the reorganization is reversible.
`data/processed/README.md` is the data dictionary for the processed CSVs.

## Getting the raw data (audio + models)

The ~27 GB of AudioMoth recordings and the classifier models are **not** in git. They are shared
separately (Google Drive / Zenodo — link TBD) and are only needed to re-run the upstream steps
(`analysis/compute_*_indices.py`, BirdNET); the report itself runs entirely from `data/processed/`.

## Field & pipeline notes

- **AudioMoth format:** 48 kHz mono 16-bit; three 2-min clips per hour (2 min on / 18 min off),
  recording ~10:40 → 9:40 next day across the full day–night cycle.
- **Clock offset:** two units (`F1503_A08`, `F3003_A07`) were set to UTC (5 h fast); timestamps were
  corrected in the detection pipeline.
- **Classifier caveats:** BirdNET (birds, range-filtered) and a custom frog classifier; the frog model
  is closed-set, so it can label noise as a frog — three taxa (*Pipa pipa*, *Sachatamia orejuela*,
  *Teratohyla pulveratum*) were reviewed and excluded (flagged, not deleted, in
  `data/processed/birdnet_detections.csv`). Insects are reliable to family level (genus approximate).

## Authors

Franz Chandi, Maria Andrade, Priscila Cajas, Noemi Castro — Tropical Ecology & Conservation, USFQ.
