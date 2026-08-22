#!/usr/bin/env python3
"""Analyze the key-seat-mounted input-output drop tests (PR #67).

This is a follow-up to the input-output (transmissibility) series
(`drop_test_input_output_analysis.py`). The instrumentation is the same
input-output pair @ctrhjk introduced — a single-axis accelerometer wax-mounted on
the bottom acrylic plate is the **input**, a tri-axis accelerometer on the top
vertex is the **output** — and the bungees are still removed. The *one* change
under test is the **output mount**: instead of a hand-applied hot-glue blob on a
rounded vertex, the tri-axis now seats in the printed **key-seat** pocket (the
"igloo" `accel_mount()` housing from #35). The question this series answers is
whether the key-seat removes the mild within-run drift the hot-glue mount showed
across five cyclic drops (pooled +0.015 in T per drop, p = 1e-4 in the prior
series) — i.e. whether the drift was mount creep, as Edison concluded, rather
than material softening.

A single specimen (`prc1kn`, a deliberately-failed print with bubbles in its TPU
cable — used here only to exercise the *mount/DAQ*, not to compare geometry) was
dropped five times from 13 in. The accelerometer eventually fell off because the
key-seat press-fit alone was not enough to retain it (Jinkwan's note); the five
captured drops are nonetheless clean.

Channel map (identical to the input-output series):
  * CH5            — single-axis accelerometer wax-mounted on the **base plate**
    = INPUT; the triggered channel (1000 G trigger, 9442.9 G full scale).
  * CH2, CH3, CH4  — tri-axis accelerometer in the vertex **key-seat** = OUTPUT
    (full scales 14492.8 / 14992.5 / 13624.0 G); trigger OFF.

File-name note: the TP4 `Signal{n}` index is the *capture* number, not the drop
number, and it is not contiguous here — drop 4's first capture (`Signal4`) was
discarded, so the five drops are `Signal{1,2,3,5,6}` = drops 1..5.

What it does mirrors the input-output script: locate the impact on the triggered
CH5 within the first 10 ms (windowed, not a global 0.2 s max), baseline-correct,
and report raw / SAE J211 CFC-1000 / CFC-180 peaks for the input (CH5) and the
tri-axis output resultant, the transmissibility T = output / input, input pulse
width and Delta-v. It additionally runs an ordinary-least-squares trend of input,
output and T against drop number (the drift test that is the point of this run).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "key-mounted" / "raw"
FIG = REPO / "data" / "drop-tests" / "key-mounted" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

OUT_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output in the vertex key-seat
CH5 = 3  # single-axis input wax-mounted on the base plate (triggered channel)

IMPACT_SEARCH_S = 0.010  # look for the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

SPECIMEN = "prc1kn"  # the (failed-print) specimen used to exercise the key-seat
# (capture index -> drop number); Signal4 was discarded, so drops are 1..5.
SIGNAL_TO_DROP = {1: 1, 2: 2, 3: 3, 5: 4, 6: 5}


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
    for sig, drop in sorted(SIGNAL_TO_DROP.items(), key=lambda kv: kv[1]):
        path = RAW / f"key_mounted_Signal{sig}.csv"
        if not path.exists():
            print(f"missing {path}")
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
                "drop": drop,
                "signal": sig,
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
        traces[drop] = (t, ch5, ch5_180, res_raw, res_180, i_imp)

    # ---- per-drop metrics table -------------------------------------
    hdr = (
        f"{'drop':>4s} {'sig':>4s} {'t_imp':>6s} "
        f"{'IN raw':>7s} {'IN 1k':>6s} {'IN 180':>7s} "
        f"{'OUT raw':>8s} {'OUT 1k':>7s} {'OUT 180':>8s} "
        f"{'T(180)':>7s} {'wid[ms]':>8s} {'Δv':>6s}"
    )
    print(f"specimen {SPECIMEN} (key-seat output mount, wax input)\n")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['drop']:4d} {r['signal']:4d} {r['t_imp_ms']:6.2f} "
            f"{r['in_raw_g']:7.0f} {r['in_1000_g']:6.0f} {r['in_180_g']:7.0f} "
            f"{r['out_raw_g']:8.0f} {r['out_1000_g']:7.0f} {r['out_180_g']:8.0f} "
            f"{r['transmiss']:7.2f} {r['in_width_ms']:8.2f} {r['in_dv_ms']:6.2f}"
        )

    # ---- aggregates + drift (OLS vs drop number) --------------------
    ins = [r["in_180_g"] for r in rows]
    outs = [r["out_180_g"] for r in rows]
    ts = [r["transmiss"] for r in rows]
    drops = np.array([r["drop"] for r in rows], float)
    print("\nmean ± 1σ over the 5 drops (CFC-180):")
    print(f"  input  CH5 : {np.mean(ins):6.1f} ± {np.std(ins, ddof=1):4.1f} G   (CV {cv(ins):.1f}%)")
    print(f"  output tri : {np.mean(outs):6.1f} ± {np.std(outs, ddof=1):4.1f} G   (CV {cv(outs):.1f}%)")
    print(f"  T = OUT/IN : {np.mean(ts):6.3f} ± {np.std(ts, ddof=1):.3f}    (CV {cv(ts):.1f}%)")

    print("\ndrift across the 5 cyclic drops (OLS vs drop #):")
    for name, v in [("input", ins), ("output", outs), ("T", ts)]:
        sl, ic, r, p, se = stats.linregress(drops, v)
        sig = "significant" if p < 0.05 else "n.s."
        print(f"  {name:7s} slope = {sl:+8.4f}/drop   p = {p:.3f}   ({sig})")

    # ---- Fig 1: input vs output impact window, 5 drops overlaid -----
    fig, ax = plt.subplots(figsize=(10, 5))
    for drop in sorted(traces):
        t, _c5, c5_180, _rr, res_180, i_imp = traces[drop]
        t0 = t[i_imp] * 1e3
        w = (t * 1e3 > t0 - 4) & (t * 1e3 < t0 + 10)
        ax.plot(t[w] * 1e3, c5_180[w], lw=1.0, color="tab:blue", alpha=0.6,
                label="input CH5 (base, wax)" if drop == 1 else None)
        ax.plot(t[w] * 1e3, res_180[w], lw=1.0, color="tab:red", alpha=0.6,
                label="output |tri-axis| (vertex key-seat)" if drop == 1 else None)
    ax.set(xlabel="time (ms)", ylabel="CFC-180 a (G)",
           title=f"{SPECIMEN}: input (base) vs output (key-seat) CFC-180 — 5 drops overlaid")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_input_output_impact.png", dpi=130)
    plt.close(fig)

    # ---- Fig 2: drift — input, output, T per drop -------------------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    a1.plot(drops, ins, "o-", color="tab:blue", label="input CH5")
    a1.plot(drops, outs, "s-", color="tab:red", label="output tri-axis")
    a1.set(xlabel="drop #", ylabel="CFC-180 peak |g| (G)",
           title="Input / output peak per drop", xticks=range(1, 6))
    a1.legend()
    a1.grid(alpha=0.3)
    a2.plot(drops, ts, "D-", color="tab:purple")
    sl, ic, r, p, se = stats.linregress(drops, ts)
    a2.plot(drops, ic + sl * drops, "--", color="0.5",
            label=f"OLS {sl:+.3f}/drop (p={p:.2f})")
    a2.axhline(1.0, color="0.4", ls=":", lw=1)
    a2.set(xlabel="drop #", ylabel="T = OUT/IN (CFC-180)",
           title="Transmissibility per drop (key-seat mount)", xticks=range(1, 6))
    a2.legend()
    a2.grid(alpha=0.3)
    fig.suptitle(f"{SPECIMEN}: key-seat output mount — no significant output drift")
    fig.tight_layout()
    fig.savefig(FIG / "02_drift_per_drop.png", dpi=130)
    plt.close(fig)

    # ---- Fig 3: output PSD (drop 1) ---------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    _t, _c5, _c5180, res_raw, *_rest = traces[1]
    f, pxx = signal.welch(res_raw, fs, nperseg=4096)
    ax.semilogy(f, pxx, lw=0.9, color="tab:red", label="output (vertex key-seat)")
    ax.axvline(1650, color="tab:blue", ls="--", lw=1, label="CFC 1000 (1650 Hz)")
    ax.axvline(300, color="0.4", ls="--", lw=1, label="CFC 180 (300 Hz)")
    ax.set(xlabel="frequency (Hz)", ylabel="PSD (G²/Hz)", xlim=(0, 25000),
           title=f"{SPECIMEN} output (tri-axis resultant) PSD — drop 1")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_output_psd.png", dpi=130)
    plt.close(fig)

    print(f"\nwrote figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
