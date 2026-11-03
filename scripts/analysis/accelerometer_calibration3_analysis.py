#!/usr/bin/env python3
"""Five-channel CH4-vs-CH5 cross-calibration with a properly-ranged single-axis
(issue #71).

@ctrhjk posted a **fourth** drop-tower series (PR #74 comment 4673864934), TP4
session name "AC3", recorded 06/10/2026. It acts on the single open blocker from
the previous (``accelerometer_calibration2_analysis``) series: CH1 (the
high-sensitivity 11.61 mV/G single-axis) hard-clipped on every drop because, even
after moving it to the 10 V range, its full scale is only ~861 G while the raw
impact transient is several thousand G.

The fix in this run is to add a **second, much lower-sensitivity single-axis
accelerometer on CH5** (1.059 mV/G -> 9442.9 G full scale on 10 V) next to the
others, on the very left. Now there are two single-axis units to compare against
the tri-axis Z (CH4), which is the reference:

* **CH5 vs CH4** -- the real cross-calibration. Both are unclipped and co-located,
  so the slope should land near 1:1 and finally give a trustworthy single-vs-tri
  factor.
* **CH1 vs CH5 / CH1 vs CH4** -- diagnoses *why* CH1 clips. CH1 and CH5 are both
  single-axis and co-located, the only difference being sensitivity/range, so CH5
  shows what CH1 *would* read if it had enough range.

Acquisition settings (from @ctrhjk, PR comment 4673864934), all on a 10 V range,
CH4 the only trigger source:

==== ============= ============ =========== =============
Ch   Sensor        Full scale   Sensitivity Trigger
==== ============= ============ =========== =============
CH1  single-axis    861.3 G      11.61 mV/G  none
CH2  tri-axis X   14492.8 G       0.690 mV/G  none
CH3  tri-axis Y   14992.5 G       0.667 mV/G  none
CH4  tri-axis Z   13624.0 G       0.734 mV/G 1000 G
CH5  single-axis   9442.9 G       1.059 mV/G  none
==== ============= ============ =========== =============

200 ms record, 25 000 samples, 125 kHz, 2 %/4 ms pre-trigger -- same TP4 format as
the earlier series, plus the extra CH5 column. The amplitude is swept by drop
height (10, 15, 20 in; 5 in was too low to trigger), five repeats each, giving a
real lever arm for the regression. Files are ``Test_{height}in_{rep}.csv``.

The script reuses the SAE J211 CFC-180 / CFC-1000 + impact-windowing machinery
from ``accelerometer_tuning_analysis`` (CH4 still column index 3, so the impact
locator is unchanged), with a 5-channel loader:

1. Parses the 5-channel TP4 time-domain exports.
2. Locates the impact from the CH4 peak in the first ~10 ms and takes each
   channel's filtered peak in a +/-1 ms window around it.
3. Cross-calibrates CH5 vs CH4 (primary) and CH1 vs CH4 (clip-limited) with
   zero-intercept fits, and tracks the per-height amplitude sweep.
4. Flags CH1 full-scale clipping and confirms CH5 stays well within range.

Outputs go to ``docs/figures/accelerometer-calibration-3/`` and
``data/drop-tests/accelerometer-calibration-3/``.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from accelerometer_tuning_analysis import (
    IMPACT_SEARCH_MS,
    IMPACT_WINDOW_MS,
    cfc_filter,
    impact_index,
    signed_peak,
    windowed_signed_peak,
)

# --------------------------------------------------------------------------- #
# Paths / metadata
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "drop-tests" / "accelerometer-calibration-3" / "raw"
OUT_DATA = ROOT / "data" / "drop-tests" / "accelerometer-calibration-3"
FIG_DIR = ROOT / "docs" / "figures" / "accelerometer-calibration-3"

# Five channels in this series (CH5 = added low-sensitivity single-axis).
CHANNELS = ["CH1", "CH2", "CH3", "CH4", "CH5"]

CH_LABELS = {
    "CH1": "CH1 (single-axis, 861.3 G / 11.61 mV/G)",
    "CH2": "CH2 (tri-axis X)",
    "CH3": "CH3 (tri-axis Y)",
    "CH4": "CH4 (tri-axis Z, impact axis / reference)",
    "CH5": "CH5 (single-axis, 9442.9 G / 1.059 mV/G)",
}

# Reported full scales (10 V range / sensitivity) for the clip/range tests.
FULL_SCALE_G = {
    "CH1": 861.3,
    "CH2": 14492.8,
    "CH3": 14992.5,
    "CH4": 13624.0,
    "CH5": 9442.9,
}


def height_rep(path: Path) -> tuple[int, int]:
    m = re.search(r"_(\d+)in_(\d+)", path.name)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def load_time_domain_5ch(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, data[N,5]) from a 5-channel TP4 time-domain export.

    Same 4-line + header TP4 format as the earlier series, but with an extra
    ``CH5 Acc (G's)`` column, so we read columns 0..5 rather than 0..4.
    """
    lines = path.read_text().splitlines()
    start = next(i for i, ln in enumerate(lines)
                 if ln.startswith("Time (sec)")) + 1
    arr = np.genfromtxt(lines[start:], delimiter=",", usecols=(0, 1, 2, 3, 4, 5))
    arr = arr[~np.isnan(arr[:, 0])]
    return arr[:, 0], arr[:, 1:6]


