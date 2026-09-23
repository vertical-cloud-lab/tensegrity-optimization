#!/usr/bin/env python3
"""Payload-protection metric audit: statistics + figures.

Consumes ``data/per-drop-payload-metrics.csv`` (from
``compute_drop_metrics.py``), aggregates per specimen and per design with
the campaign SOP (valid = raw CH5 >= 150 G, first two valid drops are
warm-up), cross-checks the reproduced legacy metrics against the
committed drop-results tables, and answers the PR #111 questions:

1. Does a time-averaged "organ deceleration" metric (moving-window
   average max, HIC-style dose, CFC-60, SDOF/SRS) rank the designs
   differently from the campaign's t180?
2. Is the longer-timescale metric a *better-measured* design property
   (reprint reliability over the nine drran/2dran design pairs,
   drop-to-drop CV) or a noisier one?
3. Where does the windowed dose live in the record: initial transmitted
   pulse, ringdown, or the specimen-hop landing ("beyond the initial
   shock wave")?

Everything lands in ``metrics.json``, ``tables/``, ``figures/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
TABLES = HERE / "tables"
FIGS = HERE / "figures"
AUDIT_DATA = HERE.parent / "cv-signal-audit" / "data"
SIM_DATA = HERE.parent / "sim-measured-correlations" / "data"

RNG_SEED = 20260923
N_PERM = 20000
WARMUP = 2
TRIGGER_LEVEL_G = 150.0

# Okabe-Ito, fixed batch order (validated with the dataviz six-checks script)
BATCHES = ["seed", "r2d2c", "drran", "2dran", "corny"]
BATCH_COLOR = {"seed": "#0072B2", "r2d2c": "#E69F00", "drran": "#009E73",
               "2dran": "#56B4E9", "corny": "#D55E00"}

COMMITTED = {
    "seed": "t3-prism-bo-batch-drop-results.csv",
    "r2d2c": "t3-prism-bo-round1-drop-results.csv",
    "drran": "t3-prism-bo-round3-drop-results.csv",
    "2dran": "t3-prism-bo-round3-reprint-drop-results.csv",
    "corny": "t3-prism-bo-round4-drop-results.csv",
}

WINDOWS_MS = (1, 3, 5, 10, 15, 36)
SRS_FN_HZ = (30, 60, 120, 250, 520, 1000)

# the metric ladder, curated reading order
LADDER = (["out_raw_g", "out_1000_g", "out_180_g", "out_cfc60_g"]
          + [f"out_avg{w}ms_g" for w in WINDOWS_MS]
          + ["out_clip3ms_g", "hic15_out", "hic36_out",
             "late_avg3ms_g", "late_avg10ms_g"]
          + [f"srs{f}_out_g" for f in SRS_FN_HZ])
LADDER_RATIO = (["t1000", "t180", "t60"]
                + [f"tavg{w}ms" for w in WINDOWS_MS]
                + ["hic15_ratio"] + [f"srs{f}_ratio" for f in SRS_FN_HZ]
                + ["e_rebound", "t_second_ms"])


def spearman_perm(x, y, rng, n_perm=N_PERM):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 4:
        return float("nan"), float("nan"), int(len(x))
    rho = stats.spearmanr(x, y).statistic
    perm = np.empty(n_perm)
    for i in range(n_perm):
        perm[i] = stats.spearmanr(x, rng.permutation(y)).statistic
    p = float((np.sum(np.abs(perm) >= abs(rho) - 1e-12) + 1) / (n_perm + 1))
    return float(rho), p, int(len(x))


def stabilized(df):
    """Valid drops minus the two SOP warm-up drops, per specimen."""
    out = []
    for (b, s), g in df.groupby(["batch", "specimen"], sort=False):
        g = g.sort_values("signal")
        v = g[g.in_raw_g >= TRIGGER_LEVEL_G]
        out.append(v.iloc[WARMUP:] if len(v) > WARMUP + 2 else v)
    return pd.concat(out, ignore_index=True)


def main():
    rng = np.random.default_rng(RNG_SEED)
    for d in (TABLES, FIGS):
        d.mkdir(exist_ok=True)

    drops = pd.read_csv(DATA / "per-drop-payload-metrics.csv")
    stab = stabilized(drops)
    num_cols = [c for c in stab.columns
                if c not in ("batch", "specimen", "signal", "file", "event_time")
                and pd.api.types.is_numeric_dtype(stab[c])]

    spec = stab.groupby(["batch", "specimen"])[num_cols].agg(["mean", "std", "count"])
    spec.columns = [f"{a}_{b}" for a, b in spec.columns]
    spec = spec.reset_index()

    # ---------------------------------------------------------------- joins
    sim = pd.read_csv(SIM_DATA / "sim-articles" / "sim_articles.csv")
    sim["print_id"] = sim.print_id.str.lower()
    spec = spec.merge(sim[["print_id", "design", "mass_g",
                           "nom_R_mm", "nom_H_mm", "nom_twist_deg",
                           "nom_strut_d_mm", "nom_cable_d_mm",
                           "tierB_t180", "tierC_t180"]],
                      left_on="specimen", right_on="print_id", how="left")

    # ------------------------------------------------- cross-check vs committed
    xcheck = {}
    for batch, fname in COMMITTED.items():
        com = pd.read_csv(AUDIT_DATA / fname).set_index("specimen")
        mine = spec[spec.batch == batch].set_index("specimen")
        common = mine.index.intersection(com.index)
        if not len(common):
            continue
        row = {"n_specimens": int(len(common))}
        for k_mine, k_com in [("t180_mean", "t180_mean"),
                              ("t1000_mean", "t1000_mean"),
                              ("e_rebound_mean", "e_rebound_mean"),
                              ("in_dv_ms_mean", "in_dv_ms_mean")]:
            if k_com in com.columns:
                d = (mine.loc[common, k_mine] - com.loc[common, k_com])
                rel = (d / com.loc[common, k_com]).abs().max()
                row[f"{k_mine}_max_rel_diff"] = float(rel)
        xcheck[batch] = row

    # ------------------------------------------------------------ design level
    spec["design_key"] = spec.design.fillna(spec.specimen)
    mapped = spec[spec.design.notna()].copy()
    des = mapped.groupby("design_key").agg(
        {**{f"{c}_mean": "mean" for c in num_cols},
         "batch": "first", "mass_g": "mean",
         "nom_R_mm": "first", "nom_H_mm": "first", "nom_twist_deg": "first",
         "nom_strut_d_mm": "first", "nom_cable_d_mm": "first",
         "tierB_t180": "mean", "tierC_t180": "mean"}).reset_index()
    # drran+2dran collapse to one design row; label that batch "round3"
    two_print = mapped.groupby("design_key").specimen.nunique()
    des["n_prints"] = des.design_key.map(two_print)
    des.loc[des.n_prints > 1, "batch"] = "round3"

    # reprint pairs: drran (print 1) vs 2dran (print 2), matched by design
    p1 = mapped[mapped.batch == "drran"].set_index("design_key")
    p2 = mapped[mapped.batch == "2dran"].set_index("design_key")
    pair_designs = p1.index.intersection(p2.index)

    # ------------------------------------------------------------- the ladder
    rows = []
    for metric in LADDER + LADDER_RATIO:
        mc = f"{metric}_mean"
        if mc not in des.columns:
            continue
        v = des[mc].astype(float)
        span = float(100 * (v.max() - v.min()) / v.mean()) if v.mean() else np.nan
        cvs = 100 * spec[f"{metric}_std"] / spec[mc].abs()
        med_cv = float(cvs.median())
        rel_rho = float(stats.spearmanr(p1.loc[pair_designs, mc],
                                        p2.loc[pair_designs, mc]).statistic)
        rho_t, p_t, _ = spearman_perm(v, des.t180_mean, rng, 2000)
        rho_c, p_c, _ = spearman_perm(v, des.nom_cable_d_mm, rng, 2000)
        rho_b, _, _ = spearman_perm(v, des.tierB_t180, rng, 2000)
        rows.append({"metric": metric, "design_span_pct": round(span, 2),
                     "median_within_cv_pct": round(med_cv, 3),
                     "span_over_cv": round(span / med_cv, 1) if med_cv else np.nan,
                     "reprint_rho_9pairs": round(rel_rho, 3),
                     "rho_vs_t180": round(rho_t, 3), "p_vs_t180": round(p_t, 4),
                     "rho_vs_cable_d": round(rho_c, 3),
                     "rho_vs_tierB_t180": round(rho_b, 3)})
    ladder = pd.DataFrame(rows)
    ladder.to_csv(TABLES / "metric_ladder.csv", index=False)

    # --------------------------------------------------------- ranking shifts
    keys = ["t180_mean", "tavg3ms_mean", "tavg10ms_mean", "tavg36ms_mean",
            "hic15_ratio_mean", "out_avg10ms_g_mean", "out_avg36ms_g_mean",
            "hic15_out_mean", "srs60_ratio_mean", "srs520_ratio_mean"]
    rk = des[["design_key", "batch"] + keys].copy()
    for k in keys:
        rk[f"rank_{k}"] = rk[k].rank()
    rk.sort_values("rank_t180_mean").to_csv(TABLES / "design_rankings.csv", index=False)
    rank_corr = {f"{a} vs {b}": round(float(stats.spearmanr(des[a], des[b]).statistic), 3)
                 for a in keys for b in keys if a < b}

    # article-level specimen table
    spec.drop(columns=["print_id"], errors="ignore").to_csv(
        TABLES / "specimen_metrics.csv", index=False)
    des.to_csv(TABLES / "design_metrics.csv", index=False)

    # ------------------------------------------------ headline correlations
    heads = {}
    for name, a, b, frame in [
        ("hic15out_vs_t180_design", "hic15_out_mean", "t180_mean", des),
        ("outavg10_vs_t180_design", "out_avg10ms_g_mean", "t180_mean", des),
        ("tavg36_vs_t180_design", "tavg36ms_mean", "t180_mean", des),
        ("late3_vs_erebound_design", "late_avg3ms_g_mean", "e_rebound_mean", des),
        ("late3_vs_tsecond_design", "late_avg3ms_g_mean", "t_second_ms_mean", des),
        ("outavg36_vs_erebound_design", "out_avg36ms_g_mean", "e_rebound_mean", des),
        ("hic15out_vs_cable_d", "hic15_out_mean", "nom_cable_d_mm", des),
        ("outavg10_vs_mass", "out_avg10ms_g_mean", "mass_g", des),
        ("tavg10_vs_tierB", "tavg10ms_mean", "tierB_t180", des),
    ]:
        rho, p, n = spearman_perm(frame[a], frame[b], rng)
        heads[name] = {"rho": round(rho, 3), "perm_p": round(p, 5), "n": n}

    # where does the dose live?
    t10 = stab.t_at_out_avg10_ms
    dose_loc = {
        "frac_at_impact_10ms": float(np.mean(t10 < 12)),
        "frac_at_second_event_10ms": float(np.mean(t10 > 12)),
        "median_t_at_10ms_dose_ms": float(t10.median()),
        "late3_over_out180_median": float((stab.late_avg3ms_g / stab.out_180_g).median()),
    }

    # notable designs under each objective
    def toplist(frame, col, k=5, asc=True):
        f = frame.sort_values(col, ascending=asc)
        return [f"{r.design_key} ({getattr(r, col):.3g})"
                for r in f.head(k).itertuples()]

    notable = {
        "best_t180": toplist(des, "t180_mean"),
        "best_tavg36": toplist(des, "tavg36ms_mean"),
        "best_out_avg10_abs": toplist(des, "out_avg10ms_g_mean"),
        "best_hic15_out": toplist(des, "hic15_out_mean"),
        "worst_hic15_out": toplist(des, "hic15_out_mean", asc=False),
    }

    metrics = {
        "config": "recomputed from Box waveforms, 45 sessions, "
                  "stabilized drops per campaign SOP (warmup 2, CH5 >= 150 G)",
        "n_captures": int(len(drops)), "n_stabilized": int(len(stab)),
        "n_specimens": int(spec.specimen.nunique()),
        "n_designs_mapped": int(des.design_key.nunique()),
        "n_reprint_pairs": int(len(pair_designs)),
        "crosscheck_vs_committed": xcheck,
        "dose_location": dose_loc,
        "headline_correlations": heads,
        "rank_correlations_between_objectives": rank_corr,
        "notable_designs": notable,
    }
    (HERE / "metrics.json").write_text(json.dumps(metrics, indent=1))
    print(json.dumps(metrics, indent=1)[:4000])
    print("\nladder:")
    print(ladder.to_string(index=False))

    make_figures(stab, spec, des, mapped, ladder, pair_designs)


# ------------------------------------------------------------------- figures
def eff_ms(metric):
    """Nominal averaging timescale for the ladder x-axis."""
    if metric.startswith("out_avg"):
        return float(metric.split("avg")[1].split("ms")[0])
    if metric.startswith("tavg"):
        return float(metric.split("tavg")[1].split("ms")[0])
    return {"out_raw_g": 0.05, "out_1000_g": 0.3, "t1000": 0.3,
            "out_180_g": 1.7, "t180": 1.7, "out_cfc60_g": 5.0, "t60": 5.0}.get(metric)


def make_anatomy_figure(spec, raw_root=Path("/tmp/waveforms"), signal_no=10):
    """In/out waveforms for the best protector vs the worst HIC design,
    with the 10 ms moving-average overlay. Decimated traces are cached in
    ``data/example-traces.npz`` so the figure re-renders without the 8.6 GB
    raw tree."""
    import re

    from scipy import signal as sig

    cache = DATA / "example-traces.npz"
    best = spec.loc[spec.hic15_out_mean.idxmin()]
    worst = spec.loc[spec.hic15_out_mean.idxmax()]
    picks = [(str(best.specimen), str(best.design)),
             (str(worst.specimen), str(worst.design))]

    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        traces = {k: z[k] for k in z.files}
        meta = json.loads(str(traces.pop("meta")))
    elif raw_root.exists():
        import compute_drop_metrics as cdm
        traces, meta = {}, {"signal": signal_no, "picks": picks, "fsd": 50000.0}
        for sname, _ in picks:
            hits = [p for p in raw_root.rglob(f"*Signal{signal_no}.csv")
                    if sname in p.name.lower() or sname in p.parent.name.lower()]
            t, ch, _ = cdm.parse_capture(hits[0])
            dt = float(np.median(np.diff(t)))
            base = np.median(ch[int(0.070 / dt):], axis=0)
            top = ch[:, cdm.TOP_COLS] - base[list(cdm.TOP_COLS)]
            ch5 = ch[:, cdm.CH5] - base[cdm.CH5]
            fsd = (1.0 / dt) / cdm.DECIM
            topd = np.stack([sig.decimate(top[:, c], cdm.DECIM, ftype="fir")
                             for c in range(3)], axis=1)
            ch5d = sig.decimate(ch5, cdm.DECIM, ftype="fir")
            sos = sig.butter(2, 1650.0 / (fsd / 2), btype="low", output="sos")
            out = np.sqrt(np.sum(np.stack([sig.sosfiltfilt(sos, topd[:, c])
                                           for c in range(3)], 1) ** 2, axis=1))
            inn = np.abs(sig.sosfiltfilt(sos, ch5d))
            i_imp = int(np.argmax(inn[:int(0.015 * fsd)]))
            traces[f"{sname}_out"] = out
            traces[f"{sname}_in"] = inn
            meta[f"{sname}_i_imp"] = i_imp
        np.savez_compressed(cache, meta=json.dumps(meta), **traces)
    else:
        print("no waveforms and no cache; skipping anatomy figure")
        return

    fsd = float(meta["fsd"])
    fig, axes = plt.subplots(2, 1, figsize=(9.8, 6.8), sharex=True)
    for ax, (sname, dname) in zip(axes, meta["picks"]):
        out = traces[f"{sname}_out"]
        inn = traces[f"{sname}_in"]
        i_imp = int(meta[f"{sname}_i_imp"])
        tt = (np.arange(len(out)) - i_imp) / fsd * 1e3
        n10 = int(0.010 * fsd)
        avg10 = np.convolve(out, np.ones(n10) / n10, mode="same")
        ax.fill_between(tt, 0, inn, color="0.75", lw=0, alpha=0.8,
                        label="base input |CH5| (CFC-1000)")
        ax.plot(tt, out, color="#0072B2", lw=0.9,
                label="top-vertex resultant (CFC-1000)")
        ax.plot(tt, avg10, color="#D55E00", lw=2.0,
                label="10 ms moving average of output")
        j = int(np.argmax(avg10))
        ax.annotate(f"max 10 ms dose: {avg10[j]:.0f} G",
                    (tt[j], avg10[j]), textcoords="offset points",
                    xytext=(12, 14), fontsize=8.5, color="#D55E00")
        ax.set_xlim(-5, 80)
        ax.set_ylabel("acceleration (G)")
        ax.set_title(f"{sname} ({dname}), drop {meta['signal']}", fontsize=9.5,
                     loc="left")
        ax.grid(alpha=0.2)
    lo = axes[0]
    lo.legend(fontsize=8, frameon=False, loc="upper right")
    for ax in axes:
        ax.annotate("initial transmitted pulse + ringdown", (8, ax.get_ylim()[1] * 0.55),
                    fontsize=8, color="0.35")
        ax.annotate("specimen-hop landing\n(the 'second event')", (48, ax.get_ylim()[1] * 0.3),
                    fontsize=8, color="0.35")
    axes[1].set_xlabel("time after impact (ms)")
    fig.suptitle("What the drop record contains, best vs worst payload-dose design",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "waveform-anatomy.png", dpi=160)
    plt.close(fig)


def make_figures(stab, spec, des, mapped, ladder, pair_designs):
    make_anatomy_figure(spec)

    # ---- F2: signal vs noise along the timescale ladder -------------------
    fig, axes = plt.subplots(2, 1, figsize=(9.5, 7.2), sharex=True)
    series = [  # (metrics, color, linestyle, label)
        (["out_1000_g", "out_180_g", "out_cfc60_g"], "#0072B2", "--",
         "absolute output, filtered peak"),
        ([f"out_avg{w}ms_g" for w in WINDOWS_MS], "#0072B2", "-",
         "absolute output, moving-window average"),
        (["t1000", "t180", "t60"], "#D55E00", "--",
         "out/in ratio, filtered peak"),
        ([f"tavg{w}ms" for w in WINDOWS_MS], "#D55E00", "-",
         "out/in ratio, moving-window average"),
    ]
    lad = ladder.set_index("metric")
    for ax, col, ylab in [(axes[0], "reprint_rho_9pairs",
                           "print-1 vs print-2 rank corr.\n(9 design pairs)"),
                          (axes[1], "median_within_cv_pct",
                           "median drop-to-drop CV (%)")]:
        for metrics, color, ls, label in series:
            xs = [eff_ms(m) for m in metrics if m in lad.index]
            ys = [lad.loc[m, col] for m in metrics if m in lad.index]
            filled = ls == "-"
            ax.plot(xs, ys, ls, color=color, lw=1.6, alpha=0.9,
                    marker="o" if filled else "s", ms=6 if filled else 5,
                    mfc=color if filled else "white", mew=1.3,
                    label=label if ax is axes[0] else None)
        ax.set_xscale("log")
        ax.grid(alpha=0.2)
        ax.set_ylabel(ylab, fontsize=9)
    axes[0].axhline(0, color="0.6", lw=0.8)
    for m, lbl, xy in [("t1000", "t1000", (-14, 6)), ("t180", "t180", (-2, -14)),
                       ("t60", "CFC-60 peak", (4, 4))]:
        axes[0].annotate(lbl, (eff_ms(m), lad.loc[m, "reprint_rho_9pairs"]),
                         textcoords="offset points", xytext=xy,
                         fontsize=8, color="#D55E00")
    axes[0].annotate("10 ms window: rho = "
                     f"{lad.loc['tavg10ms', 'reprint_rho_9pairs']:.2f}",
                     (10, lad.loc["tavg10ms", "reprint_rho_9pairs"]),
                     textcoords="offset points", xytext=(8, -2), fontsize=8.5,
                     color="#D55E00")
    axes[0].annotate("15+ ms windows swallow the\nspecimen-hop landing\n"
                     "(timing = seat noise)",
                     (15, lad.loc["tavg15ms", "reprint_rho_9pairs"]),
                     textcoords="offset points", xytext=(10, 30), fontsize=8,
                     color="0.35")
    axes[0].legend(fontsize=8, frameon=False, loc="upper left")
    axes[1].set_xlabel("effective averaging timescale (ms)", fontsize=9)
    axes[0].set_title("A 10 ms averaging window measures the design far better "
                      "than the t180 peak ratio", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(FIGS / "timescale-ladder.png", dpi=160)
    plt.close(fig)

    # ---- F3: rank shift slopegraph (t180 -> reliable 10 ms dose) ----------
    fig, ax = plt.subplots(figsize=(7.8, 9.0))
    a = des.t180_mean.rank()
    b = des.tavg10ms_mean.rank()
    n = len(des)
    friendly = {"trial37": "trial37 = corny7"}
    for i, r in des.iterrows():
        col = BATCH_COLOR.get(r.batch, "#888888") if r.batch != "round3" \
            else "#009E73"
        ax.plot([0, 1], [a[i], b[i]], "-", color=col, lw=1.1, alpha=0.75)
        ax.plot([0, 1], [a[i], b[i]], "o", color=col, ms=3.5)
        move = abs(a[i] - b[i])
        if move >= 8 or r.design_key in ("trial37", "6lhxfy"):
            ax.annotate(f" {friendly.get(r.design_key, r.design_key)}",
                        (1, b[i]), fontsize=7.5, va="center", color=col)
            ax.annotate(f"{friendly.get(r.design_key, r.design_key)} ",
                        (0, a[i]), fontsize=7.5, va="center", ha="right", color=col)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["rank by t180\n(CFC-180 peak ratio, reprint rho +0.08)",
                        "rank by tavg10ms\n(10 ms windowed dose ratio, "
                        "reprint rho +0.93)"])
    ax.set_ylabel(f"rank among {n} designs (1 = best protector)")
    ax.set_xlim(-0.42, 1.42)
    ax.invert_yaxis()
    ax.grid(alpha=0.15, axis="y")
    handles = [plt.Line2D([], [], color=c, lw=2, label=l) for l, c in
               [("seed", "#0072B2"), ("r2d2c", "#E69F00"),
                ("round3 (drran+2dran)", "#009E73"), ("corny", "#D55E00")]]
    ax.legend(handles=handles, fontsize=8, loc="lower center",
              bbox_to_anchor=(0.5, 1.005), ncol=4, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "rank-shift-slopegraph.png", dpi=160)
    plt.close(fig)

    # ---- F4: SRS ratio vs frequency per batch ----------------------------
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for bname in BATCHES:
        g = spec[spec.batch == bname]
        med = [g[f"srs{f}_ratio_mean"].median() for f in SRS_FN_HZ]
        q1 = [g[f"srs{f}_ratio_mean"].quantile(0.25) for f in SRS_FN_HZ]
        q3 = [g[f"srs{f}_ratio_mean"].quantile(0.75) for f in SRS_FN_HZ]
        ax.fill_between(SRS_FN_HZ, q1, q3, color=BATCH_COLOR[bname], alpha=0.12, lw=0)
        ax.plot(SRS_FN_HZ, med, "o-", color=BATCH_COLOR[bname], lw=1.6, ms=4.5,
                label=bname)
    ax.axhline(1.0, color="0.4", lw=0.9, ls="--")
    ax.annotate("amplifies payload SDOF response", (32, 1.03), fontsize=8, color="0.3")
    ax.annotate("isolates", (32, 0.93), fontsize=8, color="0.3")
    ax.set_xscale("log")
    ax.set_xticks(SRS_FN_HZ)
    ax.set_xticklabels([str(f) for f in SRS_FN_HZ])
    ax.set_xlabel("payload SDOF natural frequency (Hz), Q = 10")
    ax.set_ylabel("SRS ratio: top-vertex / base input")
    ax.set_title("Where a payload would feel a difference (SDOF maximax SRS, medians + IQR)",
                 fontsize=10)
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "srs-ratio-by-frequency.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
