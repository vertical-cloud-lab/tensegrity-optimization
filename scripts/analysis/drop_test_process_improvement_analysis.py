#!/usr/bin/env python3
"""Drop-test process scorecard: the first drops (05-22) vs the current SOP.

Answers @ctrhjk on PR #86 (10-10): "Compared to the very first drop test and
process, how much has this test process enhanced? Can you give a number for
that?"

Derived analysis with no raw data of its own. The first-drop numbers are
recomputed from the committed raw exports. Every later era is read from
metrics that the per-dataset analyses already committed:

  era 0  first drops, 05-22 ............. data/drop-tests/raw/ (Signal 10-14),
                                           via the drop_test_analysis.py helpers
  era 1  vertex/acrylic + clip sweep ..... capture outcomes from the two
         06-22 / 06-24                     writeups (the sweep left no CSVs)
  era 2  input-output, 06-25 ............ data/drop-tests/input-output/raw/, via
                                           the drop_test_input_output_analysis.py helpers
  era 3  key-seat + felt, 06-29 -> 07-22 . committed *_metrics.json files
  era 4  current SOP, 08-13 -> 10-02 .... the seven BO-campaign
                                           campaign_metrics.json files plus the
                                           round-3 three-print comparison

The polyurethane-mat qualification sessions (07-30 -> 08-12) belong to no
era, because they changed the absorber and the capture settings mid-stream.

Headline metric, "design resolution": the smallest difference between two
designs that the test detects with 80 % power at alpha = 0.05 (two-sided)
when each design is measured on one article:

    MDD = (z_0.975 + z_0.80) * sqrt(2) * sigma_design
    sigma_design^2 = sigma_article^2 + sigma_drop^2 / n_drops

sigma_article is the article + mount-seat + session noise. Era 0 never
measured it, so its MDD counts drop noise only. That makes it a lower bound,
and the improvement factor a lower bound too. Era 3's sigma comes from
same-article re-tests in separate sessions; era 4's from the 21 healthy
round-3 sessions (three prints of nine designs).

Outputs (data/drop-tests/process-improvement/figures/):
  process_improvement_metrics.json, 01_process_improvement.png
"""

import json
import math
import os
import sys
from datetime import datetime
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.ticker import FixedLocator, NullLocator
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
DT = os.path.join(ROOT, "data", "drop-tests")
OUT = os.path.join(DT, "process-improvement", "figures")

sys.path.insert(0, HERE)
import drop_test_analysis as first  # noqa: E402  (era 0 helpers)
import drop_test_input_output_analysis as io_an  # noqa: E402  (era 2 helpers)

BLUE = "#2a78d6"
GRAY = "#898781"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"

Z_SUM = NormalDist().inv_cdf(0.975) + NormalDist().inv_cdf(0.80)  # 2.80

# Era 1 has no per-drop repeats to compute from. Capture outcomes are taken
# from docs/drop-test-vertex-acrylic-analysis.md (vertex 4/4 clean; acrylic:
# n0jdwk 3 G, T3_0103 24 G, T3_0000 sensor fell off, only m6cyoq registered)
# and docs/drop-test-clip-height-analysis.md (0/8 triggered, video only).
ERA1_CAPTURES = [
    ("vertex mount, 06-22", 4, 4),
    ("acrylic plate, 06-22", 1, 4),
    ("clip-height sweep, 06-24", 0, 8),
]

# Era 3 sessions with a stabilized T = TOP/CH5 CV. The sample-size
# meta-analysis already collected most of them. 30drops-real is left out
# because CH5 fell off mid-run (only a saturation-biased T* exists), and its
# input-output row is era 2, recomputed below.
ERA3_EXTRA = [
    ("500drops", "500drops/figures/500drops_metrics.json",
     ["trends_ols", "T = TOP/CH5"]),
    ("500drops-nobot", "500drops-nobot/figures/500drops_nobot_metrics.json",
     ["trends_ols", "T = TOP/CH5"]),
    ("200drops-check", "200drops-check/figures/200drops_check_metrics.json",
     ["problem3_ch5", "t_ch5"]),
    ("200drops-check2", "200drops-check2/figures/200drops_check2_metrics.json",
     ["problem3_ch5", "t_ch5"]),
    ("prc1kn 60 in 07-21", "prc1kn-60in-5felt/figures/prc1kn_60in_metrics.json",
     ["specimen", "stabilized_ols", "T TOP/CH5"]),
    ("prc1kn 60 in 07-22", "7-22 - 7-27 Drop Tests/figures/batch_722_727_metrics.json",
     ["prc1kn_batch_comparison", "t_ch5", "batch2"]),
]

