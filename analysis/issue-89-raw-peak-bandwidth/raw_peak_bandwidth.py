"""Why the raw-peak saturation audit is bandwidth-dependent, quantified.

Follow-up to ``analysis/issue-89-min-sample-rate`` (issue #89): the caveat
"the spike reads ~1,900 g at 25 kHz vs ~6,000 g at 125 kHz" matters because
the saturation audit / FS-3 head-room rule that qualified the 60 in / 5 felt
operating point (docs/drop-test-felt-sheet-analysis.md, PR #86 pipeline
``drop_test_60in_5felts_analysis.py``) is denominated in *recorded* raw
peaks, and the recorded raw peak of the contact spike is a function of the
recording bandwidth, not a physical invariant.

Three measurements on the 25 TP4 captures in ``prc1kn - set 1 - 1.zip``
(200 ms @ 125 kHz, CH2-4 top-vertex tri-axis, CH5 plate input/trigger):

1. **Crest-attenuation curve** — CH5 raw impact peak vs recording
   bandwidth (zero-phase 8th-order Butterworth low-pass swept from the
   native 18.75 kHz passband down to 100 Hz), against the CH5 full scale
   (9,442.9 g), the FS/3 head-room target (3,148 g) and the CFC-180 peak
   the campaign metrics actually use.
2. **TP4 rate ladder** — the same peaks re-recorded TP4-style (low-pass at
   0.15*fs then subsample) at each selectable rate: recorded peak, %FS,
   apparent head-room, and the factor by which the FS/3 threshold would
   have to be rescaled to stay equivalent.
3. **Silent-clipping demonstration** — each capture's CH5 scaled x2 so its
   true 125 kHz peak exceeds full scale, hard-clipped at +/-FS (the analog
   rail), then viewed at each rate: does the audit's over-FS / clip-run
   detection still fire, and how much does clipping corrupt the CFC-180
   peak (and hence T = TOP/CH5)?

Usage:
    python raw_peak_bandwidth.py --zip "prc1kn - set 1 - 1.zip" --out figures
"""

import argparse
import io
import json
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

FS = 125_000.0  # Hz, reference rate
PASSBAND_FRAC = 0.15  # TP4 valid passband = 0.15 * sample rate (Table 2)
RATES = [125_000, 50_000, 25_000, 20_000, 10_000, 5_000, 2_500]

# constants vendored from drop_test_60in_5felts_analysis.py @ 32b009f
FULL_SCALE_CH5_G = 9442.9
HEADROOM_TARGET_G = FULL_SCALE_CH5_G / 3.0
TP4_HEADER_LINES = 9
IMPACT_HALF_WIN_S = 0.0015

CLIP_SCALE = 2.0  # scales every capture's true peak past full scale
NEAR_FS_FRAC = 0.98  # clip-run detector threshold (audit @ 32b009f)

BLUE, ORANGE, GRAY = "#2563EB", "#EA580C", "#6B7280"


def load_captures(zip_path):
    caps = []
    with zipfile.ZipFile(zip_path) as zf:
        for member in sorted(zf.namelist()):
            if not member.lower().endswith(".csv"):
                continue
            text = zf.read(member).decode("latin-1")
            d = np.genfromtxt(io.StringIO(text), skip_header=TP4_HEADER_LINES,
                              delimiter=",", usecols=(0, 1, 2, 3, 4))
            caps.append((member, d[:, 0], d[:, 1:5]))
    return caps


def lowpass(x, fs, cutoff):
    sos = signal.butter(8, cutoff / (fs / 2.0), btype="low", output="sos")
    return signal.sosfiltfilt(sos, x)


