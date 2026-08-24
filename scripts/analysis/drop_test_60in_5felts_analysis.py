#!/usr/bin/env python3
"""60 in / 5 felt-sheet validation campaign — specimens 7xadt6 and 9GMQYQ.

@ctrhjk ran the operating point recommended by the felt-sheet saturation
sweep (60 in drop height + 5 felt sheets, see
``docs/drop-test-felt-sheet-analysis.md``) as a full-length campaign on two
distinct-geometry specimens to validate the setting for the BO campaign:

  * ``7xadt6`` — 100 captures (``Marcus_{1..4}.zip``, session
    "7xadt6 60in+5felts"), and
  * ``9GMQYQ`` — 101 captures (``jin_{1..4}.zip``, session
    "9GMQYQ 60in+5felts"),

both on 2026-07-20. Rig unchanged from the felt-sheet sweep / 500drops-nobot
runs: CH2/CH3/CH4 = top-vertex key-seat tri-axis (X/Y/Z, "TOP" output),
CH5 = single-axis on the base acrylic plate (input + trigger), bottom
tri-axis removed, 200 ms / 125 kHz per capture. Raw data stays in the
committed zips — this script reads the CSVs straight out of them.

Questions this script answers (per @ctrhjk's request on PR #86):

  1. **OLS regression** — the established burn-in changepoint scan plus
     stabilized-phase OLS drift (slope, %/drop, 95 % CI, p, R²,
     Durbin-Watson, Shapiro-Wilk, split-half check) on the TOP CFC-180
     output, the CH5 input and the transmissibility T = TOP/CH5, per
     specimen.
  2. **Is 60 in / 5 felt a valid setting?** Saturation audit vs full scale,
     head-room vs the FS/3 target, repeatability (CV), and whether the two
     geometries are distinguishable (Welch t-test + Cohen's d on the
     stabilized drops).
  3. **Should the height / felt count change?** Cross-checked against the
     felt-sheet sweep's height/felt OLS model.

Emits ``data/drop-tests/60in-5felts-validation/figures/60in_5felts_metrics.json``
consumed by ``docs/drop-test-60in-5felts-analysis.md``.
"""
from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal, stats

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data" / "drop-tests"
OUT = DATA / "60in-5felts-validation"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output (X/Y/Z), top-vertex key-seat
CH5 = 3  # single-axis on the base plate — input + trigger channel

FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9}

TRIGGER_LEVEL_G = 300.0
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

REAL_IMPACT_FLOOR_G = 200.0  # CH5 raw floor for a captured impact

# Felt-sheet sweep 60 in / 5 felt condition (same rig, downscaled #35
# specimen, 5 drops) for cross-run context.
SWEEP_60_5 = {"ch5_raw_mean": 2614.0, "ch5_max_frac_fs": 0.297,
              "top180_mean": 462.0, "top180_cv": 0.7, "t_mean": 1.040}
# Felt-sheet sweep log10(CH5 peak) OLS model: each +10 in -> x1.85, each
# +1 felt -> x0.36 (docs/drop-test-felt-sheet-analysis.md section 3).
SWEEP_MODEL = {"height_per_in": 0.0266, "felt_per_sheet": -0.447}

SPECIMENS = [
    {"id": "7xadt6", "dir": DATA / "7xadt6 _60in_5felts folder",
     "zips": ["Marcus_1.zip", "Marcus_2.zip", "Marcus_3.zip", "Marcus_4.zip"],
     "prefix": "Marcus"},
    {"id": "9GMQYQ", "dir": DATA / "9GMQYQ_60in_5felts",
     "zips": ["jin_1.zip", "jin_2.zip", "jin_3.zip", "jin_4.zip"],
     "prefix": "jin"},
]


def load_captures(spec: dict) -> list[tuple[int, str]]:
    """Return [(signal_no, csv_text)] across the specimen's zips, sorted."""
    caps = []
    for zname in spec["zips"]:
        with zipfile.ZipFile(spec["dir"] / zname) as zf:
            for member in zf.namelist():
                stem = Path(member).name
                if not stem.lower().endswith(".csv"):
                    continue
                sig = int(stem.split("Signal")[1].split(".")[0])
                caps.append((sig, zf.read(member).decode("latin-1")))
    caps.sort(key=lambda c: c[0])
    return caps


