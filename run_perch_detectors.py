#!/usr/bin/env python3
"""Run trained Perch+logistic frog/insect detectors over AudioMoth WAV files.

Outputs one row per 5-second Perch window with frog/insect probabilities.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import joblib
import librosa
import numpy as np
import pandas as pd
import soundfile as sf
from tqdm import tqdm
from perch_hoplite.zoo import model_configs


def is_device_wav(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    if len(rel.parts) < 2:
        return False
    # Real AudioMoth folders are named like F1501_A07, P3002_A04_6julio, etc.
    top = rel.parts[0]
    return (top.startswith("F") or top.startswith("P")) and "_A" in top and path.suffix.lower() == ".wav"


def load_audio_mono(path: Path, target_sr: int) -> np.ndarray:
    audio, sr = sf.read(path, dtype="float32", always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
    return np.asarray(audio, dtype=np.float32)


def positive_proba(model, embeddings: np.ndarray, positive_label: str) -> np.ndarray:
    classes = list(model.classes_)
    if positive_label not in classes:
        raise ValueError(f"{positive_label=} not in model.classes_={classes}")
    idx = classes.index(positive_label)
    return model.predict_proba(embeddings)[:, idx]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-root", default="data/audiomoths")
    ap.add_argument("--output-dir", default="outputs/perch_audiomoth_detections")
    ap.add_argument("--frog-model", default="outputs/perch_reference_models/frog_detector_perch_logreg.joblib")
    ap.add_argument("--insect-model", default="outputs/perch_reference_models_relaxed_insect/insect_detector_perch_logreg.joblib")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of WAV files for smoke/benchmark runs")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--threshold", type=float, default=0.50)
    ap.add_argument("--include-non-device", action="store_true", help="Also process WAVs outside F*/P* device folders")
    args = ap.parse_args()

    root = Path(args.audio_root)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    wavs = sorted(p for p in root.rglob("*.WAV")) + sorted(p for p in root.rglob("*.wav"))
    if not args.include_non_device:
        wavs = [p for p in wavs if is_device_wav(p, root)]
    if args.limit:
        wavs = wavs[: args.limit]
    if not wavs:
        raise SystemExit(f"No WAV files found under {root}")

    print(f"Loading Perch v2 CPU embedding model...")
    t0 = time.time()
    perch = model_configs.load_model_by_name("perch_v2_cpu")
    print(f"Loaded Perch sample_rate={perch.sample_rate} window={perch.window_size_s}s in {time.time()-t0:.1f}s")

    frog_model = joblib.load(args.frog_model)
    insect_model = joblib.load(args.insect_model)

    rows_path = outdir / ("window_scores_sample.csv" if args.limit else "window_scores.csv")
    summary_path = outdir / ("summary_sample.json" if args.limit else "summary.json")

    total_windows = 0
    file_summaries = []
    errors = []
    t_proc = time.time()

    with rows_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file", "device", "window_index", "start_s", "end_s",
                "frog_prob", "insect_prob", "frog_hit", "insect_hit",
            ],
        )
        writer.writeheader()
        for wav in tqdm(wavs, desc="AudioMoth files"):
            rel = wav.relative_to(root)
            device = rel.parts[0]
            try:
                audio = load_audio_mono(wav, perch.sample_rate)
                frames = perch.frame_audio(audio, perch.window_size_s, perch.hop_size_s)
                n = int(frames.shape[0])
                frog_probs_all = []
                insect_probs_all = []
                for i in range(0, n, args.batch_size):
                    batch = frames[i : i + args.batch_size]
                    emb_out = perch.batch_embed(batch)
                    emb = emb_out.pooled_embeddings("squeeze", "squeeze")
                    if emb.ndim == 1:
                        emb = emb.reshape(1, -1)
                    frog_probs_all.append(positive_proba(frog_model, emb, "frog"))
                    insect_probs_all.append(positive_proba(insect_model, emb, "insect"))
                frog_probs = np.concatenate(frog_probs_all) if frog_probs_all else np.array([])
                insect_probs = np.concatenate(insect_probs_all) if insect_probs_all else np.array([])
                for j, (fp, ip) in enumerate(zip(frog_probs, insect_probs)):
                    start_s = j * float(perch.hop_size_s)
                    end_s = start_s + float(perch.window_size_s)
                    writer.writerow({
                        "file": str(rel),
                        "device": device,
                        "window_index": j,
                        "start_s": round(start_s, 3),
                        "end_s": round(end_s, 3),
                        "frog_prob": float(fp),
                        "insect_prob": float(ip),
                        "frog_hit": int(fp >= args.threshold),
                        "insect_hit": int(ip >= args.threshold),
                    })
                total_windows += n
                file_summaries.append({
                    "file": str(rel),
                    "device": device,
                    "windows": n,
                    "duration_s": round(len(audio) / perch.sample_rate, 3),
                    "max_frog_prob": float(frog_probs.max()) if len(frog_probs) else None,
                    "max_insect_prob": float(insect_probs.max()) if len(insect_probs) else None,
                    "frog_hits": int((frog_probs >= args.threshold).sum()),
                    "insect_hits": int((insect_probs >= args.threshold).sum()),
                })
            except Exception as e:  # keep batch runs going
                errors.append({"file": str(rel), "error": type(e).__name__, "message": str(e)})

    elapsed = time.time() - t_proc
    summary = {
        "audio_root": str(root),
        "n_files": len(wavs),
        "n_ok_files": len(file_summaries),
        "n_error_files": len(errors),
        "total_windows": total_windows,
        "elapsed_s_excluding_model_load": elapsed,
        "windows_per_s": total_windows / elapsed if elapsed else None,
        "files_per_s": len(file_summaries) / elapsed if elapsed else None,
        "threshold": args.threshold,
        "rows_csv": str(rows_path),
        "top_frog_files": sorted(file_summaries, key=lambda x: x["max_frog_prob"] or -1, reverse=True)[:20],
        "top_insect_files": sorted(file_summaries, key=lambda x: x["max_insect_prob"] or -1, reverse=True)[:20],
        "errors": errors[:50],
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    # Convenience ranked CSVs.
    if file_summaries:
        df = pd.DataFrame(file_summaries)
        df.sort_values(["max_frog_prob", "frog_hits"], ascending=False).to_csv(outdir / ("ranked_frog_files_sample.csv" if args.limit else "ranked_frog_files.csv"), index=False)
        df.sort_values(["max_insect_prob", "insect_hits"], ascending=False).to_csv(outdir / ("ranked_insect_files_sample.csv" if args.limit else "ranked_insect_files.csv"), index=False)

    print(json.dumps(summary, indent=2)[:4000])


if __name__ == "__main__":
    main()
