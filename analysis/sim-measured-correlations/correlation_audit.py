"""Correlate every simulated and measured quantity against the campaign objectives.

Asked on PR #111 (sgbaird, 2026-09-23): bring in the simulation results from
issues #32/#33 and test whether the outcomes simulated there correlate with
any of the objectives measured on the tower; also check every other
prediction quantity discussed in the repo for correlations, now that 44
articles have been measured (the prior sim-vs-measured study, sim branch
``94e53a8``, had 7 to 10).

Inputs (all committed on this branch):

- measured per-article session summaries: the five drop-results CSVs under
  ../cv-signal-audit/data/ (8 seed + amdjwm, 9 r2d2c, 9 drran, 9 2dran,
  9 corny), plus the LOGO CSV as a cross-check of the objective join;
- fresh simulation channels for all 44 measured articles from
  data/sim-articles/ (produced by run_sims_on_articles.py: Tier C and
  Tier B drop-tower analogues at as-printed geometry and weighed mass,
  regime metrics per design);
- the sim branch's original n = 7 correlation screen
  (data/sim-branch/pr102_correlations.csv) for the replication test, and
  its Tier-A article runs (data/sim-branch/tierA_articles.csv), which were
  never scored against the 9 r2d2c results that landed after that branch
  froze.

Statistics: Spearman rho with a Monte-Carlo permutation p (20,000 draws,
fixed seed) on every pair, Pearson r alongside, Benjamini-Hochberg FDR
within each (target, analysis family), and each predictor's relative span
(range over mean) so span-degenerate leaders are visible, per the
rel_span < 1 percent lesson of the n = 7 screen. Design level collapses
the nine drran/2dran reprint pairs to means (n = 35); article level keeps
all prints (n = 44, plus amdjwm in measured-vs-measured only).

Outputs: metrics.json, tables/*.csv, figures/*.png.
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
CV = HERE.parent / "cv-signal-audit" / "data"
SIMA = HERE / "data" / "sim-articles"
SIMB = HERE / "data" / "sim-branch"
CAMP = HERE / "data" / "campaign"
FIGS = HERE / "figures"
TABLES = HERE / "tables"

SEED = 20260923
N_PERM = 20_000
G = 9.80665
DROP_H_M = 1.524

# Okabe-Ito batch identities, matching the cv-signal-audit figures.
BATCH_STYLE = {
    "seed": dict(color="#0072B2", marker="o", filled=True, label="seed (Sobol)"),
    "r2d2c": dict(color="#E69F00", marker="s", filled=True, label="batch 2 (r2d2c)"),
    "drran": dict(color="#009E73", marker="^", filled=True, label="batch 3 (drran)"),
    "2dran": dict(color="#009E73", marker="v", filled=False, label="batch 3 reprint (2dran)"),
    "corny": dict(color="#D55E00", marker="D", filled=True, label="batch 4 (corny)"),
}
GRID = dict(color="0.92", lw=0.7, zorder=0)

MEASURED_CHANNELS = [
    "t180", "t1000", "out_180_g", "in_180_g", "in_dv_ms", "t_second_ms",
    "e_rebound", "e_reb_mJ", "fn_hz", "zeta_pct", "mass_g",
]
TARGETS = ["t180", "e_reb_mJ", "e_rebound", "out_180_g", "fn_hz", "zeta_pct"]


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_measured() -> pd.DataFrame:
    """One row per measured article: session-mean channels + batch."""
    frames = []
    for fname, batch in (
        ("t3-prism-bo-batch-drop-results.csv", "seed"),
        ("t3-prism-bo-round1-drop-results.csv", "r2d2c"),
        ("t3-prism-bo-round3-drop-results.csv", "drran"),
        ("t3-prism-bo-round3-reprint-drop-results.csv", "2dran"),
        ("t3-prism-bo-round4-drop-results.csv", "corny"),
    ):
        df = pd.read_csv(CV / fname)
        df["batch"] = batch
        frames.append(df)
    m = pd.concat(frames, ignore_index=True)
    ren = {f"{c}_mean": c for c in
           ("t180", "t1000", "out_180_g", "in_180_g", "in_dv_ms",
            "t_second_ms", "e_rebound", "fn_hz", "zeta_pct")}
    m = m.rename(columns=ren)
    m["e_reb_mJ"] = m.e_rebound * m.mass_g * G * DROP_H_M

    # cross-check the derived objective against the LOGO's observed column
    logo = pd.read_csv(CV / "full-nuts-rerun" / "t3-prism-bo-round5-logocv.csv")
    for metric, col in (("t180", "t180"), ("e_reb_mJ", "e_reb_mJ")):
        obs = logo[logo.metric == metric].set_index("print_id").observed
        joined = m.set_index("specimen")[col].reindex(obs.index)
        err = float(np.nanmax(np.abs(joined - obs)))
        assert err < 5e-3, (metric, err)
    return m


def load_sim() -> tuple[pd.DataFrame, pd.DataFrame]:
    arts = pd.read_csv(SIMA / "sim_articles.csv")
    des = pd.read_csv(SIMA / "regime_designs.csv")
    # regime evaluators repeat the analytic geometry under both prefixes;
    # keep one copy under geom_ and drop the rest
    des = des.drop(columns=[c for c in des.columns
                            if c.split("_", 1)[-1].startswith(("cell_mass",
                                                               "envelope",
                                                               "footprint"))
                            and not c.startswith("geom_")])
    return arts, des


def article_table() -> pd.DataFrame:
    """Measured channels + sim channels, one row per measured article."""
    m = load_measured()
    arts, _ = load_sim()
    sim_cols = [c for c in arts.columns if c.startswith(("tierC_", "tierB_"))]
    keep = arts[["print_id", "design", "source_trial", "R_print_mm",
                 "H_print_mm", "twist_deg", "strut_d_print_mm",
                 "cable_d_print_mm",
                 *[f"nom_{k}" for k in ("R_mm", "H_mm", "twist_deg",
                                        "strut_d_mm", "cable_d_mm")],
                 *sim_cols]]
    t = m.merge(keep, left_on="specimen", right_on="print_id", how="left")
    return t


def design_table(t: pd.DataFrame) -> pd.DataFrame:
    """Collapse reprint pairs to design means; join regime metrics."""
    _, des = load_sim()
    mapped = t[t.design.notna()].copy()
    num = mapped.select_dtypes(include=[np.number]).columns
    d = mapped.groupby("design")[list(num)].mean()
    d["batch"] = mapped.groupby("design")["batch"].first()
    d = d.merge(des.set_index("design").drop(columns=["batch"]),
                left_index=True, right_index=True, how="left")
    return d


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------

def rho_perm(x, y, rng) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = x.size
    if n < 5 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return dict(n=n, rho=np.nan, p=np.nan, r=np.nan)
    rho = stats.spearmanr(x, y).statistic
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        null[i] = np.corrcoef(rx, rng.permutation(ry))[0, 1]
    p = float((np.sum(np.abs(null) >= abs(rho) - 1e-12) + 1) / (N_PERM + 1))
    r = float(stats.pearsonr(x, y).statistic)
    return dict(n=int(n), rho=float(rho), p=p, r=r)


def bh_fdr(p: pd.Series) -> pd.Series:
    p = p.copy()
    ok = p.notna()
    q = pd.Series(np.nan, index=p.index)
    pv = p[ok].sort_values()
    m = len(pv)
    qv = pv * m / np.arange(1, m + 1)
    qv = pd.Series(np.minimum.accumulate(qv[::-1])[::-1], index=pv.index)
    q.loc[qv.index] = qv.clip(upper=1.0)
    return q


def partial_rho(df: pd.DataFrame, x: str, y: str, controls: list[str],
                rng) -> dict:
    """Rank-based partial correlation of x and y given the controls.

    Rank-transform everything, residualize x and y on the controls by OLS,
    then Pearson on the residuals (= partial Spearman), permutation p by
    shuffling the y residuals.
    """
    cols = [x, y] + controls
    sub = df[cols].astype(float).dropna()
    n = len(sub)
    if n < len(controls) + 4:
        return dict(n=n, rho=np.nan, p=np.nan)
    R = stats.rankdata(sub.values, axis=0)
    X = np.column_stack([np.ones(n), R[:, 2:]])
    beta_x, *_ = np.linalg.lstsq(X, R[:, 0], rcond=None)
    beta_y, *_ = np.linalg.lstsq(X, R[:, 1], rcond=None)
    rx = R[:, 0] - X @ beta_x
    ry = R[:, 1] - X @ beta_y
    if np.ptp(rx) == 0 or np.ptp(ry) == 0:
        return dict(n=n, rho=np.nan, p=np.nan)
    rho = float(np.corrcoef(rx, ry)[0, 1])
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        null[i] = np.corrcoef(rx, rng.permutation(ry))[0, 1]
    p = float((np.sum(np.abs(null) >= abs(rho) - 1e-12) + 1) / (N_PERM + 1))
    return dict(n=int(n), rho=rho, p=p)


def within_batch_rho(frame: pd.DataFrame, x: str, y: str, rng,
                     min_n: int = 5) -> dict:
    """Batch-stratified rank association: mean within-batch Spearman rho
    (weights n - 1) with a permutation p that shuffles y only within batch.

    This is the guard against adaptive-sampling structure: batches 2 to 4
    were chosen by the optimizer, so a pooled correlation can ride on
    between-batch shifts that have nothing to do with the predictor.
    """
    parts = []
    for b, sub in frame.groupby("batch"):
        sub = sub[[x, y]].dropna()
        if len(sub) >= min_n:
            parts.append((stats.rankdata(sub[x]), stats.rankdata(sub[y])))
    if not parts:
        return dict(n_batches=0, rho=np.nan, p=np.nan)
    w = np.array([len(rx) - 1 for rx, _ in parts], float)

    def stat(ys):
        rs = [np.corrcoef(rx, ry)[0, 1] for (rx, _), ry in zip(parts, ys)]
        return float(np.sum(np.array(rs) * w) / w.sum())

    obs = stat([ry for _, ry in parts])
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        null[i] = stat([rng.permutation(ry) for _, ry in parts])
    p = float((np.sum(np.abs(null) >= abs(obs) - 1e-12) + 1) / (N_PERM + 1))
    per_batch = {f"batch{k}": float(np.corrcoef(rx, ry)[0, 1])
                 for k, (rx, ry) in enumerate(parts)}
    return dict(n_batches=len(parts), rho=obs, p=p,
                n_total=int(w.sum() + len(parts)), **per_batch)


def rel_span(v) -> float:
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if v.size == 0 or np.mean(np.abs(v)) == 0:
        return np.nan
    return float(np.ptp(v) / np.abs(np.mean(v)))


def screen(df: pd.DataFrame, targets, predictors, rng, family: str) -> pd.DataFrame:
    rows = []
    for tgt in targets:
        for pred in predictors:
            if pred == tgt:
                continue
            s = rho_perm(df[pred], df[tgt], rng)
            rows.append(dict(family=family, target=tgt, predictor=pred,
                             rel_span=rel_span(df[pred]), **s))
    out = pd.DataFrame(rows)
    out["q"] = np.nan
    for tgt in targets:
        sel = out.target == tgt
        out.loc[sel, "q"] = bh_fdr(out.loc[sel, "p"])
    return out


# --------------------------------------------------------------------------
# analyses
# --------------------------------------------------------------------------

def main():
    rng = np.random.default_rng(SEED)
    FIGS.mkdir(exist_ok=True)
    TABLES.mkdir(exist_ok=True)
    metrics: dict = {}

    t = article_table()
    d = design_table(t)
    measured_only = t  # includes amdjwm (design NaN)
    print(f"articles: {len(t)} measured ({t.design.notna().sum()} design-mapped), "
          f"designs: {len(d)}")

    # ---- 1. sim-vs-measured, design level (primary) ----------------------
    sim_preds = [c for c in d.columns if c.startswith(("tierC_", "tierB_"))
                 and not c.endswith(("_r2", "_frac"))
                 and c not in ("tierC_mass_printed_g", "tierC_mass_flat_model_g",
                               "tierC_mass_solid_g", "tierC_v_rebound_mps",
                               "tierC_e_reb_mJ", "tierB_e_reb_mJ",
                               "tierB_in_180_g")]
    regime_preds = [c for c in d.columns if c.startswith(("crutch_", "lander_"))
                    and np.issubdtype(d[c].dtype, np.number)
                    and not c.endswith(("feasible", "ok"))]
    geom_preds = [c for c in d.columns if c.startswith("geom_")]
    coord_preds = [f"nom_{k}" for k in ("R_mm", "H_mm", "twist_deg",
                                        "strut_d_mm", "cable_d_mm")] + ["mass_g"]

    scr = screen(d, TARGETS, sim_preds + regime_preds + geom_preds + coord_preds,
                 rng, family="design")
    scr.sort_values(["target", "p"]).to_csv(
        TABLES / "sim_vs_measured_design_level.csv", index=False)

    # article level for the per-article tiers
    scr_art = screen(t[t.design.notna()], ["t180", "e_reb_mJ", "fn_hz", "zeta_pct"],
                     [p for p in sim_preds if p in t.columns], rng,
                     family="article")
    scr_art.sort_values(["target", "p"]).to_csv(
        TABLES / "sim_vs_measured_article_level.csv", index=False)

    # headline: Tier-B / Tier-C analogue tracking, design + article level
    for lvl, frame in (("design", d), ("article", t[t.design.notna()])):
        for tier in ("tierB", "tierC"):
            s = rho_perm(frame[f"{tier}_t180"], frame["t180"], rng)
            metrics[f"{tier}_t180_{lvl}"] = s
    # exploit-cluster view, articles with measured t180 in [0.95, 1.10]
    cl = t[(t.t180 >= 0.95) & (t.t180 <= 1.10) & t.design.notna()]
    metrics["tierB_t180_cluster"] = rho_perm(cl.tierB_t180, cl.t180, rng)
    metrics["tierC_t180_cluster"] = rho_perm(cl.tierC_t180, cl.t180, rng)
    # attenuator discrimination: AUC = P(a random attenuator gets a lower
    # simulated t180 than a random non-attenuator); 0.5 = chance
    att = (t[t.design.notna()].t180 < 1.0).astype(int)
    for tier in ("tierB", "tierC"):
        x = t[t.design.notna()][f"{tier}_t180"]
        ok = np.isfinite(x) & np.isfinite(att)
        n1 = int((att[ok] == 1).sum())
        n0 = int((att[ok] == 0).sum())
        mw = stats.mannwhitneyu(x[ok][att[ok] == 1], x[ok][att[ok] == 0],
                                alternative="less")
        metrics[f"{tier}_attenuator_auc"] = float(1.0 - mw.statistic / (n1 * n0))
        metrics[f"{tier}_attenuator_auc_p"] = float(mw.pvalue)

    # do the two tiers carry the same information?
    metrics["tierC_vs_tierB_t180"] = rho_perm(d.tierC_t180, d.tierB_t180, rng)

    # ---- 1b. partial correlations: is the sim just reading cable_d? -------
    top_preds = ["tierC_t180", "tierC_peak_tendon_strain",
                 "tierC_peak_tendon_energy_mJ", "tierC_e_rebound",
                 "tierB_stroke_mm", "geom_envelope_cm3", "tierC_tpu_fraction",
                 "crutch_SEA_J_per_g", "tierB_t180"]
    coords5 = ["nom_R_mm", "nom_H_mm", "nom_twist_deg", "nom_strut_d_mm",
               "nom_cable_d_mm"]
    partials = {}
    for pred in top_preds:
        partials[pred] = {
            "rho_raw": rho_perm(d[pred], d.t180, rng),
            "rho_with_cable_d": rho_perm(d[pred], d.nom_cable_d_mm, rng),
            "partial_given_cable_d": partial_rho(d, pred, "t180",
                                                 ["nom_cable_d_mm"], rng),
            "partial_given_5coords": partial_rho(d, pred, "t180", coords5, rng),
        }
    metrics["t180_partials"] = partials

    # ---- 1c. within-batch view (guards against adaptive-sampling drift) --
    wb = {}
    for pred in ("nom_cable_d_mm", "tierC_t180", "tierB_t180", "fn_hz",
                 "zeta_pct", "geom_envelope_cm3", "tierC_peak_tendon_strain"):
        wb[f"{pred}_vs_t180"] = within_batch_rho(d, pred, "t180", rng)
    for pred in ("nom_R_mm", "tierC_e_rebound", "tierB_t180"):
        wb[f"{pred}_vs_e_reb_mJ"] = within_batch_rho(d, pred, "e_reb_mJ", rng)
    wb["t180_vs_e_reb_mJ"] = within_batch_rho(d, "t180", "e_reb_mJ", rng)
    wb["zeta_pct_vs_e_rebound"] = within_batch_rho(d, "zeta_pct", "e_rebound", rng)
    metrics["within_batch_design"] = wb

    # ---- 2. replication of the n = 7 screen ------------------------------
    old = pd.read_csv(SIMB / "pr102_correlations.csv")
    name_map = {
        "sim_t180": "tierC_t180", "sim_in_180_g": "tierC_in_180_g",
        "sim_out_180_g": "tierC_out_180_g", "sim_pulse_ms": "tierC_pulse_ms",
        "sim_e_rebound": "tierC_e_rebound", "sim_e_reb_mJ": "tierC_e_reb_mJ",
        "sim_tpu_fraction": "tierC_tpu_fraction",
        "R_mm": "nom_R_mm", "H_mm": "nom_H_mm", "twist_deg": "nom_twist_deg",
        "strut_d_mm": "nom_strut_d_mm", "cable_d_mm": "nom_cable_d_mm",
        "mass_g": "mass_g", "cell_mass_g": "geom_cell_mass_g",
        "envelope_cm3": "geom_envelope_cm3", "footprint_mm2": "geom_footprint_mm2",
    }
    for c in old.observable.unique():
        if c.startswith(("crutch_", "lander_")):
            name_map.setdefault(c, c)
    rep_rows = []
    for _, r in old.iterrows():
        new_name = name_map.get(r.observable)
        if new_name is None or new_name not in d.columns:
            continue
        if r.target not in d.columns:
            continue
        s = rho_perm(d[new_name], d[r.target], rng)
        rep_rows.append(dict(target=r.target, observable=r.observable,
                             new_name=new_name, rho_n7=r.spearman_rho,
                             p_n7=r.spearman_p, rho_n35=s["rho"],
                             p_n35=s["p"], n=s["n"],
                             rel_span_n35=rel_span(d[new_name])))
    rep = pd.DataFrame(rep_rows)
    rep.to_csv(TABLES / "replication_n7_vs_n35.csv", index=False)
    metrics["replication"] = {
        "pairs_tested": int(len(rep)),
        "n7_hits_p05": int((rep.p_n7 < 0.05).sum()),
        "n7_hits_surviving_n35_p05_same_sign": int(
            ((rep.p_n7 < 0.05) & (rep.p_n35 < 0.05)
             & (np.sign(rep.rho_n7) == np.sign(rep.rho_n35))).sum()),
        "sign_agreement_frac": float(
            (np.sign(rep.rho_n7) == np.sign(rep.rho_n35)).mean()),
        "rho_of_rhos": float(stats.spearmanr(rep.rho_n7, rep.rho_n35,
                                             nan_policy="omit").statistic),
    }

    # ---- 3. Tier-A articles, scored against today's bench ----------------
    ta = pd.read_csv(SIMB / "tierA_articles.csv")
    ta = ta[ta.ok == True]  # noqa: E712
    ta = ta.merge(t[["specimen", "t180", "e_rebound", "e_reb_mJ", "fn_hz",
                     "zeta_pct"]], left_on="print_id", right_on="specimen",
                  how="inner")
    # The sim branch's Tier-A (and old Tier-B) roster simulated the r2d2c
    # articles at the superseded suggestions-round1 print dims, which do not
    # match the as-built round1-designs / drop-results geometry (up to ~40%
    # off in H). Batch-1 rows used the correct print-key dims, so the clean
    # Tier-A comparison is batch-1 only; the pooled number is kept with that
    # caveat attached.
    seeds = set(t[t.batch == "seed"].specimen)
    ta_res = {}
    for pred, tgt in (("peak_top_g", "t180"), ("e_rebound_article", "e_rebound"),
                      ("e_rebound_article", "e_reb_mJ"), ("fn_hz_x", "fn_hz_y"),
                      ("zeta_pct_x", "zeta_pct_y")):
        if pred in ta.columns and tgt in ta.columns:
            ta_res[f"{pred}_vs_{tgt}"] = rho_perm(ta[pred], ta[tgt], rng)
            tb1 = ta[ta.print_id.isin(seeds)]
            ta_res[f"{pred}_vs_{tgt}_batch1"] = rho_perm(tb1[pred], tb1[tgt],
                                                         rng)
    metrics["tierA_vs_measured"] = ta_res
    metrics["tierA_n_matched"] = int(len(ta))

    # ---- 4. measured-vs-measured cross matrix ----------------------------
    chan = MEASURED_CHANNELS
    for lvl, frame in (("article", measured_only), ("design", d)):
        mat_rho = pd.DataFrame(np.nan, index=chan, columns=chan)
        mat_p = pd.DataFrame(np.nan, index=chan, columns=chan)
        for i, a in enumerate(chan):
            for b in chan[i + 1:]:
                s = rho_perm(frame[a], frame[b], rng)
                mat_rho.loc[a, b] = mat_rho.loc[b, a] = s["rho"]
                mat_p.loc[a, b] = mat_p.loc[b, a] = s["p"]
        mat_rho.to_csv(TABLES / f"measured_cross_rho_{lvl}.csv")
        mat_p.to_csv(TABLES / f"measured_cross_p_{lvl}.csv")
        if lvl == "design":
            cross_rho, cross_p = mat_rho, mat_p

    # named pairs worth reading directly
    named = {}
    for a, b in (("t180", "e_reb_mJ"), ("t180", "e_rebound"),
                 ("t180", "fn_hz"), ("t180", "zeta_pct"), ("t180", "mass_g"),
                 ("t180", "in_180_g"), ("e_reb_mJ", "mass_g"),
                 ("e_rebound", "fn_hz"), ("e_rebound", "zeta_pct"),
                 ("fn_hz", "zeta_pct"), ("t180", "t1000"),
                 ("e_reb_mJ", "in_dv_ms")):
        named[f"{a}~{b}"] = {"design": rho_perm(d[a], d[b], rng),
                             "article": rho_perm(measured_only[a],
                                                 measured_only[b], rng)}
    metrics["named_measured_pairs"] = named

    # process parameters (rounds 3+4 varied infill/temps): within-subset screen
    proc = []
    for rnd in ("round3", "round4"):
        des_csv = pd.read_csv(CAMP / f"t3-prism-bo-{rnd}-designs.csv")
        des_csv["design"] = [f"trial{int(x)}" for x in des_csv["trial_index"]]
        proc.append(des_csv[["design", "strut_infill_pct", "tpu_infill_pct",
                             "pla_nozzle_temp_C", "tpu_nozzle_temp_C",
                             "pla_flow_mm3_s", "tpu_flow_mm3_s"]])
    proc = pd.concat(proc).set_index("design")
    dp = d.merge(proc, left_index=True, right_index=True, how="inner")
    scr_proc = screen(dp, ["t180", "e_reb_mJ", "fn_hz", "zeta_pct"],
                      list(proc.columns), rng, family="process")
    scr_proc.to_csv(TABLES / "process_params_design_level.csv", index=False)

    # ---- 5. reprint-pair reliability ceiling per channel -----------------
    pair_rows = []
    r3 = t[t.batch == "drran"].set_index("design")
    r3b = t[t.batch == "2dran"].set_index("design")
    shared = r3.index.intersection(r3b.index)
    for c in chan + ["tierB_t180", "tierC_t180"]:
        if c not in r3.columns:
            continue
        a = r3.loc[shared, c].astype(float)
        b = r3b.loc[shared, c].astype(float)
        ok = np.isfinite(a) & np.isfinite(b)
        if ok.sum() < 4:
            continue
        rho = stats.spearmanr(a[ok], b[ok]).statistic
        pair_rows.append(dict(channel=c, n_pairs=int(ok.sum()),
                              pair_rho=float(rho),
                              median_abs_rel_diff=float(np.median(
                                  np.abs(a[ok] - b[ok])
                                  / ((np.abs(a[ok]) + np.abs(b[ok])) / 2)))))
    pairs = pd.DataFrame(pair_rows)
    pairs.to_csv(TABLES / "reprint_pair_reliability.csv", index=False)

    # ---- figures ----------------------------------------------------------
    fig_heatmap(scr, d)
    fig_parity(t, d, metrics)
    fig_replication(rep)
    fig_measured(cross_rho, cross_p, d, pairs)

    with open(HERE / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=1, default=float)
    print("wrote metrics.json")

    top = scr[(scr.q < 0.10) & (scr.rel_span > 0.01)].sort_values("p")
    print("\ndesign-level hits (q < 0.10, rel_span > 1%):")
    print(top[["target", "predictor", "n", "rho", "p", "q", "rel_span"]]
          .to_string(index=False))
    return 0


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def _sig_marker(ax, i, j, q):
    if np.isfinite(q) and q < 0.05:
        ax.plot(j, i, marker="o", ms=3.5, mfc="none", mec="black", mew=1.1)


def fig_heatmap(scr: pd.DataFrame, d: pd.DataFrame):
    targets = ["t180", "e_reb_mJ", "e_rebound", "fn_hz", "zeta_pct"]
    piv = scr.pivot_table(index="predictor", columns="target", values="rho")
    qv = scr.pivot_table(index="predictor", columns="target", values="q")
    order = [p for p in scr.predictor.unique() if p in piv.index]
    order.sort(key=lambda p: (0 if p.startswith("tierC") else
                              1 if p.startswith("tierB") else
                              2 if p.startswith(("crutch", "lander")) else
                              3 if p.startswith("geom") else 4, p))
    piv = piv.loc[order, targets]
    qv = qv.loc[order, targets]

    fig, ax = plt.subplots(figsize=(7.2, 0.28 * len(order) + 1.8))
    im = ax.imshow(piv.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(targets)),
                  ["t180", "e_reb_mJ", "e_rebound\n(= per-gram)", "fn_hz",
                   "zeta_pct"], fontsize=8)
    ax.set_yticks(range(len(order)), order, fontsize=7)
    for i, p in enumerate(order):
        for j, tgt in enumerate(targets):
            v, q = piv.iloc[i, j], qv.iloc[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                        fontsize=6.2,
                        color="white" if abs(v) > 0.55 else "#1a1a1a")
                _sig_marker(ax, i, j + 0.38, q)
    ax.set_title("Simulated and geometric quantities vs measured channels\n"
                 "design level (n = 35), Spearman rho; ring = BH-FDR q < 0.05",
                 fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.5, label="Spearman rho")
    fig.tight_layout()
    fig.savefig(FIGS / "sim-vs-measured-heatmap.png", dpi=200)
    plt.close(fig)


def fig_parity(t: pd.DataFrame, d: pd.DataFrame, metrics: dict):
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.1))
    mapped = t[t.design.notna()]
    for ax, tier, title in (
            (axes[0], "tierB", "Tier B (flexural struts)"),
            (axes[1], "tierC", "Tier C (rigid struts)")):
        for b, st in BATCH_STYLE.items():
            sub = mapped[mapped.batch == b]
            ax.scatter(sub[f"{tier}_t180"], sub.t180, s=26,
                       marker=st["marker"],
                       facecolor=st["color"] if st["filled"] else "none",
                       edgecolor=st["color"], linewidth=1.1, label=st["label"],
                       zorder=3)
        s = metrics[f"{tier}_t180_article"]
        ax.set_title(f"{title}\nrho = {s['rho']:+.2f} (p = {s['p']:.3f}, "
                     f"n = {s['n']})", fontsize=9)
        ax.set_xlabel(f"simulated t180 ({tier[-1]} tier)", fontsize=9)
        ax.grid(**GRID)
    axes[0].set_ylabel("measured t180 (session mean)", fontsize=9)
    axes[0].legend(fontsize=7, loc="upper left", framealpha=0.9)

    ax = axes[2]
    s_art = metrics["tierB_t180_article"]
    per = []
    for b in ("seed", "r2d2c", "drran", "2dran", "corny"):
        sub = mapped[mapped.batch == b]
        ok = np.isfinite(sub.tierB_t180) & np.isfinite(sub.t180)
        if ok.sum() >= 5:
            per.append((b, stats.spearmanr(sub.tierB_t180[ok],
                                           sub.t180[ok]).statistic,
                        int(ok.sum())))
    ax.barh([f"{b} (n={n})" for b, _, n in per], [r for _, r, _ in per],
            color=[BATCH_STYLE[b]["color"] for b, _, _ in per], height=0.62,
            zorder=3)
    ax.axvline(0, color="0.35", lw=0.9)
    ax.axvline(s_art["rho"], color="0.2", lw=1.0, ls="--")
    ax.text(s_art["rho"], -0.62, f"pooled {s_art['rho']:+.2f}",
            fontsize=7.5, ha="center", va="top", clip_on=False)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman rho, Tier-B t180 vs measured, within batch",
                  fontsize=9)
    ax.set_title("Within-batch rank agreement (articles)", fontsize=9)
    ax.grid(axis="x", **GRID)
    fig.tight_layout()
    fig.savefig(FIGS / "tier-parity-t180.png", dpi=200)
    plt.close(fig)


def fig_replication(rep: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    ax.axhspan(-1, 1, color="0.97", zorder=0)
    ax.axhline(0, color="0.4", lw=0.8)
    ax.axvline(0, color="0.4", lw=0.8)
    ax.plot([-1, 1], [-1, 1], color="0.75", lw=0.8, ls=":")
    for tgt, color in (("t180", "#0072B2"), ("e_reb_mJ", "#D55E00")):
        sub = rep[rep.target == tgt]
        ax.scatter(sub.rho_n7, sub.rho_n35, s=26, color=color, alpha=0.85,
                   label=f"target {tgt}", zorder=3)
    lab = rep[(rep.p_n7 < 0.08) & (rep.rho_n7.abs() > 0.7)].reset_index()
    for i, r in lab.iterrows():
        dy = (3, 10, -8)[i % 3]
        ax.annotate(r.observable, (r.rho_n7, r.rho_n35), fontsize=6.2,
                    textcoords="offset points", xytext=(4, dy),
                    annotation_clip=False)
    ax.set_xlabel("Spearman rho at n = 7 (seed batch, 2026-08)", fontsize=9)
    ax.set_ylabel("Spearman rho at n = 35 designs (now)", fontsize=9)
    ax.set_title("Replication test of the sim-branch correlation screen",
                 fontsize=10)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(**GRID)
    fig.tight_layout()
    fig.savefig(FIGS / "replication-n7-vs-n35.png", dpi=200)
    plt.close(fig)


def fig_measured(cross_rho: pd.DataFrame, cross_p: pd.DataFrame,
                 d: pd.DataFrame, pairs: pd.DataFrame):
    fig = plt.figure(figsize=(12.6, 5.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1, 1], wspace=0.34)

    ax = fig.add_subplot(gs[0])
    chan = list(cross_rho.columns)
    im = ax.imshow(cross_rho.values.astype(float), cmap="RdBu_r",
                   vmin=-1, vmax=1)
    ax.set_xticks(range(len(chan)), chan, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(len(chan)), chan, fontsize=7)
    for i in range(len(chan)):
        for j in range(len(chan)):
            v = cross_rho.values[i, j]
            if i != j and np.isfinite(v):
                ax.text(j, i, f"{v:+.1f}".replace("0.", "."), ha="center",
                        va="center", fontsize=5.6,
                        color="white" if abs(v) > 0.55 else "#1a1a1a")
    ax.set_title("Measured channels, design level (n = 35)\nSpearman rho",
                 fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.65)

    ax = fig.add_subplot(gs[1])
    for b, st in BATCH_STYLE.items():
        sub = d[d.batch == b]
        ax.scatter(sub.t180, sub.e_reb_mJ, s=30, marker=st["marker"],
                   facecolor=st["color"] if st["filled"] else "none",
                   edgecolor=st["color"], linewidth=1.1, label=st["label"],
                   zorder=3)
    ax.set_xlabel("t180 (design mean)", fontsize=9)
    ax.set_ylabel("rebound score e_reb_mJ (design mean)", fontsize=9)
    ax.set_title("The two campaign objectives", fontsize=9)
    ax.legend(fontsize=6.5, loc="upper right")
    ax.grid(**GRID)

    ax = fig.add_subplot(gs[2])
    pr = pairs[pairs.channel.isin(MEASURED_CHANNELS)]
    ax.barh(pr.channel, pr.pair_rho, color="#0072B2", height=0.62, zorder=3)
    ax.axvline(0, color="0.35", lw=0.9)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman rho, print 1 vs print 2 (9 reprint pairs)",
                  fontsize=9)
    ax.set_title("Reprint reliability ceiling per channel", fontsize=9)
    ax.grid(axis="x", **GRID)

    fig.tight_layout()
    fig.savefig(FIGS / "measured-cross-correlations.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
