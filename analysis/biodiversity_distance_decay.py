#!/usr/bin/env python3
"""Tandayapa recorder-spacing study — biodiversity (species-community) analysis.

Research question: does the SPECIES COMMUNITY recorded by two AudioMoths become
more different as the distance between them grows, and is that distance-decay
steeper in forest than in pasture?

Response = pairwise community dissimilarity (Bray-Curtis on detection abundance,
Jaccard on presence) between two within-habitat recorders in the same deployment.
Predictor = nominal inter-recorder distance (spacing x |point_i - point_j|).
Replication = each spacing (15/30/60 m) was deployed on TWO separate days -> the
deploy day is a replicate block (random factor in the R/lme4 model).

This Python version computes the real numbers + figures for the report using
.venv-perch (pandas/scipy/matplotlib). The companion R script
(analysis/biodiversity_distance_decay.R) reproduces it with vegan + lme4.

Run:  .venv-perch/bin/python analysis/biodiversity_distance_decay.py
"""
from __future__ import annotations

import csv
import json
import os
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "outputs" / "web"
OUT = ROOT / "outputs" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

CONF_MIN = float(os.environ.get("CONF_MIN", "0.5"))   # reliability threshold (override via env)
RNG = np.random.default_rng(20260610)
N_PERM = 5000

# --- authoritative deploy -> recorder mapping (from tandayapa_common.R DEVICES) ---
# device folder : (deploy, habitat, point)
DEVICES = {
    # day1 15 m
    "F1501_A05": ("day1", "forest", 1), "F1502_A06": ("day1", "forest", 2), "F1503_A08": ("day1", "forest", 3),
    "P1501_A04": ("day1", "pasture", 1), "P1502_A01": ("day1", "pasture", 2), "P1503_A02": ("day1", "pasture", 3),
    # day2 30 m
    "F3001_A01": ("day2", "forest", 1), "F3002_A05": ("day2", "forest", 2), "F3003_A07": ("day2", "forest", 3),
    "P3001_A06": ("day2", "pasture", 1), "P3002_A04": ("day2", "pasture", 2),
    # day3 60 m
    "F6002_A03": ("day3", "forest", 2), "F6003_A05": ("day3", "forest", 3), "P6002_A02": ("day3", "pasture", 2),
    # day4 15 m
    "F1501_A07": ("day4", "forest", 1), "F1502_A01": ("day4", "forest", 2),
    "P1501_A02": ("day4", "pasture", 1), "P1502_A05": ("day4", "pasture", 2), "P1503_A03": ("day4", "pasture", 3),
    # day5 30 m
    "F3001_A02": ("day5", "forest", 1), "F3002_A03": ("day5", "forest", 2), "F3003_A01": ("day5", "forest", 3),
    "P3001_A05": ("day5", "pasture", 1), "P3002_A04_6julio": ("day5", "pasture", 2), "P3003_A06": ("day5", "pasture", 3),
    # day6 60 m
    "F6002_A05": ("day6", "forest", 2), "F6003_A06": ("day6", "forest", 3),
    "P6001_A02": ("day6", "pasture", 1), "P6003_A01": ("day6", "pasture", 3),
}
DAY_SPACING = {"day1": 15, "day2": 30, "day3": 60, "day4": 15, "day5": 30, "day6": 60}


def load_excluded():
    f = ROOT / "data" / "excluded_frog_taxa.csv"
    if not f.exists():
        return set()
    return {r["species"] for r in csv.DictReader(open(f))}


def load_detections():
    excl = load_excluded()
    rows = []
    dropped = unmatched = 0
    for p in sorted(WEB.glob("day*.json")):
        for d in json.load(open(p)):
            dev = d["audio"].strip("/").split("/")[0]
            meta = DEVICES.get(dev)
            if meta is None:
                unmatched += 1
                continue
            if d["species"] in excl:
                dropped += 1
                continue
            if d.get("conf", 1) < CONF_MIN:
                continue
            deploy, habitat, point = meta
            rows.append({
                "deploy": deploy, "habitat": habitat, "point": point,
                "spacing": DAY_SPACING[deploy], "device": dev,
                "group": d["group"], "species": d["species"], "conf": d["conf"],
            })
    df = pd.DataFrame(rows)
    print(f"  detections kept: {len(df)} (dropped {dropped} excluded-frog rows; "
          f"{unmatched} from non-study/backup files; conf>= {CONF_MIN})")
    return df


