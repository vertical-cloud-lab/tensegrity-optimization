"""Which simulated observable tracks the measured T-3_01 campaign objectives?

This thread has produced a lot of candidate simulation outputs: Tier-C
payload-acceleration ``F_peak``, base-reaction ``F_base_peak``, elastic
``SEA`` per gram and per cm^3, compaction efficiency ``eta``, and now the
drop-tower analogue's ``t180`` / ``e_rebound`` (``drop_tower_sim``).  The
bench has produced exactly two objectives, on eight articles (PR #86
campaign summary, ingested by PR #102's BO script): CFC-180 transmissibility
``t180`` and rebound energy ``e_reb_mJ``.

This script scores every one of those articles with every candidate
observable and reports the rank correlation against the two measured
objectives, which is the question that decides whether any of these
simulations is worth putting in front of the BO as a prior.

Seven of the eight tested articles carry a design mapping (``amdjwm`` maps
to no known print, and PR #102 skips it for the same reason), so n = 7 and a
Spearman rho needs |rho| >= 0.79 to clear p = 0.05 two-sided.  The table
therefore prints the p-value, and a ``rel_span`` column -- the observable's
range over its mean -- because an observable that ranks perfectly across a
0.1 percent span is ranking numerical structure, not a design effect, and
should not be promoted on its rho alone.

Run::

    python pr102_correlation.py                 # writes CSV + PNG + md
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import drop_tower_sim
from bo_evaluator import evaluate_printable_design, parameterization_to_design
from print_infill import scale_design
from regimes import CRUTCH, NASA_LANDER

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "pr102"
OUT = HERE / "outputs"

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
G = 9.80665
DROP_H_M = 1.524

MEASURED = ["t180", "e_reb_mJ"]


def load_measured() -> pd.DataFrame:
    """Measured objectives joined onto base Sobol coordinates.

    Mirrors ``bo/t3_prism_bo_campaign.py::load_training_data``: skip the
    unmapped article (``amdjwm``), rebuild ``e_reb_mJ`` from the article's own
    weighed mass, and carry the S0 reference in at its base coordinates.
    """
    results = pd.read_csv(DATA / "t3-prism-bo-batch-drop-results.csv",
                          dtype={"spec": "string"})
    design = pd.read_csv(DATA / "t3-prism-bo-batch.csv").set_index("specimen")

    rows = []
    for _, r in results.iterrows():
        spec = None if pd.isna(r["spec"]) else str(r["spec"]).strip()
        if not spec or pd.isna(r["mass_g"]):
            continue
        if spec == "S0":
            params = dict(drop_tower_sim.S0_BASE_PARAMS)
        else:
            base = design.loc[int(spec)]
            params = {n: float(base[n]) for n in PARAM_NAMES}
        rows.append({
            "specimen": r["specimen"], "spec": spec,
            **params,
            "mass_g": float(r["mass_g"]),
            "t180": float(r["t180_mean"]),
            "e_rebound": float(r["e_rebound_mean"]),
            "e_reb_mJ": float(r["e_rebound_mean"]) * float(r["mass_g"]) * G * DROP_H_M,
        })
    return pd.DataFrame(rows)


def score_all(measured: pd.DataFrame, *, base_reaction: bool = True) -> pd.DataFrame:
    """Add every candidate simulated observable to the measured table."""
    out = []
    for _, row in measured.iterrows():
        params = {n: float(row[n]) for n in PARAM_NAMES}
        base_design = parameterization_to_design(params)
        # Each article is simulated at the mass the scale actually read for
        # it, by solving the constant-printed-mass projection for that mass.
        # That is strictly better than projecting to a batch target here:
        # these are specific prints, their weighed masses are known, and
        # ``e_reb_mJ`` is proportional to mass, so using anything else would
        # put a known quantity into the residual.
        weighed_g = float(row["mass_g"])
        model = drop_tower_sim.mass_model()
        scale = model.solve_scale_for_printed_mass(params, weighed_g)
        printed = scale_design(base_design, scale)

        rec = {"print_scale": scale}

        # drop-tower analogue, with and without the infill correction
        dt = drop_tower_sim.simulate(printed, article_mass_g=weighed_g)
        rec.update({f"sim_{k}": v for k, v in dt.items()
                    if not isinstance(v, np.ndarray) and k != "ok"})
        # Infill ablation: same geometry, the mass it would have printed solid.
        solid_g = float(sum(model.solid_grams(params, scale)))
        dt_solid = drop_tower_sim.simulate(printed, article_mass_g=solid_g)
        rec["sim_solid_t180"] = dt_solid["t180"]
        rec["sim_solid_e_reb_mJ"] = dt_solid["e_reb_mJ"]
        rec["sim_solid_mass_g"] = solid_g

        # the application-regime Tier-C observables this thread has been
        # optimizing on, evaluated on the same printed article
        for tag, regime in (("crutch", CRUTCH), ("lander", NASA_LANDER)):
            res = evaluate_printable_design(printed, regime=regime,
                                            base_reaction=base_reaction)
            for key in ("F_peak_N", "SEA_J_per_g", "SEA_J_per_cm3", "eta",
                        "F_base_peak_N"):
                if key in res:
                    rec[f"{tag}_{key}"] = res[key]
            for key in ("cell_mass_g", "envelope_cm3", "footprint_mm2"):
                rec[key] = res[key]
        out.append(rec)
    return pd.concat([measured.reset_index(drop=True), pd.DataFrame(out)], axis=1)


def correlate(scored: pd.DataFrame) -> pd.DataFrame:
    from scipy import stats

    candidates = [c for c in scored.columns
                  if c not in ("specimen", "spec", *MEASURED, "e_rebound")]
    rows = []
    for target in MEASURED:
        y = scored[target].to_numpy(dtype=float)
        for cand in candidates:
            x = scored[cand].to_numpy(dtype=float)
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < 4 or np.allclose(x[ok], x[ok][0]):
                continue
            rho, p_rho = stats.spearmanr(x[ok], y[ok])
            r, p_r = stats.pearsonr(x[ok], y[ok])
            span = (float(np.max(x[ok]) - np.min(x[ok]))
                    / max(abs(float(np.mean(x[ok]))), 1e-12))
            rows.append({"target": target, "observable": cand, "n": int(ok.sum()),
                         "spearman_rho": float(rho), "spearman_p": float(p_rho),
                         "pearson_r": float(r), "pearson_p": float(p_r),
                         "rel_span": span})
    df = pd.DataFrame(rows)
    return df.sort_values(["target", "spearman_rho"],
                          key=lambda s: s.abs() if s.name == "spearman_rho" else s,
                          ascending=[True, False])


def plot(scored: pd.DataFrame, corr: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    top = {t: corr[corr.target == t].iloc[0] for t in MEASURED}
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.4), dpi=200)

    for ax, target in zip(axes[:2], MEASURED):
        best = top[target]
        x = scored[best.observable]
        y = scored[target]
        ax.scatter(x, y, s=50, fc="none", ec="#0b0b0b")
        for _, r in scored.iterrows():
            ax.annotate(r["specimen"], (r[best.observable], r[target]),
                        textcoords="offset points", xytext=(4, 4), fontsize=7,
                        color="#52514e")
        ax.set_xlabel(f"simulated {best.observable}")
        ax.set_ylabel(f"measured {target}")
        ax.set_title(f"best simulated predictor of {target}\n"
                     f"Spearman rho = {best.spearman_rho:+.2f} "
                     f"(p = {best.spearman_p:.3f}, n = {best.n})", fontsize=9)
        ax.grid(alpha=0.25, lw=0.5)

    # ranked bar chart of |rho| for both targets
    ax = axes[2]
    pivot = corr.pivot(index="observable", columns="target", values="spearman_rho")
    pivot = pivot.reindex(pivot.abs().max(axis=1).sort_values().index).tail(14)
    ypos = np.arange(len(pivot))
    ax.barh(ypos - 0.2, pivot[MEASURED[0]], height=0.4, color="#2a78d6",
            label=MEASURED[0])
    ax.barh(ypos + 0.2, pivot[MEASURED[1]], height=0.4, color="#eb6834",
            label=MEASURED[1])
    ax.axvline(0, color="#0b0b0b", lw=0.8)
    crit = 0.786 if int(corr["n"].max()) <= 7 else 0.714
    for v in (-crit, crit):
        ax.axvline(v, color="#52514e", lw=0.8, ls=":")
    ax.set_yticks(ypos)
    ax.set_yticklabels(pivot.index, fontsize=7)
    ax.set_xlabel("Spearman rho vs measured objective")
    n = int(corr["n"].max())
    ax.set_title(f"dotted lines: |rho| for p = 0.05 at n = {n}", fontsize=9)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.25, lw=0.5, axis="x")

    fig.suptitle("Simulated observables vs the measured T-3_01 campaign objectives",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outdir", type=Path, default=OUT)
    ap.add_argument("--no-base-reaction", action="store_true",
                    help="skip the (second) floor-reaction drop per design")
    args = ap.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)

    measured = load_measured()
    print(f"{len(measured)} articles with both a design mapping and a mass.")
    scored = score_all(measured, base_reaction=not args.no_base_reaction)
    corr = correlate(scored)

    scored.to_csv(args.outdir / "pr102_sim_vs_measured.csv", index=False,
                  float_format="%.6g")
    corr.to_csv(args.outdir / "pr102_correlations.csv", index=False,
                float_format="%.4f")
    plot(scored, corr, args.outdir / "pr102_correlation.png")

    for target in MEASURED:
        sub = corr[corr.target == target].head(6)
        print(f"\nTop simulated predictors of measured {target}:")
        print(sub[["observable", "spearman_rho", "spearman_p", "pearson_r",
                   "rel_span"]].to_string(index=False))
    print(f"\nWrote {args.outdir}/pr102_sim_vs_measured.csv, "
          f"pr102_correlations.csv, pr102_correlation.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
