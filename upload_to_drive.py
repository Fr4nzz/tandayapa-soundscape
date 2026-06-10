#!/usr/bin/env python3
"""Upload all AudioMoth device folders to Google Drive via gog, preserving the
per-device subfolder structure. Resumable: skips files already present in Drive.
Stops cleanly if the storage quota is exceeded."""
import os, re, sys, glob, json, subprocess

ROOT = r"d:\Audiomoths"
TOP_NAME = "Tandayapa_audio"
ACCOUNT = "franz.chandi@gmail.com"
FOLDER_MIME = "application/vnd.google-apps.folder"

# --- env: keyring password + account (so gog runs non-interactively) ---------
pw = os.path.join(os.environ.get("APPDATA", ""), "gogcli", ".hermes-keyring-password")
if os.path.exists(pw):
    os.environ["GOG_KEYRING_PASSWORD"] = open(pw).read().strip()
os.environ["GOG_ACCOUNT"] = ACCOUNT

def gog_json(args):
    r = subprocess.run(["gog"] + args, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return None

def gog_run(args):
    r = subprocess.run(["gog"] + args, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def children(parent):
    args = ["drive", "ls", "--json", "--results-only", "--max", "1000"]
    if parent:
        args += ["--parent", parent]
    d = gog_json(args)
    return d if isinstance(d, list) else []

def ensure_folder(name, parent=None):
    for f in children(parent):
        if f.get("name") == name and f.get("mimeType") == FOLDER_MIME:
            return f["id"]
    args = ["drive", "mkdir", name, "--json", "--results-only"]
    if parent:
        args += ["--parent", parent]
    d = gog_json(args)
    if not d or "id" not in d:
        sys.exit(f"FATAL: could not create folder {name!r}")
    return d["id"]

def main():
    top = ensure_folder(TOP_NAME)
    print(f"Drive folder '{TOP_NAME}' = {top}", flush=True)
    dirs = sorted(d for d in os.listdir(ROOT)
                  if re.match(r"^[FP]\d+_A", d) and os.path.isdir(os.path.join(ROOT, d)))
    up = skip = 0
    for d in dirs:
        # dedupe by lowercased basename (Windows glob is case-insensitive, so
        # *.WAV and *.wav would otherwise return the same files twice)
        _seen = {}
        for _w in (glob.glob(os.path.join(ROOT, d, "*.WAV")) +
                   glob.glob(os.path.join(ROOT, d, "*.wav"))):
            _seen[os.path.basename(_w).lower()] = _w
        wavs = sorted(_seen.values())
        if not wavs:
            print(f"skip empty: {d}", flush=True)
            continue
        sub = ensure_folder(d, top)
        have = {f["name"] for f in children(sub)}
        todo = [w for w in wavs if os.path.basename(w) not in have]
        print(f">>> {d}: {len(wavs)} files, {len(have)} on Drive, {len(todo)} to send", flush=True)
        cfg = os.path.join(ROOT, d, "CONFIG.TXT")
        if os.path.exists(cfg) and "CONFIG.TXT" not in have:
            todo.append(cfg)
        for w in todo:
            rc, out, err = gog_run(["drive", "upload", w, "--parent", sub])
            if rc != 0:
                blob = (out + err).lower()
                if "quota" in blob or "storagequota" in blob:
                    print("!!! STORAGE QUOTA EXCEEDED. Stopping. "
                          f"(uploaded={up} so far). Use Google One or FLAC-compress.", flush=True)
                    sys.exit(2)
                print(f"  FAIL {os.path.basename(w)}: {err.strip()[:140]}", flush=True)
            else:
                up += 1
                if up % 20 == 0:
                    print(f"  ...{up} uploaded (in {d})", flush=True)
        skip += len(have)
    print(f"ALL DONE. uploaded={up}, skipped_existing={skip}", flush=True)

if __name__ == "__main__":
    main()
