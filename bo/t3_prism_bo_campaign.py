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
    python bo/t3_prism_bo_campaign.py --prototype-next-round  # see below

Figures. ``--plot-only`` redraws the objective-space panel from the recorded
CSVs (no model refit, ~1 s). ``--prototype-next-round`` draws the layout the
campaign will want once the next batch comes back: each orange diamond joined
by a straight path to where that article actually landed, which is then drawn
as an open circle like any other tested article, with the Pareto front
recomputed over both rounds and the previous front left dashed underneath.
The round-2 outcomes it uses are SYNTHETIC (nothing has been printed or
dropped yet); see ``synthesize_round2_outcomes``, which is the single function
to replace with the measured summary when the real numbers arrive. That run
also writes the animated version of the same figure (GIF plus MP4, ~7.5 s,
last frame identical to the still); pass ``--no-animation`` to skip it. The
MP4 needs ffmpeg on PATH; without it only a Pillow-written GIF is produced.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
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
# Matches the hand-made reference posted on PR #102 (comment 5373145690):
# no legend box (series are named by leader-line callouts in the plot area),
# detached left/bottom spines, no grid, gray print IDs, large type.
INK = "#0b0b0b"          # observed-point outlines and axis ink
LABEL_GRAY = "#83827d"   # print IDs: present but de-emphasized
LEADER_GRAY = "#8d8c88"  # callout leader lines
FRONT_BLUE = "#2a78d6"   # Pareto front
SUGGEST_ORANGE = "#eb6834"  # next-round suggestions

# Humanist sans first (the reference figure's face), degrading to whatever a
# given machine has. Figures re-rendered elsewhere may pick a different face.
FIG_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Source Sans Pro", "Source Sans 3", "Open Sans", "Lato",
        "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans",
    ],
    "font.size": 20,
    "axes.labelsize": 22,
    "axes.labelcolor": INK,
    "xtick.labelsize": 21,
    "ytick.labelsize": 21,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.edgecolor": "#4a4a47",
    "axes.linewidth": 1.6,
    "xtick.major.size": 6,
    "ytick.major.size": 6,
    "xtick.major.width": 1.6,
    "ytick.major.width": 1.6,
}

Y_LABEL = "Rebound energy to payload\n(mJ per drop, lower is better)"
X_LABEL = "Shock transmissibility t180 (lower is better)"

# Candidate label placements, in points relative to the marker, tried in
# order until one lands clear of the other labels and markers. Hand-tuned
# offsets would break the moment the data moves, which it will every round.
LABEL_CANDIDATES = [
    (12, 7), (12, -20), (-12, 7), (-12, -20),
    (12, 20), (-12, 20), (0, 24), (0, -30),
    (28, -6), (-28, -6),
]


def _nice_ticks(lo, hi, step):
    """Tick array at `step` covering [lo, hi], snapped to multiples of step."""
    first = np.floor(lo / step) * step
    last = np.ceil(hi / step) * step
    return np.arange(first, last + step / 2, step)