def parse_capture(text: str) -> tuple[np.ndarray, np.ndarray, datetime]:
    ev = None
    for line in text.splitlines()[:TP4_HEADER_LINES]:
        if line.startswith("EventTime:"):
            ev = datetime.strptime(line.split(":", 1)[1].strip(),
                                   "%m/%d/%Y %I:%M:%S %p")
    d = np.genfromtxt(io.StringIO(text), skip_header=TP4_HEADER_LINES,
                      delimiter=",", usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5], ev


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


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
    a_ms2 = a_g * GRAVITY
    dv = integrate.trapezoid(a_ms2[lo : hi + 1], t[lo : hi + 1])
    return {"peak_abs_g": peak_abs, "t_peak_ms": t[idx] * 1e3,
            "pulse_width_ms": width * 1e3, "delta_v_ms": abs(dv)}


def ringdown_dom_freq(t: np.ndarray, tri: np.ndarray, i_imp: int, fs: float) -> float:
    i0 = i_imp + int(RING_START_AFTER_IMPACT_S * fs)
    i1 = min(len(t), i0 + int(RING_LEN_S * fs))
    nper = min(4096, i1 - i0)
    psd_sum = None
    for c in range(tri.shape[1]):
        seg = tri[i0:i1, c] - np.mean(tri[i0:i1, c])
        f, p = signal.welch(seg, fs=fs, nperseg=nper)
        psd_sum = p if psd_sum is None else psd_sum + p
    band = (f >= RING_BAND_HZ[0]) & (f <= RING_BAND_HZ[1])
    fb, pb = f[band], psd_sum[band]
    return float(fb[np.argmax(pb)])


def resultant(tri: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(tri**2, axis=1))


def cv(vals) -> float:
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def analyze_capture(sig: int, text: str) -> dict:
    t, ch, ev = parse_capture(text)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(BASELINE_S / dt))

    top = ch[:, TOP_COLS] - np.median(ch[:nb, TOP_COLS], axis=0)
    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])

    # Impact located on the triggered channel (CH5), as in the felt-sheet /
    # input-output scripts — not a global argmax on the output.
    i_imp = int(np.argmax(np.abs(ch5)))
    ch5_raw_pk = float(np.abs(ch5[i_imp]))
    is_real = ch5_raw_pk >= REAL_IMPACT_FLOOR_G

    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3)]:
        x = np.abs(ch[:, col] - np.median(ch[:nb, col]))
        pk = float(x.max())
        near = x >= 0.98 * FULL_SCALE_G[name]
        run = best = 0
        for v in near:
            run = run + 1 if v else 0
            best = max(best, run)
        sat[name] = {"peak_g": pk, "frac_fs": pk / FULL_SCALE_G[name],
                     "over_fs": bool(pk >= FULL_SCALE_G[name]),
                     "clip_run_samples": int(best)}

    row = {
        "signal": sig,
        "event_time": ev.isoformat(),
        "real_impact": bool(is_real),
        "t_imp_ms": float(t[i_imp] * 1e3),
        "ch5_raw_g": ch5_raw_pk,
        "top_raw_g": float(np.max(resultant(top))),
        "sat": sat,
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    m_top = windowed_peak(t, resultant(top180), i_imp, dt)
    m_ch5_180 = windowed_peak(t, cfc_filter(ch5, fs, 180), i_imp, dt)
    m_ch5_1000 = windowed_peak(t, cfc_filter(ch5, fs, 1000), i_imp, dt)

    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    axis_pk = [float(np.max(np.abs(top[lo:hi, j]))) for j in range(3)]

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5_180["peak_abs_g"],
        "ch5_1000_g": m_ch5_1000["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5_180["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_width_ms": m_ch5_180["pulse_width_ms"],
        "ch5_dv_ms": m_ch5_180["delta_v_ms"],
        "ch2_pk_g": axis_pk[0],
        "ch3_pk_g": axis_pk[1],
        "ch4_pk_g": axis_pk[2],
        "dom_freq_hz": ringdown_dom_freq(t, top, i_imp, fs),
    })
    return row


