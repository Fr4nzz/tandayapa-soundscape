#!/usr/bin/env python3
"""Make a nice satellite map of the recorder sampling points (forest vs pasture).

Reads data/raw/gps/tandayapa_gps_waypoints.csv, de-duplicates GPS reads per
canonical transect point, drops anomalous reads far from the cluster, and plots
the forest and pasture transects on Esri satellite imagery with labels, a scale
bar, a north arrow and an Ecuador locator inset.

Output: outputs/analysis/sampling_map.png
Run: .venv-perch/bin/python analysis/make_sampling_map.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import contextily as cx

ROOT = Path(__file__).resolve().parent.parent
GPS = ROOT / "data" / "raw" / "gps" / "tandayapa_gps_waypoints.csv"
OUT = ROOT / "outputs" / "analysis" / "sampling_map.png"
COLS = {"forest": "#39B54A", "pasture": "#F2C14E"}
R = 6378137.0


def merc(lon, lat):
    x = R * np.radians(lon)
    y = R * np.log(np.tan(np.pi / 4 + np.radians(np.asarray(lat)) / 2))
    return x, y


def main():
    df = pd.read_csv(GPS)
    df = df[df["canonical_point"].notna() & (df["canonical_point"] != "?")].copy()
    # average duplicate GPS reads per canonical point
    g = (df.groupby(["canonical_point", "habitat"])
           .agg(lat=("lat_dd", "mean"), lon=("lon_dd", "mean"),
                pos=("nominal_position_m", "first")).reset_index())
    # drop anomalous reads > 150 m from the median centre
    clat, clon = g["lat"].median(), g["lon"].median()
    d_m = np.hypot((g["lat"] - clat) * 111000, (g["lon"] - clon) * 111000 * np.cos(np.radians(clat)))
    dropped = g[d_m > 150]
    g = g[d_m <= 150].copy()

    # Raw GPS error (~15 m) is comparable to the 15-60 m spacing, so plotting the raw
    # reads makes the transects zig-zag. Instead we draw the *design* to scale: straight
    # transects with points at their true positions (0/15/30/60/120 m), increasing east.
    fpos = g[g.habitat == "forest"].set_index("pos")
    f0 = fpos.loc[0]; f120 = fpos.loc[120]
    de = (f120["lon"] - f0["lon"]) * 111320 * np.cos(np.radians(clat))   # east metres 0->120
    dn = (f120["lat"] - f0["lat"]) * 110570                              # north metres
    mag = np.hypot(de, dn); ue, un = de / mag, dn / mag                  # unit bearing (eastward)
    POS = [0, 15, 30, 60, 120]

    def line(lat0, lon0):
        rows = []
        for p in POS:
            rows.append(dict(pos=p,
                             lat=lat0 + p * un / 110570,
                             lon=lon0 + p * ue / (111320 * np.cos(np.radians(clat)))))
        return pd.DataFrame(rows)

    forest = line(f0["lat"], f0["lon"]); forest["habitat"] = "forest"
    # anchor the pasture line through the real pasture cluster centroid
    pc = g[g.habitat == "pasture"]
    mp = pc["pos"].mean()
    p0lat = pc["lat"].mean() - mp * un / 110570
    p0lon = pc["lon"].mean() - mp * ue / (111320 * np.cos(np.radians(clat)))
    pasture = line(p0lat, p0lon); pasture["habitat"] = "pasture"
    g = pd.concat([forest, pasture], ignore_index=True)
    g["x"], g["y"] = merc(g["lon"].values, g["lat"].values)

    fig, ax = plt.subplots(figsize=(8.5, 8))
    # transect lines + points per habitat; labels pushed radially out from the cluster
    for hab, sub in g.groupby("habitat"):
        sub = sub.sort_values("pos")
        cx0, cy0 = sub["x"].mean(), sub["y"].mean()
        ax.plot(sub["x"], sub["y"], "-", color=COLS[hab], lw=2, alpha=.85, zorder=3)
        ax.scatter(sub["x"], sub["y"], s=130, color=COLS[hab], edgecolor="white",
                   linewidth=1.8, zorder=4, label=f"{hab.capitalize()} transect")
        for _, r in sub.iterrows():
            ang = np.arctan2(r["y"] - cy0, r["x"] - cx0)
            if not np.isfinite(ang):
                ang = np.pi / 2
            off = 26
            ax.annotate(f"{int(r['pos'])} m", (r["x"], r["y"]), textcoords="offset points",
                        xytext=(off * np.cos(ang), off * np.sin(ang)),
                        ha="center", va="center", fontsize=8.5, fontweight="bold", color="white",
                        zorder=5, arrowprops=dict(arrowstyle="-", color="white", lw=.7, alpha=.7),
                        bbox=dict(boxstyle="round,pad=0.18", fc="black", ec="none", alpha=.6))

    # tight bounds + padding
    pad = 35
    ax.set_xlim(g["x"].min() - pad, g["x"].max() + pad)
    ax.set_ylim(g["y"].min() - pad, g["y"].max() + pad)
    cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery, zoom=18, attribution=False)

    # scale bar (we are on the equator, so mercator metres ≈ ground metres)
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    bar = 50.0
    bx = x0 + (x1 - x0) * 0.06; by = y0 + (y1 - y0) * 0.06
    ax.plot([bx, bx + bar], [by, by], color="white", lw=3, solid_capstyle="butt", zorder=6)
    ax.text(bx + bar / 2, by + (y1 - y0) * 0.012, "50 m", ha="center", va="bottom",
            color="white", fontsize=9, fontweight="bold", zorder=6)
    # north arrow
    nax = x1 - (x1 - x0) * 0.07; nay = y1 - (y1 - y0) * 0.14
    ax.add_patch(FancyArrowPatch((nax, nay), (nax, nay + (y1 - y0) * 0.09),
                 arrowstyle="-|>", mutation_scale=18, color="white", lw=2.2, zorder=6))
    ax.text(nax, nay + (y1 - y0) * 0.10, "N", ha="center", va="bottom",
            color="white", fontsize=12, fontweight="bold", zorder=6)

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Recorder sampling design — Tandayapa Cloud Forest Station, Ecuador\n"
                 "AudioMoth transects in forest vs pasture · points to scale at 0, 15, 30, 60, 120 m",
                 fontsize=12, fontweight="bold", pad=10)
    leg = ax.legend(loc="lower right", framealpha=.85, fontsize=10)
    leg.set_zorder(7)
    ax.text(0.01, 0.01, "Imagery © Esri, Maxar, Earthstar Geographics",
            transform=ax.transAxes, fontsize=7, color="white", alpha=.8, va="bottom")

    # locator inset (Ecuador), top-left over empty canopy
    iax = fig.add_axes([0.135, 0.6, 0.18, 0.18])
    ex, ey = merc([-81.5, -75], [-5.5, 1.8])
    iax.set_xlim(ex); iax.set_ylim(ey)
    cx.add_basemap(iax, source=cx.providers.Esri.WorldShadedRelief, attribution=False)
    px, py = merc(clon, clat)
    iax.plot(px, py, marker="*", color="#F2542D", ms=15, mec="white", mew=.8)
    iax.set_xticks([]); iax.set_yticks([])
    for s in iax.spines.values():
        s.set_edgecolor("white"); s.set_linewidth(1.2)
    iax.set_title("Ecuador", fontsize=8, color="white", backgroundcolor="#0008", pad=2)

    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"wrote {OUT}")
    if len(dropped):
        print("dropped anomalous GPS reads:", list(dropped["canonical_point"]))


if __name__ == "__main__":
    main()
