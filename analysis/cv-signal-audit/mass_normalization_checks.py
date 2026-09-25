"""Do mass-normalized objectives remove mass's predictive power?

PR #111 follow-up (sgbaird, 2026-09-25): "just divide each of the
objectives by mass and run some simple checks".

This is that test, run directly on the committed campaign record rather
than argued about. For each of the four objectives audited on this branch
it builds three framings and measures how much of each one mass can
explain:

* ``raw``       -- the objective as the campaign ingested it
* ``per_gram``  -- the objective divided by the article's weighed mass
                   (the literal ask)
* ``resid``     -- the objective with an ordinary least-squares fit on
                   mass subtracted, which zeroes the mass correlation by
                   construction and is the version of the same idea that
                   is guaranteed to work

The checks are deliberately simple and all of them are cheap:

1. mass leverage: Pearson r and Spearman rho of weighed mass against
   each framing, article level (n=44) and design level (n=35), with
   permutation p-values;
2. the arithmetic behind whatever check 1 finds: coefficient of
   variation of mass against the coefficient of variation of each
   objective, and the correlation a pure 1/m division predicts;
3. reprint-twin reliability: the nine drran/2dran pairs, which are the
   same design printed twice, scored on each framing;
4. rank agreement between framings at design level, plus the top-5
   design lists each framing would hand the optimizer;
5. design-signal retention: correlation of each framing with the five
   shape coordinates;
6. mass's predictive power measured the way the audit measures everything
   else: leave-one-design-out, predicting each held-out article from its
   weighed mass alone;
7. where mass's leverage actually lives: within the nine reprint pairs
   (same design, two prints) and within each print session.

Usage (repo root)::

    python analysis/cv-signal-audit/mass_normalization_checks.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

AUDIT = Path(__file__).resolve().parent
DATA = AUDIT / "data"
FIGS = AUDIT / "figures"
OUT_JSON = AUDIT / "metrics-mass-normalization.json"
OUT_TABLE = DATA / "mass-normalized-objectives.csv"

LOGO_CSV = DATA / "full-nuts-rerun" / "t3-prism-bo-round5-logocv.csv"
PAYLOAD_CSV = DATA / "payload-objectives.csv"
DROP_FILES = (
    "t3-prism-bo-batch-drop-results.csv",
    "t3-prism-bo-round1-drop-results.csv",
    "t3-prism-bo-round3-drop-results.csv",
    "t3-prism-bo-round3-reprint-drop-results.csv",
    "t3-prism-bo-round4-drop-results.csv",
)
COORDS = ("H_mm", "R_mm", "cable_d_mm", "strut_d_mm", "twist_deg")
OBJECTIVES = ("t180", "e_reb_mJ", "tavg10ms", "late_avg3ms_g")
FRAMINGS = ("raw", "per_gram", "resid")
N_PERM = 20_000
RNG_SEED = 20260925


# ---------------------------------------------------------------- helpers
def perm_p(x, y, statistic="spearman", n=N_PERM, seed=RNG_SEED):
    """Two-sided permutation p for a correlation, shuffling y."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    fn = stats.spearmanr if statistic == "spearman" else stats.pearsonr
    obs = float(fn(x, y)[0])
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n):
        if abs(float(fn(x, rng.permutation(y))[0])) >= abs(obs) - 1e-12:
            hits += 1
    return obs, (hits + 1) / (n + 1)


def corr_block(x, y, seed=RNG_SEED):
    r, p_r = perm_p(x, y, "pearson", seed=seed)
    rho, p_rho = perm_p(x, y, "spearman", seed=seed + 1)
    return {"pearson_r": r, "pearson_p": p_r, "spearman_rho": rho,
            "spearman_p": p_rho, "n": int(len(x))}


def cv(v):
    v = np.asarray(v, dtype=float)
    return float(np.std(v, ddof=1) / np.mean(v))


