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
4. Per-print mass accounting (requested on PR #102). Each tested article's
   weighed mass enters the objectives; see the Objectives section below.
5. Constant *printed* mass (PR #102, 2026-08-21). Round 1 was projected onto
   a constant **solid** mass manifold (PR #35 Route A: uniformly re-scale
   until rho_PLA*V_PLA + rho_TPU*V_TPU = 30.95 g, the solid mass of the S0
   reference STLs). That is constant solid mass, not constant volume and not
   constant printed mass: all 9 articles sit at 30.95 g solid and yet weigh
   18.50 to 22.29 g, because PLA prints sparse and thin TPU cables print near
   solid while the PLA/TPU split swings with the geometry. Suggestions are now
   projected onto a constant *printed* mass instead, using the calibrated
   model in ``t3_prism_mass_model.py``, and printed mass is an explicit BO
   parameter (below) rather than a tracking metric.

Search space (6 parameters). The first five are PR #35's base Sobol
coordinates (R, H, twist, strut d, cable d) with the joint diameter frozen at
7 mm; because the projection re-scales every dimension including the joint,
those five fix the article's *shape*. The sixth, ``mass_printed_g``, fixes its
*size*: the projection solves for the uniform scale that hits that printed
mass. (Shape, mass) together determine the article exactly, with no degeneracy
and no redundancy, which is what makes "hold the mass constant" expressible at
all.

The two spaces this implies, and the Ax kwarg that joins them:

* *Fit space*: mass in [18.0, 23.0] g, covering every weighed round-1 article.
* *Generation space*: mass in target +/- 0.457 g (the print-to-print scatter
  measured from the spec-08 triplicate), so every suggested article is
  specified at the same intended mass. Default target 20.23 g, the weighed
  mass of the S0 reference article ``bpx68c``; round 1 anchored its solid
  target to the same reference design. Override with ``--target-mass-g``.

Round-1 data therefore sits OUTSIDE the generation space along the mass axis.
The experiment is created on the fit space, the completed and pending trials
are attached there (``attach_trial`` validates search-space membership and
would raise otherwise, long before any model exists), and the search space is
then narrowed to the generation space, which requires
``immutable_search_space_and_opt_config=False``. The SAASBO step is given
``model_kwargs={"fit_out_of_design": True, "expand_model_space": True}`` so
those out-of-design observations are still used to fit while ``gen`` stays
inside the narrowed space (facebook/Ax#768; deprecated after Ax 1.1.2, where
``expand_model_space`` alone is the live mechanism, so this pairing is correct
for the pinned 0.5.0 and would need revisiting on 1.x).

Each suggestion is reported both as base coordinates and as the as-printed
geometry the constant-printed-mass projection produces, with PR #35's
envelope (<= 250 cm^3) and cable self-bridging (>= 3.0 mm) checks evaluated on
that geometry. The base coordinates still feed ``t3_prism_sobol_batch.py``;
its Route A solve has to be re-pointed at printed grams (target the model in
``t3_prism_mass_model.py`` instead of solid mass) before the STLs match.

Known limitation, unchanged by this: round-1 articles were built under the old
projection, so their coordinates map to slightly different physical articles
than the same coordinates would now (re-projected scales move by up to 3.5
percent). Carrying measured mass as the sixth parameter is what lets the model
account for that instead of silently averaging over it, but it is not the same
as re-fitting on as-printed geometry (facebook/Ax#3577, planned-vs-executed
parameters, still unimplemented upstream).

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
  The model sees mass through the ``mass_printed_g`` parameter instead.
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

Printed mass was a tracking metric in the first version of this script
(predicted per design). It is a BO *parameter* now: under a constant-printed-
mass projection the mass is chosen, not observed, so predicting it would be
predicting an input. The measured masses of the round-1 articles are what make
that parameter identifiable at all.

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
    python bo/t3_prism_bo_campaign.py --target-mass-g 20.6  # different target
    python bo/t3_prism_mass_model.py             # mass-model calibration report
    python bo/t3_prism_bo_campaign.py --plot-only  # redraw the figure only
                                                   # (pandas + matplotlib)
    python bo/t3_prism_bo_campaign.py --prototype-next-round  # see below

Figures. ``--plot-only`` redraws the objective-space panel from the recorded
CSVs (no model refit, ~1 s). ``--prototype-next-round`` draws the layout the
campaign will want once the next batch comes back, as two stills plus an
animation that moves between them. The stills are the two rest points of one
story: ``stage="travel"`` (each orange diamond joined by a straight path to
where that article actually landed, drawn as an open circle like any other
tested article, with no front and no print IDs on the panel) and
``stage="front"`` (the front recomputed over both rounds, the print IDs, and
nothing else). The animation plays hold, retire the round-1 front and the
IDs, travel, hold, clean up, redraw the front, bring every ID back and hold:
one idea per beat, and nothing is labeled while anything is moving
(PR #102 review). The round-2 outcomes it
uses are SYNTHETIC (nothing has been printed or dropped yet); see
``synthesize_round2_outcomes``, which is the single function to replace with
the measured summary when the real numbers arrive. Pass ``--no-animation`` to
skip the GIF/MP4. The MP4 needs ffmpeg on PATH; without it only a
Pillow-written GIF is produced.
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

# Constant-printed-mass projection and its calibration (this directory).
sys.path.insert(0, str(BO_DIR))
from t3_prism_mass_model import (  # noqa: E402
    DEFAULT_PRINTED_MASS_TARGET_G,
    calibrate,
    calibration_report,
)

# define these names as variables for reuse (Honegumi convention)
obj1_name = "t180"
obj2_name = "e_reb_mJ"
# Printed mass is a parameter, not a metric: the projection chooses it.
mass_param = "mass_printed_g"

# Shape coordinates (PR #35 base Sobol space). The projection scales all of
# them plus the 7 mm joint uniformly, so these five fix the shape and
# ``mass_param`` fixes the size.
PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
DESIGN_PARAMS = PARAM_NAMES + [mass_param]

G_M_S2 = 9.80665
DROP_H_M = 1.524  # 60 in drop height (issue #98 campaign protocol)
# Print-to-print mass scatter: sample sd of the spec-08 triplicate
# (dea4ls 22.29 g, bag26v 21.42 g, ghmj4y 22.10 g), the only design printed
# more than once. Used as the design-level mass noise everywhere.
MASS_PRINT_SD_G = 0.457

# Shape half of the search space: identical to PARAMETERS in
# bo/t3_prism_sobol_batch.py (PR #35), the space the printed Sobol batch was
# drawn from.
SHAPE_PARAMETERS = [
    {"name": "R_mm", "type": "range", "bounds": [25.0, 40.0], "value_type": "float"},
    {"name": "H_mm", "type": "range", "bounds": [60.0, 110.0], "value_type": "float"},
    {"name": "twist_deg", "type": "range", "bounds": [40.0, 80.0], "value_type": "float"},
    {"name": "strut_d_mm", "type": "range", "bounds": [6.0, 12.0], "value_type": "float"},
    {"name": "cable_d_mm", "type": "range", "bounds": [3.0, 5.5], "value_type": "float"},
]
# Mass axis of the FIT space: wide enough to hold every weighed round-1
# article (18.50 to 22.29 g) so attach_trial accepts them.
MASS_FIT_BOUNDS = [18.0, 23.0]


def fit_parameters():
    return SHAPE_PARAMETERS + [
        {"name": mass_param, "type": "range",
         "bounds": list(MASS_FIT_BOUNDS), "value_type": "float"}
    ]


# Half-width of the constant-mass generation slab. Not a FixedParameter and
# not the +/-0.457 g print scatter, for two different reasons:
#
# * FixedParameter would be stripped by Ax's RemoveFixed transform, taking the
#   mass dimension out of the model entirely. The model needs it: attributing
#   part of the round-1 objective spread to mass rather than to shape is the
#   whole reason mass is a parameter.
# * A slab as wide as the print scatter has an exploitable gradient. Rebound
#   energy scales with mass, so qNEHVI put all 9 suggestions on the light edge
#   of a +/-0.457 g slab, which means the shapes were chosen at 19.77 g and
#   then reported at 20.23 g. The tolerance is a fact about the printer, not a
#   design variable.
MASS_GEN_HALF_WIDTH_G = 0.01


def _search_space(mass_bounds):
    from ax.core.parameter import ParameterType, RangeParameter
    from ax.core.search_space import SearchSpace

    params = [
        RangeParameter(name=spec["name"], parameter_type=ParameterType.FLOAT,
                       lower=spec["bounds"][0], upper=spec["bounds"][1])
        for spec in SHAPE_PARAMETERS
    ]
    params.append(
        RangeParameter(name=mass_param, parameter_type=ParameterType.FLOAT,
                       lower=mass_bounds[0], upper=mass_bounds[1])
    )
    return SearchSpace(parameters=params)


def fit_search_space():
    """The wide space every round-1 article is a member of."""
    return _search_space(MASS_FIT_BOUNDS)


def gen_search_space(target_g, half_width_g=MASS_GEN_HALF_WIDTH_G):
    """Fit space narrowed to the constant-printed-mass slab used for `gen`."""
    return _search_space((target_g - half_width_g, target_g + half_width_g))

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


def load_training_data(results_path: Path, design_path: Path,
                       key_path: Path | None = None):
    """Join measured objectives onto base Sobol coordinates + weighed mass.

    Returns (X_train, y_train, labels, masses, pending). Each X row is a full
    6-parameter design point: the five shape coordinates plus the article's
    weighed printed mass. ``pending`` holds the same for designed-and-printed
    specs with no drop results yet, whose masses come from the print key.
    """
    results = pd.read_csv(results_path, dtype={"spec": "string"})
    design = pd.read_csv(design_path).set_index("specimen")
    key_path = key_path or (BO_DIR / "t3-prism-bo-batch-print-key.csv")
    key = pd.read_csv(key_path, dtype={"specimen": "string"})
    # one weighed mass per untested spec; average when a spec was printed more
    # than once (only spec 08, and only its official article was tested)
    printed_mass_by_spec = (
        key[key["specimen"] != "S0"]
        .assign(spec=lambda d: d["specimen"].astype(int))
        .groupby("spec")["mass_g"].mean()
    )

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
            }
        )
        params[mass_param] = mass_g
        X_train.append(params)
        labels.append(f"{row['specimen']} (spec {spec})")
        masses.append(mass_g)

    tested_specs = {
        int(s) for s in results["spec"].dropna() if str(s).strip() not in ("", "S0")
    }
    pending = []
    for spec_idx in sorted(set(design.index) - tested_specs):
        base = design.loc[spec_idx]
        mass_g = printed_mass_by_spec.get(spec_idx, float("nan"))
        if not np.isfinite(mass_g):
            print(
                f"WARNING: spec {spec_idx:02d} is printed but has no weighed "
                "mass in the print key, so it cannot be attached as pending."
            )
            continue
        params = {name: float(base[name]) for name in PARAM_NAMES}
        params[mass_param] = float(mass_g)
        pending.append((f"spec {spec_idx:02d}", params))
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
    (28, -6), (-28, -6), (26, 16), (-26, 16),
    (26, -28), (-26, -28), (0, 38), (0, -44),
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


# Relative cost of a point label overlapping each kind of obstacle. A label
# struck through by a callout leader looks far worse than one crossing a
# hairline travel path, and covering another label's words is worse still, so
# the placement search minimizes weighted overlap rather than raw area.
W_TEXT = 4.0
W_MARKER = 1.5
W_LEADER = 2.5
W_FRONT = 2.2   # the front is a bold 3.4 pt line, not a hairline
W_LINE = 1.0


def _text_boxes(fig, anns, pad=6):
    """Display-space boxes of the callout *text* (not their leader lines).

    Point labels are laid out after the callouts and treat these as
    obstacles, which is what stops an ID from landing under a series name.
    Text.get_window_extent is used explicitly because Annotation's own
    version folds in the leader line, which spans half the panel and would
    block far more than the words do.
    """
    from matplotlib.text import Text

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = []
    for ann in anns:
        bb = Text.get_window_extent(ann, renderer)
        boxes.append((bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad, W_TEXT))
    return boxes


def _segment_boxes(ends, n=14, half=6, weight=W_LINE):
    """Small display-space boxes strung along each (start, end) display-space
    segment, so point labels dodge the travel arrows, the callout leaders and
    the front polyline instead of landing on top of them."""
    boxes = []
    for (x0, y0), (x1, y1) in ends:
        for t in np.linspace(0.06, 0.94, n):
            x, y = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
            boxes.append((x - half, y - half, x + half, y + half, weight))
    return boxes


def _marker_boxes(ax, xy, r_pt=11, weight=W_MARKER):
    """Display-space boxes over a set of data-space markers, so point labels
    dodge markers that are not in the frame being labeled (the suggestion
    diamonds sit under the round-1 IDs in the animation's opening frame)."""
    r = r_pt * ax.figure.dpi / 72.0
    pts = ax.transData.transform(np.asarray(xy, float))
    return [(x - r, y - r, x + r, y + r, weight) for x, y in pts]


def _leader_ends(ax, anns):
    """Display-space endpoints of each callout's leader line."""
    return [
        (
            tuple(ax.transData.transform(ann.xy)),
            tuple(ax.transAxes.transform(ann.get_position())),
        )
        for ann in anns
    ]


def _polyline_ends(ax, xs, ys):
    """Display-space endpoints of each leg of a data-space polyline."""
    pts = ax.transData.transform(np.column_stack([xs, ys]))
    return [(tuple(a), tuple(b)) for a, b in zip(pts[:-1], pts[1:])]


def _label_points(
    ax, frame, id_col, x_col, y_col, color=LABEL_GRAY, fontsize=17, obstacles=()
):
    """Place point labels, greedily avoiding markers, callouts and each other.

    Boxes are estimated rather than measured (no renderer round trip), which
    is enough to keep IDs legible as the point cloud moves round to round.
    When no candidate offset is fully clear the least-overlapping one wins,
    rather than whichever happened to be last in the list.
    """
    pts = ax.transData.transform(frame[[x_col, y_col]].to_numpy(float))
    dpp = ax.figure.dpi / 72.0  # points -> display pixels
    marker_r = 11 * dpp
    taken = [
        (x - marker_r, y - marker_r, x + marker_r, y + marker_r, W_MARKER)
        for x, y in pts
    ]
    taken.extend(obstacles)

    def overlap_area(box):
        area = 0.0
        for t in taken:
            w = min(box[2], t[2]) - max(box[0], t[0])
            h = min(box[3], t[3]) - max(box[1], t[1])
            if w > 0 and h > 0:
                area += w * h * t[4]
        return area

    anns = []
    for (px, py), (_, row) in zip(pts, frame.iterrows()):
        text = str(row[id_col])
        w = 0.56 * fontsize * len(text) * dpp
        h = 1.25 * fontsize * dpp
        best = None
        for dx, dy in LABEL_CANDIDATES:
            x0 = px + dx * dpp if dx >= 0 else px + dx * dpp - w
            y0 = py + dy * dpp
            box = (x0, y0, x0 + w, y0 + h)
            area = overlap_area(box)
            if area <= 0.0:
                best = (0.0, dx, dy, box)
                break
            if best is None or area < best[0]:
                best = (area, dx, dy, box)
        _, dx, dy, box = best
        taken.append((*box, W_TEXT))
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
        _style_axes(
            ax,
            xlim=(0.79, 1.13),
            ylim=(5.4, 15.0),
            xticks=np.arange(0.8, 1.101, 0.1),
            yticks=np.arange(6, 14.1, 2),
        )

        # Series names as leader-line callouts instead of a legend box.
        # Placed before the point labels, which then dodge them.
        sug_anchor = suggestions.loc[suggestions[f"pred_{obj2_name}_mean"].idxmin()]
        obs_anchor = observed.loc[observed[obj1_name].idxmax()]
        callouts = [
            _callout(
                ax, "Pareto front", _front_anchor(front, 0.35),
                (0.58, 0.96), FRONT_BLUE,
            ),
            _callout(
                ax, f"Suggested points (round {round_number + 1})",
                (
                    sug_anchor[f"pred_{obj1_name}_mean"],
                    sug_anchor[f"pred_{obj2_name}_mean"],
                ),
                (0.02, 0.10), SUGGEST_ORANGE,
            ),
            _callout(
                ax, "Existing data",
                (obs_anchor[obj1_name], obs_anchor[obj2_name]),
                (0.99, 0.13), INK, leader=LEADER_GRAY, ha="right",
            ),
        ]
        _label_points(
            ax, observed, "print_id", obj1_name, obj2_name,
            obstacles=(
                _text_boxes(fig, callouts)
                + _segment_boxes(_leader_ends(ax, callouts), half=9, weight=W_LEADER)
                + _segment_boxes(
                    _polyline_ends(ax, front[obj1_name], front[obj2_name]),
                    half=9, weight=W_FRONT,
                )
            ),
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


def _prototype_limits(combined, suggestions):
    """Tick arrays shared by every round-2 artifact, so the stills and the
    animation register frame for frame."""
    xs = np.concatenate(
        [combined[obj1_name].to_numpy(float), suggestions[f"pred_{obj1_name}_mean"]]
    )
    ys = np.concatenate(
        [combined[obj2_name].to_numpy(float), suggestions[f"pred_{obj2_name}_mean"]]
    )
    xticks = _nice_ticks(xs.min(), xs.max(), 0.1)
    yticks = _nice_ticks(ys.min(), ys.max(), 2)
    return xticks, yticks


def render_prediction_vs_actual_figure(
    observed, suggestions, actual, round_number, stage="travel"
):
    """The two rest points of the round-2 story, as stills.

    ``stage="travel"``: what the model predicted (faded orange diamonds)
    joined by straight paths to where each article actually landed, drawn as
    an open black circle like any other tested article. **No front is drawn,
    and no print IDs.** The round-1 front has already been retired and the
    round-2 one has not been computed yet, which is precisely the beat the
    animation holds on; the IDs are retired with it, because seventeen of them
    over the travel paths is exactly the crowding the beat list exists to
    avoid (PR #102 review). Identity comes back on the ``"front"`` still.

    ``stage="front"``: the round-2 figure alone. One front, computed over both
    rounds, one set of articles, none of the scaffolding that explained how
    the batch got there.

    Both stages share tick ranges and label placement inputs, so the two PNGs
    (and the animation frames they correspond to) register.
    """
    if stage not in ("travel", "front"):
        raise ValueError(f"stage must be 'travel' or 'front', got {stage!r}")

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
    xticks, yticks = _prototype_limits(combined, suggestions)

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=200)
        _style_axes(
            ax,
            xlim=(xticks[0] - 0.015, xticks[-1] + 0.02),
            ylim=(yticks[0] - 0.5, yticks[-1] + 0.6),
            xticks=xticks,
            yticks=yticks,
        )

        if stage == "travel":
            # predicted -> measured travel paths
            for (_, pred), (_, act) in zip(suggestions.iterrows(), actual.iterrows()):
                ax.annotate(
                    "",
                    xy=(act[obj1_name], act[obj2_name]),
                    xytext=(
                        pred[f"pred_{obj1_name}_mean"],
                        pred[f"pred_{obj2_name}_mean"],
                    ),
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
            # where the model thought round 2 would land (now superseded)
            ax.scatter(
                suggestions[f"pred_{obj1_name}_mean"],
                suggestions[f"pred_{obj2_name}_mean"],
                marker="D", s=150, fc=SUGGEST_ORANGE, ec="none", alpha=0.38, zorder=2,
            )
            # every article is just a tested article at this point
            ax.scatter(
                combined[obj1_name], combined[obj2_name],
                fc="none", ec=INK, s=190, lw=2.4, zorder=4,
            )
        else:
            ax.plot(
                new_front[obj1_name], new_front[obj2_name],
                color=FRONT_BLUE, lw=3.4, zorder=3,
            )
            ax.scatter(
                combined.loc[~on_new_front, obj1_name],
                combined.loc[~on_new_front, obj2_name],
                fc="none", ec=INK, s=190, lw=2.4, zorder=4,
            )
            ax.scatter(
                new_front[obj1_name], new_front[obj2_name],
                fc=FRONT_BLUE, ec=INK, s=190, lw=2.4, zorder=5,
            )

        # Callouts first, so the print IDs can dodge them. At most two are
        # ever on the panel at once: one idea per figure, per the PR #102
        # review of the animation.
        if stage == "travel":
            # Name the longest predicted-to-measured travel, the clearest one
            # to read the grammar off, and only that one.
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
            pred_xy = (
                pred_row[f"pred_{obj1_name}_mean"],
                pred_row[f"pred_{obj2_name}_mean"],
            )
            act_xy = (act_row[obj1_name], act_row[obj2_name])
            callouts = [
                _callout(
                    ax, f"Predicted (round {round_number})", pred_xy,
                    _axes_frac(ax, pred_xy, -0.05, -0.13), SUGGEST_ORANGE, ha="right",
                ),
                _callout(
                    ax, "Measured", act_xy,
                    _axes_frac(ax, act_xy, 0.06, 0.09), INK, leader=LEADER_GRAY,
                ),
            ]
        else:
            # Nothing can sit below-left of a Pareto front, so that is where
            # this callout goes; it is a property of the front, not a
            # hand-placement that breaks when the data moves.
            new_anchor = _front_anchor(new_front, 0.55)
            callouts = [
                _callout(
                    ax, f"Pareto front after round {round_number}", new_anchor,
                    _axes_frac(ax, new_anchor, -0.36, -0.20), FRONT_BLUE, ha="left",
                ),
            ]
        blockers = _text_boxes(fig, callouts) + _segment_boxes(
            _leader_ends(ax, callouts), half=9, weight=W_LEADER
        )
        if stage == "travel":
            blockers += _segment_boxes(
                list(
                    zip(
                        ax.transData.transform(
                            suggestions[
                                [f"pred_{obj1_name}_mean", f"pred_{obj2_name}_mean"]
                            ].to_numpy(float)
                        ),
                        ax.transData.transform(
                            actual[[obj1_name, obj2_name]].to_numpy(float)
                        ),
                    )
                )
            )
        else:
            blockers += _segment_boxes(
                _polyline_ends(ax, new_front[obj1_name], new_front[obj2_name]),
                half=9, weight=W_FRONT,
            )
        if stage == "front":
            # Only the resting figure is labeled: at the travel beat the
            # panel is about the arrows, not about which article is which.
            _label_points(
                ax, combined, "print_id", obj1_name, obj2_name, obstacles=blockers,
            )

        ax.text(
            1.0, 1.06, "PROTOTYPE: round-2 outcomes are synthetic",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=15, color=SUGGEST_ORANGE,
        )

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        stem = (
            f"t3-prism-bo-round{round_number}-predicted-vs-actual"
            if stage == "travel"
            else f"t3-prism-bo-round{round_number}-front-final"
        )
        out_png = fig_dir / f"{stem}-PROTOTYPE.png"
        fig.savefig(out_png, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    if stage == "front":
        gained = set(new_front["print_id"]) - set(old_front["print_id"])
        print(
            f"[prototype, synthetic data] round-{round_number} front: "
            + ", ".join(new_front["print_id"])
            + (f"; new entrants: {', '.join(sorted(gained))}" if gained else "")
        )
    return out_png


# ---- round-2 prototype, animated ----------------------------------------
# Same grammar as the static prototypes, played out in time, one idea per
# beat (PR #102 review: too many things were moving and too much text was on
# screen at once). The round-1 front is retired BEFORE anything moves, the
# diamonds then travel alone, and the new front is redrawn as its own step
# after every article has landed and turned into an open black circle.
# Still SYNTHETIC outcomes; see synthesize_round2_outcomes.

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
    observed, suggestions, actual, round_number, fps=25
):
    """Animate predicted -> measured for the suggested batch (GIF + MP4).

    Choreographed one idea per beat, after the PR #102 review found the first
    cut had too much moving and too much text on screen at once:

    1. *Hold*: the round-1 figure exactly as the slide already shows it.
    2. *Retire*: the round-1 front, its blue point fills and **every print ID**
       fade out, taking the "Pareto front" and "Existing data" callouts with
       them. Nothing moves. The panel is left as unlabeled tested articles
       plus suggestions.
    3. *Travel*: the diamonds ease to their measurements and hand off to open
       black circles, alone on the panel, with no front to read across.
    4. *Hold*: predicted versus measured, named by one labeled pair.
    5. *Clean*: the prediction layer and those two callouts fade out.
    6. *Front*: the new front is redrawn over both rounds, as its own step,
       wiping in along the polyline and filling each article as it reaches it.
    7. *Hold*: the print IDs come back, all of them at once and only once the
       figure is at rest, and the round-2 figure holds.

    The IDs leaving in beat 2 and returning in beat 7 is the second half of
    the same review note that produced the beat list: eight IDs on the
    round-1 slide is fine, but carrying them through the travel while the
    round-2 IDs arrive on top of them is not (PR #102 review). Nothing is
    labeled while anything is moving.

    Beats 4 and 7 hold the same content as the two committed stills
    (``stage="travel"`` and ``stage="front"``), which is what keeps the
    animation and the PNGs telling the same story. Only the point-label
    placement differs, because each figure solves it against its own set of
    obstacles.
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
    new_front = pareto_front(combined)
    new_front_ids = set(new_front["print_id"])

    pred_xy = suggestions[
        [f"pred_{obj1_name}_mean", f"pred_{obj2_name}_mean"]
    ].to_numpy(float)
    act_xy = actual[[obj1_name, obj2_name]].to_numpy(float)
    n_r2 = len(pred_xy)

    obs_xy = observed[[obj1_name, obj2_name]].to_numpy(float)
    obs_on_old = observed["print_id"].isin(old_front["print_id"]).to_numpy()
    obs_on_new = observed["print_id"].isin(new_front_ids).to_numpy()
    act_on_new = actual["print_id"].isin(new_front_ids).to_numpy()

    xticks, yticks = _prototype_limits(combined, suggestions)

    # Arc position of every article along the new front, normalized to [0, 1],
    # so the wipe and the fills that follow it are one motion rather than a
    # line and a set of markers that happen to share a phase.
    fx = new_front[obj1_name].to_numpy(float)
    fy = new_front[obj2_name].to_numpy(float)
    xr = max(float(np.ptp(fx)), 1e-9)
    yr = max(float(np.ptp(fy)), 1e-9)
    seg = np.hypot(np.diff(fx) / xr, np.diff(fy) / yr)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    s_front = cum / max(cum[-1], 1e-9)
    arc_of = dict(zip(new_front["print_id"], s_front))
    obs_s = np.array(
        [arc_of[p] for p in observed.loc[obs_on_new, "print_id"]], float
    )
    act_s = np.array(
        [arc_of[p] for p in actual.loc[act_on_new, "print_id"]], float
    )

    def front_upto(v):
        """The front polyline truncated at normalized arc length `v`."""
        if v <= 0.0:
            return [], []
        if v >= 1.0:
            return fx, fy
        k = int(np.searchsorted(s_front, v))
        i = max(k - 1, 0)
        t = (v - s_front[i]) / max(s_front[i + 1] - s_front[i], 1e-9)
        return (
            [*fx[:k], fx[i] + t * (fx[i + 1] - fx[i])],
            [*fy[:k], fy[i] + t * (fy[i + 1] - fy[i])],
        )

    # phase lengths in frames, one idea each
    n_hold0 = int(round(1.3 * fps))    # the round-1 figure, as-is
    n_retire = int(round(0.9 * fps))   # drop the round-1 front, nothing moves
    n_travel = int(round(2.6 * fps))   # predictions travel, nothing else
    n_hold1 = int(round(1.7 * fps))    # read predicted vs measured
    n_clean = int(round(0.9 * fps))    # drop the prediction layer
    n_front = int(round(1.3 * fps))    # redraw the front, its own step
    n_hold2 = int(round(2.4 * fps))    # rest on the round-2 figure
    t_retire = n_hold0
    t_travel = t_retire + n_retire
    t_hold1 = t_travel + n_travel
    t_clean = t_hold1 + n_hold1
    t_front = t_clean + n_clean
    t_rest = t_front + n_front   # the IDs come back here, and only here
    n_frames = t_rest + n_hold2

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
        new_line, = ax.plot([], [], color=FRONT_BLUE, lw=3.4, zorder=3)

        # round-1 articles: always drawn, blue fill only while on a front
        ax.scatter(obs_xy[:, 0], obs_xy[:, 1], fc="none", ec=INK, s=190, lw=2.4, zorder=4)
        r1_old_fill = ax.scatter(
            obs_xy[obs_on_old, 0], obs_xy[obs_on_old, 1],
            fc=_rgba(FRONT_BLUE, np.ones(int(obs_on_old.sum()))),
            ec=INK, s=190, lw=2.4, zorder=5,
        )
        r1_new_fill = ax.scatter(
            obs_xy[obs_on_new, 0], obs_xy[obs_on_new, 1],
            fc=_rgba(FRONT_BLUE, np.zeros(int(obs_on_new.sum()))),
            ec=_rgba(INK, np.zeros(int(obs_on_new.sum()))),
            s=190, lw=2.4, zorder=5,
        )

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

        # Callouts, laid out before the point labels so the IDs dodge them.
        # At most three are ever lit at once (the opening frame, which is the
        # round-1 slide), and at most one while anything is moving.
        obs_anchor = observed.loc[observed[obj1_name].idxmax()]
        c_exist = _callout(
            ax, "Existing data (round 1)",
            (obs_anchor[obj1_name], obs_anchor[obj2_name]),
            (0.995, 0.72), INK, leader=LEADER_GRAY, ha="right",
        )
        c_front1 = _callout(
            ax, "Pareto front", _front_anchor(old_front, 0.30),
            (0.56, 0.98), FRONT_BLUE,
        )
        sug_i = int(np.argmin(pred_xy[:, 1]))
        c_sug = _callout(
            ax, f"Suggested points (round {round_number})",
            tuple(pred_xy[sug_i]), (0.02, 0.09), SUGGEST_ORANGE,
        )
        travel_i = int(
            np.hypot(
                act_xy[:, 0] - pred_xy[:, 0], (act_xy[:, 1] - pred_xy[:, 1]) / 40.0
            ).argmax()
        )
        c_pred = _callout(
            ax, f"Predicted (round {round_number})", tuple(pred_xy[travel_i]),
            _axes_frac(ax, pred_xy[travel_i], -0.05, -0.13), SUGGEST_ORANGE, ha="right",
        )
        c_meas = _callout(
            ax, "Measured", tuple(act_xy[travel_i]),
            _axes_frac(ax, act_xy[travel_i], 0.06, 0.09), INK, leader=LEADER_GRAY,
        )
        new_anchor = _front_anchor(new_front, 0.55)
        c_front2 = _callout(
            ax, f"Pareto front after round {round_number}", new_anchor,
            _axes_frac(ax, new_anchor, -0.36, -0.20), FRONT_BLUE, ha="left",
        )
        for ann in (c_pred, c_meas, c_front2):
            _callout_alpha(ann, 0.0)

        ax.text(
            1.0, 1.06, "PROTOTYPE: round-2 outcomes are synthetic",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=15, color=SUGGEST_ORANGE,
        )

        # Labels are laid out once, for the final frame, so nothing shuffles
        # mid-animation. They are on screen in exactly two beats, the opening
        # hold and the closing one, so they dodge what is drawn in those: the
        # callouts and their leaders, both fronts, and the suggestion diamonds
        # (which sit under the round-1 IDs in the opening frame). The travel
        # paths are not obstacles, because no label is ever lit while one is
        # on the panel.
        all_callouts = [c_exist, c_front1, c_sug, c_pred, c_meas, c_front2]
        anns = _label_points(
            ax, combined, "print_id", obj1_name, obj2_name,
            obstacles=(
                _text_boxes(fig, all_callouts)
                + _segment_boxes(
                    _leader_ends(ax, all_callouts), half=9, weight=W_LEADER
                )
                + _segment_boxes(_polyline_ends(ax, fx, fy), half=9, weight=W_FRONT)
                + _segment_boxes(
                    _polyline_ends(
                        ax, old_front[obj1_name], old_front[obj2_name]
                    ),
                    half=9, weight=W_FRONT,
                )
                + _marker_boxes(ax, pred_xy)
            ),
        )
        r1_anns, r2_anns = anns[:len(observed)], anns[len(observed):]
        for ann in r2_anns:
            ann.set_alpha(0.0)

        # per-point stagger, so the batch reads as nine articles rather than
        # one rigid swarm
        starts = np.linspace(0.0, 0.34, n_r2) if n_r2 > 1 else np.zeros(1)
        span = 0.66

        def update(f):
            # one progress variable per beat; each is zero until its beat
            q = _smoothstep((f - t_retire) / max(n_retire, 1))   # retire front
            u = np.clip((f - t_travel) / max(n_travel, 1), 0.0, 1.0)
            m = _smoothstep((f - t_hold1) / max(0.45 * fps, 1))  # name the pair
            w = _smoothstep((f - t_clean) / max(n_clean, 1))     # clean up
            v = _smoothstep((f - t_front) / max(n_front, 1))     # redraw front
            d = _smoothstep((f - t_rest) / max(0.5 * fps, 1))    # IDs return
            keep = 1.0 - w  # everything that only existed to explain the move
            p = _smoothstep((u - starts) / span)

            cur = pred_xy + p[:, None] * (act_xy - pred_xy)
            trails.set_segments([np.array([q0, c]) for q0, c in zip(pred_xy, cur)])
            trails.set_color(mcolors.to_rgba(SUGGEST_ORANGE, 0.55 * keep))
            mover.set_offsets(cur)
            # the diamond hands off to the open circle over the last 40% of
            # its own travel
            mover.set_facecolor(
                _rgba(SUGGEST_ORANGE, (1.0 - _smoothstep((p - 0.7) / 0.3)) * keep)
            )
            landed.set_edgecolor(_rgba(INK, _smoothstep((p - 0.6) / 0.4)))
            ghost.set_facecolor(
                _rgba(
                    SUGGEST_ORANGE,
                    np.full(n_r2, 1.0 - 0.62 * _smoothstep(u / 0.3)) * keep,
                )
            )
            for head, pi in zip(heads, p):
                head.arrow_patch.set_alpha(
                    0.55 * _smoothstep((pi - 0.85) / 0.15) * keep
                )
            # IDs: gone for the whole middle of the clip. The round-1 ones
            # leave with the round-1 front and come back with every other ID
            # once the figure has stopped moving.
            for ann in r1_anns:
                ann.set_alpha(float(max(1.0 - q, d)))
            for ann in r2_anns:
                ann.set_alpha(float(d))

            # beat 2: the round-1 front leaves before anything moves
            old_line.set_alpha(1.0 - q)
            r1_old_fill.set_facecolor(
                _rgba(FRONT_BLUE, np.full(int(obs_on_old.sum()), 1.0 - q))
            )
            r1_old_fill.set_edgecolor(
                _rgba(INK, np.full(int(obs_on_old.sum()), 1.0 - q))
            )

            # beat 6: the new front wipes in and fills each article it reaches
            new_line.set_data(*front_upto(v))
            r1_new_fill.set_facecolor(
                _rgba(FRONT_BLUE, _smoothstep((v - obs_s) / 0.18))
            )
            r1_new_fill.set_edgecolor(_rgba(INK, _smoothstep((v - obs_s) / 0.18)))
            r2_fill.set_facecolor(_rgba(FRONT_BLUE, _smoothstep((v - act_s) / 0.18)))
            r2_fill.set_edgecolor(_rgba(INK, _smoothstep((v - act_s) / 0.18)))

            # callouts: never more than one live while anything is in motion
            _callout_alpha(c_exist, 1.0 - q)
            _callout_alpha(c_front1, 1.0 - q)
            _callout_alpha(c_sug, 1.0 - _smoothstep(u / 0.25))
            _callout_alpha(c_pred, m * keep)
            _callout_alpha(c_meas, m * keep)
            _callout_alpha(c_front2, _smoothstep((v - 0.55) / 0.45))
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
    ap.add_argument(
        "--target-mass-g",
        type=float,
        default=DEFAULT_PRINTED_MASS_TARGET_G,
        help=(
            "constant as-printed mass every suggested article is projected "
            "onto (default: the weighed mass of the S0 reference bpx68c)"
        ),
    )
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
            # the two beats the animation holds on
            out = render_prediction_vs_actual_figure(
                observed, suggestions, actual, args.round + 1, stage="travel"
            )
            out_final = render_prediction_vs_actual_figure(
                observed, suggestions, actual, args.round + 1, stage="front"
            )
            print(
                f"Prototype figures saved to {out} and {out_final} "
                f"(dummy outcomes: {dummy_csv})"
            )
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

    mass_model = calibrate()
    print(calibration_report(mass_model, args.target_mass_g))
    print()

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
        f"corr(mass, t180) r = {r_mass_t180:.2f}. That spread is the reason "
        f"mass is a parameter: round 2 pins it at {args.target_mass_g:.2f} g "
        "so the same correlation cannot be re-created by the suggestions."
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
                model_kwargs={
                    # Round-1 articles sit outside the constant-mass generation
                    # space along the mass axis. Fit on them anyway; gen still
                    # respects the narrowed space (facebook/Ax#768).
                    "fit_out_of_design": True,
                    # expand the model's internal range-parameter bounds to the
                    # data so the out-of-design masses are not normalized as
                    # extreme outliers (default True in 0.5.0; explicit here
                    # because it is the live mechanism on Ax 1.x, where
                    # fit_out_of_design is deprecated)
                    "expand_model_space": True,
                },
            ),
        ]
    )

    ax_client = AxClient(generation_strategy=gs, random_seed=args.seed, verbose_logging=False)
    ax_client.create_experiment(
        name="t3_prism_drop_campaign",
        # created on the FIT space so the out-of-design round-1 masses can be
        # attached at all; narrowed to the constant-mass slab below
        parameters=fit_parameters(),
        objectives={
            obj1_name: ObjectiveProperties(minimize=True),
            obj2_name: ObjectiveProperties(minimize=True),
        },
        # required to narrow the search space after trials exist
        immutable_search_space_and_opt_config=False,
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

    # Narrow to the constant-printed-mass slab. Every trial attached above is
    # now out of design on the mass axis, which is exactly what
    # fit_out_of_design=True is for: they stay in the fit, and gen is confined
    # to the target mass.
    space = gen_search_space(args.target_mass_g)
    ax_client.experiment.search_space = space
    lo = space.parameters[mass_param].lower
    hi = space.parameters[mass_param].upper
    out_of_design = sum(
        1 for x in X_train + [d for _, d in pending]
        if not (lo <= x[mass_param] <= hi)
    )
    print(
        f"\nGeneration space narrowed: {mass_param} in [{lo:.3f}, {hi:.3f}] g "
        f"(target {args.target_mass_g:.2f} g +/- {MASS_GEN_HALF_WIDTH_G:.3f} g). "
        f"{out_of_design} of {len(X_train) + len(pending)} attached "
        "trials are out of design and are kept in the fit via fit_out_of_design."
    )

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
        row[mass_param] = float(parameterization[mass_param])
        for metric in (obj1_name, obj2_name):
            row[f"pred_{metric}_mean"] = f_mean[metric][j]
            row[f"pred_{metric}_sd"] = float(np.sqrt(f_cov[metric][metric][j]))
        # implied rebound fraction at the target mass, for comparison with the
        # raw e_rebound column of the results CSV
        row["pred_e_rebound_approx"] = row[f"pred_{obj2_name}_mean"] / (
            args.target_mass_g * G_M_S2 * DROP_H_M
        )
        # as-printed geometry under the constant-printed-mass projection, with
        # PR #35's two printability checks evaluated on it
        row["target_mass_g"] = args.target_mass_g
        projected = mass_model.project(
            {name: parameterization[name] for name in PARAM_NAMES},
            args.target_mass_g,
        )
        row.update({k: projected[k] for k in (
            "scale", "R_print_mm", "H_print_mm", "strut_d_print_mm",
            "cable_d_print_mm", "joint_d_print_mm", "solid_mass_g",
            "envelope_cm3", "envelope_ok", "cable_bridge_ok",
        )})
        rows.append(row)
    suggestions = pd.DataFrame(rows)

    n_env = int((~suggestions["envelope_ok"]).sum())
    n_cab = int((~suggestions["cable_bridge_ok"]).sum())
    print(
        f"\nProjected onto {args.target_mass_g:.2f} g printed: scale "
        f"{suggestions['scale'].min():.3f} to {suggestions['scale'].max():.3f}; "
        f"{n_env} over the 250 cm^3 envelope, {n_cab} under the 3.0 mm cable "
        "self-bridging floor (flagged, not dropped, same as round 1)."
    )

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
