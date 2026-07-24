"""How many ms of accelerometer data are needed to catch the full deformation?

Analyzes the 25 TP4 DAQ captures in ``prc1kn - set 1 - 1.zip``
(200 ms @ 125 kHz, CH2-4 top-vertex tri-axis, CH5 base plate,
session "prc1kn 60in - 4 felt 1 cardboard") and measures, per capture:

- pre-trigger time available before the impact pulse (~4 ms in this set)
- the deformation-band (10-100 Hz) top-vertex envelope, converted to a
  displacement-equivalent amplitude via x = a / (2*pi*f_ref)^2 at the
  dominant ~30 Hz -- "full deformation captured" is a displacement
  criterion, so the answer is the time for this to fall below a
  residual-motion threshold
- the time to cross each threshold in {0.5, 0.2, 0.1, 0.05, 0.02, 0.01} mm,
  measured directly where the crossing happens in-record and extrapolated
  with the fitted post-brake exponential decay otherwise
- brake-catch secondary event timing and magnitude (it re-excites the
  structure and therefore sets the end of the transient)

Usage:
    python accel_window.py --daq-dir /tmp/daq --out figures
"""

import argparse
import glob
import json
import os
import re

import numpy as np
from scipy import signal

FS = 125_000.0  # Hz
ENV_WIN_MS = 5.0  # moving-RMS envelope window
EDGE_TRIM_MS = 8.0  # envelope invalid near record edges (filter + conv edges)
DEF_BAND = (10.0, 100.0)  # deformation band, Hz
F_REF = 30.0  # dominant post-impact frequency (20-50 Hz band) for accel->disp
G_MM = 9810.0  # mm/s^2 per g
THRESHOLDS_MM = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01]

C_BLUE = "#2a78d6"
C_ORANGE = "#eb6834"
C_AQUA = "#1baf7a"
C_MUTED = "#898781"
C_GRID = "#e1e0d9"
C_INK = "#0b0b0b"
C_INK2 = "#52514e"
C_SURFACE = "#fcfcfb"


def load_capture(path):
    """Return (t, data[n,4]) for a TP4 CSV export."""
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Time (sec)"))
    rows = np.genfromtxt(lines[start + 1:], delimiter=",")
    rows = rows[~np.isnan(rows[:, 0])]
    return rows[:, 0], rows[:, 1:5]


def band_envelope(x, lo, hi, fs=FS, win_ms=ENV_WIN_MS):
    """Moving-RMS envelope of the band-passed resultant of columns of x."""
    sos = signal.butter(4, [lo, hi], btype="bandpass", fs=fs, output="sos")
    xf = signal.sosfiltfilt(sos, x, axis=0)
    power = np.sum(xf**2, axis=1)  # resultant magnitude squared across axes
    n = max(int(win_ms * 1e-3 * fs), 1)
    kernel = np.ones(n) / n
    return np.sqrt(np.convolve(power, kernel, mode="same"))


def accel_to_disp_mm(env_g, f_ref=F_REF):
    return env_g * G_MM / (2 * np.pi * f_ref) ** 2


