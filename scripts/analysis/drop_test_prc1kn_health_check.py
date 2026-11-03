#!/usr/bin/env python3
"""Cross-session specimen/sensor health check for the dummy specimen ``prc1kn``.

``prc1kn`` (failed print, TPU bubbles) has now been through four instrumented
input-output sessions on the same rig — ~48 recorded drops at 13 in:

  1. **key-mounted**      (5 drops,  bare press-fit key-seat; sensor fell off
     at the end of the session)                     -> cumulative drops 1-5
  2. **key-mounted-wax**  (5 drops,  wax retainer added)      -> drops 6-10
  3. **burn-in-wax**      (8 drops,  fresh wax, 3 burn-in + 5) -> drops 11-18
  4. **drift-calibration** (30 auto-drops, fresh wax; output sensor fell off
     at drop 26, drop 25 = letting-go anomaly)      -> drops 19-48

This script asks two questions the per-session analyses could not:

  * **Specimen damage** — does any damage-sensitive metric trend across the
    accumulated drops?  Output CFC-180 peak and T are mount-confounded across
    re-waxings, so the primary structural indicators here are the **ringdown
    spectral content** of the tri-axis output (dominant frequency + spectral
    centroid of the *sum of per-axis PSDs*, which is rotation-invariant and
    hence immune to the sensor slowly rotating in the seat) and the **output
    pulse width** (a softening / cracked structure lengthens the pulse and
    lowers its resonant frequencies: f ~ sqrt(k)).
  * **Sensor damage from its two fall-offs** — the tri-axis Dytran has hit the
    plate twice (after the key-mounted run and at drift-cal drop 26).  Compare
    pre-impact noise floors per axis and the response level at near-constant
    input across the fall-off boundaries.

Channel map (identical across all four sessions): CH2/CH3/CH4 = tri-axis
output in the vertex key-seat; CH5 = single-axis input wax-mounted on the base
plate (the triggered channel in sessions 2-4; in session 1 likewise CH5).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal, stats

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data" / "drop-tests"
FIG = DATA / "prc1kn-health" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665

OUT_COLS = (0, 1, 2)  # CH2, CH3, CH4
CH5 = 3

IMPACT_SEARCH_S = 0.010
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

# Ringdown band for the structural-frequency indicator: the specimen's
# structural response lives well below the plate/fixture ringing (~kHz+).
RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SESSIONS = [
    # (label, raw dir, filename template, signal numbers in drop order,
    #  drops with a detached/anomalous output sensor -> exclude from output metrics)
    ("key-mounted", "key-mounted/raw", "key_mounted_Signal{n}.csv", [1, 2, 3, 5, 6], set()),
    ("key-mounted-wax", "key-mounted-wax/raw", "key_mounted_wax_Signal{n}.csv", [7, 8, 9, 10, 11], set()),
    ("burn-in-wax", "burn-in-wax/raw", "burn_in_wax_Signal{n}.csv", list(range(1, 9)), set()),
    ("drift-calibration", "drift-calibration/raw", "drift_calibration_Signal{n}.csv", list(range(1, 31)), {25, 26, 27, 28, 29, 30}),
]


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",", usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def impact_index(t: np.ndarray, trig: np.ndarray, dt: float) -> int:
    nb = max(1, int(BASELINE_S / dt))
    base = np.median(trig[:nb])
    rel = np.abs(trig - base)
    rel[t >= IMPACT_SEARCH_S] = -np.inf
    return int(np.argmax(rel))


def windowed_peak(t: np.ndarray, a_g: np.ndarray, i_imp: int, dt: float) -> dict:
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
    dv = integrate.trapezoid(a_g[lo : hi + 1] * GRAVITY, t[lo : hi + 1])
    return {"peak_abs_g": peak_abs, "pulse_width_ms": (width) * 1e3, "delta_v_ms": abs(dv)}


def ringdown_spectrum(t: np.ndarray, out: np.ndarray, i_imp: int, fs: float) -> dict:
    """Rotation-invariant ringdown spectral indicators of the tri-axis output.

    The sum of the per-axis PSDs equals the trace of the spectral matrix, which
    is invariant under any rigid rotation of the sensor axes — so a sensor
    slowly rotating in its seat (as in the drift-calibration run) cannot fake a
    structural frequency shift here.
    """
    i0 = i_imp + int(RING_START_AFTER_IMPACT_S * fs)
    i1 = min(len(t), i0 + int(RING_LEN_S * fs))
    nper = min(4096, i1 - i0)
    psd_sum = None
    for c in OUT_COLS:
        seg = out[i0:i1, c] - np.mean(out[i0:i1, c])
        f, p = signal.welch(seg, fs=fs, nperseg=nper)
        psd_sum = p if psd_sum is None else psd_sum + p
    band = (f >= RING_BAND_HZ[0]) & (f <= RING_BAND_HZ[1])
    fb, pb = f[band], psd_sum[band]
    return {
        "dom_freq_hz": float(fb[np.argmax(pb)]),
        "centroid_hz": float(np.sum(fb * pb) / np.sum(pb)),
    }


def noise_floor(out: np.ndarray, dt: float) -> list[float]:
    """Pre-impact RMS (G) per output axis — a damaged sensor gets noisy."""
    nb = max(1, int(BASELINE_S / dt))
    return [float(np.std(out[:nb, c])) for c in OUT_COLS]


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    res = stats.linregress(x, y)
    return {"slope": res.slope, "pct_per_drop": 100.0 * res.slope / np.mean(y), "p": res.pvalue, "r2": res.rvalue**2}


def main() -> None:
    rows = []
    cum = 0
    for label, sub, tmpl, signals, bad_out in SESSIONS:
        for k, n in enumerate(signals, start=1):
            cum += 1
            path = DATA / sub / tmpl.format(n=n)
            t, ch = load(path)
            dt = float(np.median(np.diff(t)))
            fs = 1.0 / dt
            i_imp = impact_index(t, ch[:, CH5], dt)
            base = np.median(ch[: max(1, int(BASELINE_S / dt))], axis=0)
            chc = ch - base
            in180 = windowed_peak(t, cfc_filter(chc[:, CH5], fs, 180), i_imp, dt)
            # per-axis CFC-180 first, then the resultant — same order of
            # operations as every prior analysis in this series
            res_180 = np.sqrt(
                np.sum(
                    np.stack([cfc_filter(chc[:, c], fs, 180) for c in OUT_COLS], axis=1) ** 2,
                    axis=1,
                )
            )
            out180 = windowed_peak(t, res_180, i_imp, dt)
            row = {
                "session": label,
                "drop_in_session": k,
                "cum_drop": cum,
                "input_cfc180_g": in180["peak_abs_g"],
                "input_pulse_ms": in180["pulse_width_ms"],
                "output_valid": k not in bad_out,
                "noise_rms_g": noise_floor(chc, dt),
            }
            if row["output_valid"]:
                row.update(
                    output_cfc180_g=out180["peak_abs_g"],
                    output_pulse_ms=out180["pulse_width_ms"],
                    T=out180["peak_abs_g"] / in180["peak_abs_g"],
                    **ringdown_spectrum(t, chc, i_imp, fs),
                )
            rows.append(row)

    valid = [r for r in rows if r["output_valid"]]

    print(f"{'session':18s} {'drop':>4s} {'cum':>4s} {'IN180':>7s} {'OUT180':>7s} {'T':>6s} {'pulse':>6s} {'fdom':>6s} {'fcent':>6s}")
    for r in rows:
        if r["output_valid"]:
            print(
                f"{r['session']:18s} {r['drop_in_session']:4d} {r['cum_drop']:4d} "
                f"{r['input_cfc180_g']:7.1f} {r['output_cfc180_g']:7.1f} {r['T']:6.3f} "
                f"{r['output_pulse_ms']:6.3f} {r['dom_freq_hz']:6.0f} {r['centroid_hz']:6.0f}"
            )
        else:
            print(f"{r['session']:18s} {r['drop_in_session']:4d} {r['cum_drop']:4d} {r['input_cfc180_g']:7.1f}    (output sensor detached/anomalous)")

    # -- damage-trend regressions on the mount-robust indicators ------------
    print("\nOLS vs cumulative drop (valid output drops, n = %d):" % len(valid))
    trends = {}
    for key in ("dom_freq_hz", "centroid_hz", "output_pulse_ms"):
        tr = ols([r["cum_drop"] for r in valid], [r[key] for r in valid])
        trends[key] = tr
        print(f"  {key:16s} slope {tr['slope']:+8.3f}/drop  ({tr['pct_per_drop']:+.3f} %/drop)  p={tr['p']:.3f}  R2={tr['r2']:.2f}")

    # per-session summary
    print("\nPer-session summary (mean over valid output drops):")
    summary = {}
    for label, *_ in SESSIONS:
        sel = [r for r in valid if r["session"] == label]
        s = {
            "n": len(sel),
            "input_g": float(np.mean([r["input_cfc180_g"] for r in sel])),
            "output_g": float(np.mean([r["output_cfc180_g"] for r in sel])),
            "T": float(np.mean([r["T"] for r in sel])),
            "pulse_ms": float(np.mean([r["output_pulse_ms"] for r in sel])),
            "dom_freq_hz": float(np.mean([r["dom_freq_hz"] for r in sel])),
            "centroid_hz": float(np.mean([r["centroid_hz"] for r in sel])),
            "noise_rms_g": [float(np.mean([r["noise_rms_g"][i] for r in sel])) for i in range(3)],
        }
        summary[label] = s
        print(
            f"  {label:18s} n={s['n']:2d}  in {s['input_g']:5.1f} G  out {s['output_g']:5.1f} G  T {s['T']:.3f}  "
            f"pulse {s['pulse_ms']:.3f} ms  fdom {s['dom_freq_hz']:4.0f} Hz  fcent {s['centroid_hz']:4.0f} Hz  "
            f"noise RMS [{s['noise_rms_g'][0]:.2f}, {s['noise_rms_g'][1]:.2f}, {s['noise_rms_g'][2]:.2f}] G"
        )

    # ---------------------------------------------------------------- figures
    bounds = []
    acc = 0
    for _, _, _, signals, _ in SESSIONS:
        acc += len(signals)
        bounds.append(acc)

    fig, axes = plt.subplots(3, 1, figsize=(10, 11), sharex=True)
    x = [r["cum_drop"] for r in valid]
    colors = {"key-mounted": "tab:red", "key-mounted-wax": "tab:orange", "burn-in-wax": "tab:green", "drift-calibration": "tab:blue"}
    for ax, key, ylab in (
        (axes[0], "output_cfc180_g", "output CFC-180 peak (G)"),
        (axes[1], "dom_freq_hz", "ringdown dominant freq (Hz)\n100–2000 Hz band, rotation-invariant"),
        (axes[2], "output_pulse_ms", "output half-amplitude pulse width (ms)"),
    ):
        for label, *_ in SESSIONS:
            sel = [r for r in valid if r["session"] == label]
            ax.plot([r["cum_drop"] for r in sel], [r[key] for r in sel], "o-", ms=4, color=colors[label], label=label)
        for b in bounds[:-1]:
            ax.axvline(b + 0.5, color="k", ls=":", lw=0.8)
        ax.set_ylabel(ylab)
        ax.grid(alpha=0.3)
    axes[0].legend(loc="upper left", fontsize=8, ncol=2)
    axes[0].set_title("prc1kn specimen-health indicators across all four sessions (~48 drops)\n(dotted lines = session boundaries / fresh wax re-mounts)")
    axes[2].set_xlabel("cumulative recorded drop")
    fig.tight_layout()
    fig.savefig(FIG / "01_health_indicators.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i, axis_label in enumerate(("CH2", "CH3", "CH4")):
        ax.plot([r["cum_drop"] for r in rows], [r["noise_rms_g"][i] for r in rows], "o-", ms=3, label=f"{axis_label} pre-impact noise RMS")
    for b in bounds[:-1]:
        ax.axvline(b + 0.5, color="k", ls=":", lw=0.8)
    ax.set_xlabel("cumulative recorded drop")
    ax.set_ylabel("pre-impact noise RMS (G)")
    ax.set_title("Tri-axis output sensor noise floor across sessions\n(sensor fell off after session 1 and at drift-cal drop 26)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_sensor_noise_floor.png", dpi=150)
    plt.close(fig)

    with open(FIG / "prc1kn_health_metrics.json", "w") as fh:
        json.dump({"per_drop": rows, "per_session": summary, "trends_vs_cum_drop": trends}, fh, indent=2)
    print(f"\nFigures + metrics written to {FIG}")


if __name__ == "__main__":
    main()
