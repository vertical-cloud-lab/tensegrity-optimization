#!/usr/bin/env python3
"""Export one drop-test session as plain CSVs for hands-on analysis.

Requested on issue #110 (2026-09-28): the corny7 drop data as a CSV. On
Box a session is one TP4 time-domain capture per drop
(``*_Signal<k>.csv``: 4 channels, 1.25 MHz, 100 ms, ~9.6 MB each) plus the
TP4 series table (one summary row per drop, multi-line header, in/s
units). This script writes three files into ``--out``:

* ``<id>_drops.csv``: one row per drop. The lab's per-drop metrics come
  from ``analyze_capture(path, baseline="tail")``, the same call the
  campaign pipeline makes, run on every drop including the two SOP
  warm-up drops the check-in averages leave out, and joined with the TP4
  series table's own per-channel numbers.
* ``<id>_waveforms_50kHz.csv``: every drop's four acceleration channels as
  recorded (no baseline removal, no CFC filter), long format, downsampled
  25x to 50 kHz with an anti-aliasing FIR (``resample_poly``).
* ``<id>_overview.png``: drawn from the two CSVs after they are written,
  so it doubles as a read-back check. The script also re-derives T180 for
  every drop from the 50 kHz file alone and prints the worst disagreement
  with ``<id>_drops.csv``.

The per-drop metrics import the drop-test pipeline of PR #86 (branch
``copilot/add-drop-test-protocol-again``), where ``scripts/analysis/``
lives until it merges. The corny7 export used that branch at ``314fc4c``.

Usage (corny7):
    python scripts/analysis/drop_test_session_csv_export.py \\
        --manifest data/drop-tests/corny7-export/box-ids.json \\
        --raw /tmp/corny7-raw --out data/drop-tests/corny7-export \\
        --id corny7 --pipeline-dir <PR #86 checkout>/scripts/analysis
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from datetime import datetime
from http.cookiejar import CookieJar
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal as sig

DECIM = 25                 # 1.25 MHz -> 50 kHz, the pipeline's RING_DECIM step
WARMUP_DROPS = 2           # SOP: the first two drops settle the rig, not averaged
IN_TO_M = 0.0254
TAIL_MS = 70.0             # tail baseline: channel median over the last 30 ms
IMPACT_SEARCH_MS = 15.0    # pipeline SEARCH_S
PEAK_HALF_WIN_MS = 5.0     # pipeline HALF_WIN_S
CFC180_HZ = 300.0          # pipeline cfc_filter(..., 180)
BOX_DOWNLOAD = ("https://byu.app.box.com/index.php?rm=box_download_shared_file"
                "&shared_name={shared}&file_id={fid}")

# (csv column, analyze_capture key, decimals)
METRICS = (
    ("input_peak_cfc180_g", "in_180_g", 2),
    ("output_peak_cfc180_g", "out_180_g", 2),
    ("T180", "t180", 4),
    ("input_peak_cfc1000_g", "in_1000_g", 2),
    ("output_peak_cfc1000_g", "out_1000_g", 2),
    ("T1000", "t1000", 4),
    ("input_peak_raw_g", "in_raw_g", 2),
    ("output_peak_raw_g", "out_raw_g", 2),
    ("input_pulse_width_ms", "in_width_ms", 3),
    ("output_pulse_width_ms", "out_width_ms", 3),
    ("output_lag_ms", "lag_ms", 3),
    ("input_delta_v_m_s", "in_dv_ms", 3),
    ("ring_freq_hz", "fn_hz", 1),
    ("ring_damping_pct", "zeta_pct", 2),
    ("ring_fit_r2", "ring_r2", 3),
    ("rebound_time_ms", "t_second_ms", 2),
    ("e_rebound", "e_rebound", 4),
)

# chart chrome + the two series (dataviz reference palette, light mode)
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
C_IN, C_OUT = "#2a78d6", "#eb6834"


def fetch(manifest: Path, raw: Path) -> None:
    """Download the session's files from the public Box share (no login)."""
    m = json.loads(manifest.read_text())
    raw.mkdir(parents=True, exist_ok=True)
    for name, fid in m["files"].items():
        p = raw / name
        if p.exists() and p.stat().st_size > 0:
            continue
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
        op.addheaders = [("User-Agent", "Mozilla/5.0")]
        with op.open(BOX_DOWNLOAD.format(shared=m["shared_name"], fid=fid), timeout=120) as r:
            p.write_bytes(r.read())
        print(f"  fetched {name}", flush=True)


def read_series_table(path: Path) -> dict[int, dict]:
    """TP4 series table -> {event number: local time + per-channel numbers}."""
    with open(path, encoding="latin-1", newline="") as fh:
        rows = [[c.strip() for c in r] for r in csv.reader(fh)]
    h = next(i for i, r in enumerate(rows) if r and r[0] == "TriggerMethod")
    chans = [c.split(":")[0].split()[-1].lower() for c in rows[h][4::3] if c]
    units = rows[h + 1][4:4 + 3 * len(chans)]
    if units != ["G", "msec", "in/sec"] * len(chans):
        sys.exit(f"unexpected TP4 series-table units {units}")
    out = {}
    for r in rows[h + 2:]:
        if len(r) < 4 or not r[1].isdigit():
            continue
        ev = {"time_local": datetime.strptime(r[2], "%m/%d/%Y %I:%M:%S %p")}
        for i, c in enumerate(chans):
            pk, dur, dv = (float(x) for x in r[4 + 3 * i:7 + 3 * i])
            ev[f"tp4_{c}_peak_g"] = pk
            ev[f"tp4_{c}_duration_ms"] = dur
            ev[f"tp4_{c}_delta_v_m_s"] = round(dv * IN_TO_M, 3)
        out[int(r[1])] = ev
    return out


