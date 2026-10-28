#!/usr/bin/env python3
"""Diagnose the three 200-drop-campaign problems from the 30 check drops.

After the 200-drop campaign on specimen ``7xadt6`` (10 in, CH5 trigger —
see ``drop_test_200drops_analysis.py``), @ctrhjk ran 30 additional drops
(``check_Signal{203..232}.csv``, same rig/settings) specifically to diagnose
the three problems flagged in that report, plus its end-of-campaign watch
item:

  1. **BOT electrical dropout** — CH6-8 went silent for Signals 61-173 and
     self-recovered (intermittent cable/connector suspected). Is BOT alive
     and electrically healthy on all 30 check drops?
  2. **BOT over full scale at 10 in** — CH8 exceeded its ~989 G full scale on
     50/87 alive captures (and CH7 on 31/87). Still the case?
  3. **CH5 excursion** — CH5 sagged to a 210-230 G shelf across drops
     ~140-175 with T spiking to 1.09-1.16 (tape-coupling suspect). Is CH5
     back at its healthy ~242 G level with T at ~1.02?

  W. **~122 Hz mode watch item** — the rotation-invariant ringdown dominant
     mode flipped from ~550 Hz to ~122 Hz for 8 of the last 9 campaign drops
     (192-193, 195-200). If ~122 Hz dominates the check drops from drop 1,
     that is a persistent specimen change; if the mode is back at ~550 Hz it
     was transient mode-trading.
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
RAW = REPO / "data" / "drop-tests" / "200drops-check" / "raw"
FIG = REPO / "data" / "drop-tests" / "200drops-check" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate (taped) — the trigger channel
BOT_COLS = (4, 5, 6)  # CH6, CH7, CH8 — low-range tri-axis, bottom-vertex housing

FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9,
                "CH6": 1002.0, "CH7": 991.1, "CH8": 989.1}

TRIGGER_LEVEL_G = 1000.0
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SIGNALS = range(203, 233)  # check_Signal203..232 = check drops 1..30
REAL_IMPACT_FLOOR_G = 300.0
BOT_ALIVE_FLOOR_G = 50.0

# 200-drop campaign reference values (same specimen/rig, stabilized phase)
REF = {
    "top_180_g": 244.6, "ch5_180_g": 238.7, "t_ch5": 1.025,
    "ch5_healthy_g": 242.2,          # CH5 CFC-180 mean outside the excursion
    "ch5_excursion_g": 224.7,        # CH5 CFC-180 mean inside drops ~140-176
    "dom_freq_main_hz": 549.0,       # dominant ringdown mode most of campaign
    "dom_freq_watch_hz": 122.0,      # end-of-campaign low mode (192-200)
    "top_width_ms": 1.48,
}


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


def ringdown_spectrum(t: np.ndarray, tri: np.ndarray, i_imp: int, fs: float) -> dict:
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
    # power ratio of the ~122 Hz watch mode vs the ~550 Hz main mode
    def band_pow(fc, half=40.0):
        m = (fb >= fc - half) & (fb <= fc + half)
        return float(pb[m].sum()) if m.any() else 0.0
    p_lo = band_pow(REF["dom_freq_watch_hz"])
    p_hi = band_pow(REF["dom_freq_main_hz"], half=100.0)
    return {"dom_freq_hz": float(fb[np.argmax(pb)]),
            "centroid_hz": float(np.sum(fb * pb) / np.sum(pb)),
            "p122_over_p550": p_lo / p_hi if p_hi else float("inf")}


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
    ring = ringdown_spectrum(t, top, i_imp, fs)

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "ch2_pk_g": float(np.max(np.abs(top[lo:hi, 0]))),
        "ch3_pk_g": float(np.max(np.abs(top[lo:hi, 1]))),
        "ch4_pk_g": float(np.max(np.abs(top[lo:hi, 2]))),
        "ch6_pk_g": float(np.max(np.abs(bot[lo:hi, 0]))),
        "ch7_pk_g": float(np.max(np.abs(bot[lo:hi, 1]))),
        "ch8_pk_g": float(np.max(np.abs(bot[lo:hi, 2]))),
        "dom_freq_hz": ring["dom_freq_hz"],
        "centroid_hz": ring["centroid_hz"],
        "p122_over_p550": ring["p122_over_p550"],
    })
    if bot_alive:
        bot180 = np.stack([cfc_filter(bot[:, j], fs, 180) for j in range(3)], axis=1)
        m_bot = windowed_peak(t, resultant(bot180), i_imp, dt)
        row.update({
            "bot_180_g": m_bot["peak_abs_g"],
            "t_star": m_top["peak_abs_g"] / m_bot["peak_abs_g"],
        })
    return row


def ols_full(x, y) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    res = stats.linregress(x, y)
    resid = y - (res.intercept + res.slope * x)
    dw = float(np.sum(np.diff(resid) ** 2) / np.sum(resid**2)) if np.any(resid) else float("nan")
    mean = float(np.mean(y))
    return {"n": n, "slope": float(res.slope),
            "slope_pct": float(100.0 * res.slope / mean),
            "p": float(res.pvalue), "r2": float(res.rvalue**2), "dw": dw,
            "mean": mean, "cv": cv(y)}


def main() -> int:
    rows: list[dict] = []
    for sig in SIGNALS:
        row = analyze_capture(RAW / f"check_Signal{sig}.csv")
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

    print("=== 30-drop check run (7xadt6): capture health ===\n")
    print(f"captures: {len(rows)} = {len(real)} real + {len(spurious)} spurious {spurious}")
    print(f"cadence: median {np.median(gaps):.0f} s; span "
          f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min")
    print(f"CH5 first crossing of 1000 G: {t_cross.mean():.3f} +- {t_cross.std():.3f} ms")

    # ---------------- Problem 1: BOT dropout --------------------------
    dead = [r["signal"] for r in rows if not r["bot_alive"]]
    nb_bot = np.array([np.mean(r["noise_bot_g"]) for r in rows])
    print("\n=== Problem 1: BOT (CH6-8) electrical dropout ===\n")
    print(f"BOT alive on {len(rows) - len(dead)}/{len(rows)} captures"
          + (f"; DEAD on Signals {dead}" if dead else " — no dropout"))
    print(f"BOT pre-impact noise RMS: {nb_bot.mean():.3f} G "
          f"(range {nb_bot.min():.3f}-{nb_bot.max():.3f}) — "
          "dead-block level in the 200-drop run was ~0.01 G")
    bot_raw = np.array([r["bot_raw_g"] for r in real])
    print(f"BOT raw resultant peak: {bot_raw.mean():.0f} +- {bot_raw.std():.0f} G "
          f"(range {bot_raw.min():.0f}-{bot_raw.max():.0f})")

    # ---------------- Problem 2: saturation audit ---------------------
    print("\n=== Problem 2: saturation audit (raw |peak| vs full scale) ===\n")
    sat_summary = {}
    alive_rows = [r for r in rows if r["bot_alive"]]
    for name in FULL_SCALE_G:
        pool = alive_rows if name in ("CH6", "CH7", "CH8") else rows
        fr = np.array([r["sat"][name]["frac_fs"] for r in pool])
        n95 = int((fr >= 0.95).sum())
        n_over = int((fr > 1.0).sum())
        pin_max = max(r["sat"][name]["n_pinned"] for r in pool)
        sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name], "n_pool": len(pool),
                             "median_frac_fs": float(np.median(fr)),
                             "max_frac_fs": float(fr.max()),
                             "n_ge_95pct_fs": n95, "n_over_fs": n_over,
                             "max_pinned_samples": pin_max}
        print(f"  {name}: FS {FULL_SCALE_G[name]:8.1f} G   median {100 * np.median(fr):5.1f}% FS   "
              f"max {100 * fr.max():5.1f}% FS   >=95% FS on {n95:2d}/{len(pool)}   "
              f">FS on {n_over:2d}/{len(pool)}   worst flat-top {pin_max} samples")

    # ---------------- Problem 3: CH5 level / T ------------------------
    top = np.array([r["top_180_g"] for r in real])
    ch5v = np.array([r["ch5_180_g"] for r in real])
    tch5 = np.array([r["t_ch5"] for r in real])
    print("\n=== Problem 3: CH5 level / tape coupling ===\n")
    for name, y, ref in [("TOP output", top, REF["top_180_g"]),
                         ("CH5 plate", ch5v, REF["ch5_180_g"]),
                         ("T = TOP/CH5", tch5, REF["t_ch5"])]:
        o = ols_full(drops, y)
        print(f"  {name:12s}: mean {o['mean']:8.3f}  CV {o['cv']:5.2f}%   "
              f"slope {o['slope_pct']:+.3f}%/drop (p = {o['p']:.3f})   "
              f"[200-drop stabilized ref: {ref}]")
    print(f"  CH5 vs the campaign's healthy level ({REF['ch5_healthy_g']} G) "
          f"and the excursion shelf ({REF['ch5_excursion_g']} G): "
          f"check-run mean = {ch5v.mean():.1f} G")
    print(f"  T range: {tch5.min():.3f}-{tch5.max():.3f} "
          "(campaign excursion spiked to 1.09-1.16)")

    # ---------------- Watch item: ~122 Hz mode ------------------------
    dom = np.array([r["dom_freq_hz"] for r in real])
    ratio = np.array([r["p122_over_p550"] for r in real])
    n122 = int((dom < 200).sum())
    print("\n=== Watch item: ~122 Hz ringdown mode ===\n")
    print(f"dominant mode < 200 Hz on {n122}/{len(real)} drops")
    print("per-drop dominant freq (Hz):",
          " ".join(f"{v:.0f}" for v in dom))
    print(f"~122 Hz / ~550 Hz band-power ratio: median {np.median(ratio):.3f} "
          f"(range {ratio.min():.3f}-{ratio.max():.3f}); "
          "ratio > 1 means the low mode dominates")
    o_r = ols_full(drops, ratio)
    print(f"  ratio trend: {o_r['slope_pct']:+.2f}%/drop (p = {o_r['p']:.3f})")
    width = np.array([r["top_width_ms"] for r in real])
    o_w = ols_full(drops, width)
    print(f"  pulse width: mean {width.mean():.3f} ms, CV {cv(width):.2f}%, "
          f"slope {o_w['slope_pct']:+.3f}%/drop (p = {o_w['p']:.3f}) "
          f"[campaign ref {REF['top_width_ms']} ms]")

    # ---------------- figures ----------------------------------------
    s_all = np.array([r["signal"] for r in rows], float)

    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    a1.plot(s_all, [r["top_raw_g"] for r in rows], "s-", ms=3, color="tab:red",
            label="TOP raw resultant peak (CH2-4)")
    a1.plot(s_all, [r["ch5_raw_g"] for r in rows], "o-", ms=3, color="tab:blue",
            label="CH5 raw |peak| (plate, trigger)")
    a1.plot(s_all, [max(r["bot_raw_g"], 0.5) for r in rows], "^-", ms=3,
            color="tab:green", label="BOT raw resultant peak (CH6-8)")
    a1.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1.2, label="1000 G trigger level")
    a1.axhline(BOT_ALIVE_FLOOR_G, color="tab:green", ls=":", lw=1,
               label="BOT alive/dead threshold")
    a1.set(ylabel="raw |peak| (G)", yscale="log",
           title="30-drop check run (7xadt6, 10 in) — Problem 1: BOT alive on every capture")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    for name, col in [("CH6", "tab:green"), ("CH7", "tab:orange"), ("CH8", "tab:red")]:
        fr = [100 * r["sat"][name]["frac_fs"] if r["bot_alive"] else np.nan for r in rows]
        a2.plot(s_all, fr, "o-", ms=3, color=col,
                label=f"{name} raw |peak| (%FS, FS = {FULL_SCALE_G[name]:.0f} G)")
    a2.axhline(100, color="k", ls="-", lw=1.2, label="full scale")
    a2.axhline(95, color="k", ls=":", lw=1)
    a2.set(ylabel="raw |peak| (% of full scale)",
           title="Problem 2: low-range BOT headroom at 10 in")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    a3.plot([r["signal"] for r in real], ch5v, "o-", ms=3, color="tab:blue",
            label="CH5 CFC-180 peak")
    a3.axhline(REF["ch5_healthy_g"], color="tab:blue", ls="--", lw=1,
               label=f"campaign healthy level ({REF['ch5_healthy_g']} G)")
    a3.axhline(REF["ch5_excursion_g"], color="tab:red", ls=":", lw=1,
               label=f"campaign excursion shelf ({REF['ch5_excursion_g']} G)")
    a3.set(xlabel="capture (Signal #)", ylabel="CFC-180 peak (G)",
           title="Problem 3: CH5 level vs the campaign excursion")
    a3.legend(fontsize=8)
    a3.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_three_problems.png", dpi=130)
    plt.close(fig)

    fig, (b1, b2) = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    b1.plot(drops, tch5, "o-", ms=3, color="tab:purple", label="T = TOP/CH5")
    b1.axhline(REF["t_ch5"], color="k", ls="--", lw=1,
               label=f"200-drop stabilized mean ({REF['t_ch5']})")
    b1.axhspan(1.09, 1.16, color="tab:red", alpha=0.10,
               label="campaign excursion band (drops 170-176)")
    b1.set(ylabel="transmissibility", title="T = TOP/CH5 across the check drops")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)
    b2.semilogy(drops, ratio, "o-", ms=3, color="tab:red",
                label="ringdown band-power ratio  P(~122 Hz) / P(~550 Hz)")
    b2.axhline(1.0, color="k", ls="--", lw=1, label="low mode dominates above this line")
    b2.set(xlabel="check drop #", ylabel="power ratio",
           title="Watch item: ~122 Hz mode vs the ~550 Hz main mode")
    b2.legend(fontsize=8)
    b2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_transmissibility_122hz.png", dpi=130)
    plt.close(fig)

    summary = {
        "specimen": "7xadt6",
        "n_captures": len(rows),
        "signals": [int(SIGNALS.start), int(SIGNALS.stop - 1)],
        "spurious_captures": spurious,
        "cadence_s_median": float(np.median(gaps)),
        "trigger_cross_ms": {"mean": float(t_cross.mean()), "std": float(t_cross.std())},
        "problem1_bot_dropout": {
            "dead_signals": dead,
            "bot_noise_rms_g": {"mean": float(nb_bot.mean()),
                                "min": float(nb_bot.min()), "max": float(nb_bot.max())},
        },
        "problem2_saturation": sat_summary,
        "problem3_ch5": {
            "top_180": ols_full(drops, top),
            "ch5_180": ols_full(drops, ch5v),
            "t_ch5": ols_full(drops, tch5),
            "ref": REF,
        },
        "watch_122hz": {
            "n_dom_below_200hz": n122,
            "dom_freq_hz": dom.tolist(),
            "p122_over_p550": ratio.tolist(),
            "ratio_ols": o_r,
            "pulse_width_ols": o_w,
        },
        "per_capture": rows,
    }
    with open(FIG / "200drops_check_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
