#!/usr/bin/env python3
"""5 in vs 10 in drop-height comparison (500 G CH5 trigger validation).

After the 5-in practice drops on ``7xadt6`` failed to trigger at the 1000 G
level (see docs/drop-test-200drops-analysis.md section 7 and the follow-up
discussion on PR #82), @ctrhjk lowered the CH5 trigger to **500 G** and ran a
dedicated validation: 30 auto-drops at 5 in (``5vs10_Signal{1..30}.csv``)
followed by 30 auto-drops at 10 in (``5vs10_Signal{31..60}.csv``), same rig
and channel map as the 200-drop campaign / check runs (CH2-4 TOP tri-axis,
CH5 base-plate single-axis trigger, CH6-8 BOT low-range tri-axis).

Questions this script answers, per height:

  1. **Trigger reliability at 500 G** — did every drop capture a real impact,
     what is the worst-case raw CH5 margin over the 500 G level, and how much
     clearance is there between the level and pre-impact activity?
  2. **Sensor health / saturation** — does 5 in bring CH7/CH8 (the ~990 G FS
     BOT axes that run over full scale at 10 in) back inside their range?
  3. **Metric quality for BO** — repeatability (CV) of the CFC-180 input
     (CH5), output (TOP resultant) and transmissibility T = TOP/CH5; drift
     across the 30 drops; height separation and scaling of the levels.

The output is a per-height comparison table, figures and a machine-readable
metrics JSON used by docs/drop-test-5vs10-analysis.md to recommend a drop
height for the BO campaign.
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
RAW = REPO / "data" / "drop-tests" / "5vs10" / "raw"
FIG = REPO / "data" / "drop-tests" / "5vs10" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate — the trigger channel
BOT_COLS = (4, 5, 6)  # CH6, CH7, CH8 — low-range tri-axis, bottom-vertex housing

FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9,
                "CH6": 1002.0, "CH7": 991.1, "CH8": 989.1}

TRIGGER_LEVEL_G = 500.0  # lowered from 1000 G for this validation
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

GROUPS = {"5in": range(1, 31), "10in": range(31, 61)}
REAL_IMPACT_FLOOR_G = 300.0
BOT_ALIVE_FLOOR_G = 50.0

# 10-in reference values on 7xadt6 from the check runs (1000 G trigger era)
CHECK2_10IN = {"top_180_g": 236.9, "ch5_180_g": 218.8, "t_ch5": 1.083,
               "top_width_ms": 1.48, "dom_freq_hz": 549.0}


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
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    m_top = windowed_peak(t, resultant(top180), i_imp, dt)
    m_ch5 = windowed_peak(t, cfc_filter(ch5, fs, 180), i_imp, dt)

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_width_ms": m_ch5["pulse_width_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "dom_freq_hz": ringdown_dom_freq(t, top, i_imp, fs),
    })
    if bot_alive:
        bot180 = np.stack([cfc_filter(bot[:, j], fs, 180) for j in range(3)], axis=1)
        m_bot = windowed_peak(t, resultant(bot180), i_imp, dt)
        row.update({"bot_180_g": m_bot["peak_abs_g"]})
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


def arr(rows, key):
    return np.array([r[key] for r in rows], float)


def main() -> int:
    groups: dict[str, list[dict]] = {}
    for gname, sigs in GROUPS.items():
        rows = []
        for k, sig in enumerate(sigs, start=1):
            row = analyze_capture(RAW / f"5vs10_Signal{sig}.csv")
            row["signal"] = sig
            row["drop"] = k
            rows.append(row)
        groups[gname] = rows

    print("=== 5 in vs 10 in drop-height comparison (CH5 trigger @ 500 G) ===")

    summary: dict = {"trigger_level_g": TRIGGER_LEVEL_G, "groups": {}}
    for gname, rows in groups.items():
        real = [r for r in rows if r["real_impact"]]
        spurious = [r["signal"] for r in rows if not r["real_impact"]]
        times = [datetime.fromisoformat(r["event_time"]) for r in rows]
        gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])
        drops = arr(real, "drop")

        ch5_raw = arr(real, "ch5_raw_g")
        pre = arr(rows, "pre_trigger_max_g")
        t_cross = arr(real, "trig_cross_ms")
        margins = ch5_raw / TRIGGER_LEVEL_G

        print(f"\n--- {gname}: capture health & trigger @ {TRIGGER_LEVEL_G:.0f} G ---")
        print(f"captures: {len(rows)} = {len(real)} real + {len(spurious)} spurious {spurious}")
        print(f"cadence: median {np.median(gaps):.0f} s; span "
              f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min")
        print(f"CH5 raw |peak|: {ch5_raw.mean():.0f} +- {ch5_raw.std():.0f} G "
              f"(range {ch5_raw.min():.0f}-{ch5_raw.max():.0f})")
        print(f"trigger margin (raw CH5 / {TRIGGER_LEVEL_G:.0f} G): "
              f"worst {margins.min():.2f}x, median {np.median(margins):.2f}x")
        print(f"pre-impact CH5 activity: max {pre.max():.1f} G "
              f"(clearance below level: {TRIGGER_LEVEL_G / pre.max():.0f}x)")
        print(f"first crossing of {TRIGGER_LEVEL_G:.0f} G: "
              f"{t_cross.mean():.3f} +- {t_cross.std():.3f} ms")

        dead = [r["signal"] for r in rows if not r["bot_alive"]]
        print(f"BOT alive on {len(rows) - len(dead)}/{len(rows)}"
              + (f"; DEAD on {dead}" if dead else ""))

        print(f"--- {gname}: saturation audit (raw |peak| vs full scale) ---")
        sat_summary = {}
        for name in FULL_SCALE_G:
            fr = np.array([r["sat"][name]["frac_fs"] for r in rows])
            n95 = int((fr >= 0.95).sum())
            n_over = int((fr > 1.0).sum())
            pin_max = max(r["sat"][name]["n_pinned"] for r in rows)
            sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name],
                                 "median_frac_fs": float(np.median(fr)),
                                 "max_frac_fs": float(fr.max()),
                                 "n_ge_95pct_fs": n95, "n_over_fs": n_over,
                                 "max_pinned_samples": pin_max}
            print(f"  {name}: median {100 * np.median(fr):5.1f}% FS   "
                  f"max {100 * fr.max():5.1f}% FS   >=95% FS on {n95:2d}/{len(rows)}   "
                  f">FS on {n_over:2d}/{len(rows)}   worst flat-top {pin_max} samples")

        top = arr(real, "top_180_g")
        ch5v = arr(real, "ch5_180_g")
        tch5 = arr(real, "t_ch5")
        width = arr(real, "top_width_ms")
        dv = arr(real, "ch5_dv_ms")
        dom = arr(real, "dom_freq_hz")

        print(f"--- {gname}: CFC-180 metrics ---")
        metrics_ols = {}
        for label, y in [("TOP output", top), ("CH5 input", ch5v),
                         ("T = TOP/CH5", tch5), ("pulse width ms", width),
                         ("delta-v m/s", dv)]:
            o = ols_full(drops, y)
            metrics_ols[label] = o
            print(f"  {label:14s}: mean {o['mean']:8.3f}  CV {o['cv']:5.2f}%   "
                  f"drift {o['slope_pct']:+.3f}%/drop (p = {o['p']:.3f})")
        print(f"  dominant ringdown mode: median {np.median(dom):.0f} Hz "
              f"(range {dom.min():.0f}-{dom.max():.0f})")

        summary["groups"][gname] = {
            "signals": [int(min(GROUPS[gname])), int(max(GROUPS[gname]))],
            "n_real": len(real), "spurious": spurious,
            "cadence_s_median": float(np.median(gaps)),
            "trigger": {"margin_worst": float(margins.min()),
                        "margin_median": float(np.median(margins)),
                        "pre_impact_max_g": float(pre.max()),
                        "cross_ms_mean": float(t_cross.mean()),
                        "cross_ms_std": float(t_cross.std())},
            "bot_dead_signals": dead,
            "saturation": sat_summary,
            "cfc180": {k: v for k, v in metrics_ols.items()},
            "dom_freq_hz_median": float(np.median(dom)),
            "per_capture": rows,
        }

    # ---------------- height comparison -------------------------------
    r5 = [r for r in groups["5in"] if r["real_impact"]]
    r10 = [r for r in groups["10in"] if r["real_impact"]]
    print("\n=== height comparison ===\n")
    comp = {}
    for label, key in [("CH5 raw", "ch5_raw_g"), ("TOP raw", "top_raw_g"),
                       ("CH5 CFC-180", "ch5_180_g"), ("TOP CFC-180", "top_180_g"),
                       ("T = TOP/CH5", "t_ch5"), ("pulse width ms", "top_width_ms"),
                       ("delta-v m/s", "ch5_dv_ms")]:
        a, b = arr(r5, key), arr(r10, key)
        tt = stats.ttest_ind(a, b, equal_var=False)
        ratio = b.mean() / a.mean()
        # pooled-SD Cohen's d for the height separation
        sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                     / (len(a) + len(b) - 2))
        d = (b.mean() - a.mean()) / sp if sp else float("nan")
        comp[label] = {"mean_5in": float(a.mean()), "cv_5in": cv(a),
                       "mean_10in": float(b.mean()), "cv_10in": cv(b),
                       "ratio_10_over_5": float(ratio),
                       "welch_p": float(tt.pvalue), "cohens_d": float(d)}
        print(f"  {label:14s}: 5in {a.mean():8.2f} (CV {cv(a):5.2f}%)   "
              f"10in {b.mean():8.2f} (CV {cv(b):5.2f}%)   "
              f"ratio {ratio:5.3f}   d = {d:6.2f}   p = {tt.pvalue:.2e}")
    print("\n  sqrt-height scaling reference: sqrt(10/5) = 1.414 "
          "(velocity/level ratio if the impact scaled ideally)")
    summary["height_comparison"] = comp

    # ---------------- figures ----------------------------------------
    col = {"5in": "tab:blue", "10in": "tab:red"}

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 8), sharex=False)
    for gname, rows in groups.items():
        real = [r for r in rows if r["real_impact"]]
        a1.plot(arr(real, "drop"), arr(real, "ch5_raw_g"), "o-", ms=3,
                color=col[gname], label=f"{gname} CH5 raw |peak|")
    a1.axhline(TRIGGER_LEVEL_G, color="k", ls="-", lw=1.4, label="500 G trigger level")
    a1.axhline(1000, color="k", ls=":", lw=1.2, label="old 1000 G level")
    pre_all = max(arr(rows, "pre_trigger_max_g").max() for rows in groups.values())
    a1.axhline(pre_all, color="tab:green", ls="--", lw=1,
               label=f"worst pre-impact activity ({pre_all:.0f} G)")
    a1.set(ylabel="raw |peak| (G)", yscale="log", xlabel="drop #",
           title="Trigger validation: CH5 raw peaks vs the 500 G level")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    for gname, rows in groups.items():
        for name, mk in [("CH7", "o"), ("CH8", "^")]:
            fr = [100 * r["sat"][name]["frac_fs"] for r in rows]
            a2.plot([r["drop"] for r in rows], fr, mk + "-", ms=3, color=col[gname],
                    alpha=0.8 if name == "CH7" else 0.5,
                    label=f"{gname} {name} (%FS)")
    a2.axhline(100, color="k", ls="-", lw=1.2, label="full scale")
    a2.axhline(95, color="k", ls=":", lw=1)
    a2.set(xlabel="drop #", ylabel="raw |peak| (% of full scale)",
           title="Low-range BOT headroom (CH7/CH8, FS ~990 G): 5 in vs 10 in")
    a2.legend(fontsize=8, ncol=2)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_trigger_saturation.png", dpi=130)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    panels = [("ch5_180_g", "CH5 input CFC-180 (G)"),
              ("top_180_g", "TOP output CFC-180 (G)"),
              ("t_ch5", "T = TOP/CH5"),
              ("ch5_dv_ms", "input delta-v (m/s)")]
    for ax, (key, label) in zip(axes.flat, panels):
        for gname, rows in groups.items():
            real = [r for r in rows if r["real_impact"]]
            y = arr(real, key)
            ax.plot(arr(real, "drop"), y, "o-", ms=3, color=col[gname],
                    label=f"{gname} (CV {cv(y):.1f}%)")
        ax.set(xlabel="drop #", ylabel=label)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    axes.flat[2].axhline(CHECK2_10IN["t_ch5"], color="k", ls="--", lw=1)
    axes.flat[2].text(1, CHECK2_10IN["t_ch5"], " check2 10-in ref (1.083)",
                      fontsize=7, va="bottom")
    fig.suptitle("CFC-180 metrics per drop: 5 in vs 10 in (30 drops each)")
    fig.tight_layout()
    fig.savefig(FIG / "02_metrics_by_height.png", dpi=130)
    plt.close(fig)

    with open(FIG / "5vs10_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
