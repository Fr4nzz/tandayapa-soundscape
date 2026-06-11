#!/usr/bin/env python3
"""Audit Tandayapa GPS waypoints for possible mislabels.

This is intentionally diagnostic, not a publication map. It keeps the raw
coordinates visible and flags points whose raw GPS location contradicts the
nominal transect labels.

Outputs:
  outputs/analysis/gps_waypoint_audit.csv
  outputs/analysis/gps_waypoint_pairwise_distances.csv
  outputs/analysis/gps_waypoint_raw_labeled.png
"""
from __future__ import annotations

from pathlib import Path
import itertools
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GPS = ROOT / "data" / "raw" / "gps" / "tandayapa_gps_waypoints.csv"
OUTDIR = ROOT / "outputs" / "analysis"
OUTDIR.mkdir(parents=True, exist_ok=True)


def local_xy(df: pd.DataFrame) -> pd.DataFrame:
    """Approximate local metres around the equator/Tandayapa."""
    lat0 = df["lat_dd"].median()
    lon0 = df["lon_dd"].median()
    out = df.copy()
    out["x_m"] = (out["lon_dd"] - lon0) * 111320 * np.cos(np.radians(lat0))
    out["y_m"] = (out["lat_dd"] - lat0) * 110570
    return out


def add_flags(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        flags: list[str] = []
        if r["canonical_point"] == "?" or pd.isna(r["nominal_position_m"]):
            flags.append("unresolved label/position")
        if isinstance(r.get("notes"), str) and "REMOVED" in r["notes"]:
            flags.append("REMOVED from map")
        d = dict(r)
        d["audit_flags"] = "; ".join(flags)
        rows.append(d)
    return pd.DataFrame(rows)


def pairwise(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for hab, d in df.groupby("habitat"):
        for ia, ib in itertools.combinations(d.index, 2):
            a, b = d.loc[ia], d.loc[ib]
            dist = math.hypot(a.x_m - b.x_m, a.y_m - b.y_m)
            rows.append({
                "habitat": hab,
                "a": a.raw_label,
                "a_canonical": a.canonical_point,
                "b": b.raw_label,
                "b_canonical": b.canonical_point,
                "distance_m": round(dist, 1),
            })
    return pd.DataFrame(rows).sort_values(["habitat", "distance_m"])


def raw_plot(df: pd.DataFrame, out: Path) -> None:
    colors = {"forest": "#39B54A", "pasture": "#F2C14E"}
    fig, ax = plt.subplots(figsize=(8, 7))
    for hab, d in df.groupby("habitat"):
        ax.scatter(d.x_m, d.y_m, s=90, c=colors[hab], edgecolor="black", label=hab, zorder=3)
        for _, r in d.iterrows():
            flag = " ⚠" if r.audit_flags else ""
            label = f"{r.raw_label}\n{r.canonical_point}{flag}"
            ax.annotate(label, (r.x_m, r.y_m), xytext=(6, 6), textcoords="offset points",
                        fontsize=8, bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=.75, ec="none"))
    ax.axhline(0, color="0.85", lw=.8)
    ax.axvline(0, color="0.85", lw=.8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("east-west offset from dataset median (m)")
    ax.set_ylabel("north-south offset from dataset median (m)")
    ax.set_title("Raw GPS waypoint audit — labels shown exactly from CSV")
    ax.legend()
    ax.grid(True, color="0.9", lw=.6)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(GPS)
    df = local_xy(df)
    audited = add_flags(df)
    pw = pairwise(audited)
    audited.to_csv(OUTDIR / "gps_waypoint_audit.csv", index=False)
    pw.to_csv(OUTDIR / "gps_waypoint_pairwise_distances.csv", index=False)
    raw_plot(audited, OUTDIR / "gps_waypoint_raw_labeled.png")
    print("wrote", OUTDIR / "gps_waypoint_audit.csv")
    print("wrote", OUTDIR / "gps_waypoint_pairwise_distances.csv")
    print("wrote", OUTDIR / "gps_waypoint_raw_labeled.png")
    print("\nFlagged rows:")
    cols = ["raw_label", "habitat", "canonical_point", "nominal_position_m", "lat_dd", "lon_dd", "elev_m_gps", "audit_flags"]
    flagged = audited[audited.audit_flags.astype(bool)][cols]
    print(flagged.to_string(index=False))


if __name__ == "__main__":
    main()
