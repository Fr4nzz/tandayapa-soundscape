# Tandayapa sound-verification gallery (local website)

Browse BirdNET detections, filter/sort them, and play each one while a playhead
sweeps the spectrogram — so you can confirm species IDs by ear and eye.

## How to run
1. Make sure detections exist (`outputs/birdnet_detections_day1.csv`) and the data
   file is built:
   ```
   Rscript build_gallery_site.R      # writes outputs/gallery_site/manifest.js
   ```
2. Double-click **`serve_gallery.bat`** (in the `d:\Audiomoths` folder).
   It starts a local server and opens the site.
3. Open it on this PC at `http://localhost:8000/outputs/gallery_site/`, or from
   another device on the same network at the `http://<this-PC-IP>:8000/...` URL
   the window prints.

The audio is streamed straight from this PC's original WAV files — nothing is
copied or uploaded.

## Using it
- **Filters:** search species, habitat, recorder, day/night, minimum hour, and a
  minimum-confidence slider.
- **Sort:** confidence, time, or species name.
- **Each card:** click *Load spectrogram & audio*, then *Play detection* (plays
  just the detected interval, highlighted in red) or *Play full clip*. The red
  line follows playback; click the spectrogram to seek.

## Notes
- Needs Python (for the server) — already installed on this PC.
- The frequency axis is shown 0–12 kHz; the red box marks the detected time
  interval (BirdNET works on 3-s segments, so the box spans the full band).
- Rebuild `manifest.js` whenever detections change (new day, new threshold).
