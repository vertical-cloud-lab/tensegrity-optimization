#!/usr/bin/env python3
"""r2d2c1 / r2d2c2 first-upload check-in — single-drop plots (PR #86, 08-24).

Two 21-drop sessions of the replicate-print pair ``r2d2c1`` / ``r2d2c2``
(60 in, arrangement B, current SOP capture settings) were uploaded before
the full campaigns finished; the request was one representative plot per
specimen (the fifth drop of each), transmissibility averages, and a
first-look anomaly screen.

Per-drop metrics come from the standing campaign pipeline
(``drop_test_campaign_analysis.py`` on a two-specimen root, tail
baseline); this script only adds the requested per-drop waveform figures:
for Signal 5 of each session, the full 100 ms record (CFC-180 input vs
top-vertex resultant, hop landing marked) and an impact zoom (raw + CFC
input, CFC output).

Usage:
    python scripts/analysis/drop_test_r2d2_checkin_analysis.py --raw ROOT
where ROOT holds one subfolder per session with the ``*_Signal<k>.csv``
captures (the Box uploads, shares ual6v97k... / c2455s0c...).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_abc123_blind_analysis import (  # noqa: E402
    CH5, TOP_COLS, analyze_capture, cfc_filter, parse_capture)
from drop_test_60in_5felts_analysis import DATA  # noqa: E402

OUT = DATA / "r2d2-checkin"
DROP_NO = 5  # the requested drop


def fifth_drop_figure(csv_path: Path, specimen: str, fig_path: Path) -> dict:
    t, ch, ev = parse_capture(csv_path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    base = np.median(ch[int(0.070 / dt):], axis=0)  # tail baseline (08-17+ SOP)
    top = ch[:, TOP_COLS] - base[list(TOP_COLS)]
    ch5 = ch[:, CH5] - base[CH5]

    in180 = cfc_filter(ch5, fs, 180)
    out180 = np.sqrt(np.sum(np.stack([cfc_filter(top[:, c], fs, 180)
                                      for c in range(3)], 1) ** 2, axis=1))
    m = analyze_capture(csv_path, baseline="tail")
    t_imp = m["t_imp_ms"]
    tms = t * 1e3

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6),
                                   gridspec_kw={"width_ratios": [1.6, 1]})
    ax1.plot(tms, in180, lw=0.7, color="tab:blue",
             label=f"input CH5 (CFC-180), peak {m['in_180_g']:.0f} G")
    ax1.plot(tms, out180, lw=0.7, color="tab:red", alpha=0.8,
             label=f"top-vertex resultant (CFC-180), peak {m['out_180_g']:.0f} G")
    if m.get("t_second_ms"):
        ax1.axvline(t_imp + m["t_second_ms"], color="k", ls=":", lw=1,
                    label=f"specimen-hop landing (+{m['t_second_ms']:.1f} ms)")
    ax1.set_xlabel("time (ms)")
    ax1.set_ylabel("acceleration (G)")
    ax1.set_title(f"{specimen} — drop {DROP_NO}, full 100 ms record")
    ax1.legend(fontsize=8, loc="upper right")

    w = (tms > t_imp - 3) & (tms < t_imp + 7)
    ax2.plot(tms[w], ch5[w], lw=0.5, color="tab:blue", alpha=0.35, label="input raw")
    ax2.plot(tms[w], in180[w], lw=1.2, color="tab:blue", label="input CFC-180")
    ax2.plot(tms[w], out180[w], lw=1.2, color="tab:red", label="output CFC-180")
    ax2.set_xlabel("time (ms)")
    ax2.set_title(f"impact zoom — T = {m['t180']:.3f}, "
                  f"width {m['in_width_ms']:.2f} ms, Δv {m['in_dv_ms']:.2f} m/s")
    ax2.legend(fontsize=8)
    for ax in (ax1, ax2):
        ax.grid(alpha=0.3)
    fig.suptitle(f"{specimen}  ·  Signal {DROP_NO}  ·  {ev:%Y-%m-%d %H:%M:%S}"
                 if ev else specimen, y=1.0, fontsize=10)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True,
                    help="root with one subfolder per session")
    ap.add_argument("--out", type=Path, default=OUT / "figures")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for folder in sorted(p for p in args.raw.iterdir() if p.is_dir()):
        specimen = folder.name.split()[0].lower()
        hits = [p for p in folder.rglob(f"*Signal{DROP_NO}.csv")]
        if not hits:
            print(f"{specimen}: no Signal{DROP_NO} capture found, skipped")
            continue
        fig_path = args.out / f"0{3 if specimen.endswith('2') else 2}_{specimen}_drop5.png"
        m = fifth_drop_figure(hits[0], specimen, fig_path)
        print(f"{specimen} drop {DROP_NO}: T180 {m['t180']:.4f}  "
              f"in {m['in_180_g']:.1f} G  out {m['out_180_g']:.1f} G  "
              f"dv {m['in_dv_ms']:.3f} m/s  -> {fig_path.name}")


if __name__ == "__main__":
    main()