def bray_curtis(a: np.ndarray, b: np.ndarray) -> float:
    s = a.sum() + b.sum()
    return float(np.abs(a - b).sum() / s) if s else np.nan


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    A, B = a > 0, b > 0
    u = (A | B).sum()
    return float(1 - (A & B).sum() / u) if u else np.nan


def community_vectors(df: pd.DataFrame):
    """(deploy, habitat, point) -> species-count vector over the global species list."""
    species = sorted(df["species"].unique())
    idx = {s: i for i, s in enumerate(species)}
    comm = {}
    for (deploy, habitat, point), g in df.groupby(["deploy", "habitat", "point"]):
        v = np.zeros(len(species))
        for s, c in g["species"].value_counts().items():
            v[idx[s]] = c
        comm[(deploy, habitat, point)] = v
    return comm, species


def pairwise_table(comm):
    recs = {}
    for (deploy, habitat, point) in comm:
        recs.setdefault((deploy, habitat), []).append(point)
    rows = []
    for (deploy, habitat), pts in recs.items():
        for pi, pj in combinations(sorted(pts), 2):
            a, b = comm[(deploy, habitat, pi)], comm[(deploy, habitat, pj)]
            dist = DAY_SPACING[deploy] * abs(pi - pj)
            rows.append({
                "deploy": deploy, "habitat": habitat, "spacing": DAY_SPACING[deploy],
                "point_i": pi, "point_j": pj, "distance_m": dist,
                "bray_curtis": bray_curtis(a, b), "jaccard": jaccard(a, b),
                "n_sp_i": int((a > 0).sum()), "n_sp_j": int((b > 0).sum()),
            })
    return pd.DataFrame(rows).sort_values(["habitat", "distance_m"]).reset_index(drop=True)


