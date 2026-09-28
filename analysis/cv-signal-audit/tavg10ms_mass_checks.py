"""Is tavg10ms rebound-like, and should it be normalized against mass?

PR #111 (sgbaird, 2026-09-25): "Okay, sure for t180. But what about
tavg10ms, isn't that one a bit closer to the thing we've been calling
rebound energy? In this case, wouldn't it make sense to have some kind of
normalization against mass, since originally we were hoping to print
everything at the exact same mass anyway? It's just that we didn't account
for the infill percentages which led to prints of varying masses."

Parts 1 to 3 use no model and are deterministic.

1. Kinship. What ``tavg10ms`` tracks among the measured quantities
   (t180, ``e_rebound``, ``e_reb_mJ``, ``late_avg3ms_g``, ring-down
   damping), at article, design and within-batch level; where its 10 ms
   window sits relative to the hop landing, drop by drop; and a velocity
   budget: the hop launch speed is ``e_rebound`` times the input
   velocity change by the pipeline's own definition, which bounds how
   much of the 10 ms dose the rebound can account for.
2. Mass anatomy. Where the spread in weighed mass sits (per batch, share
   of the total variance), how far the constant-mass sessions landed from
   their 20.23 g target, and what the infill settings and the shape
   coordinates explain of the within-session misses (article level with
   session offsets, and at design level with the reprint twins averaged
   so a design is counted once).
3. The mass exponent at a fixed design. Dividing by mass assumes an
   objective rises in proportion to mass at a fixed design (exponent 1 in
   logs); leaving it raw assumes 0. The exponent is estimated with batch
   offsets and, in turn, no design controls, the fitted design
   coordinates, the as-printed dimensions, and the design coordinates
   plus infill, with the two high-leverage prints dropped one at a time,
   and from the reprint twins.

Part 4 grades the held-out runs for the payload pair: the committed
shape-only raw run, the committed shape-only per-gram run, and the
shape + infill run written by ``rerun_logocv_shape_infill.py``, using the
same scorecard as ``score_shape_only_per_gram.py`` (imported, not
copied), each run checked against its own archived Ax diagnostics.

Outputs: ``metrics-tavg10ms-mass.json``,
``figures/tavg10ms-mass-question.png``, and a summary on stdout.
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

import score_shape_only_per_gram as ssp

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"
PAYLOAD = HERE.parent / "payload-protection-metrics"
OUT_JSON = HERE / "metrics-tavg10ms-mass.json"

SEED = 20260925
N_PERM = ssp.N_PERM
G = 9.80665
DROP_H_M = 1.524                 # 60 in, DROP_H_M in the campaign script
TARGET_G = 20.23                 # constant-printed-mass target, drran on
WARMUP, TRIGGER_G = 2, 150.0     # campaign SOP, as payload_metric_audit.py
BATCHES = ("seed", "r2d2c", "drran", "2dran", "corny")
CONST_MASS = ("drran", "2dran", "corny")
AS_PRINTED = ("H_mm", "R_mm", "cable_d_mm", "strut_d_mm", "twist_deg")
DESIGN = ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")
INFILL = ("strut_infill_pct", "tpu_infill_pct")
LEVERAGE = ("r2d2c5", "drran7")  # heaviest print; the bubbled-tendon print

RUNS = {
    "shape-only, raw": DATA / "objective-tavg10ms-shape-only",
    "shape-only, per gram": DATA / "objective-payload-per-gram-shape-only",
    "shape + infill, raw": DATA / "objective-tavg10ms-shape-infill",
}
PAYLOAD_OBJ = ("tavg10ms", "late_avg3ms_g")


# ------------------------------------------------------------ data
def build_table() -> pd.DataFrame:
    """One row per fit article: the Section 9 table plus the design
    coordinates and infill the model was fitted on, and the bench's own
    secondary channels."""
    df = pd.read_csv(DATA / "mass-normalized-objectives.csv")
    spec = pd.read_csv(PAYLOAD / "tables" / "specimen_metrics.csv"
                       ).set_index("specimen")
    fitted = {}
    for line in (DATA / "full-nuts-rerun" / "folds.jsonl").read_text().splitlines():
        for art in json.loads(line)["articles"]:
            fitted[art["print_id"]] = art["parameters"]
    fit = pd.DataFrame.from_dict(fitted, orient="index")
    assert len(fit) == 44 and set(fit.index) == set(df.print_id)
    for c in DESIGN + INFILL:
        df[f"design_{c}" if c in DESIGN else c] = df.print_id.map(fit[c])
    # the model's own mass input is the weighed mass used here
    assert np.allclose(df.print_id.map(fit.mass_printed_g), df.mass_g)
    for c in ("zeta_pct", "fn_hz", "t_at_out_avg10_ms", "t_second_ms",
              "in_dv_ms", "in_avg10ms_g", "out_avg10ms_g", "e_rebound"):
        df[c] = df.print_id.map(spec[f"{c}_mean"])
    # e_rebound from the campaign's own e_reb_mJ; the reproduced pipeline
    # agrees with it to 5e-5 mJ
    df["e_rebound_campaign"] = df.e_reb_mJ / (df.mass_g * G * DROP_H_M)
    assert np.allclose(df.e_rebound, df.e_rebound_campaign, rtol=0, atol=2e-7)
    return df.sort_values(["batch", "print_id"]).reset_index(drop=True)


def stabilized_drops(fit_ids) -> pd.DataFrame:
    drops = pd.read_csv(PAYLOAD / "data" / "per-drop-payload-metrics.csv")
    out = []
    for _, g in drops.groupby(["batch", "specimen"], sort=False):
        g = g.sort_values("signal")
        v = g[g.in_raw_g >= TRIGGER_G]
        out.append(v.iloc[WARMUP:] if len(v) > WARMUP + 2 else v)
    st = pd.concat(out, ignore_index=True)
    return st[st.specimen.isin(set(fit_ids))]


# ------------------------------------------------------------ helpers
def perm_spearman(x, y, rng) -> dict:
    rho = float(stats.spearmanr(x, y).statistic)
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    yp = np.stack([rng.permutation(ry) for _ in range(N_PERM)])
    xc = rx - rx.mean()
    yc = yp - yp.mean(axis=1, keepdims=True)
    null = (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    p = float((np.sum(np.abs(null) >= abs(rho) - 1e-12) + 1) / (N_PERM + 1))
    return {"rho": rho, "perm_p": p, "n": int(len(x))}


def ols(y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ beta
    dof = int(len(y) - np.linalg.matrix_rank(X))
    cov = (r @ r / dof) * np.linalg.pinv(X.T @ X)
    return beta, np.sqrt(np.diag(cov)), dof


def batch_dummies(df: pd.DataFrame) -> np.ndarray:
    return pd.get_dummies(df.batch).astype(float).to_numpy()


# ------------------------------------------------------------ part 1
KIN = ("t180", "e_rebound", "e_reb_mJ", "late_avg3ms_g", "zeta_pct")


def part_kinship(df: pd.DataFrame, rng) -> dict:
    out = {"correlations_with_tavg10ms": {}}
    des = df.groupby("design").mean(numeric_only=True)
    for y in KIN:
        within = ssp.within_batch_spearman(df, "tavg10ms", y, rng)
        out["correlations_with_tavg10ms"][y] = {
            "article": perm_spearman(df.tavg10ms, df[y], rng),
            "design_mean": perm_spearman(des.tavg10ms, des[y], rng),
            "within_batch": within,
        }
    # the reference pair: the two campaign objectives against each other
    out["t180_vs_e_rebound_design_mean"] = perm_spearman(des.t180, des.e_rebound, rng)

    # where the 10 ms window sits, drop by drop
    st = stabilized_drops(df.print_id)
    end = st.t_at_out_avg10_ms + 5.0
    has_landing = st.t_second_ms.notna()
    out["window_timing_drops"] = {
        "n_stabilized_drops": int(len(st)),
        "window_center_ms_median": float(st.t_at_out_avg10_ms.median()),
        "window_center_ms_range": [float(st.t_at_out_avg10_ms.min()),
                                   float(st.t_at_out_avg10_ms.max())],
        "window_end_ms_max": float(end.max()),
        "landing_ms_min": float(st.t_second_ms[has_landing].min()),
        "drops_window_closes_before_landing": int((end[has_landing]
                                                   < st.t_second_ms[has_landing]).sum()),
        "drops_with_landing": int(has_landing.sum()),
    }

    # velocity budget, article means
    base_ratio = df.in_avg10ms_g * G * 0.010 / df.in_dv_ms
    launch = df.e_rebound * df.in_dv_ms
    share = df.e_rebound / (df.tavg10ms - 1.0)
    out["velocity_budget"] = {
        "base_10ms_average_over_input_dv_per_10ms": [float(base_ratio.min()),
                                                     float(base_ratio.max())],
        "top_10ms_average_in_m_per_s": [float((df.out_avg10ms_g * G * 0.010).min()),
                                        float((df.out_avg10ms_g * G * 0.010).max())],
        "input_dv_m_per_s": [float(df.in_dv_ms.min()), float(df.in_dv_ms.max())],
        "hop_launch_speed_m_per_s": [float(launch.min()), float(launch.max())],
        "tavg10ms_minus_1": [float((df.tavg10ms - 1).min()),
                             float((df.tavg10ms - 1).max())],
        "hop_share_of_excess_median": float(share.median()),
        "hop_share_of_excess_max": float(share.max()),
        "note": "e_rebound = g t_second / (2 dv_in) is the hop launch speed "
                "over the input velocity change, so even a launch wholly "
                "inside the window moves the top's velocity by e_rebound * "
                "dv_in, i.e. tavg10ms by about e_rebound",
    }
    return out


# ------------------------------------------------------------ part 2
def part_mass_anatomy(df: pd.DataFrame) -> dict:
    m = df.mass_g
    gm = m.mean()
    ss_tot = float(((m - gm) ** 2).sum())
    per = {}
    for b in BATCHES:
        g = df[df.batch == b].mass_g
        ss_dev = float(((g - gm) ** 2).sum())
        per[b] = {"n": int(len(g)), "mean_g": float(g.mean()),
                  "sd_g": float(g.std(ddof=1)),
                  "cv_pct": float(100 * g.std(ddof=1) / g.mean()),
                  "min_g": float(g.min()), "max_g": float(g.max()),
                  "share_of_total_squared_deviation": ss_dev / ss_tot,
                  "infill_pct_values": sorted({*df[df.batch == b].strut_infill_pct,
                                               *df[df.batch == b].tpu_infill_pct})}
    out = {"overall": {"mean_g": float(gm), "sd_g": float(m.std(ddof=1)),
                       "cv_pct": float(100 * m.std(ddof=1) / gm)},
           "per_batch": per,
           "share_seed_plus_r2d2c": per["seed"]["share_of_total_squared_deviation"]
           + per["r2d2c"]["share_of_total_squared_deviation"]}

    c = df[df.batch.isin(CONST_MASS)].copy()
    c["miss_g"] = c.mass_g - TARGET_G
    out["constant_mass_sessions"] = {
        "session_offset_g": c.groupby("batch").miss_g.mean().to_dict(),
        "within_session_sd_g": c.groupby("batch").miss_g.std(ddof=1).to_dict(),
    }

    def explained(frame, cols, dummies):
        """Share of the within-session miss variance explained by cols."""
        y = frame.miss_g.to_numpy()
        X0 = dummies
        r0 = y - X0 @ np.linalg.lstsq(X0, y, rcond=None)[0]
        X1 = np.column_stack([X0, frame[list(cols)].to_numpy(float)])
        b, se, dof = ols(y, X1)
        r1 = y - X1 @ b
        k = len(cols)
        f = ((r0 @ r0 - r1 @ r1) / k) / ((r1 @ r1) / dof)
        return {"share": float(1 - (r1 @ r1) / (r0 @ r0)),
                "F_p": float(stats.f.sf(f, k, dof)), "dof": dof,
                "slopes": {col: [float(b[-k + i]), float(se[-k + i])]
                           for i, col in enumerate(cols)},
                "resid_sd_g": float(np.sqrt(r1 @ r1 / dof))}

    # article level (27 prints, session offsets)
    d_art = batch_dummies(c)
    art = {"infill": explained(c, INFILL, d_art),
           "as_printed_shape": explained(c, AS_PRINTED, d_art),
           "as_printed_shape_plus_infill": explained(c, AS_PRINTED + INFILL, d_art)}
    # design level: each round-3 design once (drran/2dran misses averaged
    # after their session offsets), so a twin pair is not counted twice
    c["miss_c"] = c.miss_g - c.groupby("batch").miss_g.transform("mean")
    dl = c.groupby("design").agg(
        miss_g=("miss_c", "mean"), round=("batch", lambda s: "r4" if "corny" in set(s) else "r3"),
        **{k: (k, "first") for k in INFILL + AS_PRINTED})
    d_des = pd.get_dummies(dl["round"]).astype(float).to_numpy()
    des = {"infill": explained(dl, INFILL, d_des),
           "as_printed_shape": explained(dl, AS_PRINTED, d_des),
           "as_printed_shape_plus_infill": explained(dl, AS_PRINTED + INFILL, d_des),
           "n_designs": int(len(dl))}
    out["constant_mass_sessions"]["article_level"] = art
    out["constant_mass_sessions"]["design_level"] = des
    for lvl in (art, des):  # slopes per 100 percentage points of infill
        for v in lvl.values():
            if isinstance(v, dict) and "slopes" in v:
                for col in INFILL:
                    if col in v["slopes"]:
                        v["slopes"][col] = [100 * x for x in v["slopes"][col]]
    return out


# ------------------------------------------------------------ part 3
EXP_OBJ = ("tavg10ms", "t180", "late_avg3ms_g", "e_rebound", "e_reb_mJ")


def part_exponent(df: pd.DataFrame) -> dict:
    controls = {
        "batch only": (),
        "batch + design coordinates": tuple(f"design_{c}" for c in DESIGN),
        "batch + as-printed dimensions": AS_PRINTED,
        "batch + design coordinates + infill":
            tuple(f"design_{c}" for c in DESIGN) + INFILL,
    }
    out = {}
    for label, cols in controls.items():
        for drop in (None,) + LEVERAGE:
            frame = df if drop is None else df[df.print_id != drop]
            key = label if drop is None else f"{label}, without {drop}"
            ent = {}
            for y in EXP_OBJ:
                X = np.column_stack([batch_dummies(frame)]
                                    + [frame[c].to_numpy(float) for c in cols]
                                    + [np.log(frame.mass_g.to_numpy())])
                b, se, dof = ols(np.log(frame[y].to_numpy()), X)
                t = stats.t.ppf(0.975, dof)
                ent[y] = {
                    "exponent": float(b[-1]), "se": float(se[-1]),
                    "ci95": [float(b[-1] - t * se[-1]), float(b[-1] + t * se[-1])],
                    "p_vs_0": float(2 * stats.t.sf(abs(b[-1] / se[-1]), dof)),
                    "p_vs_1": float(2 * stats.t.sf(abs((b[-1] - 1) / se[-1]), dof)),
                    "dof": dof}
            out[key] = ent
    # reprint twins: same design, same infill, second print session
    tw = []
    for i in range(1, 10):
        a = df.set_index("print_id").loc[f"drran{i}"]
        b = df.set_index("print_id").loc[f"2dran{i}"]
        tw.append({"dln_m": float(np.log(b.mass_g / a.mass_g)),
                   **{y: float(np.log(b[y] / a[y])) for y in EXP_OBJ}})
    tw = pd.DataFrame(tw)
    twins = {"dln_mass_range": [float(tw.dln_m.min()), float(tw.dln_m.max())]}
    for y in EXP_OBJ:
        s = stats.linregress(tw.dln_m, tw[y])
        twins[y] = {"slope": float(s.slope), "se": float(s.stderr),
                    "r": float(s.rvalue)}
    out["reprint twins (slope of dln y on dln m, 9 pairs)"] = twins
    return out


# ------------------------------------------------------------ part 4
def mass_error_given_shape(d: pd.DataFrame, df: pd.DataFrame, rng) -> dict:
    """Mass against the held-out error with batch offsets AND the design
    coordinates held fixed: is a within-session mass trend in the errors
    mass, or the model under-reaching along a coordinate mass tracks?"""
    art = df.set_index("print_id")
    d = d.set_index("print_id")
    cols = [f"design_{c}" for c in DESIGN]
    frame = art.loc[d.index]
    X = np.column_stack([batch_dummies(frame), frame[cols].to_numpy(float)])
    err = (d.observed - d.predicted).to_numpy()
    lm = np.log(frame.mass_g.to_numpy())
    r, p = ssp.perm_r(ssp.residualize(lm, X), ssp.residualize(err, X), rng)
    return {"given_batch_and_design_r": r, "given_batch_and_design_perm_p": p}


def part_heldout(df: pd.DataFrame, rng) -> dict:
    out = {}
    raw_of = df.set_index("print_id")
    for obj in PAYLOAD_OBJ:
        ent = {}
        for label, run in RUNS.items():
            metric = f"{obj}_per_g" if "per gram" in label else obj
            d = ssp.load_run(run, metric, df)
            if d is None:
                ent[label] = None
                continue
            ok = ssp.check_archived(run, metric, d)
            if d.attrs.get("partial"):
                ent[label] = {"partial": True, "n": int(len(d))}
            elif not ok:
                raise RuntimeError(f"{run.name} misses its archived diagnostics")
            d["raw_observed"] = d.print_id.map(raw_of[obj])
            if "per gram" in label:
                graded = {"vs_raw_objective": ssp.grade(
                    d, "raw_observed", "predicted", rng, rank_only=True),
                    "on_target": ssp.grade(d, "observed", "predicted", rng)}
            else:
                graded = {"vs_raw_objective": ssp.grade(d, "observed", "predicted", rng)}
            graded["mass_vs_heldout_error"] = ssp.mass_leverage(d, rng)
            graded["mass_vs_heldout_error"].update(mass_error_given_shape(d, df, rng))
            twins = d[d.print_id.str.match(r"(drran|2dran)\d")].copy()
            twins["n"] = twins.print_id.str[-1]
            gap = twins.groupby("n").predicted.agg(lambda s: s.max() - s.min())
            graded["twin_prediction_gap"] = float(gap.mean())
            graded["archived_diagnostics_match"] = ok
            ent[label] = graded
        out[obj] = ent
    return out


# ------------------------------------------------------------ figure
# run colors: raw and per gram as in the Section 9 and 10 figures, aqua for
# the new run (the three pass the dataviz six checks all-pairs; aqua is
# under 3:1 contrast, so every bar carries its value as a label)
C_RAW, C_PG, C_INF = "#3b6ea5", "#c1553b", "#1baf7a"
# batch colors as in payload_metric_audit.py (Okabe-Ito, fixed order)
BATCH_COLOR = {"seed": "#0072B2", "r2d2c": "#E69F00", "drran": "#009E73",
               "2dran": "#56B4E9", "corny": "#D55E00"}


def make_figure(df, kin, anat, expo, held):
    fig = plt.figure(figsize=(15.5, 9.4))
    gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.30)

    # A: what tavg10ms tracks, design means
    ax = fig.add_subplot(gs[0, 0])
    names = {"t180": "t180", "e_rebound": "rebound\nfraction",
             "e_reb_mJ": "rebound\nenergy (mJ)", "late_avg3ms_g": "hop\nlanding",
             "zeta_pct": "ring-down\ndamping"}
    vals = [kin["correlations_with_tavg10ms"][k]["design_mean"]["rho"] for k in KIN]
    wb = [kin["correlations_with_tavg10ms"][k]["within_batch"]["mean_rho"] for k in KIN]
    x = np.arange(len(KIN))
    ax.bar(x - 0.19, vals, 0.38, color=C_RAW, edgecolor="white", lw=1.5,
           label="design means (n = 35)")
    ax.bar(x + 0.19, wb, 0.38, color="white", edgecolor=C_RAW, hatch="////",
           lw=1.0, label="within batch (mean of 5)")
    for xx, vv in zip(x - 0.19, vals):
        ax.text(xx, vv + (0.03 if vv >= 0 else -0.03), f"{vv:+.2f}", ha="center",
                va="bottom" if vv >= 0 else "top", fontsize=7.5)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x, [names[k] for k in KIN], fontsize=9)
    ax.set_ylim(-1, 1)
    ax.set_ylabel("Spearman rho with tavg10ms")
    ax.set_title("A. What the 10 ms dose ratio moves with", loc="left", fontsize=11)
    ax.legend(fontsize=8, frameon=False, loc="upper right")

    # B: the window vs the hop landing, per article
    ax = fig.add_subplot(gs[0, 1])
    order = df.sort_values("t_second_ms").reset_index(drop=True)
    y = np.arange(len(order))
    ax.hlines(y, order.t_at_out_avg10_ms - 5, order.t_at_out_avg10_ms + 5,
              color=C_RAW, lw=2.2, label="max 10 ms window")
    ax.scatter(order.t_second_ms, y, s=16, color="#222222", zorder=3,
               label="hop landing")
    ax.set_yticks([])
    ax.set_xlabel("time after impact (ms)")
    ax.set_ylabel("44 fit articles (means), by landing time")
    t = kin["window_timing_drops"]
    ax.set_title("B. The window closes before the rebound lands", loc="left", fontsize=11)
    ax.text(0.98, 0.04, f"{t['drops_window_closes_before_landing']} of "
            f"{t['drops_with_landing']} drops: window ends first",
            transform=ax.transAxes, ha="right", fontsize=8.5, color="#444")
    ax.legend(fontsize=8, frameon=False, loc="upper left",
              bbox_to_anchor=(0.2, 1.0))

    # C: weighed mass by batch
    ax = fig.add_subplot(gs[0, 2])
    for i, b in enumerate(BATCHES):
        g = df[df.batch == b]
        jitter = (np.arange(len(g)) - (len(g) - 1) / 2) * 0.06
        ax.scatter(i + jitter, g.mass_g, s=22, color=BATCH_COLOR[b], zorder=3)
        share = anat["per_batch"][b]["share_of_total_squared_deviation"]
        ax.text(i, 23.9, f"{100 * share:.0f}%", ha="center", fontsize=8.5, color="#444")
    ax.axhline(TARGET_G, color="k", lw=0.8, ls="--")
    ax.text(1.0, TARGET_G + 0.08, "20.23 g target", ha="center", va="bottom",
            fontsize=8)
    ax.axvspan(-0.5, 1.5, color="#eeeeee", zorder=0)
    ax.text(0.5, 16.75, "constant solid mass,\nall at 15% infill", ha="center",
            va="bottom", fontsize=8, color="#444")
    ax.text(3.0, 16.75, "constant printed mass,\ninfill in the mass model",
            ha="center", va="bottom", fontsize=8, color="#444")
    ax.set_xticks(range(len(BATCHES)), BATCHES)
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(16.6, 24.2)
    ax.set_ylabel("weighed mass (g)")
    ax.set_title("C. Where the mass spread is (share of variance)", loc="left",
                 fontsize=11)

    # D: exponent estimates for tavg10ms
    ax = fig.add_subplot(gs[1, 0])
    keys = ["batch only", "batch + design coordinates",
            "batch + as-printed dimensions", "batch + design coordinates + infill",
            "batch + as-printed dimensions, without drran7",
            "batch + as-printed dimensions, without r2d2c5"]
    short = ["batch offsets only", "+ design coordinates", "+ as-printed dimensions",
             "+ design coordinates + infill", "as-printed, without drran7",
             "as-printed, without r2d2c5"]
    for i, k in enumerate(keys):
        e = expo[k]["tavg10ms"]
        ax.errorbar(e["exponent"], i, xerr=[[e["exponent"] - e["ci95"][0]],
                                            [e["ci95"][1] - e["exponent"]]],
                    fmt="o", ms=7, color=C_RAW if i else "#8a8a8a", capsize=3)
    ax.axvline(0, color="k", lw=0.8)
    ax.axvline(1, color=C_PG, lw=1.2, ls="--")
    ax.set_yticks(range(len(keys)), short, fontsize=8.5)
    ax.set_ylim(len(keys) - 0.5, -1.1)
    ax.text(1.06, -0.75, "dividing by mass\nassumes 1", color="#444",
            fontsize=8, va="center")
    ax.text(-0.06, -0.75, "raw\nassumes 0", color="#444", fontsize=8,
            va="center", ha="right")
    ax.set_xlabel("d ln(tavg10ms) / d ln(mass), 95% CI")
    ax.set_title("D. The data cannot tell 0 from 1", loc="left", fontsize=11)

    # E, F: held out
    for j, obj in enumerate(PAYLOAD_OBJ):
        ax = fig.add_subplot(gs[1, 1 + j])
        labels = [lab for lab in RUNS if held[obj].get(lab)]
        stats_ = [("article", lambda g: g["vs_raw_objective"]["spearman_rho"]),
                  ("design mean", lambda g: g["vs_raw_objective"]["design_level"]["spearman_rho"]),
                  ("within batch", lambda g: g["vs_raw_objective"]["within_batch"]["mean_rho"])]
        width = 0.8 / max(len(labels), 1)
        colors = {"shape-only, raw": C_RAW, "shape-only, per gram": C_PG,
                  "shape + infill, raw": C_INF}
        for i, lab in enumerate(labels):
            g = held[obj][lab]
            v = [f(g) for _, f in stats_]
            xs = np.arange(len(stats_)) - 0.4 + width * (i + 0.5)
            ax.bar(xs, v, width, color=colors[lab], edgecolor="white", lw=1.5,
                   label=lab)
            for xx, vv in zip(xs, v):
                ax.text(xx, vv + 0.02, f"{vv:+.2f}", ha="center", va="bottom",
                        fontsize=7.5, rotation=90)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(range(len(stats_)), [s for s, _ in stats_])
        ax.set_ylim(-0.2, 1.0)
        ax.set_ylabel("held-out Spearman rho vs the raw objective")
        ttl = {"tavg10ms": "E. tavg10ms, held out (LOGO, 35 folds)",
               "late_avg3ms_g": "F. Hop landing, held out"}[obj]
        ax.set_title(ttl, loc="left", fontsize=11)
        if j == 0:
            ax.legend(fontsize=8, frameon=False, loc="upper left")
    fig.savefig(FIGS / "tavg10ms-mass-question.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ main
def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def main() -> int:
    rng = np.random.default_rng(SEED)
    df = build_table()
    kin = part_kinship(df, rng)
    anat = part_mass_anatomy(df)
    expo = part_exponent(df)
    held = part_heldout(df, rng)
    res = {"n_articles": int(len(df)), "n_perm": N_PERM, "seed": SEED,
           "kinship": kin, "mass_anatomy": anat, "mass_exponent": expo,
           "heldout_payload_pair": held}
    OUT_JSON.write_text(json.dumps(_jsonable(res), indent=2) + "\n")
    make_figure(df, kin, anat, expo, held)

    c = kin["correlations_with_tavg10ms"]
    print("tavg10ms vs:")
    for k in KIN:
        print(f"  {k:14s} article {c[k]['article']['rho']:+.2f} "
              f"(p {c[k]['article']['perm_p']:.3g})  design {c[k]['design_mean']['rho']:+.2f} "
              f"(p {c[k]['design_mean']['perm_p']:.3g})  within {c[k]['within_batch']['mean_rho']:+.2f} "
              f"(p {c[k]['within_batch']['perm_p']:.3g})")
    print("window timing:", kin["window_timing_drops"])
    print("velocity budget:", {k: v for k, v in kin["velocity_budget"].items() if k != "note"})
    print("mass shares:", {b: round(v["share_of_total_squared_deviation"], 3)
                           for b, v in anat["per_batch"].items()},
          "seed+r2d2c", round(anat["share_seed_plus_r2d2c"], 3))
    cm = anat["constant_mass_sessions"]
    print("constant-mass offsets:", {k: round(v, 3) for k, v in cm["session_offset_g"].items()},
          "within sd", {k: round(v, 3) for k, v in cm["within_session_sd_g"].items()})
    for lvl in ("article_level", "design_level"):
        L = cm[lvl]
        print(f"  {lvl}: infill {L['infill']['share']:.2f} (F p {L['infill']['F_p']:.3g}; "
              f"slopes {L['infill']['slopes']}), shape {L['as_printed_shape']['share']:.2f}, "
              f"shape+infill {L['as_printed_shape_plus_infill']['share']:.2f}")
    for k, ent in expo.items():
        if k.startswith("reprint"):
            print(k, {y: (round(v['slope'], 1), round(v['se'], 1)) if isinstance(v, dict) else v
                      for y, v in ent.items()})
            continue
        e = ent["tavg10ms"]
        print(f"  exponent tavg10ms [{k}]: {e['exponent']:+.2f} "
              f"({e['ci95'][0]:+.2f} to {e['ci95'][1]:+.2f}; p0 {e['p_vs_0']:.2f}, p1 {e['p_vs_1']:.2g})")
    for obj in PAYLOAD_OBJ:
        for lab, g in held[obj].items():
            if not g or g.get("partial"):
                print(obj, lab, g)
                continue
            v = g["vs_raw_objective"]
            print(f"{obj:14s} {lab:22s} article {v['spearman_rho']:+.2f} (p {v['spearman_p_perm']:.3g})"
                  f"  design {v['design_level']['spearman_rho']:+.2f}"
                  f"  within {v['within_batch']['mean_rho']:+.2f} (p {v['within_batch']['perm_p']:.3g})"
                  f"  mass-err pooled {g['mass_vs_heldout_error']['pooled_r']:+.2f}"
                  f" within {g['mass_vs_heldout_error']['within_batch_r']:+.2f}"
                  f" (p {g['mass_vs_heldout_error']['within_batch_perm_p']:.3g})"
                  f"  twin gap {g['twin_prediction_gap']:.3f}"
                  + (f"  R2oos {v['R2_oos_vs_fold_train_mean']:+.2f} cov95 {v['coverage_95_pct']:.0f}%"
                     if 'R2_oos_vs_fold_train_mean' in v else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
