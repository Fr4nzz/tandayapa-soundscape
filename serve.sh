#!/usr/bin/env bash
# Serve the verification web app on the local network / Tailscale.
# Run from the repo root on the machine that holds the audio; audio + detection
# data stream from this machine (they are not in the GitHub repo).
#   Local:     http://localhost:8000/webapp/dist/
#   Tailscale: http://<this-machine-tailscale-ip>:8000/webapp/dist/
cd "$(dirname "$0")" || exit 1
TS=$(command -v tailscale >/dev/null 2>&1 && tailscale ip -4 2>/dev/null | head -1)
echo "Serving on http://0.0.0.0:8000/webapp/dist/  (Ctrl+C to stop)"
[ -n "$TS" ] && echo "Over Tailscale:  http://$TS:8000/webapp/dist/"
python -m http.server 8000 --bind 0.0.0.0