# ------------------------------------------------------------ article table
def build_table() -> pd.DataFrame:
    """One row per fit article: mass, coordinates, four objectives."""
    drops = pd.concat(
        [pd.read_csv(DATA / f) for f in DROP_FILES], ignore_index=True
    ).set_index("specimen")

    logo = pd.read_csv(LOGO_CSV)
    wide = logo.pivot_table(index="print_id", columns="metric",
                            values="observed", aggfunc="first")
    wide_sem = logo.pivot_table(index="print_id", columns="metric",
                                values="observed_sem", aggfunc="first")
    payload = pd.read_csv(PAYLOAD_CSV).set_index("print_id")

    keys = pd.concat(
        pd.read_csv(DATA / f"t3-prism-bo-{r}-print-key.csv")[["print_id", "source_trial"]]
        for r in ("round1", "round3", "round4")
    )
    trial_of = dict(zip(keys.print_id, keys.source_trial))

    rows = []
    for pid in wide.index:                      # the 44 articles the model fit
        rows.append({
            "print_id": pid,
            "batch": payload.loc[pid, "batch"],
            "design": f"trial{trial_of[pid]}" if pid in trial_of else pid,
            "mass_g": float(drops.loc[pid, "mass_g"]),
            "t180": float(wide.loc[pid, "t180"]),
            "e_reb_mJ": float(wide.loc[pid, "e_reb_mJ"]),
            "tavg10ms": float(payload.loc[pid, "tavg10ms_mean"]),
            "late_avg3ms_g": float(payload.loc[pid, "late_avg3ms_g_mean"]),
            "t180_sem": float(wide_sem.loc[pid, "t180"]),
            "e_reb_mJ_sem": float(wide_sem.loc[pid, "e_reb_mJ"]),
            "tavg10ms_sem": float(payload.loc[pid, "tavg10ms_sem"]),
            "late_avg3ms_g_sem": float(payload.loc[pid, "late_avg3ms_g_sem"]),
            **{c: float(drops.loc[pid, c]) for c in COORDS},
        })
    df = pd.DataFrame(rows).sort_values(["batch", "print_id"]).reset_index(drop=True)
    assert len(df) == 44, len(df)
    assert df[list(OBJECTIVES) + ["mass_g"]].notna().all().all()

    for obj in OBJECTIVES:
        df[f"{obj}__raw"] = df[obj]
        df[f"{obj}__raw_sem"] = df[f"{obj}_sem"]
        # the weighed mass is a direct scale reading, far more precise than
        # the drop-to-drop scatter, so it is propagated as exact: the SEM of
        # Y/m is just SEM(Y)/m
        df[f"{obj}__per_gram"] = df[obj] / df["mass_g"]
        df[f"{obj}__per_gram_sem"] = df[f"{obj}_sem"] / df["mass_g"]
        slope, icept = np.polyfit(df["mass_g"], df[obj], 1)
        df[f"{obj}__resid"] = df[obj] - (slope * df["mass_g"] + icept)
        # subtracting a line fitted across articles leaves each article's own
        # measurement noise untouched to first order
        df[f"{obj}__resid_sem"] = df[f"{obj}_sem"]
        df[f"{obj}__resid_offset"] = slope * df["mass_g"] + icept
    return df


# ------------------------------------------------------------------- checks
def check_mass_leverage(df) -> dict:
    """How much of each framing can the article's own weighed mass explain?"""
    designs = df.groupby("design").agg(
        {**{f"{o}__{f}": "mean" for o in OBJECTIVES for f in FRAMINGS},
         "mass_g": "mean"})
    out = {"article_n44": {}, "design_n35": {}}
    for obj in OBJECTIVES:
        for fr in FRAMINGS:
            col = f"{obj}__{fr}"
            out["article_n44"].setdefault(obj, {})[fr] = corr_block(
                df["mass_g"], df[col])
            out["design_n35"].setdefault(obj, {})[fr] = corr_block(
                designs["mass_g"], designs[col])
    return out


