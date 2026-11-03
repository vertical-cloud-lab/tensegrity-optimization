#!/usr/bin/env python3
"""Analyze the first instrumented drop-tower runs (issue #36).

Input: TP4 Time Domain Export `.txt` files (4-channel accelerometer, G's,
125 kHz / 8 us sampling, 0.2 s window) committed under
`data/drop-tests/raw/`.

What it does:
  * Loads each run, identifies CH1 as the primary impact accelerometer
    (CH2/CH3 are low-level cross-axis/noise; CH4 carries a fixed ~1.4 kG
    spike at t≈4.2 ms in every run — a common trigger/magnet-release
    artifact, not the specimen impact).
  * Baseline-corrects, then computes peak |g| both raw and after SAE J211
    CFC-1000 (1650 Hz) and CFC-180 (300 Hz) low-pass filtering — raw peaks
    on a lightly damped lattice are dominated by accelerometer ringing, so
    the filtered numbers are the physically meaningful ones.
  * Estimates the impact pulse: peak time, ~half-amplitude pulse width, and
    the velocity change Δv obtained by integrating the CFC-180 acceleration
    across the pulse.
  * Emits comparison figures into `data/drop-tests/figures/` and prints a
    metrics table that backs `docs/drop-test-analysis.md`.

Note on standards: SAE J211 specifies phaseless (forward-backward)
Butterworth low-pass channel-frequency classes for impact instrumentation;
CFC 1000 ⇒ -3 dB ≈ 1650 Hz, CFC 180 ⇒ ≈ 300 Hz.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "raw"
FIG = REPO / "data" / "drop-tests" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

# label, filename -> human description
RUNS = [
    ("Signal 14 — control", "Signal_14_control.txt", "no specimen, both acrylic plates"),
    ("Signal 10 — PETG", "Signal_10_PETG.txt", "PETG specimen"),
    ("Signal 11 — audrey", "Signal_11_audrey.txt", "'audrey' specimen, run 1"),
    ("Signal 12 — audrey", "Signal_12_audrey.txt", "'audrey' specimen, run 2"),
    ("Signal 13 — audrey", "Signal_13_audrey.txt", "'audrey' specimen, run 3"),
]


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N,4]) from a TP4 export file."""
    d = np.genfromtxt(path, skip_header=4)
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    # CFC class -> nominal -3 dB cutoff (Hz): 1000->1650, 600->1000,
    # 180->300, 60->100.
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def pulse_metrics(t: np.ndarray, a_g: np.ndarray) -> dict:
    """Peak, pulse width at half max, and Δv across the main pulse.

    `a_g` should already be CFC-filtered acceleration in G.
    """
    idx = int(np.argmax(np.abs(a_g)))
    peak = a_g[idx]
    peak_abs = abs(peak)
    t_peak = t[idx]

    half = peak_abs / 2.0
    sign = np.sign(peak)
    over = (sign * a_g) >= half
    # contiguous run containing the peak
    lo = idx
    while lo > 0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < len(over) - 1 and over[hi + 1]:
        hi += 1
    width = t[hi] - t[lo]

    # velocity change across the pulse (integrate over a small window
    # around the half-max support)
    a_ms2 = a_g * GRAVITY
    dv = integrate.trapezoid(a_ms2[lo : hi + 1], t[lo : hi + 1])
    return {
        "peak_g": peak,
        "peak_abs_g": peak_abs,
        "t_peak_ms": t_peak * 1e3,
        "pulse_width_ms": width * 1e3,
        "delta_v_ms": dv,
    }


