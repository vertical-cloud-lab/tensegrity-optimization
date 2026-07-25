"""What is the minimum DAQ sample rate for the current drop-test analyses?

Retroactive, synthetic downsampling study on the 25 TP4 captures in
``prc1kn - set 1 - 1.zip`` (200 ms @ 125 kHz, CH2-4 top-vertex tri-axis,
CH5 plate input/trigger, session "prc1kn 60in - 4 felt 1 cardboard").

Each capture is re-recorded "as if" the TP4 had been set to a lower sample
rate r, in two flavors that bracket the real instrument:

- ``tp4``  : zero-phase 8th-order Butterworth low-pass at 0.15*r before
  subsampling -- matches the TP4's published valid-passband ratio
  (18.75 kHz at 125 kHz, i.e. 0.15*fs); conservative.
- ``ideal``: scipy.signal.decimate FIR anti-alias near Nyquist -- what a
  brick-wall anti-alias filter would deliver; optimistic.

At each rate two metric families are computed per capture:

1. **As-implemented** -- the exact per-capture pipeline of the campaign
   analyses.  ``cfc_filter``, ``windowed_peak``, ``ringdown_dom_freq``
   and ``resultant`` are vendored unchanged from
   ``scripts/analysis/drop_test_60in_5felts_analysis.py`` @ 32b009f
   (PR #86): raw peaks (saturation / 200 g real-impact floor / 300 g
   trigger), CFC-180 windowed peaks, T = TOP/CH5, half-max pulse width,
   delta-v over the half-max window, ringdown dominant frequency.
2. **Rate-robust variants** -- the same physical quantities with the
   sample-granularity sensitivities removed (3-point parabolic peak
   interpolation, delta-v over a fixed -2/+6 ms window, linearly
   interpolated half-max crossings, Welch nperseg scaled to keep the
   frequency-bin width of the 125 kHz reference).  These show what a
   small pipeline update buys at low rates.

The 10-100 Hz post-impact deformation quantities of
``analysis/issue-89-accel-window`` (brake-catch time, decay tau,
displacement-equivalent trace) are computed on a common 1 kHz processing
grid at every rate: the band only needs <=100 Hz content, and a fixed
grid keeps the band-pass numerically identical across rates (the
butter(4, 10-100 Hz) design is ill-conditioned at some intermediate fs).

Usage:
    python min_sample_rate.py --daq-dir /tmp/daq --out figures
"""

import argparse
import glob
import json
import os
import re
from fractions import Fraction

import numpy as np
from scipy import integrate, signal

FS = 125_000.0  # Hz, reference rate
PASSBAND_FRAC = 0.15  # TP4 valid passband = 0.15 * sample rate (Table 2)
# the TP4's actual selectable rates below 125 kHz (User's Guide Table 2),
# plus 625 Hz (not selectable) to show where everything collapses
RATES = [50_000, 25_000, 20_000, 10_000, 5_000, 2_500, 1_250, 625]

# --- constants vendored from drop_test_60in_5felts_analysis.py @ 32b009f ---
GRAVITY = 9.80665
TRIGGER_LEVEL_G = 300.0
REAL_IMPACT_FLOOR_G = 200.0
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080
REF_NPERSEG = 4096  # ringdown Welch nperseg at 125 kHz -> 30.5 Hz bins

# --- deformation-band constants from analysis/issue-89-accel-window -------
DEF_BAND = (10.0, 100.0)
F_REF = 30.0
G_MM = 9810.0
ENV_WIN_MS = 5.0
EDGE_TRIM_MS = 8.0
PROC_FS = 1000  # common processing grid for the deformation band

C_BLUE = "#2a78d6"
C_ORANGE = "#eb6834"
C_AQUA = "#1baf7a"
C_MUTED = "#898781"
C_GRID = "#e1e0d9"
C_INK = "#0b0b0b"
C_INK2 = "#52514e"
C_SURFACE = "#fcfcfb"


def load_capture(path):
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Time (sec)"))
    rows = np.genfromtxt(lines[start + 1:], delimiter=",")
    rows = rows[~np.isnan(rows[:, 0])]
    return rows[:, 1:5]


# ---- vendored pipeline functions (drop_test_60in_5felts_analysis.py) ------