def check_arithmetic(df) -> dict:
    """Why check 1 comes out the way it does: relative spreads.

    For Z = Y/m with Y statistically independent of m, working in logs
    gives corr(log m, log Z) = -sd(log m)/hypot(sd(log Y), sd(log m)),
    so division *creates* a mass correlation whenever the objective does
    not already carry a factor of m. The measured value is reported next
    to that prediction.
    """
    lm = np.log(df["mass_g"].to_numpy())
    out = {"cv_mass_pct": 100 * cv(df["mass_g"]),
           "sd_log_mass": float(np.std(lm, ddof=1)), "objectives": {}}
    for obj in OBJECTIVES:
        y = df[obj].to_numpy()
        ly = np.log(y)
        sd_ly, sd_lm = float(np.std(ly, ddof=1)), out["sd_log_mass"]
        out["objectives"][obj] = {
            "cv_pct": 100 * cv(y),
            "sd_log": sd_ly,
            "predicted_r_log_if_independent": -sd_lm / float(np.hypot(sd_ly, sd_lm)),
            "measured_r_log_per_gram": float(stats.pearsonr(lm, ly - lm)[0]),
            "measured_r_log_raw": float(stats.pearsonr(lm, ly)[0]),
        }
    return out


def check_reprint_reliability(df) -> dict:
    """The nine drran/2dran twins: same design, printed twice.

    ``pair_rank_corr`` is the Spearman correlation between the first and
    second print's values over the nine designs (the campaign's own
    reprint-reliability statistic); ``icc_like`` is the fraction of total
    variance that sits between designs rather than between prints of the
    same design.
    """
    twins = df[df.batch.isin(["drran", "2dran"])].copy()
    twins["n"] = twins.print_id.str.extract(r"(\d)$")[0].astype(int)
    out = {}
    for obj in OBJECTIVES:
        for fr in FRAMINGS:
            col = f"{obj}__{fr}"
            a = twins[twins.batch == "drran"].set_index("n")[col].sort_index()
            b = twins[twins.batch == "2dran"].set_index("n")[col].sort_index()
            assert list(a.index) == list(b.index) == list(range(1, 10))
            rho, p = perm_p(a.to_numpy(), b.to_numpy(), "spearman", n=5000)
            within = float(np.mean((a.to_numpy() - b.to_numpy()) ** 2) / 2)
            pair_means = (a.to_numpy() + b.to_numpy()) / 2
            between = float(np.var(pair_means, ddof=1))
            out.setdefault(obj, {})[fr] = {
                "pair_rank_corr": rho, "pair_rank_p": p,
                "within_pair_var": within, "between_design_var": between,
                "icc_like": (between - within / 2) / (between + within / 2)
                if (between + within / 2) > 0 else float("nan"),
            }
    return out


def check_rank_agreement(df) -> dict:
    """Does normalization actually reorder the designs, and how?"""
    designs = df.groupby("design").agg(
        {f"{o}__{f}": "mean" for o in OBJECTIVES for f in FRAMINGS})
    label = df.drop_duplicates("design").set_index("design").print_id
    out = {}
    for obj in OBJECTIVES:
        raw = designs[f"{obj}__raw"]
        ent = {"spearman_raw_vs_per_gram":
               float(stats.spearmanr(raw, designs[f"{obj}__per_gram"]).statistic),
               "spearman_raw_vs_resid":
               float(stats.spearmanr(raw, designs[f"{obj}__resid"]).statistic)}
        for fr in FRAMINGS:
            best = designs[f"{obj}__{fr}"].nsmallest(5).index
            ent[f"top5_lowest_{fr}"] = [str(label[d]) for d in best]
        out[obj] = ent
    return out


def check_design_signal(df) -> dict:
    """Does normalization strengthen or weaken the real geometry signal?"""
    out = {}
    for obj in OBJECTIVES:
        for fr in FRAMINGS:
            col = f"{obj}__{fr}"
            ent = {c: float(stats.spearmanr(df[c], df[col]).statistic)
                   for c in COORDS}
            ent["max_abs_coord_rho"] = max(abs(v) for v in ent.values())
            # within-batch: strips the per-session offsets out
            per_batch = [
                float(stats.spearmanr(g[c], g[col]).statistic)
                for c in COORDS
                for _, g in df.groupby("batch") if g[c].nunique() > 2
            ]
            ent["mean_abs_within_batch_coord_rho"] = float(
                np.mean(np.abs(per_batch)))
            out.setdefault(obj, {})[fr] = ent
    return out