# Same article, re-tested in a separate session (mount re-seated).
ERA3_PAIRS = [
    ("7xadt6, 10 in (200drops -> 200drops-check)",
     ("200drops/figures/200drops_metrics.json", ["stabilized_ols", "T TOP/CH5"]),
     ("200drops-check/figures/200drops_check_metrics.json", ["problem3_ch5", "t_ch5"])),
    ("bubbled-TPU print, 10 in (500drops -> 500drops-nobot)",
     ("500drops/figures/500drops_metrics.json", ["trends_ols", "T = TOP/CH5"]),
     ("500drops-nobot/figures/500drops_nobot_metrics.json", ["trends_ols", "T = TOP/CH5"])),
    ("prc1kn, 13 in (drift-calibration -> drift-calibration2)",
     ("drift-calibration/figures/drift_calibration_metrics.json", ["stabilized_ols", "T"]),
     ("drift-calibration2/figures/drift_calibration2_metrics.json", ["stabilized_ols", "T"])),
    ("prc1kn, 60 in (07-21 -> 07-22)",
     ("7-22 - 7-27 Drop Tests/figures/batch_722_727_metrics.json",
      ["prc1kn_batch_comparison", "t_ch5", "batch1"]),
     ("7-22 - 7-27 Drop Tests/figures/batch_722_727_metrics.json",
      ["prc1kn_batch_comparison", "t_ch5", "batch2"])),
]

ERA4_CAMPAIGNS = [
    ("sobol", "sobol-campaign/figures/campaign_metrics.json"),
    ("sobol-partial", "sobol-campaign/figures/partial_sessions_metrics.json"),
    ("r2d2", "r2d2-checkin/figures/campaign_metrics.json"),
    ("drran", "drran-checkin/figures/campaign_metrics.json"),
    ("2dran", "2dran-checkin/figures/campaign_metrics.json"),
    ("corny", "corny-checkin/figures/campaign_metrics.json"),
    ("dran3", "dran3-checkin/figures/campaign_metrics.json"),
]
# Same article, re-seated: the two interrupted SOBOL sessions re-ran in full.
ERA4_PAIRS = [("6lhxfy", "6lhxfy-s1"), ("amdjwm", "amdjwm-s1")]
THREE_PRINT = "dran3-checkin/figures/three_print_comparison.json"


def load(path):
    with open(os.path.join(DT, path)) as fh:
        return json.load(fh)


def dig(d, keys):
    for k in keys:
        d = d[k]
    return d


def cv_pct(vals):
    a = np.asarray(vals, float)
    return float(100.0 * a.std(ddof=1) / a.mean())


def era0():
    """Recompute the first drops (Signal 10-14) the way drop_test_analysis.py does."""
    runs = {}
    for _, fname, desc in first.RUNS:
        t, ch = first.load(first.RAW / fname)
        dt = float(np.median(np.diff(t)))
        ch1 = ch[:, 0] - np.median(ch[: int(0.002 / dt), 0])
        m = first.pulse_metrics(t, first.cfc_filter(ch1, 1.0 / dt, 180))
        runs[fname] = dict(desc=desc, raw_g=float(np.abs(ch1).max()),
                           cfc180_g=float(m["peak_abs_g"]),
                           width_ms=float(m["pulse_width_ms"]),
                           t_peak_ms=float(m["t_peak_ms"]))
    aud = [runs[f"Signal_1{k}_audrey.txt"] for k in (1, 2, 3)]
    peaks = [r["cfc180_g"] for r in aud]
    s, n = float(np.std(peaks, ddof=1)), len(peaks)
    # 95 % CI on sigma from n - 1 = 2 dof, expressed as a CV
    lo = s * math.sqrt((n - 1) / stats.chi2.ppf(0.975, n - 1))
    hi = s * math.sqrt((n - 1) / stats.chi2.ppf(0.025, n - 1))
    mean = float(np.mean(peaks))
    petg = runs["Signal_10_PETG.txt"]["raw_g"] / runs["Signal_14_control.txt"]["raw_g"]
    return dict(
        runs=runs,
        audrey_cfc180_g=peaks,
        drop_cv_pct=cv_pct(peaks),
        drop_cv_ci95_pct=[100 * lo / mean, 100 * hi / mean],
        raw_peak_cv_pct=cv_pct([r["raw_g"] for r in aud]),
        width_cv_pct=cv_pct([r["width_ms"] for r in aud]),
        width_range_ms=[min(r["width_ms"] for r in aud), max(r["width_ms"] for r in aud)],
        t_peak_range_ms=[min(r["t_peak_ms"] for r in runs.values()),
                         max(r["t_peak_ms"] for r in runs.values())],
        petg_raw_over_control=petg,
        # PETG's raw peak within ~1 % of the no-specimen control = a direct
        # plate-on-plate hit (bungee lift-off), per docs/drop-test-analysis.md
        specimen_drops=4,
        valid_specimen_drops=3 if petg > 0.95 else 4,
        n_drops_per_article=n,
    )


