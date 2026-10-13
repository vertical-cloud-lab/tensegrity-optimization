#!/usr/bin/env python3
"""Fetch drop captures from Box and write one 50 kHz waveform CSV per
specimen, in the same format as the corny7 export of issue #110
(``corny7_waveforms_50kHz.csv``), so Justin's script reads any of them
unchanged.

Four batches are recorded under the same procedure (60 in onto the 1/2 in
PU mat, 20 drops, same four channels): corny1 to corny9 (round 4) and the
three prints of round 3, drran1 to drran9, 2dran1 to 2dran9 and dran31 to
dran39. The Box ids of each session are in ``box-ids/``.

Each Box session folder holds one TP4 capture per drop
(``*_Signal<k>.csv``: 9 header lines, then time and CH2 to CH5 at
1.25 MHz for 100 ms, about 9.6 MB each). The conversion is the export
script's own recipe (``scripts/analysis/drop_test_session_csv_export.py``
on branch ``claude/issue-110-20260928-2047``): the channels as recorded,
no zeroing and no filtering, downsampled 25 times with
``scipy.signal.resample_poly(..., padtype="line")``. Run on corny7 it
reproduces the committed corny7 CSV byte for byte (checked with
``--check-corny7``).

Usage:
    python fetch_waveforms.py --raw /tmp/drop-raw                  # all four batches
    python fetch_waveforms.py --raw /tmp/drop-raw --batches corny  # corny only
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.cookiejar import CookieJar
from pathlib import Path

import numpy as np
from scipy import signal as sig

HERE = Path(__file__).resolve().parent
BATCHES = {
    "corny": [f"corny{n}" for n in range(1, 10)],
    "drran": [f"drran{n}" for n in range(1, 10)],
    "2dran": [f"2dran{n}" for n in range(1, 10)],
    "dran3": [f"dran3{n}" for n in range(1, 10)],
}
DECIM = 25                 # 1.25 MHz -> 50 kHz
TP4_HEADER_LINES = 9
BOX_DOWNLOAD = ("https://byu.app.box.com/index.php?rm=box_download_shared_file"
                "&shared_name={shared}&file_id={fid}")
CORNY7_EXPORT = ("https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/"
                 "5cc4b1e37ddd3f589e31b7c554d360469565233d/data/drop-tests/corny7-export/corny7_waveforms_50kHz.csv")


def download(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    with op.open(url, timeout=300) as r:
        data = r.read()
    tmp = dest.with_suffix(dest.suffix + ".part")
    tmp.write_bytes(data)
    tmp.rename(dest)


def fetch_all(raw: Path, specimens: list[str], workers: int = 8) -> None:
    jobs = []
    for spec in specimens:
        m = json.loads((HERE / "box-ids" / f"{spec}.json").read_text())
        d = raw / spec
        d.mkdir(parents=True, exist_ok=True)
        for name, fid in m["files"].items():
            jobs.append((BOX_DOWNLOAD.format(shared=m["shared_name"], fid=fid), d / name))
    with ThreadPoolExecutor(workers) as ex:
        for _ in ex.map(lambda j: download(*j), jobs):
            pass
    print(f"fetched {len(jobs)} files into {raw}", flush=True)


def signal_no(p: Path) -> int:
    return int(p.stem.split("Signal")[1])


def convert(raw_dir: Path, out_csv: Path) -> int:
    caps = sorted(raw_dir.glob("*_Signal*.csv"), key=signal_no)
    waves = []
    for p in caps:
        d = np.loadtxt(p, delimiter=",", skiprows=TP4_HEADER_LINES, usecols=(0, 1, 2, 3, 4))
        t, ch = d[:, 0], d[:, 1:]
        y = sig.resample_poly(ch, 1, DECIM, axis=0, padtype="line")
        tms = 1e3 * t[::DECIM][:len(y)]
        waves.append(np.column_stack([np.full(len(y), signal_no(p)), tms, y]))
    np.savetxt(out_csv, np.vstack(waves), delimiter=",", comments="",
               header="drop_number,time_ms,ch2_g,ch3_g,ch4_g,ch5_g",
               fmt=["%d", "%.2f", "%.3f", "%.3f", "%.3f", "%.3f"])
    return len(caps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True, help="where the Box captures go")
    ap.add_argument("--out", type=Path, default=HERE / "waveforms")
    ap.add_argument("--batches", nargs="+", choices=list(BATCHES), default=list(BATCHES))
    ap.add_argument("--check-corny7", action="store_true",
                    help="compare the corny7 CSV written here with the issue #110 export")
    args = ap.parse_args()

    specimens = [s for b in args.batches for s in BATCHES[b]]
    fetch_all(args.raw, specimens)
    args.out.mkdir(parents=True, exist_ok=True)
    for spec in specimens:
        out = args.out / f"{spec}_waveforms_50kHz.csv"
        if not out.exists():
            n = convert(args.raw / spec, out)
            print(f"  {spec}: {n} drops -> {out.name}", flush=True)

    if args.check_corny7:
        ref = args.raw / "corny7_waveforms_50kHz_issue110.csv"
        download(CORNY7_EXPORT, ref)
        same = ref.read_bytes() == (args.out / "corny7_waveforms_50kHz.csv").read_bytes()
        print(f"corny7 CSV identical to the issue #110 export: {same}")


if __name__ == "__main__":
    main()
