#!/usr/bin/env bash
# Copy all AudioMoth device folders (WAV + CONFIG) to the cloned repo on the GPD PC.
# tar-over-ssh per folder; skips empty folders and folders already fully transferred
# (so it's resumable — just re-run if interrupted).
cd "d:/Audiomoths" || exit 1
DEST="/home/franz/Documents/CodeProjs/tandayapa-soundscape"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=15"

ok=0; skip=0; done_already=0
find . -maxdepth 1 -type d \( -name 'F*_A*' -o -name 'P*_A*' \) -print0 | sort -z |
while IFS= read -r -d '' d; do
  name="${d#./}"
  lc=$(find "$d" -maxdepth 1 -iname '*.WAV' | wc -l)
  if [ "$lc" -eq 0 ]; then echo "SKIP (empty): $name"; continue; fi
  rc=$($SSH gpd "find \"$DEST/$name\" -maxdepth 1 -iname '*.WAV' 2>/dev/null | wc -l" 2>/dev/null)
  if [ "${rc:-0}" = "$lc" ]; then echo "DONE already ($lc files): $name"; continue; fi
  echo ">>> $name : sending $lc files (remote had ${rc:-0}) @ $(date +%H:%M:%S)"
  if tar -C "$d" -cf - . | $SSH gpd "mkdir -p \"$DEST/$name\" && tar -C \"$DEST/$name\" -xf -"; then
    echo "    OK $name @ $(date +%H:%M:%S)"
  else
    echo "    !! FAILED $name (will retry on next run)"
  fi
done
echo "===== AUDIO TRANSFER FINISHED @ $(date +%H:%M:%S) ====="
