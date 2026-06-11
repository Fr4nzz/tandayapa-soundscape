#!/usr/bin/env python3
"""Fetch reference calls for each detected species (to compare against detections).

For every bird and frog species in the web-app data we look up a few good
reference recordings and store their playable audio URLs + attribution, so the
web app can play them next to a detection for verification.

Sources, in order of preference:
  1. xeno-canto (API v3, needs a free key in ~/.config/tandayapa/xenocanto.key) —
     curated, quality-graded; best for birds and many frogs. Ecuador recordings
     are preferred, then by quality (A best).
  2. iNaturalist (no key) — research-grade observation audio; fallback.

Insects are skipped (neotropical Orthoptera/cicadas have almost no reference audio);
the app shows a search link for those instead.

Output: webapp/public/data/reference_calls.json (keyed by the detection species string).
Run: python3 analysis/fetch_reference_calls.py
"""
from __future__ import annotations

import glob
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "webapp" / "public" / "data"
OUT = DATA / "reference_calls.json"
KEYFILE = Path.home() / ".config" / "tandayapa" / "xenocanto.key"
XC_KEY = KEYFILE.read_text().strip() if KEYFILE.exists() else None
INAT = "https://api.inaturalist.org/v1/observations"
XC = "https://xeno-canto.org/api/3/recordings"
N = 3
UA = {"User-Agent": "tandayapa-soundscape/1.0 (research; github.com/Fr4nzz/tandayapa-soundscape)"}
QRANK = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "no score": 5, "": 5}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
        return json.load(r)


def from_xc(species: str):
    if not XC_KEY or " " not in species:
        return []
    gen, sp = species.split(" ", 1)
    q = urllib.parse.quote(f"gen:{gen} sp:{sp}")
    try:
        recs = (get(f"{XC}?query={q}&key={XC_KEY}").get("recordings") or [])
    except Exception as e:
        print(f"    xc err {species}: {str(e)[:50]}"); return []
    # prefer Ecuador, then song/call types, then quality A..E
    recs.sort(key=lambda r: (r.get("cnt") != "Ecuador",
                             "song" not in (r.get("type") or "") and "call" not in (r.get("type") or ""),
                             QRANK.get(r.get("q", ""), 5)))
    out = []
    for r in recs[:N]:
        f = r.get("file")
        if not f:
            continue
        out.append({
            "url": f, "source": "xeno-canto",
            "obs_url": f"https://xeno-canto.org/{r.get('id')}",
            "by": r.get("rec") or "xeno-canto",
            "place": ", ".join(x for x in [r.get("loc"), r.get("cnt")] if x)[:60],
            "license": (r.get("lic") or "").split("//")[-1].strip("/"),
        })
    return out


def from_inat(species: str):
    q = urllib.parse.urlencode({"taxon_name": species, "sounds": "true",
                                "quality_grade": "research", "order_by": "votes", "per_page": N})
    try:
        data = get(f"{INAT}?{q}")
    except Exception as e:
        print(f"    inat err {species}: {str(e)[:50]}"); return []
    out = []
    for obs in data.get("results", []):
        s = (obs.get("sounds") or [{}])[0]
        if not s.get("file_url"):
            continue
        out.append({
            "url": s["file_url"], "source": "iNaturalist",
            "obs_url": f"https://www.inaturalist.org/observations/{obs.get('id')}",
            "by": (obs.get("user") or {}).get("login") or "iNaturalist",
            "place": (obs.get("place_guess") or "")[:60],
            "license": s.get("license_code") or "",
        })
    return out


def species_by_group():
    out = {}
    for f in glob.glob(str(DATA / "day*.json")):
        for d in json.load(open(f, encoding="utf-8")):
            out.setdefault(d["species"], d["group"])
    return out


def main():
    sg = species_by_group()
    targets = sorted(s for s, g in sg.items() if g in ("bird", "frog"))
    print(f"{len(sg)} species; fetching refs for {len(targets)} bird/frog "
          f"(xc_key={'yes' if XC_KEY else 'no'}) ...")
    refs = {}
    for i, sp in enumerate(targets, 1):
        r = from_xc(sp)
        src = "xc"
        if not r:
            r = from_inat(sp); src = "inat"
        if r:
            refs[sp] = r
        print(f"  [{i}/{len(targets)}] {sp}: {len(r)} ({src})")
        time.sleep(0.8)
    OUT.write_text(json.dumps(refs, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT}: refs for {len(refs)}/{len(targets)} species "
          f"({sum(1 for v in refs.values() if v and v[0]['source']=='xeno-canto')} from xeno-canto)")


if __name__ == "__main__":
    main()
