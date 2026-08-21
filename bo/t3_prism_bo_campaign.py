"""Multi-objective BO for the T-3_01 prism campaign: ingest drop results, suggest next batch.

Generated from the Honegumi template (https://arxiv.org/abs/2502.06815,
https://honegumi.readthedocs.io) with options: objective=Multi,
model=Fully Bayesian (SAASBO), existing_data=True, synchrony=Batch,
visualize=True, custom_gen=True (required by the fully Bayesian choice);
all constraint/categorical/fidelity/task options False. The template pins
ax-platform==0.4.3; this script runs unchanged on ax-platform 0.5.0 (same
Service API). Deviations from the rendered template, each forced by the
real campaign rather than preference:

1. The Sobol initialization step is dropped from the GenerationStrategy
   because it already happened physically: PR #35's ``t3_prism_sobol_batch.py``
   drew the 9-point Sobol batch (seed 0) that was printed and tested. The
   strategy therefore starts directly at the SAASBO step.
2. The inline ``X_train``/``y_train`` dataframe is replaced by ingestion of
   the measured campaign summary (``t3-prism-bo-batch-drop-results.csv``,
   snapshotted from PR #86 branch commit 642b8c0, file
   ``data/drop-tests/sobol-campaign/figures/campaign_summary.csv``).
3. The optimization loop body does not evaluate a dummy objective: the
   "experiment" is a physical print + 101-drop session, so the loop runs
   exactly once, records the suggested batch to CSV, and exits. Results get
   reported back by re-running this script once the next batch is tested.
4. Per-print mass accounting (requested on PR #102). The batch generator's
   constant-mass projection holds solid CAD volume constant, but printed
   grams vary by design (18.5 to 22.3 g: PLA prints at ~57 percent of solid
   density, thin TPU cables ~solid, and the PLA/TPU split varies by design;
   see docs/drop-test-sobol-campaign-analysis.md section 7 on PR #86). Each
   tested article's measured mass therefore enters the objectives and the
   model; see the Objectives section below.

Search space: the base Sobol coordinates from PR #35's generator (not the
as-printed geometry). Each suggestion is a 5-vector (R, H, twist, strut d,
cable d) that feeds straight into ``t3_prism_sobol_batch.py``'s constant-mass
projection to produce printable STLs, exactly like round 1.

Objectives (both minimized), per the campaign analysis doc's BO hand-off
section (docs/drop-test-sobol-campaign-analysis.md on PR #86) and the
energy-absorption review (PR #97), adjusted for per-print mass:

* ``t180``: stabilized CFC-180 transmissibility TOP/CH5 (shock into
  payload). Deliberately kept a ratio, not mass-corrected: it is already
  normalized by the measured input peak, and peak acceleration on the
  payload side is a damage criterion that does not scale with specimen
  mass. t180 does correlate with mass across the batch (the script prints
  the r), but printed mass is a deterministic function of the geometry
  (light articles ARE the PLA-heavy thick-strut/thin-cable corner), so with
  n = 7 designs that correlation is confounded with the geometry effect the
  campaign is trying to learn, and regressing it out would remove signal.
  The SAAS model sees mass through the ``mass_g`` tracking metric instead.
* ``e_reb_mJ``: absolute rebound energy returned to the payload per drop,
  e_rebound * m_printed * g * h_drop (h = 60 in). The raw ``e_rebound`` is
  a fraction of the impact energy, and at fixed drop height the impact
  energy scales with the article's printed mass, so equal fractions on a
  18.5 g and a 22.3 g article differ by ~20 percent in the millijoules the
  payload actually receives. Minimizing the millijoules compares designs on
  delivered energy and re-penalizes the grams a design adds. Its SEM folds
  the print-to-print mass scatter (sd 0.457 g, from the spec-08 triplicate
  dea4ls/bag26v/ghmj4y, all one design) in quadrature with the per-drop
  SEM, so the n-of-1-article mass channel is now modeled. The remaining
  ~2 percent t180 print floor is still not (no mass-free estimate of it
  exists).

``mass_g`` is also attached as a tracking metric, so the SAAS model learns
printed mass as a function of the base coordinates from the weighed
articles, and every suggested design is reported with its predicted
as-printed mass (``pred_mass_g_mean`` in the suggestions CSV). Trades off
against nothing directly (it is not an objective), but deconfounds the
model and tells the next print session what to expect on the scale.

Ingestion notes, current as of the 2026-08-21 upload (8 of 9 specimens):

* ``amdjwm`` maps to no known print ID or Sobol spec (open item 1 in the
  campaign doc), so it cannot be attached and is skipped with a warning.
  Re-run once identified; its row already carries the objectives.
* The S0 reference prism ``bpx68c`` is off-Sobol but its base coordinates
  (25, 70, 60, 6, 3) sit inside the search space, so it is attached.
* Printed-but-untested specs (03, 06, 07) are attached as pending trials so
  the acquisition avoids re-suggesting near them.

Usage (from the repo root)::

    pip install ax-platform==0.5.0 pandas matplotlib
    python bo/t3_prism_bo_campaign.py            # writes suggestions + figure
    python bo/t3_prism_bo_campaign.py --batch-size 9 --round 1
    python bo/t3_prism_bo_campaign.py --plot-only  # redraw the figure only
                                                   # (pandas + matplotlib)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ax is imported inside main() so that --plot-only (redraw the figure from the
# recorded CSVs) needs only pandas + matplotlib, no model refit

BO_DIR = Path(__file__).resolve().parent

# define these names as variables for reuse (Honegumi convention)
obj1_name = "t180"
obj2_name = "e_reb_mJ"
mass_metric = "mass_g"

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]

G_M_S2 = 9.80665
DROP_H_M = 1.524  # 60 in drop height (issue #98 campaign protocol)
# Print-to-print mass scatter: sample sd of the spec-08 triplicate
# (dea4ls 22.29 g, bag26v 21.42 g, ghmj4y 22.10 g), the only design printed
# more than once. Used as the design-level mass noise everywhere.
MASS_PRINT_SD_G = 0.457

# Search space: identical to PARAMETERS in bo/t3_prism_sobol_batch.py (PR #35),
# the space the printed Sobol batch was drawn from.
PARAMETERS = [
    {"name": "R_mm", "type": "range", "bounds": [25.0, 40.0], "value_type": "float"},
    {"name": "H_mm", "type": "range", "bounds": [60.0, 110.0], "value_type": "float"},
    {"name": "twist_deg", "type": "range", "bounds": [40.0, 80.0], "value_type": "float"},
    {"name": "strut_d_mm", "type": "range", "bounds": [6.0, 12.0], "value_type": "float"},
    {"name": "cable_d_mm", "type": "range", "bounds": [3.0, 5.5], "value_type": "float"},
]

# Base coordinates of the S0 reference prism (bpx68c): the T3 base design,
# printed at uniform scale 1.1538 (issue #98, 2026-08-17). In-bounds, so it
# is valid existing data even though it was not part of the Sobol draw.
S0_BASE_PARAMS = {
    "R_mm": 25.0,
    "H_mm": 70.0,
    "twist_deg": 60.0,
    "strut_d_mm": 6.0,
    "cable_d_mm": 3.0,
}


def load_training_data(results_path: Path, design_path: Path):
    """Join measured objectives onto base Sobol coordinates.

    Returns (X_train, y_train, labels, masses, pending) where pending holds
    the base coordinates of designed-and-printed specs with no results yet.
    """
    results = pd.read_csv(results_path, dtype={"spec": "string"})
    design = pd.read_csv(design_path).set_index("specimen")

    X_train, y_train, labels, masses = [], [], [], []
    for _, row in results.iterrows():
        spec = row["spec"]
        spec = None if pd.isna(spec) else str(spec).strip()
        if not spec:
            print(
                f"WARNING: skipping specimen {row['specimen']!r}: no Sobol spec "
                "mapping (see campaign doc open item 1). Re-run once identified."
            )
            continue
        if pd.isna(row["mass_g"]):
            print(
                f"WARNING: skipping specimen {row['specimen']!r} (spec {spec}): "
                "no recorded mass, so the mass-aware objective cannot be built."
            )
            continue
        if spec == "S0":
            params = dict(S0_BASE_PARAMS)
        else:
            base = design.loc[int(spec)]
            params = {name: float(base[name]) for name in PARAM_NAMES}
        n = float(row["n_valid"])
        mass_g = float(row["mass_g"])
        # absolute rebound energy per drop, from the tested article's own
        # measured mass: e_rebound * m * g * h  (grams * m/s^2 * m == mJ)
        e_mean = float(row["e_rebound_mean"])
        e_sem = float(row["e_rebound_sd"]) / np.sqrt(n)
        e_reb_mJ = e_mean * mass_g * G_M_S2 * DROP_H_M
        # per-drop SEM and the design-level print-to-print mass scatter in
        # quadrature; the ~2 percent t180 print floor remains unmodeled
        e_reb_sem = e_reb_mJ * float(np.hypot(e_sem / e_mean, MASS_PRINT_SD_G / mass_g))
        y_train.append(
            {
                obj1_name: (float(row["t180_mean"]), float(row["t180_sd"]) / np.sqrt(n)),
                obj2_name: (e_reb_mJ, e_reb_sem),
                mass_metric: (mass_g, MASS_PRINT_SD_G),
            }
        )
        X_train.append(params)
        labels.append(f"{row['specimen']} (spec {spec})")
        masses.append(mass_g)

    tested_specs = {
        int(s) for s in results["spec"].dropna() if str(s).strip() not in ("", "S0")
    }
    pending = []
    for spec_idx in sorted(set(design.index) - tested_specs):
        base = design.loc[spec_idx]
        pending.append(
            (f"spec {spec_idx:02d}", {name: float(base[name]) for name in PARAM_NAMES})
        )
    return X_train, y_train, labels, masses, pending


# ---- figure styling (presentation-ready, per PR #102 review) -------------
INK = "#0b0b0b"          # observed-point outlines and axis ink
LABEL_GRAY = "#83827d"   # print IDs: present but de-emphasized
FRONT_BLUE = "#2a78d6"   # Pareto front
SUGGEST_ORANGE = "#eb6834"  # next-round suggestions


def observed_frame(y_train, labels):
    """Tidy frame of the tested articles: print ID plus both objectives."""
    return pd.DataFrame(
        {
            "print_id": [label.split(" ")[0] for label in labels],
            obj1_name: [y[obj1_name][0] for y in y_train],
            obj2_name: [y[obj2_name][0] for y in y_train],
        }
    )


def pareto_mask(xs, ys):
    """Non-dominated mask for a two-objective minimization problem."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    return np.array(
        [
            not np.any((xs <= x) & (ys <= y) & ((xs < x) | (ys < y)))
            for x, y in zip(xs, ys)
        ]
    )


