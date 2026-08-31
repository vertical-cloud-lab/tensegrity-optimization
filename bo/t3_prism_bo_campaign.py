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

6. Print-process parameters (PR #102, 2026-08-26). Six slicer settings that
   had been silent stock defaults are design variables from round 3 on: the
   sparse infill density of the strut (PLA) and cable (TPU) parts, and the
   nozzle temperature and max volumetric speed of each filament. Both tested
   plates were sliced identically, so all 17 tested articles sit at one point
   of that subspace and the round-3 batch is its initialization; see the
   PROCESS_SPECS block for the bounds and the reason for each one.
7. Global filament settings (PR #102, 2026-08-26; reworked 2026-08-31 on
   review). Nozzle temperature and max volumetric speed are filament
   settings, so a print job carries one value of each, while sparse infill
   density is a per-object setting and can vary between articles on a plate.
   An earlier version of this script bought within-round variation on the
   four filament axes by splitting the batch across plates sliced at
   different settings (commit 265bfe5); that split-plot design was replaced
   by ONE value of each for the whole batch: formally, the optimal predicted
   print parameters of the batch's best-predicted specimen, applied
   everywhere. With all 17 tested articles at a single point of the process
   space the model cannot rank process settings, so an "optimal predicted"
   setting does not exist yet and the point is drawn from a seeded scrambled
   Sobol sequence over the bounds instead; a later batch that still lacks
   process variation continues the same sequence, so the batch-level points
   accumulate as a low-discrepancy design across rounds. The two infill
   densities are still stratified per article by a Latin hypercube. The run
   prints how much replacing the acquisition's process coordinates moved the
   model's predictions, as a fraction of the model's own posterior sd, so
   the cost of the substitution is measured rather than assumed.

Search space (12 parameters). The first five are PR #35's base Sobol
coordinates (R, H, twist, strut d, cable d) with the joint diameter frozen at
7 mm; because the projection re-scales every dimension including the joint,
those five fix the article's *shape*. The sixth, ``mass_printed_g``, fixes its
*size*: the projection solves for the uniform scale that hits that printed
mass. (Shape, mass) together determine the article exactly, with no degeneracy
and no redundancy, which is what makes "hold the mass constant" expressible at
all. The remaining six are how it is printed, and one of them, the
strut infill, feeds back into the projection: a sparser article has to be
larger to weigh the same, so the solved scale moves by about -9 to +1 percent
across the infill bounds.

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
campaign will want once the next batch comes back: four stills plus an
animation that moves between them, all of them frames of one figure.

The stills are the four points at which that figure is at rest, and they are
written in slide order:

1. ``-start-PROTOTYPE.png``: the round-1 figure, its front, its print IDs and
   the orange suggested points.
2. ``-uncertainty-PROTOTYPE.png``: the predicted uncertainties shown at the
   suggested points: a horizontal and a vertical bar spanning +/- 1 posterior
   sd per objective, and a shaded axis-aligned oval through the same +/- 1 sd
   contour, both in a faded shade of the suggestion orange.
3. ``-predicted-vs-actual-PROTOTYPE.png``: each orange diamond joined by a
   straight path to where that article actually landed, drawn as an open
   circle like any other tested article. No front and no print IDs.
4. ``-front-final-PROTOTYPE.png``: the front recomputed over both rounds,
   every article labeled, and none of the scaffolding.

What the uncertainty is, precisely: the ``pred_*_sd`` columns of the
suggestions CSV are one standard deviation of the model posterior for the
noise-free objective value (the square root of the diagonal of the covariance
returned by ``TorchModelBridge.predict``, averaged over the SAAS MCMC draws).
They are epistemic model uncertainty about the design's true mean response,
not a standard error of any sample of drops. Only the per-objective marginals
were recorded, so the oval is axis-aligned; the cross-objective covariance
that ``predict`` also returns was not saved.

Because they are frames of one figure rather than four drawings, they are
the same pixel size (``ANIM_FIGSIZE * ANIM_DPI``, 3300 x 2100) and every
element that survives a beat sits at the same pixel in all four, so they can
go on four consecutive slides and be cross-faded or morphed. The animation
plays the same story in time: hold, retire the round-1 front and the IDs,
show the uncertainties and freeze, travel, hold, clean up, redraw the front,
bring every ID back and hold. One
idea per beat, and nothing is labeled while anything is moving (PR #102
review). The round-2 outcomes it uses are SYNTHETIC (nothing has been printed
or dropped yet); see ``synthesize_round2_outcomes``, which is the single
function to replace with the measured summary when the real numbers arrive.
Pass ``--no-animation`` for the stills alone. The MP4 needs ffmpeg on PATH;
without it only a Pillow-written GIF is produced.
"""

from __future__ import annotations

import argparse
import math
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
# Mass axis of the FIT space: wide enough to hold every weighed article from
# both tested batches (round 1: 18.50 to 22.29 g; round 2 r2d2c: 17.91 to
# 23.47 g) so attach_trial accepts them.
MASS_FIT_BOUNDS = [17.5, 24.0]


# ---- print-process parameters (new in round 3; PR #102, 2026-08-26) ------
# Six slicer settings promoted from silent stock defaults to design variables.
# Both tested plates were sliced from Bambu's stock "0.30mm Standard @BBL H2D
# 0.6 nozzle" process at 15 percent grid sparse infill, 2 wall loops, 0.30 mm
# layers and 0.62 mm line width, with PLA Basic at 220 C / 30 mm^3/s and TPU
# 85A at 240 C / 2.5 mm^3/s. Those are AS_PRINTED_PROCESS below, read out of
# Metadata/project_settings.config in the round-1 project committed at
# bo/slices/ and in the round-2 project posted to issue #98 on 2026-08-24, so
# all 17 tested articles sit at one single point of this six-dimensional space.
#
# Two facts about the H2D decide the shape of the round-3 batch.
#
# * Sparse infill density is a per-object (and per-part) setting, so it can
#   differ between articles on one plate, and between the PLA and the TPU
#   halves of one article. Each specimen is one Bambu object holding a
#   "<spec>-struts.stl" part on extruder 1 and a "<spec>-cables.stl" part on
#   extruder 2, so a per-part override addresses the two materials separately.
#   Without the override the two share one global value, which is why nobody
#   had chosen either of them before.
# * Nozzle temperature and max volumetric speed are FILAMENT settings. Every
#   object on a plate is built layer by layer through the same two nozzles, so
#   a print job carries only one value of each. Since 2026-08-31 the whole
#   batch carries ONE value of each (the best-predicted specimen's settings
#   applied everywhere, Sobol-drawn until data exists to rank them), so
#   variation on these four axes accrues across rounds rather than within
#   one, and plates are nothing but floor space.
#
# Speed is parameterized as the filament's max volumetric speed, not as mm/s,
# because that is the setting that actually binds. The process profile asks for
# 200 mm/s outer wall and 350 mm/s sparse infill, which at 0.62 x 0.30 mm of
# extrusion is 37 and 65 mm^3/s, so both materials already run flow-capped
# everywhere. Bambu Studio has no per-material mm/s at all (speeds belong to
# the process and are shared by both filaments), so the volumetric cap is the
# only per-material speed control there is. Every table reports the equivalent
# mm/s next to it.
EXTRUSION_AREA_MM2 = 0.62 * 0.30  # line width x layer height, both plates

# level: "article"  -> per-object/per-part override, free to vary per article
#        "filament" -> filament setting, one value for the whole batch
# step:  the slicer's own resolution for that field; suggestions are rounded to
#        it and the model is re-queried at the rounded point, so the delivered
#        coordinate and the printed setting are the same number.
PROCESS_SPECS = [
    {"name": "strut_infill_pct", "bounds": [10.0, 60.0], "level": "article",
     "step": 1.0, "unit": "%", "slicer": "sparse infill density, struts part",
     "why": "10 is below the stock 15 and 60 is a structural infill; past 60 "
            "the printed-mass model is extrapolating a long way from the one "
            "setting it was calibrated at, and print time climbs"},
    {"name": "tpu_infill_pct", "bounds": [10.0, 60.0], "level": "article",
     "step": 1.0, "unit": "%", "slicer": "sparse infill density, cables part",
     "why": "same bounds as the struts; this is the knob that decides whether "
            "the captive core is the hollow lock ball photographed on #85"},
    {"name": "pla_nozzle_temp_C", "bounds": [200.0, 235.0], "level": "filament",
     "step": 1.0, "unit": "C", "slicer": "PLA filament nozzle temperature",
     "why": "Bambu PLA Basic's own preset window is 190 to 240; held in from "
            "both ends because 30 mm^3/s through a 0.6 nozzle needs heat at "
            "the bottom and stringing across the tendons gets worse at the top"},
    {"name": "pla_flow_mm3_s", "bounds": [15.0, 30.0], "level": "filament",
     "step": 0.1, "unit": "mm^3/s", "slicer": "PLA filament max volumetric speed",
     "why": "30 is the vendor value the two tested plates ran at and is the "
            "ceiling; 15 halves it, which is as slow as a nine-article plate "
            "can afford"},
    {"name": "tpu_nozzle_temp_C", "bounds": [230.0, 250.0], "level": "filament",
     "step": 1.0, "unit": "C", "slicer": "TPU filament nozzle temperature",
     "why": "the generic Bambu TPU 85A @BBL H2D preset allows 200 to 250; "
            "centered on the 240 both plates ran at. Watch the top of this "
            "range: issue #96 traced a multi-week outage to lubricant "
            "carbonizing in the hotend on long hot TPU prints"},
    {"name": "tpu_flow_mm3_s", "bounds": [2.0, 4.8], "level": "filament",
     "step": 0.1, "unit": "mm^3/s", "slicer": "TPU filament max volumetric speed",
     "why": "4.8 is what the TPU high-flow hotend installed on 2026-08-17 is "
            "rated for (#96), which the lab has wanted to try and has not; "
            "2.0 is just below the 2.5 both plates ran at"},
]
PROCESS_PARAM_NAMES = [spec["name"] for spec in PROCESS_SPECS]
ARTICLE_PROCESS_PARAMS = [s["name"] for s in PROCESS_SPECS if s["level"] == "article"]
FILAMENT_PROCESS_PARAMS = [s["name"] for s in PROCESS_SPECS if s["level"] == "filament"]
PROCESS_BOUNDS = {s["name"]: tuple(s["bounds"]) for s in PROCESS_SPECS}
PROCESS_STEP = {s["name"]: s["step"] for s in PROCESS_SPECS}

# The single point in that space that every tested article was printed at.
AS_PRINTED_PROCESS = {
    "strut_infill_pct": 15.0,
    "tpu_infill_pct": 15.0,
    "pla_nozzle_temp_C": 220.0,
    "pla_flow_mm3_s": 30.0,
    "tpu_nozzle_temp_C": 240.0,
    "tpu_flow_mm3_s": 2.5,
}
assert all(
    PROCESS_BOUNDS[k][0] <= v <= PROCESS_BOUNDS[k][1]
    for k, v in AS_PRINTED_PROCESS.items()
), "the as-printed process point must be inside the fit space or attach_trial rejects it"

DESIGN_PARAMS_R3 = PARAM_NAMES + [mass_param] + PROCESS_PARAM_NAMES


def flow_to_mm_s(mm3_s: float) -> float:
    """Volumetric cap in mm^3/s -> the mm/s it allows at this profile's bead."""
    return mm3_s / EXTRUSION_AREA_MM2


def round_to_step(value: float, step: float) -> float:
    """Round a suggestion onto the slicer field's own resolution."""
    return round(round(value / step) * step, 6)


def process_parameters():
    return [
        {"name": spec["name"], "type": "range", "bounds": list(spec["bounds"]),
         "value_type": "float"}
        for spec in PROCESS_SPECS
    ]


def fit_parameters(include_process: bool = True):
    """Ax parameter specs for the fit space.

    ``include_process=False`` gives back the six-parameter space of rounds 1
    and 2. The diagnostics use it: their subject is the 17 tested articles,
    every one of which sits at the same process point, so six constant
    dimensions would add nothing to a refit and the round-1 and round-2
    AxClient snapshots they load were written without them.
    """
    params = SHAPE_PARAMETERS + [
        {"name": mass_param, "type": "range",
         "bounds": list(MASS_FIT_BOUNDS), "value_type": "float"}
    ]
    return params + process_parameters() if include_process else params


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


def _search_space(mass_bounds, process_bounds=None, include_process=True):
    from ax.core.parameter import ParameterType, RangeParameter
    from ax.core.search_space import SearchSpace

    process_bounds = process_bounds or {}
    params = [
        RangeParameter(name=spec["name"], parameter_type=ParameterType.FLOAT,
                       lower=spec["bounds"][0], upper=spec["bounds"][1])
        for spec in SHAPE_PARAMETERS
    ]
    params.append(
        RangeParameter(name=mass_param, parameter_type=ParameterType.FLOAT,
                       lower=mass_bounds[0], upper=mass_bounds[1])
    )
    if include_process:
        for spec in PROCESS_SPECS:
            lo, hi = process_bounds.get(spec["name"], spec["bounds"])
            params.append(
                RangeParameter(name=spec["name"],
                               parameter_type=ParameterType.FLOAT,
                               lower=float(lo), upper=float(hi))
            )
    return SearchSpace(parameters=params)


def fit_search_space(include_process: bool = True):
    """The wide space every tested article is a member of."""
    return _search_space(MASS_FIT_BOUNDS, include_process=include_process)


def gen_search_space(target_g, half_width_g=MASS_GEN_HALF_WIDTH_G,
                     process_bounds=None):
    """Fit space narrowed to the constant-printed-mass slab used for `gen`."""
    return _search_space((target_g - half_width_g, target_g + half_width_g),
                         process_bounds=process_bounds)

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
                       key_path: Path | None = None,
                       process: dict | None = AS_PRINTED_PROCESS):
    """Join measured objectives onto base Sobol coordinates + weighed mass.

    Returns (X_train, y_train, labels, masses, pending). Each X row is a full
    design point: the five shape coordinates, the article's weighed printed
    mass, and the six print-process coordinates, which are the same for every
    article because both tested plates were sliced identically. ``pending``
    holds the same for designed-and-printed specs with no drop results yet,
    whose masses come from the print key.
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
        params.update(process or {})
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
        params.update(process or {})
        pending.append((f"spec {spec_idx:02d}", params))
    return X_train, y_train, labels, masses, pending


# Round-2 (r2d2c) batch files. The designs table is the plate that was
# actually printed (bo/t3-prism-bo-round1.csv on the PR #35 branch, commit
# 8809b25): its R_mm..cable_d_mm columns are the BASE coordinates of Ax
# trials 10-18 (the 7a048ee mass-aware suggestions), which is the space the
# model fits in, and its *_print_* columns are the constant-SOLID-mass
# projection that went to the printer. The predictions table is the
# suggestions CSV as it stood when the plate was generated (commit 7a048ee),
# kept so predicted-vs-measured is drawn against what the model actually
# claimed, not against a later re-run.
ROUND2_RESULTS = BO_DIR / "t3-prism-bo-round1-drop-results.csv"
ROUND2_DESIGNS = BO_DIR / "t3-prism-bo-round1-designs.csv"
ROUND2_KEY = BO_DIR / "t3-prism-bo-round1-print-key.csv"
ROUND2_PREDICTIONS = BO_DIR / "t3-prism-bo-round1-predictions.csv"


def load_round2_training_data(results_path=ROUND2_RESULTS,
                              designs_path=ROUND2_DESIGNS,
                              key_path=ROUND2_KEY,
                              process: dict | None = AS_PRINTED_PROCESS):
    """Measured r2d2c articles as (X, y) in the same fit space.

    Base coordinates come from the printed plate's design table via the
    print key's trial mapping; the sixth parameter is the article's weighed
    mass (with label, the same convention as the round-1 ingestion).
    Returns (X, y, labels, masses, trial_of_label). Sessions whose t180 is
    drift-flagged by the campaign analysis are ingested at their stabilized
    mean with a prominent warning: the drift inflates the recorded sd, so
    the SEM the GP receives already carries the contamination.
    """
    if not results_path.exists():
        print(f"WARNING: no round-2 results at {results_path}; skipping.")
        return [], [], [], [], {}
    results = pd.read_csv(results_path)
    designs = pd.read_csv(designs_path).set_index("source_trial")
    key = pd.read_csv(key_path).set_index("print_id")

    X, y, labels, masses, trial_of = [], [], [], [], {}
    for _, row in results.iterrows():
        pid = str(row["specimen"]).strip()
        if pid not in key.index:
            print(f"WARNING: skipping {pid!r}: not in the round-2 print key.")
            continue
        trial = int(key.loc[pid, "source_trial"])
        base = designs.loc[trial]
        params = {name: float(base[name]) for name in PARAM_NAMES}
        mass_g = float(row["mass_g"])
        n = float(row["n_valid"])
        e_mean = float(row["e_rebound_mean"])
        e_sem = float(row["e_rebound_sd"]) / np.sqrt(n)
        e_reb_mJ = e_mean * mass_g * G_M_S2 * DROP_H_M
        e_reb_sem = e_reb_mJ * float(
            np.hypot(e_sem / e_mean, MASS_PRINT_SD_G / mass_g)
        )
        if bool(row.get("t_drift_flag", False)):
            print(
                f"WARNING: {pid} (trial {trial}) is T-DRIFT flagged "
                f"(slope {row.get('t180_slope_pct_per_drop')}, "
                f"end-to-end {row.get('t180_e2e_pct')} %): its t180 mean is "
                "drift-contaminated; ingested with the inflated sd, but "
                "resolve per the campaign-analysis watch before trusting it."
            )
        y.append(
            {
                obj1_name: (float(row["t180_mean"]),
                            float(row["t180_sd"]) / np.sqrt(n)),
                obj2_name: (e_reb_mJ, e_reb_sem),
            }
        )
        params[mass_param] = mass_g
        params.update(process or {})
        X.append(params)
        label = f"{pid} (trial {trial})"
        labels.append(label)
        masses.append(mass_g)
        trial_of[label] = trial
    return X, y, labels, masses, trial_of


def measured_round2_frame(y_round2, labels_round2, trial_of, predictions):
    """Measured round-2 outcomes row-aligned to the predictions table.

    This is the real-data replacement for ``synthesize_round2_outcomes``:
    same columns, but the objectives are the drop-tested values and the
    ordering matches ``predictions`` (one row per suggested trial) so the
    travel animation joins each prediction to its own article's landing.
    Trials whose article has no session yet get NaN rows and are dropped
    with a note.
    """
    frame = observed_frame(y_round2, labels_round2)
    frame["trial_index"] = [trial_of[label] for label in labels_round2]
    merged = predictions[["trial_index"]].merge(frame, on="trial_index", how="left")
    missing = merged["print_id"].isna()
    if missing.any():
        miss = predictions.loc[missing.to_numpy(), "trial_index"].tolist()
        print(f"NOTE: trials with no drop session yet: {miss} (dropped from "
              "the predicted-vs-measured figure)")
    kept = ~missing.to_numpy()
    return merged[~missing].reset_index(drop=True), kept


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
# 300 dpi throughout: the stills go on slides and into print-resolution
# decks, and the video is exported from the same canvas so the clip and
# the stills stay interchangeable.
FIGURE_DPI = 300

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

# U+2193 in place of the words "lower is better": it reads at a glance from
# the back of a room, and it survives being shrunk into a slide corner. The
# glyph is present in every face in FIG_RC["font.sans-serif"]; matplotlib
# falls through that list per character if a machine's pick lacks it.
ARROW_DOWN = "\u2193"
Y_LABEL = f"Rebound energy to payload\n(mJ per drop, {ARROW_DOWN} is better)"
X_LABEL = f"Shock transmissibility t180 ({ARROW_DOWN} is better)"

# Objective-2 display mode. The default is the absolute rebound energy in mJ
# per drop, the quantity the committed suggestions optimized. --per-gram
# divides every rebound-energy quantity (measured value, predicted mean and
# sd) by the article's mass, per the intensive-form notes on PR #33: for a
# measured article that quotient is exactly e_rebound * g * h, so the
# per-gram axis is the restitution fraction in disguise and strips the
# printed-mass dividend out of the comparison. Display only: the recorded
# CSVs and the BO fit stay in absolute mJ.
Y_TICK_STEP = 2.0
OBJ2_UNIT = "mJ"
FILE_TAG = ""
PRIOR_FRONT_GRAY = "#b9b8b4"


def set_per_gram_mode():
    """Switch every figure this module draws to mJ/g per drop."""
    global Y_LABEL, Y_TICK_STEP, OBJ2_UNIT, FILE_TAG
    Y_LABEL = f"Rebound energy per gram\n(mJ/g per drop, {ARROW_DOWN} is better)"
    Y_TICK_STEP = 0.1
    OBJ2_UNIT = "mJ/g"
    FILE_TAG = "-per-gram"

# Candidate label placements, in points relative to the marker, tried in
# order until one lands clear of the other labels and markers. Hand-tuned
# offsets would break the moment the data moves, which it will every round.
LABEL_CANDIDATES = [
    (12, 7), (12, -20), (-12, 7), (-12, -20),
    (12, 20), (-12, 20), (0, 24), (0, -30),
    (28, -6), (-28, -6), (26, 16), (-26, 16),
    (26, -28), (-26, -28), (0, 38), (0, -44),
    # a farther ring, reached only when every near candidate collides
    # (dense clusters like the per-gram low-rebound corner need it)
    (44, -6), (-44, -6), (40, 26), (-40, 26),
    (40, -38), (-40, -38), (0, 52), (0, -58),
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
# a label across an open marker circle is nearly as illegible as one across
# text, so markers cost close to what text does
W_MARKER = 3.0
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


def render_objective_figure(observed, suggestions, round_number,
                            prior_front=None, batch_number=None):
    """Single objective-space panel, sized and styled for slides.

    The Honegumi template's second (parallel-coordinates) panel is omitted.
    The front is the non-dominated set of the *observed* points, which for
    round 1 is the same three articles as Ax's model-predicted Pareto set.
    `prior_front`, when given, is the previous round's front drawn as a faded
    gray line with no markers, so the hypervolume gained by the newest batch
    reads visually (PR #102 review).
    """
    front = pareto_front(observed)
    on_front = observed["print_id"].isin(front["print_id"])

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=FIGURE_DPI)

        if prior_front is not None:
            ax.plot(
                prior_front[obj1_name], prior_front[obj2_name],
                color=PRIOR_FRONT_GRAY, lw=2.6, zorder=1.5,
            )
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
        # Limits follow the data (round 2 brought a 1.33 t180 that the round-1
        # panel's hard-coded 1.13 ceiling would have cropped).
        xticks, yticks = _prototype_limits(observed, suggestions)
        _style_axes(
            ax,
            xlim=(xticks[0] - 0.015, xticks[-1] + 0.02),
            # padding in fractions of the tick step so the absolute (mJ) and
            # per-gram (mJ/g) renderings breathe the same amount
            ylim=(yticks[0] - 0.25 * Y_TICK_STEP, yticks[-1] + 0.3 * Y_TICK_STEP),
            xticks=xticks,
            yticks=yticks,
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
                ax, "Suggested points (round "
                f"{round_number + 1 if batch_number is None else batch_number})",
                (
                    sug_anchor[f"pred_{obj1_name}_mean"],
                    sug_anchor[f"pred_{obj2_name}_mean"],
                ),
                # parked below the anchor's height so the leader rises off
                # the text instead of striking through it
                (0.02, 0.045), SUGGEST_ORANGE,
            ),
            _callout(
                ax, "Existing data",
                (obs_anchor[obj1_name], obs_anchor[obj2_name]),
                (0.99, 0.13), INK, leader=LEADER_GRAY, ha="right",
            ),
        ]
        prior_obstacles = []
        if prior_front is not None:
            callouts.append(
                _callout(
                    ax, f"Round-{round_number - 1} front",
                    _front_anchor(prior_front, 0.42),
                    (0.02, 0.68), PRIOR_FRONT_GRAY, leader=PRIOR_FRONT_GRAY,
                )
            )
            prior_obstacles = _segment_boxes(
                _polyline_ends(
                    ax, prior_front[obj1_name], prior_front[obj2_name]
                ),
                half=9, weight=W_FRONT,
            )
        _label_points(
            ax, observed, "print_id", obj1_name, obj2_name,
            obstacles=(
                _text_boxes(fig, callouts)
                + _segment_boxes(_leader_ends(ax, callouts), half=9, weight=W_LEADER)
                + _segment_boxes(
                    _polyline_ends(ax, front[obj1_name], front[obj2_name]),
                    half=9, weight=W_FRONT,
                )
                + prior_obstacles
            ),
        )

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        out_png = fig_dir / f"t3-prism-bo-round{round_number}-pareto{FILE_TAG}.png"
        fig.savefig(out_png, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    obj2_fmt = ".2f" if Y_TICK_STEP < 1 else ".1f"
    print(
        "Pareto-front articles: "
        + ", ".join(
            f"{r['print_id']} (t180 {r[obj1_name]:.3f}, "
            f"{r[obj2_name]:{obj2_fmt}} {OBJ2_UNIT})"
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
    yticks = _nice_ticks(ys.min(), ys.max(), Y_TICK_STEP)
    return xticks, yticks


# ---- round-2 prototype: one figure, four stills and an animation --------
# One idea per beat (PR #102 review: too many things were moving and too much
# text was on screen at once). The round-1 front is retired BEFORE anything
# moves, the diamonds then travel alone, and the new front is redrawn as its
# own step after every article has landed and turned into an open black
# circle. Still SYNTHETIC outcomes; see synthesize_round2_outcomes.
#
# The four stills are frames of this same figure rather than separately
# drawn panels, which is what lets them be dropped on four consecutive
# slides and cross-faded: same canvas, same size, same axes, same label
# placement, so every element that survives a beat stays exactly where it
# was (PR #102 review). Drawing them twice could not guarantee that, since
# each panel solves its own label placement.

ANIM_FIGSIZE = (11.0, 7.0)
ANIM_DPI = FIGURE_DPI  # 11 x 7 in -> 3300 x 2100 px, both even (h.264 needs even)
GIF_WIDTH_PX = 1280  # the GIF is for threads and the README, not for slides

# Frames exported as stills, in slide order. Keyed on the beat they rest in;
# resolved against the frame table inside render_round2_prototype.
STILL_STAGES = ("start", "uncertainty", "travel", "front")


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


def render_round2_prototype(
    observed, suggestions, actual, round_number, fps=25, animate=True,
    synthetic=True, stem=None, series_label=None, pred_label=None,
    front_label=None, unc_label=None,
):
    """The round-2 story as four registered stills plus an animation.

    Also the engine for the LOOCV version of the same story (PR #102
    request): pass an **empty** ``observed`` frame and every article's
    held-out prediction as ``suggestions`` (with the measured outcomes as
    ``actual``), and the round-1 layer plus its retire beat simply drop out.
    ``stem`` overrides the output file stem, and the four ``*_label``
    arguments re-word the callouts, so the cross-validation set reads
    "held out" where the campaign set reads "suggested". Everything else,
    beats, registration, label placement, is shared, so the two sets cannot
    drift apart stylistically.

    Returns ``(stills, gif, mp4)``. ``stills`` is a dict keyed by
    ``STILL_STAGES``, in slide order:

    * ``"start"``: the round-1 figure, front and print IDs and the orange
      suggestions.
    * ``"uncertainty"``: the predicted +/- 1 sd bars and ovals frozen at the
      suggested points.
    * ``"travel"``: predicted joined to measured, no front and no IDs.
    * ``"front"``: the round-2 figure alone, front recomputed over both
      rounds, every article labeled.

    All four are frames of one figure, exported at ``ANIM_DPI`` with no
    ``bbox_inches="tight"``, so they are the same pixel size as each other
    and as the video. Put them on four consecutive slides and any transition
    between them registers, because nothing that survives a beat has moved.

    Choreographed one idea per beat, after the PR #102 review found the first
    cut had too much moving and too much text on screen at once:

    1. *Hold*: the round-1 figure exactly as the slide already shows it.
    2. *Retire*: the round-1 front, its blue point fills and **every print ID**
       fade out, taking the "Pareto front" and "Existing data" callouts with
       them. Nothing moves. The panel is left as unlabeled tested articles
       plus suggestions.
    3. *Uncertainty*: each suggestion grows a horizontal and a vertical bar
       spanning +/- 1 posterior sd per objective and a shaded axis-aligned
       oval through the same contour, in a faded shade of the suggestion
       orange, then the panel **freezes** so they can be read before anything
       moves (PR #102 review). The sd is the model posterior for the
       noise-free objective (see the module docstring), and the oval is
       axis-aligned because only the marginal sds were recorded.
    4. *Travel*: the diamonds ease to their measurements and hand off to open
       black circles. The uncertainty layer stays anchored at the predictions
       and fades to the same ghost level as the diamonds' origin markers, so
       predicted-band-versus-landing stays readable in a freeze frame.
    5. *Hold*: predicted versus measured, named by one labeled pair.
    6. *Clean*: the prediction layer, its uncertainties and those callouts
       fade out.
    7. *Front*: the new front is redrawn over both rounds, as its own step,
       wiping in along the polyline and filling each article as it reaches it.
    8. *Hold*: the print IDs come back, all of them at once and only once the
       figure is at rest, and the round-2 figure holds.

    The IDs leaving in beat 2 and returning in beat 8 is the second half of
    the same review note that produced the beat list: eight IDs on the
    round-1 slide is fine, but carrying them through the travel while the
    round-2 IDs arrive on top of them is not (PR #102 review). Nothing is
    labeled while anything is moving.

    The exported stills are beats 1, 3, 5 and 8, the four points at which the
    figure is at rest.
    """
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
    from matplotlib.collections import LineCollection
    from matplotlib.patches import Ellipse

    if stem is None:
        stem = f"t3-prism-bo-round{round_number}"
    if series_label is None:
        series_label = f"Suggested points (round {round_number})"
    if pred_label is None:
        pred_label = f"Predicted (round {round_number})"
    if front_label is None:
        front_label = f"Pareto front after round {round_number}"
    if unc_label is None:
        unc_label = "Predicted ± 1 sd\n(model posterior)"

    has_prior = len(observed) > 0
    combined = pd.concat(
        [
            observed[["print_id", obj1_name, obj2_name]],
            actual[["print_id", obj1_name, obj2_name]],
        ],
        ignore_index=True,
    )
    old_front = pareto_front(observed) if has_prior else observed.iloc[0:0]
    new_front = pareto_front(combined)
    new_front_ids = set(new_front["print_id"])

    pred_xy = suggestions[
        [f"pred_{obj1_name}_mean", f"pred_{obj2_name}_mean"]
    ].to_numpy(float)
    # One posterior sd of the noise-free objective per suggestion, straight
    # from the suggestions CSV (sqrt of the diagonal of the covariance that
    # TorchModelBridge.predict returned when the batch was generated). The
    # cross-objective covariance was not recorded, so the uncertainty oval
    # drawn from these is axis-aligned.
    pred_sd = suggestions[
        [f"pred_{obj1_name}_sd", f"pred_{obj2_name}_sd"]
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
    # nothing to retire when there is no prior-round layer (the LOOCV set)
    n_retire = int(round(0.9 * fps)) if has_prior else 0
    n_unc = int(round(0.7 * fps))      # the +/- 1 sd bars and ovals grow in
    n_freeze = int(round(1.4 * fps))   # ...and freeze, to be read
    n_travel = int(round(2.6 * fps))   # predictions travel, nothing else
    n_hold1 = int(round(1.7 * fps))    # read predicted vs measured
    n_clean = int(round(0.9 * fps))    # drop the prediction layer
    n_front = int(round(1.3 * fps))    # redraw the front, its own step
    n_hold2 = int(round(2.4 * fps))    # rest on the round-2 figure
    t_retire = n_hold0
    t_unc = t_retire + n_retire
    t_travel = t_unc + n_unc + n_freeze
    t_hold1 = t_travel + n_travel
    t_clean = t_hold1 + n_hold1
    t_front = t_clean + n_clean
    t_rest = t_front + n_front   # the IDs come back here, and only here
    n_frames = t_rest + n_hold2

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=ANIM_FIGSIZE, dpi=ANIM_DPI)
        # No bbox_inches="tight" for animations, so the margins are explicit;
        # the y-axis label sits above the axes and needs the headroom.
        fig.subplots_adjust(left=0.115, right=0.975, top=0.80, bottom=0.175)
        fig.patch.set_facecolor("white")

        _style_axes(
            ax,
            xlim=(xticks[0] - 0.015, xticks[-1] + 0.02),
            # padding in fractions of the tick step so the absolute (mJ) and
            # per-gram (mJ/g) renderings breathe the same amount
            ylim=(yticks[0] - 0.25 * Y_TICK_STEP, yticks[-1] + 0.3 * Y_TICK_STEP),
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

        # Predicted uncertainty, one layer per suggestion: a +/- 1 sd bar per
        # objective and a shaded axis-aligned oval through the same +/- 1 sd
        # contour. Both are faded shades of the suggestion orange, sit under
        # the markers, and clip at the axes: several rebound-energy sds are
        # taller than the panel, which is the honest picture (the LOOCV found
        # no out-of-sample skill on that objective) and worth showing rather
        # than shrinking.
        unc_ovals = []
        for (px, py), (sx, sy) in zip(pred_xy, pred_sd):
            ell = Ellipse(
                (px, py), width=2.0 * sx, height=2.0 * sy,
                facecolor=SUGGEST_ORANGE, edgecolor="none",
                alpha=0.0, zorder=1.2,
            )
            ax.add_patch(ell)
            unc_ovals.append(ell)
        unc_bars = LineCollection(
            [
                seg
                for (px, py), (sx, sy) in zip(pred_xy, pred_sd)
                for seg in (
                    [(px - sx, py), (px + sx, py)],
                    [(px, py - sy), (px, py + sy)],
                )
            ],
            colors=mcolors.to_rgba(SUGGEST_ORANGE, 0.0),
            linewidths=2.2,
            zorder=1.6,
        )
        ax.add_collection(unc_bars)

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
        if has_prior:
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
        else:
            c_exist = c_front1 = None
        sug_i = int(np.argmin(pred_xy[:, 1]))
        c_sug = _callout(
            ax, series_label,
            tuple(pred_xy[sug_i]), (0.02, 0.09), SUGGEST_ORANGE,
        )
        # Uncertainty callout, anchored to a horizontal bar end so the leader
        # touches the thing the words describe. The leftmost bar end is used
        # and the text parked in the top-left corner, the one region the
        # ovals cannot wash over (the panel's own limits crop them there).
        unc_i = int(np.argmin(pred_xy[:, 0] - pred_sd[:, 0]))
        unc_anchor = (
            pred_xy[unc_i, 0] - pred_sd[unc_i, 0], pred_xy[unc_i, 1]
        )
        c_unc = _callout(
            ax, unc_label, unc_anchor,
            (0.02, 0.90), SUGGEST_ORANGE,
        )
        # longest travel in axis-normalized units (y down-weighted so t180
        # misses dominate the pick), so the labeled pair is chosen the same
        # way whether the y-axis is in mJ or mJ/g
        travel_i = int(
            np.hypot(
                (act_xy[:, 0] - pred_xy[:, 0]) / (xticks[-1] - xticks[0]),
                0.5 * (act_xy[:, 1] - pred_xy[:, 1]) / (yticks[-1] - yticks[0]),
            ).argmax()
        )
        c_pred = _callout(
            ax, pred_label, tuple(pred_xy[travel_i]),
            _axes_frac(ax, pred_xy[travel_i], -0.05, -0.13), SUGGEST_ORANGE, ha="right",
        )
        # The labeled landing can sit anywhere, including the panel's right
        # edge (r2d2c3 measured at t180 1.33), so the text goes on whichever
        # side of the point has room.
        meas_right = ax.transLimits.transform(act_xy[travel_i])[0] > 0.6
        c_meas = _callout(
            ax, "Measured", tuple(act_xy[travel_i]),
            _axes_frac(
                ax, act_xy[travel_i], -0.06 if meas_right else 0.06, 0.09
            ),
            INK, leader=LEADER_GRAY, ha="right" if meas_right else "left",
        )
        new_anchor = _front_anchor(new_front, 0.55)
        c_front2 = _callout(
            ax, front_label, new_anchor,
            _axes_frac(ax, new_anchor, -0.36, -0.20), FRONT_BLUE, ha="left",
        )
        for ann in (c_unc, c_pred, c_meas, c_front2):
            _callout_alpha(ann, 0.0)

        if synthetic:
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
        all_callouts = [
            c for c in (c_exist, c_front1, c_sug, c_unc, c_pred, c_meas, c_front2)
            if c is not None
        ]
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
            e = _smoothstep((f - t_unc) / max(n_unc, 1))         # sd bars grow
            u = np.clip((f - t_travel) / max(n_travel, 1), 0.0, 1.0)
            m = _smoothstep((f - t_hold1) / max(0.45 * fps, 1))  # name the pair
            w = _smoothstep((f - t_clean) / max(n_clean, 1))     # clean up
            v = _smoothstep((f - t_front) / max(n_front, 1))     # redraw front
            d = _smoothstep((f - t_rest) / max(0.5 * fps, 1))    # IDs return
            keep = 1.0 - w  # everything that only existed to explain the move
            p = _smoothstep((u - starts) / span)

            # beat 3: the uncertainty layer grows in and freezes; once the
            # travel starts it stays anchored at the predictions and drops to
            # the same ghost level as the diamonds' origin markers
            ua = e * (1.0 - 0.62 * _smoothstep(u / 0.3)) * keep
            for ell in unc_ovals:
                ell.set_alpha(0.07 * ua)
            unc_bars.set_color(mcolors.to_rgba(SUGGEST_ORANGE, 0.55 * ua))

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

            # beat 6: the new front wipes in and fills each article it reaches.
            # The fill variable overshoots (v * 1.18) so the article at the
            # very end of the polyline (arc position 1.0) still completes its
            # fill by v = 1; without it the last front point stayed unfilled
            # in the final frame.
            new_line.set_data(*front_upto(v))
            fill_obs = _smoothstep((v * 1.18 - obs_s) / 0.18)
            fill_act = _smoothstep((v * 1.18 - act_s) / 0.18)
            r1_new_fill.set_facecolor(_rgba(FRONT_BLUE, fill_obs))
            r1_new_fill.set_edgecolor(_rgba(INK, fill_obs))
            r2_fill.set_facecolor(_rgba(FRONT_BLUE, fill_act))
            r2_fill.set_edgecolor(_rgba(INK, fill_act))

            # callouts: never more than one live while anything is in motion
            if c_exist is not None:
                _callout_alpha(c_exist, 1.0 - q)
                _callout_alpha(c_front1, 1.0 - q)
            _callout_alpha(c_sug, 1.0 - _smoothstep(u / 0.25))
            _callout_alpha(c_unc, e * (1.0 - _smoothstep(u / 0.25)))
            _callout_alpha(c_pred, m * keep)
            _callout_alpha(c_meas, m * keep)
            _callout_alpha(c_front2, _smoothstep((v - 0.55) / 0.45))
            return ()

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        tag = ("-PROTOTYPE" if synthetic else "") + FILE_TAG

        # The four rest points, exported from this figure rather than
        # redrawn: beat 1 (before anything moves), the end of the uncertainty
        # freeze, the end of beat 5 (both travel callouts fully lit) and the
        # last frame. No bbox_inches, so every PNG is exactly
        # ANIM_FIGSIZE * ANIM_DPI and the set lines up on consecutive slides.
        still_frames = {
            "start": 0,
            "uncertainty": t_travel - 1,
            "travel": t_clean - 1,
            "front": n_frames - 1,
        }
        still_names = {
            "start": f"{stem}-start{tag}.png",
            "uncertainty": f"{stem}-uncertainty{tag}.png",
            "travel": f"{stem}-predicted-vs-actual{tag}.png",
            "front": f"{stem}-front-final{tag}.png",
        }
        stills = {}
        for stage in STILL_STAGES:
            update(still_frames[stage])
            out = fig_dir / still_names[stage]
            fig.savefig(out, dpi=ANIM_DPI, facecolor="white")
            stills[stage] = out

        out_mp4 = out_gif = None
        have_ffmpeg = shutil.which("ffmpeg") is not None
        if animate:
            anim = FuncAnimation(
                fig, update, frames=n_frames, interval=1000 / fps
            )
            out_mp4 = fig_dir / f"{stem}-predicted-vs-actual{tag}.mp4"
            out_gif = fig_dir / f"{stem}-predicted-vs-actual{tag}.gif"
            if have_ffmpeg:
                anim.save(
                    out_mp4,
                    writer=FFMpegWriter(
                        fps=fps, codec="libx264", bitrate=-1,
                        extra_args=["-pix_fmt", "yuv420p", "-crf", "18"],
                    ),
                    savefig_kwargs={"facecolor": "white"},
                )
            else:
                out_mp4 = None
                print("ffmpeg not found: skipping the MP4, writing the GIF only")
                anim.save(out_gif, writer=PillowWriter(fps=12))
        plt.close(fig)

    if animate and have_ffmpeg:
        # Palette-based GIF off the MP4: far smaller and cleaner than a
        # frame-by-frame quantization, and it keeps the two in sync.
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(out_mp4),
                "-vf",
                f"fps=12,scale={GIF_WIDTH_PX}:-2:flags=lanczos,split[a][b];"
                "[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=3",
                "-loop", "0", str(out_gif),
            ],
            check=True,
        )

    gained = (set(new_front_ids) - set(old_front["print_id"])) if has_prior else set()
    prefix = "[prototype, synthetic data]" if synthetic else "[measured]"
    print(
        f"{prefix} {stem} front: "
        + ", ".join(new_front["print_id"])
        + (f"; new entrants: {', '.join(sorted(gained))}" if gained else "")
    )
    return stills, out_gif, out_mp4


def render_process_space_figure(suggestions, round_number, path=None,
                                batch_number=None):
    """One strip per print-process parameter: where the data is, where round N goes.

    The point of the panel is the row of black circles. All 17 tested articles
    were printed at one setting of every one of these six parameters, so the
    campaign's whole knowledge of them is a single point, and the batch drawn
    in color is the first time any of them moves.
    """
    fig_dir = BO_DIR / "figures"
    fig_dir.mkdir(exist_ok=True)
    path = path or (
        fig_dir / f"t3-prism-bo-round{round_number}-process-space.png")
    batch_number = round_number if batch_number is None else batch_number
    n = len(PROCESS_SPECS)
    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(
            n + 1, 1, figsize=(12.5, 1.75 * n + 1.0),
            gridspec_kw={"height_ratios": [1] * n + [0.55]})
        for ax, spec in zip(axes, PROCESS_SPECS):
            name = spec["name"]
            lo, hi = spec["bounds"]
            held = AS_PRINTED_PROCESS[name]
            pad = 0.06 * (hi - lo)
            ax.set_xlim(lo - pad, hi + pad)
            ax.set_ylim(-1.0, 1.0)
            for side in ("top", "right", "left"):
                ax.spines[side].set_visible(False)
            ax.spines["bottom"].set_position(("outward", 10))
            ax.spines["bottom"].set_bounds(lo, hi)
            ax.set_yticks([])
            ticks = [lo, held, hi] if lo < held < hi else [lo, hi]
            ax.set_xticks(ticks)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
            ax.plot([lo, hi], [0, 0], color="#d8d7d3", lw=3.4,
                    solid_capstyle="butt", zorder=1)
            vals = suggestions[name].to_numpy()
            if spec["level"] == "filament":
                # one value for the whole batch, so one marker
                vals = vals[:1]
            ax.scatter(vals, np.zeros_like(vals), s=190, marker="D",
                       color=SUGGEST_ORANGE, alpha=0.92, zorder=3,
                       clip_on=False)
            ax.scatter([held], [0], s=400, facecolor="none", edgecolor=INK,
                       linewidths=2.6, zorder=5, clip_on=False)
            unit = spec["unit"].replace("^", "")
            ax.text(0.0, 1.06, f"{name}   ({unit})", transform=ax.transAxes,
                    ha="left", va="bottom", fontsize=20, color=INK)
            level_text = ("article-level" if spec["level"] == "article"
                          else "filament-level, one value for the batch")
            ax.text(1.0, 1.06, level_text, transform=ax.transAxes,
                    ha="right", va="bottom", fontsize=18, color=LABEL_GRAY)

        # key strip: no axis, just the marker vocabulary spelled out
        key = axes[-1]
        key.set_axis_off()
        key.set_xlim(0, 1)
        key.set_ylim(0, 1)
        key.scatter([0.012], [0.55], s=400, facecolor="none", edgecolor=INK,
                    linewidths=2.6, clip_on=False)
        key.text(0.035, 0.55, "all 17 tested articles", va="center",
                 fontsize=19, color=INK)
        key.scatter([0.36], [0.55], s=190, marker="D", color=SUGGEST_ORANGE,
                    clip_on=False)
        key.text(0.382, 0.55, f"round {batch_number} batch (one filament "
                 "setting everywhere)", va="center", fontsize=19,
                 color=SUGGEST_ORANGE)
        fig.tight_layout(h_pad=2.0)
        fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    return path


# ---- round-3 batch assembly: process coordinates and plate structure -----
# Usable plate area and inter-article gap, same numbers PR #35's grid_layout
# used: the H2D's 350 x 320 mm plate less 5 mm margins and a 50 mm +X reserve
# for the prime tower.
PLATE_USABLE_X_MM = 290.0
PLATE_USABLE_Y_MM = 310.0
PLATE_GAP_MM = 6.0


def space_filling_process(n, names, seed):
    """``n`` process points over ``names``, stratified per axis and on-grid.

    Used for the two per-article infill axes. A Latin hypercube rather than
    the acquisition function, because all 17 tested articles sit at one point
    of the process space: there is no data from which a GP could learn to
    prefer one process coordinate over another, and a design that stratifies
    each axis into ``n`` bins is what makes round 4 able to tell them apart.
    Centered (``scramble=False``) rather than randomized inside each bin:
    levels sitting at the bin centers are evenly spaced and cleaner to reason
    about than randomly placed ones. Each coordinate is rounded onto the
    slicer field's own resolution (1 C, 1 percent, 0.1 mm^3/s) so the number
    in the table is the number typed into Bambu Studio.
    """
    from scipy.stats import qmc

    unit = qmc.LatinHypercube(d=len(names), scramble=False, seed=seed).random(n)
    points = []
    for row in unit:
        point = {}
        for name, u in zip(names, row):
            lo, hi = PROCESS_BOUNDS[name]
            value = round_to_step(lo + u * (hi - lo), PROCESS_STEP[name])
            point[name] = float(min(max(value, lo), hi))
        points.append(point)
    return points


def sobol_process_point(names, seed, index=0):
    """The ``index``-th point of a seeded scrambled Sobol sequence, on-grid.

    One point per BATCH, not per article: nozzle temperature and volumetric
    speed are filament settings, so a batch printed as one job carries exactly
    one value of each, and the only way to vary them is across rounds. For a
    single point a scrambled Sobol draw is a uniform random draw with a
    reproducible seed, which is all "optimal" can mean while no data varies
    these axes; Sobol rather than a plain RNG so that a later batch that
    still lacks process data can continue the same sequence (its
    ``batch_number`` picks the index) and the accumulated batch-level points
    stay spread out instead of clumping the way independent draws can.
    Coordinates are rounded onto the slicer field's own resolution, same as
    ``space_filling_process``.
    """
    from scipy.stats import qmc

    sampler = qmc.Sobol(d=len(names), scramble=True, seed=seed)
    if index:
        sampler.fast_forward(index)
    row = sampler.random(1)[0]
    point = {}
    for name, u in zip(names, row):
        lo, hi = PROCESS_BOUNDS[name]
        value = round_to_step(lo + u * (hi - lo), PROCESS_STEP[name])
        point[name] = float(min(max(value, lo), hi))
    return point


# Reference point for hypervolume bookkeeping, the same (t180, e_reb_mJ)
# corner used for the round-2 front-expansion numbers on PR #102: slightly
# worse than the worst article measured so far on each axis.
HV_REF = (1.35, 15.0)


def hypervolume_2d(xs, ys, ref=HV_REF):
    """Dominated hypervolume of 2-D minimization points against ``ref``."""
    mask = pareto_mask(xs, ys)
    pts = sorted(zip(np.asarray(xs, float)[mask], np.asarray(ys, float)[mask]))
    hv, ceiling = 0.0, ref[1]
    for x, y in pts:
        if x >= ref[0] or y >= ceiling:
            continue
        hv += (ref[0] - x) * (ceiling - y)
        ceiling = y
    return hv


def best_predicted_position(front, suggestions):
    """Frame index of the batch's best-predicted specimen.

    Best = the candidate whose predicted means add the most dominated
    hypervolume to the measured front at ``HV_REF``. When no candidate's
    predicted means improve the front (a humble model predicts inside it),
    the tie-break is the lowest predicted t180, the campaign's primary
    endpoint per the Edison round-2 review.
    """
    fx = front[obj1_name].to_numpy(float)
    fy = front[obj2_name].to_numpy(float)
    base = hypervolume_2d(fx, fy)
    px = suggestions[f"pred_{obj1_name}_mean"].to_numpy(float)
    py = suggestions[f"pred_{obj2_name}_mean"].to_numpy(float)
    hvi = np.array([
        hypervolume_2d(np.append(fx, x), np.append(fy, y)) - base
        for x, y in zip(px, py)
    ])
    if hvi.max() > 1e-9:
        return suggestions.index[int(np.argmax(hvi))], float(hvi.max())
    return suggestions.index[int(np.argmin(px))], 0.0


def plates_for_packing(footprint_mm):
    """Plate number per article: as few plates as the batch packs onto.

    The filament settings are one value for the whole batch, so a plate
    carries no treatment and is nothing but floor space. Plate counts are
    tried smallest first; articles are chunked largest-first so an oversized
    article inflates one plate's uniform grid cell rather than every plate's.
    """
    n = len(footprint_mm)
    order = sorted(range(n), key=lambda i: -footprint_mm[i])
    for n_plates in range(1, n + 1):
        bounds = [round(k * n / n_plates) for k in range(n_plates + 1)]
        chunks = [order[bounds[k]:bounds[k + 1]] for k in range(n_plates)]
        if all(plate_packing([footprint_mm[i] for i in c])[2] for c in chunks):
            plate_of = [0] * n
            for plate, chunk in enumerate(chunks, start=1):
                for i in chunk:
                    plate_of[i] = plate
            return plate_of
    raise ValueError("an article is too large to pack even on its own plate")


def smallest_printed_r_mm():
    """Smallest as-printed end-cap radius over every article printed so far."""
    radii = []
    for path in (BO_DIR / "t3-prism-bo-batch-print-key.csv", ROUND2_DESIGNS):
        if path.exists():
            radii.append(float(pd.read_csv(path)["R_print_mm"].min()))
    return min(radii) if radii else float("nan")


def plate_packing(footprint_mm):
    """(width, height, fits) of a uniform-cell grid holding these articles."""
    n = len(footprint_mm)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    cell = max(footprint_mm) + PLATE_GAP_MM
    width = cols * cell - PLATE_GAP_MM
    height = rows * cell - PLATE_GAP_MM
    return width, height, (width <= PLATE_USABLE_X_MM
                           and height <= PLATE_USABLE_Y_MM)


def write_plate_recipe(suggestions, round_number, target_g, path=None,
                       batch_number=None):
    """Emit the slicer recipe: one filament block for the batch, overrides per part."""
    batch_number = round_number if batch_number is None else batch_number
    floor = smallest_printed_r_mm()
    path = path or BO_DIR / f"t3-prism-bo-round{round_number}-plate-recipe.md"
    first = suggestions.iloc[0]
    best_trial = None
    if "best_predicted" in suggestions.columns:
        marked = suggestions[suggestions["best_predicted"].astype(bool)]
        if len(marked):
            best_trial = int(marked["trial_index"].iloc[0])
    n_plates = suggestions["plate"].nunique()
    lines = [
        f"# Round-{batch_number} print recipe",
        "",
        "Generated by `python bo/t3_prism_bo_campaign.py --round "
        f"{round_number} --batch-number {batch_number}`. Every article is "
        "specified at "
        f"{target_g:.2f} g as printed; the scale column is what gets that mass "
        "at that article's own strut infill, so a sparse article is a larger "
        "one.",
        "",
        "## Filament settings, one value for the whole batch",
        "",
        f"- PLA at {first['pla_nozzle_temp_C']:.0f} C and "
        f"{first['pla_flow_mm3_s']:.1f} mm^3/s "
        f"({flow_to_mm_s(first['pla_flow_mm3_s']):.0f} mm/s at the profile's "
        "0.62 x 0.30 mm bead)",
        f"- TPU at {first['tpu_nozzle_temp_C']:.0f} C and "
        f"{first['tpu_flow_mm3_s']:.1f} mm^3/s "
        f"({flow_to_mm_s(first['tpu_flow_mm3_s']):.0f} mm/s)",
        "",
        "These four are filament settings, so a print job carries exactly one "
        "value of each. Set them once and print every plate of this batch "
        "with them"
        + (": formally they are the print parameters of trial "
           f"{best_trial}, the batch's best-predicted specimen, applied "
           "everywhere. " if best_trial is not None else ". ")
        + "With all 17 tested articles at a single point of the process "
        "space there is no data to prefer one setting over another, so the "
        "values were drawn by Sobol sampling within the bounds (see the "
        "README) rather than asked of the model.",
        "",
    ]
    if first["tpu_nozzle_temp_C"] > 240:
        lines += [
            "**Before slicing, switch the TPU filament preset.** Both tested "
            "plates carry `Bambu TPU 85A @BBL H2D 0.4 nozzle`, left over from "
            "before the high-flow hotend went in, and it caps the temperature "
            "window at 240 C, below what this batch asks for. Switch to "
            "`Bambu TPU 85A @BBL H2D`, whose window is 200 to 250 C. Typing "
            "the number into the old preset is not the same thing.",
            "",
        ]
    lines += [
        "The two infill densities are per part, set by right-clicking the "
        "part in the object list and adding a sparse infill density override: "
        "the `-struts` part runs on extruder 1 (PLA), the `-cables` part on "
        "extruder 2 (TPU). Without those overrides both parts inherit the one "
        "global value and the batch loses its two per-article process axes.",
        "",
        f"Articles whose end-cap radius comes out below {floor:.1f} mm are "
        "flagged `end cap`. That is the smallest article printed so far, and "
        "the three igloo mounts and three key-seats are absolute-size, so "
        "check in the slicer that they still fit before printing.",
        "",
    ]
    for plate, group in suggestions.groupby("plate", sort=True):
        w, h, fits = plate_packing(group["footprint_d_mm"].tolist())
        lines += [
            f"## Plate {int(plate)} ({len(group)} articles"
            + (", the whole batch)" if n_plates == 1 else ")"),
            "",
            f"- Packing: {w:.0f} x {h:.0f} mm of the usable "
            f"{PLATE_USABLE_X_MM:.0f} x {PLATE_USABLE_Y_MM:.0f} mm"
            + ("." if fits else ", WHICH DOES NOT FIT: split this plate."),
            "",
            "| trial | struts infill | cables infill | scale | R (mm) | "
            "H (mm) | strut Ø (mm) | cable Ø (mm) | footprint Ø (mm) | flags |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for _, row in group.iterrows():
            flags = []
            if not row["envelope_ok"]:
                flags.append("envelope > 250 cm3")
            if not row["cable_bridge_ok"]:
                flags.append("cable < 3.0 mm")
            if row["R_print_mm"] < floor:
                flags.append("end cap")
            if best_trial is not None and int(row["trial_index"]) == best_trial:
                flags.append("best predicted")
            lines.append(
                f"| {int(row['trial_index'])} | {row['strut_infill_pct']:.0f} % "
                f"| {row['tpu_infill_pct']:.0f} % | {row['scale']:.4f} "
                f"| {row['R_print_mm']:.2f} | {row['H_print_mm']:.2f} "
                f"| {row['strut_d_print_mm']:.2f} | {row['cable_d_print_mm']:.2f} "
                f"| {row['footprint_d_mm']:.1f} | {', '.join(flags) or 'ok'} |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n")
    return path


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
    ap.add_argument("--batch-size", type=int, default=9,
                    help="articles per round (9, one 3x3 grid's worth)")
    ap.add_argument(
        "--freeze-process",
        action="store_true",
        help=(
            "pin all six print-process parameters at the values both tested "
            "plates were printed at, reducing the batch to the shape-plus-mass "
            "batch of rounds 1 and 2"
        ),
    )
    ap.add_argument(
        "--target-mass-g",
        type=float,
        default=DEFAULT_PRINTED_MASS_TARGET_G,
        help=(
            "constant as-printed mass every suggested article is projected "
            "onto (default: the weighed mass of the S0 reference bpx68c)"
        ),
    )
    ap.add_argument("--round", type=int, default=1,
                    help="run number of this script, used for file names")
    ap.add_argument(
        "--batch-number",
        type=int,
        default=None,
        help=(
            "which physical print batch these suggestions are, for the "
            "figure callout and the recipe title. Defaults to --round plus "
            "one, which is right whenever every previous run's batch was "
            "printed. Run 2's batch never was, so run 3 supersedes it and "
            "takes --batch-number 3"
        ),
    )
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
        "--measured-round2",
        action="store_true",
        help=(
            "draw the predicted-vs-measured figure set and animation for the "
            "round-2 batch from the MEASURED campaign summary "
            "(t3-prism-bo-round1-drop-results.csv) against the predictions "
            "the printed plate was generated from "
            "(t3-prism-bo-round1-predictions.csv); no model refit"
        ),
    )
    ap.add_argument(
        "--per-gram",
        action="store_true",
        help=(
            "plot rebound energy divided by each article's mass (mJ/g per "
            "drop; predictions divided by their predicted or target mass), "
            "per the PR #33 intensive-form notes; display only, the BO fit "
            "and the recorded CSVs stay in absolute mJ; use with "
            "--plot-only or --measured-round2"
        ),
    )
    ap.add_argument(
        "--no-animation",
        action="store_true",
        help=(
            "with --prototype-next-round, write only the four still PNGs "
            "and skip the animated GIF/MP4"
        ),
    )
    args = ap.parse_args(argv)
    batch_number = args.round + 1 if args.batch_number is None else args.batch_number

    X1, y1, labels1, masses1, pending = load_training_data(args.results, args.design)
    X2, y2, labels2, masses2, trial_of = load_round2_training_data()
    X_train = X1 + X2
    y_train = y1 + y2
    labels = labels1 + labels2
    masses = masses1 + masses2

    if args.per_gram and not (args.plot_only or args.measured_round2):
        ap.error("--per-gram is a display mode: use it with --plot-only "
                 "or --measured-round2 (the BO fit stays in absolute mJ)")
    # weighed mass per tested article, for the per-gram display division
    mass_of = {lab.split(" ")[0]: m for lab, m in zip(labels, masses)}
    if args.per_gram:
        set_per_gram_mode()

    if args.measured_round2:
        # The real-data version of the prototype: predictions frozen at the
        # plate that was printed (7a048ee), landings from the measured
        # round-2 campaign summary. No Ax import needed.
        predictions = pd.read_csv(ROUND2_PREDICTIONS)
        actual, kept = measured_round2_frame(y2, labels2, trial_of, predictions)
        obs1 = observed_frame(y1, labels1)
        if args.per_gram:
            # measured values by weighed mass; predictions by the mass the
            # model predicted for the design when the plate was generated
            obs1[obj2_name] /= obs1["print_id"].map(mass_of)
            actual[obj2_name] /= actual["print_id"].map(mass_of)
            predictions[f"pred_{obj2_name}_mean"] /= predictions["pred_mass_g_mean"]
            predictions[f"pred_{obj2_name}_sd"] /= predictions["pred_mass_g_mean"]
        stills, gif, mp4 = render_round2_prototype(
            obs1,
            predictions.loc[kept].reset_index(drop=True),
            actual, 2, animate=not args.no_animation, synthetic=False,
        )
        print("Measured round-2 stills (slide order):")
        for i, stage in enumerate(STILL_STAGES, start=1):
            print(f"  slide {i} ({stage}): {stills[stage]}")
        if gif or mp4:
            print("Animation saved to "
                  + ", ".join(str(x) for x in (mp4, gif) if x))
        return 0

    if args.plot_only or args.prototype_next_round:
        observed = observed_frame(y_train, labels)
        suggestions = pd.read_csv(
            BO_DIR / f"t3-prism-bo-suggestions-round{args.round}.csv"
        )
        if args.per_gram:
            observed[obj2_name] /= observed["print_id"].map(mass_of)
            # round-2+ suggestions are pinned at the constant printed-mass
            # target; the mass-blind round-1 file carries a predicted mass
            div = suggestions.get(
                "mass_printed_g", suggestions.get("pred_mass_g_mean")
            )
            suggestions[f"pred_{obj2_name}_mean"] /= div
            suggestions[f"pred_{obj2_name}_sd"] /= div
        if args.plot_only:
            prior = None
            if args.round >= 2 and y1:
                # the front as it stood before the newest measured batch,
                # drawn as a faded gray line for the hypervolume comparison
                r1_frame = observed_frame(y1, labels1)
                if args.per_gram:
                    r1_frame[obj2_name] /= r1_frame["print_id"].map(mass_of)
                prior = pareto_front(r1_frame)
            print(
                "Figure saved to "
                f"{render_objective_figure(observed, suggestions, args.round, prior_front=prior, batch_number=batch_number)}"
            )
            # a batch carrying print-process columns can have its recipe and
            # its process-space panel rebuilt here too, with no Ax install
            if "plate" in suggestions.columns and not args.per_gram:
                print("Plate recipe written to " + str(write_plate_recipe(
                    suggestions, args.round,
                    float(suggestions["target_mass_g"].iloc[0]),
                    batch_number=batch_number)))
                print("Process-space figure saved to "
                      + str(render_process_space_figure(
                          suggestions, args.round, batch_number=batch_number)))
        if args.prototype_next_round:
            actual = synthesize_round2_outcomes(suggestions, seed=args.seed)
            dummy_csv = (
                BO_DIR
                / f"t3-prism-bo-round{args.round + 1}-outcomes-PROTOTYPE-dummy.csv"
            )
            actual[["print_id", "trial_index", *PARAM_NAMES, obj1_name, obj2_name]].to_csv(
                dummy_csv, index=False, float_format="%.4f"
            )
            stills, gif, mp4 = render_round2_prototype(
                observed, suggestions, actual, args.round + 1,
                animate=not args.no_animation,
            )
            w, h = int(ANIM_FIGSIZE[0] * ANIM_DPI), int(ANIM_FIGSIZE[1] * ANIM_DPI)
            print(f"Prototype stills ({w} x {h} px each, slide order):")
            for i, stage in enumerate(STILL_STAGES, start=1):
                print(f"  slide {i} ({stage}): {stills[stage]}")
            print(f"Dummy outcomes: {dummy_csv}")
            if gif or mp4:
                print(
                    "Prototype animation saved to "
                    + ", ".join(str(x) for x in (mp4, gif) if x)
                )
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
    print(
        "Every one of them carries the same print-process coordinates ("
        + ", ".join(f"{k} {v:g}" for k, v in AS_PRINTED_PROCESS.items())
        + "), read out of the two committed .3mf projects. The six process "
        "parameters are therefore unidentified from existing data, and this "
        "batch is their initialization."
    )

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
        f"mass is a parameter: round {args.round} pins every suggestion at "
        f"{args.target_mass_g:.2f} g so the same correlation cannot be "
        "re-created by the batch."
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
    proposed_indices = list(parameterizations.keys())
    proposed = [dict(p) for p in parameterizations.values()]
    model = ax_client.generation_strategy.model

    # ---- process coordinates --------------------------------------------
    # The acquisition function chose values for the six process parameters
    # too, and they are worth nothing. A GP cannot learn a response from an
    # input that never varied, and every tested article sits at one point of
    # this subspace, so what little sensitivity the model shows along it is
    # the SAAS prior rather than evidence, and where the optimizer landed
    # inside it is an artifact of its starting points. Report the spread it
    # produced, then replace it with a stratified design.
    print("\nProcess axes as the acquisition left them (all 17 observations "
          "sit at one point of this subspace, so this is prior, not signal):")
    for name in PROCESS_PARAM_NAMES:
        vals = np.array([p[name] for p in proposed])
        lo, hi = PROCESS_BOUNDS[name]
        print(f"  {name:<20} {vals.min():8.2f} to {vals.max():8.2f} "
              f"(covers {100 * (vals.max() - vals.min()) / (hi - lo):5.1f} "
              "percent of its range)")

    if args.freeze_process:
        filament_pt = {k: AS_PRINTED_PROCESS[k] for k in FILAMENT_PROCESS_PARAMS}
        article_pts = [{k: AS_PRINTED_PROCESS[k] for k in ARTICLE_PROCESS_PARAMS}
                       for _ in proposed]
        print("\n--freeze-process: every article pinned at the as-printed "
              "process point, so this batch varies shape only.")
    else:
        # One set of filament settings for the whole batch: formally the
        # optimal predicted print parameters of the batch's best-predicted
        # specimen (named below), applied everywhere. No data varies these
        # axes yet, so "optimal predicted" cannot be computed and the point
        # is Sobol-drawn instead; batch N of the campaign takes point N-3 of
        # the same seeded sequence, so if later batches are still drawn this
        # way the accumulated points stay spread out.
        sobol_index = max(batch_number - 3, 0)
        filament_pt = sobol_process_point(
            FILAMENT_PROCESS_PARAMS, args.seed + 1, index=sobol_index)
        article_pts = space_filling_process(
            len(proposed), ARTICLE_PROCESS_PARAMS, args.seed)
        print("\nFilament settings, one value for the whole batch (point "
              f"{sobol_index} of the seeded Sobol sequence over the bounds; "
              "no tested article varies these axes, so a model-preferred "
              "setting does not exist yet):")
        for k in FILAMENT_PROCESS_PARAMS:
            print(f"  {k:<20} {filament_pt[k]:g}")
    delivered = [dict(p, **a, **filament_pt)
                 for p, a in zip(proposed, article_pts)]

    # How much did moving the process coordinates change what the model
    # claims? If the answer is "much less than the prediction's own sd", the
    # replacement above cost the batch nothing in acquisition value, which is
    # the whole argument for making it.
    f_prop, _ = model.predict(
        [ObservationFeatures(parameters=dict(x)) for x in proposed])
    f_mean, f_cov = model.predict(
        [ObservationFeatures(parameters=dict(x)) for x in delivered])
    print("\nPrediction shift from that replacement, against the model's own "
          "uncertainty:")
    for metric in (obj1_name, obj2_name):
        shift = np.abs(np.asarray(f_mean[metric]) - np.asarray(f_prop[metric]))
        sd = np.sqrt([f_cov[metric][metric][j] for j in range(len(delivered))])
        print(f"  {metric:<10} max |change| {shift.max():.4g} "
              f"vs. mean posterior sd {sd.mean():.4g} "
              f"({100 * shift.max() / sd.mean():.2f} percent of it)")

    # Record the delivered points, not the proposed ones, as the pending
    # trials: the snapshot is what a later round warm-starts from, so it has
    # to hold the batch that is actually going to the printer.
    try:
        for idx in proposed_indices:
            ax_client.abandon_trial(
                trial_index=idx,
                reason="process coordinates replaced by the stratified design",
            )
        trial_indices = [ax_client.attach_trial(x)[1] for x in delivered]
    except Exception as exc:  # pragma: no cover - Ax API drift
        print(f"WARNING: could not re-attach the delivered batch ({exc}); the "
              "snapshot keeps the proposed process coordinates. The "
              "suggestions CSV is authoritative either way.")
        trial_indices = proposed_indices

    rows = []
    for j, (trial_index, parameterization) in enumerate(
            zip(trial_indices, delivered)):
        row = {"round": args.round, "plate": 0,
               "trial_index": trial_index, "best_predicted": False}
        row.update({name: parameterization[name] for name in PARAM_NAMES})
        row[mass_param] = float(parameterization[mass_param])
        row.update({name: float(parameterization[name])
                    for name in PROCESS_PARAM_NAMES})
        row["pla_speed_mm_s"] = flow_to_mm_s(row["pla_flow_mm3_s"])
        row["tpu_speed_mm_s"] = flow_to_mm_s(row["tpu_flow_mm3_s"])
        for metric in (obj1_name, obj2_name):
            row[f"pred_{metric}_mean"] = f_mean[metric][j]
            row[f"pred_{metric}_sd"] = float(np.sqrt(f_cov[metric][metric][j]))
        # implied rebound fraction at the target mass, for comparison with the
        # raw e_rebound column of the results CSV
        row["pred_e_rebound_approx"] = row[f"pred_{obj2_name}_mean"] / (
            args.target_mass_g * G_M_S2 * DROP_H_M
        )
        # as-printed geometry under the constant-printed-mass projection at
        # this article's own infill, with PR #35's two printability checks
        # evaluated on it
        row["target_mass_g"] = args.target_mass_g
        projected = mass_model.project(
            {name: parameterization[name] for name in PARAM_NAMES},
            args.target_mass_g,
            parameterization["strut_infill_pct"],
            parameterization["tpu_infill_pct"],
        )
        row.update({k: projected[k] for k in (
            "scale", "R_print_mm", "H_print_mm", "strut_d_print_mm",
            "cable_d_print_mm", "joint_d_print_mm", "core_d_print_mm",
            "shell_d_print_mm", "footprint_d_mm", "solid_mass_g",
            "printed_mass_g", "envelope_cm3", "envelope_ok", "cable_bridge_ok",
        )})
        rows.append(row)
    suggestions = pd.DataFrame(rows)
    # plates are floor space only now that the filament settings are one
    # value everywhere; use as few as the footprints pack onto
    suggestions["plate"] = plates_for_packing(
        suggestions["footprint_d_mm"].tolist())
    suggestions = suggestions.sort_values(
        ["plate", "trial_index"]).reset_index(drop=True)

    # The specimen the global filament settings formally belong to.
    front = pareto_front(observed_frame(y_train, labels))
    best_pos, best_hvi = best_predicted_position(front, suggestions)
    suggestions.loc[best_pos, "best_predicted"] = True
    best = suggestions.loc[best_pos]
    print(
        f"\nBest-predicted specimen of the batch: trial "
        f"{int(best['trial_index'])} (predicted {obj1_name} "
        f"{best[f'pred_{obj1_name}_mean']:.3f}, {obj2_name} "
        f"{best[f'pred_{obj2_name}_mean']:.2f} mJ), "
        + (f"adding {best_hvi:.3f} of predicted hypervolume over the "
           f"measured front at reference {HV_REF}."
           if best_hvi > 0 else
           "by lowest predicted t180: no candidate's predicted means improve "
           "the measured front, so predicted hypervolume gain cannot rank "
           "them.")
        + " The batch-wide filament settings are formally this specimen's "
        "print parameters, applied everywhere."
    )

    n_env = int((~suggestions["envelope_ok"]).sum())
    n_cab = int((~suggestions["cable_bridge_ok"]).sum())
    print(
        f"\nProjected onto {args.target_mass_g:.2f} g printed: scale "
        f"{suggestions['scale'].min():.3f} to {suggestions['scale'].max():.3f}; "
        f"{n_env} over the 250 cm^3 envelope, {n_cab} under the 3.0 mm cable "
        "self-bridging floor (flagged, not dropped, same as round 1)."
    )
    for plate, group in suggestions.groupby("plate", sort=True):
        w, h, fits = plate_packing(group["footprint_d_mm"].tolist())
        print(f"  plate {int(plate)}: {len(group)} articles, "
              f"{w:.0f} x {h:.0f} mm of {PLATE_USABLE_X_MM:.0f} x "
              f"{PLATE_USABLE_Y_MM:.0f} mm usable"
              + ("" if fits else "  DOES NOT FIT: split this plate"))

    # The three igloo mounts and three key-seats are absolute-size, so a
    # design that projects small hands them a bigger share of the article and
    # a smaller end cap to sit on. Denser infill projects smaller, so this is
    # the corner the new infill axis pushes into.
    floor = smallest_printed_r_mm()
    small = suggestions[suggestions["R_print_mm"] < floor]
    print(f"End-cap radius {suggestions['R_print_mm'].min():.1f} to "
          f"{suggestions['R_print_mm'].max():.1f} mm as printed, against "
          f"{floor:.1f} mm for the smallest article printed so far.")
    if len(small):
        trials = ", ".join(str(int(t)) for t in small["trial_index"])
        print(f"  {len(small)} of {len(suggestions)} go below that (trial "
              f"{trials}). The sensor housings do not scale with the design, "
              "so check in the slicer that they still fit the end cap.")

    recipe = write_plate_recipe(suggestions, args.round, args.target_mass_g,
                                batch_number=batch_number)
    print(f"Plate recipe written to {recipe}")

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
    out_png = render_objective_figure(observed_frame(y_train, labels), suggestions,
                                      args.round, batch_number=batch_number)
    print(f"Figure saved to {out_png}")
    proc_png = render_process_space_figure(suggestions, args.round,
                                           batch_number=batch_number)
    print(f"Process-space figure saved to {proc_png}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