def era2():
    """Per-drop T for the input-output series, same reduction as its script."""
    by_spec = {}
    for spec in io_an.SPECIMENS:
        ts, outs = [], []
        for k in range(1, io_an.N_DROPS + 1):
            t, ch = io_an.load(io_an.RAW / f"{spec}_Signal{k}.csv")
            dt = float(np.median(np.diff(t)))
            fs = 1.0 / dt
            nb = max(1, int(io_an.BASELINE_S / dt))
            ch5 = ch[:, io_an.CH5] - np.median(ch[:nb, io_an.CH5])
            out = ch[:, io_an.OUT_COLS] - np.median(ch[:nb, io_an.OUT_COLS], axis=0)
            i_imp = io_an.impact_index(t, ch5, dt)
            in180 = io_an.windowed_peak(t, io_an.cfc_filter(ch5, fs, 180), i_imp, dt)["peak_abs_g"]
            res = io_an.resultant(np.stack(
                [io_an.cfc_filter(out[:, j], fs, 180) for j in range(out.shape[1])], axis=1))
            out180 = io_an.windowed_peak(t, res, i_imp, dt)["peak_abs_g"]
            ts.append(out180 / in180)
            outs.append(out180)
        by_spec[spec] = dict(t_mean=float(np.mean(ts)), t_cv_pct=cv_pct(ts),
                             out_cv_pct=cv_pct(outs))
    return dict(sessions=by_spec, valid=20, captures=20,
                median_t_cv_pct=float(np.median([v["t_cv_pct"] for v in by_spec.values()])),
                median_out_cv_pct=float(np.median([v["out_cv_pct"] for v in by_spec.values()])))


def era3():
    ss = load("sample-size/figures/sample_size_metrics.json")
    sessions = []
    for c in ss["campaigns"]:
        if c["dataset"] != "30drops-real":
            sessions.append((c["dataset"], c["T_cv"]))
    for c in ss["n5_series"]:
        if not c["dataset"].startswith("input-output"):
            sessions.append((c["dataset"], c["T_cv"]))
    for label, path, keys in ERA3_EXTRA:
        sessions.append((label, dig(load(path), keys)["cv"]))
    pairs = []
    for label, (pa, ka), (pb, kb) in ERA3_PAIRS:
        a, b = dig(load(pa), ka)["mean"], dig(load(pb), kb)["mean"]
        pairs.append(dict(article=label, t_first=a, t_second=b, delta_pct=100 * (b - a) / a))
    return dict(sessions=[dict(label=k, t_cv_pct=v) for k, v in sessions],
                median_t_cv_pct=float(np.median([v for _, v in sessions])),
                retest_pairs=pairs)


