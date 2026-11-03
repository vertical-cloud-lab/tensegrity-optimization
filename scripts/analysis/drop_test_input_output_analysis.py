#!/usr/bin/env python3
"""Analyze the input-output accelerometer drop tests (PR #67).

Input: TP4 Time Domain Export `.csv` files committed under
`data/drop-tests/input-output/raw/`. This series tests an *input-output*
(transmissibility) instrumentation design proposed by @ctrhjk: a single-axis
accelerometer on the bottom acrylic plate is the **input** sensor (it sees the
plate strike), and a tri-axis accelerometer hot-glued to the top vertex is the
**output** sensor (it sees what the specimen transmits). Crucially the bungees
were removed for this series (pretension off), so the bungee-driven specimen
lift-off that contaminated earlier drops is no longer in play.

Channel map (this series):
  * CH5            — single-axis accelerometer on the **base plate** = INPUT;
    this is the triggered channel (trigger level 1000 G, full scale 9442.9 G).
  * CH2, CH3, CH4  — tri-axis accelerometer on the **top vertex** = OUTPUT
    (full scales 14492.8 / 14992.5 / 13624.0 G); trigger OFF on all three.

Four distinct-geometry specimens (Practice, n0jdwk, yqpmx1, h8Lbev) were each
dropped five times from 13 in. Sampling is 125 kHz (8 us), 200 ms window, 2 %
(4 ms) pre-trigger, so the impact lands at t ~= 3.9 ms.

What it does:
  * Loads each run and locates the impact from the triggered CH5 (input)
    channel inside the first 10 ms (a *windowed* peak search, not a global
    0.2 s max which is usually a later mount/ringdown lobe).
  * Baseline-corrects on the pre-impact samples, then reports, both raw and
    after SAE J211 CFC-1000 (1650 Hz) / CFC-180 (300 Hz) low-pass filtering:
      - input peak |g| on the single-axis CH5,
      - output peak |g| on the tri-axis resultant sqrt(CH2^2+CH3^2+CH4^2),
      - transmissibility T = output / input (the candidate BO observable),
      - input pulse width and Delta-v.
    Raw peaks on a lightly damped lattice are accelerometer-ringing dominated,
    so the CFC-180 number is the physically meaningful one.
  * Aggregates the five drops per specimen as mean +- 1 sigma and CV, which is
    what tells us whether transmissibility is a repeatable, geometry-
    discriminating objective.
  * Emits figures into `data/drop-tests/input-output/figures/` and prints the
    metrics tables backing `docs/drop-test-input-output-analysis.md`.

Note on standards: SAE J211 specifies phaseless (forward-backward) Butterworth
low-pass channel-frequency classes for impact instrumentation; CFC 1000 =>
-3 dB ~= 1650 Hz, CFC 180 => ~= 300 Hz.
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
RAW = REPO / "data" / "drop-tests" / "input-output" / "raw"
FIG = REPO / "data" / "drop-tests" / "input-output" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

# Column layout within channels[:, 0:4] == (CH2, CH3, CH4, CH5).
OUT_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output on the top vertex
CH5 = 3  # single-axis input on the base plate (triggered channel)

IMPACT_SEARCH_S = 0.010  # look for the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

# Distinct-geometry specimens, each dropped five times (Signal1..Signal5).
SPECIMENS = ["practice", "n0jdwk", "yqpmx1", "h8Lbev"]
N_DROPS = 5


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 4]) = (time, [CH2, CH3, CH4, CH5])."""
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",", usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def impact_index(t: np.ndarray, trig: np.ndarray, dt: float) -> int:
    """Index of the trigger-channel (CH5 input) impact inside the first 10 ms."""
    nb = max(1, int(BASELINE_S / dt))
    base = np.median(trig[:nb])
    search = t < IMPACT_SEARCH_S
    rel = np.abs(trig - base)
    rel[~search] = -np.inf
    return int(np.argmax(rel))


def windowed_peak(t: np.ndarray, a_g: np.ndarray, i_imp: int, dt: float) -> dict:
    """Peak |g|, peak time, half-amplitude width and Delta-v near the impact."""
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


def resultant(out: np.ndarray) -> np.ndarray:
    """Magnitude of the tri-axis (CH2, CH3, CH4) vector at each sample."""
    return np.sqrt(np.sum(out**2, axis=1))