def main() -> int:
    fs = None
    summaries = []
    traces = {}
    for label, fname, desc in RUNS:
        path = RAW / fname
        if not path.exists():
            print(f"missing {path}", file=sys.stderr)
            continue
        t, ch = load(path)
        dt = float(np.median(np.diff(t)))
        fs = 1.0 / dt
        ch1 = ch[:, 0]
        ch1 = ch1 - np.median(ch1[: int(0.002 / dt)])  # baseline on first 2 ms

        raw_peak = np.abs(ch1).max()
        cfc1000 = cfc_filter(ch1, fs, 1000)
        cfc180 = cfc_filter(ch1, fs, 180)
        m = pulse_metrics(t, cfc180)
        m1000 = pulse_metrics(t, cfc1000)

        summaries.append(
            {
                "label": label,
                "desc": desc,
                "raw_peak_g": raw_peak,
                "cfc1000_peak_g": m1000["peak_abs_g"],
                "cfc180_peak_g": m["peak_abs_g"],
                "t_peak_ms": m["t_peak_ms"],
                "pulse_width_ms": m["pulse_width_ms"],
                "delta_v_ms": abs(m["delta_v_ms"]),
            }
        )
        traces[label] = (t, ch1, cfc1000, cfc180, ch[:, 3])

    # ---- table -------------------------------------------------------
    hdr = (
        f"{'run':24s} {'raw|g|':>9s} {'CFC1000':>9s} {'CFC180':>9s} "
        f"{'t_pk[ms]':>9s} {'width[ms]':>10s} {'Δv[m/s]':>9s}"
    )
    print(hdr)
    print("-" * len(hdr))
    for s in summaries:
        print(
            f"{s['label']:24s} {s['raw_peak_g']:9.0f} {s['cfc1000_peak_g']:9.0f} "
            f"{s['cfc180_peak_g']:9.0f} {s['t_peak_ms']:9.2f} "
            f"{s['pulse_width_ms']:10.2f} {s['delta_v_ms']:9.2f}"
        )

    # ---- Fig 1: full-window CH1 overlay ------------------------------
    fig, ax = plt.subplots(figsize=(11, 5))
    for label, (t, ch1, _, _, _) in traces.items():
        ax.plot(t * 1e3, ch1, lw=0.6, label=label)
    ax.set(xlabel="time (ms)", ylabel="CH1 acceleration (G)",
           title="Drop-tower CH1 — full 200 ms window (baseline-corrected)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_ch1_full_window.png", dpi=130)
    plt.close(fig)

    # ---- Fig 2: per-run impact zoom, raw vs CFC1000 vs CFC180 --------
    fig, axes = plt.subplots(len(RUNS), 1, figsize=(11, 13), sharex=False)
    for ax, (label, (t, ch1, c1000, c180, _)) in zip(axes, traces.items()):
        idx = int(np.argmax(np.abs(c180)))
        t0 = t[idx]
        w = (t * 1e3 > (t0 * 1e3 - 8)) & (t * 1e3 < (t0 * 1e3 + 12))
        ax.plot(t[w] * 1e3, ch1[w], lw=0.5, color="0.7", label="raw")
        ax.plot(t[w] * 1e3, c1000[w], lw=1.0, color="tab:blue", label="CFC 1000")
        ax.plot(t[w] * 1e3, c180[w], lw=1.6, color="tab:red", label="CFC 180")
        ax.set(ylabel="a (G)", title=label)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="upper right")
    axes[-1].set_xlabel("time (ms)")
    fig.suptitle("Impact window: raw vs SAE J211 CFC-filtered CH1", y=1.0)
    fig.tight_layout()
    fig.savefig(FIG / "02_impact_zoom_filtered.png", dpi=130)
    plt.close(fig)

    # ---- Fig 3: peak-g comparison bar chart --------------------------
    labels = [s["label"].split("—")[1].strip() for s in summaries]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - 0.27, [s["raw_peak_g"] for s in summaries], 0.27, label="raw |g|")
    ax.bar(x, [s["cfc1000_peak_g"] for s in summaries], 0.27, label="CFC 1000")
    ax.bar(x + 0.27, [s["cfc180_peak_g"] for s in summaries], 0.27, label="CFC 180")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15)
    ax.set(ylabel="peak |acceleration| (G)",
           title="Peak CH1 acceleration by run (raw vs CFC-filtered)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "03_peak_g_comparison.png", dpi=130)
    plt.close(fig)

    # ---- Fig 4: PSD of CH1 -------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    for label, (t, ch1, _, _, _) in traces.items():
        f, pxx = signal.welch(ch1, fs, nperseg=4096)
        ax.semilogy(f, pxx, lw=0.8, label=label)
    ax.axvline(1650, color="tab:blue", ls="--", lw=1, label="CFC 1000 (1650 Hz)")
    ax.axvline(300, color="tab:red", ls="--", lw=1, label="CFC 180 (300 Hz)")
    ax.set(xlabel="frequency (Hz)", ylabel="PSD (G²/Hz)", xlim=(0, 25000),
           title="CH1 power spectral density")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "04_ch1_psd.png", dpi=130)
    plt.close(fig)

    # ---- Fig 5: CH4 trigger artifact ---------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for label, (t, _, _, _, ch4) in traces.items():
        w = t * 1e3 < 10
        ax.plot(t[w] * 1e3, ch4[w], lw=0.8, label=label)
    ax.set(xlabel="time (ms)", ylabel="CH4 acceleration (G)",
           title="CH4 first 10 ms — fixed ~1.4 kG spike at t≈4.2 ms in every run "
                 "(trigger/release artifact, not impact)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "05_ch4_trigger_artifact.png", dpi=130)
    plt.close(fig)

    print(f"\nwrote figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
