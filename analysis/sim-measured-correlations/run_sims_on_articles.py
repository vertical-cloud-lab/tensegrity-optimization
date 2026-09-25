"""Run the #33 drop-tower simulators on every measured campaign article.

The simulation work from issues #32/#33 (branch
``copilot/explore-simulations-for-tensegrity``, tip ``94e53a8``, 2026-08-26)
built three tiers of drop-tower analogue and correlated them against the
bench, but only ever at seed-batch scale (n = 7 to 10 measured articles).
This driver re-runs the two cheap tiers on all 44 LOGO articles (plus the
mapped-but-unmeasured batch-1 prints) at their as-printed geometry and
weighed mass, and the regime evaluators on each distinct design, so the
correlation audit next door can test the old n = 7 findings at n = 35/44.

Tiers run here (code imported from the sim branch tree, see --sim-dir):

- Tier C ``drop_tower_sim.simulate``: rigid struts, dead-band tendons,
  calibrated Hunt-Crossley mat. Outputs the campaign objective pair plus
  tendon strain/energy, stroke, pulse width.
- Tier B ``drop_tower_tierB.simulate_tierB``: 6-segment flexural struts,
  Kelvin-Voigt tendons. Adds ringdown fn/zeta (dominant and flexural band).
- Regime metrics ``bo_evaluator.evaluate_printable_design`` (crutch and
  lander): F_peak_N, SEA_J_per_g, SEA_J_per_cm3, eta, F_base_peak_N, plus
  analytic cell mass / envelope / footprint. Note the regime override does
  not consume the twist axis (known Tier-C plumbing gap, sobol_t3
  diagnostics); the drop-tower tiers above do consume twist.

Article identity and geometry come from the campaign's photo-confirmed
print keys and per-trial design tables (vendored under data/campaign/ from
branch ``claude/issue-98-20260821-0103`` at ``3ad4dd6``), NOT from the
geometry columns of the drop-results CSVs, which for round 1 are known to
disagree with the confirmed key (tier_promotion.md, 2026-08-25).
``amdjwm`` (measured, seed batch) has no design mapping and cannot be
simulated; it is excluded here and joins only the measured-vs-measured
part of the audit.

Usage::

    python run_sims_on_articles.py --sim-dir /tmp/simtree/simulations

where --sim-dir points at the ``simulations/`` tree of the sim branch at
``94e53a8`` (``git archive origin/copilot/explore-simulations-for-tensegrity
simulations | tar -x -C /tmp/simtree``). Requires mujoco, numpy, pandas,
scipy. Deterministic: the simulators are noiseless and single-threaded.

Outputs (data/sim-articles/):

- ``sim_articles.csv``: one row per mapped article, roster + tierC_* +
  tierB_* channels.
- ``regime_designs.csv``: one row per distinct design, crutch_* and
  lander_* regime metrics + geometry metrics.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CAMP = HERE / "data" / "campaign"
CV = HERE.parent / "cv-signal-audit" / "data"
OUT = HERE / "data" / "sim-articles"

SIM_BRANCH_COMMIT = "94e53a8"      # copilot/explore-simulations-for-tensegrity
CAMPAIGN_COMMIT = "3ad4dd6"        # claude/issue-98-20260821-0103

# Seed specimens measured on the tower, per the batch drop results and the
# round-5 LOGO roster. Spec 8 printed three times (dea4ls / bag26v / ghmj4y);
# bag26v is the article in the drop results and the LOGO, per the issue #98
# comment recorded in the print key's role column.
SEED_ARTICLES = {
    "9hhbkp", "6lhxfy", "autv5r", "ebdna8", "nvxsrv",
    "6nheas", "1zm8rv", "ajhby6", "bag26v", "bpx68c",
}


def build_roster() -> pd.DataFrame:
    """One row per design-mapped article: as-printed dims + weighed mass."""
    rows = []

    key1 = pd.read_csv(CAMP / "t3-prism-bo-batch-print-key.csv")
    nominal = pd.read_csv(CAMP / "t3-prism-bo-batch.csv").set_index("specimen")
    for _, r in key1.iterrows():
        if r["print_id"] not in SEED_ARTICLES:
            continue
        spec = str(r["specimen"])
        if spec == "S0":
            nom = {"R_mm": 25.0, "H_mm": 70.0, "twist_deg": 60.0,
                   "strut_d_mm": 6.0, "cable_d_mm": 3.0}
        else:
            n = nominal.loc[int(spec)]
            nom = {k: float(n[k]) for k in
                   ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")}
        rows.append({
            "print_id": r["print_id"], "batch": "seed",
            "design": r["print_id"],           # seed designs are unique
            "source_trial": np.nan,
            "R_print_mm": float(r["R_print_mm"]),
            "H_print_mm": float(r["H_print_mm"]),
            "twist_deg": float(r["twist_deg"]),
            "strut_d_print_mm": float(r["strut_d_print_mm"]),
            "cable_d_print_mm": float(r["cable_d_print_mm"]),
            "mass_g": float(r["mass_g"]),
            **{f"nom_{k}": v for k, v in nom.items()},
        })

    for rnd, batches in (("round1", ("r2d2c",)),
                         ("round3", ("drran", "2dran")),
                         ("round4", ("corny",))):
        key = pd.read_csv(CV / f"t3-prism-bo-{rnd}-print-key.csv")
        designs = pd.read_csv(
            CAMP / f"t3-prism-bo-{rnd}-designs.csv").set_index("source_trial"
            if rnd == "round1" else "trial_index")
        for _, r in key.iterrows():
            if not any(str(r["print_id"]).startswith(b) for b in batches):
                continue
            d = designs.loc[int(r["source_trial"])]
            rows.append({
                "print_id": r["print_id"],
                "batch": ("2dran" if str(r["print_id"]).startswith("2dran")
                          else batches[0]),
                "design": f"trial{int(r['source_trial'])}",
                "source_trial": int(r["source_trial"]),
                "R_print_mm": float(d["R_print_mm"]),
                "H_print_mm": float(d["H_print_mm"]),
                "twist_deg": float(d["twist_deg"]),
                "strut_d_print_mm": float(d["strut_d_print_mm"]),
                "cable_d_print_mm": float(d["cable_d_print_mm"]),
                "mass_g": float(r["mass_g_with_label"]),
                **{f"nom_{k}": float(d[k]) for k in
                   ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")},
            })

    df = pd.DataFrame(rows)
    assert df.print_id.is_unique, "duplicate print ids in roster"
    return df


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sim-dir", default="/tmp/simtree/simulations",
                    help=f"simulations/ tree at {SIM_BRANCH_COMMIT}")
    ap.add_argument("--skip-tierb", action="store_true")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(Path(args.sim_dir).resolve()))
    import drop_tower_sim as dts
    from bo_evaluator import (cell_geometry_metrics, evaluate_printable_design,
                              parameterization_to_design)
    from drop_tower_tierB import simulate_tierB
    from regimes import CRUTCH, NASA_LANDER

    roster = build_roster()
    print(f"roster: {len(roster)} mapped articles, "
          f"{roster.design.nunique()} designs")

    def design_of(row):
        return parameterization_to_design({
            "R_mm": row.R_print_mm, "H_mm": row.H_print_mm,
            "twist_deg": row.twist_deg, "strut_d_mm": row.strut_d_print_mm,
            "cable_d_mm": row.cable_d_print_mm})

    recs = []
    for _, r in roster.iterrows():
        t0 = time.time()
        design = design_of(r)
        rec = dict(r)

        c = dts.simulate(design, article_mass_g=r.mass_g)
        rec.update({f"tierC_{k}": v for k, v in c.items()
                    if np.isscalar(v) and k != "ok"})

        if not args.skip_tierb:
            b = simulate_tierB(design, article_mass_g=r.mass_g)
            rec.update({f"tierB_{k}": v for k, v in b.items()
                        if np.isscalar(v) and k != "ok"})

        recs.append(rec)
        print(f"{r.print_id}: tierC t180={rec['tierC_t180']:.4f}"
              + (f" tierB t180={rec.get('tierB_t180', float('nan')):.4f}"
                 f" fn={rec.get('tierB_fn_hz', float('nan')):.0f}"
                 if not args.skip_tierb else "")
              + f" [{time.time() - t0:.1f}s]", flush=True)

    arts = pd.DataFrame(recs)
    OUT.mkdir(parents=True, exist_ok=True)
    arts.to_csv(OUT / "sim_articles.csv", index=False)
    print(f"wrote {OUT / 'sim_articles.csv'} ({len(arts)} rows)")

    drecs = []
    for design_id, grp in roster.groupby("design"):
        r = grp.iloc[0]
        design = design_of(r)
        rec = {"design": design_id, "batch": r.batch}
        rec.update({f"geom_{k}": v
                    for k, v in cell_geometry_metrics(design).items()})
        for tag, regime in (("crutch", CRUTCH), ("lander", NASA_LANDER)):
            res = evaluate_printable_design(design, regime=regime,
                                            base_reaction=True)
            rec.update({f"{tag}_{k}": v for k, v in res.items()
                        if np.isscalar(v)})
        drecs.append(rec)
        print(f"{design_id}: crutch F={rec['crutch_F_peak_N']:.0f} "
              f"lander F={rec['lander_F_peak_N']:.0f}", flush=True)

    des = pd.DataFrame(drecs)
    des.to_csv(OUT / "regime_designs.csv", index=False)
    print(f"wrote {OUT / 'regime_designs.csv'} ({len(des)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