def render_objective_figure(observed, suggestions, round_number):
    """Single objective-space panel, sized and styled for slides.

    The Honegumi template's second (parallel-coordinates) panel is omitted.
    The front is the non-dominated set of the *observed* points, which for
    round 1 is the same three articles as Ax's model-predicted Pareto set.
    """
    front = observed[pareto_mask(observed[obj1_name], observed[obj2_name])]
    front = front.sort_values(obj1_name)

    with plt.rc_context(
        {
            "font.size": 15,
            "axes.labelsize": 17,
            "axes.labelcolor": INK,
            "xtick.labelsize": 15,
            "ytick.labelsize": 15,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "axes.edgecolor": "#4a4a47",
        }
    ):
        fig, ax = plt.subplots(figsize=(9.0, 5.6), dpi=220)

        ax.scatter(
            observed[obj1_name], observed[obj2_name],
            fc="none", ec=INK, s=110, lw=1.8, label="Tested (round 1)", zorder=3,
        )
        ax.plot(
            front[obj1_name], front[obj2_name],
            color=FRONT_BLUE, lw=2.6, marker="o", ms=9, zorder=2,
            label="Pareto front",
        )
        ax.scatter(
            suggestions[f"pred_{obj1_name}_mean"], suggestions[f"pred_{obj2_name}_mean"],
            marker="D", s=95, fc=SUGGEST_ORANGE, ec="white", lw=1.2, zorder=4,
            label=f"Suggested round {round_number + 1}",
        )
        for _, row in observed.iterrows():
            ax.annotate(
                row["print_id"], (row[obj1_name], row[obj2_name]),
                textcoords="offset points", xytext=(9, 6),
                fontsize=12.5, color=LABEL_GRAY,
            )

        ax.set_xlabel("Shock transmissibility t180 (lower is better)")
        # Horizontal y-axis label, parked above the axis so it reads at a glance
        # from a slide instead of asking the audience to tilt their head.
        ax.set_ylabel(
            "Rebound energy to payload\n(mJ per drop, lower is better)",
            rotation=0, ha="left", va="bottom", linespacing=1.4,
        )
        ax.yaxis.set_label_coords(-0.035, 1.04)
        ax.set_xlim(0.80, 1.12)
        ax.set_ylim(5.5, 14.8)
        ax.set_xticks(np.arange(0.8, 1.101, 0.1))
        ax.set_yticks(np.arange(6, 14.1, 2))
        ax.grid(False)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.legend(
            loc="upper left", bbox_to_anchor=(1.02, 1.0),
            frameon=False, fontsize=14, handletextpad=0.6, borderaxespad=0.0,
        )

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        out_png = fig_dir / f"t3-prism-bo-round{round_number}-pareto.png"
        fig.savefig(out_png, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    print(
        "Pareto-front articles: "
        + ", ".join(
            f"{r['print_id']} (t180 {r[obj1_name]:.3f}, {r[obj2_name]:.1f} mJ)"
            for _, r in front.iterrows()
        )
    )
    return out_png


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--results",
        type=Path,
        default=BO_DIR / "t3-prism-bo-batch-drop-results.csv",
        help="campaign summary CSV (snapshot of PR #86 campaign_summary.csv)",
    )
    ap.add_argument(
        "--design",
        type=Path,
        default=BO_DIR / "t3-prism-bo-batch.csv",
        help="Sobol batch design table (base coordinates), from PR #35",
    )
    ap.add_argument("--batch-size", type=int, default=9, help="prints per round (9 plates)")
    ap.add_argument("--round", type=int, default=1, help="suggestion round number, for file names")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--plot-only",
        action="store_true",
        help=(
            "redraw the figure from the recorded results and suggestions CSVs "
            "without refitting the model (needs only pandas + matplotlib)"
        ),
    )
    args = ap.parse_args(argv)

    X_train, y_train, labels, masses, pending = load_training_data(args.results, args.design)

    if args.plot_only:
        suggestions = pd.read_csv(
            BO_DIR / f"t3-prism-bo-suggestions-round{args.round}.csv"
        )
        print(
            f"Figure saved to "
            f"{render_objective_figure(observed_frame(y_train, labels), suggestions, args.round)}"
        )
        return 0

    from ax.core.observation import ObservationFeatures
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
    from ax.service.ax_client import AxClient, ObjectiveProperties

    n_train = len(X_train)
    print(f"Attaching {n_train} completed trials; {len(pending)} printed-but-untested pending.")

    # mass diagnostic: printed mass is set by the geometry (constant solid
    # volume + design-dependent PLA/TPU split), so any correlation with the
    # objectives is confounded with the geometry effect; report, don't correct
    t180_means = np.array([y[obj1_name][0] for y in y_train])
    masses_arr = np.array(masses)
    r_mass_t180 = float(np.corrcoef(masses_arr, t180_means)[0, 1])
    print(
        f"Masses of tested articles: {masses_arr.min():.2f} to {masses_arr.max():.2f} g "
        f"(CV {100 * masses_arr.std(ddof=1) / masses_arr.mean():.1f} percent); "
        f"corr(mass, t180) r = {r_mass_t180:.2f} (confounded with geometry, "
        "handled via the mass_g tracking metric, not regression)"
    )

    # Fully Bayesian (SAASBO) generation strategy. The Sobol step from the
    # Honegumi template is omitted: initialization was the physical batch.
    gs = GenerationStrategy(
        steps=[
            GenerationStep(
                # https://arxiv.org/abs/2103.00349
                model=Models.SAASBO,
                num_trials=-1,  # no limit on trials (final model step)
                max_parallelism=max(args.batch_size, len(pending) + args.batch_size),
            ),
        ]
    )

    ax_client = AxClient(generation_strategy=gs, random_seed=args.seed, verbose_logging=False)
    ax_client.create_experiment(
        name="t3_prism_drop_campaign",
        parameters=PARAMETERS,
        objectives={
            obj1_name: ObjectiveProperties(minimize=True),
            obj2_name: ObjectiveProperties(minimize=True),
        },
        # printed mass as a learned function of the base coordinates, so
        # suggestions carry a predicted as-printed mass (not an objective)
        tracking_metric_names=[mass_metric],
    )

    # Add existing data to the AxClient
    for parameterization, results_i in zip(X_train, y_train):
        # signal to Ax that you intend to carry out a particular trial
        _, trial_index = ax_client.attach_trial(parameterization)
        # pass the (historically available) outcome for that trial
        ax_client.complete_trial(trial_index=trial_index, raw_data=results_i)

    # printed but not yet tested: attach without completing so the acquisition
    # treats them as pending points
    pending_indices = {}
    for label, parameterization in pending:
        _, trial_index = ax_client.attach_trial(parameterization)
        pending_indices[trial_index] = label
        print(f"  pending trial {trial_index}: {label}")

    # one physical round per script run: fit + suggest the next batch
    # (note the plural "trials" for batch optimization)
    parameterizations, optimization_complete = ax_client.get_next_trials(args.batch_size)

    # model predictions (posterior mean +/- sd) for the suggested designs
    model = ax_client.generation_strategy.model
    obs_feats = [
        ObservationFeatures(parameters=dict(p)) for p in parameterizations.values()
    ]
    f_mean, f_cov = model.predict(obs_feats)

    rows = []
    for j, (trial_index, parameterization) in enumerate(parameterizations.items()):
        row = {"round": args.round, "trial_index": trial_index}
        row.update({name: parameterization[name] for name in PARAM_NAMES})
        for metric in (obj1_name, obj2_name, mass_metric):
            row[f"pred_{metric}_mean"] = f_mean[metric][j]
            row[f"pred_{metric}_sd"] = float(np.sqrt(f_cov[metric][metric][j]))
        # implied rebound fraction at the predicted mass, for comparison
        # with the raw e_rebound column of the results CSV
        row["pred_e_rebound_approx"] = row[f"pred_{obj2_name}_mean"] / (
            row[f"pred_{mass_metric}_mean"] * G_M_S2 * DROP_H_M
        )
        rows.append(row)
    suggestions = pd.DataFrame(rows)

    out_csv = BO_DIR / f"t3-prism-bo-suggestions-round{args.round}.csv"
    suggestions.to_csv(out_csv, index=False, float_format="%.4f")
    print(f"\nSuggested batch (recorded to {out_csv}):")
    print(suggestions.to_string(index=False))

    # persist full experiment state (trials, data, generation strategy)
    snapshot = BO_DIR / f"t3-prism-bo-ax-client-round{args.round}.json"
    ax_client.save_to_json_file(str(snapshot))
    print(f"AxClient snapshot saved to {snapshot}")

    # ---- visualization (Honegumi visualize=True block, adapted) ----------
    # presentation-ready single panel; the parallel-coordinates panel that the
    # template pairs with it was dropped on review (PR #102)
    out_png = render_objective_figure(observed_frame(y_train, labels), suggestions, args.round)
    print(f"Figure saved to {out_png}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
