#!/usr/bin/env python3
"""500-drop failure test (bubbled-TPU print, 10 in, CH5 trigger @ 300 G):
what tripped the TP4 overload condition at drop 256?

@ctrhjk ran a failure test on the newest print (new TPU filament; three
diagonal tendons with serious bubbles from >10 % humidity — see PR #35) with
the drop count set to 500. At the 256th drop the Lansmont Test Partner 4
showed an overload condition and all signals were disconnected. This script
analyzes the 256 recorded captures (``500drops_Signal{1..256}.csv``) and
answers:

  1. **Capture health** — are all 256 captures real impacts with all seven
     channels alive, including the final one before the overload?
  2. **Overload diagnosis** — which channel(s) exceeded full scale, when,
     and how often? (TP4 flags an overload when a channel's input exceeds
     its calibrated range.)
  3. **Failure-test trends** — how did the specimen and sensor chain evolve
     over 256 drops (raw peaks, CFC-180 levels, T = TOP/CH5, BOT axis mix,
     ringdown dominant mode, pulse width)?
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "500drops" / "raw"
FIG = REPO / "data" / "drop-tests" / "500drops" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate — the trigger channel (300 G)
BOT_COLS = (4, 5, 6)  # CH6, CH7, CH8 — low-range tri-axis, bottom-vertex housing

CH_NAMES = ("CH2", "CH3", "CH4", "CH5", "CH6", "CH7", "CH8")
FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9,
                "CH6": 1002.0, "CH7": 991.1, "CH8": 989.1}

TRIGGER_LEVEL_G = 300.0
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SIGNALS = range(1, 257)  # 500drops_Signal1..256 — run stopped at the overload
REAL_IMPACT_FLOOR_G = 300.0
BOT_ALIVE_FLOOR_G = 50.0


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",",
                      usecols=(0, 1, 2, 3, 4, 5, 6, 7))
    return d[:, 0], d[:, 1:8]


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

    over = np.abs(ch5) >= TRIGGER_LEVEL_G
    i_x = int(np.argmax(over)) if over.any() else -1
    t_x_ms = float(t[i_x] * 1e3) if i_x >= 0 else float("nan")
    pre = np.abs(ch5[t < 0.0035])
    pre_max_g = float(pre.max()) if len(pre) else 0.0

    sat = {}
    for j, name in enumerate(CH_NAMES):
        x = np.abs(ch[:, j] - np.median(ch[:nb, j]))
        pk = float(x.max())
        sat[name] = {
            "peak_g": pk,
            "frac_fs": pk / FULL_SCALE_G[name],
            "n_pinned": int((x >= 0.995 * pk).sum()) if pk >= 0.95 * FULL_SCALE_G[name] else 0,
        }

    row = {
        "signal": None,
        "event_time": event_time(path).isoformat(),
        "real_impact": bool(is_real),
        "bot_alive": bot_alive,
        "t_imp_ms": float(t[i_imp] * 1e3),
        "trig_cross_ms": t_x_ms,
        "pre_trigger_max_g": pre_max_g,
        "top_raw_g": top_raw_pk,
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "bot_raw_g": float(np.max(bot_res_raw)),
        "sat": sat,
        "noise_bot_g": [float(np.std(bot[:nb, j])) for j in range(3)],
        "noise_top_g": [float(np.std(top[:nb, j])) for j in range(3)],
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    m_top = windowed_peak(t, resultant(top180), i_imp, dt)
    m_ch5 = windowed_peak(t, cfc_filter(ch5, fs, 180), i_imp, dt)

    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "ch6_pk_g": float(np.max(np.abs(bot[lo:hi, 0]))),
        "ch7_pk_g": float(np.max(np.abs(bot[lo:hi, 1]))),
        "ch8_pk_g": float(np.max(np.abs(bot[lo:hi, 2]))),
        "bot_res_pk_g": float(np.max(bot_res_raw[lo:hi])),
        "dom_freq_hz": ringdown_dom_freq(t, top, i_imp, fs),
    })
    return row


def ols_full(x, y) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    res = stats.linregress(x, y)
    mean = float(np.mean(y))
    return {"n": len(x), "slope": float(res.slope),
            "slope_pct": float(100.0 * res.slope / mean),
            "p": float(res.pvalue), "r2": float(res.rvalue**2),
            "mean": mean, "cv": cv(y)}


def main() -> int:
    rows: list[dict] = []
    for sig in SIGNALS:
        row = analyze_capture(RAW / f"500drops_Signal{sig}.csv")
        row["signal"] = sig
        rows.append(row)

    real = [r for r in rows if r["real_impact"]]
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])
    t_cross = np.array([r["trig_cross_ms"] for r in real])
    drops = np.array([r["drop"] for r in real], float)
    sigs = np.array([r["signal"] for r in rows], float)

    print("=== 500-drop failure test (bubbled-TPU print, 10 in): capture health ===\n")
    print(f"captures: {len(rows)} = {len(real)} real + {len(spurious)} spurious {spurious}")
    print(f"cadence: median {np.median(gaps):.0f} s; max gap {gaps.max():.0f} s; span "
          f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min "
          f"({times[0].time()} - {times[-1].time()})")
    print(f"CH5 first crossing of {TRIGGER_LEVEL_G:.0f} G: "
          f"{t_cross.mean():.3f} +- {t_cross.std():.3f} ms")
    pre_worst = max(r["pre_trigger_max_g"] for r in rows)
    print(f"worst pre-impact CH5 activity: {pre_worst:.1f} G "
          f"({TRIGGER_LEVEL_G / pre_worst:.0f}x below the 300 G level)")
    dead = [r["signal"] for r in rows if not r["bot_alive"]]
    print(f"BOT alive on {len(rows) - len(dead)}/{len(rows)} captures"
          + (f"; DEAD on Signals {dead}" if dead else " — no electrical dropout"))

    # ---------------- overload diagnosis ------------------------------
    print("\n=== Overload diagnosis: raw |peak| vs full scale, per channel ===\n")
    sat_summary = {}
    for name in CH_NAMES:
        fr = np.array([r["sat"][name]["frac_fs"] for r in rows])
        n95 = int((fr >= 0.95).sum())
        n_over = int((fr > 1.0).sum())
        first_over = int(sigs[np.argmax(fr > 1.0)]) if n_over else None
        # first signal from which >FS is sustained (5 consecutive captures)
        sustained = None
        ov = fr > 1.0
        for i in range(len(ov) - 4):
            if ov[i : i + 5].all():
                sustained = int(sigs[i])
                break
        pin_max = max(r["sat"][name]["n_pinned"] for r in rows)
        sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name],
                             "median_frac_fs": float(np.median(fr)),
                             "max_frac_fs": float(fr.max()),
                             "n_ge_95pct_fs": n95, "n_over_fs": n_over,
                             "first_over_fs_signal": first_over,
                             "sustained_over_fs_from_signal": sustained,
                             "max_pinned_samples": pin_max}
        print(f"  {name}: FS {FULL_SCALE_G[name]:8.1f} G   median {100 * np.median(fr):5.1f}% FS   "
              f"max {100 * fr.max():5.1f}% FS   >=95% FS on {n95:3d}/256   "
              f">FS on {n_over:3d}/256   first >FS: "
              f"{'Signal ' + str(first_over) if first_over else '-':>10s}   "
              f"sustained from: {'Signal ' + str(sustained) if sustained else '-'}")

    ch6 = np.array([r["ch6_pk_g"] for r in real])
    ch7 = np.array([r["ch7_pk_g"] for r in real])
    ch8 = np.array([r["ch8_pk_g"] for r in real])
    bot_res = np.array([r["bot_res_pk_g"] for r in real])
    print("\nCH6 growth into overload (impact-window |peak|, drops 1-10 vs 247-256):")
    print(f"  CH6: {ch6[:10].mean():6.0f} G -> {ch6[-10:].mean():6.0f} G "
          f"({100 * (ch6[-10:].mean() / ch6[:10].mean() - 1):+.0f}%)   "
          f"[FS {FULL_SCALE_G['CH6']:.0f} G]")
    print(f"  CH7: {ch7[:10].mean():6.0f} G -> {ch7[-10:].mean():6.0f} G "
          f"({100 * (ch7[-10:].mean() / ch7[:10].mean() - 1):+.0f}%)")
    print(f"  CH8: {ch8[:10].mean():6.0f} G -> {ch8[-10:].mean():6.0f} G "
          f"({100 * (ch8[-10:].mean() / ch8[:10].mean() - 1):+.0f}%)")
    print(f"  BOT resultant: {bot_res[:10].mean():6.0f} G -> {bot_res[-10:].mean():6.0f} G "
          f"({100 * (bot_res[-10:].mean() / bot_res[:10].mean() - 1):+.0f}%)")

    # ---------------- failure-test trends -----------------------------
    top = np.array([r["top_180_g"] for r in real])
    ch5v = np.array([r["ch5_180_g"] for r in real])
    tch5 = np.array([r["t_ch5"] for r in real])
    ch5_raw = np.array([r["ch5_raw_g"] for r in real])
    top_raw = np.array([r["top_raw_g"] for r in real])
    width = np.array([r["top_width_ms"] for r in real])
    dv = np.array([r["ch5_dv_ms"] for r in real])
    dom = np.array([r["dom_freq_hz"] for r in real])

    print("\n=== Failure-test trends over the 256 drops (OLS vs drop #) ===\n")
    trends = {}
    for name, y in [("CH5 raw", ch5_raw), ("TOP raw resultant", top_raw),
                    ("CH5 CFC-180", ch5v), ("TOP CFC-180", top),
                    ("T = TOP/CH5", tch5), ("pulse width (ms)", width),
                    ("input dv (m/s)", dv), ("CH6 impact pk", ch6),
                    ("CH7 impact pk", ch7), ("BOT resultant pk", bot_res)]:
        o = ols_full(drops, y)
        trends[name] = o
        total = o["slope"] * (len(drops) - 1)
        print(f"  {name:18s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%   "
              f"slope {o['slope_pct']:+.3f}%/drop (p = {o['p']:.2e})   "
              f"net over run {total / o['mean'] * 100:+.0f}%")
    n_low = int((dom < 200).sum())
    print(f"\nringdown dominant mode: median {np.median(dom):.0f} Hz "
          f"(range {dom.min():.0f}-{dom.max():.0f}); < 200 Hz on {n_low}/{len(real)} drops")

    # ---------------- figures ----------------------------------------
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 8.5), sharex=True)
    for name, col in [("CH6", "tab:green"), ("CH7", "tab:orange"), ("CH8", "tab:red"),
                      ("CH5", "tab:blue")]:
        fr = [100 * r["sat"][name]["frac_fs"] for r in rows]
        a1.plot(sigs, fr, "o-", ms=2, lw=0.8, color=col,
                label=f"{name} raw |peak| (FS = {FULL_SCALE_G[name]:.0f} G)")
    a1.axhline(100, color="k", ls="-", lw=1.2, label="full scale (TP4 overload)")
    a1.axhline(95, color="k", ls=":", lw=1)
    f_over = sat_summary["CH6"]["first_over_fs_signal"]
    f_sus = sat_summary["CH6"]["sustained_over_fs_from_signal"]
    a1.axvline(f_over, color="tab:green", ls="--", lw=1,
               label=f"CH6 first >FS (Signal {f_over})")
    a1.axvline(f_sus, color="tab:green", ls="-", lw=1,
               label=f"CH6 >FS sustained (Signal {f_sus})")
    a1.set(ylabel="raw |peak| (% of full scale)",
           title="500-drop failure test — overload diagnosis: CH6 walks over its 1002 G full scale")
    a1.legend(fontsize=8, ncol=2)
    a1.grid(alpha=0.3)
    a2.plot(sigs, [r["ch5_raw_g"] for r in rows], "o-", ms=2, lw=0.8,
            color="tab:blue", label="CH5 raw |peak| (plate, trigger)")
    a2.plot(sigs, [r["top_raw_g"] for r in rows], "s-", ms=2, lw=0.8,
            color="tab:red", label="TOP raw resultant peak (CH2-4)")
    a2.plot(sigs, [r["bot_raw_g"] for r in rows], "^-", ms=2, lw=0.8,
            color="tab:green", label="BOT raw resultant peak (CH6-8)")
    a2.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1.2, label="300 G trigger level")
    a2.set(xlabel="capture (Signal # = drop #)", ylabel="raw |peak| (G)", yscale="log")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_overload_diagnosis.png", dpi=130)
    plt.close(fig)

    fig, (b1, b2, b3) = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
    b1.plot(drops, ch5v, "o-", ms=2, lw=0.8, color="tab:blue", label="CH5 CFC-180 peak")
    b1.plot(drops, top, "s-", ms=2, lw=0.8, color="tab:red", label="TOP CFC-180 peak")
    b1.set(ylabel="CFC-180 peak (G)",
           title="Failure-test trends: input/output levels, transmissibility, ringdown mode")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)
    b2.plot(drops, tch5, "o-", ms=2, lw=0.8, color="tab:purple", label="T = TOP/CH5")
    b2.set(ylabel="transmissibility")
    b2.legend(fontsize=8)
    b2.grid(alpha=0.3)
    b3.plot(drops, dom, "o", ms=3, color="tab:red", label="dominant ringdown mode (TOP)")
    b3.set(xlabel="drop #", ylabel="frequency (Hz)")
    b3.legend(fontsize=8)
    b3.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_failure_trends.png", dpi=130)
    plt.close(fig)

    # early vs late CH6 waveform: the walk over full scale
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, sig in zip(axes, (1, 250)):
        t, ch = load(RAW / f"500drops_Signal{sig}.csv")
        nb = max(1, int(BASELINE_S / float(np.median(np.diff(t)))))
        x = ch[:, 4] - np.median(ch[:nb, 4])
        i_imp = int(np.argmax(np.abs(x)))
        m = (t >= t[i_imp] - 0.003) & (t <= t[i_imp] + 0.006)
        ax.plot(t[m] * 1e3, x[m], lw=0.7, color="tab:green")
        ax.axhline(FULL_SCALE_G["CH6"], color="k", ls="--", lw=1, label="CH6 full scale (+/-1002 G)")
        ax.axhline(-FULL_SCALE_G["CH6"], color="k", ls="--", lw=1)
        ax.set(xlabel="time (ms)", title=f"Signal {sig}: CH6 raw |peak| "
               f"{np.max(np.abs(x)):.0f} G ({100 * np.max(np.abs(x)) / FULL_SCALE_G['CH6']:.0f}% FS)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("CH6 acceleration (G)")
    axes[0].legend(fontsize=8)
    fig.suptitle("CH6 (bottom-vertex low-range axis): within range early, over full scale late")
    fig.tight_layout()
    fig.savefig(FIG / "03_ch6_waveforms.png", dpi=130)
    plt.close(fig)

    # ---------------- metrics JSON (compact per-capture arrays) -------
    def col(key, pool=rows, default=float("nan")):
        return [r.get(key, default) for r in pool]

    summary = {
        "specimen": "newest print, new TPU filament, three bubbled diagonal tendons (PR #35, 2026-07-15)",
        "setup": {"height_in": 10, "trigger": "CH5 @ 300 G", "planned_drops": 500,
                  "recorded_drops": len(rows), "stop_reason": "TP4 overload condition at drop 256"},
        "n_captures": len(rows),
        "spurious_captures": spurious,
        "cadence_s_median": float(np.median(gaps)),
        "cadence_s_max": float(gaps.max()),
        "trigger_cross_ms": {"mean": float(t_cross.mean()), "std": float(t_cross.std())},
        "worst_pre_trigger_g": pre_worst,
        "bot_dead_signals": dead,
        "saturation": sat_summary,
        "trends_ols": trends,
        "ringdown": {"median_hz": float(np.median(dom)),
                     "min_hz": float(dom.min()), "max_hz": float(dom.max()),
                     "n_below_200hz": n_low},
        "per_capture": {
            "signal": col("signal"),
            "event_time": col("event_time"),
            "ch5_raw_g": col("ch5_raw_g"),
            "top_raw_g": col("top_raw_g"),
            "bot_raw_g": col("bot_raw_g"),
            "ch5_180_g": col("ch5_180_g"),
            "top_180_g": col("top_180_g"),
            "t_ch5": col("t_ch5"),
            "top_width_ms": col("top_width_ms"),
            "ch5_dv_ms": col("ch5_dv_ms"),
            "dom_freq_hz": col("dom_freq_hz"),
            "ch6_pk_g": col("ch6_pk_g"),
            "ch7_pk_g": col("ch7_pk_g"),
            "ch8_pk_g": col("ch8_pk_g"),
            "frac_fs": {n: [r["sat"][n]["frac_fs"] for r in rows] for n in CH_NAMES},
        },
    }
    with open(FIG / "500drops_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