def _style_axes(ax, xlim, ylim, xticks, yticks):
    """Detached left/bottom spines, no grid, slide-sized ticks."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.grid(False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_position(("outward", 14))
    # Spines stop at the outermost ticks, so the axes read as two rules
    # rather than a box corner.
    ax.spines["bottom"].set_bounds(xticks[0], xticks[-1])
    ax.spines["left"].set_bounds(yticks[0], yticks[-1])

    ax.set_xlabel(X_LABEL, labelpad=12)
    # Horizontal y-axis label, parked above the axis so it reads at a glance
    # from a slide instead of asking the audience to tilt their head.
    ax.set_ylabel(Y_LABEL, rotation=0, ha="left", va="bottom", linespacing=1.35)
    ax.yaxis.set_label_coords(-0.045, 1.06)


def _callout(ax, text, xy, xytext, color, leader=None, ha="left", va="center"):
    """Named series label with a thin leader line, in place of a legend.

    Returns the Annotation so callers can fade it (see the animation).
    """
    return ax.annotate(
        text,
        xy=xy,
        xycoords="data",
        xytext=xytext,
        textcoords="axes fraction",
        color=color,
        ha=ha,
        va=va,
        arrowprops=dict(
            arrowstyle="-",
            color=leader if leader is not None else color,
            lw=1.8,
            alpha=0.75,
            shrinkA=10,
            shrinkB=10,
        ),
        zorder=6,
    )


def _axes_frac(ax, xy, dx, dy):
    """Axes-fraction position offset from a data point, kept inside the axes."""
    fx, fy = ax.transLimits.transform(xy)
    return float(np.clip(fx + dx, 0.02, 0.98)), float(np.clip(fy + dy, 0.03, 0.98))


def _label_points(ax, frame, id_col, x_col, y_col, color=LABEL_GRAY, fontsize=17):
    """Place point labels, greedily avoiding other labels and markers.

    Boxes are estimated rather than measured (no renderer round trip), which
    is enough to keep IDs legible as the point cloud moves round to round.
    """
    pts = ax.transData.transform(frame[[x_col, y_col]].to_numpy(float))
    dpp = ax.figure.dpi / 72.0  # points -> display pixels
    marker_r = 11 * dpp
    taken = [(x - marker_r, y - marker_r, x + marker_r, y + marker_r) for x, y in pts]

    def overlaps(box):
        return any(
            box[0] < t[2] and t[0] < box[2] and box[1] < t[3] and t[1] < box[3]
            for t in taken
        )

    anns = []
    for (px, py), (_, row) in zip(pts, frame.iterrows()):
        text = str(row[id_col])
        w = 0.56 * fontsize * len(text) * dpp
        h = 1.25 * fontsize * dpp
        for dx, dy in LABEL_CANDIDATES:
            x0 = px + dx * dpp if dx >= 0 else px + dx * dpp - w
            y0 = py + dy * dpp
            box = (x0, y0, x0 + w, y0 + h)
            if not overlaps(box):
                break
        taken.append(box)
        anns.append(
            ax.annotate(
                text,
                (row[x_col], row[y_col]),
                textcoords="offset points",
                xytext=(dx, dy),
                ha="left" if dx >= 0 else "right",
                va="bottom",
                fontsize=fontsize,
                color=color,
                zorder=5,
            )
        )
    return anns


def _front_anchor(front, frac=0.45):
    """Point at `frac` of the way along the front polyline, for a callout."""
    xs = front[obj1_name].to_numpy(float)
    ys = front[obj2_name].to_numpy(float)
    if len(xs) < 2:
        return float(xs[0]), float(ys[0])
    # Interpolate in axes-ish units by normalizing each objective's range
    xr = max(float(np.ptp(xs)), 1e-9)
    yr = max(float(np.ptp(ys)), 1e-9)
    seg = np.hypot(np.diff(xs) / xr, np.diff(ys) / yr)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    target = frac * cum[-1]
    i = int(np.clip(np.searchsorted(cum, target) - 1, 0, len(seg) - 1))
    t = (target - cum[i]) / max(seg[i], 1e-9)
    return float(xs[i] + t * (xs[i + 1] - xs[i])), float(ys[i] + t * (ys[i + 1] - ys[i]))


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


def pareto_front(frame):
    """Non-dominated subset of `frame`, sorted along the first objective."""
    mask = pareto_mask(frame[obj1_name], frame[obj2_name])
    return frame[mask].sort_values(obj1_name)


def render_objective_figure(observed, suggestions, round_number):
    """Single objective-space panel, sized and styled for slides.

    The Honegumi template's second (parallel-coordinates) panel is omitted.
    The front is the non-dominated set of the *observed* points, which for
    round 1 is the same three articles as Ax's model-predicted Pareto set.
    """
    front = pareto_front(observed)
    on_front = observed["print_id"].isin(front["print_id"])

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=200)

        ax.scatter(
            observed.loc[~on_front, obj1_name], observed.loc[~on_front, obj2_name],
            fc="none", ec=INK, s=190, lw=2.4, zorder=3,
        )
        ax.plot(
            front[obj1_name], front[obj2_name],
            color=FRONT_BLUE, lw=3.4, zorder=2,
        )
        ax.scatter(
            front[obj1_name], front[obj2_name],
            fc=FRONT_BLUE, ec=INK, s=190, lw=2.4, zorder=4,
        )
        ax.scatter(
            suggestions[f"pred_{obj1_name}_mean"], suggestions[f"pred_{obj2_name}_mean"],
            marker="D", s=150, fc=SUGGEST_ORANGE, ec="none", zorder=4,
        )
        _label_points(ax, observed, "print_id", obj1_name, obj2_name)

        _style_axes(
            ax,
            xlim=(0.79, 1.13),
            ylim=(5.4, 15.0),
            xticks=np.arange(0.8, 1.101, 0.1),
            yticks=np.arange(6, 14.1, 2),
        )

        # Series names as leader-line callouts instead of a legend box.
        _callout(
            ax, "Pareto front", _front_anchor(front, 0.35),
            (0.58, 0.96), FRONT_BLUE,
        )
        sug_anchor = suggestions.loc[suggestions[f"pred_{obj2_name}_mean"].idxmin()]
        _callout(
            ax, f"Suggested points (round {round_number + 1})",
            (sug_anchor[f"pred_{obj1_name}_mean"], sug_anchor[f"pred_{obj2_name}_mean"]),
            (0.02, 0.10), SUGGEST_ORANGE,
        )
        obs_anchor = observed.loc[observed[obj1_name].idxmax()]
        _callout(
            ax, "Existing data",
            (obs_anchor[obj1_name], obs_anchor[obj2_name]),
            (0.99, 0.13), INK, leader=LEADER_GRAY, ha="right",
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


# ---- round-2 prototype: predicted vs. measured ---------------------------
# Prototype only. The round-2 articles have not been printed or dropped, so
# the "measured" points below are SYNTHETIC, drawn from the model's own
# predictive distribution for the suggested designs. The figure exists to fix
# the visual grammar now (diamond travels along a straight path to the
# measurement, and lands as an open circle like every other tested article)
# so that swapping the dummy column for the real one is a one-line change.


def synthesize_round2_outcomes(suggestions, seed=0, shrink=0.3):
    """DUMMY round-2 outcomes: predictive mean plus a draw at `shrink` * sd.

    `shrink` is well below 1 on purpose: the SAAS posterior sd after 7 points
    in 5D is wide enough that a full draw scatters the batch off the panel,
    which would make the prototype about the noise rather than about the
    layout it is meant to fix.

    Replace this function's output with the measured campaign summary once
    the round-2 batch has been printed and dropped. Deterministic given
    `seed` so the prototype figure is reproducible.
    """
    rng = np.random.default_rng(seed)
    out = suggestions.copy()
    for obj in (obj1_name, obj2_name):
        mean = suggestions[f"pred_{obj}_mean"].to_numpy(float)
        sd = suggestions[f"pred_{obj}_sd"].to_numpy(float)
        draw = mean + shrink * sd * rng.standard_normal(len(mean))
        out[obj] = np.clip(draw, 0.6 * mean.min(), None)
    out["print_id"] = [f"r2-{i:02d}" for i in suggestions["trial_index"]]
    return out


def render_prediction_vs_actual_figure(observed, suggestions, actual, round_number):
    """Prototype of the post-round-2 figure: predictions travel to measurements.

    Each orange diamond (what the model predicted for a suggested design) is
    joined by a straight path to the open black circle where that article
    actually landed, and the Pareto front is recomputed over round 1 plus
    round 2. The round-1 front stays as a dashed line so the improvement is
    visible.
    """
    combined = pd.concat(
        [
            observed[["print_id", obj1_name, obj2_name]],
            actual[["print_id", obj1_name, obj2_name]],
        ],
        ignore_index=True,
    )
    old_front = pareto_front(observed)
    new_front = pareto_front(combined)
    on_new_front = combined["print_id"].isin(new_front["print_id"])

    xs = np.concatenate(
        [combined[obj1_name], suggestions[f"pred_{obj1_name}_mean"]]
    )
    ys = np.concatenate(
        [combined[obj2_name], suggestions[f"pred_{obj2_name}_mean"]]
    )
    xticks = _nice_ticks(xs.min(), xs.max(), 0.1)
    yticks = _nice_ticks(ys.min(), ys.max(), 2)

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=200)

        # predicted -> measured travel paths
        for (_, pred), (_, act) in zip(suggestions.iterrows(), actual.iterrows()):
            ax.annotate(
                "",
                xy=(act[obj1_name], act[obj2_name]),
                xytext=(pred[f"pred_{obj1_name}_mean"], pred[f"pred_{obj2_name}_mean"]),
                arrowprops=dict(
                    arrowstyle="-|>",
                    color=SUGGEST_ORANGE,
                    lw=1.8,
                    alpha=0.55,
                    shrinkA=8,
                    shrinkB=10,
                ),
                zorder=1,
            )

        # where the model thought round 2 would land (now superseded, so faded)
        ax.scatter(
            suggestions[f"pred_{obj1_name}_mean"], suggestions[f"pred_{obj2_name}_mean"],
            marker="D", s=150, fc=SUGGEST_ORANGE, ec="none", alpha=0.38, zorder=2,
        )

        ax.plot(
            old_front[obj1_name], old_front[obj2_name],
            color=FRONT_BLUE, lw=2.4, ls=(0, (5, 4)), alpha=0.45, zorder=2,
        )
        ax.plot(
            new_front[obj1_name], new_front[obj2_name],
            color=FRONT_BLUE, lw=3.4, zorder=3,
        )
        ax.scatter(
            combined.loc[~on_new_front, obj1_name], combined.loc[~on_new_front, obj2_name],
            fc="none", ec=INK, s=190, lw=2.4, zorder=4,
        )
        ax.scatter(
            new_front[obj1_name], new_front[obj2_name],
            fc=FRONT_BLUE, ec=INK, s=190, lw=2.4, zorder=5,
        )
        _label_points(ax, combined, "print_id", obj1_name, obj2_name)

        _style_axes(
            ax,
            xlim=(xticks[0] - 0.015, xticks[-1] + 0.02),
            ylim=(yticks[0] - 0.5, yticks[-1] + 0.6),
            xticks=xticks,
            yticks=yticks,
        )

        # Callouts are placed relative to what they point at, because the
        # front and the point cloud both move every round.
        new_anchor = _front_anchor(new_front, 0.45)
        _callout(
            ax, f"Pareto front after round {round_number}", new_anchor,
            _axes_frac(ax, new_anchor, -0.02, 0.20), FRONT_BLUE, ha="right",
        )
        old_anchor = _front_anchor(old_front, 0.75)
        _callout(
            ax, "Round-1 front", old_anchor,
            _axes_frac(ax, old_anchor, 0.06, 0.12), FRONT_BLUE,
        )
        # Label the longest predicted-to-measured travel, the clearest one to
        # read the grammar off.
        travel = int(
            np.hypot(
                actual[obj1_name].to_numpy(float)
                - suggestions[f"pred_{obj1_name}_mean"].to_numpy(float),
                (
                    actual[obj2_name].to_numpy(float)
                    - suggestions[f"pred_{obj2_name}_mean"].to_numpy(float)
                )
                / 40.0,
            ).argmax()
        )
        pred_row, act_row = suggestions.iloc[travel], actual.iloc[travel]
        pred_xy = (pred_row[f"pred_{obj1_name}_mean"], pred_row[f"pred_{obj2_name}_mean"])
        _callout(
            ax, "Predicted (round 2)", pred_xy,
            _axes_frac(ax, pred_xy, -0.10, -0.30), SUGGEST_ORANGE, ha="right",
        )
        act_xy = (act_row[obj1_name], act_row[obj2_name])
        _callout(
            ax, "Measured", act_xy,
            _axes_frac(ax, act_xy, 0.10, 0.13), INK, leader=LEADER_GRAY,
        )
        ax.text(
            1.0, 1.06, "PROTOTYPE: round-2 outcomes are synthetic",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=15, color=SUGGEST_ORANGE,
        )

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        out_png = (
            fig_dir
            / f"t3-prism-bo-round{round_number}-predicted-vs-actual-PROTOTYPE.png"
        )
        fig.savefig(out_png, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    gained = set(new_front["print_id"]) - set(old_front["print_id"])
    print(
        f"[prototype, synthetic data] round-{round_number} front: "
        + ", ".join(new_front["print_id"])
        + (f"; new entrants: {', '.join(sorted(gained))}" if gained else "")
    )
    return out_png


# ---- round-2 prototype, animated ----------------------------------------
# Same grammar as the static prototype, played out in time: the orange
# diamonds (predictions) travel along straight paths to where the articles
# actually landed, turning into open black circles on arrival, and the front
# is then recomputed with the round-1 front left dashed underneath. Still
# SYNTHETIC outcomes; see synthesize_round2_outcomes.

ANIM_DPI = 100  # 11 x 7 in -> 1100 x 700 px, both even (h.264 needs even)


def _smoothstep(x):
    """Cubic ease, so the diamonds start and stop rather than jerk."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def _rgba(color, alphas):
    """Per-point RGBA array from one color and an array of alphas."""
    base = np.array(mcolors.to_rgba(color))
    alphas = np.atleast_1d(np.asarray(alphas, float))
    out = np.tile(base, (len(alphas), 1))
    out[:, 3] = np.clip(alphas, 0.0, 1.0)
    return out


