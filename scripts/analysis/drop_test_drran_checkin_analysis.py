#!/usr/bin/env python3
"""drran1..drran9 check-in — single-drop plots (PR #86, 09-05).

Nine 20-drop sessions recorded 09-03 (60 in, arrangement B = 1/2 in PU
mat, current SOP capture settings) and posted by @ctrhjk as subfolders of
the standing public Box share; the request repeats the r2d2 check-in
format for the new batch: one representative waveform plot per specimen
(the fifth drop of each), transmissibility averages, and a first-look
anomaly screen.

Per-drop metrics come from the standing campaign pipeline
(``drop_test_campaign_analysis.py`` on a nine-specimen root, tail
baseline, standing T-drift watch); this script only adds the requested
fifth-drop waveform figure for each session, reusing the r2d2 check-in
figure unchanged.

Usage:
    python scripts/analysis/drop_test_drran_checkin_analysis.py --raw ROOT
where ROOT holds one subfolder per session (``drran1`` .. ``drran9``)
with the ``*_Signal<k>.csv`` captures.  Raw data stays on Box (share
``kkhmvnj9ni19b57dryk3gdroqrp5uf0b``); the per-session
``raw/<id>/box-ids.json`` manifests re-fetch it via
``scripts/fetch_box_shared_folder.py``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_r2d2_checkin_analysis import DROP_NO, fifth_drop_figure  # noqa: E402
from drop_test_60in_5felts_analysis import DATA  # noqa: E402

OUT = DATA / "drran-checkin"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True,
                    help="root with one subfolder per session")
    ap.add_argument("--out", type=Path, default=OUT / "figures")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    # 01 is the campaign-series figure from the batch pipeline; the nine
    # drop-5 figures take 02..10.
    for i, folder in enumerate(sorted(p for p in args.raw.iterdir() if p.is_dir())):
        specimen = folder.name.split()[0].lower()
        hits = sorted(folder.rglob(f"*Signal{DROP_NO}.csv"))
        if not hits:
            print(f"{specimen}: no Signal{DROP_NO} capture found, skipped")
            continue
        fig_path = args.out / f"{i + 2:02d}_{specimen}_drop5.png"
        m = fifth_drop_figure(hits[0], specimen, fig_path)
        print(f"{specimen} drop {DROP_NO}: T180 {m['t180']:.4f}  "
              f"in {m['in_180_g']:.1f} G  out {m['out_180_g']:.1f} G  "
              f"dv {m['in_dv_ms']:.3f} m/s  -> {fig_path.name}")


if __name__ == "__main__":
    main()