def cfc_filter(x, fs, cfc):
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    if cutoff >= fs / 2.0:
        return None  # filter undefined at this rate
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def windowed_peak(t, a_g, i_imp, dt):
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
    dv = integrate.trapezoid(a_ms2[lo: hi + 1], t[lo: hi + 1])
    return {"peak_abs_g": peak_abs, "t_peak_ms": t[idx] * 1e3,
            "pulse_width_ms": width * 1e3, "delta_v_ms": abs(dv),
            "idx": idx}


def ringdown_dom_freq(t, tri, i_imp, fs, nperseg_cap=REF_NPERSEG):
    i0 = i_imp + int(RING_START_AFTER_IMPACT_S * fs)
    i1 = min(len(t), i0 + int(RING_LEN_S * fs))
    if i1 - i0 < 16:
        return None
    nper = min(nperseg_cap, i1 - i0)
    psd_sum = None
    for c in range(tri.shape[1]):
        seg = tri[i0:i1, c] - np.mean(tri[i0:i1, c])
        f, p = signal.welch(seg, fs=fs, nperseg=nper)
        psd_sum = p if psd_sum is None else psd_sum + p
    band = (f >= RING_BAND_HZ[0]) & (f <= RING_BAND_HZ[1])
    if not np.any(band):
        return None
    fb, pb = f[band], psd_sum[band]
    return float(fb[np.argmax(pb)])


def resultant(tri):
    return np.sqrt(np.sum(tri**2, axis=1))


# ---- rate-robust metric variants ------------------------------------------

def parabolic_peak(y, idx):
    """3-point parabolic interpolation of |peak| around sample idx."""
    a = np.abs(y)
    if idx <= 0 or idx >= len(a) - 1:
        return float(a[idx])
    y0, y1, y2 = a[idx - 1], a[idx], a[idx + 1]
    denom = y0 - 2 * y1 + y2
    if denom >= 0:
        return float(y1)
    return float(y1 - (y0 - y2) ** 2 / (8 * denom))


def interp_halfmax_width(t, y, idx):
    """Half-max width (ms) with linearly interpolated crossings, walking
    from the peak without the +-1.5 ms window clamp."""
    peak = y[idx]
    s = np.sign(peak) if peak else 1.0
    z = s * y - abs(peak) / 2.0
    i = idx
    while i > 0 and z[i - 1] >= 0:
        i -= 1
    if i == 0:
        left = t[0]
    else:
        left = t[i - 1] + (t[i] - t[i - 1]) * (-z[i - 1]) / (z[i] - z[i - 1])
    i = idx
    while i < len(z) - 1 and z[i + 1] >= 0:
        i += 1
    if i == len(z) - 1:
        right = t[-1]
    else:
        right = t[i] + (t[i + 1] - t[i]) * z[i] / (z[i] - z[i + 1])
    return (right - left) * 1e3


def dv_fixed_window(t, a_g, idx, fs):
    """Delta-v (m/s) over a fixed -2/+6 ms window around the peak."""
    j0 = max(0, idx - int(2e-3 * fs))
    j1 = min(len(a_g), idx + int(6e-3 * fs) + 1)
    return float(abs(integrate.trapezoid(a_g[j0:j1] * GRAVITY, t[j0:j1])))


# ---- deformation-band metrics (analysis/issue-89-accel-window), on a ------
# ---- common 1 kHz processing grid -----------------------------------------

