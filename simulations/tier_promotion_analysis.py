"""Compare the Tier-B (and, when present, Tier-A) article runs to the bench.

Reads ``outputs/tierB_articles.csv`` (and ``outputs/tierA_articles.csv`` if
the PolyFEM runs have landed), joins the measured channels from both batches
(batch 1: ``t3-prism-bo-batch-drop-results.csv``; round 2:
``t3-prism-bo-round1-drop-results.csv``), and reports, per channel the tier
promotion was supposed to revive (``t180``, ``fn_hz``, ``zeta_pct``,
``e_rebound``):

* simulated vs measured scatter with the identity line,
* Spearman rank correlation (n is small; hypothesis-level, printed with p),
* the span check: does the simulated channel *move* across designs now,
  where Tier C was flat?

Writes ``outputs/tier_promotion_comparison.png`` and
``outputs/tier_promotion_comparison.csv``.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "pr102"
OUT = HERE / "outputs"

# fn/zeta compare the *flexural-band* sim fit (fmin=150 Hz) because every
# bench fit sits in the flexural family (>=286 Hz); the unrestricted
# dominant-line fit is kept in the CSV for the honest spectrum story.
CHANNELS = [("t180", "t180_mean"), ("fn_flex_hz", "fn_hz_mean"),
            ("zeta_flex_pct", "zeta_pct_mean"), ("e_rebound", "e_rebound_mean")]


def measured_table() -> pd.DataFrame:
    b1 = pd.read_csv(DATA / "t3-prism-bo-batch-drop-results.csv")
    b2 = pd.read_csv(DATA / "t3-prism-bo-round1-drop-results.csv")
    cols = ["specimen"] + [m for _, m in CHANNELS]
    return pd.concat([b1[cols], b2[cols]], ignore_index=True).rename(
        columns={"specimen": "print_id"})


def main() -> int:
    from scipy import stats
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sim = pd.read_csv(OUT / "tierB_articles.csv")
    meas = measured_table()
    df = sim.merge(meas, on="print_id", how="left")
    tierA = None
    if (OUT / "tierA_articles.csv").exists():
        tierA = pd.read_csv(OUT / "tierA_articles.csv")
        tierA = tierA[tierA.get("ok", True) == True]  # noqa: E712
        df = df.merge(tierA.add_prefix("tA_"),
                      left_on="print_id", right_on="tA_print_id", how="left")

    df.to_csv(OUT / "tier_promotion_comparison.csv", index=False)

    fig, axes = plt.subplots(2, 4, figsize=(17, 8))
    stats_rows = []
    for j, (sim_col, meas_col) in enumerate(CHANNELS):
        ax = axes[0, j]
        ok = np.isfinite(df[sim_col]) & np.isfinite(df[meas_col])
        x, y = df.loc[ok, meas_col], df.loc[ok, sim_col]
        ax.scatter(x, y, c=["tab:blue" if b == 1 else "tab:orange"
                            for b in df.loc[ok, "batch"]], zorder=3)
        for _, r in df[ok].iterrows():
            ax.annotate(r["print_id"], (r[meas_col], r[sim_col]),
                        fontsize=6, alpha=0.7)
        lo = min(x.min(), y.min()) if len(x) else 0
        hi = max(x.max(), y.max()) if len(x) else 1
        ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, alpha=0.5)
        rho, p = (stats.spearmanr(x, y) if ok.sum() >= 4
                  else (float("nan"), float("nan")))
        ok1 = ok & (df["batch"] == 1)
        rho1, p1 = (stats.spearmanr(df.loc[ok1, meas_col], df.loc[ok1, sim_col])
                    if ok1.sum() >= 4 else (float("nan"), float("nan")))
        stats_rows.append({"channel": sim_col, "n": int(ok.sum()),
                           "spearman_rho": rho, "spearman_p": p,
                           "n_batch1": int(ok1.sum()),
                           "rho_batch1": rho1, "p_batch1": p1})
        ax.set_title(f"{sim_col}: Tier-B vs measured\n"
                     f"rho={rho:+.2f} (p={p:.2f}, n={ok.sum()})")
        ax.set_xlabel("measured")
        ax.set_ylabel("Tier-B simulated")

        ax2 = axes[1, j]
        order = np.argsort(df[sim_col].to_numpy())
        vals = df[sim_col].to_numpy()[order]
        ax2.bar(range(len(vals)), vals,
                color=["tab:blue" if b == 1 else "tab:orange"
                       for b in df["batch"].to_numpy()[order]])
        ax2.set_xticks(range(len(vals)))
        ax2.set_xticklabels(df["print_id"].to_numpy()[order],
                            rotation=90, fontsize=6)
        ax2.set_title(f"simulated {sim_col} across all 21 articles")
    fig.suptitle("Tier-B promotion (flexural struts + Kelvin-Voigt tendons): "
                 "simulated vs measured channels\n"
                 "blue = batch 1, orange = round 2 (as-printed geometry, "
                 "weighed mass)")
    fig.tight_layout()
    fig.savefig(OUT / "tier_promotion_comparison.png", dpi=130)

    # Tier-A panel: article-intrinsic observables (rigid floor, no mat), so
    # fn/zeta compare like-for-like while restitution and peak-g are
    # span/rank checks against rig-mediated measurements, not identities.
    if tierA is not None and len(tierA):
        tA_channels = [
            ("tA_fn_hz", "fn_hz_mean", "flexural ringdown fn (Hz)", True),
            ("tA_zeta_pct", "zeta_pct_mean", "ringdown damping zeta (%)", True),
            ("tA_e_rebound_article", "e_rebound_mean",
             "restitution (article-only vs rig)", False),
            ("tA_peak_top_g", None, "peak top-vertex accel (g)", False),
        ]
        figA, axesA = plt.subplots(2, 4, figsize=(17, 8))
        for j, (sim_col, meas_col, label, identity) in enumerate(tA_channels):
            ax = axesA[0, j]
            if meas_col is not None:
                ok = np.isfinite(df[sim_col]) & np.isfinite(df[meas_col])
                x, y = df.loc[ok, meas_col], df.loc[ok, sim_col]
                ax.scatter(x, y, c=["tab:blue" if b == 1 else "tab:orange"
                                    for b in df.loc[ok, "batch"]], zorder=3)
                for _, r in df[ok].iterrows():
                    ax.annotate(r["print_id"], (r[meas_col], r[sim_col]),
                                fontsize=6, alpha=0.7)
                if identity and len(x):
                    lo = min(x.min(), y.min())
                    hi = max(x.max(), y.max())
                    ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, alpha=0.5)
                rho, p = (stats.spearmanr(x, y) if ok.sum() >= 4
                          else (float("nan"), float("nan")))
                stats_rows.append({"channel": sim_col, "n": int(ok.sum()),
                                   "spearman_rho": rho, "spearman_p": p,
                                   "n_batch1": int((ok & (df["batch"] == 1)).sum()),
                                   "rho_batch1": float("nan"),
                                   "p_batch1": float("nan")})
                ax.set_title(f"{label}\nTier-A vs measured: "
                             f"rho={rho:+.2f} (p={p:.2f}, n={ok.sum()})")
                ax.set_xlabel("measured")
                ax.set_ylabel("Tier-A simulated")
            else:
                ok = np.isfinite(df[sim_col])
                ax.hist(df.loc[ok, sim_col], bins=12, color="tab:green",
                        alpha=0.8)
                ax.set_title(f"{label}\nTier-A distribution (n={ok.sum()})")
                ax.set_xlabel("Tier-A simulated")

            ax2 = axesA[1, j]
            okb = np.isfinite(df[sim_col])
            sub = df[okb]
            order = np.argsort(sub[sim_col].to_numpy())
            vals = sub[sim_col].to_numpy()[order]
            ax2.bar(range(len(vals)), vals,
                    color=["tab:blue" if b == 1 else "tab:orange"
                           for b in sub["batch"].to_numpy()[order]])
            ax2.set_xticks(range(len(vals)))
            ax2.set_xticklabels(sub["print_id"].to_numpy()[order],
                                rotation=90, fontsize=6)
            ax2.set_title(f"Tier-A {sim_col} across articles")
        figA.suptitle("Tier-A (PolyFEM+IPC, viscoelastic PLA+TPU, rigid "
                      "floor at 5.30 m/s): article-intrinsic observables\n"
                      "blue = batch 1, orange = round 2; restitution and "
                      "peak-g have no mat in the loop, so identity lines "
                      "apply to fn/zeta only")
        figA.tight_layout()
        figA.savefig(OUT / "tier_promotion_tierA.png", dpi=130)

    st = pd.DataFrame(stats_rows)
    st.to_csv(OUT / "tier_promotion_stats.csv", index=False)
    print(st.to_string(index=False))
    if tierA is not None:
        print("\nTier-A rows:")
        print(tierA.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