def era4():
    sessions = {}
    for batch, path in ERA4_CAMPAIGNS:
        for sid, s in load(path)["specimens"].items():
            m, rows = s["metrics"], s["rows"]
            times = [datetime.fromisoformat(r["event_time"]) for r in rows]
            gaps = np.diff([x.timestamp() for x in times])
            sessions[sid] = dict(
                batch=batch, first_event=s["event_first"],
                captures=s["n_captures"], valid=s["n_valid"],
                n_stabilized=m["t180"]["n"], t180=m["t180"]["mean"],
                t180_cv_pct=m["t180"]["cv_pct"],
                out180_cv_pct=m["out_180_g"]["cv_pct"],
                in180_cv_pct=m["in_180_g"]["cv_pct"],
                out_width_cv_pct=cv_pct([r["out_width_ms"] for r in rows]),
                t_imp_ms_mean=float(np.mean([r["t_imp_ms"] for r in rows])),
                t_imp_ms_sd=float(np.std([r["t_imp_ms"] for r in rows], ddof=1)),
                cadence_s=float(np.median(gaps)) if len(gaps) else None,
                dv_ms=s["dv_health"]["session_mean"],
                dv_frac_freefall=s["dv_health"]["frac_freefall"],
                ch5_worst_frac_fs=s["worst_frac_fs"]["CH5"],
            )
    v = list(sessions.values())
    med = lambda k: float(np.median([x[k] for x in v]))  # noqa: E731
    pairs = []
    for full, partial in ERA4_PAIRS:  # the interrupted session ran first
        t1, t2 = sessions[partial]["t180"], sessions[full]["t180"]
        pairs.append(dict(article=full, t_first=t1, t_second=t2, delta_pct=100 * (t2 - t1) / t1))
    dates = sorted(x["first_event"][:10] for x in v)
    return dict(
        sessions=sessions, n_sessions=len(v), first_date=dates[0], last_date=dates[-1],
        captures=sum(x["captures"] for x in v), valid=sum(x["valid"] for x in v),
        median_t_cv_pct=med("t180_cv_pct"), median_out_cv_pct=med("out180_cv_pct"),
        median_in_cv_pct=med("in180_cv_pct"), median_out_width_cv_pct=med("out_width_cv_pct"),
        t_imp_ms_range=[min(x["t_imp_ms_mean"] for x in v), max(x["t_imp_ms_mean"] for x in v)],
        median_t_imp_sd_ms=med("t_imp_ms_sd"), median_cadence_s=med("cadence_s"),
        dv_range_ms=[min(x["dv_ms"] for x in v), max(x["dv_ms"] for x in v)],
        dv_frac_freefall_range=[min(x["dv_frac_freefall"] for x in v),
                                max(x["dv_frac_freefall"] for x in v)],
        ch5_worst_frac_fs=max(x["ch5_worst_frac_fs"] for x in v),
        retest_pairs=pairs,
    )


def three_print():
    """Round-3 article + seat noise and how well the health screen catches outliers."""
    d = load(THREE_PRINT)
    fit = d["aggregate"]["additive_fit_screened"]
    cells = []
    for des in d["designs"]:
        vals = [p["t180"] for p in des["prints"].values()]
        med = float(np.median(vals))
        for p in des["prints"].values():
            cells.append(dict(label=p["label"], spec=des["spec"], screened=p["screened"],
                              t180=p["t180"], dev_pct=100 * (p["t180"] - med) / med))
    scr = [c for c in cells if c["screened"]]
    flagged = [c for c in cells if not c["screened"]]
    return dict(
        resid_sd=fit["resid_sd"], dof=fit["dof"], n_cells=fit["n_cells"],
        screened_mean_t=float(np.mean([c["t180"] for c in scr])),
        article_sd_pct=100 * fit["resid_sd"] / float(np.mean([c["t180"] for c in scr])),
        n_flagged=len(flagged),
        flagged_abs_dev_pct=sorted(abs(c["dev_pct"]) for c in flagged),
        screened_median_abs_dev_pct=float(np.median([abs(c["dev_pct"]) for c in scr])),
        screened_max_abs_dev_pct=float(max(abs(c["dev_pct"]) for c in scr)),
        n_over_2pct=sum(abs(c["dev_pct"]) > 2 for c in cells),
        n_over_2pct_flagged=sum(abs(c["dev_pct"]) > 2 for c in flagged),
        model_rho=d["model_agreement"]["screened_design_means"]["spearman_rho"],
        model_rms=d["model_agreement"]["screened_design_means"]["rms_vs_pred"],
    )


def mdd(sigma_design_pct):
    return Z_SUM * math.sqrt(2.0) * sigma_design_pct