def analyze(path):
    t, data = load_capture(path)
    top = data[:, 0:3] - np.median(data[:, 0:3], axis=0)
    plate = data[:, 3] - np.median(data[:, 3])
    i_imp = int(np.argmax(np.abs(plate)))  # raw plate peak = impact pulse

    env_def = band_envelope(top, *DEF_BAND)
    disp = accel_to_disp_mm(env_def)

    trim = int(EDGE_TRIM_MS * 1e-3 * FS)
    i_end = len(disp) - trim  # last envelope sample not biased by edges

    # brake catch: strongest deformation-band event 80-140 ms after impact
    # (it sits at 104 +/- 1 ms across the set)
    j0 = i_imp + int(80e-3 * FS)
    j1 = min(i_imp + int(140e-3 * FS), i_end)
    i_brake = j0 + int(np.argmax(env_def[j0:j1]))
    brake_ms = (i_brake - i_imp) / FS * 1e3
    brake_g = float(np.max(np.linalg.norm(
        top[i_brake - 600: i_brake + 600], axis=1)))

    # exponential decay fit after the last major event (the brake catch)
    i_fit0 = i_imp + int(120e-3 * FS)
    tt = np.arange(i_end - i_fit0) / FS
    seg = disp[i_fit0:i_end]
    slope, icpt = np.polyfit(tt, np.log(seg), 1)
    tau_ms = -1e3 / slope if slope < 0 else None

    # time (ms after impact) for residual motion to fall below each threshold:
    # direct last-crossing where it happens in-record, decay-fit extrapolation
    # otherwise
    t_cross = {}
    for thr in THRESHOLDS_MM:
        above = np.nonzero(disp[i_imp:i_end] > thr)[0]
        if above.size == 0:
            t_cross[thr] = {"ms": 0.0, "how": "direct"}
        elif above[-1] < i_end - i_imp - 1 - int(2e-3 * FS):
            t_cross[thr] = {"ms": above[-1] / FS * 1e3, "how": "direct"}
        elif tau_ms is not None:
            t_ext = (i_fit0 - i_imp) / FS * 1e3 + tau_ms * (icpt - np.log(thr))
            t_cross[thr] = {"ms": float(t_ext), "how": "extrapolated"}
        else:
            t_cross[thr] = {"ms": None, "how": "censored"}

    n = len(t)
    return {
        "file": os.path.basename(path),
        "pre_trigger_ms": i_imp / FS * 1e3,
        "post_window_ms": (n - i_imp) / FS * 1e3,
        "peak_top_g": float(np.max(np.linalg.norm(top, axis=1))),
        "peak_disp_mm": float(np.max(disp[i_imp:i_end])),
        "brake_ms": brake_ms,
        "brake_g": brake_g,
        "decay_tau_ms": tau_ms,
        "t_cross_mm": {str(k): v for k, v in t_cross.items()},
        "_disp": disp,
        "_i_imp": i_imp,
        "_i_end": i_end,
        "_top": top,
        "_t": t,
    }


