#!/usr/bin/env python3
"""Analyze @ctrhjk's clip-height / trigger-diagnostic drop tests.

Context: two PR-comment experiments aimed at the recurring "the accelerometer
on the acrylic plate never registers an impact above its 1000 G trigger"
problem (see ``data/drop-tests/vertex-acrylic/`` for the original series).

  1. Clip-height sweep (PR comment 4794351098). @ctrhjk added bungee cords so
     two vertices were each pinned by two cords and the third by the remaining
     two, then placed the tri-axis accelerometer on the acrylic plate with a
     vertex directly below and swept the retaining-clip height (0.5, 1.0, 1.5,
     2.0 in above the plate), two drops per height, on a "Practice" specimen.
     **None of the eight drops triggered** (no acceleration above 1000 G was
     recorded), so there is no waveform CSV — only video. The added cords cured
     the specimen fly-off, but the load still never reached the plate sensor.

  2. Accelerometer check (PR comment 4794438322). To test whether the sensor /
     DAQ itself was at fault, @ctrhjk moved the tri-axis accelerometer onto the
     **bottom (base) plate** (no acrylic plate in the load path), same channel
     setup, and dropped from 13 in. This produced one CSV
     (``Accelerometer_check_Signal1.csv``), which this script analyzes.

Channel map (same as the vertex-acrylic series, single-axis CH5 absent here):
  * CH2, CH3, CH4 — three-axis accelerometer; CH4 is the triggered axis
    (trigger level 1000 G; full scales 14492.8 / 14992.5 / 13624.0 G).
  * CH5           — single-axis channel column present in the export but unused
    in this test (sits at sensor noise, ~tens of G).

Sampling is 125 kHz (8 us), 200 ms window, 2 % (4 ms) pre-trigger, so a real
impact lands at t ~= 3.9-4.1 ms.

What it does:
  * Loads the base-plate run, locates the impact from the triggered CH4 channel
    inside the first 10 ms (windowed search, not a global 0.2 s max).
  * Baseline-corrects on the pre-impact samples and reports peak |g| on the
    tri-axis channels both raw and after SAE J211 CFC-1000 (1650 Hz) / CFC-180
    (300 Hz) phaseless low-pass filtering. Raw peaks are accelerometer-ringing
    dominated, so CFC-180 is the physically meaningful structural number.
  * Confirms the base-plate impact clears the 1000 G trigger by a wide margin,
    which isolates the clip-height "no trigger" failure to the load path
    (acrylic plate seating on / damped by the specimen), not the sensor / DAQ.
  * Emits figures into ``data/drop-tests/clip-height/figures/``.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "clip-height" / "raw"
FIG = REPO / "data" / "drop-tests" / "clip-height" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

# Column indices within channels[:, 0:4] == (CH2, CH3, CH4, CH5).
CH2, CH3, CH4, CH5 = 0, 1, 2, 3
TRI_AXIS = [CH2, CH3, CH4]
TRIGGER_LEVEL_G = 1000.0  # CH4 trigger level set on the TP4

IMPACT_SEARCH_S = 0.010  # locate the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

BASE_PLATE_RUN = RAW / "Accelerometer_check_Signal1.csv"
CH_NAMES = {CH2: "CH2", CH3: "CH3", CH4: "CH4 (trig)", CH5: "CH5"}


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 4]) = (time, [CH2, CH3, CH4, CH5])."""
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",", usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def impact_index(t: np.ndarray, ch4: np.ndarray, dt: float) -> int:
    """Index of the trigger-channel (CH4) impact inside the first 10 ms."""
    nb = max(1, int(BASELINE_S / dt))
    base = np.median(ch4[:nb])
    rel = np.abs(ch4 - base)
    rel[t >= IMPACT_SEARCH_S] = -np.inf
    return int(np.argmax(rel))


def windowed_peak(t: np.ndarray, a_g: np.ndarray, i_imp: int, dt: float) -> dict:
    """Peak |g|, peak time, half-amplitude width and Δv near the impact."""
    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo0, hi0 = max(0, i_imp - half), min(len(a_g), i_imp + half)
    seg = a_g[lo0:hi0]
    j = int(np.argmax(np.abs(seg)))
    idx = lo0 + j
    peak = a_g[idx]
    peak_abs = abs(peak)

    thr = peak_abs / 2.0
    sign = np.sign(peak)
    over = (sign * a_g) >= thr
    lo = idx
    while lo > lo0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < hi0 - 1 and over[hi + 1]:
        hi += 1
    width = t[hi] - t[lo]
    a_ms2 = a_g * GRAVITY
    dv = integrate.trapezoid(a_ms2[lo : hi + 1], t[lo : hi + 1])
    return {
        "peak_abs_g": peak_abs,
        "t_peak_ms": t[idx] * 1e3,
        "pulse_width_ms": width * 1e3,
        "delta_v_ms": abs(dv),
    }


