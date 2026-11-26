#!/usr/bin/env python3
"""Analyze the 200-drop campaign on specimen ``7xadt6`` (PR #67).

First long campaign on a fresh intact print (unique ID ``7xadt6``) — every
previous >=30-drop campaign used the failed prints ``prc1kn``/``RW5F61``, so
this is the first dataset where the damage indicators watch a real specimen.

Setup (from @ctrhjk's posting comment):
  * drop height **10 in** — a practice test at 5 in engaged neither a CH4 nor
    a CH5 trigger at 1000 G, so the height was raised until triggering worked;
  * **trigger back on CH5 (base plate, 1000 G)** — not CH4 as in the previous
    two campaigns;
  * otherwise the 7-channel layout is unchanged: CH2-4 top-vertex key-seat
    tri-axis ("TOP", output), CH5 single-axis base plate (taped), CH6-8
    low-range tri-axis in the bottom-vertex housing ("BOT").

Files are ``200drops_Signal{3..202}.csv`` (Signals 1-2 were the failed
practice/trigger attempts and were not exported), i.e. drop k = Signal k+2.

Deliverables:
  1. capture classification + CH5 trigger health at 10 in;
  2. BOT-channel dropout forensics — CH6-8 collapse to the noise floor for a
     contiguous block of the campaign and then recover;
  3. saturation audit (CH8 vs its ~989 G full scale at 10 in);
  4. burn-in + stabilized-phase OLS drift on TOP, CH5, T = TOP/CH5 (and BOT,
     T* = TOP/BOT on the BOT-alive drops), with reliability checks;
  5. mount-robust damage indicators over 200 drops on the fresh specimen.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "200drops" / "raw"
FIG = REPO / "data" / "drop-tests" / "200drops" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate (taped) — the trigger channel
BOT_COLS = (4, 5, 6)  # CH6, CH7, CH8 — low-range tri-axis, bottom-vertex housing

FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9,
                "CH6": 1002.0, "CH7": 991.1, "CH8": 989.1}

TRIGGER_LEVEL_G = 1000.0
PRETRIGGER_S = 0.004  # 2% of 200 ms

IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-trigger baseline window (nominal impact ~4.0 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

RING_BAND_HZ = (100.0, 2000.0)  # structural ringdown band
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SIGNALS = range(3, 203)  # Signals 3..202 = drops 1..200
REAL_IMPACT_FLOOR_G = 300.0
BOT_ALIVE_FLOOR_G = 50.0  # live BOT resultants are ~500-1100 G; dead <1 G

# RW5F61 reference campaigns (different specimen — context, not baselines)
RUN13 = {"label": "RW5F61 @ 13 in (CH4 trig)", "top": 226.7, "ch5": 236.3,
         "t_ch5": 0.960, "t_ch5_cv": 1.20, "ch4_raw": 3472.0}
RUN5 = {"label": "RW5F61 @ 5 in (CH4 trig)", "top": 164.5, "ch5": 174.2,
        "t_ch5": 0.945, "t_ch5_cv": 0.42, "ch4_raw_lo": 1433.0,
        "ch4_raw_hi": 1865.0}


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 7]) = (time, [CH2..CH8])."""
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",",
                      usecols=(0, 1, 2, 3, 4, 5, 6, 7))
    return d[:, 0], d[:, 1:8]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


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


def ringdown_spectrum(t: np.ndarray, tri: np.ndarray, i_imp: int, fs: float) -> dict:
    """Rotation-invariant ringdown spectral indicators of a tri-axis block."""
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
    return {
        "dom_freq_hz": float(fb[np.argmax(pb)]),
        "centroid_hz": float(np.sum(fb * pb) / np.sum(pb)),
    }


def resultant(tri: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(tri**2, axis=1))


def cv(vals) -> float:
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def event_time(path: Path) -> datetime:
    with open(path) as fh:
        for line in fh:
            if line.startswith("EventTime:"):
                return datetime.strptime(line.split(":", 1)[1].strip(),
                                         "%m/%d/%Y %I:%M:%S %p")
    raise ValueError(f"no EventTime in {path}")


