#!/usr/bin/env python3
"""Co-located accelerometer cross-calibration (issue #71 follow-up).

@ctrhjk posted a second drop-tower series (PR #74) recorded on 06/08/2026 with
TP4 session name "Accelerometer callibaration". Unlike the 06/02/2026 "tuning"
series (where the sensors were swapped between positions), in this series **both
accelerometers are mounted directly on the bottom acrylic plate** — i.e. the
co-located, back-to-back arrangement we recommended, so the two sensors should see
the *same* rigid-body input and can finally be cross-calibrated.

Known acquisition settings (from @ctrhjk, PR comment 4663450421):

* ``CH1``      -> single-axis accelerometer: full-scale **20,000 G**, **0.25 mV/G**
* ``CH2..CH4`` -> tri-axis accelerometer:    full-scale **10,000 G**, **1.0 mV/G**
  (CH4 is its impact / drop-direction axis, as in the 06/02 series).

Files (event number is in the file name):

* ``500G_Signal5.csv``  -- trigger level 500 G. @ctrhjk raised the trigger after an
  early-measurement issue, so this event is a low-amplitude / aborted capture and
  is excluded from the cross-calibration regression.
* ``1000G_Signal{6,7,9,12,14,15,17}.csv`` -- trigger level 1000 G; seven repeated
  clean drops used for the cross-calibration.

The script:

1. Parses the TP4 time-domain exports (same format as the 06/02 series).
2. Applies the SAE J211 CFC-180 / CFC-1000 phaseless filter (reused from
   ``accelerometer_tuning_analysis``).
3. Locates the impact from the CH4 (tri-axis impact axis) peak in the first ~10 ms
   and takes each channel's filtered peak in a +/-1 ms window around it.
4. Cross-calibrates the single-axis (CH1) against the tri-axis impact axis (CH4)
   with a zero-intercept regression (slope = scale factor, with standard error).
5. Flags CH1 full-scale clipping and writes ``calibration_summary.csv`` + figures.

Outputs go to ``docs/figures/accelerometer-calibration/`` and
``data/drop-tests/accelerometer-calibration/``.
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
RAW_DIR = ROOT / "data" / "drop-tests" / "accelerometer-calibration" / "raw"
OUT_DATA = ROOT / "data" / "drop-tests" / "accelerometer-calibration"
FIG_DIR = ROOT / "docs" / "figures" / "accelerometer-calibration"

CH_LABELS = {
    "CH1": "CH1 (single-axis, 20 kG / 0.25 mV/G)",
    "CH2": "CH2 (tri-axis X)",
    "CH3": "CH3 (tri-axis Y)",
    "CH4": "CH4 (tri-axis Z, impact axis)",
}

# Single-axis full-scale clip (observed flat ceiling, see find CH1 clipping).
CH1_FULL_SCALE_G = 20000.0

# 500G_Signal5 is the low-amplitude / aborted capture (see module docstring); the
# seven 1000 G events are the clean repeated drops used for cross-calibration.
CALIBRATION_TRIGGER = "1000G"


def event_number(path: Path) -> int:
    m = re.search(r"Signal(\d+)", path.name)
    return int(m.group(1)) if m else -1


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #
def plot_overlay(name: str, t, data, fs) -> None:
    """CH1 vs CH4 (raw + CFC-180) for one event on twin axes.

    The two channels are co-located, so this shows (a) they are time-aligned on
    the impact and (b) the single-axis channel both clips during the impact and
    carries a large post-impact low-frequency excursion the tri-axis never sees.
    """
    tms = t * 1e3
    c1 = cfc_filter(data[:, 0], fs, 180.0)
    c4 = cfc_filter(data[:, 3], fs, 180.0)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tms, data[:, 0], lw=0.4, color="C0", alpha=0.35, label="CH1 raw")
    ax.plot(tms, c1, lw=1.6, color="C0", label="CH1 CFC-180")
    ax.axhline(CH1_FULL_SCALE_G, color="C0", ls=":", lw=1)
    ax.axhline(-CH1_FULL_SCALE_G, color="C0", ls=":", lw=1,
               label="CH1 +/-20 kG full scale")
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
        f"Co-located impact, {name}: CH1 and CH4 are time-aligned but on very "
        f"different scales (note independent axes)", fontweight="bold", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch1_ch4_calibration_overlay.png", dpi=110)
    plt.close(fig)


def plot_clipping(name: str, t, data) -> None:
    """Zoom on CH1 raw around the impact to show the +20 kG clip + ringing."""
    ch1 = data[:, 0]
    # Center on the impact (first strong CH4-correlated CH1 excursion), not on
    # the later negative ringing burst, so the +full-scale clip is visible.
    k = int(np.searchsorted(t, IMPACT_SEARCH_MS * 1e-3))
    k = int(np.argmax(ch1[:k]))  # first positive-going clip at impact
    lo = max(0, k - 60)
    hi = min(len(t), k + 360)
    sl = slice(lo, hi)
    ceiling = float(np.max(ch1))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t[sl] * 1e3, ch1[sl], marker=".", ms=3, lw=0.8, color="C0")
    ax.axhline(ceiling, color="k", ls="--", lw=1,
               label=f"positive clip ceiling ~{ceiling:.0f} G")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("CH1 single-axis acceleration (G)")
    ax.set_title(
        f"CH1 still clips at +full scale during the impact ({name}); the violent "
        f"+/-20 kG ringing is mount resonance", fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch1_clipping.png", dpi=110)
    plt.close(fig)


def plot_regression(rows: list[dict], slope: float, se: float) -> None:
    """Zero-intercept CH1-vs-CH4 cross-calibration over the clean drops."""
    cal = [r for r in rows if r["series"] == CALIBRATION_TRIGGER]
    x = np.array([abs(r["CH4_cfc180_win"]) for r in cal])
    y = np.array([abs(r["CH1_cfc180_win"]) for r in cal])
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(x, y, s=60, color="C3", zorder=3,
               label=f"{len(cal)} repeated 1000 G drops")
    xx = np.linspace(0, x.max() * 1.05, 50)
    ax.plot(xx, slope * xx, color="0.3", lw=1.6,
            label=f"CH1 = {slope:.1f}(+/-{se:.1f}) x CH4")
    for r in cal:
        ax.annotate(f"E{r['event']}",
                    (abs(r["CH4_cfc180_win"]), abs(r["CH1_cfc180_win"])),
                    textcoords="offset points", xytext=(6, -2), fontsize=8)
    ax.set_xlabel("CH4 tri-axis Z, CFC-180 impact-window peak (G)")
    ax.set_ylabel("CH1 single-axis, CFC-180 impact-window peak (G)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_title("Co-located cross-calibration: single-axis reads ~30x the "
                 "tri-axis", fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cross_calibration_regression.png", dpi=110)
    plt.close(fig)


def plot_repeatability(rows: list[dict]) -> None:
    """Per-event CH1 & CH4 impact-window peaks + their ratio (repeatability)."""
    cal = [r for r in rows if r["series"] == CALIBRATION_TRIGGER]
    evs = [r["event"] for r in cal]
    ch1 = [abs(r["CH1_cfc180_win"]) for r in cal]
    ch4 = [abs(r["CH4_cfc180_win"]) for r in cal]
    ratio = [r["CH1_over_CH4_cfc180_win"] for r in cal]
    x = np.arange(len(evs))
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12, 4.5))
    axL.bar(x - 0.2, ch1, 0.4, label="CH1 single-axis", color="C0")
    axL.bar(x + 0.2, ch4, 0.4, label="CH4 tri-axis Z", color="C1")
    axL.set_yscale("log")
    axL.set_xticks(x)
    axL.set_xticklabels([f"E{e}" for e in evs])
    axL.set_ylabel("|CFC-180| impact-window peak (G)")
    axL.set_xlabel("Event")
    axL.set_title("Per-drop peaks (repeatable)", fontsize=10)
    axL.grid(alpha=0.3, axis="y", which="both")
    axL.legend(fontsize=8)

    axR.plot(x, ratio, "o-", color="C3")
    axR.set_xticks(x)
    axR.set_xticklabels([f"E{e}" for e in evs])
    axR.set_ylabel("CH1 / CH4 scale factor")
    axR.set_xlabel("Event")
    axR.set_ylim(0, max(ratio) * 1.25)
    axR.set_title("Single-axis / tri-axis ratio per drop", fontsize=10)
    axR.grid(alpha=0.3)
    fig.suptitle("Cross-calibration repeatability across the seven 1000 G drops",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "peak_repeatability.png", dpi=110)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.csv"), key=event_number)
    assert files, f"no CSVs in {RAW_DIR}"

    rows: list[dict] = []
    half_win = IMPACT_WINDOW_MS * 1e-3
    events: dict[str, tuple] = {}
    fs = None
    for path in files:
        t, data = load_time_domain(path)
        fs = 1.0 / np.median(np.diff(t))
        series = path.name.split("_")[0]  # "500G" / "1000G"
        ev = event_number(path)
        events[path.name] = (t, data, fs)

        filt180 = {ch: cfc_filter(data[:, ci], fs, 180.0)
                   for ci, ch in enumerate(CHANNELS)}
        filt1000 = {ch: cfc_filter(data[:, ci], fs, 1000.0)
                    for ci, ch in enumerate(CHANNELS)}
        impact_idx = impact_index(data, t)

        row: dict = {"event": ev, "series": series,
                     "impact_t_ms": float(t[impact_idx] * 1e3)}
        for ci, ch in enumerate(CHANNELS):
            row[f"{ch}_raw"] = signed_peak(data[:, ci])
            row[f"{ch}_cfc180"] = signed_peak(filt180[ch])
            row[f"{ch}_cfc1000"] = signed_peak(filt1000[ch])
            p180, _ = windowed_signed_peak(filt180[ch], t, impact_idx, half_win)
            p1000, _ = windowed_signed_peak(filt1000[ch], t, impact_idx, half_win)
            row[f"{ch}_cfc180_win"] = p180
            row[f"{ch}_cfc1000_win"] = p1000
        tri = np.sqrt(filt180["CH2"] ** 2 + filt180["CH3"] ** 2
                      + filt180["CH4"] ** 2)
        tri_win, _ = windowed_signed_peak(tri, t, impact_idx, half_win)
        row["tri_resultant_cfc180_win"] = float(abs(tri_win))
        c1 = abs(row["CH1_cfc180_win"])
        c4 = abs(row["CH4_cfc180_win"])
        row["CH1_over_CH4_cfc180_win"] = c1 / c4 if c4 > 1e-6 else float("nan")
        # CH1 clips when raw reaches its +/-full-scale rail (within 1%).
        row["CH1_clipped"] = abs(row["CH1_raw"]) > 0.99 * CH1_FULL_SCALE_G
        rows.append(row)

    assert fs is not None

    # Zero-intercept cross-calibration over the clean 1000 G drops only:
    #   CH1_peak = slope * CH4_peak  ->  slope = sum(xy)/sum(x^2)
    cal = [r for r in rows if r["series"] == CALIBRATION_TRIGGER]
    x = np.array([abs(r["CH4_cfc180_win"]) for r in cal])
    y = np.array([abs(r["CH1_cfc180_win"]) for r in cal])
    slope = float(np.dot(x, y) / np.dot(x, x))
    resid = y - slope * x
    n = len(cal)
    s2 = float(np.dot(resid, resid) / (n - 1)) if n > 1 else float("nan")
    se = float(np.sqrt(s2 / np.dot(x, x))) if n > 1 else float("nan")
    ratios = np.array([r["CH1_over_CH4_cfc180_win"] for r in cal])

    # Figures (use a representative clean drop for the single-event panels).
    rep = next(name for name in events if name.startswith(CALIBRATION_TRIGGER))
    t_r, d_r, fs_r = events[rep]
    plot_overlay(rep.replace(".csv", ""), t_r, d_r, fs_r)
    plot_clipping(rep.replace(".csv", ""), t_r, d_r)
    plot_regression(rows, slope, se)
    plot_repeatability(rows)

    # Summary CSV.
    cols = (
        ["event", "series", "impact_t_ms"]
        + [f"{ch}_raw" for ch in CHANNELS]
        + [f"{ch}_cfc1000_win" for ch in CHANNELS]
        + [f"{ch}_cfc180_win" for ch in CHANNELS]
        + ["tri_resultant_cfc180_win", "CH1_over_CH4_cfc180_win", "CH1_clipped"]
    )
    out_csv = OUT_DATA / "calibration_summary.csv"
    with out_csv.open("w") as f:
        f.write(",".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: r["event"]):
            f.write(",".join(_fmt(r[c]) for c in cols) + "\n")

    # Console summary.
    print(f"Sampling rate: {fs/1e3:.1f} kHz, window {len(t_r)} samples")
    print("\nevent  series  t_imp/ms  CH1_raw  CH1_180win  CH4_180win  CH1/CH4  clip")
    for r in sorted(rows, key=lambda r: r["event"]):
        print(f"{r['event']:>4}  {r['series']:>6}  {r['impact_t_ms']:8.2f}  "
              f"{r['CH1_raw']:8.0f}  {r['CH1_cfc180_win']:10.0f}  "
              f"{r['CH4_cfc180_win']:10.1f}  {r['CH1_over_CH4_cfc180_win']:7.1f}  "
              f"{'YES' if r['CH1_clipped'] else ''}")
    print(f"\nCo-located cross-calibration (CFC-180 impact-window peaks, "
          f"{n} clean 1000 G drops):")
    print(f"  zero-intercept slope  CH1 = {slope:.2f} (+/-{se:.2f}) x CH4")
    print(f"  per-drop ratio        mean {ratios.mean():.2f} +/- "
          f"{ratios.std(ddof=1):.2f} (SD)")
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