def natural_key(path):
    m = re.search(r"Signal(\d+)", path)
    return int(m.group(1)) if m else 0


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "median": float(np.median(vals)),
            "p95": float(np.percentile(vals, 95)),
            "max": float(np.max(vals)), "min": float(np.min(vals))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daq-dir", default="/tmp/daq")
    ap.add_argument("--out", default="figures")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    files = sorted(glob.glob(os.path.join(args.daq_dir, "*.csv")), key=natural_key)
    results = [analyze(f) for f in files]

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": C_SURFACE, "axes.facecolor": C_SURFACE,
        "savefig.facecolor": C_SURFACE, "axes.edgecolor": C_GRID,
        "axes.labelcolor": C_INK2, "text.color": C_INK,
        "xtick.color": C_MUTED, "ytick.color": C_MUTED,
        "grid.color": C_GRID, "grid.linewidth": 0.6,
        "axes.grid": True, "axes.axisbelow": True,
        "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    })

    # ---- figure 1: representative capture -------------------------------
    rep = results[0]
    t_ms = (rep["_t"] - rep["_t"][rep["_i_imp"]]) * 1e3
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True)

    ax1.plot(t_ms, np.linalg.norm(rep["_top"], axis=1), color=C_BLUE, lw=0.5)
    ax1.set_ylabel("top-vertex |a| (g)")
    ax1.set_title(
        "Representative capture (Signal1): impact at 0, brake catch at "
        f"+{rep['brake_ms']:.0f} ms re-excites the structure",
        loc="left", fontsize=11, color=C_INK)

    valid = slice(0, rep["_i_end"])
    ax2.semilogy(t_ms[valid], rep["_disp"][valid], color=C_ORANGE, lw=1.8,
                 label="10–100 Hz residual motion (mm-equivalent @30 Hz)")
    for thr, ls in ((0.5, "--"), (0.05, ":")):
        ax2.axhline(thr, color=C_INK2, lw=0.9, ls=ls)
        ax2.annotate(f"{thr} mm", xy=(-2, thr * 1.25), color=C_INK2,
                     fontsize=8.5, ha="right")
    ax2.set_xlabel("time after impact (ms)")
    ax2.set_ylabel("residual motion (mm)")
    ax2.set_ylim(1e-3, 50)
    ax2.legend(loc="upper right", frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, "01_capture_residual_motion.png"), dpi=150)
    plt.close(fig)

    # ---- figure 2: all captures + record length vs threshold ------------
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [1.6, 1]})
    for r in results:
        tt = (np.arange(r["_i_end"]) - r["_i_imp"]) / FS * 1e3
        ax1.semilogy(tt, r["_disp"][:r["_i_end"]], color=C_BLUE, lw=0.7,
                     alpha=0.22)
    med_brake = np.median([r["brake_ms"] for r in results])
    ax1.axvline(med_brake, color=C_MUTED, lw=0.9, ls="--")
    ax1.annotate("brake catch", xy=(med_brake + 3, 20), color=C_INK2, fontsize=9)
    for thr in (0.5, 0.05):
        ax1.axhline(thr, color=C_INK2, lw=0.9, ls=":")
        ax1.annotate(f"{thr} mm", xy=(-28, thr * 1.25), color=C_INK2, fontsize=8.5)
    ax1.set_xlim(-30, 195)
    ax1.set_ylim(1e-3, 50)
    ax1.set_xlabel("time after impact (ms)")
    ax1.set_ylabel("residual motion (mm)")
    ax1.set_title("All 25 captures: 10–100 Hz residual motion",
                  loc="left", fontsize=11, color=C_INK)

    meds, p95s = [], []
    for thr in THRESHOLDS_MM:
        vals = [r["t_cross_mm"][str(thr)]["ms"] for r in results
                if r["t_cross_mm"][str(thr)]["ms"] is not None]
        meds.append(np.median(vals))
        p95s.append(np.percentile(vals, 95))
    ax2.plot(THRESHOLDS_MM, p95s, "-o", color=C_ORANGE, ms=5,
             label="p95 of 25 drops")
    ax2.plot(THRESHOLDS_MM, meds, "-o", color=C_BLUE, ms=5, label="median")
    ax2.set_xscale("log")
    ax2.invert_xaxis()
    ax2.set_xlabel("residual-motion threshold (mm)")
    ax2.set_ylabel("required post-impact record (ms)")
    ax2.set_title("Record length vs how still is “still”",
                  loc="left", fontsize=11, color=C_INK)
    ax2.legend(loc="upper left", frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, "02_record_length_vs_threshold.png"),
                dpi=150)
    plt.close(fig)

    # ---- metrics ---------------------------------------------------------
    metrics = {
        "n_captures": len(results),
        "capture_len_ms": 200.0,
        "f_ref_hz": F_REF,
        "pre_trigger_ms": stats([r["pre_trigger_ms"] for r in results]),
        "post_window_ms": stats([r["post_window_ms"] for r in results]),
        "peak_top_g": stats([r["peak_top_g"] for r in results]),
        "peak_disp_mm": stats([r["peak_disp_mm"] for r in results]),
        "brake_ms": stats([r["brake_ms"] for r in results]),
        "brake_g": stats([r["brake_g"] for r in results]),
        "decay_tau_ms": stats([r["decay_tau_ms"] for r in results]),
        "t_cross_ms_by_threshold": {
            str(thr): {
                "median": float(np.median([
                    r["t_cross_mm"][str(thr)]["ms"] for r in results
                    if r["t_cross_mm"][str(thr)]["ms"] is not None])),
                "p95": float(np.percentile([
                    r["t_cross_mm"][str(thr)]["ms"] for r in results
                    if r["t_cross_mm"][str(thr)]["ms"] is not None], 95)),
                "n_extrapolated": sum(
                    r["t_cross_mm"][str(thr)]["how"] == "extrapolated"
                    for r in results),
            } for thr in THRESHOLDS_MM
        },
        "per_capture": [
            {k: v for k, v in r.items() if not k.startswith("_")} for r in results
        ],
    }
    with open(os.path.join(args.out, "accel_window_metrics.json"), "w") as fh:
        json.dump(metrics, fh, indent=2)

    print(json.dumps({k: v for k, v in metrics.items() if k != "per_capture"},
                     indent=2))


if __name__ == "__main__":
    main()