def resolution(e0, e3, e4, tp):
    n4 = 18  # stabilized drops in the standard 20-drop session
    s0 = e0["drop_cv_pct"] / math.sqrt(e0["n_drops_per_article"])  # drop noise only
    # same-article re-tests: sigma of one session = rms(delta) / sqrt(2)
    s3 = math.sqrt(np.mean([p["delta_pct"] ** 2 for p in e3["retest_pairs"]]) / 2.0)
    sa, sd = tp["article_sd_pct"], e4["median_t_cv_pct"]
    s4_1 = math.sqrt(sa ** 2 + sd ** 2 / n4)
    s4_3 = math.sqrt(sa ** 2 / 3 + sd ** 2 / (3 * n4))
    s4_seat = math.sqrt(np.mean([p["delta_pct"] ** 2 for p in e4["retest_pairs"]]) / 2.0)
    lo, hi = e0["drop_cv_ci95_pct"]
    n0 = e0["n_drops_per_article"]
    return dict(
        z_sum=Z_SUM, n_drops_era4=n4,
        sigma_design_pct=dict(era0_lower_bound=s0, era3_session=s3,
                              era4_one_article=s4_1, era4_three_prints=s4_3),
        sigma_same_article_retest_pct=dict(era3=s3, era4=s4_seat),
        mdd_pct=dict(era0_lower_bound=mdd(s0), era3_session=mdd(s3),
                     era4_one_article=mdd(s4_1), era4_three_prints=mdd(s4_3)),
        factor_design_one_article=mdd(s0) / mdd(s4_1),
        factor_design_three_prints=mdd(s0) / mdd(s4_3),
        factor_design_ci95_from_era0_cv=[lo / math.sqrt(n0) / s4_1, hi / math.sqrt(n0) / s4_1],
        factor_per_drop=e0["drop_cv_pct"] / e4["median_t_cv_pct"],
        factor_per_drop_ci95=[lo / e4["median_t_cv_pct"], hi / e4["median_t_cv_pct"]],
        factor_per_drop_same_quantity=e0["drop_cv_pct"] / e4["median_out_cv_pct"],
        era0_drops_to_match_era4=(e0["drop_cv_pct"] / s4_1) ** 2,
        factor_session_retest=s3 / s4_seat,
    )


def rounded_barh(ax, y, width, color, thick_pt=18.0, r_pt=3.0):
    """Horizontal bar, square at the baseline and rounded at the data end."""
    fig = ax.figure
    fig.canvas.draw()
    bb = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    px_x, px_y = bb.width / (x1 - x0), bb.height / abs(y1 - y0)
    h = thick_pt / 72.0 * fig.dpi / px_y
    rx = min(r_pt / 72.0 * fig.dpi / px_x, width / 2)
    ry = min(r_pt / 72.0 * fig.dpi / px_y, h / 2)
    k = 0.5523  # cubic-Bezier quarter-circle constant
    b, t, w = y - h / 2, y + h / 2, width
    verts = [(0, b), (w - rx, b), (w - rx + k * rx, b), (w, b + ry - k * ry), (w, b + ry),
             (w, t - ry), (w, t - ry + k * ry), (w - rx + k * rx, t), (w - rx, t), (0, t),
             (0, b)]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec="none", zorder=3))


def style(ax):
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(AXIS)
        ax.spines[sp].set_linewidth(0.8)
    ax.tick_params(colors=TEXT2, labelsize=8, length=0)


def jitter(n, width=0.22):
    """Deterministic horizontal spread: value-neighbors land in different columns."""
    if n < 5:
        return np.linspace(-width, width, n) if n > 1 else np.zeros(1)
    cols = np.linspace(-width, width, 5)[[2, 0, 4, 1, 3]]
    return cols[np.arange(n) % 5]