def deformation_metrics(top, i_imp, fs):
    if 0.5 * fs <= DEF_BAND[1] * 1.1:
        return None
    frac = Fraction(PROC_FS, int(round(fs))).limit_denominator(100000)
    x = signal.resample_poly(top, frac.numerator, frac.denominator, axis=0)
    i_imp = int(round(i_imp * PROC_FS / fs))
    sos = signal.butter(4, DEF_BAND, btype="bandpass", fs=PROC_FS,
                        output="sos")
    xf = signal.sosfiltfilt(sos, x, axis=0)
    power = np.sum(xf**2, axis=1)
    n = max(int(ENV_WIN_MS * 1e-3 * PROC_FS), 1)
    env = np.sqrt(np.convolve(power, np.ones(n) / n, mode="same"))
    disp = env * G_MM / (2 * np.pi * F_REF) ** 2
    trim = max(int(EDGE_TRIM_MS * 1e-3 * PROC_FS), 1)
    i_end = len(disp) - trim
    j0 = i_imp + int(80e-3 * PROC_FS)
    j1 = min(i_imp + int(140e-3 * PROC_FS), i_end)
    brake_ms = None
    if j1 - j0 >= 3:
        i_brake = j0 + int(np.argmax(env[j0:j1]))
        brake_ms = (i_brake - i_imp) / PROC_FS * 1e3
    i_fit0 = i_imp + int(120e-3 * PROC_FS)
    tau_ms = None
    if i_end - i_fit0 >= 10:
        tt = np.arange(i_end - i_fit0) / PROC_FS
        seg = disp[i_fit0:i_end]
        slope, _ = np.polyfit(tt, np.log(np.maximum(seg, 1e-9)), 1)
        tau_ms = -1e3 / slope if slope < 0 else None
    t_ms = (np.arange(len(disp)) - i_imp) / PROC_FS * 1e3
    return {"disp": disp, "t_ms": t_ms, "i_end": i_end,
            "brake_ms": brake_ms, "tau_ms": tau_ms}


# ---- rate simulation ------------------------------------------------------

def simulate_rate(data, rate, flavor):
    """Re-record `data` (columns = channels @ FS) at `rate`."""
    frac = Fraction(int(rate), int(FS))
    if flavor == "tp4":
        sos = signal.butter(8, PASSBAND_FRAC * rate, fs=FS, output="sos")
        data = signal.sosfiltfilt(sos, data, axis=0)
    # polyphase resampling; its kaiser FIR anti-aliases at the target
    # Nyquist, which is the whole simulation for the "ideal" flavor
    return signal.resample_poly(data, frac.numerator, frac.denominator,
                                axis=0)


# ---- per-capture pipeline at a given rate ---------------------------------

def analyze_at_rate(data, rate=None, flavor=None):
    """Run the campaign per-capture pipeline (plus rate-robust variants)
    on `data` re-recorded at `rate` (None = full-rate reference)."""
    fs = float(rate) if rate else FS
    ch = data if rate is None else simulate_rate(data, rate, flavor)
    t = np.arange(len(ch)) / fs
    dt = 1.0 / fs
    nb = max(1, int(BASELINE_S / dt))

    top = ch[:, 0:3] - np.median(ch[:nb, 0:3], axis=0)
    ch5 = ch[:, 3] - np.median(ch[:nb, 3])

    i_imp = int(np.argmax(np.abs(ch5)))
    row = {
        "fs": fs,
        "ch5_raw_g": float(np.abs(ch5[i_imp])),
        "top_raw_g": float(np.max(resultant(top))),
    }
    f180 = cfc_filter(ch5, fs, 180)
    if f180 is not None:
        top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)],
                          axis=1)
        res180 = resultant(top180)
        m_top = windowed_peak(t, res180, i_imp, dt)
        m_ch5 = windowed_peak(t, f180, i_imp, dt)
        # as-implemented campaign metrics
        row.update({
            "top_180_g": m_top["peak_abs_g"],
            "ch5_180_g": m_ch5["peak_abs_g"],
            "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
            "ch5_width_ms": m_ch5["pulse_width_ms"],
            "ch5_dv_ms": m_ch5["delta_v_ms"],
        })
        # rate-robust variants of the same quantities
        top_i = parabolic_peak(res180, m_top["idx"])
        ch5_i = parabolic_peak(f180, m_ch5["idx"])
        row.update({
            "top_180i_g": top_i,
            "ch5_180i_g": ch5_i,
            "t_ch5i": top_i / ch5_i,
            "ch5_widthi_ms": interp_halfmax_width(t, f180, m_ch5["idx"]),
            "ch5_dvf_ms": dv_fixed_window(t, f180, m_ch5["idx"], fs),
        })
    f1000 = cfc_filter(ch5, fs, 1000)
    if f1000 is not None:
        row["ch5_1000_g"] = windowed_peak(t, f1000, i_imp, dt)["peak_abs_g"]
    row["dom_freq_hz"] = ringdown_dom_freq(t, top, i_imp, fs)
    # resolution-matched variant: keep the reference's 30.5 Hz bin width
    row["dom_freqm_hz"] = ringdown_dom_freq(
        t, top, i_imp, fs, nperseg_cap=max(8, int(round(REF_NPERSEG * fs / FS))))
    row["_dm"] = deformation_metrics(top, i_imp, fs)
    dm = row["_dm"]
    row["brake_ms"] = dm["brake_ms"] if dm else None
    row["tau_ms"] = dm["tau_ms"] if dm else None
    return row


