#!/usr/bin/env python3
"""Transmissibility trace figure for the manuscript (Methods).

Regenerates, from data, the trace figure on hidden slide 25 of the group
deck: one commissioning drop (TP4 session "57vqhX 60 in - 4 felt 1 crdbrd",
2026-07-28, event 50; 60 in drop onto the earlier stack of four felt pads
and one cardboard sheet, not the campaign polyurethane surface).

Capture: TP4 time-domain export, 1.25 MHz over a 20 ms window.
CH2, CH3, CH4 = triaxial top-vertex accelerometer (X, Y, Z), CH5 =
single-axis base-plate accelerometer (input and trigger), all in G.

Processing follows the deck's own recipe (``make_teaching_figures.py``,
commit 90a0658 on ``claude/issue-94-20260817-1700``), which is the
corrected SAE J211/1 CFC filter the manuscript describes:
``butter(2, 2.0775*CFC, fs=fs)`` applied forward and backward
(``filtfilt``), so the two-pass corner sits at the CFC corner. Baseline
is each channel's median over the quiet pre-trigger window (first
0.18 ms). The top-vertex response is the magnitude of the three
filtered axes. Transmissibility is the ratio of the peak top-vertex
magnitude to the peak absolute base acceleration at the same filter class.

For comparison the JSON also records the same ratios under the older
in-house filter (single-pass corner 1.65*CFC, the ~20 % narrow variant)
with a full-record median baseline.

Usage:
    python scripts/figures/build_transmissibility_trace_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "manuscript" / "data" / "57vqhX_Signal50.csv"
OUT_DIR = ROOT / "figures" / "analysis"
STEM = "transmissibility-trace-57vqhX-drop50"

HEADER_LINES = 10      # 9 metadata lines + the column-name line
PRETRIGGER_S = 0.00018  # quiet window before the impact (deck recipe)
WINDOW_MS = (-0.3, 3.0)  # clipped to the record start (about -0.26 ms)

BASE_COLOR = "#2a78d6"  # base plate (input)
TOP_COLOR = "#eb6834"   # top vertex (transmitted)
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e6e4de"


def j211(x: np.ndarray, cfc: int, fs: float) -> np.ndarray:
    """SAE J211/1 CFC filter, two-pass corner at the CFC corner."""
    b, a = signal.butter(2, 2.0775 * cfc, fs=fs)
    return signal.filtfilt(b, a, x)


def legacy(x: np.ndarray, cfc: int, fs: float) -> np.ndarray:
    """Older in-house variant: single-pass corner 1.65*CFC (narrow)."""
    b, a = signal.butter(2, {180: 300.0, 1000: 1650.0}[cfc], fs=fs)
    return signal.filtfilt(b, a, x)


def ratios(t, ch, filt, fs, baseline):
    out = {}
    chb = [x - baseline(x) for x in ch]
    for cfc in (180, 1000):
        base = filt(chb[3], cfc, fs)
        top = np.sqrt(sum(filt(c, cfc, fs) ** 2 for c in chb[:3]))
        i_in = int(np.argmax(np.abs(base)))
        i_out = int(np.argmax(top))
        out[cfc] = {
            "base_peak_g": float(abs(base[i_in])),
            "top_peak_g": float(top[i_out]),
            "ratio": float(top[i_out] / abs(base[i_in])),
            "t_base_peak_ms": float(t[i_in] * 1e3),
            "t_top_peak_ms": float(t[i_out] * 1e3),
            "base": base,
            "top": top,
        }
    return out


def main() -> None:
    d = np.genfromtxt(CSV, delimiter=",", skip_header=HEADER_LINES,
                      usecols=(0, 1, 2, 3, 4))
    t = d[:, 0]
    fs = 1.0 / float(np.median(np.diff(t)))
    ch = [d[:, k] for k in range(1, 5)]
    pre = t < PRETRIGGER_S

    res = ratios(t, ch, j211, fs, lambda x: np.median(x[pre]))
    old = ratios(t, ch, legacy, fs, lambda x: np.median(x))

    # Time zero: CFC-1000 base trace first reaches 5 % of its peak.
    b1000 = res[1000]["base"]
    i0 = int(np.argmax(np.abs(b1000) > 0.05 * np.max(np.abs(b1000))))
    tm = (t - t[i0]) * 1e3
    sel = (tm > WINDOW_MS[0]) & (tm < WINDOW_MS[1])

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "TeX Gyre Termes",
                       "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7,
        "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.linewidth": 0.6, "axes.edgecolor": INK2,
        "xtick.color": INK2, "ytick.color": INK2,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    fig, axes = plt.subplots(2, 1, figsize=(3.4, 3.7), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.115,
                        hspace=0.16)

    labels = {
        180: ("(a) CFC-180, reporting class",
              r"$t_{{180}}$ = {top:.0f} / {base:.0f} = {r:.3f}"),
        1000: ("(b) CFC-1000, diagnostic class",
               "ratio = {top:.0f} / {base:.0f} = {r:.3f}"),
    }
    for ax, cfc in zip(axes, (180, 1000)):
        r = res[cfc]
        ax.axhline(0, color=INK2, lw=0.5, zorder=1)
        ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
        ax.plot(tm[sel], r["base"][sel], color=BASE_COLOR, lw=1.2,
                label="Base plate (input)", zorder=3)
        ax.plot(tm[sel], r["top"][sel], color=TOP_COLOR, lw=1.2,
                ls=(0, (4, 1.6)), label="Top vertex (magnitude)", zorder=4)
        # Peak callouts
        i_in = int(np.argmax(np.abs(r["base"])))
        i_out = int(np.argmax(r["top"]))
        ax.plot(tm[i_in], abs(r["base"][i_in]), "o", ms=4, mfc="white",
                mec=BASE_COLOR, mew=1.0, zorder=5)
        ax.plot(tm[i_out], r["top"][i_out], "s", ms=4, mfc="white",
                mec=TOP_COLOR, mew=1.0, zorder=5)
        ymax = max(r["top"][sel].max(), np.abs(r["base"][sel]).max())
        ax.annotate(f"{r['top_peak_g']:.0f} G", xy=(tm[i_out], r["top"][i_out]),
                    xytext=(5, 3), textcoords="offset points", fontsize=7,
                    color=INK, ha="left", va="bottom")
        ax.annotate(f"{r['base_peak_g']:.0f} G", xy=(tm[i_in], abs(r["base"][i_in])),
                    # Inside the broad CFC-180 pulse; left of the narrow
                    # CFC-1000 pulse, where neither trace reaches this level.
                    xytext=(0, -7) if cfc == 180 else (-6, 0),
                    textcoords="offset points", fontsize=7, color=INK,
                    ha="center" if cfc == 180 else "right",
                    va="top" if cfc == 180 else "center")
        title, ratio_fmt = labels[cfc]
        ax.text(0.99, 0.97, title, transform=ax.transAxes, ha="right",
                va="top", fontsize=7.5, color=INK)
        ax.text(0.99, 0.84, ratio_fmt.format(top=r["top_peak_g"],
                                             base=r["base_peak_g"],
                                             r=r["ratio"]),
                transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
                color=INK)
        ax.set_ylim(-0.12 * ymax, 1.45 * ymax)
        ax.set_ylabel("Acceleration (G)")
    axes[1].legend(loc="center right", bbox_to_anchor=(1.0, 0.45),
                   frameon=False, handlelength=2.4, borderaxespad=0.2)
    axes[1].set_xlabel("Time after impact onset (ms)")
    axes[1].set_xlim(max(WINDOW_MS[0], tm[0]), WINDOW_MS[1])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # No CreationDate, so a rerun reproduces the committed PDF byte for byte.
    fig.savefig(OUT_DIR / f"{STEM}.pdf", metadata={"CreationDate": None})
    fig.savefig(OUT_DIR / f"{STEM}.png", dpi=200)
    plt.close(fig)

    def strip(rr):
        return {str(k): {kk: vv for kk, vv in v.items()
                         if kk not in ("base", "top")} for k, v in rr.items()}

    summary = {
        "source_csv": "manuscript/data/57vqhX_Signal50.csv",
        "session": "57vqhX 60 in - 4 felt 1 crdbrd",
        "session_date": "2026-07-28",
        "event": 50,
        "drop_height_in": 60,
        "surface": "four felt pads and one cardboard sheet (commissioning stack)",
        "sample_rate_hz": fs,
        "record_ms": float((t[-1] - t[0]) * 1e3),
        "channels": {"CH2": "top vertex X (G)", "CH3": "top vertex Y (G)",
                     "CH4": "top vertex Z (G)",
                     "CH5": "base plate, single axis, input and trigger (G)"},
        "filter": "SAE J211/1 CFC: butter(2, 2.0775*CFC) forward and backward",
        "baseline": "per-channel median over t < 0.18 ms (pre-trigger)",
        "time_zero": "CFC-1000 base trace first reaches 5 % of its peak",
        "t_zero_s_in_record": float(t[i0]),
        "corrected_j211": strip(res),
        "legacy_1p65cfc_fullmedian": strip(old),
        "t180": round(res[180]["ratio"], 4),
        "cfc1000_ratio": round(res[1000]["ratio"], 4),
        "seat_gauge_cfc1000_over_cfc180": round(res[1000]["ratio"] / res[180]["ratio"], 4),
    }
    (OUT_DIR / f"{STEM}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("t180", "cfc1000_ratio",
                                              "seat_gauge_cfc1000_over_cfc180")}))
    for k in ("180", "1000"):
        c = summary["corrected_j211"][k]
        print(f"CFC-{k}: base {c['base_peak_g']:.1f} G, top {c['top_peak_g']:.1f} G, "
              f"ratio {c['ratio']:.4f}; legacy ratio "
              f"{summary['legacy_1p65cfc_fullmedian'][k]['ratio']:.4f}")


if __name__ == "__main__":
    main()
