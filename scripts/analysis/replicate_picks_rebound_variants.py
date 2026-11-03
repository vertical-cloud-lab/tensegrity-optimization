"""Do the replicate-study picks keep their roles if the rebound index is m*e^2?

Question (PR #97, me-madsen, 2026-10-29): does ranking by m*e^2 change the
best, mid and bad specimens picked for validation testing? Those are the
three batch-4 designs of the replicate rank-stability study, accepted by the
lab on 2026-09-28 (PR #102, ``bo/t3-prism-replicate-study-plan.md``):
corny7 (on the front), corny8 (further away) and corny2 (furthest away),
with corny6 and corny5 named there as alternates. The plan spaced them along
t180; the brief on PR #102 (2026-09-23) put them "kind of along the
diagonal".

For each pick and alternate this reports, under m*e (which ranks exactly as
the current objective E_reb) and under m*e^2:

* t180 and its rank, which the form of the index cannot change;
* the index, its rank, the Pareto layer (non-dominated sorting depth) and
  the number of designs that dominate it, over all 35 designs and over
  batch 4 alone (the pool the picks were drawn from);
* the distance to the front with both axes scaled 0 to 1 over the 35
  designs, counting only the directions in which the design is worse than a
  front member (the IGD+ distance). This is how far out a point looks on
  the plot;
* the plan's rebound endpoint (corny8's index over the mean of corny7 and
  corny2) and the corny7 to corny2 ratio, which the plan scores as a tie.

Inputs and conventions are those of ``pareto_rebound_index_variants.py``
(imported from this folder): ``data/bo-campaign-snapshot/``, design means
over the three prints of each batch-3 design, each print's index computed
from its own mass.

Outputs (``docs/figures/``): ``replicate_picks_rebound_variants.csv`` and
``replicate_picks_rebound_variants.png``.

Usage (from the repo root)::

    pip install pandas matplotlib scipy
    python scripts/analysis/replicate_picks_rebound_variants.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pareto_rebound_index_variants import (
    ARROW_DOWN,
    FIG_RC,
    INK,
    LABEL_GRAY,
    OUT_DIR,
    REF_GRAY,
    _style,
    design_means,
    load_articles,
    pareto_layers,
    pareto_mask,
)

OUT_CSV = OUT_DIR / "replicate_picks_rebound_variants.csv"
OUT_PNG = OUT_DIR / "replicate_picks_rebound_variants.png"

# role in the replicate-study plan (PR #102, picks accepted 2026-09-28)
PICKS = {
    "corny7": "on the front",
    "corny8": "further away",
    "corny2": "furthest away",
    "corny6": "alternate for corny7",
    "corny5": "alternate for corny2",
}
# categorical slots 1 to 3 of the dataviz reference palette, validated
# all-pairs in light mode; aqua sits under 3:1 contrast on white, so every
# pick also carries a direct label in ink
PICK_COLORS = {"corny7": "#2a78d6", "corny8": "#eb6834", "corny2": "#1baf7a"}
# label offsets in points; corny7's sits above the front's first step
PICK_LABEL_OFFSET = {"corny7": (12, 14), "corny8": (14, 0), "corny2": (14, 0)}
FORMS = {"me_g": "m·e", "me2_mg": "m·e²"}
DOT_GRAY = "#c9c8c3"


def dominated_by(xs, ys) -> np.ndarray:
    """How many points dominate each point (both objectives minimized)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    return np.array([
        int(np.sum((xs <= x) & (ys <= y) & ((xs < x) | (ys < y))))
        for x, y in zip(xs, ys)
    ])