def disp_rmse(ref_dm, dm):
    """RMS error (mm) of the 10-100 Hz deformation trace vs reference."""
    if dm is None or ref_dm is None:
        return None
    t0 = 10.0
    t1 = min(ref_dm["t_ms"][ref_dm["i_end"] - 1], dm["t_ms"][dm["i_end"] - 1])
    m = (ref_dm["t_ms"] >= t0) & (ref_dm["t_ms"] <= t1)
    interp = np.interp(ref_dm["t_ms"][m], dm["t_ms"][: dm["i_end"]],
                       dm["disp"][: dm["i_end"]])
    return float(np.sqrt(np.mean((interp - ref_dm["disp"][m]) ** 2)))


def natural_key(path):
    m = re.search(r"Signal(\d+)", path)
    return int(m.group(1)) if m else 0


def agg(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "median": float(np.median(vals)),
            "p95": float(np.percentile(vals, 95))}


REL_METRICS = ["ch5_raw_g", "top_raw_g", "ch5_180_g", "top_180_g", "t_ch5",
               "ch5_width_ms", "ch5_dv_ms", "ch5_1000_g",
               "ch5_180i_g", "top_180i_g", "t_ch5i", "ch5_widthi_ms",
               "ch5_dvf_ms", "tau_ms"]
ABS_METRICS = ["dom_freq_hz", "dom_freqm_hz", "brake_ms"]

# acceptance: median |error| for "the analysis still works at this rate"
ACCEPT_ASIS = {"t_ch5": 1.0, "top_180_g": 2.0, "ch5_180_g": 2.0,
               "ch5_dv_ms": 2.0, "ch5_width_ms": 5.0}  # %
ACCEPT_ROBUST = {"t_ch5i": 1.0, "top_180i_g": 2.0, "ch5_180i_g": 2.0,
                 "ch5_dvf_ms": 2.0, "ch5_widthi_ms": 5.0}  # %
