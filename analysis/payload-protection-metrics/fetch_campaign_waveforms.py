#!/usr/bin/env python3
"""Fetch the BO-campaign drop waveforms from the public Box share.

The campaign's per-drop TP4 captures (100 ms at 1.25 MHz, CH2-CH4
top-vertex tri-axis, CH5 base-plate input) were never committed to git
(~20 GB); every session lives on the lab's public Box share under
``Drop Test Data``, the same share recorded by the ``box-ids.json``
manifests on the ``copilot/add-drop-test-protocol-again`` branch. This
script enumerates that share live (no login; the share is public),
selects the captures the payload-protection audit needs, and downloads
them to a scratch directory OUTSIDE the repo:

* every capture of the four 20-ish-drop check-in batches
  (r2d2c1-9, drran1-9, 2dran1-9, corny1-9);
* every signal of each 101-drop seed-batch session (``--seed-full``,
  the 2026-09-24 refinement asked for on PR #111; the original
  selection was the first 26 signal numbers, matching the check-in
  sample size), preferring the full/pm session where a specimen has an
  interrupted partial session (6lhxfy-s1, amdjwm-s1 are skipped).

``--seed-full`` upgrades a cached manifest in place: each seed
session's folder id is re-listed and its file map extended to all
signal numbers; check-in sessions are untouched. ``--only-batch seed``
restricts the download to the seed sessions (the check-in captures
feed rows of ``per-drop-payload-metrics.csv`` that are already
bit-exact against the committed drop-results tables and do not need
re-fetching).

Writes ``data/box-session-manifest.json`` (session folder name, Box
folder id, file name -> file id for the selected files) so the exact
inputs are reproducible, then downloads with a small thread pool and
verifies sizes.

Usage:
    python fetch_campaign_waveforms.py --dest /tmp/waveforms [--jobs 6]
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.cookiejar import CookieJar
from pathlib import Path

SHARED_NAME = "kkhmvnj9ni19b57dryk3gdroqrp5uf0b"  # umbrella share: tensegrity-optimization/
HOST = "byu.box.com"
APP_HOST = "byu.app.box.com"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "data" / "box-session-manifest.json"

# batch -> (session-folder regex under "Drop Test Data", specimen-folder regex,
#           max signal number to take, or None for all)
SEED_MAX_SIGNAL = 26
SESSIONS = {
    "seed": (r"^8-1[3-9]-2026|^8-2[01]-2026", None, SEED_MAX_SIGNAL),
    "r2d2c": (r"^8-24-2026 - r2d2c$", r"r2d2c\d", None),
    "drran": (r"^9-03-2026 - drran$", r"drran\d", None),
    "2dran": (r"^9-09-2026 - 2dran$", r"2dran\d", None),
    "corny": (r"^9-14-2026 - corny_$", r"corny\d", None),
}
# interrupted partial seed sessions to skip (the pm/full session is used)
SKIP_FOLDERS = re.compile(r"35 drops|87 drops|calibration")


def make_opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    return op


def get(opener, url, tries=4):
    for k in range(tries):
        try:
            with opener.open(url, timeout=180) as r:
                return r.read()
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


def page_data(opener, url):
    html = get(opener, url).decode("utf-8", "replace")
    i = html.find("Box.postStreamData = ")
    if i < 0:
        raise RuntimeError(f"no postStreamData at {url}")
    data, _ = json.JSONDecoder().raw_decode(html[i + len("Box.postStreamData = "):])
    return data


def list_folder(opener, folder_id):
    items, page, pages, name = [], 1, 1, None
    while page <= pages:
        d = page_data(opener,
                      f"https://{APP_HOST}/s/{SHARED_NAME}/folder/{folder_id}?page={page}")
        sf = d["/app-api/enduserapp/shared-folder"]
        pages = int(sf.get("pageCount") or 1)
        items.extend(sf["items"])
        name = sf.get("currentFolderName")
        page += 1
    return name, items


def signal_no(name: str):
    m = re.search(r"Signal(\d+)\.csv$", name)
    return int(m.group(1)) if m else None


def build_manifest(opener) -> dict:
    d = page_data(opener, f"https://{HOST}/s/{SHARED_NAME}")
    root_id = d["/app-api/enduserapp/shared-item"]["itemID"]
    _, root_items = list_folder(opener, root_id)
    dtd = next(it for it in root_items if it["name"] == "Drop Test Data")
    _, sess_items = list_folder(opener, dtd["id"])

    manifest = {"shared_name": SHARED_NAME, "host": HOST, "sessions": {}}
    for batch, (sess_re, spec_re, max_sig) in SESSIONS.items():
        for sess in sess_items:
            if sess["type"] != "folder" or not re.search(sess_re, str(sess["name"])):
                continue
            name, items = list_folder(opener, sess["id"])
            # seed sessions are one folder per specimen at Drop Test Data level,
            # except the 8-13..8-17 umbrella which nests one more level
            subfolders = [it for it in items if it["type"] == "folder"]
            leaves = [(name, sess["id"], items)]
            if subfolders:
                leaves = []
                for sub in subfolders:
                    if SKIP_FOLDERS.search(str(sub["name"])):
                        continue
                    if spec_re and not re.search(spec_re, str(sub["name"]), re.I):
                        continue
                    n2, it2 = list_folder(opener, sub["id"])
                    leaves.append((n2, sub["id"], it2))
                # files sitting next to the subfolders (series tables) are kept
                # with the parent only if it is itself a specimen session
            for leaf_name, leaf_id, leaf_items in leaves:
                if SKIP_FOLDERS.search(str(leaf_name)):
                    continue
                files = [it for it in leaf_items if it["type"] == "file"]
                sigs = sorted(((signal_no(str(f["name"])), f) for f in files
                               if signal_no(str(f["name"])) is not None),
                              key=lambda x: x[0])
                keep = [f for n, f in sigs if max_sig is None or n <= max_sig]
                series = [f for f in files if signal_no(str(f["name"])) is None
                          and str(f["name"]).lower().endswith(".csv")]
                if not keep:
                    continue
                manifest["sessions"][leaf_name] = {
                    "batch": batch, "folder_id": leaf_id,
                    "n_signals_available": len(sigs),
                    "files": {str(f["name"]): {"id": f["id"], "size": f.get("itemSize")}
                              for f in keep + series},
                }
    return manifest


def refresh_seed_full(opener, manifest) -> int:
    """Extend each cached seed session to all signal numbers, in place.

    Re-lists the session's Box folder by the id frozen in the manifest,
    so the selection stays tied to the same folders the original audit
    used; only the per-session file map grows.
    """
    added = 0
    for name, s in manifest["sessions"].items():
        if s["batch"] != "seed":
            continue
        _, items = list_folder(opener, s["folder_id"])
        files = [it for it in items if it["type"] == "file"]
        sigs = sorted(((signal_no(str(f["name"])), f) for f in files
                       if signal_no(str(f["name"])) is not None),
                      key=lambda x: x[0])
        series = [f for f in files if signal_no(str(f["name"])) is None
                  and str(f["name"]).lower().endswith(".csv")]
        before = len(s["files"])
        s["files"] = {str(f["name"]): {"id": f["id"], "size": f.get("itemSize")}
                      for _, f in sigs}
        s["files"].update({str(f["name"]): {"id": f["id"], "size": f.get("itemSize")}
                           for f in series})
        s["n_signals_available"] = len(sigs)
        s["selection"] = "all signals (2026-09-24 full-seed pass)"
        added += len(s["files"]) - before
        print(f"  seed-full: {name}: {before} -> {len(s['files'])} files")
    return added


def fetch_one(f_id, size, dest: Path):
    if dest.exists() and size and dest.stat().st_size == size:
        return "cached"
    dest.parent.mkdir(parents=True, exist_ok=True)
    op = make_opener()
    url = (f"https://{APP_HOST}/index.php?rm=box_download_shared_file"
           f"&shared_name={SHARED_NAME}&file_id=f_{f_id}")
    data = get(op, url)
    if size and len(data) != size:
        raise RuntimeError(f"size mismatch: {len(data)} != {size}")
    dest.write_bytes(data)
    return f"{len(data)} B"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=Path("/tmp/waveforms"))
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--manifest-only", action="store_true")
    ap.add_argument("--seed-full", action="store_true",
                    help="extend the cached manifest's seed sessions to all "
                         "signal numbers (re-lists their frozen folder ids)")
    ap.add_argument("--only-batch", default=None,
                    help="download only sessions of this batch")
    args = ap.parse_args()

    opener = make_opener()
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        print(f"manifest cached: {len(manifest['sessions'])} sessions")
    else:
        manifest = build_manifest(opener)
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=1))
        print(f"manifest -> {MANIFEST} ({len(manifest['sessions'])} sessions)")
    if args.seed_full:
        added = refresh_seed_full(opener, manifest)
        MANIFEST.write_text(json.dumps(manifest, indent=1))
        print(f"manifest updated in place: +{added} seed files")
    for name, s in sorted(manifest["sessions"].items()):
        tot = sum(f.get("size") or 0 for f in s["files"].values())
        print(f"  [{s['batch']:5s}] {name}  {len(s['files'])} files, {tot/1e6:.0f} MB")
    if args.manifest_only:
        return

    jobs = []
    for name, s in manifest["sessions"].items():
        if args.only_batch and s["batch"] != args.only_batch:
            continue
        sig_names = [fn for fn in s["files"] if "_Signal" in fn]
        spec = (sig_names[0].split("_Signal")[0].lower() if sig_names
                else re.sub(r"\W+", "_", name))
        for fname, f in s["files"].items():
            jobs.append((f["id"], f.get("size"),
                         args.dest / s["batch"] / spec / fname))
    total = sum(sz or 0 for _, sz, _ in jobs)
    print(f"downloading {len(jobs)} files, {total/1e9:.1f} GB -> {args.dest}")
    t0 = time.time()
    with ThreadPoolExecutor(args.jobs) as ex:
        futs = {ex.submit(fetch_one, fid, sz, p): p for fid, sz, p in jobs}
        for n, fut in enumerate(as_completed(futs), 1):
            fut.result()
            if n % 50 == 0 or n == len(futs):
                print(f"  {n}/{len(futs)}  ({(time.time()-t0)/60:.1f} min)", flush=True)
    print(f"done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
