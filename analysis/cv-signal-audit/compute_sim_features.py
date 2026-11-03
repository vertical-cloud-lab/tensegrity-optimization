"""Simulation outputs as candidate input features for the surrogate.

PR #111 (sgbaird, 2026-10-13): "see what happens if you bring in simulation
results from PR #33 as additional contextual variables the model is able to
learn and if it improves uncertainty (see the Honegumi featurization
tutorial). Are these correlated?"

The Honegumi recipe computes features outside Ax for every training point
and every candidate, then adds them to the search space as range
parameters next to the raw inputs, so the GP can use whichever
representation describes the data better. The features here are the #33
drop-tower analogues (Tier C rigid-strut MuJoCo, Tier B flexural-strut
MuJoCo), which ``../sim-measured-correlations/run_sims_on_articles.py``
already ran on every measured article at as-printed geometry and weighed
mass.

This script re-runs the same two simulators on the same roster with one
change: the article mass handed to the simulator is the **design-mean
weighed mass** (the mean over a design's prints; identical to the weighed
mass for the 26 single-print designs) instead of each print's own weighed
mass. Reprint twins therefore share identical feature values, so the
features cannot address a single print the way weighed mass did (audit
README, Sections 6 and 9). The alternative of running with no mass at all
(``article_mass_g=None``) was tried first and rejected: that code path
puts only the sparse-PLA capsule density on the struts, dropping the
joint and housing share of the mass and, in Tier B, the vertex masses
that set the flexural frequencies, so it is a different instrument from
the one the sibling audit validated (Tier B ringdown frequency agreed
with the weighed-mass run at Spearman +0.22). The sensitivity to the
mass choice within a design is small: the nine twin pairs differ by 0.17
to 0.34 g and their Tier C t180 by about 0.003, so a predicted printed
mass from the campaign's mass model (the quantity available before a
candidate is printed) would give practically the same features. The
per-print weighed-mass versions from the sibling run are carried along
with a ``_weighed`` suffix so the two can be compared.

Usage (repo root)::

    python analysis/cv-signal-audit/compute_sim_features.py \
        --sim-dir /tmp/simtree/simulations

where ``--sim-dir`` is the ``simulations/`` tree of the sim branch at
``94e53a8`` (``git archive 94e53a8 simulations | tar -x -C /tmp/simtree``).
Deterministic (no RNG in either simulator). Output:
``data/sim-features.csv``, one row per design-mapped article (46: the 44
LOGO articles plus the printed-but-unmeasured ``ebdna8`` and ``1zm8rv``).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SIM_AUDIT = HERE.parent / "sim-measured-correlations"
SIM_ARTICLES = SIM_AUDIT / "data" / "sim-articles" / "sim_articles.csv"
OUT = HERE / "data" / "sim-features.csv"

SIM_BRANCH_COMMIT = "94e53a8"      # copilot/explore-simulations-for-tensegrity

# The six features the LOGO driver appends to the fit space, chosen before
# any held-out number was looked at, from the sibling audit's design-level
# results: the two purpose-built transmissibility analogues (Tier C and
# Tier B rank the designs almost independently, rho -0.14), one
# representative of the tendon-deformation cluster (strain, energy and
# stroke are one cluster; energy had the strongest design-level rho), the
# Tier C stroke (the payload-stroke axis, nearly uncorrelated with t180),
# and the Tier B ringdown pair (the structural mode the SRS analysis put
# the between-design differences at).
FEATURES = {
    "sim_tierC_t180": "tierC_t180",
    "sim_tierC_tendon_energy_mJ": "tierC_peak_tendon_energy_mJ",
    "sim_tierC_stroke_mm": "tierC_stroke_mm",
    "sim_tierB_t180": "tierB_t180",
    "sim_tierB_fn_hz": "tierB_fn_hz",
    "sim_tierB_zeta_pct": "tierB_zeta_pct",
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sim-dir", default="/tmp/simtree/simulations",
                    help=f"simulations/ tree at {SIM_BRANCH_COMMIT}")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(Path(args.sim_dir).resolve()))
    sys.path.insert(0, str(SIM_AUDIT))
    import drop_tower_sim as dts
    from bo_evaluator import parameterization_to_design
    from drop_tower_tierB import simulate_tierB
    from run_sims_on_articles import build_roster

    roster = build_roster()
    weighed = pd.read_csv(SIM_ARTICLES).set_index("print_id")
    assert set(roster.print_id) == set(weighed.index), "roster changed"
    print(f"roster: {len(roster)} mapped articles, "
          f"{roster.design.nunique()} designs", flush=True)
    design_mass = roster.groupby("design")["mass_g"].mean()

    recs = []
    for _, r in roster.iterrows():
        t0 = time.time()
        design = parameterization_to_design({
            "R_mm": r.R_print_mm, "H_mm": r.H_print_mm,
            "twist_deg": r.twist_deg, "strut_d_mm": r.strut_d_print_mm,
            "cable_d_mm": r.cable_d_print_mm})
        rec = dict(r)
        mass = float(design_mass[r.design])
        rec["mass_used_g"] = mass
        c = dts.simulate(design, article_mass_g=mass)
        rec.update({f"tierC_{k}": v for k, v in c.items()
                    if np.isscalar(v) and k != "ok"})
        b = simulate_tierB(design, article_mass_g=mass)
        rec.update({f"tierB_{k}": v for k, v in b.items()
                    if np.isscalar(v) and k != "ok"})
        for feat, src in FEATURES.items():
            rec[feat] = rec[src]
            rec[f"{feat}_weighed"] = float(weighed.loc[r.print_id, src])
        print(f"{r.print_id}: design-mean mass {mass:.2f} g "
              f"(weighed {r.mass_g:.2f}); tierC t180 {rec['tierC_t180']:.4f} "
              f"(weighed-mass run {rec['sim_tierC_t180_weighed']:.4f}); "
              f"tierB t180 {rec['tierB_t180']:.4f} [{time.time() - t0:.1f}s]",
              flush=True)
        recs.append(rec)

    df = pd.DataFrame(recs)
    # reprint twins must now be indistinguishable in every feature, and a
    # single-print design must reproduce the sibling run (same inputs; the
    # only difference is mujoco 3.15.0 here against 3.14.0 there, which
    # moved the worst channel by 2e-7 relative)
    worst = 0.0
    for design_id, grp in df.groupby("design"):
        if len(grp) > 1:
            for feat in FEATURES:
                assert grp[feat].nunique() == 1, (design_id, feat)
        else:
            for feat in FEATURES:
                a, b = float(grp[feat].iloc[0]), float(grp[f"{feat}_weighed"].iloc[0])
                rel = abs(a - b) / max(1.0, abs(b))
                worst = max(worst, rel)
                assert rel <= 1e-6, (design_id, feat, a, b)
    print(f"single-print designs reproduce the sibling run to {worst:.1e} relative")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, float_format="%.10g")
    print(f"wrote {OUT} ({len(df)} rows, {len(FEATURES)} fit features)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