def main() -> int:
    if not BASE_PLATE_RUN.exists():
        raise SystemExit(f"missing {BASE_PLATE_RUN}")

    t, ch = load(BASE_PLATE_RUN)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(BASELINE_S / dt))
    i_imp = impact_index(t, ch[:, CH4], dt)
    t_imp_ms = t[i_imp] * 1e3

    print(f"Base-plate accelerometer-check run: {BASE_PLATE_RUN.name}")
    print(f"  fs = {fs/1e3:.0f} kHz, window = {t[-1]*1e3:.0f} ms, impact at t = {t_imp_ms:.2f} ms")
    print(f"  trigger level (CH4) = {TRIGGER_LEVEL_G:.0f} G\n")

    hdr = f"{'chan':10s} {'raw |g|':>9s} {'CFC1000':>9s} {'CFC180':>9s} {'wid[ms]':>8s} {'Δv[m/s]':>8s}"
    print(hdr)
    print("-" * len(hdr))
    metrics = {}
    for c in TRI_AXIS:
        a = ch[:, c] - np.median(ch[:nb, c])
        raw = windowed_peak(t, a, i_imp, dt)["peak_abs_g"]
        a1000 = cfc_filter(a, fs, 1000)
        a180 = cfc_filter(a, fs, 180)
        m1000 = windowed_peak(t, a1000, i_imp, dt)
        m180 = windowed_peak(t, a180, i_imp, dt)
        metrics[c] = (a, a1000, a180, raw, m1000, m180)
        print(
            f"{CH_NAMES[c]:10s} {raw:9.0f} {m1000['peak_abs_g']:9.0f} "
            f"{m180['peak_abs_g']:9.0f} {m180['pulse_width_ms']:8.2f} {m180['delta_v_ms']:8.2f}"
        )

    ch4_raw = metrics[CH4][3]
    print(
        f"\nCH4 raw peak {ch4_raw:.0f} G is {ch4_raw/TRIGGER_LEVEL_G:.1f}x the 1000 G trigger "
        "=> sensor + DAQ register a clean base-plate impact.\n"
    )

    # ---- Fig 1: tri-axis impact window on the base plate -------------
    fig, ax = plt.subplots(figsize=(10, 5))
    w = (t * 1e3 > t_imp_ms - 4) & (t * 1e3 < t_imp_ms + 12)
    for c, color in zip(TRI_AXIS, ["tab:gray", "tab:olive", "tab:red"]):
        a180 = metrics[c][2]
        ax.plot(t[w] * 1e3, a180[w], lw=1.4, color=color, label=f"{CH_NAMES[c]} CFC-180")
    ax.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1, label="1000 G trigger")
    ax.axhline(-TRIGGER_LEVEL_G, color="k", ls=":", lw=1)
    ax.set(
        xlabel="time (ms)",
        ylabel="acceleration (G)",
        title="Base-plate accelerometer check — tri-axis CFC-180 impact window (13 in drop)",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_baseplate_impact_window.png", dpi=130)
    plt.close(fig)

    # ---- Fig 2: raw CH4 vs filtered, full window --------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    a, a1000, a180 = metrics[CH4][0], metrics[CH4][1], metrics[CH4][2]
    ax.plot(t * 1e3, a, lw=0.3, color="0.7", label="CH4 raw")
    ax.plot(t * 1e3, a1000, lw=0.8, color="tab:blue", label="CH4 CFC-1000")
    ax.plot(t * 1e3, a180, lw=1.3, color="tab:red", label="CH4 CFC-180")
    ax.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1, label="1000 G trigger")
    ax.set(
        xlabel="time (ms)",
        ylabel="CH4 acceleration (G)",
        title="Base-plate accelerometer check — triggered CH4, full 200 ms window",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_ch4_full_window.png", dpi=130)
    plt.close(fig)

    # ---- Fig 3: PSD of the base-plate CH4 trace ---------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    f, pxx = signal.welch(metrics[CH4][0], fs, nperseg=4096)
    ax.semilogy(f, pxx, lw=0.9, color="tab:red", label="CH4 (base plate)")
    ax.axvline(1650, color="tab:blue", ls="--", lw=1, label="CFC 1000 (1650 Hz)")
    ax.axvline(300, color="tab:red", ls="--", lw=1, label="CFC 180 (300 Hz)")
    ax.set(
        xlabel="frequency (Hz)",
        ylabel="PSD (G²/Hz)",
        xlim=(0, 25000),
        title="CH4 power spectral density — base-plate check (raw peak is ringing-dominated)",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_ch4_psd.png", dpi=130)
    plt.close(fig)

    print(f"wrote figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
