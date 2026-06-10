#!/usr/bin/env python3
"""Acoustic-index distance-decay + comparison with the BirdNET biodiversity result.

Asks the SAME research question with cheap acoustic indices (ACI, BI, ADI): do two
recorders give more DIFFERENT index values as the distance between them grows, and
is that steeper in forest than pasture? Then compares the index-based answer with
the species-community (BirdNET) answer from biodiversity_distance_decay.py.

Response per within-habitat recorder pair:
  - |ACI_i - ACI_j|, |BI_i - BI_j|, |ADI_i - ADI_j|  (per-index)
  - 'acoustic dissimilarity' = Euclidean distance on z-scored (ACI,BI,ADI)  (combined)
Predictor: nominal inter-recorder distance.

Reads outputs/analysis/acoustic_indices.csv (from compute_acoustic_indices.py).
Writes outputs/analysis/index_effect_sizes.csv + figures + a comparison vs the
community result (outputs/analysis/effect_sizes.csv).

Run: .venv-perch/bin/python analysis/index_distance_decay.py
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "analysis"
IDX = OUT / "acoustic_indices.csv"
COLS = {"forest": "#2C5F2D", "pasture": "#D9A441"}


def slope_effect(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    lr = sstats.linregress(x, y)
    t = sstats.t.ppf(0.975, len(x) - 2)
    return dict(slope=lr.slope, ci_lo=lr.slope - t*lr.stderr, ci_hi=lr.slope + t*lr.stderr,
                r2=lr.rvalue**2, n=len(x))


def interaction_effect(df, ycol):
    d = df.copy(); d["forest"] = (d.habitat == "forest").astype(float)
    X = np.column_stack([np.ones(len(d)), d.distance_m, d.forest, d.distance_m*d.forest])
    y = d[ycol].to_numpy(float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X@beta; dof = len(y) - X.shape[1]
    cov = (resid@resid)/dof * np.linalg.inv(X.T@X); se = np.sqrt(cov[3, 3])
    t = sstats.t.ppf(0.975, dof)
    return dict(diff=beta[3], ci_lo=beta[3]-t*se, ci_hi=beta[3]+t*se)


def main():
    if not IDX.exists():
        raise SystemExit(f"missing {IDX} — run compute_acoustic_indices.py first")
    idx = pd.read_csv(IDX)
    # z-score the indices for the combined 'acoustic dissimilarity'
    for c in ["ACI", "BI", "ADI"]:
        idx[c + "_z"] = (idx[c] - idx[c].mean()) / idx[c].std(ddof=1)

    # within-habitat recorder pairs
    rows = []
    for (deploy, habitat), g in idx.groupby(["deploy", "habitat"]):
        g = g.set_index("point")
        for pi, pj in combinations(sorted(g.index), 2):
            a, b = g.loc[pi], g.loc[pj]
            dist = a["spacing"] * abs(pi - pj)
            acoustic_diss = float(np.sqrt(sum((a[c+"_z"]-b[c+"_z"])**2 for c in ["ACI","BI","ADI"])))
            rows.append(dict(deploy=deploy, habitat=habitat, distance_m=dist,
                dACI=abs(a.ACI-b.ACI), dBI=abs(a.BI-b.BI), dADI=abs(a.ADI-b.ADI),
                acoustic_diss=acoustic_diss))
    pw = pd.DataFrame(rows)
    pw.to_csv(OUT / "index_pairwise.csv", index=False)
    print(f"index pairs: {len(pw)} (forest {sum(pw.habitat=='forest')}, pasture {sum(pw.habitat=='pasture')})")
    print("distances:", sorted(pw.distance_m.unique()))

    # effect sizes per metric
    es_rows, lines = [], []
    metrics = [("dACI", "|ACI diff|"), ("dBI", "|BI diff|"), ("dADI", "|ADI diff|"),
               ("acoustic_diss", "acoustic dissimilarity (z, ACI+BI+ADI)")]
    for col, lab in metrics:
        lines.append(f"\n===== {lab} =====")
        for hab in ["forest", "pasture"]:
            d = pw[pw.habitat == hab]; e = slope_effect(d.distance_m, d[col])
            es_rows.append(dict(metric=lab, term=hab, n=e["n"],
                slope_per10m=round(e["slope"]*10,4), ci_lo=round(e["ci_lo"]*10,4),
                ci_hi=round(e["ci_hi"]*10,4), R2=round(e["r2"],3)))
            lines.append(f"  {hab:8} slope(+10m)={e['slope']*10:+.4f} "
                         f"[95% CI {e['ci_lo']*10:+.4f}, {e['ci_hi']*10:+.4f}]  R²={e['r2']:.3f}")
        ie = interaction_effect(pw, col)
        es_rows.append(dict(metric=lab, term="forest-minus-pasture (H2)", n=len(pw),
            slope_per10m=round(ie["diff"]*10,4), ci_lo=round(ie["ci_lo"]*10,4),
            ci_hi=round(ie["ci_hi"]*10,4), R2=np.nan))
        lines.append(f"  H2 diff(+10m)={ie['diff']*10:+.4f} [95% CI {ie['ci_lo']*10:+.4f}, {ie['ci_hi']*10:+.4f}]"
                     f" -> CI {'includes 0' if ie['ci_lo']<=0<=ie['ci_hi'] else 'excludes 0'}")
    es = pd.DataFrame(es_rows); es.to_csv(OUT / "index_effect_sizes.csv", index=False)
    summary = "\n".join(lines); print(summary)
    (OUT / "index_model_summary.txt").write_text(summary + "\n")

    # figure: acoustic dissimilarity (combined index) vs distance, by habitat
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for hab in ["forest", "pasture"]:
        d = pw[pw.habitat == hab]
        ax.scatter(d.distance_m + (1.5 if hab=="pasture" else -1.5), d.acoustic_diss,
                   s=46, color=COLS[hab], alpha=.8, edgecolor="white", linewidth=.6, label=hab, zorder=3)
        xs = np.linspace(pw.distance_m.min(), pw.distance_m.max(), 50)
        b1, b0 = np.polyfit(d.distance_m, d.acoustic_diss, 1); ax.plot(xs, b0+b1*xs, color=COLS[hab], lw=2)
    ax.set_xlabel("Distance between recorders (m)"); ax.set_ylabel("Acoustic-index dissimilarity (z, ACI+BI+ADI)")
    ax.set_title("Acoustic-INDEX distance-decay · forest vs pasture")
    ax.legend(frameon=False); ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(OUT / "fig4_index_distance_decay.png", dpi=150)

    # comparison vs community result, if present
    comm = OUT / "effect_sizes.csv"
    if comm.exists():
        c = pd.read_csv(comm)
        print("\n===== COMPARISON: index vs biodiversity (forest distance slope, per +10 m) =====")
        cf = c[(c.metric == "Jaccard") & (c.term == "forest")]
        if len(cf):
            print(f"  BirdNET community (Jaccard) forest: slope {cf.slope_per10m.iloc[0]:+.4f} "
                  f"[{cf.ci95_lo.iloc[0]:+.4f},{cf.ci95_hi.iloc[0]:+.4f}] R²={cf.R2.iloc[0]}")
        af = es[(es.metric.str.startswith('acoustic')) & (es.term == 'forest')]
        if len(af):
            print(f"  Acoustic-index (combined)  forest: slope {af.slope_per10m.iloc[0]:+.4f} "
                  f"[{af.ci_lo.iloc[0]:+.4f},{af.ci_hi.iloc[0]:+.4f}] R²={af.R2.iloc[0]}")
    print(f"\nwrote index_effect_sizes.csv, index_pairwise.csv, fig4_index_distance_decay.png -> {OUT}")


if __name__ == "__main__":
    main()