def _callout_alpha(ann, alpha):
    """Fade a leader-line callout, text and leader together."""
    ann.set_alpha(alpha)
    if ann.arrow_patch is not None:
        ann.arrow_patch.set_alpha(0.75 * alpha)


def render_prediction_animation(
    observed, suggestions, actual, round_number, fps=25, seconds=None
):
    """Animate predicted -> measured for the suggested batch (GIF + MP4).

    Frames: hold on the suggested batch, then each prediction travels to its
    measurement (staggered, eased) and lands as an open circle, then the
    Pareto front is recomputed while the round-1 front drops back to a pale
    dashed line and the new print IDs fade in. The last frame is the static
    prototype figure, so the two artifacts agree.
    """
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
    from matplotlib.collections import LineCollection

    combined = pd.concat(
        [
            observed[["print_id", obj1_name, obj2_name]],
            actual[["print_id", obj1_name, obj2_name]],
        ],
        ignore_index=True,
    )
    old_front = pareto_front(observed)
    new_front_ids = set(pareto_front(combined)["print_id"])
    new_front = pareto_front(combined)

    pred_xy = suggestions[
        [f"pred_{obj1_name}_mean", f"pred_{obj2_name}_mean"]
    ].to_numpy(float)
    act_xy = actual[[obj1_name, obj2_name]].to_numpy(float)
    n_r2 = len(pred_xy)

    obs_xy = observed[[obj1_name, obj2_name]].to_numpy(float)
    obs_on_old = observed["print_id"].isin(old_front["print_id"]).to_numpy()
    obs_on_new = observed["print_id"].isin(new_front_ids).to_numpy()
    act_on_new = actual["print_id"].isin(new_front_ids).to_numpy()

    xs = np.concatenate([combined[obj1_name].to_numpy(float), pred_xy[:, 0]])
    ys = np.concatenate([combined[obj2_name].to_numpy(float), pred_xy[:, 1]])
    xticks = _nice_ticks(xs.min(), xs.max(), 0.1)
    yticks = _nice_ticks(ys.min(), ys.max(), 2)

    # phase lengths in frames
    n_hold0 = int(round(1.2 * fps))
    n_travel = int(round(2.6 * fps))
    n_front = int(round(1.1 * fps))
    n_hold1 = int(round(2.6 * fps))
    n_frames = n_hold0 + n_travel + n_front + n_hold1

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=ANIM_DPI)
        # No bbox_inches="tight" for animations, so the margins are explicit;
        # the y-axis label sits above the axes and needs the headroom.
        fig.subplots_adjust(left=0.115, right=0.975, top=0.80, bottom=0.175)
        fig.patch.set_facecolor("white")

        _style_axes(
            ax,
            xlim=(xticks[0] - 0.015, xticks[-1] + 0.02),
            ylim=(yticks[0] - 0.5, yticks[-1] + 0.6),
            xticks=xticks,
            yticks=yticks,
        )

        trails = LineCollection(
            [np.array([p, p]) for p in pred_xy],
            colors=[mcolors.to_rgba(SUGGEST_ORANGE, 0.55)] * n_r2,
            linewidths=1.8,
            zorder=1,
        )
        ax.add_collection(trails)
        # arrowheads land only once the travel is over, so nothing overshoots
        heads = [
            ax.annotate(
                "",
                xy=tuple(a),
                xytext=tuple(p),
                arrowprops=dict(
                    arrowstyle="-|>", color=SUGGEST_ORANGE, lw=1.8,
                    alpha=0.0, shrinkA=8, shrinkB=10,
                ),
                zorder=1,
            )
            for p, a in zip(pred_xy, act_xy)
        ]

        ghost = ax.scatter(
            pred_xy[:, 0], pred_xy[:, 1], marker="D", s=150,
            fc=_rgba(SUGGEST_ORANGE, np.ones(n_r2)), ec="none", zorder=2,
        )
        mover = ax.scatter(
            pred_xy[:, 0], pred_xy[:, 1], marker="D", s=150,
            fc=_rgba(SUGGEST_ORANGE, np.ones(n_r2)), ec="none", zorder=6,
        )

        old_line, = ax.plot(
            old_front[obj1_name], old_front[obj2_name],
            color=FRONT_BLUE, lw=3.4, zorder=3,
        )
        new_line, = ax.plot(
            new_front[obj1_name], new_front[obj2_name],
            color=FRONT_BLUE, lw=3.4, alpha=0.0, zorder=3,
        )

        # round-1 articles: always drawn, blue fill only while on the front
        ax.scatter(obs_xy[:, 0], obs_xy[:, 1], fc="none", ec=INK, s=190, lw=2.4, zorder=4)
        r1_fill = ax.scatter(
            obs_xy[obs_on_old, 0], obs_xy[obs_on_old, 1],
            fc=_rgba(FRONT_BLUE, np.ones(int(obs_on_old.sum()))),
            ec=INK, s=190, lw=2.4, zorder=5,
        )
        r1_stays = obs_on_new[obs_on_old]  # of the round-1 front, who survives

        landed = ax.scatter(
            act_xy[:, 0], act_xy[:, 1], fc="none",
            ec=_rgba(INK, np.zeros(n_r2)), s=190, lw=2.4, zorder=4,
        )
        r2_fill = ax.scatter(
            act_xy[act_on_new, 0], act_xy[act_on_new, 1],
            fc=_rgba(FRONT_BLUE, np.zeros(int(act_on_new.sum()))),
            ec=_rgba(INK, np.zeros(int(act_on_new.sum()))),
            s=190, lw=2.4, zorder=5,
        )

        # Labels are laid out once, for the final frame, so nothing shuffles
        # mid-animation; the round-2 IDs fade in as their articles land.
        anns = _label_points(ax, combined, "print_id", obj1_name, obj2_name)
        r2_anns = anns[len(observed):]
        for ann in r2_anns:
            ann.set_alpha(0.0)

        # callouts: the round-1 set fades out as the round-2 set fades in
        obs_anchor = observed.loc[observed[obj1_name].idxmax()]
        _callout(
            ax, "Existing data (round 1)",
            (obs_anchor[obj1_name], obs_anchor[obj2_name]),
            (0.995, 0.72), INK, leader=LEADER_GRAY, ha="right",
        )
        old_anchor = _front_anchor(old_front, 0.30)
        c_front1 = _callout(
            ax, "Pareto front", old_anchor, (0.56, 0.98), FRONT_BLUE,
        )
        sug_i = int(np.argmin(pred_xy[:, 1]))
        c_sug = _callout(
            ax, f"Suggested points (round {round_number})",
            tuple(pred_xy[sug_i]), (0.02, 0.09), SUGGEST_ORANGE,
        )
        new_anchor = _front_anchor(new_front, 0.45)
        c_front2 = _callout(
            ax, f"Pareto front after round {round_number}", new_anchor,
            _axes_frac(ax, new_anchor, -0.02, 0.20), FRONT_BLUE, ha="right",
        )
        old_anchor2 = _front_anchor(old_front, 0.75)
        c_front1b = _callout(
            ax, "Round-1 front", old_anchor2, (0.985, 0.47), FRONT_BLUE, ha="right",
        )
        travel_i = int(
            np.hypot(
                act_xy[:, 0] - pred_xy[:, 0], (act_xy[:, 1] - pred_xy[:, 1]) / 40.0
            ).argmax()
        )
        c_pred = _callout(
            ax, f"Predicted (round {round_number})", tuple(pred_xy[travel_i]),
            _axes_frac(ax, pred_xy[travel_i], -0.10, -0.30), SUGGEST_ORANGE, ha="right",
        )
        c_meas = _callout(
            ax, "Measured", tuple(act_xy[travel_i]),
            _axes_frac(ax, act_xy[travel_i], 0.10, 0.13), INK, leader=LEADER_GRAY,
        )
        for ann in (c_front2, c_front1b, c_pred, c_meas):
            _callout_alpha(ann, 0.0)

        ax.text(
            1.0, 1.06, "PROTOTYPE: round-2 outcomes are synthetic",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=15, color=SUGGEST_ORANGE,
        )

        # per-point stagger, so the batch reads as nine articles rather than
        # one rigid swarm
        starts = np.linspace(0.0, 0.34, n_r2) if n_r2 > 1 else np.zeros(1)
        span = 0.66

        def update(f):
            u = np.clip((f - n_hold0) / max(n_travel, 1), 0.0, 1.0)
            v = _smoothstep((f - n_hold0 - n_travel) / max(n_front, 1))
            p = _smoothstep((u - starts) / span)

            cur = pred_xy + p[:, None] * (act_xy - pred_xy)
            trails.set_segments([np.array([q, c]) for q, c in zip(pred_xy, cur)])
            mover.set_offsets(cur)
            # the diamond hands off to the open circle over the last 40% of
            # its own travel
            mover.set_facecolor(_rgba(SUGGEST_ORANGE, 1.0 - _smoothstep((p - 0.7) / 0.3)))
            landed.set_edgecolor(_rgba(INK, _smoothstep((p - 0.6) / 0.4)))
            ghost.set_facecolor(
                _rgba(
                    SUGGEST_ORANGE,
                    np.full(n_r2, 1.0 - 0.62 * _smoothstep(u / 0.3)),
                )
            )
            for head, pi in zip(heads, p):
                head.arrow_patch.set_alpha(0.55 * _smoothstep((pi - 0.85) / 0.15))

            old_line.set_alpha(1.0 - 0.55 * v)
            old_line.set_linewidth(3.4 - 1.0 * v)
            old_line.set_linestyle("solid" if v < 0.35 else (0, (5, 4)))
            new_line.set_alpha(v)
            r1_fill.set_facecolor(
                _rgba(FRONT_BLUE, np.where(r1_stays, 1.0, 1.0 - v))
            )
            r1_fill.set_edgecolor(_rgba(INK, np.where(r1_stays, 1.0, 1.0 - v)))
            r2_fill.set_facecolor(_rgba(FRONT_BLUE, np.full(int(act_on_new.sum()), v)))
            r2_fill.set_edgecolor(_rgba(INK, np.full(int(act_on_new.sum()), v)))
            for ann in r2_anns:
                ann.set_alpha(v)
            for ann in (c_front1, c_sug):
                _callout_alpha(ann, 1.0 - v)
            for ann in (c_front2, c_front1b, c_pred, c_meas):
                _callout_alpha(ann, v)
            return ()

        anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 / fps)

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        stem = f"t3-prism-bo-round{round_number}-predicted-vs-actual-PROTOTYPE"
        out_mp4 = fig_dir / f"{stem}.mp4"
        out_gif = fig_dir / f"{stem}.gif"

        have_ffmpeg = shutil.which("ffmpeg") is not None
        if have_ffmpeg:
            anim.save(
                out_mp4,
                writer=FFMpegWriter(
                    fps=fps, codec="libx264", bitrate=-1,
                    extra_args=["-pix_fmt", "yuv420p", "-crf", "20"],
                ),
                savefig_kwargs={"facecolor": "white"},
            )
        else:
            out_mp4 = None
            print("ffmpeg not found: skipping the MP4, writing the GIF only")
        plt.close(fig)

    if have_ffmpeg:
        # Palette-based GIF off the MP4: far smaller and cleaner than a
        # frame-by-frame quantization, and it keeps the two in sync.
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(out_mp4),
                "-vf",
                "fps=12,scale=980:-2:flags=lanczos,split[a][b];"
                "[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=3",
                "-loop", "0", str(out_gif),
            ],
            check=True,
        )
    else:
        anim.save(out_gif, writer=PillowWriter(fps=12))

    return out_gif, out_mp4


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
    ap.add_argument(
        "--prototype-next-round",
        action="store_true",
        help=(
            "draw the PROTOTYPE predicted-vs-measured figure for the next "
            "round using SYNTHETIC outcomes drawn from the model's own "
            "predictive distribution (no real round-2 measurements exist yet)"
        ),
    )
    ap.add_argument(
        "--no-animation",
        action="store_true",
        help=(
            "with --prototype-next-round, write only the still PNG and skip "
            "the animated GIF/MP4"
        ),
    )
    args = ap.parse_args(argv)

    X_train, y_train, labels, masses, pending = load_training_data(args.results, args.design)

    if args.plot_only or args.prototype_next_round:
        observed = observed_frame(y_train, labels)
        suggestions = pd.read_csv(
            BO_DIR / f"t3-prism-bo-suggestions-round{args.round}.csv"
        )
        if args.plot_only:
            print(
                "Figure saved to "
                f"{render_objective_figure(observed, suggestions, args.round)}"
            )
        if args.prototype_next_round:
            actual = synthesize_round2_outcomes(suggestions, seed=args.seed)
            dummy_csv = (
                BO_DIR
                / f"t3-prism-bo-round{args.round + 1}-outcomes-PROTOTYPE-dummy.csv"
            )
            actual[["print_id", "trial_index", *PARAM_NAMES, obj1_name, obj2_name]].to_csv(
                dummy_csv, index=False, float_format="%.4f"
            )
            out = render_prediction_vs_actual_figure(
                observed, suggestions, actual, args.round + 1
            )
            print(f"Prototype figure saved to {out} (dummy outcomes: {dummy_csv})")
            if not args.no_animation:
                gif, mp4 = render_prediction_animation(
                    observed, suggestions, actual, args.round + 1
                )
                print(f"Prototype animation saved to {gif}" + (f" and {mp4}" if mp4 else ""))
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