def cv(vals: list[float]) -> float:
    """Coefficient of variation (%) = 100 * std / mean."""
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def main() -> int:
    fs = None
    rows = []
    traces = {}
    for spec in SPECIMENS:
        for k in range(1, N_DROPS + 1):
            path = RAW / f"{spec}_Signal{k}.csv"
            if not path.exists():
                print(f"missing {path}", file=sys.stderr)
                continue
            t, ch = load(path)
            dt = float(np.median(np.diff(t)))
            fs = 1.0 / dt
            nb = max(1, int(BASELINE_S / dt))

            ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])  # input (base plate)
            out = ch[:, OUT_COLS] - np.median(ch[:nb, OUT_COLS], axis=0)
            i_imp = impact_index(t, ch5, dt)

            in_raw = windowed_peak(t, ch5, i_imp, dt)["peak_abs_g"]
            ch5_1000 = cfc_filter(ch5, fs, 1000)
            ch5_180 = cfc_filter(ch5, fs, 180)
            m_in_1000 = windowed_peak(t, ch5_1000, i_imp, dt)
            m_in_180 = windowed_peak(t, ch5_180, i_imp, dt)

            res_raw = resultant(out)
            out180 = np.stack([cfc_filter(out[:, j], fs, 180) for j in range(out.shape[1])], axis=1)
            out1000 = np.stack([cfc_filter(out[:, j], fs, 1000) for j in range(out.shape[1])], axis=1)
            res_180 = resultant(out180)
            res_1000 = resultant(out1000)
            out_raw_peak = windowed_peak(t, res_raw, i_imp, dt)["peak_abs_g"]
            m_out_1000 = windowed_peak(t, res_1000, i_imp, dt)
            m_out_180 = windowed_peak(t, res_180, i_imp, dt)

            in180 = m_in_180["peak_abs_g"]
            out180_pk = m_out_180["peak_abs_g"]
            transmiss = out180_pk / in180 if in180 else float("nan")

            rows.append(
                {
                    "spec": spec,
                    "drop": k,
                    "t_imp_ms": t[i_imp] * 1e3,
                    "in_raw_g": in_raw,
                    "in_1000_g": m_in_1000["peak_abs_g"],
                    "in_180_g": in180,
                    "out_raw_g": out_raw_peak,
                    "out_1000_g": m_out_1000["peak_abs_g"],
                    "out_180_g": out180_pk,
                    "transmiss": transmiss,
                    "in_width_ms": m_in_180["pulse_width_ms"],
                    "in_dv_ms": m_in_180["delta_v_ms"],
                }
            )
            traces[(spec, k)] = (t, ch5, ch5_180, res_raw, res_180, i_imp)

    # ---- per-drop metrics table -------------------------------------
    hdr = (
        f"{'specimen':9s} {'drop':>4s} {'t_imp':>6s} "
        f"{'IN raw':>7s} {'IN 1k':>6s} {'IN 180':>7s} "
        f"{'OUT raw':>8s} {'OUT 1k':>7s} {'OUT 180':>8s} "
        f"{'T(180)':>7s} {'wid[ms]':>8s} {'Δv':>6s}"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['spec']:9s} {r['drop']:4d} {r['t_imp_ms']:6.2f} "
            f"{r['in_raw_g']:7.0f} {r['in_1000_g']:6.0f} {r['in_180_g']:7.0f} "
            f"{r['out_raw_g']:8.0f} {r['out_1000_g']:7.0f} {r['out_180_g']:8.0f} "
            f"{r['transmiss']:7.2f} {r['in_width_ms']:8.2f} {r['in_dv_ms']:6.2f}"
        )

    # ---- per-specimen aggregates (mean +- 1 sigma, CV) ---------------
    print("\nper-specimen (mean +- 1σ over 5 drops; CV in %)")
    aggs = {}
    ahdr = (
        f"{'specimen':9s} {'IN 180 [G]':>16s} {'OUT 180 [G]':>16s} "
        f"{'T = OUT/IN':>16s} {'in CV':>6s} {'out CV':>7s} {'T CV':>6s}"
    )
    print(ahdr)
    print("-" * len(ahdr))
    for spec in SPECIMENS:
        rs = [r for r in rows if r["spec"] == spec]
        if not rs:
            continue
        ins = [r["in_180_g"] for r in rs]
        outs = [r["out_180_g"] for r in rs]
        ts = [r["transmiss"] for r in rs]
        aggs[spec] = {
            "in_mean": np.mean(ins),
            "in_std": np.std(ins, ddof=1),
            "out_mean": np.mean(outs),
            "out_std": np.std(outs, ddof=1),
            "t_mean": np.mean(ts),
            "t_std": np.std(ts, ddof=1),
            "in_cv": cv(ins),
            "out_cv": cv(outs),
            "t_cv": cv(ts),
        }
        a = aggs[spec]
        print(
            f"{spec:9s} {a['in_mean']:8.0f} ± {a['in_std']:5.0f} "
            f"{a['out_mean']:8.0f} ± {a['out_std']:5.0f} "
            f"{a['t_mean']:8.2f} ± {a['t_std']:5.2f} "
            f"{a['in_cv']:5.1f} {a['out_cv']:6.1f} {a['t_cv']:5.1f}"
        )

    # ---- Fig 1: input vs output impact window, one panel per specimen
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, spec in zip(axes.ravel(), SPECIMENS):
        for k in range(1, N_DROPS + 1):
            key = (spec, k)
            if key not in traces:
                continue
            t, _c5, c5_180, _rr, res_180, i_imp = traces[key]
            t0 = t[i_imp] * 1e3
            w = (t * 1e3 > t0 - 4) & (t * 1e3 < t0 + 10)
            ax.plot(t[w] * 1e3, c5_180[w], lw=1.0, color="tab:blue", alpha=0.6,
                    label="input CH5 (base)" if k == 1 else None)
            ax.plot(t[w] * 1e3, res_180[w], lw=1.0, color="tab:red", alpha=0.6,
                    label="output |tri-axis| (vertex)" if k == 1 else None)
        a = aggs.get(spec, {})
        title = spec
        if a:
            title += f"  —  T = {a['t_mean']:.2f} ± {a['t_std']:.2f}"
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.3)
        ax.set_ylabel("CFC-180 a (G)")
    axes[0, 0].legend(fontsize=7, loc="upper right")
    for ax in axes[-1]:
        ax.set_xlabel("time (ms)")
    fig.suptitle(
        "Input (base CH5) vs output (vertex tri-axis) CFC-180 — 5 drops overlaid per specimen",
        y=0.995,
    )
    fig.tight_layout()
    fig.savefig(FIG / "01_input_output_impact.png", dpi=130)
    plt.close(fig)

    # ---- Fig 2: transmissibility per specimen (mean +- 1 sigma) ------
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(SPECIMENS))
    means = [aggs[s]["t_mean"] for s in SPECIMENS]
    stds = [aggs[s]["t_std"] for s in SPECIMENS]
    bars = ax.bar(x, means, yerr=stds, capsize=5, color="tab:purple", alpha=0.8)
    ax.axhline(1.0, color="0.4", ls="--", lw=1, label="T = 1 (output = input)")
    for xi, s in zip(x, SPECIMENS):
        ax.text(xi, aggs[s]["t_mean"] + aggs[s]["t_std"] + 0.02,
                f"CV {aggs[s]['t_cv']:.1f}%", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(SPECIMENS)
    ax.set(
        ylabel="transmissibility T = OUT/IN (CFC-180)",
        title="Vertex/base transmissibility per specimen (mean ± 1σ over 5 drops)",
    )
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "02_transmissibility_bars.png", dpi=130)
    plt.close(fig)

    # ---- Fig 3: input repeatability (CH5 CFC-180 peak per drop) ------
    fig, ax = plt.subplots(figsize=(9, 5))
    for spec in SPECIMENS:
        rs = [r for r in rows if r["spec"] == spec]
        ax.plot([r["drop"] for r in rs], [r["in_180_g"] for r in rs], "o-",
                label=f"{spec} (in)", alpha=0.8)
    ax.set(
        xlabel="drop #",
        ylabel="input CH5 CFC-180 peak |g| (G)",
        title="Input (base-plate) repeatability — bungees removed gives a controlled strike",
        xticks=range(1, N_DROPS + 1),
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_input_repeatability.png", dpi=130)
    plt.close(fig)

    # ---- Fig 4: output PSD per specimen (first drop) -----------------
    fig, ax = plt.subplots(figsize=(10, 5))
    for spec in SPECIMENS:
        key = (spec, 1)
        if key not in traces:
            continue
        _t, _c5, _c5180, res_raw, *_rest = traces[key]
        f, pxx = signal.welch(res_raw, fs, nperseg=4096)
        ax.semilogy(f, pxx, lw=0.9, label=f"{spec} (vertex out)")
    ax.axvline(1650, color="tab:blue", ls="--", lw=1, label="CFC 1000 (1650 Hz)")
    ax.axvline(300, color="tab:red", ls="--", lw=1, label="CFC 180 (300 Hz)")
    ax.set(
        xlabel="frequency (Hz)",
        ylabel="PSD (G²/Hz)",
        xlim=(0, 25000),
        title="Output (vertex tri-axis resultant) PSD — drop 1 (raw peaks are ringing-dominated)",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "04_output_psd.png", dpi=130)
    plt.close(fig)

    print(f"\nwrote figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
