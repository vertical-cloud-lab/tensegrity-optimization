#!/usr/bin/env python3
"""Corrected-sensitivity, metal-mount accelerometer cross-calibration (issue #71).

@ctrhjk posted a **third** drop-tower series (PR #74 comment 4664234492), TP4
session name "Accelerometer Callibartion 2", recorded 06/09/2026. It is the run
that acts on the two recommendations from the previous
(`accelerometer_calibration_analysis`) co-located series:

1. **The per-channel sensitivities were re-entered from the calibration
   certificates.** The 06/08 series used the placeholder values 0.25 mV/G (CH1)
   and 1.0 mV/G (CH2-4); the certificate values are CH1 = 11.61 mV/G,
   CH2 = 0.690, CH3 = 0.667, CH4 = 0.734 mV/G. (The old 0.25 mV/G CH1 entry was
   ``11.61 / 0.25 = 46x`` too small, which is what produced the spurious ~30x
   single-vs-tri ratio.)
2. **Both sensors are bolted to the bare metal load** (the acrylic plates were
   removed), on the same level ~1/4 in apart, single-axis on the left -- i.e. a
   stiffer, genuinely co-located mount.

Acquisition settings (from @ctrhjk, PR comment 4664234492), all on a 5 V range:

==== ============= ============ =========== =============
Ch   Sensor        Full scale   Sensitivity Trigger
==== ============= ============ =========== =============
CH1  single-axis    430.7 G      11.61 mV/G  430.66 G
CH2  tri-axis X    7246.4 G       0.690 mV/G 1000 G
CH3  tri-axis Y    7496.3 G       0.667 mV/G 1000 G
CH4  tri-axis Z    6812.0 G       0.734 mV/G 1000 G
==== ============= ============ =========== =============

200 ms record, 25 000 samples, 125 kHz, 2 %/4 ms pre-trigger -- same TP4 format as
the earlier series. The amplitude was **swept by drop height** (10, 15, 20 in;
5 in was too low to trigger), five repeats each, giving a real lever arm for the
regression. Files are ``Test_{height}in_{rep}.csv``.

The script reuses the SAE J211 CFC-180 / CFC-1000 + impact-windowing machinery
from ``accelerometer_tuning_analysis``:

1. Parses the TP4 time-domain exports.
2. Locates the impact from the CH4 (tri-axis impact axis) peak in the first ~10 ms
   and takes each channel's filtered peak in a +/-1 ms window around it.
3. Flags CH1 full-scale clipping (the corrected 11.61 mV/G sensitivity drops CH1's
   full scale to only 430.7 G, so it now rails on every usable drop).
4. Cross-calibrates CH1 vs CH4 and tracks the per-height amplitude sweep, writing
   ``calibration_summary.csv`` + figures.

Outputs go to ``docs/figures/accelerometer-calibration-2/`` and
``data/drop-tests/accelerometer-calibration-2/``.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from accelerometer_tuning_analysis import (
    CHANNELS,
    IMPACT_SEARCH_MS,
    IMPACT_WINDOW_MS,
    cfc_filter,
    impact_index,
    load_time_domain,
    signed_peak,
    windowed_signed_peak,
)

# --------------------------------------------------------------------------- #
# Paths / metadata
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "drop-tests" / "accelerometer-calibration-2" / "raw"
OUT_DATA = ROOT / "data" / "drop-tests" / "accelerometer-calibration-2"
FIG_DIR = ROOT / "docs" / "figures" / "accelerometer-calibration-2"

# Certificate sensitivities (mV/G) re-entered for this series, with full scales
# (5 V range / sensitivity) reported by @ctrhjk.
CH_LABELS = {
    "CH1": "CH1 (single-axis, 430.7 G / 11.61 mV/G)",
    "CH2": "CH2 (tri-axis X)",
    "CH3": "CH3 (tri-axis Y)",
    "CH4": "CH4 (tri-axis Z, impact axis)",
}

# Corrected single-axis full scale: 5 V range / 11.61 mV/G = 430.7 G. The observed
# hard digital rail sits at ~441 G (the part's actual +full scale); use the
# reported nominal value for the clip test with a small margin.
CH1_FULL_SCALE_G = 430.7

# Old vs certificate single-axis sensitivity, for the scale-error consistency note.
CH1_SENS_OLD_MVG = 0.25
CH1_SENS_CERT_MVG = 11.61


def height_rep(path: Path) -> tuple[int, int]:
    m = re.search(r"_(\d+)in_(\d+)", path.name)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #
def plot_overlay(name: str, t, data, fs) -> None:
    """CH1 vs CH4 (raw + CFC-180) for one drop on twin axes.

    Shows the two channels are time-aligned on the impact, but that the
    single-axis channel hard-clips at its (now far too low) +full scale while the
    tri-axis Z is a clean pulse.
    """
    tms = t * 1e3
    c1 = cfc_filter(data[:, 0], fs, 180.0)
    c4 = cfc_filter(data[:, 3], fs, 180.0)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tms, data[:, 0], lw=0.4, color="C0", alpha=0.35, label="CH1 raw")
    ax.plot(tms, c1, lw=1.6, color="C0", label="CH1 CFC-180")
    ax.axhline(CH1_FULL_SCALE_G, color="C0", ls=":", lw=1,
               label="CH1 +430.7 G full scale")
    ax.set_ylabel("CH1 single-axis (G)", color="C0")
    ax.tick_params(axis="y", labelcolor="C0")
    ax.set_xlabel("Time (ms)")
    ax.set_xlim(0, 12)
    ax.grid(alpha=0.3)

    ax2 = ax.twinx()
    ax2.plot(tms, data[:, 3], lw=0.4, color="C1", alpha=0.35, label="CH4 raw")
    ax2.plot(tms, c4, lw=1.6, color="C1", label="CH4 CFC-180")
    ax2.set_ylabel("CH4 tri-axis Z (G)", color="C1")
    ax2.tick_params(axis="y", labelcolor="C1")

    lines = [ln for ln in ax.get_lines() + ax2.get_lines()
             if not ln.get_label().startswith("_")]
    ax.legend(lines, [ln.get_label() for ln in lines], fontsize=8,
              loc="lower right", ncol=2)
    ax.set_title(
        f"Co-located metal mount, {name}: CH1 and CH4 are time-aligned, but CH1 "
        f"clips at its 430.7 G full scale (note independent axes)",
        fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch1_ch4_overlay.png", dpi=110)
    plt.close(fig)


def plot_clipping(name: str, t, data) -> None:
    """Zoom on CH1 raw at the impact to show the flat +full-scale clip plateau."""
    ch1 = data[:, 0]
    k = int(np.searchsorted(t, IMPACT_SEARCH_MS * 1e-3))
    k = int(np.argmax(ch1[:k]))  # positive-going clip at impact
    lo = max(0, k - 80)
    hi = min(len(t), k + 320)
    sl = slice(lo, hi)
    ceiling = float(np.max(ch1))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t[sl] * 1e3, ch1[sl], marker=".", ms=3, lw=0.8, color="C0")
    ax.axhline(ceiling, color="k", ls="--", lw=1,
               label=f"flat digital clip ~{ceiling:.0f} G")
    ax.axhline(CH1_FULL_SCALE_G, color="C3", ls=":", lw=1,
               label="reported 430.7 G full scale")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("CH1 single-axis acceleration (G)")
    ax.set_title(
        f"CH1 hard-clips flat at +full scale during the impact ({name}); the "
        f"corrected 11.61 mV/G sensitivity makes the 430.7 G range too small",
        fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch1_clipping.png", dpi=110)
    plt.close(fig)


def plot_amplitude_sweep(rows: list[dict]) -> None:
    """CH4 (clean) impact peak grows with drop height while CH1 rails flat."""
    heights = sorted({r["height_in"] for r in rows})
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for ch, color, marker in (("CH4", "C1", "o"), ("CH1", "C0", "s")):
        xs, ys = [], []
        for h in heights:
            grp = [abs(r[f"{ch}_cfc180_win"]) for r in rows if r["height_in"] == h]
            xs.append(h)
            ys.append(np.mean(grp))
            ax.scatter([h] * len(grp), grp, s=28, color=color, alpha=0.5, zorder=3)
        ax.plot(xs, ys, color=color, lw=1.5, marker=marker,
                label=f"{ch} mean CFC-180 impact peak")
    # CH1 raw clip ceiling reference
    clip = np.mean([r["CH1_raw_pos"] for r in rows])
    ax.axhline(clip, color="C0", ls=":", lw=1,
               label=f"CH1 raw clip ceiling ~{clip:.0f} G (full scale)")
    ax.set_xlabel("Drop height (in)")
    ax.set_ylabel("|CFC-180| impact-window peak (G)")
    ax.set_xticks(heights)
    ax.set_title("Amplitude sweep: CH4 scales cleanly with height; CH1's impact "
                 "is rail-limited", fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "amplitude_sweep.png", dpi=110)
    plt.close(fig)


def plot_regression(rows: list[dict], slope: float, se: float) -> None:
    """CH1-vs-CH4 cross-calibration over the height sweep (CH1 clip-limited)."""
    x = np.array([abs(r["CH4_cfc180_win"]) for r in rows])
    y = np.array([abs(r["CH1_cfc180_win"]) for r in rows])
    colors = {10: "C0", 15: "C2", 20: "C3"}
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for h in sorted(colors):
        m = [r["height_in"] == h for r in rows]
        ax.scatter(x[m], y[m], s=55, color=colors[h], zorder=3, label=f"{h} in")
    xx = np.linspace(0, x.max() * 1.05, 50)
    ax.plot(xx, slope * xx, color="0.3", lw=1.4,
            label=f"CH1 = {slope:.2f}(+/-{se:.2f}) x CH4 (CH1 clipped)")
    ax.plot(xx, xx, color="0.6", lw=1.0, ls="--", label="1:1")
    ax.set_xlabel("CH4 tri-axis Z, CFC-180 impact-window peak (G)")
    ax.set_ylabel("CH1 single-axis, CFC-180 impact-window peak (G)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_title("Sensitivity fix removes the ~30x error, but CH1 now clips -> "
                 "slope is not yet trustworthy", fontweight="bold", fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cross_calibration_regression.png", dpi=110)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.csv"), key=height_rep)
    assert files, f"no CSVs in {RAW_DIR}"

    rows: list[dict] = []
    half_win = IMPACT_WINDOW_MS * 1e-3
    events: dict[str, tuple] = {}
    fs = None
    for path in files:
        t, data = load_time_domain(path)
        fs = 1.0 / np.median(np.diff(t))
        h, rep = height_rep(path)
        events[path.name] = (t, data, fs)

        filt180 = {ch: cfc_filter(data[:, ci], fs, 180.0)
                   for ci, ch in enumerate(CHANNELS)}
        filt1000 = {ch: cfc_filter(data[:, ci], fs, 1000.0)
                    for ci, ch in enumerate(CHANNELS)}
        impact_idx = impact_index(data, t)

        row: dict = {"height_in": h, "rep": rep,
                     "impact_t_ms": float(t[impact_idx] * 1e3)}
        for ci, ch in enumerate(CHANNELS):
            row[f"{ch}_raw"] = signed_peak(data[:, ci])
            p180, _ = windowed_signed_peak(filt180[ch], t, impact_idx, half_win)
            p1000, _ = windowed_signed_peak(filt1000[ch], t, impact_idx, half_win)
            row[f"{ch}_cfc180_win"] = p180
            row[f"{ch}_cfc1000_win"] = p1000
        row["CH1_raw_pos"] = float(np.max(data[:, 0]))  # +full-scale clip plateau
        tri = np.sqrt(filt180["CH2"] ** 2 + filt180["CH3"] ** 2
                      + filt180["CH4"] ** 2)
        tri_win, _ = windowed_signed_peak(tri, t, impact_idx, half_win)
        row["tri_resultant_cfc180_win"] = float(abs(tri_win))
        c1 = abs(row["CH1_cfc180_win"])
        c4 = abs(row["CH4_cfc180_win"])
        row["CH1_over_CH4_cfc180_win"] = c1 / c4 if c4 > 1e-6 else float("nan")
        # CH1 clips when its +full-scale rail is reached (within 2%).
        row["CH1_clipped"] = row["CH1_raw_pos"] > 0.98 * CH1_FULL_SCALE_G
        rows.append(row)

    assert fs is not None

    # CH1-vs-CH4 zero-intercept fit over all drops (CH1 clip-limited -> lower bound).
    x = np.array([abs(r["CH4_cfc180_win"]) for r in rows])
    y = np.array([abs(r["CH1_cfc180_win"]) for r in rows])
    slope = float(np.dot(x, y) / np.dot(x, x))
    resid = y - slope * x
    n = len(rows)
    s2 = float(np.dot(resid, resid) / (n - 1)) if n > 1 else float("nan")
    se = float(np.sqrt(s2 / np.dot(x, x))) if n > 1 else float("nan")

    # Figures (use a representative 20 in drop for the single-event panels).
    rep_name = next(name for name in events if name.startswith("Test_20in"))
    t_r, d_r, fs_r = events[rep_name]
    plot_overlay(rep_name.replace(".csv", ""), t_r, d_r, fs_r)
    plot_clipping(rep_name.replace(".csv", ""), t_r, d_r)
    plot_amplitude_sweep(rows)
    plot_regression(rows, slope, se)

    # Summary CSV.
    cols = (
        ["height_in", "rep", "impact_t_ms"]
        + [f"{ch}_raw" for ch in CHANNELS]
        + ["CH1_raw_pos"]
        + [f"{ch}_cfc1000_win" for ch in CHANNELS]
        + [f"{ch}_cfc180_win" for ch in CHANNELS]
        + ["tri_resultant_cfc180_win", "CH1_over_CH4_cfc180_win", "CH1_clipped"]
    )
    out_csv = OUT_DATA / "calibration_summary.csv"
    with out_csv.open("w") as f:
        f.write(",".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: (r["height_in"], r["rep"])):
            f.write(",".join(_fmt(r[c]) for c in cols) + "\n")

    # Console summary.
    print(f"Sampling rate: {fs/1e3:.1f} kHz, window {len(t_r)} samples")
    print(f"CH1 sensitivity 0.25 -> 11.61 mV/G = "
          f"{CH1_SENS_CERT_MVG / CH1_SENS_OLD_MVG:.1f}x correction "
          f"(explains the prior ~30x); CH1 full scale now {CH1_FULL_SCALE_G:.1f} G")
    print("\nh/in rep  t_imp/ms  CH1_raw_pos  CH1_180w  CH4_180w  CH1/CH4  clip")
    for r in sorted(rows, key=lambda r: (r["height_in"], r["rep"])):
        print(f"{r['height_in']:>4} {r['rep']:>3}  {r['impact_t_ms']:8.2f}  "
              f"{r['CH1_raw_pos']:11.0f}  {r['CH1_cfc180_win']:8.0f}  "
              f"{r['CH4_cfc180_win']:8.0f}  {r['CH1_over_CH4_cfc180_win']:7.2f}  "
              f"{'YES' if r['CH1_clipped'] else ''}")
    print("\nPer-height mean CH4 CFC-180 impact peak (clean lever arm):")
    for h in sorted({r["height_in"] for r in rows}):
        g4 = [abs(r["CH4_cfc180_win"]) for r in rows if r["height_in"] == h]
        print(f"  {h:>2} in : {np.mean(g4):6.1f} +/- {np.std(g4, ddof=1):4.1f} G "
              f"(n={len(g4)})")
    print(f"\nCH1-vs-CH4 zero-intercept fit (CH1 clip-limited, lower bound): "
          f"CH1 = {slope:.2f} (+/-{se:.2f}) x CH4")
    print(f"\nWrote {out_csv.relative_to(ROOT)} and figures to "
          f"{FIG_DIR.relative_to(ROOT)}")


def _fmt(v) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


if __name__ == "__main__":
    main()