def slope_effect(x, y, n=N_PERM):
    """Effect size for y ~ x: slope (+95% CI), R^2, standardized beta, perm-p.

    The slope IS the effect size (change in dissimilarity per metre). We add the
    parametric 95% CI, R^2 (variance explained), the standardized slope (per SD of
    distance), and a permutation p (secondary)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    lr = sstats.linregress(x, y)                       # slope, intercept, r, p, stderr
    t = sstats.t.ppf(0.975, len(x) - 2)
    ci = (lr.slope - t * lr.stderr, lr.slope + t * lr.stderr)
    beta = lr.slope * (x.std(ddof=1) / y.std(ddof=1))  # standardized slope
    count = 0
    for _ in range(n):
        if abs(np.polyfit(x, RNG.permutation(y), 1)[0]) >= abs(lr.slope):
            count += 1
    return dict(slope=lr.slope, ci_lo=ci[0], ci_hi=ci[1], r2=lr.rvalue**2,
                beta=beta, perm_p=(count + 1) / (n + 1), n=len(x))


def interaction_effect(df, ycol):
    """Effect size of H2: forest-minus-pasture difference in distance slope, with 95% CI.
    OLS y ~ distance + forest + distance:forest (forest=1). The interaction coefficient
    is the slope difference; its 95% CI is the honest effect-size statement for H2."""
    d = df.copy()
    d["forest"] = (d.habitat == "forest").astype(float)
    X = np.column_stack([np.ones(len(d)), d.distance_m, d.forest, d.distance_m * d.forest])
    y = d[ycol].to_numpy(float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    sigma2 = (resid @ resid) / dof
    cov = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(cov[3, 3])
    t = sstats.t.ppf(0.975, dof)
    diff = beta[3]
    return dict(diff_per_m=diff, ci_lo=diff - t * se, ci_hi=diff + t * se, dof=dof)


def interaction_perm(df, ycol, n=N_PERM):
    """Difference in distance slope between forest and pasture, permutation test.
    Null: habitat label is exchangeable -> permute habitat across pairs."""
    def diff(d):
        sf = np.polyfit(d[d.habitat == "forest"]["distance_m"], d[d.habitat == "forest"][ycol], 1)[0]
        sp = np.polyfit(d[d.habitat == "pasture"]["distance_m"], d[d.habitat == "pasture"][ycol], 1)[0]
        return sf - sp
    obs = diff(df)
    hab = df["habitat"].values.copy()
    count = 0
    for _ in range(n):
        dperm = df.copy(); dperm["habitat"] = RNG.permutation(hab)
        try:
            if abs(diff(dperm)) >= abs(obs):
                count += 1
        except Exception:
            pass
    return obs, (count + 1) / (n + 1)


def main():
    print("Loading detections ...")
    df = load_detections()

    # --- descriptive richness ---
    rich = (df.groupby(["habitat", "group"])["species"].nunique().unstack(fill_value=0))
    rich["TOTAL"] = df.groupby("habitat")["species"].nunique()
    rich.to_csv(OUT / "richness_by_habitat.csv")
    print("\nRichness by habitat x group:\n", rich)

    comm, species = community_vectors(df)
    print(f"\nSamples (deploy x habitat x point): {len(comm)} ; total species: {len(species)}")

    pw = pairwise_table(comm)
    pw.to_csv(OUT / "pairwise_dissimilarity.csv", index=False)
    print(f"\nWithin-habitat recorder pairs: {len(pw)} "
          f"(forest {sum(pw.habitat=='forest')}, pasture {sum(pw.habitat=='pasture')})")
    print("Distances sampled (m):", sorted(pw.distance_m.unique()))

    # --- EFFECT SIZES (lead) + permutation p (secondary) ---
    label = {"bray_curtis": "Bray-Curtis", "jaccard": "Jaccard"}
    rows_es, lines = [], []
    for ycol in ["bray_curtis", "jaccard"]:
        lines.append(f"\n===== {label[ycol]} =====")
        for hab in ["forest", "pasture"]:
            d = pw[pw.habitat == hab]
            e = slope_effect(d["distance_m"], d[ycol])
            rows_es.append(dict(metric=label[ycol], term=hab, n=e["n"],
                slope_per10m=round(e["slope"]*10, 4),
                ci95_lo=round(e["ci_lo"]*10, 4), ci95_hi=round(e["ci_hi"]*10, 4),
                R2=round(e["r2"], 3), std_beta=round(e["beta"], 3), perm_p=round(e["perm_p"], 4)))
            lines.append(f"  {hab:8} n={e['n']:2d}  Δdissim/+10m = {e['slope']*10:+.4f} "
                         f"[95% CI {e['ci_lo']*10:+.4f}, {e['ci_hi']*10:+.4f}]  "
                         f"R²={e['r2']:.3f}  std-β={e['beta']:+.3f}  (perm-p={e['perm_p']:.4f})")
        ie = interaction_effect(pw, ycol)
        _, pint = interaction_perm(pw, ycol)
        inc0 = ie["ci_lo"] <= 0 <= ie["ci_hi"]
        rows_es.append(dict(metric=label[ycol], term="forest-minus-pasture (H2)", n=len(pw),
            slope_per10m=round(ie["diff_per_m"]*10, 4),
            ci95_lo=round(ie["ci_lo"]*10, 4), ci95_hi=round(ie["ci_hi"]*10, 4),
            R2=np.nan, std_beta=np.nan, perm_p=round(pint, 4)))
        lines.append(f"  H2 forest−pasture slope diff/+10m = {ie['diff_per_m']*10:+.4f} "
                     f"[95% CI {ie['ci_lo']*10:+.4f}, {ie['ci_hi']*10:+.4f}]  (perm-p={pint:.4f})  "
                     f"-> CI {'INCLUDES 0 (H2 not supported)' if inc0 else 'excludes 0'}")
    es = pd.DataFrame(rows_es)
    es.to_csv(OUT / "effect_sizes.csv", index=False)
    summary = "\n".join(lines)
    print(summary)
    (OUT / "model_summary.txt").write_text(
        f"CONF_MIN={CONF_MIN}  n_perm={N_PERM}\n"
        f"Samples={len(comm)}  species={len(species)}  pairs={len(pw)}\n"
        "Effect size = slope (Δ dissimilarity per +10 m) with 95% CI; R² = variance explained;\n"
        "std-β = slope per 1 SD of distance. H2 effect = forest−pasture slope difference + 95% CI.\n"
        + summary + "\n\nNOTE: formal random-effects model (dissim ~ distance*habitat + (1|deploy))"
        " + its CIs/R² are in analysis/biodiversity_distance_decay.R (lme4). Python leads with"
        " effect sizes + 95% CIs; permutation p is secondary.\n")

    # --- figures ---
    figs = []
    # 1. distance-decay (Bray-Curtis) by habitat
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    colors = {"forest": "#2C5F2D", "pasture": "#D9A441"}
    for hab in ["forest", "pasture"]:
        d = pw[pw.habitat == hab]
        ax.scatter(d.distance_m + (1.5 if hab == "pasture" else -1.5), d.bray_curtis,
                   s=46, color=colors[hab], alpha=.8, edgecolor="white", linewidth=.6, label=hab, zorder=3)
        xs = np.linspace(pw.distance_m.min(), pw.distance_m.max(), 50)
        b1, b0 = np.polyfit(d.distance_m, d.bray_curtis, 1)
        ax.plot(xs, b0 + b1 * xs, color=colors[hab], lw=2)
    ax.set_xlabel("Distance between recorders (m)"); ax.set_ylabel("Community dissimilarity (Bray-Curtis)")
    ax.set_title("Acoustic community distance-decay · forest vs pasture")
    ax.legend(frameon=False); ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(OUT / "fig1_distance_decay_braycurtis.png", dpi=150); figs.append("fig1")

    # 2. same for Jaccard
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for hab in ["forest", "pasture"]:
        d = pw[pw.habitat == hab]
        ax.scatter(d.distance_m + (1.5 if hab == "pasture" else -1.5), d.jaccard,
                   s=46, color=colors[hab], alpha=.8, edgecolor="white", linewidth=.6, label=hab, zorder=3)
        xs = np.linspace(pw.distance_m.min(), pw.distance_m.max(), 50)
        b1, b0 = np.polyfit(d.distance_m, d.jaccard, 1)
        ax.plot(xs, b0 + b1 * xs, color=colors[hab], lw=2)
    ax.set_xlabel("Distance between recorders (m)"); ax.set_ylabel("Community dissimilarity (Jaccard, presence)")
    ax.set_title("Species turnover with distance · forest vs pasture")
    ax.legend(frameon=False); ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(OUT / "fig2_distance_decay_jaccard.png", dpi=150); figs.append("fig2")

    # 3. richness by habitat x group
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    groups = [g for g in ["bird", "frog", "insect"] if g in rich.columns]
    x = np.arange(len(groups)); w = .38
    for i, hab in enumerate(["forest", "pasture"]):
        ax.bar(x + (i - .5) * w, [rich.loc[hab, g] for g in groups], w, color=colors[hab], label=hab)
    ax.set_xticks(x); ax.set_xticklabels([g.capitalize() for g in groups])
    ax.set_ylabel("Species richness"); ax.set_title("Species richness by habitat")
    ax.legend(frameon=False); ax.grid(alpha=.25, axis="y"); fig.tight_layout()
    fig.savefig(OUT / "fig3_richness_by_habitat.png", dpi=150); figs.append("fig3")

    print(f"\nWrote: richness_by_habitat.csv, pairwise_dissimilarity.csv, model_summary.txt, "
          f"{', '.join(f+'.png' for f in figs)}  -> {OUT}")


if __name__ == "__main__":
    main()
