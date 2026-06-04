#!/usr/bin/env python3
"""Analysis of the drop-tower accelerometer "tuning" data (issue #71).

Me (@me-madsen) and @ctrhjk ran a series of drop-tower tests on 06/02/2026 to
standardize the test setup and to understand why the **single-axis** and
**tri-axis** accelerometers do not report the same acceleration. The raw data
are TP4 (Test Partner 4) exports:

* ``06.02.2026.csv``        -- series *table* export: one row per event with the
  per-channel peak ``Accel``, pulse ``Duration`` and ``Delta V``.
* ``06.02.2026_SignalN.csv`` -- *time-domain* export for event ``N`` (N = 1..13),
  4 channels sampled at 125 kHz for 0.2 s (25 000 samples).

Channel mapping (inferred from the data; see report -- pending confirmation of
the per-test position labels):

* ``CH1``           -> single-axis accelerometer (impact direction only)
* ``CH2, CH3, CH4`` -> tri-axis accelerometer (X, Y, Z); CH4 is its impact axis

The script:

1. Parses the table and time-domain exports.
2. Plots every event (all four channels, raw + SAE J211 CFC-filtered).
3. Applies SAE J211 (CFC 180 and CFC 1000) phaseless filtering to separate the
   rigid-body shock from sensor/mount ringing.
4. Computes the frequency content (PSD) to expose the ringing/resonance.
5. Builds a peak-comparison / sensitivity-ratio table (single vs tri-axis) and
   flags channel saturation (clipping).

Outputs are written to ``docs/figures/accelerometer-tuning/`` and
``data/drop-tests/accelerometer-tuning/``.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "drop-tests" / "accelerometer-tuning" / "raw"
OUT_DATA = ROOT / "data" / "drop-tests" / "accelerometer-tuning"
FIG_DIR = ROOT / "docs" / "figures" / "accelerometer-tuning"

CHANNELS = ["CH1", "CH2", "CH3", "CH4"]
CH_LABELS = {
    "CH1": "CH1 (single-axis)",
    "CH2": "CH2 (tri-axis X)",
    "CH3": "CH3 (tri-axis Y)",
    "CH4": "CH4 (tri-axis Z)",
}
N_EVENTS = 13


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def load_time_domain(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, data[N,4]) from a TP4 time-domain export."""
    lines = path.read_text().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Time (sec)")) + 1
    arr = np.genfromtxt(lines[start:], delimiter=",", usecols=(0, 1, 2, 3, 4))
    arr = arr[~np.isnan(arr[:, 0])]
    return arr[:, 0], arr[:, 1:5]


# --------------------------------------------------------------------------- #
# SAE J211 / ISO 6487 CFC filter (phaseless 4-pole Butterworth)
# --------------------------------------------------------------------------- #
def cfc_filter(x: np.ndarray, fs: float, cfc: float) -> np.ndarray:
    """Apply the SAE J211 Channel Frequency Class filter.

    Implements the 2-pole Butterworth low-pass from SAE J211-1 Appendix C run
    forward then backward to give a phaseless 4-pole response. ``cfc`` is the
    Channel Frequency Class (e.g. 180, 1000); the -3 dB point is ~1.66 * cfc.
    """
    T = 1.0 / fs
    wd = 2.0 * math.pi * cfc * 2.0775
    wa = math.tan(wd * T / 2.0)
    den = 1.0 + math.sqrt(2.0) * wa + wa * wa
    a0 = wa * wa / den
    a1 = 2.0 * a0
    a2 = a0
    b1 = -2.0 * (wa * wa - 1.0) / den
    b2 = (-1.0 + math.sqrt(2.0) * wa - wa * wa) / den

    def _pass(sig: np.ndarray) -> np.ndarray:
        y = np.empty_like(sig)
        y[0] = sig[0]
        y[1] = sig[1]
        for i in range(2, len(sig)):
            y[i] = (
                a0 * sig[i] + a1 * sig[i - 1] + a2 * sig[i - 2]
                + b1 * y[i - 1] + b2 * y[i - 2]
            )
        return y

    fwd = _pass(x)
    bwd = _pass(fwd[::-1])[::-1]
    return bwd


