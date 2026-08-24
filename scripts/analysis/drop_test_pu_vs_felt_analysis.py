#!/usr/bin/env python3
"""Polyurethane-rubber vs felt+cardboard absorber-stack comparison.

@me-madsen posted a paired A/B test on PR #86 (Box folder
``qfryxzjej47yil7ztvqxmhf5qcq0qa4p``): the same specimen (``bpx68c``)
dropped 5 times on the incumbent 4-felt + 1-cardboard stack (session
"bpx68c - 60 in - 4 flt 1 crdbrd", 2026-07-30 11:19-11:23) and then 5
times on the new polyurethane rubber sheets (session "bpx68c -
Polyurethane Rubber", 11:41-11:45) — the "mini-sweep" step of the
qualification protocol in ``docs/drop-test-absorber-alternatives.md``.

Format: full 4-channel export (CH2-4 = top-vertex key-seat tri-axis
"TOP" output, CH5 = single-axis base-plate input + trigger) at 1.25 MHz
over a 20 ms window. Two convention deviations from the 200 ms-format
scripts, both forced by this capture format:

  * the ~1 ms pre-trigger is contaminated by the pulse onset (the felt
    records carry ~50 G on CH5 in their first 0.3 ms), so the baseline
    is the full-record median (robust: the impact occupies < 25 % of the
    window) instead of a pre-trigger window;
  * the PU pulse peaks 1.6-3.5 ms into the record, far from the raw
    trigger spike, so the impact is located at the global argmax of the
    CFC-180-filtered CH5 within the first 12 ms and the peak walk is
    bounded at +-4 ms (the PU half-max width alone is ~2.7 ms).

Emits ``data/drop-tests/pu-vs-felt/figures/pu_vs_felt_metrics.json``
consumed by ``docs/drop-test-pu-vs-felt-analysis.md``.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import (  # noqa: E402
    DATA,
    FULL_SCALE_G,
    GRAVITY,
    TP4_HEADER_LINES,
    arr,
    cfc_filter,
    cv,
    resultant,
)

OUT = DATA / "pu-vs-felt"
RAW = OUT / "raw"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4
CH5 = 3

SEARCH_S = 0.012  # impact must land in the first 12 ms of the 20 ms record
HALF_WIN_S = 0.004  # peak walk bound: PU half-max width alone is ~2.7 ms
DV_TOTAL_S = 0.012  # cumulative-integral plateau (both stacks settle by ~6 ms)

CONDITIONS = [
    {"key": "felt", "label": "4 felt + 1 cardboard", "zip": RAW / "felt-cardboard.zip",
     "color": "tab:orange"},
    {"key": "pu", "label": "polyurethane rubber", "zip": RAW / "polyurethane.zip",
     "color": "tab:blue"},
]


def load_captures(zpath: Path) -> list[tuple[int, str]]:
    caps = []
    with zipfile.ZipFile(zpath) as zf:
        for member in zf.namelist():
            stem = Path(member).name
            if "Signal" not in stem or not stem.lower().endswith(".csv"):
                continue
            sig = int(stem.split("Signal")[1].split(".")[0])
            caps.append((sig, zf.read(member).decode("latin-1")))
    caps.sort(key=lambda c: c[0])
    return caps


def half_max_pulse(t: np.ndarray, a_g: np.ndarray, idx: int, dt: float) -> dict:
    half = int(HALF_WIN_S / dt)
    lo0, hi0 = max(0, idx - half), min(len(a_g), idx + half)
    peak = a_g[idx]
    thr = abs(peak) / 2.0
    over = (np.sign(peak) * a_g) >= thr
    lo = idx
    while lo > lo0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < hi0 - 1 and over[hi + 1]:
        hi += 1
    dv = integrate.trapezoid(a_g[lo : hi + 1] * GRAVITY, t[lo : hi + 1])
    return {"peak_abs_g": float(abs(peak)), "t_peak_ms": float(t[idx] * 1e3),
            "pulse_width_ms": float((t[hi] - t[lo]) * 1e3), "delta_v_ms": float(abs(dv))}


def analyze_capture(sig: int, text: str) -> dict:
    ev = None
    for line in text.splitlines()[:TP4_HEADER_LINES]:
        if line.startswith("EventTime:"):
            ev = datetime.strptime(line.split(":", 1)[1].strip(),
                                   "%m/%d/%Y %I:%M:%S %p")
    d = np.genfromtxt(io.StringIO(text), skip_header=TP4_HEADER_LINES,
                      delimiter=",", usecols=(0, 1, 2, 3, 4))
    t, ch = d[:, 0], d[:, 1:5]
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt

    ch = ch - np.median(ch, axis=0)  # full-record median baseline (see module doc)
    top = ch[:, TOP_COLS]
    ch5 = ch[:, CH5]

    n_search = int(SEARCH_S / dt)
    ch5_180 = cfc_filter(ch5, fs, 180)
    i_imp = int(np.argmax(np.abs(ch5_180[:n_search])))

    m_ch5 = half_max_pulse(t, ch5_180, i_imp, dt)
    ch5_1000 = cfc_filter(ch5, fs, 1000)
    i_1000 = int(np.argmax(np.abs(ch5_1000[:n_search])))

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    res180 = resultant(top180)
    half = int(HALF_WIN_S / dt)
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    i_top = lo + int(np.argmax(res180[lo:hi]))
    m_top = half_max_pulse(t, res180, i_top, dt)

    # full-pulse velocity change: plateau of the cumulative CH5 integral
    n_dv = int(DV_TOTAL_S / dt)
    v = integrate.cumulative_trapezoid(ch5_180[:n_dv] * GRAVITY, t[:n_dv], initial=0.0)
    dv_total = float(np.max(np.abs(v)))

    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3)]:
        pk = float(np.max(np.abs(ch[:, col])))
        sat[name] = {"peak_g": pk, "frac_fs": pk / FULL_SCALE_G[name]}

    return {
        "signal": sig,
        "event_time": ev.isoformat(),
        "t_imp_ms": m_ch5["t_peak_ms"],
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "ch5_frac_fs": sat["CH5"]["frac_fs"],
        "ch5_1000_g": float(abs(ch5_1000[i_1000])),
        "ch5_180_g": m_ch5["peak_abs_g"],
        "ch5_width_ms": m_ch5["pulse_width_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "ch5_dv_total_ms": dv_total,
        "top_180_g": m_top["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "sat": sat,
        "series": {  # decimated traces for the overlay figures
            "t_ms": (t[:n_dv:50] * 1e3).tolist(),
            "ch5_180_g": ch5_180[:n_dv:50].tolist(),
            "v_ms": v[::50].tolist(),
        },
    }


def welch(a: np.ndarray, b: np.ndarray) -> dict:
    tt = stats.ttest_ind(a, b, equal_var=False)
    sp = np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 2.0)
    return {
        "felt": {"n": int(len(a)), "mean": float(a.mean()), "sd": float(a.std(ddof=1)),
                 "cv": cv(a)},
        "pu": {"n": int(len(b)), "mean": float(b.mean()), "sd": float(b.std(ddof=1)),
               "cv": cv(b)},
        "diff_pct": float(100.0 * (b.mean() - a.mean()) / a.mean()),
        "welch_p": float(tt.pvalue),
        "cohens_d": float((b.mean() - a.mean()) / sp) if sp else float("nan"),
    }


def main() -> int:
    per_cond = {}
    for cond in CONDITIONS:
        rows = [analyze_capture(sig, text) for sig, text in load_captures(cond["zip"])]
        per_cond[cond["key"]] = rows
        print(f"\n{'=' * 78}\n=== {cond['label']} ({len(rows)} drops) ===\n{'=' * 78}")
        for r in rows:
            print(f"  S{r['signal']}: t_imp {r['t_imp_ms']:5.2f} ms   "
                  f"CH5 raw {r['ch5_raw_g']:6.0f} G ({100 * r['ch5_frac_fs']:4.1f}% FS)   "
                  f"CFC-180 {r['ch5_180_g']:5.1f} G  w {r['ch5_width_ms']:.2f} ms  "
                  f"dv_tot {r['ch5_dv_total_ms']:.2f} m/s   "
                  f"TOP {r['top_180_g']:5.1f} G   T {r['t_ch5']:.3f}")
        for key, label in [("ch5_raw_g", "CH5 raw (G)"), ("ch5_180_g", "CH5 CFC-180 (G)"),
                           ("ch5_width_ms", "width (ms)"), ("ch5_dv_total_ms", "dv_tot (m/s)"),
                           ("top_180_g", "TOP CFC-180 (G)"), ("t_ch5", "T = TOP/CH5")]:
            a = arr(rows, key)
            print(f"  {label:16s}: mean {a.mean():8.3f}   sd {a.std(ddof=1):7.3f}   "
                  f"CV {cv(a):5.1f}%")

    felt, pu = per_cond["felt"], per_cond["pu"]

    print(f"\n{'=' * 78}\n=== felt+cardboard vs polyurethane (Welch) ===\n{'=' * 78}")
    comparison = {}
    for key, label in [("ch5_raw_g", "CH5 raw peak"), ("ch5_180_g", "CH5 input CFC-180"),
                       ("ch5_width_ms", "input pulse width"), ("ch5_dv_total_ms", "full-pulse dv"),
                       ("top_180_g", "TOP output CFC-180"), ("t_ch5", "T = TOP/CH5")]:
        c = welch(arr(felt, key), arr(pu, key))
        comparison[key] = c
        print(f"  {label:18s}: felt {c['felt']['mean']:8.3f} (CV {c['felt']['cv']:4.1f}%)  ->  "
              f"PU {c['pu']['mean']:8.3f} (CV {c['pu']['cv']:4.1f}%)   "
              f"{c['diff_pct']:+6.1f}%   p = {c['welch_p']:.2e}   d = {c['cohens_d']:+.1f}")

    # PU repeatability clusters (stiff S3/S5 vs soft S1/S2/S4) — report, don't hide
    pu_by_width = sorted(pu, key=lambda r: r["ch5_width_ms"])
    print("\nPU drops sorted by input pulse width (stiff -> soft):")
    for r in pu_by_width:
        print(f"  S{r['signal']}: {r['ch5_180_g']:.0f} G / {r['ch5_width_ms']:.2f} ms "
              f"(T = {r['t_ch5']:.3f})")

    # ---------------- figures ------------------------------------------
    # Fig 1: input pulse + cumulative velocity, felt vs PU
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    for row, cond in enumerate(CONDITIONS):
        rows = per_cond[cond["key"]]
        for r in rows:
            s = r["series"]
            axes[row, 0].plot(s["t_ms"], s["ch5_180_g"], lw=1.1, label=f"S{r['signal']}")
            axes[row, 1].plot(s["t_ms"], s["v_ms"], lw=1.1, label=f"S{r['signal']}")
        axes[row, 0].set(xlabel="time (ms)", ylabel="CH5 CFC-180 (G)",
                         title=f"{cond['label']}: base-plate input pulse")
        axes[row, 1].set(xlabel="time (ms)", ylabel="cumulative Δv (m/s)",
                         title=f"{cond['label']}: velocity change (full pulse)")
        axes[row, 1].axhline(5.47, color="k", ls=":", lw=1.2, label="free fall, 60 in")
        for ax in axes[row]:
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)
    fig.suptitle("bpx68c, 5 + 5 drops: input pulse on the two absorber stacks")
    fig.tight_layout()
    fig.savefig(FIG / "01_input_pulses.png", dpi=130)
    plt.close(fig)

    # Fig 2: transmissibility + output-vs-input
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))
    ax = axes[0]
    for k, cond in enumerate(CONDITIONS):
        rows = per_cond[cond["key"]]
        tvals = arr(rows, "t_ch5")
        ax.plot(np.full(len(tvals), k) + np.linspace(-0.08, 0.08, len(tvals)), tvals,
                "o", ms=7, color=cond["color"])
        ax.hlines(tvals.mean(), k - 0.2, k + 0.2, color=cond["color"], lw=2.5,
                  label=f"{cond['label']}: T = {tvals.mean():.3f} (CV {cv(tvals):.1f}%)")
    ax.axhline(1.0, color="k", ls=":", lw=1.2)
    ax.set(xticks=[0, 1], xticklabels=[c["label"] for c in CONDITIONS],
           ylabel="T = TOP/CH5 (CFC-180)", title="transmissibility per drop")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    ax = axes[1]
    lims = [0, 1.1 * max(arr(felt, "ch5_180_g").max(), arr(felt, "top_180_g").max())]
    for cond in CONDITIONS:
        rows = per_cond[cond["key"]]
        ax.plot(arr(rows, "ch5_180_g"), arr(rows, "top_180_g"), "o", ms=7,
                color=cond["color"], label=cond["label"])
    ax.plot(lims, lims, "k:", lw=1.2, label="T = 1")
    ax.set(xlabel="CH5 input CFC-180 (G)", ylabel="TOP output CFC-180 (G)",
           title="output vs input (per drop)", xlim=lims, ylim=lims)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.suptitle("bpx68c: transmissibility on the two absorber stacks")
    fig.tight_layout()
    fig.savefig(FIG / "02_transmissibility.png", dpi=130)
    plt.close(fig)

    # Fig 3: raw head-room per drop
    fig, ax = plt.subplots(figsize=(10, 5.2))
    width = 0.38
    for k, cond in enumerate(CONDITIONS):
        rows = per_cond[cond["key"]]
        x = np.arange(len(rows)) + (k - 0.5) * width
        ax.bar(x, 100 * arr(rows, "ch5_frac_fs"), width=width, color=cond["color"],
               alpha=0.75, label=cond["label"])
    ax.axhline(100 / 3, color="k", ls=":", lw=1.2, label="FS/3 head-room target")
    ax.set(xticks=np.arange(5), xticklabels=[f"drop {k}" for k in range(1, 6)],
           ylabel="CH5 raw |peak| (% of 9,443 G FS)",
           title="bpx68c: base-sensor head-room, felt+cardboard vs polyurethane")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "03_headroom.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary --------------------------
    strip = lambda rows: [{k: v for k, v in r.items() if k != "series"} for r in rows]
    summary = {
        "specimen": "bpx68c",
        "sessions": {
            "felt": {"session_id": "bpx68c - 60 in - 4 flt 1 crdbrd",
                     "label": "4 felt + 1 cardboard", "date": "2026-07-30"},
            "pu": {"session_id": "bpx68c - Polyurethane Rubber",
                   "label": "polyurethane rubber", "date": "2026-07-30"},
        },
        "per_capture": {k: strip(v) for k, v in per_cond.items()},
        "comparison": comparison,
    }
    with open(FIG / "pu_vs_felt_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