def _logo_mass_only(mass, y, design, resid_in_fold):
    """Held-out predictions of y from mass alone, on the audit's folds.

    ``resid_in_fold`` residualizes inside each fold (the line is fitted on
    the training articles only) so the transform never sees the held-out
    article, which is what makes the number honest.
    """
    pred = np.full(len(y), np.nan)
    obs = np.asarray(y, dtype=float).copy()
    for d in dict.fromkeys(design):
        test = np.asarray([x == d for x in design])
        m_tr, y_tr = mass[~test], obs[~test]
        if resid_in_fold:
            sl, ic = np.polyfit(m_tr, y_tr, 1)
            y_tr = y_tr - (sl * m_tr + ic)
            obs_test = obs[test] - (sl * mass[test] + ic)
        else:
            obs_test = obs[test]
        sl2, ic2 = np.polyfit(m_tr, y_tr, 1)
        pred[test] = sl2 * mass[test] + ic2
        obs[test] = obs_test
    return pred, obs


def check_mass_alone_skill(df, n_null=1000) -> dict:
    """Mass's predictive power, scored the way the audit scores the surrogate.

    Leave-one-design-out (reprint twins held out together, exactly the
    audit's folds), refitting an ordinary least-squares line on mass for
    every fold and predicting the held-out article(s): "how well can you
    rank these articles knowing nothing but what they weigh".

    Refitting a line inside every fold is itself biased when the predictor
    carries no signal (dropping an article tilts the line away from it, so
    a useless predictor scores *negative* rather than zero), so the null is
    generated by the same procedure with mass shuffled between articles
    rather than assumed to be zero. ``excess_over_null`` is the number that
    matters; the raw statistic on its own is not interpretable.

    The ``resid`` framing is residualized inside each fold here, unlike the
    committed column, which is fitted on all 44 articles and is only used
    for the pooled checks.
    """
    rng = np.random.default_rng(RNG_SEED + 7)
    mass = df["mass_g"].to_numpy()
    design = list(df.design)
    out = {}
    for obj in OBJECTIVES:
        for fr in FRAMINGS:
            col = f"{obj}__{fr}" if fr != "resid" else f"{obj}__raw"
            y = df[col].to_numpy()
            pred, obs = _logo_mass_only(mass, y, design, fr == "resid")
            rho = float(stats.spearmanr(pred, obs).statistic)
            ss_res = float(np.sum((obs - pred) ** 2))
            ss_tot = float(np.sum((obs - obs.mean()) ** 2))
            null = np.empty(n_null)
            for i in range(n_null):
                pm = rng.permutation(mass)
                pp, oo = _logo_mass_only(pm, y, design, fr == "resid")
                null[i] = stats.spearmanr(pp, oo).statistic
            p = (np.sum(np.abs(null - null.mean()) >= abs(rho - null.mean())) + 1) \
                / (n_null + 1)
            out.setdefault(obj, {})[fr] = {
                "heldout_spearman": rho,
                "null_mean_spearman": float(null.mean()),
                "null_sd_spearman": float(null.std(ddof=1)),
                "excess_over_null": rho - float(null.mean()),
                "p_vs_null": float(p),
                "heldout_r2_vs_pooled_mean": 1 - ss_res / ss_tot,
            }
    return out