def cfc_filter(x, fs, cfc=180):
    cutoff = {180: 300.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def tp4_rerecord(x, rate):
    """Re-record a 125 kHz trace as if the TP4 were set to `rate`."""
    if rate == FS:
        return x, FS
    y = lowpass(x, FS, PASSBAND_FRAC * rate)
    step = int(round(FS / rate))
    return y[::step], FS / step


def impact_peak(x, fs, i_imp_ref_t):
    half = int(round(IMPACT_HALF_WIN_S * fs))
    i = int(round(i_imp_ref_t * fs))
    lo, hi = max(0, i - half), min(len(x), i + half)
    return float(np.max(np.abs(x[lo:hi])))


def clip_run(x, full_scale):
    """Longest consecutive run of samples at >= 0.98 FS (audit @ 32b009f)."""
    near = np.abs(x) >= NEAR_FS_FRAC * full_scale
    best = run = 0
    for v in near:
        run = run + 1 if v else 0
        best = max(best, run)
    return int(best)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default="prc1kn - set 1 - 1.zip")
    ap.add_argument("--out", default="figures")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    caps = load_captures(args.zip)
    print(f"{len(caps)} captures")

    # impact time per capture (raw CH5 argmax), in seconds
    t_imps = [c[1][int(np.argmax(np.abs(c[2][:, 3])))] for c in caps]

    # ---- 1. crest-attenuation curve ------------------------------------
    cutoffs = np.geomspace(100.0, PASSBAND_FRAC * FS, 36)
    crest = np.empty((len(caps), len(cutoffs)))
    for i, (name, t, ch) in enumerate(caps):
        ch5 = ch[:, 3]
        for j, fc in enumerate(cutoffs):
            crest[i, j] = impact_peak(lowpass(ch5, FS, fc), FS, t_imps[i])
    cfc180 = np.array([impact_peak(cfc_filter(c[2][:, 3], FS), FS, ti)
                       for c, ti in zip(caps, t_imps)])
    raw125 = np.array([impact_peak(c[2][:, 3], FS, ti)
                       for c, ti in zip(caps, t_imps)])

    # ---- 2. TP4 rate ladder --------------------------------------------
    ladder = {}
    peaks_by_rate = {}
    for rate in RATES:
        pks = []
        for (name, t, ch), ti in zip(caps, t_imps):
            y, fs_r = tp4_rerecord(ch[:, 3], rate)
            pks.append(impact_peak(y, fs_r, ti))
        pks = np.array(pks)
        peaks_by_rate[rate] = pks
        atten = pks / raw125
        ladder[rate] = {
            "peak_g_median": float(np.median(pks)),
            "peak_g_min": float(pks.min()),
            "peak_g_max": float(pks.max()),
            "frac_fs_median": float(np.median(pks) / FULL_SCALE_CH5_G),
            "frac_fs_max": float(pks.max() / FULL_SCALE_CH5_G),
            "apparent_headroom_median": float(FULL_SCALE_CH5_G / np.median(pks)),
            "atten_vs_125k_median": float(np.median(atten)),
            "atten_vs_125k_min": float(atten.min()),
            "atten_vs_125k_max": float(atten.max()),
            "fs3_equiv_threshold_g": float(HEADROOM_TARGET_G * np.median(atten)),
        }
        print(f"{rate/1000:6.1f} kHz: peak {np.median(pks):6.0f} g "
              f"({100 * np.median(pks) / FULL_SCALE_CH5_G:4.1f}% FS), "
              f"atten x{np.median(atten):.3f} "
              f"[{atten.min():.3f}-{atten.max():.3f}]")

    # ---- 3. silent-clipping demonstration ------------------------------
    clip_demo = {}
    for rate in RATES:
        rows = []
        for (name, t, ch), ti in zip(caps, t_imps):
            ref = CLIP_SCALE * ch[:, 3]
            clp = np.clip(ref, -FULL_SCALE_CH5_G, FULL_SCALE_CH5_G)
            yr, fs_r = tp4_rerecord(ref, rate)
            yc, _ = tp4_rerecord(clp, rate)
            pk_c = impact_peak(yc, fs_r, ti)
            cfc_r = impact_peak(cfc_filter(yr, fs_r), fs_r, ti)
            cfc_c = impact_peak(cfc_filter(yc, fs_r), fs_r, ti)
            rows.append({
                "true_peak_g": impact_peak(ref, FS, ti),
                "rec_peak_g": pk_c,
                "over_fs": pk_c >= FULL_SCALE_CH5_G,
                "clip_run": clip_run(yc, FULL_SCALE_CH5_G),
                "cfc180_err_pct": 100.0 * (cfc_c - cfc_r) / cfc_r,
                "t_inflation": cfc_r / cfc_c,
            })
        n = len(rows)
        clip_demo[rate] = {
            "detected_over_fs": sum(r["over_fs"] for r in rows),
            "detected_clip_run": sum(r["clip_run"] >= 2 for r in rows),
            "n": n,
            "rec_peak_frac_fs_median": float(np.median(
                [r["rec_peak_g"] for r in rows]) / FULL_SCALE_CH5_G),
            "cfc180_err_pct_median": float(np.median(
                [r["cfc180_err_pct"] for r in rows])),
            "t_inflation_median": float(np.median(
                [r["t_inflation"] for r in rows])),
        }
        d = clip_demo[rate]
        print(f"clip demo {rate/1000:6.1f} kHz: over-FS {d['detected_over_fs']}"
              f"/{n}, clip-run {d['detected_clip_run']}/{n}, recorded "
              f"{100 * d['rec_peak_frac_fs_median']:.0f}% FS, CFC-180 err "
              f"{d['cfc180_err_pct_median']:+.1f}%, T x{d['t_inflation_median']:.2f}")

    # ---- figures -------------------------------------------------------
    plt.rcParams.update({"figure.dpi": 130, "axes.grid": True,
                         "grid.alpha": 0.25, "axes.axisbelow": True,
                         "font.size": 9})

    # Fig 1: crest attenuation + rate ladder
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    med = np.median(crest, axis=0)
    ax.fill_between(cutoffs, crest.min(axis=0), crest.max(axis=0),
                    color=BLUE, alpha=0.18, lw=0)
    ax.plot(cutoffs, med, color=BLUE, lw=2)
    for rate, dy in zip(RATES, [(-14), 10, -16, 10, 10, 10, -16]):
        fc = PASSBAND_FRAC * rate
        pk = np.interp(fc, cutoffs, med)
        ax.plot([fc], [pk], "o", color=BLUE, ms=6, mec="white", mew=1)
        ax.annotate(f"{rate / 1000:g} kHz", (fc, pk),
                    textcoords="offset points", xytext=(0, dy),
                    ha="center", fontsize=8, color=GRAY)
    ax.axhline(FULL_SCALE_CH5_G, color=GRAY, lw=1.2, ls="--")
    ax.axhline(HEADROOM_TARGET_G, color=GRAY, lw=1.2, ls=":")
    ax.axhline(np.median(cfc180), color=ORANGE, lw=1.4)
    ax.text(105, FULL_SCALE_CH5_G - 620, "CH5 full scale 9,443 g",
            color=GRAY, fontsize=8)
    ax.text(105, HEADROOM_TARGET_G + 180, "FS/3 head-room target 3,148 g",
            color=GRAY, fontsize=8)
    ax.text(105, np.median(cfc180) + 620,
            f"CFC-180 peak the analysis uses ({np.median(cfc180):.0f} g)",
            color=ORANGE, fontsize=8)
    ax.set_xscale("log")
    ax.set_ylim(-300, FULL_SCALE_CH5_G * 1.06)
    ax.set_xlabel("recording bandwidth (low-pass cutoff, Hz)")
    ax.set_ylabel("CH5 raw impact peak (g)")
    ax.set_title("Same 25 impacts, read at different bandwidths\n"
                 "(median, min–max band; dots = TP4 rate-setting passbands)")

    x = np.arange(len(RATES))
    fracs = [100 * np.median(peaks_by_rate[r]) / FULL_SCALE_CH5_G for r in RATES]
    ax2.bar(x, fracs, 0.62, color=BLUE)
    for xi, (r, f) in zip(x, zip(RATES, fracs)):
        hr = FULL_SCALE_CH5_G / np.median(peaks_by_rate[r])
        ax2.annotate(f"{f:.0f}% FS\n×{hr:.1f}", (xi, f),
                     textcoords="offset points", xytext=(0, 4),
                     ha="center", fontsize=8, color="#111827")
    ax2.axhline(100 / 3, color=GRAY, lw=1.2, ls=":")
    ax2.text(len(RATES) - 0.4, 100 / 3 + 1.2, "FS/3 target", color=GRAY,
             fontsize=8, ha="right")
    ax2.set_xticks(x, [f"{r / 1000:g}k" for r in RATES])
    ax2.set_xlabel("TP4 sample-rate setting")
    ax2.set_ylabel("recorded CH5 raw peak (% of full scale)")
    ax2.set_title("What the saturation audit would report for the\n"
                  "identical physical event (×N = apparent head-room)")
    ax2.set_ylim(0, max(fracs) * 1.30)
    fig.tight_layout()
    fig.savefig(out / "01_crest_attenuation.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 2: silent clipping, representative capture (raw peak nearest the
    # median so the x2-scaled trace genuinely exceeds full scale)
    i_rep = int(np.argmin(np.abs(raw125 - np.median(raw125))))
    name, t, ch = caps[i_rep]
    ti = t_imps[i_rep]
    ref = CLIP_SCALE * ch[:, 3]
    clp = np.clip(ref, -FULL_SCALE_CH5_G, FULL_SCALE_CH5_G)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    w = 0.0012
    m = (t > ti - w) & (t < ti + w)
    ax = axes[0]
    ax.plot((t[m] - ti) * 1e3, ref[m], color=GRAY, lw=1.2,
            label="true (scaled ×2)")
    ax.plot((t[m] - ti) * 1e3, clp[m], color=BLUE, lw=1.6,
            label="analog rail at FS")
    ax.axhline(FULL_SCALE_CH5_G, color=GRAY, ls="--", lw=1)
    ax.set_title("125 kHz record: flat-top at full scale\n→ audit flags it")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_xlabel("time from impact (ms)")
    ax.set_ylabel("CH5 (g)")
    ax = axes[1]
    for rate, color, lbl in [(125_000, GRAY, "125 kHz"), (25_000, BLUE, "25 kHz")]:
        yc, fs_r = tp4_rerecord(clp, rate)
        tt = np.arange(len(yc)) / fs_r
        mm = (tt > ti - w) & (tt < ti + w)
        ax.plot((tt[mm] - ti) * 1e3, yc[mm], color=color, lw=1.6, label=lbl)
    ax.axhline(FULL_SCALE_CH5_G, color=GRAY, ls="--", lw=1)
    yc25, fs25 = tp4_rerecord(clp, 25_000)
    pk25 = impact_peak(yc25, fs25, ti)
    ax.text(0.03, 0.72, f"25 kHz records {pk25:.0f} g\n= "
            f"{100 * pk25 / FULL_SCALE_CH5_G:.0f}% FS — looks fine",
            transform=ax.transAxes, fontsize=8, color=BLUE)
    ax.set_title("Same clipped event at 25 kHz: smooth,\nfar from FS → audit sees nothing")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_xlabel("time from impact (ms)")
    ax = axes[2]
    yr, fs_r = tp4_rerecord(ref, 25_000)
    yc, _ = tp4_rerecord(clp, 25_000)
    tt = np.arange(len(yr)) / fs_r
    w2 = 0.004
    mm = (tt > ti - w2) & (tt < ti + w2)
    ax.plot((tt[mm] - ti) * 1e3, cfc_filter(yr, fs_r)[mm], color=GRAY, lw=1.6,
            label="CFC-180, unclipped")
    ax.plot((tt[mm] - ti) * 1e3, cfc_filter(yc, fs_r)[mm], color=ORANGE, lw=1.6,
            label="CFC-180, clipped")
    d25 = clip_demo[25_000]
    ax.text(0.03, 0.60, f"median over 25 drops:\nCFC-180 peak "
            f"{d25['cfc180_err_pct_median']:+.1f}%\n→ T biased "
            f"×{d25['t_inflation_median']:.2f}\n(campaign CV of T: 0.5%)",
            transform=ax.transAxes, fontsize=8, color="#111827")
    ax.set_title("The campaign metric is corrupted either way\n(CFC-180 peak depressed → T inflated)")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_xlabel("time from impact (ms)")
    fig.tight_layout()
    fig.savefig(out / "02_silent_clipping.png", bbox_inches="tight")
    plt.close(fig)

    metrics = {
        "n_captures": len(caps),
        "full_scale_ch5_g": FULL_SCALE_CH5_G,
        "raw125_peak_g": {"median": float(np.median(raw125)),
                          "min": float(raw125.min()),
                          "max": float(raw125.max())},
        "cfc180_peak_g_median": float(np.median(cfc180)),
        "crest_factor_raw125_over_cfc180_median":
            float(np.median(raw125 / cfc180)),
        "ladder": {str(k): v for k, v in ladder.items()},
        "clip_demo_scale": CLIP_SCALE,
        "clip_demo": {str(k): v for k, v in clip_demo.items()},
    }
    with open(out / "raw_peak_bandwidth_metrics.json", "w") as f:
        json.dump(metrics, f, indent=1)
    print("wrote", out / "raw_peak_bandwidth_metrics.json")


if __name__ == "__main__":
    main()
