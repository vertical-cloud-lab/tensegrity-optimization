"""Score the mass-normalized LOGO runs against the committed baselines.

PR #111 follow-up (sgbaird, 2026-09-25): "just divide each of the
objectives by mass". ``rerun_logocv_mass_normalized.py`` re-ran the
audit's standard LOGO protocol with ``t180`` and ``e_reb_mJ`` divided by
each article's weighed mass, in two fit spaces that both **keep mass as
an input** (the campaign's 12 parameters, and the rounds-1-and-2 six).
This scores those runs next to the three committed raw-objective runs.

Three views, because a rank statistic computed on a transformed target
is not by itself comparable with one computed on the original:

* ``on_transformed``: predictions against the per-gram values the model
  was actually fitted to. This is the number the run "earns", and it is
  inflated by the 1/m component the transform writes into the target.
* ``on_raw``: the same predictions ranked against the **raw** objective,
  which is the decision anyone actually makes (rank these designs by
  transmissibility). Multiplying a per-gram prediction back by the
  article's own mass is the like-for-like reconstruction, so both the
  bare prediction and the mass-restored one are scored.
* ``vs_mass_alone``: the same held-out folds, predicting from nothing
  but the article's weighed mass (``mass_normalization_checks.py``
  check 6). If a run does not beat this, it learned nothing the scale
  did not already say.

Plus the memorization check Section 6 turns on: whether the model still
gives the two prints of one design different predictions. Mass is what
makes reprint twins addressable, and dividing the *objective* by mass
cannot change that, so the twins should stay separable in every run that
keeps mass in the space.

Outputs: metrics-mass-normalized-logocv.json,
figures/mass-normalized-logocv.png, and a headline table on stdout.
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
from mass_normalization_checks import _logo_mass_only

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"
OUT_JSON = HERE / "metrics-mass-normalized-logocv.json"
CSV_NAME = "t3-prism-bo-round5-logocv.csv"
DIAG_NAME = "t3-prism-bo-round5-logocv-diagnostics.json"

RAW_RUNS = {
    "raw|12p": DATA / "full-nuts-rerun",
    "raw|6p": DATA / "ablation-six-param",
    "raw|5p shape-only": DATA / "ablation-shape-only",
}
NORM_RUNS = {
    "per-gram|12p": DATA / "objective-per-gram",
    "per-gram|6p": DATA / "objective-per-gram-six-param",
}
RAW_METRICS = ("t180", "e_reb_mJ")
NORM_METRICS = ("t180_per_g", "e_reb_mJ_per_g")
SOURCE_OF = dict(zip(NORM_METRICS, RAW_METRICS))
BATCHES = ("seed", "r2d2c", "drran", "2dran", "corny")
N_PERM_BATCH = 20_000


def within_batch(d: pd.DataFrame, rng) -> dict:
    per, groups = {}, []
    for b in BATCHES:
        g = d[d.batch == b]
        per[b] = float(stats.spearmanr(g.observed, g.predicted).statistic)
        groups.append((g.observed.to_numpy(), g.predicted.to_numpy()))
    mean_obs = float(np.mean(list(per.values())))
    null = np.empty(N_PERM_BATCH)
    for i in range(N_PERM_BATCH):
        null[i] = np.mean([stats.spearmanr(o, rng.permutation(p)).statistic
                           for o, p in groups])
    p = float((np.sum(np.abs(null) >= abs(mean_obs) - 1e-12) + 1)
              / (N_PERM_BATCH + 1))
    return {"per_batch_rho": per, "mean_rho": mean_obs, "perm_p": p}


def load_run(run_dir: Path) -> pd.DataFrame:
    logo = base.load_logo(run_dir / CSV_NAME)
    diag = json.loads((run_dir / DIAG_NAME).read_text())
    logo.attrs["diagnostics"] = diag
    return logo


def twin_separation(d: pd.DataFrame) -> dict:
    """Does the model give the two prints of one design different answers?

    ``predicted_gap_over_design_sd`` is the mean absolute difference
    between the twins' predictions, in units of the between-design sd of
    the predictions. Zero means the model cannot tell the twins apart
    (which is what a space without mass forces); anything well above zero
    means it can, which is the addressability Section 6 identified.
    """
    p1 = d[d.batch == "drran"].set_index("design").sort_index()
    p2 = d[d.batch == "2dran"].set_index("design").sort_index()
    common = p1.index.intersection(p2.index)
    gap = np.abs(p1.loc[common].predicted.to_numpy()
                 - p2.loc[common].predicted.to_numpy())
    design_sd = float(d.groupby("design").predicted.mean().std(ddof=1))
    return {
        "n_pairs": int(len(common)),
        "mean_predicted_gap": float(gap.mean()),
        "between_design_pred_sd": design_sd,
        "predicted_gap_over_design_sd": float(gap.mean() / design_sd)
        if design_sd > 0 else float("nan"),
        "observed_pair_rho": float(stats.spearmanr(
            p1.loc[common].observed, p2.loc[common].observed).statistic),
        "predicted_pair_rho": float(stats.spearmanr(
            p1.loc[common].predicted, p2.loc[common].predicted).statistic),
    }


def score_metric(d: pd.DataFrame, rng) -> dict:
    m = base.held_out_metrics(d.observed.to_numpy(), d.predicted.to_numpy(),
                              d.predicted_sem.to_numpy(),
                              d.design.to_numpy(), rng)
    m["within_batch"] = within_batch(d, rng)
    g = d.groupby("design").agg(observed=("observed", "mean"),
                                predicted=("predicted", "mean"),
                                predicted_sem=("predicted_sem", "mean"))
    m["design_level"] = base.held_out_metrics(
        g.observed.to_numpy(), g.predicted.to_numpy(),
        g.predicted_sem.to_numpy(), g.index.to_numpy(), rng)
    m["twins"] = twin_separation(d)
    return m



RUN_ORDER = ["raw|12p", "per-gram|12p", "raw|6p", "per-gram|6p",
             "raw|5p shape-only"]
RUN_COLOR = {"raw|12p": "#3b6ea5", "per-gram|12p": "#c1553b",
             "raw|6p": "#6b93c4", "per-gram|6p": "#e0805f",
             "raw|5p shape-only": "#4b8a5a"}


def make_figure(results, ref, logo_norm):
    names = [n for n in RUN_ORDER if n in results]
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.6))

    def bars(ax, getter, title, ylabel, ref_line=None, ref_label=None):
        vals = [getter(n) for n in names]
        xs = np.arange(len(names))
        b = ax.bar(xs, vals, 0.62, color=[RUN_COLOR[n] for n in names])
        for rect, v in zip(b, vals):
            if v is None or not np.isfinite(v):
                continue
            ax.text(rect.get_x() + rect.get_width() / 2,
                    v + (0.025 if v >= 0 else -0.06), f"{v:+.2f}",
                    ha="center", fontsize=9)
        if ref_line is not None:
            ax.axhline(ref_line, ls=":", lw=1.6, color="0.3")
            ax.text(0.01, ref_line, f" {ref_label}", fontsize=8.5,
                    va="bottom", ha="left", color="0.3")
        ax.axhline(0, color="k", lw=0.9)
        finite = [v for v in vals if v is not None and np.isfinite(v)]
        if finite:
            lo, hi = min(finite + [0.0]), max(finite + [0.0])
            pad = 0.16 * max(hi - lo, 1e-9)
            ax.set_ylim(lo - pad, hi + pad)
        ax.set_xticks(xs)
        ax.set_xticklabels([n.replace("|", "\n") for n in names], fontsize=8.5)
        ax.set_ylabel(ylabel, fontsize=9.5)
        ax.set_title(title, fontsize=10.5)

    bars(axes[0, 0],
         lambda n: results[n]["on_transformed"]["t180"]["spearman_rho"],
         "A. t180, ranked against the target each run was fitted to\n"
         "(per-gram runs are graded on the per-gram values)",
         "article rho_s (n = 44)",
         ref["t180"]["per_gram"]["mass_alone_spearman_on_transformed"],
         "mass alone, per-gram target")
    bars(axes[0, 1],
         lambda n: results[n]["on_raw"]["t180"]["spearman_rho"],
         "B. The decision view: every run ranked against RAW t180\n"
         "(what you actually choose designs on)",
         "article rho_s vs raw t180 (n = 44)",
         ref["t180"]["per_gram"]["mass_alone_spearman_on_raw"],
         "mass alone, per-gram target")
    bars(axes[1, 0],
         lambda n: results[n]["on_transformed"]["e_reb_mJ"]["spearman_rho"],
         "C. Rebound. Dividing by mass recovers e_rebound exactly,\n"
         "so this is the one objective the transform is built for",
         "article rho_s (n = 44)")
    bars(axes[1, 1],
         lambda n: results[n]["on_transformed"]["t180"]["twins"][
             "predicted_gap_over_design_sd"],
         "D. Can the model still tell the two prints of one design apart?\n"
         "Mass is the only coordinate that separates them",
         "predicted twin gap / between-design sd")
    axes[1, 1].set_ylim(0, max(0.34, axes[1, 1].get_ylim()[1]))

    fig.suptitle("Objectives divided by mass, mass kept in the fit space: "
                 "held-out LOGO-CV against the committed baselines",
                 fontsize=13, y=0.985)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    out = FIGS / "mass-normalized-logocv.png"
    fig.savefig(out, dpi=150)
    print(f"-> {out}")


def main() -> int:
    rng = np.random.default_rng(20260925)
    table = pd.read_csv(DATA / "mass-normalized-objectives.csv")
    mass_of = dict(zip(table.print_id, table.mass_g))
    raw_of = {src: dict(zip(table.print_id, table[src])) for src in RAW_METRICS}

    results, missing = {}, []
    for name, run_dir in RAW_RUNS.items():
        if not (run_dir / CSV_NAME).exists():
            missing.append(name)
            continue
        logo = load_run(run_dir)
        results[name] = {"on_transformed": {}, "on_raw": {},
                         "diagnostics_check": {}}
        for metric in RAW_METRICS:
            d = logo[logo.metric == metric]
            s = score_metric(d, rng)
            diag = logo.attrs["diagnostics"]
            s["matches_archived_diagnostics"] = bool(
                abs(s["pearson_r"] - diag["Correlation coefficient"][metric]) < 1e-4
                and abs(s["spearman_rho"] - diag["Rank correlation"][metric]) < 1e-3)
            assert s["matches_archived_diagnostics"], (
                f"{name}/{metric} does not reproduce its archived Ax "
                "diagnostics; refusing to report it")
            # raw runs: the transformed and raw views are the same thing
            results[name]["on_transformed"][metric] = s
            results[name]["on_raw"][metric] = s

    for name, run_dir in NORM_RUNS.items():
        if not (run_dir / CSV_NAME).exists():
            missing.append(name)
            continue
        logo = load_run(run_dir)
        results[name] = {"on_transformed": {}, "on_raw": {}}
        for metric in NORM_METRICS:
            src = SOURCE_OF[metric]
            d = logo[logo.metric == metric].copy()
            s = score_metric(d, rng)
            diag = logo.attrs["diagnostics"]
            s["matches_archived_diagnostics"] = bool(
                abs(s["pearson_r"] - diag["Correlation coefficient"][metric]) < 1e-4
                and abs(s["spearman_rho"] - diag["Rank correlation"][metric]) < 1e-3)
            assert s["matches_archived_diagnostics"], (
                f"{name}/{metric} does not reproduce its archived Ax "
                "diagnostics; refusing to report it")
            results[name]["on_transformed"][src] = s

            # the decision view: rank the RAW objective. Two reconstructions,
            # the bare per-gram prediction and the mass-restored one.
            raw_obs = np.array([raw_of[src][p] for p in d.print_id])
            mass = np.array([mass_of[p] for p in d.print_id])
            bare = d.copy()
            bare["observed"] = raw_obs
            restored = bare.copy()
            restored["predicted"] = d.predicted.to_numpy() * mass
            restored["predicted_sem"] = d.predicted_sem.to_numpy() * mass
            results[name]["on_raw"][src] = score_metric(bare, rng)
            results[name]["on_raw"][src]["mass_restored"] = score_metric(
                restored, rng)

    # what mass alone buys on the same folds, for reference in both views
    ref = {}
    design = list(table.design)
    mass_arr = table.mass_g.to_numpy()
    for src in RAW_METRICS:
        ref[src] = {}
        for framing, col in (("raw", f"{src}__raw"),
                             ("per_gram", f"{src}__per_gram")):
            pred, obs = _logo_mass_only(mass_arr, table[col].to_numpy(),
                                        design, False)
            ref[src][framing] = {
                "mass_alone_spearman_on_transformed": float(
                    stats.spearmanr(pred, obs).statistic),
                "mass_alone_spearman_on_raw": float(
                    stats.spearmanr(pred, table[f"{src}__raw"]).statistic),
            }

    out = {
        "provenance": {
            "generated_by": "analysis/cv-signal-audit/score_mass_normalized.py",
            "question": "PR #111, sgbaird 2026-09-25: divide the objectives by "
                        "mass; does the held-out skill recover with mass still "
                        "in the fit space",
            "runs_scored": sorted(results),
            "runs_missing": missing,
            "n_permutations_within_batch": N_PERM_BATCH,
        },
        "runs": results,
        "mass_alone_reference": ref,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"-> {OUT_JSON}")
    if missing:
        print(f"  (not yet available: {', '.join(missing)})")

    print("\n=== held-out rank skill, article level (n=44) ===")
    print(f"{'run':>22} | {'t180 (fitted target)':>22} | "
          f"{'t180 vs RAW t180':>22} | {'rebound (fitted)':>18}")
    for name in results:
        t = results[name]["on_transformed"].get("t180")
        tr = results[name]["on_raw"].get("t180")
        e = results[name]["on_transformed"].get("e_reb_mJ")
        if t is None:
            continue
        print(f"{name:>22} | {t['spearman_rho']:+.2f} "
              f"(p {t['spearman_p_perm']:.4f})".ljust(48)[:48]
              + f"| {tr['spearman_rho']:+.2f} "
                f"(p {tr['spearman_p_perm']:.4f})".ljust(24)[:24]
              + f"| {e['spearman_rho']:+.2f} (p {e['spearman_p_perm']:.4f})")

    print("\n=== mass alone on the same folds, for reference ===")
    for src in RAW_METRICS:
        for framing in ("raw", "per_gram"):
            v = ref[src][framing]
            print(f"  {src:>10} {framing:>9}: on fitted target "
                  f"{v['mass_alone_spearman_on_transformed']:+.2f}, "
                  f"vs raw {v['mass_alone_spearman_on_raw']:+.2f}")

    if not missing:
        make_figure(results, ref, None)

    print("\n=== can the model still tell reprint twins apart? ===")
    for name in results:
        t = results[name]["on_transformed"].get("t180")
        if t is None:
            continue
        tw = t["twins"]
        print(f"{name:>22}: predicted twin gap = "
              f"{tw['predicted_gap_over_design_sd']:.2f} x between-design sd")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