def signal_no(p: Path) -> int:
    return int(p.stem.split("Signal")[1])


def t180_from_waveforms(w: np.ndarray, fs: float) -> float:
    """T180 from one drop's rows of the 50 kHz file (time_ms, CH2..CH5),
    following the pipeline recipe: tail-median zero, CFC-180, top-vertex
    resultant over CH5, peaks within +/-5 ms of the CH5 impact peak."""
    tms = w[:, 0]
    z = w[:, 1:] - np.median(w[tms >= TAIL_MS, 1:], axis=0)
    b, a = sig.butter(2, CFC180_HZ / (fs / 2.0), btype="low")
    f = sig.filtfilt(b, a, z, axis=0)
    inp = np.abs(f[:, 3])
    out = np.sqrt((f[:, :3] ** 2).sum(axis=1))
    i = int(np.argmax(np.where(tms < IMPACT_SEARCH_MS, inp, 0.0)))
    near = np.abs(tms - tms[i]) <= PEAK_HALF_WIN_MS
    return float(out[near].max() / inp[near].max())


def make_figure(spec_id: str, drops_csv: Path, wave_csv: Path, png: Path) -> float:
    d = np.genfromtxt(drops_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    w = np.loadtxt(wave_csv, delimiter=",", skiprows=1)
    fs = 1e3 / float(np.median(np.diff(w[w[:, 0] == w[0, 0], 1])))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6), facecolor=SURFACE,
                                   gridspec_kw={"width_ratios": [1.35, 1]})
    worst, curves = 0.0, {}
    b, a = sig.butter(2, CFC180_HZ / (fs / 2.0), btype="low")
    for k in d["drop_number"]:
        wk = w[w[:, 0] == k][:, 1:]
        tms = wk[:, 0]
        z = wk[:, 1:] - np.median(wk[tms >= TAIL_MS, 1:], axis=0)
        f = sig.filtfilt(b, a, z, axis=0)
        curves[k] = (tms, np.abs(f[:, 3]), np.sqrt((f[:, :3] ** 2).sum(axis=1)))
        ax1.plot(tms, curves[k][1], color=C_IN, lw=0.8, alpha=0.45)
        ax1.plot(tms, curves[k][2], color=C_OUT, lw=0.8, alpha=0.45)
        t_csv = float(d["T180"][d["drop_number"] == k][0])
        worst = max(worst, abs(t180_from_waveforms(wk, fs) / t_csv - 1.0))
    ax1.plot([], [], color=C_IN, lw=2, label="Input: base plate (CH5)")
    ax1.plot([], [], color=C_OUT, lw=2, label="Output: top vertex (CH2, CH3, CH4 resultant)")
    tms, inp, out = curves[d["drop_number"][WARMUP_DROPS]]
    for y, name in ((inp, "input peak"), (out, "output peak")):
        j = int(np.argmax(np.where(tms < IMPACT_SEARCH_MS, y, 0.0)))
        ax1.annotate(name, xy=(tms[j], y[j]), xytext=(tms[j] + 2.2, 0.9 * y[j]),
                     va="center", color=INK2, fontsize=9,
                     arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    ax1.set_xlim(0, 12)
    ax1.set_ylim(0, 1.25 * max(c[1].max() for c in curves.values()))
    ax1.set_xlabel("Time in record (ms); trigger at 2 ms")
    ax1.set_ylabel("Acceleration, CFC-180 (G)")
    ax1.set_title(f"All {len(d)} drops overlaid", loc="left", color=INK, fontsize=11)
    ax1.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=INK2)

    warm = d["warmup"].astype(str) == "True"
    stab = d["T180"][~warm]
    lo = min(d["T180"].min(), 1.0) - 0.10
    ax2.axhline(1.0, color=AXIS, lw=1.0)
    ax2.text(len(d) + 0.4, 1.0, "T = 1: output peak equals input peak", ha="right",
             va="bottom", color=MUTED, fontsize=9)
    ax2.axhline(stab.mean(), color=C_IN, lw=1.0, ls=(0, (4, 3)))
    ax2.text(len(d) + 0.4, stab.mean() + 0.015,
             f"mean of drops {WARMUP_DROPS + 1} to {len(d)}: {stab.mean():.3f} "
             f"(CV {100 * stab.std(ddof=1) / stab.mean():.2f} %)",
             ha="right", va="bottom", color=INK2, fontsize=9)
    ax2.plot(d["drop_number"][~warm], stab, "o", ms=6, color=C_IN, mec=SURFACE, mew=1.0)
    ax2.plot(d["drop_number"][warm], d["T180"][warm], "o", ms=6, mfc=SURFACE, mec=C_IN, mew=1.5)
    ax2.annotate("warm-up drops,\nnot averaged", xy=(1.5, d["T180"][warm].min() - 0.008),
                 xytext=(1.5, lo + 0.045), ha="center", va="top", color=INK2, fontsize=9,
                 arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    ax2.set_xlim(0.3, len(d) + 0.7)
    ax2.set_ylim(lo, max(d["T180"].max(), 1.0) + 0.04)
    ax2.set_xticks([1, 5, 10, 15, 20])
    ax2.set_xlabel("Drop number")
    ax2.set_ylabel("T180 = output peak / input peak")
    ax2.set_title("Transmissibility per drop", loc="left", color=INK, fontsize=11)

    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(AXIS)
        ax.tick_params(colors=MUTED, labelcolor=INK2, labelsize=9)
        ax.xaxis.label.set_color(INK2)
        ax.yaxis.label.set_color(INK2)
    fig.suptitle(f"{spec_id}: {len(d)} drops from 60 in onto the 1/2 in PU mat, "
                 f"{d['time_local'][0][:10]}", x=0.01, ha="left", color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True,
                    help="folder with the session's *_Signal<k>.csv captures + series table")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--id", required=True, help="specimen id used in the file names")
    ap.add_argument("--manifest", type=Path, default=None,
                    help="box-ids.json: fetch any missing files into --raw first")
    ap.add_argument("--pipeline-dir", type=Path,
                    default=Path(__file__).resolve().parent,
                    help="PR #86 scripts/analysis (holds drop_test_abc123_blind_analysis.py)")
    ap.add_argument("--check", type=Path, default=None,
                    help="campaign_metrics.json to compare the stabilized drops against")
    args = ap.parse_args()

    sys.path.insert(0, str(args.pipeline_dir))
    try:
        from drop_test_abc123_blind_analysis import analyze_capture, parse_capture
    except ImportError:
        sys.exit(f"drop-test pipeline not found in {args.pipeline_dir}; pass --pipeline-dir "
                 "pointing at scripts/analysis of PR #86 (copilot/add-drop-test-protocol-again)")

    if args.manifest:
        fetch(args.manifest, args.raw)
    caps = sorted(args.raw.glob("*_Signal*.csv"), key=signal_no)
    tables = [p for p in args.raw.glob("*.csv") if "Signal" not in p.name]
    if not caps or len(tables) != 1:
        sys.exit(f"need Signal captures and exactly one TP4 series table in {args.raw}")
    series = read_series_table(tables[0])
    args.out.mkdir(parents=True, exist_ok=True)

    drops, waves = [], []
    for p in caps:
        k = signal_no(p)
        m = analyze_capture(p, baseline="tail")
        row = {"drop_number": k, "time_local": series[k]["time_local"].isoformat(sep=" "),
               "warmup": k <= WARMUP_DROPS}
        row.update({col: round(m[key], nd) if np.isfinite(m.get(key, np.nan)) else ""
                    for col, key, nd in METRICS})
        row.update({c: v for c, v in series[k].items() if c.startswith("tp4_")})
        drops.append(row)

        t, ch, _ = parse_capture(p)
        y = sig.resample_poly(ch, 1, DECIM, axis=0, padtype="line")
        tms = 1e3 * t[::DECIM][:len(y)]
        waves.append(np.column_stack([np.full(len(y), k), tms, y]))
        print(f"  drop {k:2d}  T180 {m['t180']:.4f}  in {m['in_180_g']:6.1f} G  "
              f"out {m['out_180_g']:6.1f} G", flush=True)

    drops_csv = args.out / f"{args.id}_drops.csv"
    with open(drops_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(drops[0]))
        w.writeheader()
        w.writerows(drops)
    wave_csv = args.out / f"{args.id}_waveforms_50kHz.csv"
    np.savetxt(wave_csv, np.vstack(waves), delimiter=",", comments="",
               header="drop_number,time_ms,ch2_g,ch3_g,ch4_g,ch5_g",
               fmt=["%d", "%.2f", "%.3f", "%.3f", "%.3f", "%.3f"])

    if args.check:
        ref = json.loads(args.check.read_text())["specimens"][args.id]["rows"]
        full = {signal_no(p): analyze_capture(p, baseline="tail") for p in caps}
        diff = max(abs(full[r["signal"]][k] / v - 1.0) for r in ref for k, v in r.items()
                   if isinstance(v, float) and v and np.isfinite(v))
        print(f"check vs {args.check.name}: {len(ref)} drops, "
              f"worst relative difference {diff:.2e}")

    png = args.out / f"{args.id}_overview.png"
    worst = make_figure(args.id, drops_csv, wave_csv, png)
    print(f"T180 re-derived from the 50 kHz CSV: worst difference {100 * worst:.3f} % "
          f"vs {drops_csv.name}")
    print(f"wrote {drops_csv}, {wave_csv} "
          f"({wave_csv.stat().st_size / 1e6:.1f} MB), {png}")


if __name__ == "__main__":
    main()
