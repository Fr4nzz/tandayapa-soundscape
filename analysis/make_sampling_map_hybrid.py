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
OUT_POINTS = ROOT / "outputs" / "analysis" / "sampling_gps_points.png"
OUT_TRAIL = ROOT / "outputs" / "analysis" / "sampling_trail_map.png"
OUT_MERGED = ROOT / "outputs" / "analysis" / "sampling_map_merged.png"
R = 6378137.0
COLS = {"forest": "#39B54A", "pasture": "#F2C14E", "trail": "#E74C3C", "study_area": "#3498DB"}


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

    # Parse trail
    trail_lons, trail_lats = [], []
    if TRAIL.exists():
        trail_lons, trail_lats = parse_gpx_trail(TRAIL)
    trail_x, trail_y = merc(trail_lons, trail_lats) if trail_lons else ([], [])

    # Compute study area center (centroid of all points)
    center_x = plot["x"].mean()
    center_y = plot["y"].mean()

    # Get trail start and end for labels
    trail_start_x, trail_start_y = trail_x[0], trail_y[0] if len(trail_x) > 0 else (None, None)
    trail_end_x, trail_end_y = trail_x[-1], trail_y[-1] if len(trail_x) > 0 else (None, None)

    label_offsets = {
        ("forest", 0): (-62, 16), ("forest", 15): (-42, 34), ("forest", 30): (-10, 42),
        ("forest", 60): (0, 38), ("forest", 120): (18, 25),
        ("pasture", 0): (-22, -38), ("pasture", 15): (-8, -38), ("pasture", 30): (8, -38),
        ("pasture", 60): (0, -38), ("pasture", 120): (15, -38),
    }

    # === MERGED FIGURE: side-by-side trail + zoomed points ===
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(18, 9))

    # --- LEFT: Trail map with small sampling points + big study area / start / end points ---
    if len(trail_x) > 0:
        ax_left.plot(trail_x, trail_y, "-", color=COLS["trail"], lw=2.5, alpha=.85, zorder=4)

    # Draw small sampling points with lines on trail map
    for hab, sub in plot.groupby("habitat"):
        sub = sub.sort_values("pos")
        color = COLS[hab]
        ax_left.plot(sub["x"], sub["y"], "-", color=color, lw=1.5, alpha=.7, zorder=5)
        ax_left.scatter(sub["x"], sub["y"], s=60, color=color, edgecolor="white", lw=1, zorder=6)

    # Big point at study area center
    ax_left.scatter([center_x], [center_y], s=200, color=COLS["study_area"], edgecolor="white", lw=2, zorder=6)
    ax_left.annotate("Study area", (center_x, center_y), xytext=(18, 18), textcoords="offset points",
                ha="center", va="center", fontsize=9, fontweight="bold", color="white",
                arrowprops=dict(arrowstyle="-", color="white", lw=.6, alpha=.65),
                bbox=dict(boxstyle="round,pad=0.2", fc=COLS["study_area"], ec="white", alpha=.9), zorder=7)

    # Big point and label for trail start (Tandayapa Station)
    if trail_start_x is not None:
        ax_left.scatter([trail_start_x], [trail_start_y], s=200, color=COLS["study_area"], edgecolor="white", lw=2, zorder=6)
        ax_left.annotate("Tandayapa Station", (trail_start_x, trail_start_y), xytext=(-15, -30),
                        textcoords="offset points", ha="center", va="center",
                        fontsize=9, fontweight="bold", color="white",
                        arrowprops=dict(arrowstyle="-", color="white", lw=.6, alpha=.65),
                        bbox=dict(boxstyle="round,pad=0.2", fc=COLS["study_area"], ec="white", alpha=.9), zorder=7)

    # Big point and label for trail end (Domos)
    if trail_end_x is not None:
        ax_left.scatter([trail_end_x], [trail_end_y], s=200, color=COLS["study_area"], edgecolor="white", lw=2, zorder=6)
        ax_left.annotate("Domos", (trail_end_x, trail_end_y), xytext=(15, 15),
                        textcoords="offset points", ha="center", va="center",
                        fontsize=9, fontweight="bold", color="white",
                        arrowprops=dict(arrowstyle="-", color="white", lw=.6, alpha=.65),
                        bbox=dict(boxstyle="round,pad=0.2", fc=COLS["study_area"], ec="white", alpha=.9), zorder=7)

    # Set bounds for left panel to show full trail + points
    if len(trail_x) > 0:
        all_x = list(trail_x) + list(plot["x"])
        all_y = list(trail_y) + list(plot["y"])
    else:
        all_x = list(plot["x"])
        all_y = list(plot["y"])
    pad_left = 80
    ax_left.set_xlim(min(all_x) - pad_left, max(all_x) + pad_left)
    ax_left.set_ylim(min(all_y) - pad_left, max(all_y) + pad_left)
    cx.add_basemap(ax_left, source=cx.providers.Esri.WorldImagery, zoom=17, attribution=False)

    # Left panel: scale and north
    x0, x1 = ax_left.get_xlim(); y0, y1 = ax_left.get_ylim()
    bx = x0 + (x1 - x0) * .06; by = y0 + (y1 - y0) * .06
    ax_left.plot([bx, bx + 50], [by, by], color="white", lw=3, zorder=8)
    ax_left.text(bx + 25, by + (y1-y0)*.012, "50 m", color="white", ha="center", va="bottom", fontsize=9, fontweight="bold", zorder=8)
    nax = x1 - (x1-x0)*.07; nay = y1 - (y1-y0)*.14
    ax_left.add_patch(FancyArrowPatch((nax, nay), (nax, nay + (y1-y0)*.09), arrowstyle="-|>", mutation_scale=18, color="white", lw=2.2, zorder=8))
    ax_left.text(nax, nay + (y1-y0)*.10, "N", ha="center", va="bottom", color="white", fontsize=12, fontweight="bold", zorder=8)
    ax_left.set_xticks([]); ax_left.set_yticks([])
    ax_left.set_title("(A) Trail from Tandayapa Station to Domos", fontsize=11, fontweight="bold")
    ax_left.text(.01, .01, "Imagery © Esri, Maxar, Earthstar Geographics",
                transform=ax_left.transAxes, fontsize=7, color="white", alpha=.8)

    # --- RIGHT: Zoomed sampling points ---
    for hab, sub in plot.groupby("habitat"):
        sub = sub.sort_values("pos")
        color = COLS[hab]
        ax_right.plot(sub["x"], sub["y"], "-", color=color, lw=2.2,
                alpha=.9, zorder=5, label=("Forest" if hab == "forest" else "Pasture"))
        ax_right.scatter(sub["x"], sub["y"], s=130, color=color, edgecolor="white", lw=1.8, zorder=6)
        for _, r in sub.iterrows():
            dx, dy = label_offsets.get((hab, int(r["pos"])), (0, 22))
            ax_right.annotate(r["label"], (r["x"], r["y"]), xytext=(dx, dy), textcoords="offset points",
                        ha="center", va="center", fontsize=7.5, fontweight="bold", color="white",
                        arrowprops=dict(arrowstyle="-", color="white", lw=.6, alpha=.65),
                        bbox=dict(boxstyle="round,pad=0.16", fc="black", ec="none", alpha=.65), zorder=7)

    pad = 45
    ax_right.set_xlim(plot["x"].min() - pad, plot["x"].max() + pad)
    ax_right.set_ylim(plot["y"].min() - pad, plot["y"].max() + pad)
    cx.add_basemap(ax_right, source=cx.providers.Esri.WorldImagery, zoom=18, attribution=False)

    # Right panel: scale and north
    x0, x1 = ax_right.get_xlim(); y0, y1 = ax_right.get_ylim()
    bx = x0 + (x1 - x0) * .06; by = y0 + (y1 - y0) * .06
    ax_right.plot([bx, bx + 50], [by, by], color="white", lw=3, zorder=8)
    ax_right.text(bx + 25, by + (y1-y0)*.012, "50 m", color="white", ha="center", va="bottom", fontsize=9, fontweight="bold", zorder=8)
    nax = x1 - (x1-x0)*.07; nay = y1 - (y1-y0)*.14
    ax_right.add_patch(FancyArrowPatch((nax, nay), (nax, nay + (y1-y0)*.09), arrowstyle="-|>", mutation_scale=18, color="white", lw=2.2, zorder=8))
    ax_right.text(nax, nay + (y1-y0)*.10, "N", ha="center", va="bottom", color="white", fontsize=12, fontweight="bold", zorder=8)
    ax_right.set_xticks([]); ax_right.set_yticks([])
    ax_right.set_title("(B) Sampling points (forest raw GPS, pasture corrected)", fontsize=11, fontweight="bold")
    ax_right.legend(loc="lower right", framealpha=.86, fontsize=8)
    ax_right.text(.01, .01, "Imagery © Esri, Maxar, Earthstar Geographics",
                transform=ax_right.transAxes, fontsize=7, color="white", alpha=.8)

    fig.tight_layout()
    fig.savefig(OUT_MERGED, dpi=200, bbox_inches="tight")
    print("wrote", OUT_MERGED)

    # === Also keep the individual point map for reference ===
    fig1, ax1 = plt.subplots(figsize=(9, 8))
    for hab, sub in plot.groupby("habitat"):
        sub = sub.sort_values("pos")
        color = COLS[hab]
        ax1.plot(sub["x"], sub["y"], "-", color=color, lw=2.2,
                alpha=.9, zorder=5, label=("Forest original GPS points" if hab == "forest" else "Pasture corrected GPS points"))
        ax1.scatter(sub["x"], sub["y"], s=130, color=color, edgecolor="white", lw=1.8, zorder=6)
        for _, r in sub.iterrows():
            dx, dy = label_offsets.get((hab, int(r["pos"])), (0, 22))
            ax1.annotate(r["label"], (r["x"], r["y"]), xytext=(dx, dy), textcoords="offset points",
                        ha="center", va="center", fontsize=7.5, fontweight="bold", color="white",
                        arrowprops=dict(arrowstyle="-", color="white", lw=.6, alpha=.65),
                        bbox=dict(boxstyle="round,pad=0.16", fc="black", ec="none", alpha=.65), zorder=7)
    pad = 45
    ax1.set_xlim(plot["x"].min() - pad, plot["x"].max() + pad)
    ax1.set_ylim(plot["y"].min() - pad, plot["y"].max() + pad)
    cx.add_basemap(ax1, source=cx.providers.Esri.WorldImagery, zoom=18, attribution=False)
    x0, x1 = ax1.get_xlim(); y0, y1 = ax1.get_ylim()
    bx = x0 + (x1 - x0) * .06; by = y0 + (y1 - y0) * .06
    ax1.plot([bx, bx + 50], [by, by], color="white", lw=3, zorder=8)
    ax1.text(bx + 25, by + (y1-y0)*.012, "50 m", color="white", ha="center", va="bottom", fontsize=9, fontweight="bold", zorder=8)
    nax = x1 - (x1-x0)*.07; nay = y1 - (y1-y0)*.14
    ax1.add_patch(FancyArrowPatch((nax, nay), (nax, nay + (y1-y0)*.09), arrowstyle="-|>", mutation_scale=18, color="white", lw=2.2, zorder=8))
    ax1.text(nax, nay + (y1-y0)*.10, "N", ha="center", va="bottom", color="white", fontsize=12, fontweight="bold", zorder=8)
    ax1.set_xticks([]); ax1.set_yticks([])
    ax1.set_title("Tandayapa recorder sampling map — forest raw GPS, pasture corrected GPS", fontsize=11, fontweight="bold")
    ax1.legend(loc="lower right", framealpha=.86, fontsize=8)
    ax1.text(.01, .01, "Imagery © Esri, Maxar, Earthstar Geographics",
            transform=ax1.transAxes, fontsize=7, color="white", alpha=.8)
    fig1.savefig(OUT_POINTS, dpi=200, bbox_inches="tight")
    print("wrote", OUT_POINTS)

    print("forest: raw/original GPS points plotted")
    print("pasture: corrected GPS points plotted (no red X markers)")


if __name__ == "__main__":
    main()