def front_distance(xs, ys) -> np.ndarray:
    """IGD+ distance to the front with both axes scaled 0 to 1: for each
    point, the smallest over front members of the length of the part of
    (point - member) that is positive. 0 on the front."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    u = (xs - xs.min()) / (xs.max() - xs.min())
    v = (ys - ys.min()) / (ys.max() - ys.min())
    on = pareto_mask(xs, ys)
    fu, fv = u[on], v[on]
    return np.array([
        np.min(np.hypot(np.maximum(0.0, a - fu), np.maximum(0.0, b - fv)))
        for a, b in zip(u, v)
    ])


def standing(d: pd.DataFrame, suffix: str) -> pd.DataFrame:
    """Ranks, layers, dominator counts and front distance under both forms."""
    out = pd.DataFrame({"design": d["design"]})
    out[f"rank_t180{suffix}"] = d["t180"].rank(method="min").astype(int)
    for col, tag in (("me_g", "me"), ("me2_mg", "me2")):
        out[f"rank_{tag}{suffix}"] = d[col].rank(method="min").astype(int)
        out[f"layer_{tag}{suffix}"] = pareto_layers(d["t180"], d[col])
        out[f"dominated_by_{tag}{suffix}"] = dominated_by(d["t180"], d[col])
        if not suffix:
            out[f"front_dist_{tag}"] = front_distance(d["t180"], d[col])
    return out


def render(d: pd.DataFrame) -> None:
    """All 35 designs in gray, the front as a staircase, the three picks in
    color with their Pareto layer; m*e on the left, m*e^2 on the right."""
    xlim, xticks = (0.78, 1.35), np.arange(0.8, 1.31, 0.1)
    panels = [
        ("me_g", "layer_me", "m·e (g)", (-0.03, 1.3),
         np.arange(0.0, 1.21, 0.4), "Current index, m·e"),
        ("me2_mg", "layer_me2", "m·e² (mg)", (-2.5, 80.0),
         np.arange(0, 81, 20), "Squared, m·e²"),
    ]
    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, 2, figsize=(15.0, 6.8), dpi=300)
        for ax, (col, lcol, ylabel, ylim, yticks, title) in zip(axes, panels):
            ax.scatter(d["t180"], d[col], s=46, fc=DOT_GRAY, ec="none",
                       zorder=2)
            # the front as the edge of the region it dominates: up from its
            # first member, down the steps, and out from its last member
            front = d[pareto_mask(d["t180"], d[col])].sort_values("t180")
            fx = np.r_[front["t180"].iloc[0], front["t180"], xlim[1]]
            fy = np.r_[ylim[1], front[col], front[col].iloc[-1]]
            ax.step(fx, fy, where="post", color=REF_GRAY, lw=2.0, zorder=1)
            for key, color in PICK_COLORS.items():
                r = d[d["design"] == key].iloc[0]
                ax.scatter(r["t180"], r[col], s=190, fc=color, ec="white",
                           lw=2.0, zorder=4)
                ax.annotate(f"{key}, layer {r[lcol]}", xy=(r["t180"], r[col]),
                            xytext=PICK_LABEL_OFFSET[key],
                            textcoords="offset points", color=INK, ha="left",
                            va="center", fontsize=16, zorder=5)
            _style(ax, xlim, ylim, xticks, yticks,
                   f"{ylabel}, {ARROW_DOWN} is better")
            ax.text(1.0, 1.03, title, transform=ax.transAxes, ha="right",
                    va="bottom", fontsize=18, fontweight="semibold")
        fig.text(
            0.5, -0.07,
            "Gray: all 35 designs (53 tested specimens; batch-3 designs at the "
            "mean of their three prints). Line: the Pareto front.\n"
            "Layer 1 is the front, layer 2 is the front once layer 1 is "
            "removed, and so on.",
            ha="center", va="top", fontsize=13, color=LABEL_GRAY,
            linespacing=1.4,
        )
        fig.subplots_adjust(wspace=0.30)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def main() -> int:
    d = design_means(load_articles())
    d = d.merge(standing(d, ""), on="design")
    b4 = standing(d[d["batch"] == 4].reset_index(drop=True), "_batch4")
    d = d.merge(b4, on="design", how="left")
    d[b4.columns[1:]] = d[b4.columns[1:]].astype("Int64")  # NaN off batch 4

    rows = d[d["design"].isin(PICKS)].copy()
    rows["role"] = rows["design"].map(PICKS)
    rows["order"] = rows["design"].map({k: i for i, k in enumerate(PICKS)})
    rows = rows.sort_values("order").drop(columns="order")
    cols = (
        ["design", "role", "m_g", "e", "t180", "rank_t180", "rank_t180_batch4"]
        + [f"{c}_{t}{s}" for t in ("me", "me2") for s in ("", "_batch4")
           for c in ("rank", "layer", "dominated_by")]
        + ["front_dist_me", "front_dist_me2", "me_g", "me2_mg", "E_reb_mJ"]
    )
    rows = rows[cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows.round(5).to_csv(OUT_CSV, index=False)

    print(f"{len(d)} designs, {len(b4)} in batch 4\n")
    for _, r in rows.iterrows():
        print(f"{r['design']} ({r['role']}): t180 {r['t180']:.3f}, "
              f"rank {r['rank_t180']} of {len(d)} ({r['rank_t180_batch4']} "
              f"of {len(b4)} in batch 4)")
        for tag, name in (("me", "m·e "), ("me2", "m·e²")):
            print(f"  {name}: index rank {r[f'rank_{tag}']:>2}, layer "
                  f"{r[f'layer_{tag}']}, dominated by "
                  f"{r[f'dominated_by_{tag}']:>2}; batch 4: rank "
                  f"{r[f'rank_{tag}_batch4']}, layer "
                  f"{r[f'layer_{tag}_batch4']}, dominated by "
                  f"{r[f'dominated_by_{tag}_batch4']}; front distance "
                  f"{r[f'front_dist_{tag}']:.3f}")

    same_b4 = all(
        (b4[f"{c}_me_batch4"] == b4[f"{c}_me2_batch4"]).all()
        for c in ("rank", "layer", "dominated_by")
    )
    print(f"\nBatch 4 ranks, layers and dominator counts identical under "
          f"both forms: {same_b4}")

    p = d.set_index("design")
    for col, name in FORMS.items():
        c7, c8, c2 = (p.loc[k, col] for k in ("corny7", "corny8", "corny2"))
        print(f"{name}: corny8 / mean(corny7, corny2) = {c8 / ((c7 + c2) / 2):.2f}"
              f", corny7 / corny2 = {c7 / c2:.3f}")
    for col in FORMS:
        doms = {}
        for key in ("corny8", "corny2"):
            r = p.loc[key]
            mask = ((p["t180"] <= r["t180"]) & (p[col] <= r[col])
                    & ((p["t180"] < r["t180"]) | (p[col] < r[col])))
            doms[key] = sorted(p.index[mask])
        print(f"{FORMS[col]} dominators: corny8 {doms['corny8']}; "
              f"corny2 {len(doms['corny2'])}")

    render(d)
    print(f"\nWrote {OUT_CSV.relative_to(OUT_DIR.parents[1])} and "
          f"{OUT_PNG.relative_to(OUT_DIR.parents[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