def check_print_session_confound(df) -> dict:
    """Where mass's leverage lives: within reprint pairs, within sessions.

    The pooled mass/objective correlation can be flat while mass still
    tracks the objective *inside* a print session, which is the structure
    Section 6 identified (every 2dran article weighed more than its drran
    twin and read t180 higher). Division by mass attacks exactly that
    component, so it is measured separately from the pooled one.
    """
    twins = df[df.batch.isin(["drran", "2dran"])].copy()
    twins["n"] = twins.print_id.str.extract(r"(\d)$")[0].astype(int)
    a = twins[twins.batch == "drran"].set_index("n").sort_index()
    b = twins[twins.batch == "2dran"].set_index("n").sort_index()
    d_mass = (b["mass_g"] - a["mass_g"]).to_numpy()

    out = {"twin_pairs": {"n_pairs": int(len(d_mass)),
                          "delta_mass_g_mean": float(d_mass.mean()),
                          "delta_mass_g_min": float(d_mass.min()),
                          "delta_mass_g_max": float(d_mass.max()),
                          "all_second_print_heavier": bool((d_mass > 0).all()),
                          "objectives": {}},
           "within_batch": {}}
    for obj in OBJECTIVES:
        d_obj = (b[obj] - a[obj]).to_numpy()
        r = float(stats.pearsonr(d_mass, d_obj)[0])
        slope = float(np.polyfit(d_mass, d_obj, 1)[0])
        out["twin_pairs"]["objectives"][obj] = {
            "pearson_r_delta_mass_vs_delta_obj": r,
            "slope_per_gram": slope,
            "implied_pooled_slope": float(np.polyfit(df["mass_g"], df[obj], 1)[0]),
            "mean_abs_delta_obj": float(np.mean(np.abs(d_obj))),
        }
    for obj in OBJECTIVES:
        for fr in FRAMINGS:
            col = f"{obj}__{fr}"
            per = [float(stats.pearsonr(g["mass_g"], g[col])[0])
                   for _, g in df.groupby("batch") if len(g) >= 5]
            out["within_batch"].setdefault(obj, {})[fr] = {
                "per_batch_r": per, "mean_r": float(np.mean(per)),
                "mean_abs_r": float(np.mean(np.abs(per))),
            }
    return out


# ------------------------------------------------------------------- figure
def make_figure(df, leverage, arith, reliab, alone, confound):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(17.5, 9.8))
    colors = {"raw": "#3b6ea5", "per_gram": "#c1553b", "resid": "#4b8a5a"}
    nice = {"raw": "raw objective", "per_gram": "divided by mass",
            "resid": "mass regressed out"}
    objlab = {"t180": "t180", "e_reb_mJ": "rebound\n(mJ)",
              "tavg10ms": "tavg10ms", "late_avg3ms_g": "late\navg3ms"}
    w, xs = 0.26, np.arange(len(OBJECTIVES))

    def grouped(ax, getter, star=None, ylabel="", title="", ylim=(-1, 1)):
        for i, fr in enumerate(FRAMINGS):
            vals = [getter(o, fr) for o in OBJECTIVES]
            bars = ax.bar(xs + (i - 1) * w, vals, w, label=nice[fr],
                          color=colors[fr])
            if star is not None:
                for b, v, o in zip(bars, vals, OBJECTIVES):
                    if star(o, fr):
                        ax.text(b.get_x() + b.get_width() / 2,
                                v + (0.05 if v >= 0 else -0.11), "*",
                                ha="center", fontsize=14, color=colors[fr])
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(xs)
        ax.set_xticklabels([objlab[o] for o in OBJECTIVES], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9.5)
        ax.set_title(title, fontsize=10.5)
        ax.set_ylim(*ylim)

    # A: pooled mass leverage
    grouped(axes[0, 0],
            lambda o, fr: leverage["article_n44"][o][fr]["pearson_r"],
            lambda o, fr: leverage["article_n44"][o][fr]["pearson_p"] < 0.05,
            "Pearson r, mass vs objective",
            "A. Pooled: what mass explains after each\ntransform (n=44). * = permutation p < 0.05")
    axes[0, 0].legend(fontsize=8.5, loc="lower left")

    # B: within-session mass leverage, the part division does fix
    grouped(axes[0, 1],
            lambda o, fr: confound["within_batch"][o][fr]["mean_r"], None,
            "mean within-batch Pearson r",
            "B. Within a print session: division does\nremove t180's mass leverage (+0.42 to -0.10)")

    # C: held-out skill of mass alone
    grouped(axes[0, 2],
            lambda o, fr: alone[o][fr]["excess_over_null"],
            lambda o, fr: alone[o][fr]["p_vs_null"] < 0.05,
            "held-out rank skill above shuffled-mass null",
            "C. Mass alone, on the audit's own folds.\nDividing t180 by mass CREATES the skill")
    axes[0, 2].legend(fontsize=8.5, loc="lower left")

    # D: the arithmetic
    ax = axes[1, 0]
    pred = [arith["objectives"][o]["predicted_r_log_if_independent"]
            for o in OBJECTIVES]
    meas = [arith["objectives"][o]["measured_r_log_per_gram"] for o in OBJECTIVES]
    ax.scatter(pred, meas, s=95, c=colors["per_gram"], zorder=3)
    for pv, mv, o in zip(pred, meas, OBJECTIVES):
        ax.annotate(objlab[o].replace("\n", " "), (pv, mv),
                    textcoords="offset points", xytext=(8, 4), fontsize=9)
    lo = min(min(pred), min(meas)) - 0.1
    ax.plot([lo, 0.12], [lo, 0.12], "k--", lw=1, zorder=1)
    ax.set_xlabel("r predicted by arithmetic alone:\n"
                  r"$-\,sd(\log m)\,/\,\sqrt{sd(\log Y)^2 + sd(\log m)^2}$",
                  fontsize=9)
    ax.set_ylabel(r"measured $r(\log m,\ \log(Y/m))$", fontsize=9.5)
    ax.set_title("D. The injected correlation is the 1/m gradient,\n"
                 "not physics: it tracks the spread ratio", fontsize=10.5)
    ax.grid(alpha=0.3)

    # E: reprint reliability
    grouped(axes[1, 1],
            lambda o, fr: reliab[o][fr]["pair_rank_corr"], None,
            "reprint pair rank correlation (9 designs)",
            "E. Print-to-print reliability: the ceiling on\nany held-out skill. t180 improves, others do not")

    # F: the concrete picture
    ax = axes[1, 2]
    m = df["mass_g"].to_numpy()
    for fr, marker in (("raw", "o"), ("per_gram", "s")):
        y = df[f"t180__{fr}"].to_numpy()
        z = (y - y.mean()) / y.std(ddof=1)
        r = float(stats.pearsonr(m, y)[0])
        ax.scatter(m, z, s=40, marker=marker, alpha=0.8, color=colors[fr],
                   label=f"t180 {nice[fr]} (r = {r:+.2f})")
        b, a_ = np.polyfit(m, z, 1)
        xx = np.linspace(m.min(), m.max(), 20)
        ax.plot(xx, b * xx + a_, color=colors[fr], lw=1.8)
    ax.set_xlabel("weighed printed mass (g)", fontsize=9.5)
    ax.set_ylabel("objective, standardized", fontsize=9.5)
    ax.set_title("F. t180 is uncorrelated with mass\nuntil you divide by it",
                 fontsize=10.5)
    ax.legend(fontsize=8.5)
    ax.grid(alpha=0.3)

    fig.suptitle("Dividing the objectives by mass: what it actually does to "
                 "mass's predictive power (44 articles, 35 designs)",
                 fontsize=13.5, y=0.985)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    out = FIGS / "mass-normalization-checks.png"
    fig.savefig(out, dpi=150)
    print(f"-> {out}")


