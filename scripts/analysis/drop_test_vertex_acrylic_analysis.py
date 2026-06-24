#!/usr/bin/env python3
"""Analyze the vertex- vs. acrylic-plate T3-prism drop tests (PR #67).

Input: TP4 Time Domain Export `.csv` files committed under
`data/drop-tests/vertex-acrylic/raw/`. Each specimen was dropped twice from
13 ft — `Signal1` with the accelerometer hot-glued to a vertex, `Signal2`
with the accelerometer above the acrylic plate. CH1 was removed for this
series; the recorded channels are:

  * CH2, CH3, CH4 — three-axis accelerometer (CH4 is the triggered axis,
    trigger level 1000 G; full scales 14492.8 / 14992.5 / 13624.0 G).
  * CH5           — single-axis accelerometer (full scale 9442.9 G); this is
    the sensor the project will use going forward (issues #71 / #74).

Sampling is 125 kHz (8 us), 200 ms window, 2 % (4 ms) pre-trigger, so the
impact lands at t ~= 3.9-4.1 ms.

What it does:
  * Loads each run and locates the impact from the triggered CH4 channel
    inside the first 10 ms (a *windowed* peak search rather than a global
    0.2 s max — the global max is often a later mount/ringdown oscillation).
  * Baseline-corrects on the pre-impact samples, then reports peak |g| for
    the single-axis CH5 (primary) and the triggered CH4 both raw and after
    SAE J211 CFC-1000 (1650 Hz) / CFC-180 (300 Hz) low-pass filtering. Raw
    peaks on a lightly damped lattice are dominated by accelerometer
    ringing, so the CFC-180 number is the physically meaningful one.
  * Flags runs that never registered a clean impact (CH5 CFC-180 peak below
    a small threshold) — these are the "no measurement above trigger" cases
    @ctrhjk described, plus the known-invalid T3_0000 acrylic run where the
    accelerometer fell off.
  * Emits comparison figures into `data/drop-tests/vertex-acrylic/figures/`
    and prints the metrics table backing
    `docs/drop-test-vertex-acrylic-analysis.md`.

Note on standards: SAE J211 specifies phaseless (forward-backward)
Butterworth low-pass channel-frequency classes for impact instrumentation;
CFC 1000 => -3 dB ~= 1650 Hz, CFC 180 => ~= 300 Hz.
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
RAW = REPO / "data" / "drop-tests" / "vertex-acrylic" / "raw"
FIG = REPO / "data" / "drop-tests" / "vertex-acrylic" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

# CH4 is the triggered three-axis channel; CH5 the single-axis sensor.
CH4 = 2  # column index within channels[:, 0:4] (CH2, CH3, CH4, CH5)
CH5 = 3

IMPACT_SEARCH_S = 0.010  # look for the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
NO_IMPACT_CFC180_G = 30.0  # CH5 CFC-180 peak below this => no clean impact

# specimen id -> printed label (distinct T3-prism geometries)
SPECIMENS = ["n0jdwk", "m6cyoq", "T3_0103", "T3_0000"]
MOUNTS = [("Signal1", "vertex"), ("Signal2", "acrylic")]
# runs known to be invalid regardless of the numbers
KNOWN_INVALID = {
    ("T3_0000", "acrylic"): "accelerometer not secured, fell off on the drop",
}


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 4]) = (time, [CH2, CH3, CH4, CH5])."""
    d = np.genfromtxt(path, skip_header=9, delimiter=",", usecols=(0, 1, 2, 3, 4))
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
    search = t < IMPACT_SEARCH_S
    rel = np.abs(ch4 - base)
    rel[~search] = -np.inf
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
    fs = None
    rows = []
    traces = {}
    for spec in SPECIMENS:
        for sig, mount in MOUNTS:
            path = RAW / f"{spec}_{sig}.csv"
            if not path.exists():
                print(f"missing {path}", file=sys.stderr)
                continue
            t, ch = load(path)
            dt = float(np.median(np.diff(t)))
            fs = 1.0 / dt
            nb = max(1, int(BASELINE_S / dt))

            i_imp = impact_index(t, ch[:, CH4], dt)
            ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])
            ch4 = ch[:, CH4] - np.median(ch[:nb, CH4])

            ch5_raw_peak = windowed_peak(t, ch5, i_imp, dt)["peak_abs_g"]
            ch5_1000 = cfc_filter(ch5, fs, 1000)
            ch5_180 = cfc_filter(ch5, fs, 180)
            m5 = windowed_peak(t, ch5_180, i_imp, dt)
            m5_1000 = windowed_peak(t, ch5_1000, i_imp, dt)
            ch4_180 = cfc_filter(ch4, fs, 180)
            m4 = windowed_peak(t, ch4_180, i_imp, dt)

            invalid = KNOWN_INVALID.get((spec, mount))
            no_impact = m5["peak_abs_g"] < NO_IMPACT_CFC180_G
            if invalid:
                flag = f"INVALID ({invalid})"
            elif no_impact:
                flag = "no clean CH5 impact (below trigger / plate seated on specimen)"
            else:
                flag = ""

            rows.append(
                {
                    "spec": spec,
                    "mount": mount,
                    "t_imp_ms": t[i_imp] * 1e3,
                    "ch5_raw_g": ch5_raw_peak,
                    "ch5_1000_g": m5_1000["peak_abs_g"],
                    "ch5_180_g": m5["peak_abs_g"],
                    "ch4_180_g": m4["peak_abs_g"],
                    "width_ms": m5["pulse_width_ms"],
                    "dv_ms": m5["delta_v_ms"],
                    "flag": flag,
                }
            )
            traces[(spec, mount)] = (t, ch5, ch5_1000, ch5_180, ch4, i_imp, flag)

    # ---- metrics table ----------------------------------------------
    hdr = (
        f"{'specimen':9s} {'mount':8s} {'t_imp':>6s} {'CH5 raw':>8s} "
        f"{'CH5 1k':>7s} {'CH5 180':>8s} {'CH4 180':>8s} {'wid[ms]':>8s} "
        f"{'Δv':>6s}  flag"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['spec']:9s} {r['mount']:8s} {r['t_imp_ms']:6.2f} "
            f"{r['ch5_raw_g']:8.0f} {r['ch5_1000_g']:7.0f} {r['ch5_180_g']:8.0f} "
            f"{r['ch4_180_g']:8.0f} {r['width_ms']:8.2f} {r['dv_ms']:6.2f}  {r['flag']}"
        )

    # ---- Fig 1: CH5 impact zoom, vertex column vs acrylic column -----
    fig, axes = plt.subplots(len(SPECIMENS), 2, figsize=(12, 12), sharex=True)
    for i, spec in enumerate(SPECIMENS):
        for j, (_, mount) in enumerate(MOUNTS):
            ax = axes[i, j]
            key = (spec, mount)
            if key not in traces:
                ax.set_axis_off()
                continue
            t, c5, c1000, c180, _, i_imp, flag = traces[key]
            t0 = t[i_imp] * 1e3
            w = (t * 1e3 > t0 - 6) & (t * 1e3 < t0 + 12)
            ax.plot(t[w] * 1e3, c5[w], lw=0.4, color="0.7", label="raw")
            ax.plot(t[w] * 1e3, c1000[w], lw=0.9, color="tab:blue", label="CFC 1000")
            ax.plot(t[w] * 1e3, c180[w], lw=1.6, color="tab:red", label="CFC 180")
            title = f"{spec} — {mount}"
            if flag:
                title += "  ⚠"
            ax.set_title(title, fontsize=9)
            ax.grid(alpha=0.3)
            if i == 0 and j == 0:
                ax.legend(fontsize=7, loc="upper right")
            if j == 0:
                ax.set_ylabel("CH5 a (G)")
    for ax in axes[-1]:
        ax.set_xlabel("time (ms)")
    fig.suptitle(
        "Single-axis CH5 impact window — vertex (left) vs acrylic (right)", y=0.995
    )
    fig.tight_layout()
    fig.savefig(FIG / "01_ch5_vertex_vs_acrylic.png", dpi=130)
    plt.close(fig)

    # ---- Fig 2: CFC-180 peak-g grouped bar chart ---------------------
    valid = [r for r in rows if not r["flag"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(SPECIMENS))
    for off, mount, color in [(-0.2, "vertex", "tab:green"), (0.2, "acrylic", "tab:orange")]:
        vals, hatches = [], []
        for spec in SPECIMENS:
            r = next((r for r in rows if r["spec"] == spec and r["mount"] == mount), None)
            vals.append(r["ch5_180_g"] if r else 0.0)
            hatches.append("//" if (r and r["flag"]) else "")
        bars = ax.bar(x + off, vals, 0.4, label=mount, color=color)
        for b, h in zip(bars, hatches):
            if h:
                b.set_hatch(h)
                b.set_alpha(0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(SPECIMENS)
    ax.set(
        ylabel="CH5 CFC-180 peak |g| (G)",
        title="Vertex vs acrylic — single-axis CFC-180 peak (hatched = invalid / no clean impact)",
    )
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "02_cfc180_peak_bars.png", dpi=130)
    plt.close(fig)

    # ---- Fig 3: PSD of the valid vertex CH5 traces -------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    for (spec, mount), (t, c5, *_rest) in traces.items():
        if mount != "vertex":
            continue
        f, pxx = signal.welch(c5, fs, nperseg=4096)
        ax.semilogy(f, pxx, lw=0.9, label=f"{spec} (vertex)")
    ax.axvline(1650, color="tab:blue", ls="--", lw=1, label="CFC 1000 (1650 Hz)")
    ax.axvline(300, color="tab:red", ls="--", lw=1, label="CFC 180 (300 Hz)")
    ax.set(
        xlabel="frequency (Hz)",
        ylabel="PSD (G²/Hz)",
        xlim=(0, 25000),
        title="CH5 power spectral density — vertex runs (raw peaks are ringing-dominated)",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_ch5_psd_vertex.png", dpi=130)
    plt.close(fig)

    print(f"\nwrote figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