def figure(e0, e2, e3, e4, res, path):
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.5, 5.6), dpi=150, facecolor=SURFACE,
        gridspec_kw=dict(width_ratios=[1.3, 1], wspace=0.42))

    # ---- panel 1: per-session drop-to-drop CV, by era --------------------
    style(ax1)
    ax1.set_yscale("log")
    ax1.set_ylim(0.04, 30)
    ax1.set_xlim(-0.6, 4.75)
    eras = [
        ("05-22\nfirst drops\n(bungee, cage)", [e0["drop_cv_pct"]], GRAY),
        ("06-22 – 06-24\nvertex/acrylic,\nclip sweep", [], GRAY),
        ("06-25\ninput–output\n(hot glue, 13 in)",
         [v["t_cv_pct"] for v in e2["sessions"].values()], GRAY),
        ("06-29 – 07-22\nkey-seat + felt,\nauto-drop",
         [s["t_cv_pct"] for s in e3["sessions"]], GRAY),
        (f"{e4['first_date'][5:]} – {e4['last_date'][5:]}\ncurrent SOP\n(PU mat, 60 in)",
         [s["t180_cv_pct"] for s in e4["sessions"].values()], BLUE),
    ]
    for i, (_, vals, col) in enumerate(eras):
        if not vals:
            ax1.text(i, 1.0, "no repeat\ndrops", ha="center", va="center",
                     fontsize=8, color=TEXT2)
            continue
        vals = np.sort(np.asarray(vals))
        ax1.scatter(i + jitter(len(vals)), vals, s=36, c=col, edgecolors=SURFACE,
                    linewidths=1.5, zorder=3)
        med = float(np.median(vals))
        ax1.plot([i - 0.32, i + 0.32], [med, med], color=TEXT, lw=1.5,
                 solid_capstyle="round", zorder=4)
        ax1.text(i + 0.36, med, f"{med:.2g} %" if med < 1 else f"{med:.3g} %",
                 va="center", ha="left", fontsize=9, color=TEXT, zorder=5)
    ax1.set_xticks(range(len(eras)))
    ax1.set_xticklabels([e[0] for e in eras], fontsize=7.6, color=TEXT2)
    ax1.yaxis.set_major_locator(FixedLocator([0.1, 0.3, 1, 3, 10]))
    ax1.yaxis.set_minor_locator(NullLocator())
    ax1.set_yticklabels(["0.1 %", "0.3 %", "1 %", "3 %", "10 %"])
    ax1.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax1.set_ylabel("drop-to-drop CV within a session (log)", fontsize=8.5, color=TEXT2)
    ax1.set_title(f"Per drop: {e0['drop_cv_pct']:.1f} % → {e4['median_t_cv_pct']:.2f} % CV "
                  f"(≈{res['factor_per_drop']:.0f}× more repeatable)",
                  fontsize=10.5, color=TEXT, loc="left", pad=10)
    ax1.text(0, -0.235, "One dot per session; bar = median. 05-22 is the CFC-180 peak of the "
             "impact channel (3 drops, no input\nsensor yet). From 06-25 it is T = output/input. "
             f"Current SOP: {e4['n_sessions']} sessions, {e4['captures']:,} captures.",
             transform=ax1.transAxes, fontsize=7.4, color=TEXT2, va="top")

    # ---- panel 2: design resolution -------------------------------------
    style(ax2)
    m = res["mdd_pct"]
    bars = [
        ("05-22 first drops\n1 article × 3 drops", m["era0_lower_bound"], GRAY, "≥ "),
        ("July key-seat + felt\nsame article, re-tested", m["era3_session"], GRAY, "≈ "),
        ("current SOP\n1 article × 20 drops", m["era4_one_article"], BLUE, ""),
        ("current SOP\n3 prints × 20 drops", m["era4_three_prints"], BLUE, ""),
    ]
    ys = np.arange(len(bars))[::-1].astype(float)
    ax2.set_xlim(0, 32)
    ax2.set_ylim(-0.6, len(bars) - 0.4)
    for y, (_, v, col, pre) in zip(ys, bars):
        rounded_barh(ax2, y, v, col)
        ax2.text(v + 0.6, y, f"{pre}{v:.1f} %", va="center", ha="left",
                 fontsize=9, color=TEXT)
    ax2.set_yticks(ys)
    ax2.set_yticklabels([b[0] for b in bars], fontsize=8, color=TEXT2)
    ax2.xaxis.set_major_locator(FixedLocator([0, 10, 20, 30]))
    ax2.set_xticklabels(["0", "10 %", "20 %", "30 %"])
    ax2.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax2.set_xlabel("smallest difference between two designs that is detected "
                   "(80 % power, α = 0.05)", fontsize=8.5, color=TEXT2)
    ax2.set_title(f"Per design: ≥ {m['era0_lower_bound']:.0f} % → {m['era4_one_article']:.1f} % "
                  f"(≥ {res['factor_design_one_article']:.1f}× finer)",
                  fontsize=10.5, color=TEXT, loc="left", pad=10)
    ax2.text(0, -0.235, "05-22 counts drop noise only, because print and seat noise were never "
             "measured,\nso it is a lower bound. July: 4 same-article re-tests in separate "
             "sessions.\nCurrent: print + seat noise from the 21 healthy round-3 sessions "
             "(sd 0.0087 in T).",
             transform=ax2.transAxes, fontsize=7.4, color=TEXT2, va="top")

    fig.suptitle("How much the drop test has improved since the first drops (05-22 → "
                 f"{e4['last_date'][5:]})", fontsize=12.5, color=TEXT, x=0.125,
                 ha="left", y=1.02)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    e0, e2, e3, e4, tp = era0(), era2(), era3(), era4(), three_print()
    res = resolution(e0, e3, e4, tp)
    era1 = dict(captures=[dict(config=c, valid=v, drops=n) for c, v, n in ERA1_CAPTURES],
                valid=sum(v for _, v, _ in ERA1_CAPTURES),
                drops=sum(n for _, _, n in ERA1_CAPTURES))

    figure(e0, e2, e3, e4, res, os.path.join(OUT, "01_process_improvement.png"))
    out = dict(
        question="PR #86, @ctrhjk 2026-10-10: how much has the test process improved "
                 "since the very first drop test? Give a number.",
        method="Design resolution = (z_0.975 + z_0.80) * sqrt(2) * sigma_design, "
               "sigma_design^2 = sigma_article^2 + sigma_drop^2 / n_drops (one article "
               "per design). Era 0 lacks sigma_article, so its value is a lower bound.",
        era0_first_drops=e0, era1_vertex_acrylic_clip=era1, era2_input_output=e2,
        era3_keyseat_felt=e3, era4_current_sop=e4, era4_three_print=tp, resolution=res,
    )
    with open(os.path.join(OUT, "process_improvement_metrics.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)

    print(f"era 0: audrey CFC-180 {['%.0f' % p for p in e0['audrey_cfc180_g']]} G, "
          f"CV {e0['drop_cv_pct']:.2f} % (95 % CI {e0['drop_cv_ci95_pct'][0]:.1f}-"
          f"{e0['drop_cv_ci95_pct'][1]:.1f} %), raw CV {e0['raw_peak_cv_pct']:.0f} %, "
          f"width CV {e0['width_cv_pct']:.0f} %, PETG/control raw {e0['petg_raw_over_control']:.3f}, "
          f"valid {e0['valid_specimen_drops']}/{e0['specimen_drops']}")
    print(f"era 1: valid {era1['valid']}/{era1['drops']}")
    print(f"era 2: T CV {[round(v['t_cv_pct'], 2) for v in e2['sessions'].values()]}, "
          f"median {e2['median_t_cv_pct']:.2f} %")
    print(f"era 3: {len(e3['sessions'])} sessions, median T CV {e3['median_t_cv_pct']:.2f} %; "
          f"re-tests {[round(p['delta_pct'], 2) for p in e3['retest_pairs']]} %")
    print(f"era 4: {e4['n_sessions']} sessions {e4['first_date']}..{e4['last_date']}, "
          f"valid {e4['valid']}/{e4['captures']}, median T CV {e4['median_t_cv_pct']:.3f} %, "
          f"out CV {e4['median_out_cv_pct']:.2f} %, in CV {e4['median_in_cv_pct']:.2f} %, "
          f"out width CV {e4['median_out_width_cv_pct']:.2f} %, t_imp {e4['t_imp_ms_range']} ms "
          f"(sd {e4['median_t_imp_sd_ms']:.4f}), cadence {e4['median_cadence_s']:.0f} s, "
          f"dv {e4['dv_range_ms']}, CH5 worst {100 * e4['ch5_worst_frac_fs']:.1f} % FS; "
          f"re-seats {[round(p['delta_pct'], 2) for p in e4['retest_pairs']]} %")
    print(f"three-print: sd {tp['resid_sd']} ({tp['article_sd_pct']:.2f} %), flagged "
          f"{tp['n_flagged']} |dev| {[round(x, 1) for x in tp['flagged_abs_dev_pct']]}, "
          f"screened median/max |dev| {tp['screened_median_abs_dev_pct']:.2f}/"
          f"{tp['screened_max_abs_dev_pct']:.2f} %, >2 % flagged "
          f"{tp['n_over_2pct_flagged']}/{tp['n_over_2pct']}")
    print("resolution:", json.dumps({k: (round(v, 3) if isinstance(v, float) else v)
                                     for k, v in res.items() if not isinstance(v, dict)}))
    print("mdd %:", {k: round(v, 2) for k, v in res["mdd_pct"].items()},
          "sigma %:", {k: round(v, 3) for k, v in res["sigma_design_pct"].items()})


if __name__ == "__main__":
    main()