def main():
    df = build_table()
    OUT_TABLE.write_text(df.to_csv(index=False, float_format="%.6g"))
    print(f"-> {OUT_TABLE} ({len(df)} articles)")

    leverage = check_mass_leverage(df)
    arith = check_arithmetic(df)
    reliab = check_reprint_reliability(df)
    ranks = check_rank_agreement(df)
    signal = check_design_signal(df)
    alone = check_mass_alone_skill(df)
    confound = check_print_session_confound(df)

    metrics = {
        "provenance": {
            "generated_by": "analysis/cv-signal-audit/mass_normalization_checks.py",
            "question": "PR #111, sgbaird 2026-09-25: divide each objective by "
                        "mass and check whether mass keeps predictive power",
            "n_articles": int(len(df)),
            "n_designs": int(df.design.nunique()),
            "n_permutations": N_PERM,
            "seed": RNG_SEED,
        },
        "check1_mass_leverage": leverage,
        "check2_arithmetic": arith,
        "check3_reprint_reliability": reliab,
        "check4_rank_agreement": ranks,
        "check5_design_signal": signal,
        "check6_mass_alone_heldout_skill": alone,
        "check7_print_session_confound": confound,
    }
    OUT_JSON.write_text(json.dumps(metrics, indent=2))
    print(f"-> {OUT_JSON}")

    make_figure(df, leverage, arith, reliab, alone, confound)

    # ---- console summary -------------------------------------------------
    print("\n=== CHECK 1: Pearson r of weighed mass vs objective (n=44) ===")
    print(f"{'objective':>16} | {'raw':>16} | {'/ mass':>16} | {'resid':>16}")
    for o in OBJECTIVES:
        cells = []
        for fr in FRAMINGS:
            e = leverage["article_n44"][o][fr]
            cells.append(f"{e['pearson_r']:+.2f} (p {e['pearson_p']:.3f})")
        print(f"{o:>16} | {cells[0]:>16} | {cells[1]:>16} | {cells[2]:>16}")

    print("\n=== CHECK 2: relative spreads and the predicted injection ===")
    print(f"mass CV = {arith['cv_mass_pct']:.1f}%")
    for o in OBJECTIVES:
        e = arith["objectives"][o]
        print(f"{o:>16}: CV {e['cv_pct']:5.1f}%  "
              f"predicted r(log m, log Y/m) {e['predicted_r_log_if_independent']:+.2f}  "
              f"measured {e['measured_r_log_per_gram']:+.2f}")

    print("\n=== CHECK 3: reprint pair rank correlation (9 twin designs) ===")
    for o in OBJECTIVES:
        cells = [f"{reliab[o][fr]['pair_rank_corr']:+.2f}" for fr in FRAMINGS]
        print(f"{o:>16} | raw {cells[0]} | /mass {cells[1]} | resid {cells[2]}")

    print("\n=== CHECK 4: design-level rank agreement raw vs normalized ===")
    for o in OBJECTIVES:
        print(f"{o:>16}: rho(raw, /mass) = "
              f"{ranks[o]['spearman_raw_vs_per_gram']:+.3f}  "
              f"rho(raw, resid) = {ranks[o]['spearman_raw_vs_resid']:+.3f}")
        for fr in FRAMINGS:
            print(f"{'':>16}  top5 {fr:>8}: {', '.join(ranks[o][f'top5_lowest_{fr}'])}")

    print("\n=== CHECK 5: strongest shape-coordinate correlation ===")
    for o in OBJECTIVES:
        cells = [f"{signal[o][fr]['max_abs_coord_rho']:.2f}" for fr in FRAMINGS]
        print(f"{o:>16} | raw {cells[0]} | /mass {cells[1]} | resid {cells[2]}")

    print("\n=== CHECK 6: held-out rank skill from mass ALONE (LOGO folds) ===")
    print("    rho, and rho above the shuffled-mass null for the same procedure")
    for o in OBJECTIVES:
        cells = [f"{alone[o][fr]['heldout_spearman']:+.2f} "
                 f"[{alone[o][fr]['excess_over_null']:+.2f}, "
                 f"p {alone[o][fr]['p_vs_null']:.3f}]" for fr in FRAMINGS]
        print(f"{o:>16} | raw {cells[0]:>22} | /mass {cells[1]:>22} | "
              f"resid {cells[2]:>22}")

    print("\n=== CHECK 7: where mass's leverage lives ===")
    tp = confound["twin_pairs"]
    print(f"nine reprint pairs: second print heavier by "
          f"{tp['delta_mass_g_mean']:+.2f} g on average "
          f"({tp['delta_mass_g_min']:+.2f} to {tp['delta_mass_g_max']:+.2f}); "
          f"all heavier: {tp['all_second_print_heavier']}")
    for o in OBJECTIVES:
        e = tp["objectives"][o]
        print(f"{o:>16}: r(d_mass, d_obj) = "
              f"{e['pearson_r_delta_mass_vs_delta_obj']:+.2f}  "
              f"within-pair slope {e['slope_per_gram']:+.4g} /g  vs "
              f"pooled slope {e['implied_pooled_slope']:+.4g} /g")
    print("  within-batch mean r(mass, objective):")
    for o in OBJECTIVES:
        cells = [f"{confound['within_batch'][o][fr]['mean_r']:+.2f}"
                 for fr in FRAMINGS]
        print(f"{o:>16} | raw {cells[0]} | /mass {cells[1]} | resid {cells[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
