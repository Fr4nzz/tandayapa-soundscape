#!/usr/bin/env python3
"""Hybrid sampling map for Franz's correction request.

Uses actual/raw GPS coordinates for both forest and pasture, but with corrected
labels for pasture. Does NOT show red X markers.

Output:
  outputs/analysis/sampling_map_hybrid_raw_forest_corrected_pasture.png
"""
from __future__ import annotations

from pathlib import Path

import xml.etree.ElementTree as ET

import contextily as cx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GPS = ROOT / "data" / "raw" / "gps" / "tandayapa_gps_waypoints.csv"
TRAIL = ROOT / "data" / "raw" / "gps" / "tandayapa-audiomoths-experiment.gpx"
OUT = ROOT / "outputs" / "analysis" / "sampling_gps_points.png"
R = 6378137.0
COLS = {"forest": "#39B54A", "pasture": "#F2C14E", "trail": "#E74C3C"}


def merc(lon, lat):
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    x = R * np.radians(lon)
    y = R * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
    return x, y


def parse_gpx_trail(path):
    """Extract lat/lon points from a GPX track."""
    tree = ET.parse(path)
    root = tree.getroot()
    # Handle namespace
    ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
    lats, lons = [], []
    for trkpt in root.findall(".//gpx:trkpt", ns):
        lat = trkpt.get("lat")
        lon = trkpt.get("lon")
        if lat and lon:
            lats.append(float(lat))
            lons.append(float(lon))
    return lons, lats


def main() -> None:
    df = pd.read_csv(GPS)
    clat = df["lat_dd"].median()

    # Filter out rows explicitly marked as REMOVED in notes
    df = df[~(df["notes"].astype(str).str.contains("REMOVED", na=False))].copy()

    # FOREST: preserve original/raw GPS points, excluding the unresolved '?' row.
    forest = df[(df.habitat == "forest") & (df.canonical_point != "?")].copy()
    forest["plot_kind"] = "raw GPS"
    forest["pos"] = forest["nominal_position_m"]
    forest["label"] = forest.apply(lambda r: f"{int(r['nominal_position_m'])} m", axis=1)

    # PASTURE: use actual GPS coordinates but with corrected labels
    pasture = df[(df.habitat == "pasture") & (df.canonical_point != "?")].copy()
    pasture["plot_kind"] = "corrected GPS"
    pasture["pos"] = pasture["nominal_position_m"]
    pasture["label"] = pasture.apply(lambda r: f"{int(r['nominal_position_m'])} m", axis=1)

    plot = pd.concat([
        forest[["habitat", "lat_dd", "lon_dd", "pos", "raw_label", "plot_kind", "label"]],
        pasture[["habitat", "lat_dd", "lon_dd", "pos", "raw_label", "plot_kind", "label"]],
    ], ignore_index=True)
    plot["x"], plot["y"] = merc(plot["lon_dd"], plot["lat_dd"])

    fig, ax = plt.subplots(figsize=(9, 8))

    label_offsets = {
        ("forest", 0): (-62, 16), ("forest", 15): (-42, 34), ("forest", 30): (-10, 42),
        ("forest", 60): (0, 38), ("forest", 120): (18, 25),
        ("pasture", 0): (-22, -38), ("pasture", 15): (-8, -38), ("pasture", 30): (8, -38),
        ("pasture", 60): (0, -38), ("pasture", 120): (15, -38),
    }

    # Draw lines in nominal order, then points
    for hab, sub in plot.groupby("habitat"):
        sub = sub.sort_values("pos")
        color = COLS[hab]
        ax.plot(sub["x"], sub["y"], "-", color=color, lw=2.2,
                alpha=.9, zorder=5, label=("Forest original GPS points" if hab == "forest" else "Pasture corrected GPS points"))
        ax.scatter(sub["x"], sub["y"], s=130, color=color, edgecolor="white", lw=1.8, zorder=6)
        for _, r in sub.iterrows():
            dx, dy = label_offsets.get((hab, int(r["pos"])), (0, 22))
            ax.annotate(r["label"], (r["x"], r["y"]), xytext=(dx, dy), textcoords="offset points",
                        ha="center", va="center", fontsize=7.5, fontweight="bold", color="white",
                        arrowprops=dict(arrowstyle="-", color="white", lw=.6, alpha=.65),
                        bbox=dict(boxstyle="round,pad=0.16", fc="black", ec="none", alpha=.65), zorder=7)

    pad = 45
    ax.set_xlim(plot["x"].min() - pad, plot["x"].max() + pad)
    ax.set_ylim(plot["y"].min() - pad, plot["y"].max() + pad)
    cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery, zoom=18, attribution=False)

    # Draw trail from GPX
    if TRAIL.exists():
        trail_lons, trail_lats = parse_gpx_trail(TRAIL)
        trail_x, trail_y = merc(trail_lons, trail_lats)
        ax.plot(trail_x, trail_y, "-", color=COLS["trail"], lw=2.5, alpha=.85, zorder=4, label="Trail from Tandayapa Station")

    # scale and north
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    bx = x0 + (x1 - x0) * .06; by = y0 + (y1 - y0) * .06
    ax.plot([bx, bx + 50], [by, by], color="white", lw=3, zorder=8)
    ax.text(bx + 25, by + (y1-y0)*.012, "50 m", color="white", ha="center", va="bottom", fontsize=9, fontweight="bold", zorder=8)
    nax = x1 - (x1-x0)*.07; nay = y1 - (y1-y0)*.14
    ax.add_patch(FancyArrowPatch((nax, nay), (nax, nay + (y1-y0)*.09), arrowstyle="-|>", mutation_scale=18, color="white", lw=2.2, zorder=8))
    ax.text(nax, nay + (y1-y0)*.10, "N", ha="center", va="bottom", color="white", fontsize=12, fontweight="bold", zorder=8)

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Tandayapa recorder sampling map — forest raw GPS, pasture corrected GPS\n"
                 "Pasture P6002 corrected to P-000; P30-02-A03 corrected to P-060", fontsize=11, fontweight="bold")
    ax.legend(loc="lower right", framealpha=.86, fontsize=8)
    ax.text(.01, .01, "Imagery © Esri, Maxar, Earthstar Geographics",
            transform=ax.transAxes, fontsize=7, color="white", alpha=.8)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print("wrote", OUT)
    print("forest: raw/original GPS points plotted")
    print("pasture: corrected GPS points plotted (no red X markers)")


if __name__ == "__main__":
    main()