def zero_intercept_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Zero-intercept slope of y on x with its standard error."""
    slope = float(np.dot(x, y) / np.dot(x, x))
    resid = y - slope * x
    n = len(x)
    s2 = float(np.dot(resid, resid) / (n - 1)) if n > 1 else float("nan")
    se = float(np.sqrt(s2 / np.dot(x, x))) if n > 1 else float("nan")
    return slope, se


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #
def plot_ch4_ch5_overlay(name: str, t, data, fs) -> None:
    """CH4 (reference) vs CH5 (new single-axis) raw + CFC-180 for one drop.

    The success plot: both are unclipped, co-located and time-aligned, and their
    CFC-180 impact pulses nearly coincide.
    """
    tms = t * 1e3
    c4 = cfc_filter(data[:, 3], fs, 180.0)
    c5 = cfc_filter(data[:, 4], fs, 180.0)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tms, data[:, 3], lw=0.4, color="C1", alpha=0.30, label="CH4 raw")
    ax.plot(tms, c4, lw=1.8, color="C1", label="CH4 CFC-180 (reference)")
    ax.plot(tms, data[:, 4], lw=0.4, color="C2", alpha=0.30, label="CH5 raw")
    ax.plot(tms, c5, lw=1.8, color="C2", label="CH5 CFC-180")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Acceleration (G)")
    ax.set_xlim(0, 12)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    ax.set_title(
        f"Co-located metal mount, {name}: CH5 (new single-axis) tracks the CH4 "
        f"reference -- both unclipped and time-aligned",
        fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch4_ch5_overlay.png", dpi=110)
    plt.close(fig)


def plot_ch1_clipping(name: str, t, data) -> None:
    """CH1 (clipping) vs CH5 (clean) at the impact, on a shared axis.

    Both are single-axis and co-located; CH5 shows the true raw transient (~a few
    thousand G) that CH1 cannot capture because its 861 G range rails it.
    """
    k = int(np.searchsorted(t, IMPACT_SEARCH_MS * 1e-3))
    k = int(np.argmax(np.abs(data[:k, 3])))  # CH4 impact index
    lo = max(0, k - 80)
    hi = min(len(t), k + 320)
    sl = slice(lo, hi)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t[sl] * 1e3, data[sl, 4], marker=".", ms=2.5, lw=0.8, color="C2",
            label="CH5 raw (9442.9 G range, clean)")
    ax.plot(t[sl] * 1e3, data[sl, 0], marker=".", ms=2.5, lw=0.8, color="C0",
            label="CH1 raw (clips)")
    ax.axhline(FULL_SCALE_G["CH1"], color="C0", ls="--", lw=1,
               label=f"CH1 +{FULL_SCALE_G['CH1']:.0f} G full scale")
    ax.axhline(-FULL_SCALE_G["CH1"], color="C0", ls="--", lw=1)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Single-axis acceleration (G)")
    ax.set_title(
        f"Why CH1 clips ({name}): its 861 G range cannot hold the raw transient "
        f"that the co-located CH5 measures cleanly",
        fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch1_clipping.png", dpi=110)
    plt.close(fig)


def plot_amplitude_sweep(rows: list[dict]) -> None:
    """CH4, CH5 (clean) impact peaks grow with height; CH1 is rail-corrupted."""
    heights = sorted({r["height_in"] for r in rows})
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for ch, color, marker in (("CH4", "C1", "o"), ("CH5", "C2", "D"),
                              ("CH1", "C0", "s")):
        xs, ys = [], []
        for h in heights:
            grp = [abs(r[f"{ch}_cfc180_win"]) for r in rows
                   if r["height_in"] == h]
            xs.append(h)
            ys.append(np.mean(grp))
            ax.scatter([h] * len(grp), grp, s=26, color=color, alpha=0.5, zorder=3)
        ax.plot(xs, ys, color=color, lw=1.5, marker=marker,
                label=f"{ch} mean CFC-180 impact peak")
    ax.set_xlabel("Drop height (in)")
    ax.set_ylabel("|CFC-180| impact-window peak (G)")
    ax.set_xticks(heights)
    ax.set_title("Amplitude sweep: CH4 and CH5 scale together with height; CH1 is "
                 "rail-corrupted", fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "amplitude_sweep.png", dpi=110)
    plt.close(fig)


def plot_regression(rows: list[dict], slope54: float, se54: float,
                    slope14: float, se14: float) -> None:
    """CH5-vs-CH4 (primary) and CH1-vs-CH4 (clip-limited) cross-calibration."""
    x = np.array([abs(r["CH4_cfc180_win"]) for r in rows])
    y5 = np.array([abs(r["CH5_cfc180_win"]) for r in rows])
    y1 = np.array([abs(r["CH1_cfc180_win"]) for r in rows])
    markers = {10: "o", 15: "^", 20: "s"}
    fig, ax = plt.subplots(figsize=(7.8, 6.2))
    for h in sorted(markers):
        m = np.array([r["height_in"] == h for r in rows])
        ax.scatter(x[m], y5[m], s=55, color="C2", marker=markers[h], zorder=3,
                   label=f"CH5, {h} in")
        ax.scatter(x[m], y1[m], s=45, color="C0", marker=markers[h], zorder=3,
                   alpha=0.7, label=f"CH1, {h} in")
    xx = np.linspace(0, x.max() * 1.05, 50)
    ax.plot(xx, slope54 * xx, color="C2", lw=1.6,
            label=f"CH5 = {slope54:.3f}(+/-{se54:.3f}) x CH4")
    ax.plot(xx, slope14 * xx, color="C0", lw=1.4, ls="-.",
            label=f"CH1 = {slope14:.3f}(+/-{se14:.3f}) x CH4 (clipped)")
    ax.plot(xx, xx, color="0.6", lw=1.0, ls="--", label="1:1")
    ax.set_xlabel("CH4 tri-axis Z, CFC-180 impact-window peak (G)")
    ax.set_ylabel("Single-axis, CFC-180 impact-window peak (G)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_title("CH5 vs CH4 lands near 1:1 (trustworthy); CH1 stays clip-limited",
                 fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7.5, loc="upper left", ncol=2)
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
        t, data = load_time_domain_5ch(path)
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
        peak_times: dict[str, float] = {}
        for ci, ch in enumerate(CHANNELS):
            row[f"{ch}_raw"] = signed_peak(data[:, ci])
            p180, tp = windowed_signed_peak(filt180[ch], t, impact_idx, half_win)
            p1000, _ = windowed_signed_peak(filt1000[ch], t, impact_idx, half_win)
            row[f"{ch}_cfc180_win"] = p180
            row[f"{ch}_cfc1000_win"] = p1000
            peak_times[ch] = tp
            # A channel clips when its raw excursion reaches +/-full scale (2%).
            row[f"{ch}_clipped"] = (
                max(abs(data[:, ci].max()), abs(data[:, ci].min()))
                > 0.98 * FULL_SCALE_G[ch]
            )
        # CH5 vs CH4 alignment (single-sample agreement expected if co-located).
        row["CH5_minus_CH4_peak_us"] = (peak_times["CH5"]
                                        - peak_times["CH4"]) * 1e6
        tri = np.sqrt(filt180["CH2"] ** 2 + filt180["CH3"] ** 2
                      + filt180["CH4"] ** 2)
        tri_win, _ = windowed_signed_peak(tri, t, impact_idx, half_win)
        row["tri_resultant_cfc180_win"] = float(abs(tri_win))
        c4 = abs(row["CH4_cfc180_win"])
        row["CH5_over_CH4_cfc180_win"] = (
            abs(row["CH5_cfc180_win"]) / c4 if c4 > 1e-6 else float("nan"))
        row["CH1_over_CH4_cfc180_win"] = (
            abs(row["CH1_cfc180_win"]) / c4 if c4 > 1e-6 else float("nan"))
        rows.append(row)

    assert fs is not None

    # Primary cross-calibration: CH5 vs CH4 (both unclipped) -> trustworthy.
    x = np.array([abs(r["CH4_cfc180_win"]) for r in rows])
    y5 = np.array([abs(r["CH5_cfc180_win"]) for r in rows])
    y1 = np.array([abs(r["CH1_cfc180_win"]) for r in rows])
    slope54, se54 = zero_intercept_fit(x, y5)
    slope14, se14 = zero_intercept_fit(x, y1)  # CH1 clip-limited (not trustworthy)

    # Figures (use a representative 20 in drop for the single-event panels).
    rep_name = next(name for name in events if name.startswith("Test_20in"))
    t_r, d_r, fs_r = events[rep_name]
    plot_ch4_ch5_overlay(rep_name.replace(".csv", ""), t_r, d_r, fs_r)
    plot_ch1_clipping(rep_name.replace(".csv", ""), t_r, d_r)
    plot_amplitude_sweep(rows)
    plot_regression(rows, slope54, se54, slope14, se14)

    # Summary CSV.
    cols = (
        ["height_in", "rep", "impact_t_ms"]
        + [f"{ch}_raw" for ch in CHANNELS]
        + [f"{ch}_cfc1000_win" for ch in CHANNELS]
        + [f"{ch}_cfc180_win" for ch in CHANNELS]
        + [f"{ch}_clipped" for ch in CHANNELS]
        + ["tri_resultant_cfc180_win", "CH5_minus_CH4_peak_us",
           "CH5_over_CH4_cfc180_win", "CH1_over_CH4_cfc180_win"]
    )
    out_csv = OUT_DATA / "calibration_summary.csv"
    with out_csv.open("w") as f:
        f.write(",".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: (r["height_in"], r["rep"])):
            f.write(",".join(_fmt(r[c]) for c in cols) + "\n")

    # Console summary.
    print(f"Sampling rate: {fs/1e3:.1f} kHz, window {len(t_r)} samples")
    print("\nh/in rep t_imp/ms  CH1_180w CH4_180w CH5_180w  CH5/CH4 CH1/CH4 "
          "lag_us  clip(C1,C5)")
    for r in sorted(rows, key=lambda r: (r["height_in"], r["rep"])):
        print(f"{r['height_in']:>4} {r['rep']:>3} {r['impact_t_ms']:7.2f}  "
              f"{r['CH1_cfc180_win']:8.0f} {r['CH4_cfc180_win']:8.0f} "
              f"{r['CH5_cfc180_win']:8.0f}  {r['CH5_over_CH4_cfc180_win']:6.3f} "
              f"{r['CH1_over_CH4_cfc180_win']:6.3f} "
              f"{r['CH5_minus_CH4_peak_us']:6.0f}  "
              f"{'Y' if r['CH1_clipped'] else 'n'},"
              f"{'Y' if r['CH5_clipped'] else 'n'}")
    print("\nPer-height mean CFC-180 impact peak (clean reference channels):")
    for h in sorted({r["height_in"] for r in rows}):
        g4 = [abs(r["CH4_cfc180_win"]) for r in rows if r["height_in"] == h]
        g5 = [abs(r["CH5_cfc180_win"]) for r in rows if r["height_in"] == h]
        print(f"  {h:>2} in : CH4 {np.mean(g4):6.1f} +/- {np.std(g4, ddof=1):4.1f} "
              f"G | CH5 {np.mean(g5):6.1f} +/- {np.std(g5, ddof=1):4.1f} G "
              f"(n={len(g4)})")
    r54 = [r["CH5_over_CH4_cfc180_win"] for r in rows]
    print(f"\nPrimary CH5-vs-CH4 zero-intercept fit (both unclipped): "
          f"CH5 = {slope54:.3f} (+/-{se54:.3f}) x CH4")
    print(f"  per-drop CH5/CH4 ratio: {np.mean(r54):.3f} +/- "
          f"{np.std(r54, ddof=1):.3f} (SD)")
    print(f"CH1-vs-CH4 zero-intercept fit (CH1 clip-limited, NOT trustworthy): "
          f"CH1 = {slope14:.3f} (+/-{se14:.3f}) x CH4")
    n_clip = sum(r["CH1_clipped"] for r in rows)
    print(f"\nCH1 clipped on {n_clip}/{len(rows)} drops (861 G range too small); "
          f"CH5 clipped on {sum(r['CH5_clipped'] for r in rows)}/{len(rows)}.")
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