def ols_full(x, y) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    res = stats.linregress(x, y)
    resid = y - (res.intercept + res.slope * x)
    dw = float(np.sum(np.diff(resid) ** 2) / np.sum(resid**2)) if np.any(resid) else float("nan")
    sh_p = float(stats.shapiro(resid).pvalue) if n >= 3 else float("nan")
    tcrit = stats.t.ppf(0.975, n - 2)
    mean = float(np.mean(y))
    return {
        "n": n,
        "slope": float(res.slope),
        "slope_pct": float(100.0 * res.slope / mean),
        "ci_lo": float(res.slope - tcrit * res.stderr),
        "ci_hi": float(res.slope + tcrit * res.stderr),
        "p": float(res.pvalue),
        "r2": float(res.rvalue**2),
        "dw": dw,
        "shapiro_p": sh_p,
        "mean": mean,
        "cv": cv(y),
    }


def arr(rows, key):
    return np.array([r[key] for r in rows], float)


def analyze_specimen(spec: dict) -> dict:
    caps = load_captures(spec)
    rows = [analyze_capture(sig, text) for sig, text in caps]

    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    real = [r for r in rows if r["real_impact"]]
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])

    print(f"\n{'=' * 70}\n=== {spec['id']} ===\n{'=' * 70}")
    print(f"captures: {len(rows)} total = {len(real)} real drops"
          f" + {len(spurious)} spurious {spurious}")
    print(f"cadence: median {np.median(gaps):.0f} s "
          f"(range {gaps.min():.0f}-{gaps.max():.0f} s); span "
          f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min")
    t_imps = arr(real, "t_imp_ms")
    print(f"impact lands at {t_imps.mean():.2f} +- {t_imps.std():.2f} ms into the record")

    # saturation audit
    print("\n--- saturation audit (raw |peak| vs nominal full scale) ---")
    sat_summary = {}
    for name in FULL_SCALE_G:
        fr = np.array([r["sat"][name]["frac_fs"] for r in rows])
        clip = max(r["sat"][name]["clip_run_samples"] for r in rows)
        sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name],
                             "median_frac_fs": float(np.median(fr)),
                             "max_frac_fs": float(fr.max()),
                             "n_ge_95pct_fs": int((fr >= 0.95).sum()),
                             "n_over_fs": int((fr > 1.0).sum()),
                             "max_clip_run": clip}
        print(f"  {name}: FS {FULL_SCALE_G[name]:8.1f} G   "
              f"median {100 * np.median(fr):5.1f}% FS   max {100 * fr.max():5.1f}% FS   "
              f">=95% FS on {sat_summary[name]['n_ge_95pct_fs']}/{len(rows)}")

    drops = arr(real, "drop")
    top = arr(real, "top_180_g")
    ch5v = arr(real, "ch5_180_g")
    tch5 = arr(real, "t_ch5")
    last = int(drops[-1])

    # burn-in changepoint scan on the TOP output
    print(f"\n--- burn-in changepoint scan (TOP CFC-180, OLS on drops k+1..{last}) ---")
    scan = {}
    burn_in_k = None
    for k in range(0, 21):
        m = drops > k
        if m.sum() < 5:
            break
        o = ols_full(drops[m], top[m])
        scan[k] = o
        if burn_in_k is None and o["p"] > 0.05:
            burn_in_k = k
            print(f"  k = {k}: slope {o['slope_pct']:+.3f}%/drop, p = {o['p']:.3f}  <- first n.s.")
    if burn_in_k is None:
        burn_in_k = 5
        print(f"  no k in 0..20 yields an n.s. trend; using SOP burn-in = {burn_in_k} "
              "(campaign-scale trend, not a seating transient)")

    # stabilized-phase OLS
    stable = drops > burn_in_k
    xs = drops[stable]
    print(f"\n--- stabilized-phase OLS (drops {burn_in_k + 1}..{last}, n = {int(stable.sum())}) ---")
    results = {}
    for name, y in [("TOP output", top[stable]), ("CH5 input", ch5v[stable]),
                    ("T TOP/CH5", tch5[stable])]:
        o = ols_full(xs, y)
        results[name] = o
        print(f"  {name:11s}: mean {o['mean']:8.3f}  CV {o['cv']:5.2f}%   "
              f"slope {o['slope']:+9.4f}/drop ({o['slope_pct']:+.3f}%/drop)   "
              f"95% CI [{o['ci_lo']:+.4f}, {o['ci_hi']:+.4f}]   p = {o['p']:.2e}  "
              f"R² = {o['r2']:.3f}  DW = {o['dw']:.2f}  Shapiro p = {o['shapiro_p']:.2f}")

    mid = xs[len(xs) // 2]
    o_h1 = ols_full(xs[xs <= mid], top[stable][xs <= mid])
    o_h2 = ols_full(xs[xs > mid], top[stable][xs > mid])
    print(f"  split-half (TOP): drops {int(xs[0])}-{int(mid)}: "
          f"{o_h1['slope_pct']:+.3f}%/drop (p = {o_h1['p']:.2e}); "
          f"drops {int(mid) + 1}-{last}: {o_h2['slope_pct']:+.3f}%/drop (p = {o_h2['p']:.2e})")

    # damage / health indicators over the full campaign
    dmg = {}
    for key, label in [("top_width_ms", "output pulse width (ms)"),
                       ("dom_freq_hz", "ringdown dominant freq (Hz)"),
                       ("ch5_dv_ms", "plate input Δv (m/s)")]:
        o = ols_full(drops, arr(real, key))
        dmg[key] = o
        print(f"  {label:28s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%  "
              f"slope {o['slope_pct']:+.3f}%/drop  p = {o['p']:.2e}")

    return {
        "id": spec["id"],
        "rows": rows,
        "real": real,
        "n_captures": len(rows),
        "spurious_captures": spurious,
        "cadence_s": {"median": float(np.median(gaps)), "min": float(gaps.min()),
                      "max": float(gaps.max())},
        "span_min": float((times[-1] - times[0]).total_seconds() / 60.0),
        "saturation": sat_summary,
        "burn_in_drops": burn_in_k,
        "burn_in_scan": {str(k): v for k, v in scan.items()},
        "stabilized_window": [int(burn_in_k) + 1, last],
        "stabilized_ols": results,
        "split_half": {"first": o_h1, "second": o_h2},
        "damage_indicators": dmg,
    }


def main() -> int:
    specs = [analyze_specimen(s) for s in SPECIMENS]
    s7, s9 = specs

    # ---------------- between-specimen discrimination ----------------
    print(f"\n{'=' * 70}\n=== specimen discrimination (stabilized drops) ===\n{'=' * 70}")
    comparison = {}
    for key, label in [("top_180_g", "TOP CFC-180 (G)"), ("t_ch5", "T = TOP/CH5")]:
        vals = {}
        for s in specs:
            real = s["real"]
            drops = arr(real, "drop")
            vals[s["id"]] = arr(real, key)[drops > s["burn_in_drops"]]
        a, b = vals[s7["id"]], vals[s9["id"]]
        tt = stats.ttest_ind(a, b, equal_var=False)
        sp = np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 2.0)
        d = float((a.mean() - b.mean()) / sp) if sp else float("nan")
        comparison[key] = {
            s7["id"]: {"mean": float(a.mean()), "sd": float(a.std(ddof=1)), "cv": cv(a)},
            s9["id"]: {"mean": float(b.mean()), "sd": float(b.std(ddof=1)), "cv": cv(b)},
            "diff_pct": float(100.0 * (a.mean() - b.mean()) / b.mean()),
            "welch_t": float(tt.statistic), "welch_p": float(tt.pvalue),
            "cohens_d": d,
        }
        c = comparison[key]
        print(f"  {label:16s}: {s7['id']} {a.mean():8.3f} (CV {cv(a):.2f}%)  vs  "
              f"{s9['id']} {b.mean():8.3f} (CV {cv(b):.2f}%)   "
              f"diff {c['diff_pct']:+.1f}%   Welch p = {c['welch_p']:.2e}   d = {d:.1f}")

    # ---------------- validity of the 60 in / 5 felt setting ----------
    print(f"\n=== 60 in / 5 felt operating point vs the felt-sheet sweep ===")
    ch5_max_frac = max(s["saturation"]["CH5"]["max_frac_fs"] for s in specs)
    headroom = 1.0 / ch5_max_frac
    print(f"  worst-case CH5: {100 * ch5_max_frac:.1f}% FS -> head-room {headroom:.1f}x "
          f"(sweep predicted {100 * SWEEP_60_5['ch5_max_frac_fs']:.1f}% FS)")
    for s in specs:
        o = s["stabilized_ols"]["TOP output"]
        print(f"  {s['id']}: TOP {o['mean']:.1f} G (CV {o['cv']:.2f}%)  "
              f"[sweep specimen: {SWEEP_60_5['top180_mean']:.0f} G, "
              f"CV {SWEEP_60_5['top180_cv']:.1f}%]")

    # felt count needed at each height for worst-case CH5 <= FS/3, anchored
    # on this campaign's worst case at (60 in, 5 felt)
    anchor = np.log10(ch5_max_frac * FULL_SCALE_G["CH5"])
    target = np.log10(FULL_SCALE_G["CH5"] / 3.0)
    felt_needed = {}
    for h in (20, 30, 40, 50, 60):
        lhs = anchor + SWEEP_MODEL["height_per_in"] * (h - 60)
        need = 5.0 + max(0.0, (lhs - target) / -SWEEP_MODEL["felt_per_sheet"])
        felt_needed[h] = float(need)
    print("  felt sheets needed for CH5 <= FS/3 (sweep model, anchored on this "
          "campaign's worst case): "
          + ", ".join(f"{h} in: {v:.1f}" for h, v in felt_needed.items()))

    # ---------------- figures ----------------------------------------
    colors = {s7["id"]: "tab:red", s9["id"]: "tab:blue"}

    # Fig 1: full-series raw peaks per specimen
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for ax, s in zip(axes, specs):
        rows = s["rows"]
        sigs = arr(rows, "signal")
        ax.plot(sigs, arr(rows, "ch5_raw_g"), "o-", ms=3, color="tab:blue",
                label="CH5 raw |peak| (base plate, trigger)")
        ax.plot(sigs, arr(rows, "top_raw_g"), "s-", ms=3, color="tab:red",
                label="TOP |tri-axis| raw peak (CH2-4)")
        ax.axhline(FULL_SCALE_G["CH5"] / 3.0, color="k", ls=":", lw=1.2,
                   label="CH5 FS/3 head-room target")
        for sp_sig in s["spurious_captures"]:
            ax.axvline(sp_sig, color="gray", ls="--", lw=1)
        ax.set(ylabel="raw |peak| (G)",
               title=f"{s['id']}: {len(s['real'])} real drops / {s['n_captures']} captures "
                     f"(median cadence {s['cadence_s']['median']:.0f} s)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    axes[1].set_xlabel("capture (Signal #)")
    fig.suptitle("60 in / 5 felt validation — full series")
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: stabilized-phase OLS, TOP and T per specimen
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    for i, s in enumerate(specs):
        real = s["real"]
        drops = arr(real, "drop")
        stable = drops > s["burn_in_drops"]
        xs = drops[stable]
        for j, (key, name) in enumerate([("top_180_g", "TOP output CFC-180 (G)"),
                                         ("t_ch5", "T = TOP/CH5 (CFC-180)")]):
            ax = axes[j][i]
            y = arr(real, key)[stable]
            o = ols_full(xs, y)
            ax.plot(xs, y, "o", ms=3.5, color=colors[s["id"]])
            fit = o["mean"] - o["slope"] * xs.mean() + o["slope"] * xs
            ax.plot(xs, fit, "k-", lw=1.5,
                    label=f"OLS {o['slope']:+.4f}/drop ({o['slope_pct']:+.3f}%/drop)\n"
                          f"p = {o['p']:.1e}, R² = {o['r2']:.2f}")
            lo_f = o["mean"] - o["ci_lo"] * xs.mean() + o["ci_lo"] * xs
            hi_f = o["mean"] - o["ci_hi"] * xs.mean() + o["ci_hi"] * xs
            ax.fill_between(xs, np.minimum(lo_f, hi_f), np.maximum(lo_f, hi_f),
                            color=colors[s["id"]], alpha=0.15, label="95% CI on slope")
            ax.set(xlabel="drop #", ylabel=name,
                   title=f"{s['id']} (drops {s['stabilized_window'][0]}-"
                         f"{s['stabilized_window'][1]})")
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)
    fig.suptitle("stabilized-phase OLS drift — 60 in / 5 felt")
    fig.tight_layout()
    fig.savefig(FIG / "02_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 3: saturation audit
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for s in specs:
        rows = s["rows"]
        sigs = arr(rows, "signal")
        fr5 = np.array([r["sat"]["CH5"]["frac_fs"] for r in rows]) * 100
        fr4 = np.array([r["sat"]["CH4"]["frac_fs"] for r in rows]) * 100
        ax.plot(sigs, fr5, "o-", ms=3, color=colors[s["id"]],
                label=f"{s['id']} CH5 (FS {FULL_SCALE_G['CH5']:.0f} G)")
        ax.plot(sigs, fr4, "s--", ms=2.5, color=colors[s["id"]], alpha=0.5,
                label=f"{s['id']} CH4 (FS {FULL_SCALE_G['CH4']:.0f} G)")
    ax.axhline(100 / 3, color="k", ls=":", lw=1.2, label="FS/3 head-room target")
    ax.axhline(100, color="k", lw=1.2, label="full scale")
    ax.set(xlabel="capture (Signal #)", ylabel="raw |peak| (% of full scale)",
           title="saturation audit: worst channel per capture vs full scale")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_saturation.png", dpi=130)
    plt.close(fig)

    # Fig 4: specimen discrimination (stabilized TOP and T)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, (key, name) in zip(axes, [("top_180_g", "TOP output CFC-180 (G)"),
                                      ("t_ch5", "T = TOP/CH5")]):
        data, labels = [], []
        for s in specs:
            real = s["real"]
            drops = arr(real, "drop")
            data.append(arr(real, key)[drops > s["burn_in_drops"]])
            labels.append(s["id"])
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.5)
        for patch, s in zip(bp["boxes"], specs):
            patch.set_facecolor(colors[s["id"]])
            patch.set_alpha(0.4)
        c = comparison[key]
        ax.set(ylabel=name,
               title=f"diff {c['diff_pct']:+.1f}%  Welch p = {c['welch_p']:.1e}  "
                     f"d = {c['cohens_d']:.1f}")
        ax.grid(alpha=0.3, axis="y")
    fig.suptitle("specimen discrimination on the stabilized drops")
    fig.tight_layout()
    fig.savefig(FIG / "04_specimen_comparison.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary ------------------------
    summary = {
        "condition": {"height_in": 60, "felt_sheets": 5},
        "specimens": {s["id"]: {k: v for k, v in s.items() if k not in ("rows", "real")}
                      for s in specs},
        "per_capture": {s["id"]: s["rows"] for s in specs},
        "comparison": comparison,
        "ch5_worst_frac_fs": ch5_max_frac,
        "ch5_headroom_x": headroom,
        "felt_needed_for_fs3": felt_needed,
        "sweep_60_5_reference": SWEEP_60_5,
    }
    with open(FIG / "60in_5felts_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