def analyze_capture(path: Path) -> dict:
    t, ch = load(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(BASELINE_S / dt))

    top = ch[:, TOP_COLS] - np.median(ch[:nb, TOP_COLS], axis=0)
    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])
    bot = ch[:, BOT_COLS] - np.median(ch[:nb, BOT_COLS], axis=0)

    top_res_raw = resultant(top)
    bot_res_raw = resultant(bot)

    i_imp = int(np.argmax(top_res_raw))
    top_raw_pk = float(top_res_raw[i_imp])
    is_real = top_raw_pk >= REAL_IMPACT_FLOOR_G
    bot_alive = bool(np.max(bot_res_raw) >= BOT_ALIVE_FLOOR_G)

    # trigger forensics on CH5: first |crossing| of the 1000 G level.
    # With a 2% pre-trigger that crossing should sit at ~4.000 ms.
    over = np.abs(ch5) >= TRIGGER_LEVEL_G
    i_x = int(np.argmax(over)) if over.any() else -1
    t_x_ms = float(t[i_x] * 1e3) if i_x >= 0 else float("nan")
    # quiet check ends at 3.5 ms so the impact's own rising edge (which by
    # construction approaches the level just before the crossing) is excluded
    pre = np.abs(ch5[t < 0.0035])
    pre_max_g = float(pre.max()) if len(pre) else 0.0

    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3),
                      ("CH6", 4), ("CH7", 5), ("CH8", 6)]:
        x = np.abs(ch[:, col] - np.median(ch[:nb, col]))
        pk = float(x.max())
        sat[name] = {
            "peak_g": pk,
            "frac_fs": pk / FULL_SCALE_G[name],
            "n_pinned": int((x >= 0.995 * pk).sum()) if pk >= 0.95 * FULL_SCALE_G[name] else 0,
        }

    row = {
        "signal": None,  # filled by caller
        "event_time": event_time(path).isoformat(),
        "real_impact": bool(is_real),
        "bot_alive": bot_alive,
        "t_imp_ms": float(t[i_imp] * 1e3),
        "trig_cross_ms": t_x_ms,
        "pre_trigger_max_g": pre_max_g,
        "ch4_raw_g": float(np.max(np.abs(top[:, 2]))),
        "top_raw_g": top_raw_pk,
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "bot_raw_g": float(np.max(bot_res_raw)),
        "sat": sat,
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    res_top_180 = resultant(top180)
    ch5_180 = cfc_filter(ch5, fs, 180)

    m_top = windowed_peak(t, res_top_180, i_imp, dt)
    m_ch5 = windowed_peak(t, ch5_180, i_imp, dt)

    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    top_axis_pk = [float(np.max(np.abs(top[lo:hi, j]))) for j in range(3)]
    bot_axis_pk = [float(np.max(np.abs(bot[lo:hi, j]))) for j in range(3)]
    ring = ringdown_spectrum(t, top, i_imp, fs)
    noise_top = [float(np.std(top[:nb, j])) for j in range(3)]
    noise_bot = [float(np.std(bot[:nb, j])) for j in range(3)]

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "ch2_pk_g": top_axis_pk[0],
        "ch3_pk_g": top_axis_pk[1],
        "ch4_pk_g": top_axis_pk[2],
        "ch6_pk_g": bot_axis_pk[0],
        "ch7_pk_g": bot_axis_pk[1],
        "ch8_pk_g": bot_axis_pk[2],
        "dom_freq_hz": ring["dom_freq_hz"],
        "centroid_hz": ring["centroid_hz"],
        "noise_top_g": noise_top,
        "noise_bot_g": noise_bot,
    })
    if bot_alive:
        bot180 = np.stack([cfc_filter(bot[:, j], fs, 180) for j in range(3)], axis=1)
        m_bot = windowed_peak(t, resultant(bot180), i_imp, dt)
        row.update({
            "bot_180_g": m_bot["peak_abs_g"],
            "t_star": m_top["peak_abs_g"] / m_bot["peak_abs_g"],
            "bot_dv_ms": m_bot["delta_v_ms"],
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


def main() -> int:
    rows: list[dict] = []
    for sig in SIGNALS:
        row = analyze_capture(RAW / f"200drops_Signal{sig}.csv")
        row["signal"] = sig
        rows.append(row)

    # ---------------- capture classification + trigger health --------
    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    real = [r for r in rows if r["real_impact"]]
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])
    t_imps = np.array([r["t_imp_ms"] for r in real])
    t_cross = np.array([r["trig_cross_ms"] for r in real])
    ch5_pks = np.array([r["ch5_raw_g"] for r in real])
    ch4_pks = np.array([r["ch4_raw_g"] for r in real])
    pre_max = np.array([r["pre_trigger_max_g"] for r in real])

    print("=== 200-drop campaign (7xadt6, 10 in, CH5 trigger): classification ===\n")
    print(f"captures: {len(rows)} total = {len(real)} real drops + "
          f"{len(spurious)} spurious {spurious}")
    print(f"cadence: median {np.median(gaps):.0f} s (range {gaps.min():.0f}-{gaps.max():.0f} s); "
          f"campaign span {(times[-1] - times[0]).total_seconds() / 60:.0f} min")
    print(f"CH5 first crossing of {TRIGGER_LEVEL_G:.0f} G: "
          f"{t_cross.mean():.3f} +- {t_cross.std():.3f} ms "
          f"(range {t_cross.min():.3f}-{t_cross.max():.3f}; nominal pre-trigger 4.000 ms)")
    print(f"impact (TOP resultant argmax): {t_imps.mean():.2f} +- {t_imps.std():.2f} ms")
    print(f"CH5 raw |peak|: {ch5_pks.mean():.0f} +- {ch5_pks.std():.0f} G "
          f"(range {ch5_pks.min():.0f}-{ch5_pks.max():.0f}) -> trigger margin "
          f"{(ch5_pks / TRIGGER_LEVEL_G).min():.2f}-{(ch5_pks / TRIGGER_LEVEL_G).max():.2f}x")
    print(f"CH4 raw |peak| (for the 5-in no-trigger question): "
          f"{ch4_pks.mean():.0f} G (range {ch4_pks.min():.0f}-{ch4_pks.max():.0f})")
    print(f"pre-impact quiet: max |CH5| before 3.5 ms "
          f"{pre_max.max():.0f} G ({100 * pre_max.max() / TRIGGER_LEVEL_G:.0f}% of level)")

    # ---------------- BOT dropout forensics --------------------------
    alive = np.array([r["bot_alive"] for r in rows])
    dead_sigs = [r["signal"] for r in rows if not r["bot_alive"]]
    print(f"\n=== BOT (CH6-8) dropout ===\n")
    if dead_sigs:
        print(f"BOT at noise floor on {len(dead_sigs)}/{len(rows)} captures: "
              f"Signals {dead_sigs[0]}-{dead_sigs[-1]}"
              + ("" if np.all(np.diff(dead_sigs) == 1) else " (non-contiguous!)"))
        i0, i1 = rows.index(next(r for r in rows if not r["bot_alive"])), None
        last_dead = max(i for i, r in enumerate(rows) if not r["bot_alive"])
        nb_dead = [float(np.mean(r["noise_bot_g"])) for r in real if not r["bot_alive"]]
        print(f"dead-block dropout window: {rows[i0]['event_time']} .. "
              f"{rows[last_dead]['event_time']}")
        if nb_dead:
            print(f"BOT noise RMS while dead: {np.mean(nb_dead):.2f} G "
                  "(sensor electrically quiet, not rattling loose)")
    else:
        print("BOT alive on all captures")

    # ---------------- saturation audit -------------------------------
    print("\n=== saturation audit (raw |peak| vs nominal full scale) ===\n")
    sat_summary = {}
    alive_rows = [r for r in rows if r["bot_alive"]]
    for name in FULL_SCALE_G:
        pool = alive_rows if name in ("CH6", "CH7", "CH8") else rows
        fr = np.array([r["sat"][name]["frac_fs"] for r in pool])
        n95 = int((fr >= 0.95).sum())
        n_over = int((fr > 1.0).sum())
        pin_max = max(r["sat"][name]["n_pinned"] for r in pool)
        sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name],
                             "n_pool": len(pool),
                             "median_frac_fs": float(np.median(fr)),
                             "max_frac_fs": float(fr.max()),
                             "n_ge_95pct_fs": n95, "n_over_fs": n_over,
                             "max_pinned_samples": pin_max}
        print(f"  {name}: FS {FULL_SCALE_G[name]:8.1f} G   median {100 * np.median(fr):5.1f}% FS   "
              f"max {100 * fr.max():5.1f}% FS   >=95% FS on {n95:3d}/{len(pool)}   "
              f">FS on {n_over:3d}/{len(pool)}   worst flat-top {pin_max} samples")

    drops = np.array([r["drop"] for r in real], float)
    top = np.array([r["top_180_g"] for r in real], float)
    ch5v = np.array([r["ch5_180_g"] for r in real], float)
    tch5 = np.array([r["t_ch5"] for r in real], float)
    last = int(drops[-1])
    alive_real = [r for r in real if r["bot_alive"]]
    drops_b = np.array([r["drop"] for r in alive_real], float)
    bot = np.array([r["bot_180_g"] for r in alive_real], float)
    tst = np.array([r["t_star"] for r in alive_real], float)

    # ---------------- burn-in changepoint scan (TOP output) ----------
    print(f"\n=== burn-in changepoint scan (TOP CFC-180, OLS on drops k+1..{last}) ===\n")
    print(f"{'burn-in k':>9s} {'n':>3s} {'slope G/drop':>13s} {'%/drop':>8s} {'p':>7s}")
    scan = {}
    burn_in_k = None
    for k in range(0, 31):
        m = drops > k
        if m.sum() < 5:
            break
        o = ols_full(drops[m], top[m])
        scan[k] = o
        if k <= 20 or k % 5 == 0:
            print(f"{k:9d} {o['n']:3d} {o['slope']:+13.3f} {o['slope_pct']:+8.3f} {o['p']:7.3f}")
        if burn_in_k is None and o["p"] > 0.05:
            burn_in_k = k
    if burn_in_k is None:
        burn_in_k = 10
        print(f"\n-> no k in 0..30 yields an n.s. trend; using SOP burn-in = {burn_in_k} "
              "(trend is campaign-scale, not a seating transient — see OLS section)")
    else:
        print(f"\n-> smallest k with n.s. seating trend: burn-in = {burn_in_k} drops")

    def expo(d, a, b, tau):
        return a - b * np.exp(-d / tau)

    p0 = (top[-20:].mean(), top[-20:].mean() - top[0], 5.0)
    try:
        popt, _ = optimize.curve_fit(expo, drops, top, p0=p0, maxfev=20000)
        a_fit, b_fit, tau = (float(v) for v in popt)
        print(f"exponential-approach fit: plateau {a_fit:.1f} G, amplitude {b_fit:.1f} G, "
              f"tau = {tau:.1f} drops")
    except RuntimeError:
        a_fit = b_fit = tau = float("nan")
        print("exponential-approach fit did not converge (no seating transient?)")

    # ---------------- stabilized-phase OLS ---------------------------
    stable = drops > burn_in_k
    xs = drops[stable]
    print(f"\n=== stabilized-phase OLS (drops {burn_in_k + 1}..{last}, "
          f"n = {int(stable.sum())}) ===\n")
    results = {}
    for name, x_, y in [("TOP output", xs, top[stable]),
                        ("CH5 plate", xs, ch5v[stable]),
                        ("T TOP/CH5", xs, tch5[stable])]:
        o = ols_full(x_, y)
        results[name] = o
        print(f"  {name:13s}: mean {o['mean']:8.3f}  CV {o['cv']:6.2f}%   "
              f"slope {o['slope']:+9.4f}/drop ({o['slope_pct']:+.3f}%/drop)   "
              f"95% CI [{o['ci_lo']:+.4f}, {o['ci_hi']:+.4f}]   "
              f"p = {o['p']:.2e}  R² = {o['r2']:.3f}  DW = {o['dw']:.2f}  "
              f"Shapiro p = {o['shapiro_p']:.2f}")
    m_b = drops_b > burn_in_k
    for name, y in [("BOT input", bot), ("T* TOP/BOT", tst)]:
        o = ols_full(drops_b[m_b], y[m_b])
        results[name] = o
        print(f"  {name:13s}: mean {o['mean']:8.3f}  CV {o['cv']:6.2f}%   "
              f"slope {o['slope']:+9.4f}/drop ({o['slope_pct']:+.3f}%/drop)   "
              f"p = {o['p']:.2e}  (BOT-alive drops only, n = {o['n']}; "
              "CH8 over FS — qualitative)")

    print("\n  start-drop sensitivity (TOP output %/drop):")
    sens = {}
    for k in range(0, 101, 20):
        m = drops > k
        if m.sum() < 10:
            break
        o = ols_full(drops[m], top[m])
        sens[k] = o
        print(f"    start {k + 1:3d}: {o['slope_pct']:+.3f}%/drop  (p = {o['p']:.2e})")

    mid = xs[len(xs) // 2]
    o_h1 = ols_full(xs[xs <= mid], top[stable][xs <= mid])
    o_h2 = ols_full(xs[xs > mid], top[stable][xs > mid])
    print(f"\n  split-half check (TOP): drops {int(xs[0])}-{int(mid)}: "
          f"{o_h1['slope_pct']:+.3f}%/drop (p = {o_h1['p']:.2e}); "
          f"drops {int(mid) + 1}-{last}: {o_h2['slope_pct']:+.3f}%/drop "
          f"(p = {o_h2['p']:.2e})")

    # ---------------- per-axis migration (seat health) ---------------
    print("\n=== per-axis raw |peak| migration ===\n")
    axis_ols = {}
    for name, key in [("CH2", "ch2_pk_g"), ("CH3", "ch3_pk_g"), ("CH4", "ch4_pk_g")]:
        y = np.array([r[key] for r in real], float)
        o = ols_full(drops, y)
        axis_ols[name] = o
        print(f"  {name}: {y[:5].mean():6.0f} G (first 5) -> {y[-5:].mean():6.0f} G (last 5)   "
              f"slope {o['slope']:+7.1f} G/drop ({o['slope_pct']:+.2f}%/drop)  p = {o['p']:.1e}")
    for name, key in [("CH6", "ch6_pk_g"), ("CH7", "ch7_pk_g"), ("CH8", "ch8_pk_g")]:
        y = np.array([r[key] for r in alive_real], float)
        o = ols_full(drops_b, y)
        axis_ols[name] = o
        print(f"  {name}: {y[:5].mean():6.0f} G (first 5) -> {y[-5:].mean():6.0f} G (last 5)   "
              f"slope {o['slope']:+7.1f} G/drop ({o['slope_pct']:+.2f}%/drop)  p = {o['p']:.1e}  "
              "(BOT-alive only)")

    # ---------------- specimen damage indicators ---------------------
    print("\n=== specimen damage indicators (mount-robust; fresh print 7xadt6) ===\n")
    dmg = {}
    for key, label in [("top_width_ms", "output pulse width (ms)"),
                       ("dom_freq_hz", "ringdown dominant freq (Hz)"),
                       ("centroid_hz", "ringdown spectral centroid (Hz)"),
                       ("ch5_dv_ms", "plate input Δv (m/s)")]:
        y = np.array([r[key] for r in real], float)
        o = ols_full(drops, y)
        dmg[key] = o
        print(f"  {label:34s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%  "
              f"slope {o['slope_pct']:+.3f}%/drop  p = {o['p']:.2e}")
    ntop = np.array([r["noise_top_g"] for r in real], float)
    print(f"  pre-impact noise RMS TOP (CH2/3/4): first 5 "
          f"{ntop[:5].mean(axis=0).round(2).tolist()} G -> last 5 "
          f"{ntop[-5:].mean(axis=0).round(2).tolist()} G")

    print(f"\n=== context vs RW5F61 campaigns (different specimen!) ===\n")
    for ref in (RUN13, RUN5):
        print(f"  {ref['label']}: TOP {ref['top']:.1f} G, CH5 {ref['ch5']:.1f} G, "
              f"T {ref['t_ch5']:.3f} (CV {ref['t_ch5_cv']:.2f}%)")
    print(f"  7xadt6 @ 10 in (this run): TOP {results['TOP output']['mean']:.1f} G, "
          f"CH5 {results['CH5 plate']['mean']:.1f} G, "
          f"T {results['T TOP/CH5']['mean']:.3f} (CV {results['T TOP/CH5']['cv']:.2f}%)")

    # ---------------- figures ---------------------------------------
    s_all = np.array([r["signal"] for r in rows], float)

    # Fig 1: full-series raw peaks + trigger health + cadence
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(12, 10.5), sharex=True,
                                     gridspec_kw={"height_ratios": [3, 1.4, 1]})
    a1.plot(s_all, [r["top_raw_g"] for r in rows], "s-", ms=3, color="tab:red",
            label="TOP |tri-axis| raw peak (CH2-4, key-seat)")
    a1.plot(s_all, [r["ch5_raw_g"] for r in rows], "o-", ms=3, color="tab:blue",
            label="CH5 raw |peak| (base plate, taped — trigger)")
    a1.plot(s_all, [max(r["bot_raw_g"], 0.5) for r in rows], "^-", ms=3, color="tab:green",
            label="BOT |tri-axis| raw peak (CH6-8, low-range)")
    a1.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1.2, label="1000 G trigger level")
    a1.set(ylabel="raw |peak| (G)", yscale="log",
           title="200-drop campaign (7xadt6, 10 in, CH5 trigger @ 1000 G)")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    a2.plot([r["signal"] for r in real], t_cross, "x-", ms=4, color="tab:blue",
            label="CH5 first crossing of 1000 G")
    a2.plot([r["signal"] for r in real], t_imps, "s", ms=3, color="tab:red",
            label="impact (TOP resultant argmax)")
    a2.axhline(4.0, color="k", ls=":", lw=1.2, label="nominal pre-trigger 4.000 ms")
    a2.set(ylabel="time into record (ms)", title="trigger timing")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    a3.plot(s_all[1:], gaps, "k.-", ms=3)
    a3.set(xlabel="capture (Signal #)", ylabel="gap to previous (s)",
           title="release cadence")
    a3.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: BOT dropout + CH8 headroom
    fig, (c1, c2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    c1.semilogy(s_all, [max(r["bot_raw_g"], 0.1) for r in rows], "o-", ms=3,
                color="tab:green")
    c1.axhline(BOT_ALIVE_FLOOR_G, color="k", ls=":", lw=1.2,
               label=f"alive/dead threshold ({BOT_ALIVE_FLOOR_G:.0f} G)")
    if dead_sigs:
        c1.axvspan(dead_sigs[0], dead_sigs[-1], color="tab:red", alpha=0.12,
                   label=f"BOT at noise floor (Signals {dead_sigs[0]}-{dead_sigs[-1]})")
    c1.set(ylabel="BOT raw resultant peak (G)",
           title="bottom tri-axis dropout — electrically quiet, then recovers")
    c1.legend(fontsize=8)
    c1.grid(alpha=0.3)
    for name, col in [("CH6", "tab:green"), ("CH7", "tab:orange"), ("CH8", "tab:red")]:
        fr = [100 * r["sat"][name]["frac_fs"] if r["bot_alive"] else np.nan for r in rows]
        c2.plot(s_all, fr, "o-", ms=3, color=col,
                label=f"{name} raw |peak| (%FS, FS = {FULL_SCALE_G[name]:.0f} G)")
    c2.axhline(100, color="k", ls="-", lw=1.2, label="full scale")
    c2.axhline(95, color="k", ls=":", lw=1)
    c2.set(xlabel="capture (Signal #)", ylabel="raw |peak| (% of full scale)",
           title="low-range BOT headroom at 10 in (alive captures)")
    c2.legend(fontsize=8)
    c2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_bot_dropout_headroom.png", dpi=130)
    plt.close(fig)

    # Fig 3: per-drop CFC-180 peaks + transmissibility
    fig, (b1, b2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    b1.plot(drops, top, "s-", ms=3, color="tab:red", label="TOP CFC-180 (CH2-4 resultant)")
    b1.plot(drops, ch5v, "o-", ms=3, color="tab:blue", label="CH5 CFC-180 (base plate)")
    b1.plot(drops_b, bot, "^", ms=3, color="tab:green",
            label="BOT CFC-180 (CH6-8; alive drops, CH8 over FS — qualitative)")
    b1.set(ylabel="CFC-180 peak |g| (G)", title="per-drop CFC-180 peaks")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)
    b2.plot(drops, tch5, "o-", ms=3, color="tab:blue", label="T = TOP/CH5 (plate input)")
    b2.plot(drops_b, tst, "d", ms=3, color="tab:purple",
            label="T* = TOP/BOT (qualitative)")
    b2.set(xlabel="drop #", ylabel="transmissibility")
    b2.legend(fontsize=8)
    b2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_cfc180_series.png", dpi=130)
    plt.close(fig)

    # Fig 4: stabilized-phase OLS (TOP output + CH5 + T)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5))
    for ax_, y, name, col in [(axes[0], top[stable], "TOP output CFC-180 (G)", "tab:red"),
                              (axes[1], ch5v[stable], "CH5 plate CFC-180 (G)", "tab:blue"),
                              (axes[2], tch5[stable], "T = TOP/CH5 (CFC-180)", "tab:purple")]:
        o = ols_full(xs, y)
        ax_.plot(xs, y, "o", ms=3, color=col)
        fit = o["mean"] - o["slope"] * xs.mean() + o["slope"] * xs
        ax_.plot(xs, fit, "-", color="k", lw=1.5,
                 label=f"OLS {o['slope']:+.4f}/drop ({o['slope_pct']:+.3f}%/drop)\n"
                       f"p = {o['p']:.1e}, R² = {o['r2']:.2f}")
        lo_fit = o["mean"] - o["ci_lo"] * xs.mean() + o["ci_lo"] * xs
        hi_fit = o["mean"] - o["ci_hi"] * xs.mean() + o["ci_hi"] * xs
        ax_.fill_between(xs, np.minimum(lo_fit, hi_fit), np.maximum(lo_fit, hi_fit),
                         color=col, alpha=0.15, label="95% CI on slope")
        ax_.set(xlabel="drop #", ylabel=name)
        ax_.legend(fontsize=8)
        ax_.grid(alpha=0.3)
    fig.suptitle(f"stabilized-phase drift (drops {burn_in_k + 1}-{last})")
    fig.tight_layout()
    fig.savefig(FIG / "04_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 5: damage indicators
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    for ax_, key, label in [(axes[0], "top_width_ms", "output half-amplitude\npulse width (ms)"),
                            (axes[1], "dom_freq_hz",
                             "ringdown dominant freq (Hz)\n100–2000 Hz, rotation-invariant"),
                            (axes[2], "centroid_hz", "ringdown spectral centroid (Hz)")]:
        y = np.array([r[key] for r in real], float)
        o = dmg[key]
        ax_.plot(drops, y, "o-", ms=2.5, color="tab:red")
        ax_.set(xlabel="drop #",
                title=f"{label}\nslope {o['slope_pct']:+.3f}%/drop, p = {o['p']:.1e}")
        ax_.grid(alpha=0.3)
    fig.suptitle("mount-robust specimen damage indicators — 7xadt6, 200 drops at 10 in")
    fig.tight_layout()
    fig.savefig(FIG / "05_damage_indicators.png", dpi=130)
    plt.close(fig)

    # Fig 6: per-axis migration (both seats)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharex=True)
    for key, name, col in [("ch2_pk_g", "CH2", "tab:green"),
                           ("ch3_pk_g", "CH3", "tab:orange"),
                           ("ch4_pk_g", "CH4", "tab:red")]:
        axes[0].plot(drops, [r[key] for r in real], "o-", ms=2.5, color=col,
                     label=f"{name} raw |peak|")
    axes[0].set(xlabel="drop #", ylabel="raw |peak| per axis (G)",
                title="top seat (CH2-4, taped housing entrance)")
    for key, name, col in [("ch6_pk_g", "CH6", "tab:green"),
                           ("ch7_pk_g", "CH7", "tab:orange"),
                           ("ch8_pk_g", "CH8", "tab:red")]:
        axes[1].plot(drops_b, [r[key] for r in alive_real], "o-", ms=2.5, color=col,
                     label=f"{name} raw |peak|")
    axes[1].set(xlabel="drop #", title="bottom seat (CH6-8, low-range; alive drops)")
    for ax_ in axes:
        ax_.legend(fontsize=8)
        ax_.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "06_axis_migration.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary -----------------------
    summary = {
        "specimen": "7xadt6",
        "n_captures": len(rows),
        "signals": [int(SIGNALS.start), int(SIGNALS.stop - 1)],
        "spurious_captures": spurious,
        "n_real_drops_captured": len(real),
        "drop_height_in": 10.0,
        "trigger": {
            "channel": "CH5",
            "level_g": TRIGGER_LEVEL_G,
            "cross_ms": {"mean": float(t_cross.mean()), "std": float(t_cross.std()),
                         "min": float(t_cross.min()), "max": float(t_cross.max())},
            "impact_ms": {"mean": float(t_imps.mean()), "std": float(t_imps.std())},
            "ch5_raw_peak_g": {"mean": float(ch5_pks.mean()), "min": float(ch5_pks.min()),
                               "max": float(ch5_pks.max())},
            "margin_x": {"min": float((ch5_pks / TRIGGER_LEVEL_G).min()),
                         "max": float((ch5_pks / TRIGGER_LEVEL_G).max())},
            "pre_cross_max_g": float(pre_max.max()),
            "ch4_raw_peak_g": {"mean": float(ch4_pks.mean()), "min": float(ch4_pks.min()),
                               "max": float(ch4_pks.max())},
        },
        "cadence_s": {"median": float(np.median(gaps)), "min": float(gaps.min()),
                      "max": float(gaps.max())},
        "bot_dropout": {"dead_signals": dead_sigs,
                        "n_dead": len(dead_sigs),
                        "n_alive": int(alive.sum())},
        "saturation": sat_summary,
        "burn_in_drops": burn_in_k,
        "expo_fit": {"plateau_g": a_fit, "amplitude_g": b_fit, "tau_drops": tau},
        "stabilized_window": [int(burn_in_k) + 1, last],
        "stabilized_ols": results,
        "split_half": {"first": o_h1, "second": o_h2},
        "burn_in_scan": {str(k): v for k, v in scan.items()},
        "start_drop_sensitivity": {str(k): v for k, v in sens.items()},
        "axis_migration": axis_ols,
        "damage_indicators": dmg,
        "per_capture": rows,
    }
    with open(FIG / "200drops_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
