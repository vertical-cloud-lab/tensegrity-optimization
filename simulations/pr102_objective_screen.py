"""Screen replacement second objectives for the simulated PR #102 campaign.

Context (PR #33, 2026-08-24): the simulated ``e_rebound`` is dead as an
objective (span under 1 % across the ratio manifold, owned by the calibrated
mat rather than the design), and ``zeta_analysis.py`` showed Tier C cannot
resolve the bench's proposed replacement ``zeta_pct`` either (wrong mode
family, parasitic damping floor).  Before swapping in a new second
objective, this script measures every candidate the extended
``drop_tower_sim`` can produce, on the same constant-printed-mass ratio
manifold the campaign searches, and scores each on the three properties an
objective needs:

* **design response**: relative span (max-min over mean) across a Sobol set;
* **independence from t180**: |Spearman rho| well away from 1, ideally a
  genuine trade-off (negative rho), since a near-duplicate of the first
  objective collapses the front to a sliver as ``e_rebound`` did;
* **a physical reading**: asserted per candidate in CANDIDATES, checked by
  the per-axis sensitivities the CSV carries.

Run::

    python pr102_objective_screen.py --n 128
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd
from scipy.stats import qmc, spearmanr

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import pr102_sim_campaign as camp  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"

# candidate -> what it means physically, and which way "better" points
CANDIDATES = {
    "e_rebound": "restitution velocity ratio (the objective being replaced)",
    "t1000": "CFC-1000 transmissibility (high-frequency transmission)",
    "out_180_g": "absolute filtered peak at the top vertex",
    "pulse_ms": "input pulse width at half peak (mat-owned; null control)",
    "in_180_g": "input peak (mat-owned; null control)",
    "peak_tendon_strain": "max TPU tension strain above slack (survivability)",
    "peak_tendon_energy_mJ": "peak elastic energy in the tendon network",
    "stroke_mm": "max top-vertex-to-plate compression (article deformation)",
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)

    lo = np.array([p["bounds"][0] for p in camp.RATIO_PARAMETERS])
    hi = np.array([p["bounds"][1] for p in camp.RATIO_PARAMETERS])
    pts = qmc.Sobol(d=len(lo), scramble=True, seed=args.seed).random(args.n)
    pts = lo + pts * (hi - lo)

    rows = []
    for x in pts:
        params = dict(zip(camp.RATIO_PARAMS, map(float, x)))
        res = camp.evaluate(params, space="ratios")
        rows.append({**params, **res})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pr102_objective_screen.csv", index=False,
              float_format="%.6g")

    ok = df[df["feasible"].astype(bool) & np.isfinite(df["t180"])]
    print(f"{len(ok)}/{len(df)} printable designs")

    summary = []
    for name, meaning in CANDIDATES.items():
        v = ok[name].to_numpy(dtype=float)
        rel_span = float((v.max() - v.min()) / abs(v.mean())) if v.mean() else np.nan
        rho, p = spearmanr(ok["t180"], v)
        row = {"candidate": name, "rel_span": rel_span,
               "rho_vs_t180": float(rho), "p": float(p), "meaning": meaning}
        for ax_name in camp.RATIO_PARAMS:
            r, _ = spearmanr(ok[ax_name], v)
            row[f"rho_{ax_name}"] = float(r)
        summary.append(row)
    sdf = pd.DataFrame(summary)
    sdf.to_csv(OUT / "pr102_objective_screen_summary.csv", index=False,
               float_format="%.4g")
    print(sdf.drop(columns="meaning").to_string(index=False))

    show = ["e_rebound", "t1000", "peak_tendon_strain",
            "peak_tendon_energy_mJ", "stroke_mm", "out_180_g"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5), dpi=170)
    for ax, name in zip(axes.ravel(), show):
        ax.scatter(ok["t180"], ok[name], s=14, alpha=0.7, color="#2a78d6")
        r = sdf.set_index("candidate").loc[name]
        ax.set_title(f"{name}  (span {100 * r['rel_span']:.1f} %, "
                     f"rho vs t180 {r['rho_vs_t180']:+.2f})", fontsize=10)
        ax.set_xlabel("t180 (simulated)")
        ax.set_ylabel(name)
        ax.grid(alpha=0.25, lw=0.5)
    fig.suptitle(f"Second-objective candidates on the constant-mass ratio "
                 f"manifold ({len(ok)} printable Sobol designs)", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "pr102_objective_screen.png", bbox_inches="tight")
    print(f"wrote {OUT}/pr102_objective_screen.{{csv,png}} and _summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