ACCEPT_DOM_HZ = 16.0  # ~half the reference Welch bin (30.5 Hz)
ACCEPT_BRAKE_MS = 2.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daq-dir", default="/tmp/daq")
    ap.add_argument("--out", default="figures")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    files = sorted(glob.glob(os.path.join(args.daq_dir, "*.csv")),
                   key=natural_key)
    captures = [load_capture(f) for f in files]
    refs = [analyze_at_rate(d) for d in captures]

    errors = {fl: {} for fl in ("tp4", "ideal")}
    extras = {fl: {} for fl in ("tp4", "ideal")}
    for fl in ("tp4", "ideal"):
        for r in RATES:
            sims = [analyze_at_rate(d, r, fl) for d in captures]
            e = {}
            for k in REL_METRICS:
                e[k] = [abs(s[k] / rf[k] - 1) * 100
                        for s, rf in zip(sims, refs)
                        if s.get(k) and rf.get(k)]
            for k in ABS_METRICS:
                e[k] = [abs(s[k] - rf[k])
                        for s, rf in zip(sims, refs)
                        if s.get(k) is not None and rf.get(k) is not None]
            e["disp_rmse_mm"] = [v for v in (
                disp_rmse(rf["_dm"], s["_dm"])
                for s, rf in zip(sims, refs)) if v is not None]
            errors[fl][r] = e
            tv = [s["t_ch5"] for s in sims if s.get("t_ch5")]
            extras[fl][r] = {
                "ch5_raw_median_g": agg([s["ch5_raw_g"] for s in sims]),
                "frac_above_floor": float(np.mean(
                    [s["ch5_raw_g"] >= REAL_IMPACT_FLOOR_G for s in sims])),
                "frac_above_trigger": float(np.mean(
                    [s["ch5_raw_g"] >= TRIGGER_LEVEL_G for s in sims])),
                "t_ch5_cv_pct": (float(100 * np.std(tv, ddof=1)
                                       / np.mean(tv)) if len(tv) > 2
                                 else None),
            }

    def min_ok_rate(fl, accept, dom_key):
        ok_rates = []
        for r in RATES:
            e = errors[fl][r]
            ok = all(e[k] and np.median(e[k]) <= thr
                     for k, thr in accept.items())
            if dom_key:
                ok = ok and e[dom_key] and \
                    np.median(e[dom_key]) <= ACCEPT_DOM_HZ
                ok = ok and e["brake_ms"] and \
                    np.median(e["brake_ms"]) <= ACCEPT_BRAKE_MS
            ok = ok and extras[fl][r]["frac_above_trigger"] == 1.0
            if ok:
                ok_rates.append(r)
        return min(ok_rates) if ok_rates else None

    min_rate = {
        "as_implemented": {fl: min_ok_rate(fl, ACCEPT_ASIS, None)
                           for fl in ("tp4", "ideal")},
        "robust_variants": {fl: min_ok_rate(fl, ACCEPT_ROBUST, "dom_freqm_hz")
                            for fl in ("tp4", "ideal")},
    }

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
        "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False,
    })

    # ---- figure 1: where the signal content lives -----------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    d0 = captures[0]
    nb = int(BASELINE_S * FS)
    plate0 = d0[:, 3] - np.median(d0[:nb, 3])
    top0 = d0[:, 0:3] - np.median(d0[:nb, 0:3], axis=0)
    topres = resultant(top0)
    for sig, col, lab in ((plate0, C_BLUE, "CH5 plate (input/trigger)"),
                          (topres, C_ORANGE, "top vertex |a| (CH2-4)")):
        f, p = signal.welch(sig - np.mean(sig), fs=FS, nperseg=1 << 14)
        ax1.loglog(f[1:], np.sqrt(p[1:]), color=col, lw=1.2, label=lab)
        cum = np.cumsum(p) / np.sum(p)
        f99 = f[np.searchsorted(cum, 0.99)]
        ax2.semilogx(f[1:], cum[1:] * 100, color=col, lw=1.6)
        ax2.plot([f99], [99], "o", color=col, ms=5)
        ax2.annotate(f"99% @ {f99:.0f} Hz",
                     xy=(f99 * 1.25, 96 if col == C_BLUE else 89),
                     color=col, fontsize=8.5)
    ax1.axvline(300, color=C_MUTED, lw=0.9, ls="--")
    ax1.annotate("CFC-180\ncutoff", xy=(330, 2e-4), color=C_INK2,
                 fontsize=8.5)
    ax1.set_xlabel("frequency (Hz)")
    ax1.set_ylabel("amplitude spectral density (g/√Hz)")
    ax1.set_title("Spectral content of a 60″ drop (Signal1)",
                  loc="left", fontsize=11, color=C_INK)
    ax1.legend(loc="lower left", frameon=False, fontsize=8.5)
    ax2.set_xlabel("frequency (Hz)")
    ax2.set_ylabel("cumulative signal energy (%)")
    ax2.set_ylim(0, 104)
    ax2.set_title("Energy is gone long before the 18.75 kHz passband",
                  loc="left", fontsize=11, color=C_INK)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, "01_spectral_content.png"), dpi=150)
    plt.close(fig)

    # ---- figure 2: the analysis pulse re-recorded at candidate rates ----
    fig, ax = plt.subplots(figsize=(9, 4.6))
    i_pk = int(np.argmax(np.abs(plate0)))
    t_ms = (np.arange(len(plate0)) - i_pk) / FS * 1e3
    ax.plot(t_ms, plate0, color=C_GRID, lw=0.8, label="raw CH5 @ 125 kHz")
    ax.plot(t_ms, cfc_filter(plate0, FS, 180), color=C_INK, lw=1.8,
            label="CFC-180 @ 125 kHz (what the analysis uses)", zorder=5)
    for r, col in zip([10_000, 5_000, 2_500, 1_250],
                      [C_BLUE, C_AQUA, C_ORANGE, C_MUTED]):
        sim = simulate_rate(d0, r, "tp4")
        nb_r = max(1, int(BASELINE_S * r))
        pl = sim[:, 3] - np.median(sim[:nb_r, 3])
        fl180 = cfc_filter(pl, r, 180)
        if fl180 is None:
            continue
        tt = (np.arange(len(pl)) * (FS / r) - i_pk) / FS * 1e3
        ax.plot(tt, fl180, "-o", color=col, lw=1.1, ms=3.2,
                label=f"CFC-180 @ {r/1000:g} kHz (TP4-style)")
    ax.set_xlim(-4, 9)
    ax.set_xlabel("time after raw peak (ms)")
    ax.set_ylabel("plate acceleration (g)")
    ax.set_title("The CFC-180 analysis pulse, synthetically re-recorded",
                 loc="left", fontsize=11, color=C_INK)
    ax.legend(loc="upper right", frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, "02_pulse_vs_rate.png"), dpi=150)
    plt.close(fig)

    # ---- figure 3: metric errors vs rate --------------------------------
    panels = [
        ("t_ch5", "t_ch5i", "T = TOP/CH5 error (%)", 1.0, "%"),
        ("top_180_g", "top_180i_g", "TOP CFC-180 peak error (%)", 2.0, "%"),
        ("ch5_180_g", "ch5_180i_g", "CH5 CFC-180 peak error (%)", 2.0, "%"),
        ("ch5_dv_ms", "ch5_dvf_ms", "Δv error (%)", 2.0, "%"),
        ("ch5_width_ms", "ch5_widthi_ms", "pulse width error (%)", 5.0, "%"),
        ("dom_freq_hz", "dom_freqm_hz", "ringdown dom. freq error (Hz)",
         ACCEPT_DOM_HZ, "Hz"),
        ("brake_ms", None, "brake-catch timing error (ms)",
         ACCEPT_BRAKE_MS, "ms"),
        ("disp_rmse_mm", None, "deformation trace RMSE (mm)", 0.1, "mm"),
        ("tau_ms", None, "decay τ error (%)", 10.0, "%"),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(11.5, 9.6))
    for ax, (mkey, rkey, ylab, thr, unit) in zip(axes.flat, panels):
        for fl, col in (("tp4", C_ORANGE), ("ideal", C_BLUE)):
            for key, ls, lw in ((mkey, "-", 1.6), (rkey, "--", 1.2)):
                if key is None:
                    continue
                xs, med = [], []
                for r in RATES:
                    vals = errors[fl][r].get(key, [])
                    if len(vals) >= 5:
                        xs.append(r)
                        med.append(max(np.median(vals), 1e-4))
                ax.plot(xs, med, ls, marker="o", color=col, ms=3.5, lw=lw)
        ax.axhline(thr, color=C_INK2, lw=0.9, ls=":")
        ax.annotate(f"accept ≤ {thr:g} {unit}", xy=(0.02, 0.92),
                    xycoords="axes fraction", color=C_INK2, fontsize=8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("simulated sample rate (Hz)")
        ax.set_title(ylab, loc="left", fontsize=10, color=C_INK)
    from matplotlib.lines import Line2D
    handles = [
        Line2D([], [], color=C_ORANGE, lw=1.6, marker="o", ms=3.5,
               label="TP4-style (0.15·fs passband), as-implemented"),
        Line2D([], [], color=C_ORANGE, lw=1.2, ls="--", marker="o", ms=3.5,
               label="TP4-style, rate-robust variant"),
        Line2D([], [], color=C_BLUE, lw=1.6, marker="o", ms=3.5,
               label="ideal anti-alias, as-implemented"),
        Line2D([], [], color=C_BLUE, lw=1.2, ls="--", marker="o", ms=3.5,
               label="ideal anti-alias, rate-robust variant"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False,
               fontsize=8.5)
    fig.suptitle("Campaign-pipeline metric error vs simulated DAQ rate "
                 "(median over 25 drops)",
                 x=0.01, ha="left", fontsize=12, color=C_INK)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    fig.savefig(os.path.join(args.out, "03_metric_errors_vs_rate.png"),
                dpi=150)
    plt.close(fig)

    # ---- figure 4: raw peak attenuation -> trigger / floor margins ------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    for fl, col, lab in (("tp4", C_ORANGE, "TP4-style"),
                         ("ideal", C_BLUE, "ideal anti-alias")):
        xs = RATES
        med = [extras[fl][r]["ch5_raw_median_g"]["median"] for r in xs]
        ax1.plot(xs, med, "-o", color=col, ms=4, lw=1.6, label=lab)
        ax2.plot(xs, [100 * extras[fl][r]["frac_above_trigger"] for r in xs],
                 "-o", color=col, ms=4, lw=1.6, label=lab)
    ref_raw = np.median([r["ch5_raw_g"] for r in refs])
    ax1.axhline(ref_raw, color=C_INK, lw=0.9, ls=":")
    ax1.annotate(f"125 kHz reference ({ref_raw:.0f} g)",
                 xy=(700, ref_raw * 1.2), color=C_INK2, fontsize=8.5)
    ax1.axhline(TRIGGER_LEVEL_G, color=C_INK2, lw=0.9, ls="--")
    ax1.annotate("300 g trigger level", xy=(700, TRIGGER_LEVEL_G * 1.18),
                 color=C_INK2, fontsize=8.5)
    ax1.axhline(REAL_IMPACT_FLOOR_G, color=C_MUTED, lw=0.9, ls="--")
    ax1.annotate("200 g real-impact floor",
                 xy=(700, REAL_IMPACT_FLOOR_G * 0.6),
                 color=C_INK2, fontsize=8.5)
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("simulated sample rate (Hz)")
    ax1.set_ylabel("median CH5 raw |peak| (g)")
    ax1.set_title("Raw-peak attenuation vs rate", loc="left",
                  fontsize=11, color=C_INK)
    ax1.legend(loc="lower right", frameon=False, fontsize=8.5)
    ax2.set_xscale("log")
    ax2.set_ylim(-4, 104)
    ax2.set_xlabel("simulated sample rate (Hz)")
    ax2.set_ylabel("captures with CH5 raw ≥ 300 g (%)")
    ax2.set_title("Would the 300 g trigger still fire?", loc="left",
                  fontsize=11, color=C_INK)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, "04_trigger_margin.png"), dpi=150)
    plt.close(fig)

    # ---- metrics json ---------------------------------------------------
    out = {
        "n_captures": len(captures),
        "reference_fs_hz": FS,
        "rates_hz": RATES,
        "passband_frac_tp4": PASSBAND_FRAC,
        "acceptance": {"as_implemented_pct": ACCEPT_ASIS,
                       "robust_pct": ACCEPT_ROBUST,
                       "dom_freq_hz": ACCEPT_DOM_HZ,
                       "brake_ms": ACCEPT_BRAKE_MS,
                       "trigger_retention": 1.0},
        "min_acceptable_rate_hz": min_rate,
        "reference_metrics": {
            k: agg([r.get(k) for r in refs])
            for k in REL_METRICS + ABS_METRICS
        },
        "errors": {
            fl: {str(r): {k: agg(v) for k, v in errors[fl][r].items()}
                 for r in RATES}
            for fl in ("tp4", "ideal")
        },
        "extras": {fl: {str(r): extras[fl][r] for r in RATES}
                   for fl in ("tp4", "ideal")},
        "capture_files": [os.path.basename(f) for f in files],
    }
    with open(os.path.join(args.out, "min_sample_rate_metrics.json"),
              "w") as fh:
        json.dump(out, fh, indent=2)

    print(json.dumps({"reference_metrics": out["reference_metrics"],
                      "min_acceptable_rate_hz": min_rate}, indent=2))
    keys = ["t_ch5", "t_ch5i", "top_180_g", "top_180i_g", "ch5_dv_ms",
            "ch5_dvf_ms", "ch5_width_ms", "ch5_widthi_ms", "dom_freqm_hz",
            "brake_ms", "disp_rmse_mm"]
    for fl in ("tp4", "ideal"):
        print(f"\n=== {fl}: median errors ===")
        print(" | ".join(f"{h:>12s}" for h in ["rate"] + keys + ["trig%"]))
        for r in RATES:
            row = [f"{r:>12d}"]
            for k in keys:
                a = agg(errors[fl][r].get(k, []))
                row.append(f"{a['median']:>12.3f}" if a else f"{'—':>12s}")
            row.append(f"{100 * extras[fl][r]['frac_above_trigger']:>12.0f}")
            print(" | ".join(row))


if __name__ == "__main__":
    main()
