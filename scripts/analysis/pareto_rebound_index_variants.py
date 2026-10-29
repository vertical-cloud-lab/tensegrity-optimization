"""Pareto fronts with the mass-weighted rebound index as m*e and as m*e^2.

Question (PR #97, me-madsen, 2026-10-23): how do the tested specimens sit
on the Pareto front if the mass-weighted index is computed as m*e, and again
as m*e^2, where e is the usual rebound coefficient
e = g * t_second / (2 * dv)? Compare both against the current front.

The current BO objective (PR #102, ``bo/t3_prism_bo_campaign.py``) is
E_reb = e * m * g * h in mJ per drop, both objectives minimized. m*e is that
objective divided by the constant g*h = 14.95 m^2/s^2, so its front is the
current front by construction. m*e^2 is the one that can differ.

Inputs (``data/bo-campaign-snapshot/``, verbatim copies, see its README):
the five campaign summaries the BO fits on (PR #102 at 65ff978) and the third
print of the batch-3 designs (dran31-39, PR #86 at 64e468e), 53 articles in
all. ``amdjwm`` has no weighed mass and is skipped, as in the BO script.

Conventions follow PR #102 and the manuscript (PR #76):

* t180 and e are each article's stabilized session means.
* m is the article's own weighed mass in grams.
* Design-level points: the batch-3 designs (trials 28 to 36) were printed
  three times (drranN, 2dranN, dran3N). Each print's index is computed with
  its own mass, then the design plots at the mean of its prints, the same
  way ``aggregate_repeats`` treats E_reb. Every other article is its own
  design.
* SEM, as in the BO loaders: e_sem = e_sd / sqrt(n_valid), folded in
  quadrature with the 0.457 g print-to-print mass scatter. For m*e^2 the
  relative e term doubles.

Robustness checks printed to stdout: every article as its own point, first
prints only, and batch-3 design means over health-screened sessions only
(seat gauge t1000/t180 < 1.145 and no drift flag). A Monte Carlo pass
redraws every design with the print-to-print scatter measured from the
batch-3 triplicates and reports how often each design lands on the front.
Ranking changes (PR #97 follow-up): every design's and article's rank on
the index alone and its Pareto layer (non-dominated sorting depth) under
both forms, printed and written to the CSVs, with a slope chart of the
design ranks. Every pair of designs, and of articles, that the two forms
put in opposite order is listed with its cause and batches, and the ranks
are compared against e alone (no mass weight, the manuscript's VLI) for
scale.

Outputs (``docs/figures/``): ``pareto_rebound_index_variants.png`` (all
designs, both fronts), ``..._knee.png`` (zoom where the fronts differ),
``..._ranks.png`` (rank under m*e against rank under m*e^2),
``..._swap_zone.png`` (every pair of articles, and the band where the two
forms disagree), the per-article and per-design CSVs, and ``..._swaps.csv``
(every pair that swaps order).

Usage (from the repo root)::

    pip install pandas matplotlib scipy
    python scripts/analysis/pareto_rebound_index_variants.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data" / "bo-campaign-snapshot"
OUT_DIR = REPO / "docs" / "figures"
OUT_PNG = OUT_DIR / "pareto_rebound_index_variants.png"
OUT_KNEE = OUT_DIR / "pareto_rebound_index_variants_knee.png"
OUT_RANKS = OUT_DIR / "pareto_rebound_index_variants_ranks.png"
OUT_ZONE = OUT_DIR / "pareto_rebound_index_variants_swap_zone.png"
OUT_ARTICLES = OUT_DIR / "pareto_rebound_index_variants_articles.csv"
OUT_DESIGNS = OUT_DIR / "pareto_rebound_index_variants_designs.csv"
OUT_SWAPS = OUT_DIR / "pareto_rebound_index_variants_swaps.csv"

G = 9.80665          # m/s^2, as in the BO script
H = 1.524            # m, 60 in drop
MASS_SD_G = 0.457    # print-to-print mass sd, spec-08 triplicate (BO script)
GAUGE_MAX = 1.145    # seat-gauge screen used by the three-print analysis

# (file stem, physical batch, print number within the batch)
SOURCES = [
    ("t3-prism-bo-batch-drop-results", 1, 1),
    ("t3-prism-bo-round1-drop-results", 2, 1),
    ("t3-prism-bo-round3-drop-results", 3, 1),
    ("t3-prism-bo-round3-reprint-drop-results", 3, 2),
    ("t3-prism-bo-round3-third-print-drop-results", 3, 3),
    ("t3-prism-bo-round4-drop-results", 4, 1),
]

# reprints of a batch-3 design share the first print's label (2dranN and
# dran3N are drranN's design), the same keys as REPRINT_PREFIX in PR #102
REPRINT_PREFIX = {"2dran": "drran", "dran3": "drran"}

# Monte Carlo noise, per print: pooled within-design sd over the screened
# batch-3 triplicates (21 sessions, 12 dof), computed below and rounded
MC_DRAWS = 20000
MC_SEED = 0

# figure styling, matching the PR #102 Pareto panels
INK = "#0b0b0b"
FRONT_BLUE = "#2a78d6"
REF_GRAY = "#8d8c88"     # the current front, drawn for reference in panel B
LABEL_GRAY = "#83827d"
FIG_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Source Sans Pro", "Source Sans 3", "Open Sans", "Lato",
        "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans",
    ],
    "font.size": 17,
    "axes.labelsize": 18,
    "axes.labelcolor": INK,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.edgecolor": "#4a4a47",
    "axes.linewidth": 1.4,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.major.width": 1.4,
    "ytick.major.width": 1.4,
}
ARROW_DOWN = "↓"


def design_of(specimen: str) -> str:
    for prefix, base in REPRINT_PREFIX.items():
        if specimen.startswith(prefix):
            return base + specimen[len(prefix):]
    return specimen


def load_articles() -> pd.DataFrame:
    frames = []
    for stem, batch, print_no in SOURCES:
        d = pd.read_csv(DATA / f"{stem}.csv")
        d["batch"], d["print_no"], d["source"] = batch, print_no, stem
        frames.append(d)
    a = pd.concat(frames, ignore_index=True)
    skipped = a.loc[a["mass_g"].isna(), "specimen"].tolist()
    if skipped:
        print(f"Skipped (no weighed mass): {', '.join(skipped)}")
    a = a[a["mass_g"].notna()].copy()

    n = a["n_valid"].astype(float)
    a["design"] = a["specimen"].map(design_of)
    a["m_g"] = a["mass_g"].astype(float)
    a["e"] = a["e_rebound_mean"].astype(float)
    a["e_sem"] = a["e_rebound_sd"].astype(float) / np.sqrt(n)
    a["t180"] = a["t180_mean"].astype(float)
    a["t180_sem"] = a["t180_sd"].astype(float) / np.sqrt(n)
    a["E_reb_mJ"] = a["e"] * a["m_g"] * G * H
    a["me_g"] = a["m_g"] * a["e"]
    a["me2_mg"] = a["m_g"] * a["e"] ** 2 * 1000.0
    rel_m = MASS_SD_G / a["m_g"]
    a["me_sem_g"] = a["me_g"] * np.hypot(a["e_sem"] / a["e"], rel_m)
    a["me2_sem_mg"] = a["me2_mg"] * np.hypot(2 * a["e_sem"] / a["e"], rel_m)
    a["gauge"] = a["t1000_mean"] / a["t180_mean"]
    a["drift"] = a["t_drift_flag"].astype(str).eq("True")
    a["screened"] = ~((a["batch"] == 3) & ((a["gauge"] >= GAUGE_MAX) | a["drift"]))
    return a


def pareto_mask(xs, ys) -> np.ndarray:
    """Non-dominated mask, both objectives minimized (as in PR #102)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    return np.array([
        not np.any((xs <= x) & (ys <= y) & ((xs < x) | (ys < y)))
        for x, y in zip(xs, ys)
    ])