def signed_peak(x: np.ndarray) -> float:
    """Largest absolute value, keeping its sign."""
    return float(x[int(np.argmax(np.abs(x)))])


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #
def plot_event(ev: int, t: np.ndarray, data: np.ndarray, fs: float) -> None:
    """Time-domain overview for one event: raw + CFC-180 for each channel."""
    tms = t * 1e3
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    for ax, ci in zip(axes.ravel(), range(4)):
        raw = data[:, ci]
        filt = cfc_filter(raw, fs, 180.0)
        ax.plot(tms, raw, lw=0.5, color="0.6", label="raw")
        ax.plot(tms, filt, lw=1.2, color="C3", label="CFC 180")
        ax.set_title(
            f"{CH_LABELS[CHANNELS[ci]]}  |  raw pk={signed_peak(raw):.0f} G, "
            f"CFC180 pk={signed_peak(filt):.0f} G"
        )
        ax.grid(alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("Time (ms)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Acceleration (G)")
    fig.suptitle(f"Event {ev} -- 06/02/2026 drop-tower test", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"event_{ev:02d}_timeseries.png", dpi=110)
    plt.close(fig)


def plot_psd(events: dict[int, tuple[np.ndarray, np.ndarray]], fs: float) -> None:
    """Welch PSD of CH1 and CH4 for the impact events, to expose ringing."""
    from scipy.signal import welch

    impact = [e for e in (1, 2, 3, 4, 5) if e in events]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ci, ax, name in zip((0, 3), axes, ("CH1 (single-axis)", "CH4 (tri-axis Z)")):
        for e in impact:
            _, data = events[e]
            f, p = welch(data[:, ci], fs=fs, nperseg=4096)
            ax.semilogy(f / 1e3, p, lw=1.0, label=f"event {e}")
        ax.set_title(name)
        ax.set_xlabel("Frequency (kHz)")
        ax.set_xlim(0, 30)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8)
    axes[0].set_ylabel("PSD (G$^2$/Hz)")
    fig.suptitle("Frequency content of impact events (CH1 vs CH4)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "psd_impact_events.png", dpi=110)
    plt.close(fig)


def plot_saturation(events: dict[int, tuple[np.ndarray, np.ndarray]], fs: float) -> None:
    """Zoom on CH1 of the high-amplitude events to show the ~8.8 kG ceiling."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for e in (2, 3, 5):
        if e not in events:
            continue
        t, data = events[e]
        ch1 = data[:, 0]
        k = int(np.argmax(np.abs(ch1)))
        sl = slice(max(0, k - 60), k + 60)
        ax.plot((t[sl] - t[k]) * 1e3, ch1[sl], marker=".", ms=3, lw=0.9,
                label=f"event {e} (peak {ch1[k]:.0f} G)")
    ax.axhline(8806, color="k", ls="--", lw=1, label="~8806 G recurring ceiling")
    ax.set_xlabel("Time relative to peak (ms)")
    ax.set_ylabel("CH1 acceleration (G)")
    ax.set_title("CH1 single-axis: recurring ~8.8 kG ceiling = full-scale saturation",
                 fontweight="bold")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch1_saturation.png", dpi=110)
    plt.close(fig)


def plot_peak_comparison(rows: list[dict]) -> None:
    """Bar chart of CH1 vs CH4 CFC-1000 peaks across events."""
    evs = [r["event"] for r in rows]
    ch1 = [abs(r["CH1_cfc1000"]) for r in rows]
    ch4 = [abs(r["CH4_cfc1000"]) for r in rows]
    x = np.arange(len(evs))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - 0.2, ch1, 0.4, label="CH1 single-axis", color="C0")
    ax.bar(x + 0.2, ch4, 0.4, label="CH4 tri-axis Z", color="C1")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"E{e}" for e in evs])
    ax.set_ylabel("|peak| acceleration, CFC 1000 (G)")
    ax.set_xlabel("Event")
    ax.set_title("Single-axis (CH1) vs tri-axis impact axis (CH4): CFC-1000 peaks",
                 fontweight="bold")
    ax.grid(alpha=0.3, axis="y", which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "peak_comparison_ch1_ch4.png", dpi=110)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)

    events: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    fs = None
    for ev in range(1, N_EVENTS + 1):
        path = RAW_DIR / f"06.02.2026_Signal{ev}.csv"
        if not path.exists():
            continue
        t, data = load_time_domain(path)
        fs = 1.0 / np.median(np.diff(t))
        events[ev] = (t, data)
        plot_event(ev, t, data, fs)

    assert fs is not None, "no time-domain files found"

    rows: list[dict] = []
    for ev, (t, data) in events.items():
        row: dict = {"event": ev}
        for ci, ch in enumerate(CHANNELS):
            raw = data[:, ci]
            row[f"{ch}_raw"] = signed_peak(raw)
            row[f"{ch}_cfc180"] = signed_peak(cfc_filter(raw, fs, 180.0))
            row[f"{ch}_cfc1000"] = signed_peak(cfc_filter(raw, fs, 1000.0))
        # tri-axis resultant (CH2/3/4) on the CFC-180 traces
        tri = np.sqrt(
            cfc_filter(data[:, 1], fs, 180.0) ** 2
            + cfc_filter(data[:, 2], fs, 180.0) ** 2
            + cfc_filter(data[:, 3], fs, 180.0) ** 2
        )
        row["tri_resultant_cfc180"] = float(tri.max())
        # single (CH1) vs tri impact axis (CH4) ratio, CFC 180
        c1 = abs(row["CH1_cfc180"])
        c4 = abs(row["CH4_cfc180"])
        row["CH1_over_CH4_cfc180"] = c1 / c4 if c4 > 1e-6 else float("nan")
        # saturation flag: CH1 within 2% of the recurring ~8806 G ceiling
        row["CH1_saturated"] = abs(row["CH1_raw"]) > 0.98 * 8806.0
        rows.append(row)

    plot_psd(events, fs)
    plot_saturation(events, fs)
    plot_peak_comparison(rows)

    # write a tidy summary CSV
    cols = (
        ["event"]
        + [f"{ch}_raw" for ch in CHANNELS]
        + [f"{ch}_cfc1000" for ch in CHANNELS]
        + [f"{ch}_cfc180" for ch in CHANNELS]
        + ["tri_resultant_cfc180", "CH1_over_CH4_cfc180", "CH1_saturated"]
    )
    out_csv = OUT_DATA / "peak_summary.csv"
    with out_csv.open("w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(_fmt(r[c]) for c in cols) + "\n")

    # console summary
    print(f"Sampling rate: {fs/1e3:.1f} kHz, window {len(events[1][0])} samples")
    print("\nevent  CH1_raw  CH1_cfc180  CH4_cfc180  CH1/CH4  saturated")
    for r in rows:
        print(
            f"{r['event']:>4}  {r['CH1_raw']:8.0f}  {r['CH1_cfc180']:9.0f}  "
            f"{r['CH4_cfc180']:9.0f}  {r['CH1_over_CH4_cfc180']:7.2f}  "
            f"{'YES' if r['CH1_saturated'] else ''}"
        )
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
