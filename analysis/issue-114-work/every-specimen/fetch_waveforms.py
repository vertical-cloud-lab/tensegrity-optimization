#!/usr/bin/env python3
"""Fetch the drop captures of every BO-campaign session from Box and write
one 50 kHz waveform CSV per specimen, in the format of the corny7 export of
issue #110 (``corny7_waveforms_50kHz.csv``), so Justin's script reads any of
them unchanged.

This extends ``../all-specimens/fetch_waveforms.py`` (36 specimens) to all 54
sessions of the campaign, every one dropped from 60 in onto the 1/2 in PU mat
(arrangement B) with the same four channels and 100 ms captures:

* seed  (batch 1, Sobol): 6lhxfy 6nheas 9hhbkp amdjwm autv5r bag26v bpx68c
  nvxsrv ajhby6, 101 drops each. Only the first 20 captures are fetched, so
  these specimens are measured over the same drops (3 to 20) as every other
  batch.

Drop k is the session's k-th capture in signal order. That is the signal
number everywhere except 6lhxfy, whose captures start at Signal2, and r2d2c8,
whose export also holds a stray bare ``..._Signal9.csv`` next to
``..._Signal9_Signal<k>.csv`` (the doubled names are used).
* r2d2c (batch 2, round 1): r2d2c1 to r2d2c9, 21 drops each.
* drran, 2dran, dran3 (batch 3, three prints of the round-3 plate) and
  corny (batch 4, round 4), 20 drops each.

Box file ids: ``box-ids/<specimen>.json``. The batch 3 and 4 ids are copied
from ``../all-specimens/box-ids`` (PR #86 check-ins); the seed and r2d2c ids
come from ``box-session-manifest.json`` on branch
``claude/cv-signal-audit-20260922`` (folder
``analysis/payload-protection-metrics/data``).

The conversion is the export recipe of issue #110: channels as recorded, no
zeroing, no filtering, downsampled 25 times (1.25 MHz to 50 kHz) with
``scipy.signal.resample_poly(..., padtype="line")``. ``--check-corny7``
confirms the output is byte-identical to the committed corny7 export.

Usage:
    python fetch_waveforms.py --raw /tmp/drop-raw [--batches seed r2d2c] [--jobs 8]
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.cookiejar import CookieJar
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal as sig

HERE = Path(__file__).resolve().parent
BATCHES = {
    "seed": ["6lhxfy", "6nheas", "9hhbkp", "amdjwm", "autv5r", "bag26v", "bpx68c",
             "nvxsrv", "ajhby6"],
    "r2d2c": [f"r2d2c{n}" for n in range(1, 10)],
    "drran": [f"drran{n}" for n in range(1, 10)],
    "2dran": [f"2dran{n}" for n in range(1, 10)],
    "dran3": [f"dran3{n}" for n in range(1, 10)],
    "corny": [f"corny{n}" for n in range(1, 10)],
}
MAX_DROPS = 20             # drops 1 to 20; the analysis uses 3 to 20
DECIM = 25                 # 1.25 MHz -> 50 kHz
TP4_HEADER_LINES = 9
BOX_DOWNLOAD = ("https://byu.app.box.com/index.php?rm=box_download_shared_file"
                "&shared_name={shared}&file_id={fid}")
CORNY7_EXPORT = ("https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/"
                 "5cc4b1e37ddd3f589e31b7c554d360469565233d/data/drop-tests/corny7-export/"
                 "corny7_waveforms_50kHz.csv")


def signal_no(name: str) -> int | None:
    """Capture number: the last ``Signal<k>`` in the file name."""
    m = re.findall(r"Signal(\d+)", name)
    return int(m[-1]) if m and name.endswith(".csv") else None


def pick_files(files: dict[str, str]) -> dict[int, tuple[int, str, str]]:
    """The session's first ``MAX_DROPS`` captures in signal order, keyed by drop
    number (1, 2, ...): drop k is the k-th capture, so a session whose numbering
    starts at Signal2 (6lhxfy) still gives drops 1 to 20."""
    by_sig: dict[int, tuple[str, str]] = {}
    for name, fid in files.items():
        k = signal_no(name)
        if k is None:
            continue
        if k in by_sig and name.count("Signal") < by_sig[k][0].count("Signal"):
            continue
        by_sig[k] = (name, fid)
    return {i: (k, *by_sig[k]) for i, k in enumerate(sorted(by_sig)[:MAX_DROPS], start=1)}


def download(url: str, dest: Path, tries: int = 4) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    for k in range(tries):
        try:
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
            op.addheaders = [("User-Agent", "Mozilla/5.0")]
            with op.open(url, timeout=300) as r:
                data = r.read()
            tmp = dest.with_suffix(dest.suffix + ".part")
            tmp.write_bytes(data)
            tmp.rename(dest)
            return
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))


def fetch(raw: Path, spec: str, jobs: int) -> dict[int, Path]:
    m = json.loads((HERE / "box-ids" / f"{spec}.json").read_text())
    d = raw / spec
    d.mkdir(parents=True, exist_ok=True)
    picks = pick_files(m["files"])
    todo = [(BOX_DOWNLOAD.format(shared=m["shared_name"], fid=fid), d / f"Signal{k}.csv")
            for k, name, fid in picks.values()]
    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(lambda j: download(*j), todo))
    return {i: d / f"Signal{k}.csv" for i, (k, _, _) in picks.items()}


def convert(caps: dict[int, Path], out_csv: Path) -> int:
    waves = []
    for k in sorted(caps):
        d = pd.read_csv(caps[k], skiprows=TP4_HEADER_LINES, header=None, usecols=range(5),
                        float_precision="round_trip").to_numpy(dtype=float)
        t, ch = d[:, 0], d[:, 1:]
        y = sig.resample_poly(ch, 1, DECIM, axis=0, padtype="line")
        tms = 1e3 * t[::DECIM][:len(y)]
        waves.append(np.column_stack([np.full(len(y), k), tms, y]))
    np.savetxt(out_csv, np.vstack(waves), delimiter=",", comments="",
               header="drop_number,time_ms,ch2_g,ch3_g,ch4_g,ch5_g",
               fmt=["%d", "%.2f", "%.3f", "%.3f", "%.3f", "%.3f"])
    return len(caps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True, help="scratch folder for the Box captures")
    ap.add_argument("--out", type=Path, default=HERE / "waveforms")
    ap.add_argument("--batches", nargs="+", choices=list(BATCHES), default=list(BATCHES))
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--check-corny7", action="store_true",
                    help="compare the corny7 CSV written here with the issue #110 export")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    for spec in [s for b in args.batches for s in BATCHES[b]]:
        out = args.out / f"{spec}_waveforms_50kHz.csv"
        if out.exists():
            continue
        t0 = time.time()
        caps = fetch(args.raw, spec, args.jobs)
        n = convert(caps, out)
        print(f"{spec}: {n} drops -> {out.name} ({time.time() - t0:.0f} s)", flush=True)

    if args.check_corny7:
        ref = args.raw / "corny7_waveforms_50kHz_issue110.csv"
        download(CORNY7_EXPORT, ref)
        same = ref.read_bytes() == (args.out / "corny7_waveforms_50kHz.csv").read_bytes()
        print(f"corny7 CSV identical to the issue #110 export: {same}")


if __name__ == "__main__":
    main()