def pareto_layers(xs, ys) -> np.ndarray:
    """Non-dominated sorting depth: 1 = the front, 2 = the front once layer 1
    is removed, and so on (both objectives minimized)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    layer = np.zeros(len(xs), dtype=int)
    left = np.ones(len(xs), dtype=bool)
    k = 0
    while left.any():
        k += 1
        idx = np.flatnonzero(left)
        on = pareto_mask(xs[idx], ys[idx])
        layer[idx[on]] = k
        left[idx[on]] = False
    return layer


def add_ranks(frame: pd.DataFrame) -> pd.DataFrame:
    """Index rank (1 = lowest index) and Pareto layer under both forms."""
    frame = frame.copy()
    for col, tag in (("me_g", "me"), ("me2_mg", "me2")):
        frame[f"rank_{tag}"] = frame[col].rank(method="min").astype(int)
        frame[f"layer_{tag}"] = pareto_layers(frame["t180"], frame[col])
    frame["rank_shift"] = frame["rank_me2"] - frame["rank_me"]
    frame["layer_shift"] = frame["layer_me2"] - frame["layer_me"]
    return frame


def print_rank_changes(frame: pd.DataFrame, key: str, what: str) -> None:
    moved = frame[(frame["rank_shift"] != 0) | (frame["layer_shift"] != 0)]
    print(f"\n{what}: {int((frame['rank_shift'] != 0).sum())} of {len(frame)} "
          f"change index rank (largest shift {int(frame['rank_shift'].abs().max())} "
          f"places); {int((frame['layer_shift'] != 0).sum())} change Pareto layer")
    for _, r in moved.sort_values("rank_me").iterrows():
        print(f"  {r[key]:8s} m {r['m_g']:6.2f} g  e {r['e']:.4f}  "
              f"rank {r['rank_me']:2d} -> {r['rank_me2']:2d}  "
              f"layer {r['layer_me']} -> {r['layer_me2']}")


def swapped_pairs(frame: pd.DataFrame, key: str, level: str) -> pd.DataFrame:
    """Every pair that m*e and m*e^2 put in opposite order.

    ``a`` is the member m*e ranks better (lower), ``b`` the one m*e^2 ranks
    better. Two single prints swap exactly when the lighter one is bouncier
    by a factor between sqrt(mass ratio) and the mass ratio. A design mean
    can also swap because averaging m*e^2 over prints that bounce
    differently weights the bounciest print more than averaging m*e does.
    ``cause`` is "mass against bounce" if the pair still swaps with each
    design scored at its mean mass and mean e, else "print averaging".
    """
    f = frame.reset_index(drop=True)
    rows = []
    for i in range(len(f)):
        for j in range(i + 1, len(f)):
            p, q = f.iloc[i], f.iloc[j]
            if np.sign(p["me_g"] - q["me_g"]) == np.sign(p["me2_mg"] - q["me2_mg"]):
                continue
            a, b = (p, q) if p["me_g"] < q["me_g"] else (q, p)
            plain = (np.sign(a["m_g"] * a["e"] - b["m_g"] * b["e"])
                     != np.sign(a["m_g"] * a["e"] ** 2 - b["m_g"] * b["e"] ** 2))
            rows.append({
                "level": level, "a": a[key], "b": b[key],
                "batch_a": a["batch"], "batch_b": b["batch"],
                "m_a_g": a["m_g"], "m_b_g": b["m_g"], "e_a": a["e"], "e_b": b["e"],
                "me_a_g": a["me_g"], "me_b_g": b["me_g"],
                "me2_a_mg": a["me2_mg"], "me2_b_mg": b["me2_mg"],
                # how far the loser sits above the winner under each form
                "gap_me_pct": 100 * (b["me_g"] / a["me_g"] - 1),
                "gap_me2_pct": 100 * (a["me2_mg"] / b["me2_mg"] - 1),
                "cause": "mass against bounce" if plain else "print averaging",
            })
    return pd.DataFrame(rows).sort_values("me_a_g", ignore_index=True)


def print_swaps(sw: pd.DataFrame, frame: pd.DataFrame, what: str) -> None:
    n = len(frame)
    same = sw["batch_a"] == sw["batch_b"]
    print(f"\n{what}: {len(sw)} of {n * (n - 1) // 2} pairs swap order, "
          f"{int(same.sum())} within a batch and {int((~same).sum())} across "
          f"batches; {sw['cause'].value_counts().to_dict()}")
    for b, grp in frame.groupby("batch"):
        k = int(((sw["batch_a"] == b) & (sw["batch_b"] == b)).sum())
        print(f"  batch {b}: {k} of {len(grp) * (len(grp) - 1) // 2} "
              f"within-batch pairs swap")
    for _, r in sw.sort_values("me_a_g").iterrows():
        print(f"  {r['a']:8s} ({r['m_a_g']:5.2f} g, e {r['e_a']:.4f}) lower m*e by "
              f"{r['gap_me_pct']:4.1f}%;  {r['b']:8s} ({r['m_b_g']:5.2f} g, "
              f"e {r['e_b']:.4f}) lower m*e^2 by {r['gap_me2_pct']:4.1f}%  "
              f"[{r['cause']}]")


def design_means(a: pd.DataFrame) -> pd.DataFrame:
    g = a.groupby("design", sort=False)
    d = g.agg(
        batch=("batch", "first"),
        n_prints=("specimen", "size"),
        prints=("specimen", lambda s: " ".join(s)),
        m_g=("m_g", "mean"),
        e=("e", "mean"),
        t180=("t180", "mean"),
        E_reb_mJ=("E_reb_mJ", "mean"),
        me_g=("me_g", "mean"),
        me2_mg=("me2_mg", "mean"),
    ).reset_index()
    d["label"] = [
        f"{k} x{n}" if n > 1 else k for k, n in zip(d["design"], d["n_prints"])
    ]
    return d


def fronts(frame: pd.DataFrame, key: str) -> dict[str, list[str]]:
    out = {}
    for col in ("E_reb_mJ", "me_g", "me2_mg", "e"):
        mask = pareto_mask(frame["t180"], frame[col])
        out[col] = frame[mask].sort_values("t180")[key].tolist()
    return out


def pooled_print_sd(a: pd.DataFrame) -> tuple[float, float, int]:
    """Within-design sd of t180 and ln(e) over the screened batch-3 prints."""
    b3 = a[(a["batch"] == 3) & a["screened"]]
    ss_t = ss_e = 0.0
    dof = 0
    for _, grp in b3.groupby("design"):
        if len(grp) < 2:
            continue
        ss_t += float(((grp["t180"] - grp["t180"].mean()) ** 2).sum())
        lne = np.log(grp["e"])
        ss_e += float(((lne - lne.mean()) ** 2).sum())
        dof += len(grp) - 1
    return np.sqrt(ss_t / dof), np.sqrt(ss_e / dof), dof


def front_probability(d: pd.DataFrame, sd_t: float, sd_lne: float,
                      power: int) -> np.ndarray:
    """Share of redraws in which each design is non-dominated.

    Every design is redrawn as if reprinted: t180, ln(e) and mass get the
    per-print scatter, divided by sqrt(prints) for the triplicated designs.
    """
    rng = np.random.default_rng(MC_SEED)
    k = d["n_prints"].to_numpy(float)
    shape = (MC_DRAWS, len(d))
    t = d["t180"].to_numpy() + rng.standard_normal(shape) * sd_t / np.sqrt(k)
    e = np.exp(np.log(d["e"].to_numpy())
               + rng.standard_normal(shape) * sd_lne / np.sqrt(k))
    m = d["m_g"].to_numpy() + rng.standard_normal(shape) * MASS_SD_G / np.sqrt(k)
    y = m * e ** power
    # 2-D front per draw: sort by t180, keep points below the running minimum
    order = np.argsort(t, axis=1)
    ys = np.take_along_axis(y, order, axis=1)
    run_min = np.minimum.accumulate(ys, axis=1)
    prev = np.concatenate([np.full((MC_DRAWS, 1), np.inf), run_min[:, :-1]], axis=1)
    on = np.zeros(shape, dtype=bool)
    np.put_along_axis(on, order, ys < prev, axis=1)
    return on.mean(axis=0)


def _style(ax, xlim, ylim, xticks, yticks, ylabel, xfmt="{:.1f}"):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(xticks)
    ax.set_xticklabels([xfmt.format(v) for v in xticks])
    ax.set_yticks(yticks)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_position(("outward", 10))
    ax.spines["bottom"].set_bounds(xticks[0], xticks[-1])
    ax.spines["left"].set_bounds(yticks[0], yticks[-1])
    ax.set_xlabel(f"Transmissibility t180 ({ARROW_DOWN} is better)", labelpad=8)
    ax.set_ylabel(ylabel, rotation=0, ha="left", va="bottom")
    ax.yaxis.set_label_coords(-0.07, 1.03)


def _label(ax, text, xy, offset, color=INK, ha="left", leader=False, size=15):
    """Point label in points relative to the marker, optional thin leader."""
    arrow = (dict(arrowstyle="-", color=LABEL_GRAY, lw=1.0, shrinkA=2, shrinkB=7)
             if leader else None)
    ax.annotate(text, xy=xy, xytext=offset, textcoords="offset points",
                color=color, ha=ha, va="center", fontsize=size, zorder=6,
                arrowprops=arrow)


def _points(ax, d, col, on, gray=()):
    """Open circles for everything, filled blue for the front, gray rings."""
    is_gray = d["design"].isin(gray).to_numpy()
    plain = ~on & ~is_gray
    ax.scatter(d.loc[plain, "t180"], d.loc[plain, col], s=90, fc="none",
               ec=INK, lw=1.6, zorder=3)
    ax.scatter(d.loc[is_gray, "t180"], d.loc[is_gray, col], s=120, fc="white",
               ec=REF_GRAY, lw=2.6, zorder=4)
    front = d[on].sort_values("t180")
    ax.plot(front["t180"], front[col], color=FRONT_BLUE, lw=2.8, zorder=2)
    ax.scatter(front["t180"], front[col], s=120, fc=FRONT_BLUE, ec=INK,
               lw=1.8, zorder=5)
    return front


# label offsets in points, per panel column, for the overview figure;
# corny4 and r2d2c6 nearly coincide at this scale and share one label
OVERVIEW_LABELS = {
    "me_g": {
        "corny7": ((10, 10), False), "corny6": ((-10, -18), False),
        "r2d2c2": ((-30, -40), True), "corny4": ((14, -26), True),
    },
    "me2_mg": {
        "corny7": ((10, 10), False), "corny6": ((-10, -22), False),
        "r2d2c2": ((-50, 88), True), "corny4": ((14, -18), True),
    },
}


def _legend(fig, with_line=False):
    """One legend above both panels (the same symbols in each)."""
    from matplotlib.lines import Line2D
    handles = [
        Line2D([], [], color=FRONT_BLUE, lw=2.8, marker="o", ms=10,
               mfc=FRONT_BLUE, mec=INK, mew=1.6),
        Line2D([], [], ls="none", marker="o", ms=9, mfc="none", mec=INK, mew=1.6),
        Line2D([], [], ls="none", marker="o", ms=10, mfc="white", mec=REF_GRAY,
               mew=2.4),
    ]
    labels = ["Pareto front", "Other designs",
              "On the current front, not on the m·e² front"]
    if with_line:
        handles.append(Line2D([], [], color=REF_GRAY, lw=2.0))
        labels.append("Current front's members, joined")
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0),
               ncol=len(handles), frameon=False, fontsize=15,
               handlelength=2.2, columnspacing=1.8)


def render_overview(d: pd.DataFrame) -> None:
    """All 35 designs: the m*e panel (current front) next to the m*e^2 panel."""
    current = d.loc[d["front_E_reb_mJ"], "design"].tolist()
    xlim, xticks = (0.78, 1.35), np.arange(0.8, 1.31, 0.1)
    panels = [
        ("me_g", "front_me_g", "m·e (g)", (-0.03, 1.3),
         np.arange(0.0, 1.21, 0.4), "Current index, m·e"),
        ("me2_mg", "front_me2_mg", "m·e² (mg)", (-2.5, 80.0),
         np.arange(0, 81, 20), "Squared, m·e²"),
    ]
    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, 2, figsize=(15.0, 6.8), dpi=300)
        for ax, (col, fcol, ylabel, ylim, yticks, title) in zip(axes, panels):
            on = d[fcol].to_numpy()
            gray = [k for k in current if k not in set(d.loc[on, "design"])]
            front = _points(ax, d, col, on, gray=gray)
            for _, r in d[on | d["design"].isin(gray)].iterrows():
                if r["design"] == "r2d2c6":
                    continue  # labeled together with corny4
                (dx, dy), leader = OVERVIEW_LABELS[col][r["design"]]
                text = "corny4 and r2d2c6" if r["design"] == "corny4" else r["label"]
                xy = (r["t180"], r[col])
                if r["design"] == "corny4":
                    pair = d[d["design"].isin(["corny4", "r2d2c6"])]
                    xy = (pair["t180"].mean(), pair[col].mean())
                _label(ax, text, xy, (dx, dy),
                       color=REF_GRAY if r["design"] in gray else INK,
                       ha="right" if dx < 0 else "left", leader=leader)
            _style(ax, xlim, ylim, xticks, yticks,
                   f"{ylabel}, {ARROW_DOWN} is better")
            ax.text(1.0, 1.03, title, transform=ax.transAxes, ha="right",
                    va="bottom", fontsize=18, fontweight="semibold")
        fig.text(
            0.5, -0.07,
            "35 designs from 53 tested articles. The nine batch-3 designs were "
            "printed three times and plot at the mean of their prints.\n"
            "m·e is the current objective divided by the constant g·h, so the "
            "left panel is the current front.",
            ha="center", va="top", fontsize=13, color=LABEL_GRAY,
            linespacing=1.4,
        )
        _legend(fig)
        fig.subplots_adjust(wspace=0.30)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def render_knee(d: pd.DataFrame) -> None:
    """Zoom on the knee: why r2d2c2 is on one front and not the other."""
    current = d.loc[d["front_E_reb_mJ"], "design"].tolist()
    c6 = d.set_index("design").loc["corny6"]
    c2 = d.set_index("design").loc["r2d2c2"]
    xlim, xticks = (0.885, 1.075), np.arange(0.90, 1.051, 0.05)
    panels = [
        ("me_g", "front_me_g", "m·e (g)", (0.255, 0.48),
         np.arange(0.26, 0.461, 0.04), "Current index, m·e", "{:.2f}"),
        ("me2_mg", "front_me2_mg", "m·e² (mg)", (3.2, 12.0),
         np.arange(4.0, 12.01, 2.0), "Squared, m·e²", "{:.0f}"),
    ]
    labels = {
        "me_g": {"corny6": ((-10, -16), False), "r2d2c2": ((10, -14), False),
                 "corny4": ((12, 6), False), "r2d2c6": ((12, -6), False),
                 "r2d2c1": ((-8, 14), False)},
        "me2_mg": {"corny6": ((-10, -16), False), "r2d2c2": ((10, -12), False),
                   "corny4": ((12, 6), False), "r2d2c6": ((12, -6), False),
                   "r2d2c1": ((-8, 16), False)},
    }
    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, 2, figsize=(15.0, 6.8), dpi=300)
        for ax, (col, fcol, ylabel, ylim, yticks, title, yfmt) in zip(axes, panels):
            on = d[fcol].to_numpy()
            gray = [k for k in current if k not in set(d.loc[on, "design"])]
            # everything up and to the right of corny6 is dominated by it
            ax.add_patch(plt.Rectangle(
                (c6["t180"], c6[col]), xlim[1] - c6["t180"], ylim[1] - c6[col],
                fc="#efeeec", ec="none", zorder=0))
            ax.text(c6["t180"] + 0.004, ylim[1] - 0.03 * (ylim[1] - ylim[0]),
                    "Dominated by corny6\n(higher t180 and higher index)",
                    ha="left", va="top", fontsize=13, color=LABEL_GRAY)
            if gray:
                ref = d[d["design"].isin(current)].sort_values("t180")
                ax.plot(ref["t180"], ref[col], color=REF_GRAY, lw=2.0, zorder=1.5)
            _points(ax, d, col, on, gray=gray)
            for key, ((dx, dy), leader) in labels[col].items():
                r = d.set_index("design").loc[key]
                is_gray = key in gray
                _label(ax, key, (r["t180"], r[col]), (dx, dy),
                       color=REF_GRAY if is_gray else INK,
                       ha="right" if dx < 0 else "left", leader=leader)
            ratio = c2[col] / c6[col] - 1
            note = (f"r2d2c2 sits {abs(ratio):.1%} below corny6,\nso it stays on the front"
                    if ratio < 0 else
                    f"r2d2c2 sits {ratio:.1%} above corny6,\nso corny6 dominates it")
            ax.annotate(note, xy=(c2["t180"], c2[col]),
                        xytext=(0.08, 0.20 if ratio < 0 else 0.16),
                        textcoords="axes fraction", ha="left", va="center",
                        fontsize=14, color=INK,
                        arrowprops=dict(arrowstyle="-", color=LABEL_GRAY, lw=1.0,
                                        shrinkA=4, shrinkB=8))
            _style(ax, xlim, ylim, xticks, yticks,
                   f"{ylabel}, {ARROW_DOWN} is better", xfmt="{:.2f}")
            ax.set_yticklabels([yfmt.format(v) for v in yticks])
            ax.text(1.0, 1.03, title, transform=ax.transAxes, ha="right",
                    va="bottom", fontsize=18, fontweight="semibold")
        fig.text(
            0.5, -0.07,
            "Zoom on the low-rebound end of both fronts. r2d2c2 (17.96 g) is "
            "lighter than corny6 (19.45 g), but its e is higher.\n"
            "With m·e the mass advantage wins; with m·e² e counts twice and "
            "corny6 wins. The shaded box is everything corny6 dominates.",
            ha="center", va="top", fontsize=13, color=LABEL_GRAY,
            linespacing=1.4,
        )
        _legend(fig, with_line=True)
        fig.subplots_adjust(wspace=0.30)
        fig.savefig(OUT_KNEE, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def render_ranks(d: pd.DataFrame) -> None:
    """Slope chart: each design's index rank under m*e (left) and m*e^2 (right)."""
    d = d.sort_values("rank_me")
    n = len(d)
    light, mid = "#cfcecb", REF_GRAY
    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(8.0, 11.5), dpi=300)
        for _, r in d.iterrows():
            shift = abs(int(r["rank_shift"]))
            color = light if shift == 0 else (mid if shift == 1 else INK)
            lw = 1.4 if shift == 0 else (1.8 if shift == 1 else 2.6)
            y0, y1 = r["rank_me"], r["rank_me2"]
            ax.plot([0, 1], [y0, y1], color=color, lw=lw, zorder=2 + shift)
            for x, y, on in ((0, y0, r["front_me_g"]), (1, y1, r["front_me2_mg"])):
                ax.scatter([x], [y], s=60, zorder=6,
                           fc=FRONT_BLUE if on else "white",
                           ec=INK if on else color, lw=1.4)
            text_color = LABEL_GRAY if shift == 0 else INK
            weight = "semibold" if shift >= 2 else "normal"
            ax.text(-0.05, y0, r["label"], ha="right", va="center", fontsize=12,
                    color=text_color, fontweight=weight)
            ax.text(1.05, y1, r["label"], ha="left", va="center", fontsize=12,
                    color=text_color, fontweight=weight)
        # rows sit at their rank on both sides, so one rank column serves both
        for k in range(1, n + 1):
            ax.text(-0.50, k, str(k), ha="right", va="center", fontsize=11,
                    color=LABEL_GRAY)
        ax.text(-0.50, 0.0, "rank", ha="right", va="bottom", fontsize=12,
                color=LABEL_GRAY)
        ax.set_xlim(-0.58, 1.55)
        ax.set_ylim(n + 0.8, 0.2)
        ax.axis("off")
        ax.text(0, 0.0, "m·e", ha="center", va="bottom", fontsize=17,
                fontweight="semibold")
        ax.text(1, 0.0, "m·e²", ha="center", va="bottom", fontsize=17,
                fontweight="semibold")
        n_moved = int((d["rank_shift"] != 0).sum())
        n_big = int((d["rank_shift"].abs() >= 2).sum())
        fig.text(
            0.5, 0.06,
            f"Rank by the rebound index alone, 1 = lowest. {n_moved} of {n} "
            f"designs move, {n_big} by 2 or 3 places (dark lines).\n"
            "Filled blue: on that version's Pareto front against t180.",
            ha="center", va="top", fontsize=12, color=LABEL_GRAY,
            linespacing=1.4,
        )
        fig.savefig(OUT_RANKS, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def render_swap_zone(a: pd.DataFrame, n_swaps: int) -> None:
    """Every pair of articles: mass ratio against e ratio, with the band in
    which m*e and m*e^2 disagree on which print of the pair is better."""
    m, e = a["m_g"].to_numpy(), a["e"].to_numpy()
    names = a["specimen"].to_numpy()
    i, j = np.triu_indices(len(a), k=1)
    n_equal = int((m[i] == m[j]).sum())   # equal masses: same order under both
    i, j = i[m[i] != m[j]], j[m[i] != m[j]]
    light, heavy = np.where(m[i] < m[j], i, j), np.where(m[i] < m[j], j, i)
    x, y = m[heavy] / m[light], e[light] / e[heavy]
    flip = (y > np.sqrt(x)) & (y < x)
    assert flip.sum() == n_swaps, "band must hold exactly the swapped pairs"
    # the pair whose swap takes r2d2c2 off the design-mean front
    named = frozenset(("r2d2c2", "corny6"))
    backing = dict(fc="white", ec="none", alpha=0.85, pad=2.0)
    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(10.0, 7.4), dpi=300)
        xx = np.linspace(1.0, 1.32, 200)
        ax.fill_between(xx, np.sqrt(xx), xx, color=FRONT_BLUE, alpha=0.14, lw=0,
                        zorder=1)
        for edge in (np.sqrt(xx), xx):
            ax.plot(xx, edge, color=FRONT_BLUE, lw=1.4, zorder=2)
        ax.scatter(x[~flip], y[~flip], s=16, fc=REF_GRAY, ec="none", alpha=0.45,
                   zorder=3)
        ax.scatter(x[flip], y[flip], s=80, fc=FRONT_BLUE, ec="white", lw=1.6,
                   zorder=5)
        for k in np.flatnonzero(flip):
            if frozenset((names[light[k]], names[heavy[k]])) == named:
                ax.annotate("r2d2c2 and corny6", xy=(x[k], y[k]),
                            xytext=(-14, 46), textcoords="offset points",
                            ha="right", va="center", fontsize=14, color=INK,
                            zorder=6, bbox=backing,
                            arrowprops=dict(arrowstyle="-", color=LABEL_GRAY,
                                            lw=1.0, shrinkA=2, shrinkB=7))
        ax.annotate("Inside the band the order flips:\nm·e ranks the lighter "
                    "print better,\nm·e² ranks the heavier one better",
                    xy=(1.285, 1.207), xytext=(1.205, 1.78), ha="left",
                    va="center", fontsize=14, color=INK, zorder=6, bbox=backing,
                    arrowprops=dict(arrowstyle="-", color=LABEL_GRAY, lw=1.0,
                                    shrinkA=4, shrinkB=4))
        ax.text(1.205, 3.7, "Above the band, the heavier print\nranks better "
                "under both", ha="left", va="center", fontsize=14,
                color=LABEL_GRAY, zorder=6, bbox=backing)
        ax.text(1.205, 0.30, "Below the band, the lighter print\nranks better "
                "under both", ha="left", va="center", fontsize=14,
                color=LABEL_GRAY, zorder=6, bbox=backing)
        ax.set_yscale("log")
        ax.set_xlim(0.995, 1.325)
        ax.set_ylim(0.2, 5.0)
        xticks, yticks = [1.0, 1.1, 1.2, 1.3], [0.25, 0.5, 1, 2, 4]
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{v:.1f}" for v in xticks])
        ax.set_yticks(yticks)
        ax.set_yticklabels(["0.25", "0.5", "1", "2", "4"])
        from matplotlib.ticker import NullLocator
        ax.yaxis.set_minor_locator(NullLocator())
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_position(("outward", 10))
        ax.spines["bottom"].set_bounds(xticks[0], xticks[-1])
        ax.spines["left"].set_bounds(yticks[0], yticks[-1])
        ax.set_xlabel("Mass ratio, heavier print ÷ lighter print", labelpad=8)
        ax.set_ylabel("e ratio, lighter print ÷ heavier print", rotation=0,
                      ha="left", va="bottom")
        ax.yaxis.set_label_coords(-0.09, 1.03)
        from matplotlib.lines import Line2D
        handles = [
            Line2D([], [], ls="none", marker="o", ms=9, mfc=FRONT_BLUE,
                   mec="white", mew=1.4),
            Line2D([], [], ls="none", marker="o", ms=5, mfc=REF_GRAY, mec="none",
                   alpha=0.6),
        ]
        labels = [f"Pair that m·e and m·e² put in opposite order ({n_swaps})",
                  f"Pair in the same order under both ({len(x) - n_swaps:,})"]
        fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0),
                   ncol=2, frameon=False, fontsize=15, handlelength=1.2,
                   columnspacing=1.8)
        fig.text(
            0.5, -0.04,
            f"Each dot is one pair of the {len(a)} tested prints "
            f"({n_equal} pairs with identical masses always keep their order "
            "and are left out).\nA pair swaps only if the lighter print's e is "
            "higher by a factor between √(mass ratio) and the mass ratio.\n"
            "The prints weigh 17.9 to 23.5 g, so the band stays close to an "
            "e ratio of 1.",
            ha="center", va="top", fontsize=13, color=LABEL_GRAY,
            linespacing=1.4,
        )
        fig.savefig(OUT_ZONE, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def main() -> int:
    a = load_articles()
    d = design_means(a)
    print(f"{len(a)} articles, {len(d)} designs")

    for col in ("E_reb_mJ", "me_g", "me2_mg", "e"):
        d[f"front_{col}"] = pareto_mask(d["t180"], d[col])
    f = fronts(d, "design")
    print("\nDesign-mean fronts (all prints), sorted by t180:")
    for col, name in [("E_reb_mJ", "current E_reb = m*e*g*h"), ("me_g", "m*e"),
                      ("me2_mg", "m*e^2"), ("e", "e alone (1 - VLI)")]:
        print(f"  {name:24s} {', '.join(f[col])}")
    assert f["me_g"] == f["E_reb_mJ"], "m*e must reproduce the current front"

    print("\nRobustness:")
    for name, frame, key in [
        ("every article", a, "specimen"),
        ("first prints only", a[a["print_no"] == 1], "specimen"),
        ("screened design means", design_means(a[a["screened"]]), "design"),
    ]:
        fr = fronts(frame, key)
        print(f"  {name}:")
        for col in ("me_g", "me2_mg"):
            print(f"    {col:7s} {', '.join(fr[col])}")

    sw_d = swapped_pairs(d, "design", "design")
    sw_a = swapped_pairs(a, "specimen", "article")
    for name, frame, sw in (("designs", d, sw_d), ("articles", a, sw_a)):
        rho = spearmanr(frame["me_g"], frame["me2_mg"]).statistic
        tau = kendalltau(frame["me_g"], frame["me2_mg"]).statistic
        n = len(frame)
        print(f"\nm*e against m*e^2 over {name}: Spearman rho {rho:.3f}, Kendall "
              f"tau {tau:.3f}; {len(sw)} of {n * (n - 1) // 2} pairs swap order")

    d = add_ranks(d)
    a = add_ranks(a)
    print_rank_changes(d, "label", "Designs")
    print_rank_changes(a, "specimen", "Articles (every print its own point)")
    print_swaps(sw_d, d, "Design pairs")
    print_swaps(sw_a, a, "Article pairs")

    # for scale: ranking by e alone (no mass weight, the manuscript's VLI)
    print("\nRank by e alone, against each mass-weighted form:")
    for name, frame in (("designs", d), ("articles", a)):
        rank_e = frame["e"].rank(method="min").astype(int)
        layer_e = pareto_layers(frame["t180"], frame["e"])
        for tag, col in (("m*e", "me"), ("m*e^2", "me2")):
            shift = rank_e - frame[f"rank_{col}"]
            print(f"  {name}, e alone vs {tag}: {int((shift != 0).sum())} of "
                  f"{len(frame)} change rank (largest shift "
                  f"{int(shift.abs().max())} places), "
                  f"{int((layer_e != frame[f'layer_{col}']).sum())} change layer")

    sd_t, sd_lne, dof = pooled_print_sd(a)
    print(f"\nPrint-to-print scatter (screened batch-3 triplicates, {dof} dof): "
          f"t180 sd {sd_t:.4f}, ln(e) sd {sd_lne:.3f}")
    d["p_front_me"] = front_probability(d, sd_t, sd_lne, power=1)
    d["p_front_me2"] = front_probability(d, sd_t, sd_lne, power=2)
    show = d[(d["p_front_me"] >= 0.1) | (d["p_front_me2"] >= 0.1)
             | d["front_me_g"] | d["front_me2_mg"]].sort_values("t180")
    print("Share of redraws on the front:")
    for _, r in show.iterrows():
        print(f"  {r['label']:10s} t180 {r['t180']:.3f}  m*e {r['p_front_me']:.2f}"
              f"  m*e^2 {r['p_front_me2']:.2f}")

    article_cols = [
        "specimen", "design", "batch", "print_no", "m_g", "t180", "t180_sem",
        "e", "e_sem", "E_reb_mJ", "me_g", "me_sem_g", "me2_mg", "me2_sem_mg",
        "gauge", "drift", "screened", "rank_me", "rank_me2", "layer_me",
        "layer_me2", "source",
    ]
    a[article_cols].to_csv(OUT_ARTICLES, index=False, float_format="%.5g")
    design_cols = [
        "design", "label", "batch", "n_prints", "prints", "m_g", "t180", "e",
        "E_reb_mJ", "me_g", "me2_mg", "front_E_reb_mJ", "front_me_g",
        "front_me2_mg", "front_e", "rank_me", "rank_me2", "layer_me",
        "layer_me2", "p_front_me", "p_front_me2",
    ]
    d.sort_values("t180")[design_cols].to_csv(OUT_DESIGNS, index=False,
                                              float_format="%.5g")
    pd.concat([sw_d, sw_a], ignore_index=True).to_csv(
        OUT_SWAPS, index=False, float_format="%.5g")
    render_overview(d)
    render_knee(d)
    render_ranks(d)
    render_swap_zone(a, len(sw_a))
    print(f"\nWrote {OUT_PNG.relative_to(REPO)}, {OUT_KNEE.relative_to(REPO)}, "
          f"{OUT_RANKS.relative_to(REPO)}, {OUT_ZONE.relative_to(REPO)}, "
          f"{OUT_ARTICLES.relative_to(REPO)}, {OUT_DESIGNS.relative_to(REPO)}, "
          f"{OUT_SWAPS.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
