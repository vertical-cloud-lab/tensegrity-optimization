"""Mass out of the fit space and the objectives divided by mass, scored,
plus the within-session claim of Section 9.3 decomposed.

PR #111 (sgbaird, 2026-09-25): "So then, just take the mass out of the
input space and divide the objectives by the mass. Right?", and on the
Section 9.3 line "division fixes the within-session confound and creates
a pooled one": "if true, this seems important, and it's cryptic."

Part 1, the decode (no model, deterministic). Section 9.3 read the
within-session effect off the *mean of the signed per-batch correlations*
(+0.42 raw, -0.10 per gram). This part asks where that correlation comes
from and what division does to it:

* per batch: r(mass, Y), r(mass, Y/m), and the log-log elasticity
  d ln Y / d ln m (dividing by m subtracts exactly 1 from it);
* mean signed r next to mean |r|;
* the within-batch relation with batch fixed effects, and the same with
  the five shape coordinates also held fixed (an added-variable, or
  partial, correlation), with a permutation p on the residuals;
* how much of the within-batch mass variation the shape coordinates
  explain;
* the reprint-twin reliability of mass itself, which is what the per-gram
  reliability gain quoted in Section 9.3 is built from.

Part 2, the held-out test. The shape-only per-gram runs written by
``rerun_logocv_shape_only_per_gram.py`` are graded next to the committed
shape-only raw runs (``data/ablation-shape-only/`` for t180 and rebound,
``data/objective-tavg10ms-shape-only/`` for the payload pair) three ways:
on the target each run was fitted to; against the raw objective (the
bare per-gram prediction ranked against raw values, the ranking an
optimizer minimizing the per-gram objective would act on; the
prediction multiplied back by the weighed mass is kept in the JSON); and
**mass leverage on the held-out residuals**, the direct test of the goal
"mass has no predictive power relative to the objectives": after a model
that cannot see mass has predicted each held-out article, does mass
still correlate with what it got wrong?

Outputs: ``metrics-shape-only-per-gram.json``,
``figures/mass-within-session-decoded.png``,
``figures/shape-only-per-gram-logocv.png``, and a summary on stdout.
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

import cv_signal_audit as base

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"
OUT_JSON = HERE / "metrics-shape-only-per-gram.json"
NORMALIZED_CSV = DATA / "mass-normalized-objectives.csv"
CSV_NAME = "t3-prism-bo-round5-logocv.csv"
DIAG_NAME = "t3-prism-bo-round5-logocv-diagnostics.json"

SEED = 20260925
N_PERM = int(__import__("os").environ.get("N_PERM", 20_000))
# the audit's scorecard helpers default to 100k permutations; 20k keeps this
# script to about a minute and moves p-values only in the third decimal
base.N_PERM = N_PERM
LEVERAGE_ID = "r2d2c5"   # 23.47 g, 4.1 g above its batch mean: the one
                         # high-leverage point in the mass residuals
OBJECTIVES = ("t180", "e_reb_mJ", "tavg10ms", "late_avg3ms_g")
OBJ_LABEL = {"t180": "t180", "e_reb_mJ": "rebound (mJ)",
             "tavg10ms": "tavg10ms", "late_avg3ms_g": "late_avg3ms"}
COORDS = ("H_mm", "R_mm", "cable_d_mm", "strut_d_mm", "twist_deg")
BATCHES = ("seed", "r2d2c", "drran", "2dran", "corny")

RAW_RUNS = {"t180": DATA / "ablation-shape-only",
            "e_reb_mJ": DATA / "ablation-shape-only",
            "tavg10ms": DATA / "objective-tavg10ms-shape-only",
            "late_avg3ms_g": DATA / "objective-tavg10ms-shape-only"}
PG_RUNS = {"t180": DATA / "objective-per-gram-shape-only",
           "e_reb_mJ": DATA / "objective-per-gram-shape-only",
           "tavg10ms": DATA / "objective-payload-per-gram-shape-only",
           "late_avg3ms_g": DATA / "objective-payload-per-gram-shape-only"}
RAW_COLOR, PG_COLOR = "#3b6ea5", "#c1553b"   # as in the Section 9 figures


# ------------------------------------------------------------ helpers
def residualize(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def controls(df: pd.DataFrame, batch: bool, shape: bool) -> np.ndarray:
    """Columns held fixed: batch dummies (or an intercept) and/or shape."""
    cols = [pd.get_dummies(df.batch).astype(float).to_numpy() if batch
            else np.ones((len(df), 1))]
    if shape:
        cols.append(df[list(COORDS)].to_numpy(dtype=float))
    return np.column_stack(cols)


def perm_r(x: np.ndarray, y: np.ndarray, rng) -> tuple[float, float]:
    """Pearson r with a two-sided permutation p (residuals permuted)."""
    r = float(np.corrcoef(x, y)[0, 1])
    yp = np.stack([rng.permutation(y) for _ in range(N_PERM)])
    xc = x - x.mean()
    yc = yp - yp.mean(axis=1, keepdims=True)
    null = (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    return r, float((np.sum(np.abs(null) >= abs(r) - 1e-12) + 1) / (N_PERM + 1))


def added_variable(df: pd.DataFrame, y: np.ndarray, batch: bool, shape: bool,
                   rng) -> dict:
    """Relation of ln(mass) to ln(y) with the given controls held fixed."""
    X = controls(df, batch, shape)
    em = residualize(np.log(df.mass_g.to_numpy()), X)
    ey = residualize(np.log(y), X)
    r, p = perm_r(em, ey, rng)
    return {"r": r, "perm_p": p, "elasticity": float(em @ ey / (em @ em)),
            "n": int(len(df)), "dof": int(len(df) - X.shape[1]),
            "_em": em, "_ey": ey}


def within_batch_spearman(d: pd.DataFrame, obs_col: str, pred_col: str,
                          rng) -> dict:
    """Mean of the per-batch Spearman rho, with a within-batch shuffle null."""
    per, null = {}, np.zeros(N_PERM)
    batches = [b for b in BATCHES if (d.batch == b).sum() >= 3]
    for b in batches:
        g = d[d.batch == b]
        rx = stats.rankdata(g[obs_col].to_numpy())
        ry = stats.rankdata(g[pred_col].to_numpy())
        per[b] = float(np.corrcoef(rx, ry)[0, 1])
        idx = np.argsort(rng.random((N_PERM, len(ry))), axis=1)
        yp = ry[idx]
        xc = rx - rx.mean()
        yc = yp - yp.mean(axis=1, keepdims=True)
        null += (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    null /= len(batches)
    mean_obs = float(np.mean(list(per.values())))
    p = float((np.sum(np.abs(null) >= abs(mean_obs) - 1e-12) + 1) / (N_PERM + 1))
    return {"per_batch_rho": per, "mean_rho": mean_obs, "perm_p": p}


def strip(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}


# ------------------------------------------------------------ part 1
def decode(df: pd.DataFrame, rng) -> dict:
    out = {"per_objective": {}}

    # where within-batch mass variation comes from
    Xb, Xbs = controls(df, True, False), controls(df, True, True)
    m = df.mass_g.to_numpy()
    mb, mbs = residualize(m, Xb), residualize(m, Xbs)
    out["within_batch_mass"] = {
        "sd_g": float(mb.std(ddof=1)),
        "sd_g_given_shape": float(mbs.std(ddof=1)),
        "share_explained_by_shape": float(1 - mbs.var() / mb.var()),
        "r_with_coordinate": {
            c: float(np.corrcoef(mb, residualize(df[c].to_numpy(dtype=float),
                                                 Xb))[0, 1])
            for c in COORDS},
    }
    out["batch_mass"] = {
        b: {"n": int((df.batch == b).sum()),
            "mean_g": float(df.loc[df.batch == b, "mass_g"].mean()),
            "sd_g": float(df.loc[df.batch == b, "mass_g"].std(ddof=1)),
            "min_g": float(df.loc[df.batch == b, "mass_g"].min()),
            "max_g": float(df.loc[df.batch == b, "mass_g"].max())}
        for b in BATCHES}

    for obj in OBJECTIVES:
        y_raw = df[obj].to_numpy()
        ent = {}
        for fr, y in (("raw", y_raw), ("per_gram", y_raw / m)):
            per = {}
            for b in BATCHES:
                g = df.batch == b
                lm, ly = np.log(m[g]), np.log(y[g])
                per[b] = {"r": float(np.corrcoef(m[g], y[g])[0, 1]),
                          "elasticity": float(np.polyfit(lm, ly, 1)[0])}
            rs = [v["r"] for v in per.values()]
            ent[fr] = {
                "per_batch": per,
                "mean_signed_r": float(np.mean(rs)),
                "mean_abs_r": float(np.mean(np.abs(rs))),
                "pooled_r": float(np.corrcoef(m, y)[0, 1]),
                "between_batch_r_of_means": float(np.corrcoef(
                    [m[df.batch == b].mean() for b in BATCHES],
                    [y[df.batch == b].mean() for b in BATCHES])[0, 1]),
                "within_batch": strip(added_variable(df, y, True, False, rng)),
                "within_batch_given_shape": added_variable(df, y, True, True, rng),
                "given_shape_no_batch": strip(added_variable(df, y, False, True, rng)),
            }
            keep = (df.print_id != LEVERAGE_ID).to_numpy()
            sub = df[keep].reset_index(drop=True)
            ent[fr][f"within_batch_given_shape_without_{LEVERAGE_ID}"] = strip(
                added_variable(sub, y[keep], True, True, rng))
            av = ent[fr]["within_batch_given_shape"]
            ent[fr]["within_batch_given_shape"]["spearman"] = float(
                stats.spearmanr(av["_em"], av["_ey"]).statistic)
        out["per_objective"][obj] = ent

    # reprint twins: the per-gram "reliability gain" is the reliability of
    # the mass that was divided in
    tw = df[df.batch.isin(["drran", "2dran"])].copy()
    tw["n"] = tw.print_id.str.extract(r"(\d)$")[0].astype(int)
    a = tw[tw.batch == "drran"].set_index("n").sort_index()
    b = tw[tw.batch == "2dran"].set_index("n").sort_index()
    twins = {"mass_g": {"pair_spearman": float(stats.spearmanr(a.mass_g, b.mass_g).statistic),
                        "pair_pearson": float(np.corrcoef(a.mass_g, b.mass_g)[0, 1])}}
    for obj in OBJECTIVES:
        for fr, fa, fb in (("raw", a[obj], b[obj]),
                           ("per_gram", a[obj] / a.mass_g, b[obj] / b.mass_g)):
            twins[f"{obj}__{fr}"] = {
                "pair_spearman": float(stats.spearmanr(fa, fb).statistic),
                "pair_pearson": float(np.corrcoef(fa, fb)[0, 1])}
    out["twin_reliability"] = twins
    return out


# ------------------------------------------------------------ part 2
def load_run(run_dir: Path, metric: str, df: pd.DataFrame) -> pd.DataFrame | None:
    """A finished run from its CSV; a run still in flight from its checkpoint
    (``attrs['partial']`` set, graded only on the articles it has reached)."""
    path = run_dir / CSV_NAME
    partial = False
    if not path.exists():
        folds = run_dir / "folds.jsonl"
        if not folds.exists():
            return None
        rows = []
        for line in folds.read_text().splitlines():
            for art in json.loads(line)["articles"]:
                i = art["observed"]["metric_names"].index(metric)
                j = art["predicted"]["metric_names"].index(metric)
                rows.append({
                    "arm_name": art["arm_name"], "print_id": art["print_id"],
                    "metric": metric,
                    "observed": art["observed"]["means"][i],
                    "observed_sem": art["observed"]["covariance"][i][i] ** 0.5,
                    "predicted": art["predicted"]["means"][j],
                    "predicted_sem": art["predicted"]["covariance"][j][j] ** 0.5})
        path = Path("/tmp") / f"{run_dir.name}-partial.csv"
        pd.DataFrame(rows).drop_duplicates("print_id").to_csv(path, index=False)
        partial = True
    logo = base.load_logo(path)
    d = logo[logo.metric == metric].copy()
    d.attrs["partial"] = partial
    assert partial or len(d) == 44, (run_dir, metric, len(d))
    art = df.set_index("print_id")
    d["mass_g"] = d.print_id.map(art.mass_g)
    return d


def check_archived(run_dir: Path, metric: str, d: pd.DataFrame) -> bool | None:
    if d.attrs.get("partial"):
        return None
    diag = json.loads((run_dir / DIAG_NAME).read_text())
    r = float(np.corrcoef(d.observed, d.predicted)[0, 1])
    mape = float(np.mean(np.abs(d.observed - d.predicted) / np.abs(d.observed)))
    return bool(abs(r - diag["Correlation coefficient"][metric]) < 1e-4
                and abs(mape - diag["MAPE"][metric]) < 1e-4)


RANK_KEYS = ("n", "spearman_rho", "spearman_p_perm")


def grade(d: pd.DataFrame, obs_col: str, pred_col: str, rng,
          sem_col: str = "predicted_sem", rank_only: bool = False) -> dict:
    """The audit's scorecard; rank_only when the prediction is in other units
    than the observation (a bare per-gram prediction against a raw value),
    where only rank statistics mean anything."""
    m = base.held_out_metrics(d[obs_col].to_numpy(), d[pred_col].to_numpy(),
                              d[sem_col].to_numpy(), d.design.to_numpy(), rng)
    g = d.groupby("design").agg(o=(obs_col, "mean"), p=(pred_col, "mean"),
                                s=(sem_col, "mean"))
    dl = base.held_out_metrics(
        g.o.to_numpy(), g.p.to_numpy(), g.s.to_numpy(), g.index.to_numpy(), rng)
    if rank_only:
        m = {k: m[k] for k in RANK_KEYS}
        dl = {k: dl[k] for k in RANK_KEYS}
    m["within_batch"] = within_batch_spearman(d, obs_col, pred_col, rng)
    m["design_level"] = dl
    return m


def mass_leverage(d: pd.DataFrame, rng) -> dict:
    """Does mass predict what a mass-blind model got wrong, held out?"""
    resid = (d.observed - d.predicted).to_numpy()
    m = d.mass_g.to_numpy()
    r, p = perm_r(m, resid, rng)
    Xb = controls(d.assign(batch=d.batch), True, False)
    rw, pw = perm_r(residualize(m, Xb), residualize(resid, Xb), rng)
    return {"pooled_r": r, "pooled_perm_p": p,
            "within_batch_r": rw, "within_batch_perm_p": pw}


def heldout(df: pd.DataFrame, rng) -> dict:
    out = {}
    raw_of = df.set_index("print_id")
    for obj in OBJECTIVES:
        ent = {}
        d_raw = load_run(RAW_RUNS[obj], obj, df)
        ent["archived_diagnostics_match_raw"] = check_archived(RAW_RUNS[obj], obj, d_raw)
        ent["raw_shape_only"] = {
            "on_target": grade(d_raw, "observed", "predicted", rng),
            "mass_leverage_on_residuals": mass_leverage(d_raw, rng)}
        d_pg = load_run(PG_RUNS[obj], f"{obj}_per_g", df)
        if d_pg is not None:
            ent["archived_diagnostics_match_per_gram"] = check_archived(
                PG_RUNS[obj], f"{obj}_per_g", d_pg)
            if d_pg.attrs["partial"]:
                # interim: grade both runs on the same held-out articles
                ent["per_gram_run_partial"] = True
                ent["n_articles_graded"] = int(len(d_pg))
                d_raw = d_raw[d_raw.print_id.isin(d_pg.print_id)].copy()
                ent["raw_shape_only"] = {
                    "on_target": grade(d_raw, "observed", "predicted", rng),
                    "mass_leverage_on_residuals": mass_leverage(d_raw, rng)}
            # the per-gram observations must be exactly raw / mass
            # (the LOGO CSV rounds to five decimals)
            recon = d_pg.print_id.map(raw_of[obj]) / d_pg.mass_g
            assert np.allclose(recon, d_pg.observed, rtol=0, atol=6e-6), obj
            d_pg["raw_observed"] = d_pg.print_id.map(raw_of[obj])
            d_pg["restored"] = d_pg.predicted * d_pg.mass_g
            d_pg["restored_sem"] = d_pg.predicted_sem * d_pg.mass_g
            ent["per_gram_shape_only"] = {
                "on_target": grade(d_pg, "observed", "predicted", rng),
                "vs_raw_objective": grade(d_pg, "raw_observed", "predicted", rng,
                                          rank_only=True),
                "vs_raw_objective_mass_restored": grade(
                    d_pg, "raw_observed", "restored", rng, sem_col="restored_sem"),
                "mass_leverage_on_residuals": mass_leverage(d_pg, rng)}
            # same-article agreement of the two models' held-out rankings
            both = d_raw.set_index("print_id").predicted.to_frame("raw").join(
                d_pg.set_index("print_id").predicted.rename("pg"))
            ent["rank_agreement_raw_vs_per_gram_predictions"] = float(
                stats.spearmanr(both.raw, both.pg).statistic)
        out[obj] = ent
    return out


# ------------------------------------------------------------ figures
def style(ax):
    ax.grid(color="0.92", lw=0.7, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_decode(df: pd.DataFrame, dec: dict):
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.2))
    t = dec["per_objective"]["t180"]

    # A: what the "+0.42 to -0.10" average was made of
    ax = axes[0, 0]
    ys = np.arange(len(BATCHES))[::-1]
    for y, b in zip(ys, BATCHES):
        r0 = t["raw"]["per_batch"][b]["r"]
        r1 = t["per_gram"]["per_batch"][b]["r"]
        ax.plot([r0, r1], [y, y], color="0.75", lw=2, zorder=2)
        ax.scatter([r0], [y], s=80, color=RAW_COLOR, zorder=3,
                   edgecolor="white", linewidth=1.5)
        ax.scatter([r1], [y], s=80, color=PG_COLOR, zorder=3,
                   edgecolor="white", linewidth=1.5)
    ax.axvline(0, color="0.3", lw=0.8)
    ax.set_yticks(ys)
    ax.set_yticklabels([base.BATCH_STYLE[b]["label"] for b in BATCHES], fontsize=9)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("within-batch Pearson r, weighed mass vs t180", fontsize=9.5)
    ax.scatter([], [], s=60, color=RAW_COLOR,
               label=f"raw t180: mean r {t['raw']['mean_signed_r']:+.2f}, "
                     f"mean |r| {t['raw']['mean_abs_r']:.2f}")
    ax.scatter([], [], s=60, color=PG_COLOR,
               label=f"t180 / mass: mean r {t['per_gram']['mean_signed_r']:+.2f}, "
                     f"mean |r| {t['per_gram']['mean_abs_r']:.2f}")
    ax.legend(fontsize=8.5, loc="lower left", frameon=False)
    ax.set_title("A. The +0.42 to -0.10 was an average of signed values.\n"
                 "Division moved every batch down and zeroed none of them",
                 fontsize=10.5)
    style(ax)

    # B: within a session, heavier means thicker cables
    ax = axes[0, 1]
    Xb = controls(df, True, False)
    mb = residualize(df.mass_g.to_numpy(), Xb)
    cb = residualize(df.cable_d_mm.to_numpy(dtype=float), Xb)
    for b in BATCHES:
        g = (df.batch == b).to_numpy()
        st = base.BATCH_STYLE[b]
        ax.scatter(cb[g], mb[g], s=48, marker=st["marker"],
                   facecolor=st["color"] if st["filled"] else "white",
                   edgecolor=st["color"], linewidth=1.3, label=st["label"],
                   zorder=3)
    sl, ic = np.polyfit(cb, mb, 1)
    xx = np.linspace(cb.min(), cb.max(), 10)
    ax.plot(xx, sl * xx + ic, color="0.35", lw=1.5, zorder=2)
    wm = dec["within_batch_mass"]
    ax.set_xlabel("cable diameter minus its batch mean (mm)", fontsize=9.5)
    ax.set_ylabel("weighed mass minus its batch mean (g)", fontsize=9.5)
    ax.legend(fontsize=8, loc="upper left", frameon=False)
    ax.set_title(f"B. Within a session, the heavier prints are the thick-cable "
                 f"designs\n(r {wm['r_with_coordinate']['cable_d_mm']:+.2f}; "
                 f"the 5 shape coordinates explain "
                 f"{100 * wm['share_explained_by_shape']:.0f}% of within-session mass)",
                 fontsize=10.5)
    style(ax)

    # C, D: added-variable plots with batch and shape held fixed
    for ax, fr, color, letter in ((axes[1, 0], "raw", RAW_COLOR, "C"),
                                  (axes[1, 1], "per_gram", PG_COLOR, "D")):
        av = t[fr]["within_batch_given_shape"]
        wb = t[fr]["within_batch"]
        x, y = 100 * av["_em"], 100 * av["_ey"]
        for b in BATCHES:
            g = (df.batch == b).to_numpy()
            st = base.BATCH_STYLE[b]
            ax.scatter(x[g], y[g], s=48, marker=st["marker"],
                       facecolor=st["color"] if st["filled"] else "white",
                       edgecolor=st["color"], linewidth=1.3, zorder=3)
        xx = np.linspace(x.min(), x.max(), 10)
        ax.plot(xx, av["elasticity"] * xx, color=color, lw=2.2, zorder=4)
        ax.axhline(0, color="0.3", lw=0.8)
        ax.set_xlabel("weighed mass, % from what batch + shape predict", fontsize=9.5)
        what = "t180" if fr == "raw" else "t180 / mass"
        ax.set_ylabel(f"{what}, % from what batch + shape predict", fontsize=9.5)
        ax.set_ylim(-26, 26)
        wo = t[fr][f"within_batch_given_shape_without_{LEVERAGE_ID}"]
        verdict = ("mass adds nothing once shape is known" if fr == "raw"
                   else "division writes a slope of -1 into the target")
        ax.set_title(
            f"{letter}. {what}: {verdict}\n"
            f"slope {av['elasticity']:+.2f}, r {av['r']:+.2f} (perm p "
            f"{av['perm_p']:.3f}); batch only: slope {wb['elasticity']:+.2f}, "
            f"r {wb['r']:+.2f}", fontsize=10.5)
        ax.text(0.98, 0.03,
                f"without {LEVERAGE_ID} (far right): slope "
                f"{wo['elasticity']:+.2f}, r {wo['r']:+.2f} (p {wo['perm_p']:.2f})",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5,
                color="0.3")
        style(ax)
    lo = min(axes[1, 0].get_xlim()[0], axes[1, 1].get_xlim()[0])
    hi = max(axes[1, 0].get_xlim()[1], axes[1, 1].get_xlim()[1])
    for ax in axes[1]:
        ax.set_xlim(lo, hi)

    fig.suptitle("Where the within-session mass correlation comes from, and what "
                 "dividing t180 by mass does to it (44 articles)",
                 fontsize=13, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    out = FIGS / "mass-within-session-decoded.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"-> {out}")


def fig_logo(res: dict):
    objs = [o for o in OBJECTIVES if "per_gram_shape_only" in res[o]]
    if not objs:
        return
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.6))
    xs, w = np.arange(len(objs)), 0.34

    def bars(ax, get_raw, get_pg, get_p_raw, get_p_pg, ylabel, title):
        for off, get, getp, color, lab in (
                (-w / 2, get_raw, get_p_raw, RAW_COLOR, "raw objective"),
                (w / 2, get_pg, get_p_pg, PG_COLOR, "objective / mass")):
            vals = [get(o) for o in objs]
            ax.bar(xs + off, vals, w * 0.92, color=color, label=lab, zorder=3)
            for x, v, o in zip(xs + off, vals, objs):
                star = "*" if getp(o) < 0.05 else ""
                ax.text(x, v + (0.03 if v >= 0 else -0.03), f"{v:+.2f}{star}",
                        ha="center", va="bottom" if v >= 0 else "top",
                        fontsize=8.5, color="0.2")
        ax.axhline(0, color="0.3", lw=0.8)
        ax.set_xticks(xs)
        ax.set_xticklabels(
            [OBJ_LABEL[o] + (f"\ninterim: {res[o]['n_articles_graded']} of 44"
                             if res[o].get("per_gram_run_partial") else "")
             for o in objs], fontsize=9.5)
        ax.set_ylim(-0.85, 0.95)
        ax.set_ylabel(ylabel, fontsize=9.5)
        ax.set_title(title, fontsize=10.5)
        style(ax)

    raw = lambda o: res[o]["raw_shape_only"]            # noqa: E731
    pg = lambda o: res[o]["per_gram_shape_only"]         # noqa: E731
    bars(axes[0],
         lambda o: raw(o)["on_target"]["spearman_rho"],
         lambda o: pg(o)["vs_raw_objective"]["spearman_rho"],
         lambda o: raw(o)["on_target"]["spearman_p_perm"],
         lambda o: pg(o)["vs_raw_objective"]["spearman_p_perm"],
         "held-out Spearman rho vs the RAW objective",
         "A. Ranking articles by the real objective\n(the decision an optimizer makes)")
    axes[0].legend(fontsize=9, loc="lower left", frameon=False)
    bars(axes[1],
         lambda o: raw(o)["on_target"]["within_batch"]["mean_rho"],
         lambda o: pg(o)["vs_raw_objective"]["within_batch"]["mean_rho"],
         lambda o: raw(o)["on_target"]["within_batch"]["perm_p"],
         lambda o: pg(o)["vs_raw_objective"]["within_batch"]["perm_p"],
         "mean within-batch Spearman rho vs the RAW objective",
         "B. The same, inside each print session\n(no session offsets to lean on)")
    bars(axes[2],
         lambda o: raw(o)["mass_leverage_on_residuals"]["pooled_r"],
         lambda o: pg(o)["mass_leverage_on_residuals"]["pooled_r"],
         lambda o: raw(o)["mass_leverage_on_residuals"]["pooled_perm_p"],
         lambda o: pg(o)["mass_leverage_on_residuals"]["pooled_perm_p"],
         "Pearson r, weighed mass vs held-out residual",
         "C. The goal, tested: can mass predict what the\n"
         "mass-blind model got wrong? (0 = no)")
    fig.suptitle("Mass out of the fit space (5 shape coordinates), objective raw vs "
                 "divided by mass: held-out LOGO-CV, 35 design folds, NUTS 256/512 "
                 "(* permutation p < 0.05)", fontsize=12.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = FIGS / "shape-only-per-gram-logocv.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"-> {out}")


# ------------------------------------------------------------ main
def main() -> int:
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(NORMALIZED_CSV)
    assert len(df) == 44 and set(df.batch) == set(BATCHES)

    dec = decode(df, rng)
    fig_decode(df, dec)
    res = heldout(df, rng)
    fig_logo(res)

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items() if not str(k).startswith("_")}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        return o

    metrics = {
        "provenance": {
            "generated_by": "analysis/cv-signal-audit/score_shape_only_per_gram.py",
            "question": "PR #111, sgbaird 2026-09-25: take mass out of the input "
                        "space and divide the objectives by mass; and is 'division "
                        "fixes the within-session confound and creates a pooled "
                        "one' (Section 9.3) true?",
            "seed": SEED, "n_permutations": N_PERM,
            "article_table": NORMALIZED_CSV.name,
            "raw_runs": {k: str(v.relative_to(HERE)) for k, v in RAW_RUNS.items()},
            "per_gram_runs": {k: str(v.relative_to(HERE)) for k, v in PG_RUNS.items()},
        },
        "decode": dec,
        "heldout": res,
    }
    OUT_JSON.write_text(json.dumps(clean(metrics), indent=2) + "\n")
    print(f"-> {OUT_JSON}")

    # ---- console summary -------------------------------------------------
    print("\n=== DECODE: mass vs objective (ln-ln), 44 articles ===")
    for obj in OBJECTIVES:
        for fr in ("raw", "per_gram"):
            e = dec["per_objective"][obj][fr]
            wb, ws = e["within_batch"], e["within_batch_given_shape"]
            print(f"{obj:>14} {fr:>8} | mean signed r {e['mean_signed_r']:+.2f} "
                  f"mean|r| {e['mean_abs_r']:.2f} | pooled {e['pooled_r']:+.2f} | "
                  f"within-batch r {wb['r']:+.2f} (el {wb['elasticity']:+.2f}) | "
                  f"+shape r {ws['r']:+.2f} p {ws['perm_p']:.3f} "
                  f"(el {ws['elasticity']:+.2f}) | w/o {LEVERAGE_ID} "
                  f"r {e[f'within_batch_given_shape_without_{LEVERAGE_ID}']['r']:+.2f} "
                  f"p {e[f'within_batch_given_shape_without_{LEVERAGE_ID}']['perm_p']:.3f}")
    wm = dec["within_batch_mass"]
    print(f"within-batch mass sd {wm['sd_g']:.3f} g, given shape "
          f"{wm['sd_g_given_shape']:.3f} g; shape explains "
          f"{100 * wm['share_explained_by_shape']:.0f}%; r with coords "
          + ", ".join(f"{k} {v:+.2f}" for k, v in wm["r_with_coordinate"].items()))
    tw = dec["twin_reliability"]
    print("twin pair Spearman: " + ", ".join(
        f"{k} {v['pair_spearman']:+.2f}" for k, v in tw.items()))

    print("\n=== HELD OUT, shape-only space ===")
    for obj in OBJECTIVES:
        e = res[obj]
        r = e["raw_shape_only"]
        line = (f"{obj:>14} raw: rho {r['on_target']['spearman_rho']:+.2f} "
                f"(p {r['on_target']['spearman_p_perm']:.3f}) within "
                f"{r['on_target']['within_batch']['mean_rho']:+.2f} | mass->resid "
                f"{r['mass_leverage_on_residuals']['pooled_r']:+.2f} "
                f"(p {r['mass_leverage_on_residuals']['pooled_perm_p']:.3f})")
        if "per_gram_shape_only" in e:
            p = e["per_gram_shape_only"]
            line += (f"\n{'':>14} /m : on target {p['on_target']['spearman_rho']:+.2f} "
                     f"(p {p['on_target']['spearman_p_perm']:.3f}); vs raw "
                     f"{p['vs_raw_objective']['spearman_rho']:+.2f} (p "
                     f"{p['vs_raw_objective']['spearman_p_perm']:.3f}) within "
                     f"{p['vs_raw_objective']['within_batch']['mean_rho']:+.2f}; "
                     f"restored {p['vs_raw_objective_mass_restored']['spearman_rho']:+.2f}"
                     f" | mass->resid {p['mass_leverage_on_residuals']['pooled_r']:+.2f}"
                     f" (p {p['mass_leverage_on_residuals']['pooled_perm_p']:.3f})"
                     f" | archived match {e['archived_diagnostics_match_per_gram']}")
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
