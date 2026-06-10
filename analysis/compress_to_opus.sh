#!/usr/bin/env bash
# Compress every study WAV to a small mono Opus clip (48 kbps) for web serving.
# Mirrors data/raw/audio/<date>/<folder>/<name>.WAV -> data/web_audio/.../<name>.opus
SRC="data/raw/audio"; DST="data/web_audio"
find "$SRC" -name "*.WAV" -print0 | xargs -0 -P 8 -I{} bash -c '
  f="$1"; src="data/raw/audio"; dst="data/web_audio"
  rel="${f#$src/}"; out="$dst/${rel%.WAV}.opus"
  [ -f "$out" ] && exit 0
  mkdir -p "$(dirname "$out")"
  ffmpeg -hide_banner -loglevel error -y -i "$f" -ac 1 -c:a libopus -b:a 48k "$out"
' _ {}
echo "DONE: $(find "$DST" -name '*.opus' | wc -l) opus files, $(du -sh "$DST" | cut -f1)"
