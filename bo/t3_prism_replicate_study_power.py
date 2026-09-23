#!/usr/bin/env python3
"""Power analysis and pre-registration tables for the 3-design replicate study.

Supports the study plan in t3-prism-replicate-study-plan.md (the 27-article
repeatability study proposed on PR #102 on 2026-09-23: 3 characteristic
designs x 3 copies per plate x 3 plates). Everything here is derived from
data already committed on this branch:

- bo/t3-prism-bo-round3-repeatability.csv: the nine drran/2dran reprint
  pairs, the campaign's only measured article-to-article repeat data.
- bo/t3-prism-bo-round4-drop-results.csv: measured values for the three
  proposed designs (corny7 = trial 37, corny8 = trial 39, corny2 = trial 38).
- bo/t3-prism-bo-round5-logocv.csv: the current 44-article model's held-out
  (leave-one-design-out) predictions for the same articles.
- bo/t3-prism-bo-round4-predictions.csv: the frozen acquisition predictions
  the round-4 plate was generated from.

Outputs:
- bo/t3-prism-replicate-study-picks.csv: the pre-registered reference values
  (measured, held-out model, frozen round-4 model) per pick and objective.
- bo/t3-prism-replicate-study-power.csv: noise estimates and ordering
  probabilities at n = 1 / 3 / 9 articles per design.
- bo/figures/t3-prism-replicate-study-power.png: reprint-pair parity per
  objective plus the pairwise-ordering power curves.

Noise model, stated so the numbers are auditable. For a pair delta
d_i = y2_i - y1_i over reprinted designs, the article-level (print + seat +
session-residual) sd is sd(d)/sqrt(2) after removing the common batch shift
mean(d). The one observed batch shift (drran -> 2dran, +0.028 t180) is a
single draw of a session/plate block effect; in the proposed study every
plate carries all three designs equally, so block effects cancel out of
design contrasts and the contrast SE uses only the article-level sd (any
design x plate interaction is not estimable from n = 2 and is called out in
the plan). The drran7 pair (t180 delta -0.223) is excluded from the t180 sd
as a gross artifact (both extremes failed to replicate; see the README
repeatability section) and reported separately as an artifact rate; all nine
pairs stay in the rebound sd because sign-flipping deltas of that size are
the rebound phenomenon itself, not an outlier from it.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

BO_DIR = Path(__file__).resolve().parent
FIG_DIR = BO_DIR / "figures"

# The proposed picks: print_id, trial, role. All three are round-4 articles
# so one plate at the round-4 filament point reproduces the originals.
PICKS = [
    ("corny7", 37, "on the front (record attenuator)"),
    ("corny8", 39, "mid (near-twin of corny7; rebound outlier)"),
    ("corny2", 38, "far (tall amplifier family)"),
]
GRAVITY_TIMES_DROP = 9.80665 * 60 * 0.0254  # J/kg for the 60 in drop
N_PER_DESIGN = (1, 3, 9)
MC_DRAWS = 200_000
RNG = np.random.default_rng(0)


def read_rows(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def pair_stats() -> dict:
    rows = read_rows(BO_DIR / "t3-prism-bo-round3-repeatability.csv")
    t180_d = np.array([float(r["t180_delta"]) for r in rows])
    reb_d = np.array([float(r["e_reb_mJ_delta"]) for r in rows])
    keep = np.array([r["trial"] != "32" for r in rows])  # drran7 artifact
    t180_kept = t180_d[keep]
    stats = {
        "t180_shift": float(np.mean(t180_kept)),
        "t180_sigma_article": float(np.std(t180_kept, ddof=1) / math.sqrt(2)),
        "t180_artifact_pairs": int((~keep).sum()),
        "n_pairs": len(rows),
        "reb_shift": float(np.mean(reb_d)),
        "reb_sigma_article": float(np.std(reb_d, ddof=1) / math.sqrt(2)),
    }
    # Single-article sd when sessions are NOT balanced (the campaign's usual
    # n = 1 cross-round comparison): article sd plus the session block,
    # treating the one observed shift as one draw of a block difference.
    sigma_session = abs(stats["t180_shift"]) / math.sqrt(2)
    stats["t180_sigma_unbalanced"] = math.hypot(
        stats["t180_sigma_article"], sigma_session)
    # Rank stability across the reprint, per objective (all nine pairs).
    def spearman(a: np.ndarray, b: np.ndarray) -> float:
        ra = np.argsort(np.argsort(a)).astype(float)
        rb = np.argsort(np.argsort(b)).astype(float)
        return float(np.corrcoef(ra, rb)[0, 1])
    t1 = np.array([float(r["t180_1"]) for r in rows])
    t2 = np.array([float(r["t180_2"]) for r in rows])
    r1 = np.array([float(r["e_reb_mJ_1"]) for r in rows])
    r2 = np.array([float(r["e_reb_mJ_2"]) for r in rows])
    stats["t180_pair_rank_corr"] = spearman(t1, t2)
    stats["reb_pair_rank_corr"] = spearman(r1, r2)
    return stats


def picks_table() -> list[dict]:
    measured = {r["specimen"]: r
                for r in read_rows(BO_DIR / "t3-prism-bo-round4-drop-results.csv")}
    logocv: dict[tuple[str, str], dict] = {}
    for r in read_rows(BO_DIR / "t3-prism-bo-round5-logocv.csv"):
        logocv[(r["print_id"], r["metric"])] = r
    frozen = {int(float(r["trial_index"])): r
              for r in read_rows(BO_DIR / "t3-prism-bo-round4-predictions.csv")}
    out = []
    for pid, trial, role in PICKS:
        m, f = measured[pid], frozen[trial]
        mass = float(m["mass_g"])
        n = float(m["n_valid"])
        reb_mean = float(m["e_rebound_mean"]) * mass * GRAVITY_TIMES_DROP
        reb_sem = (float(m["e_rebound_sd"]) / math.sqrt(n)) * mass * GRAVITY_TIMES_DROP
        out.append({
            "print_id": pid, "trial": trial, "role": role,
            "R_mm": f["R_mm"], "H_mm": f["H_mm"], "twist_deg": f["twist_deg"],
            "strut_d_mm": f["strut_d_mm"], "cable_d_mm": f["cable_d_mm"],
            "strut_infill_pct": f["strut_infill_pct"],
            "tpu_infill_pct": f["tpu_infill_pct"],
            "mass_g": mass,
            "meas_t180": float(m["t180_mean"]),
            "meas_t180_sem": float(m["t180_sd"]) / math.sqrt(n),
            "meas_e_reb_mJ": reb_mean,
            "meas_e_reb_mJ_sem": reb_sem,
            "logocv_t180": float(logocv[(pid, "t180")]["predicted"]),
            "logocv_t180_sd": float(logocv[(pid, "t180")]["predicted_sem"]),
            "logocv_e_reb_mJ": float(logocv[(pid, "e_reb_mJ")]["predicted"]),
            "logocv_e_reb_mJ_sd": float(logocv[(pid, "e_reb_mJ")]["predicted_sem"]),
            "frozen_t180": float(f["pred_t180_mean"]),
            "frozen_t180_sd": float(f["pred_t180_sd"]),
            "frozen_e_reb_mJ": float(f["pred_e_reb_mJ_mean"]),
            "frozen_e_reb_mJ_sd": float(f["pred_e_reb_mJ_sd"]),
        })
    return out


def p_pairwise(gap: float, sigma: float, n: int) -> float:
    """P(the two design means order correctly) for a true gap and n articles
    per design, sessions balanced so block effects cancel."""
    if gap <= 0:
        return 0.5
    z = gap / (sigma * math.sqrt(2.0 / n))
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2)))


def p_full_ordering(means: list[float], sigma: float, n: int,
                    target_order: list[int]) -> float:
    """MC probability that sample design means reproduce target_order."""
    draws = RNG.normal(loc=np.array(means),
                       scale=sigma / math.sqrt(n),
                       size=(MC_DRAWS, len(means)))
    order = np.argsort(draws, axis=1)
    return float(np.mean(np.all(order == np.array(target_order), axis=1)))


def p_argmax(means: list[float], sigma: float, n: int, idx: int) -> float:
    """MC probability that design ``idx`` has the highest sample mean."""
    draws = RNG.normal(loc=np.array(means),
                       scale=sigma / math.sqrt(n),
                       size=(MC_DRAWS, len(means)))
    return float(np.mean(np.argmax(draws, axis=1) == idx))


def main() -> int:
    stats = pair_stats()
    picks = picks_table()
    picks_path = BO_DIR / "t3-prism-replicate-study-picks.csv"
    with open(picks_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(picks[0].keys()))
        w.writeheader()
        w.writerows(picks)

    s_t, s_r = stats["t180_sigma_article"], stats["reb_sigma_article"]
    meas_t = [p["meas_t180"] for p in picks]          # corny7, corny8, corny2
    meas_r = [p["meas_e_reb_mJ"] for p in picks]
    logo_t = [p["logocv_t180"] for p in picks]

    power_rows = []
    for n in N_PER_DESIGN:
        power_rows.append({
            "n_per_design": n,
            "t180_se_design_mean": s_t / math.sqrt(n),
            "reb_se_design_mean": s_r / math.sqrt(n),
            # P(reproduce the measured ordering) if the first articles are truth
            "p_t180_order_meas_truth": p_full_ordering(
                meas_t, s_t, n, [0, 1, 2]),
            # ... and if the held-out model is truth (its corny8 < corny7)
            "p_t180_order_model_truth": p_full_ordering(
                logo_t, s_t, n, [0, 1, 2]),
            "p_reb_corny8_highest_meas_truth": p_argmax(meas_r, s_r, n, 1),
            "p_reb_corny7_vs_corny2": p_pairwise(
                abs(meas_r[0] - meas_r[2]), s_r, n),
        })
    power_path = BO_DIR / "t3-prism-replicate-study-power.csv"
    with open(power_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(power_rows[0].keys()))
        w.writeheader()
        w.writerows(power_rows)

    render_figure(stats, picks)

    print("Pair statistics:", {k: round(v, 4) if isinstance(v, float) else v
                               for k, v in stats.items()})
    for row in power_rows:
        print({k: round(v, 4) if isinstance(v, float) else v
               for k, v in row.items()})
    print(f"Wrote {picks_path.name}, {power_path.name}, and the figure.")
    return 0


def render_figure(stats: dict, picks: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3", "Source Sans Pro", "Open Sans",
                            "Lato", "Helvetica", "Arial", "DejaVu Sans"],
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelsize": 15, "xtick.labelsize": 13, "ytick.labelsize": 13,
    })
    BLUE, GRAY, ORANGE = "#2b6ca3", "#83827d", "#e6862c"
    SEQ = {1: "#a6c8e8", 3: "#4a90c9", 9: "#0d4f8b"}

    rows = read_rows(BO_DIR / "t3-prism-bo-round3-repeatability.csv")
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 9.4))

    # Panel A/B: reprint parity per objective.
    for ax, key, label, unit in (
            (axes[0][0], "t180", "Shock transmissibility t180", ""),
            (axes[0][1], "e_reb_mJ", "Rebound energy", " (mJ per drop)")):
        x = np.array([float(r[f"{key}_1"]) for r in rows])
        y = np.array([float(r[f"{key}_2"]) for r in rows])
        lo = min(x.min(), y.min())
        hi = max(x.max(), y.max())
        pad = 0.06 * (hi - lo)
        lo, hi = lo - pad, hi + pad
        ax.plot([lo, hi], [lo, hi], color=GRAY, lw=1.2, ls=(0, (4, 3)),
                zorder=1)
        ax.scatter(x, y, s=64, facecolor=BLUE, edgecolor="black", lw=0.8,
                   zorder=3)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal")
        ax.set_xlabel(f"first print (drran){unit}")
        ax.set_ylabel(f"reprint (2dran){unit}")
        ax.set_title(label + ", nine reprint pairs", fontsize=16, pad=10)
        if key == "t180":
            i = [r["trial"] for r in rows].index("32")
            ax.annotate("drran7 pair\n(1.251 did not replicate)",
                        (x[i], y[i]), textcoords="offset points",
                        xytext=(14, -4), fontsize=12, color=GRAY)
            ax.text(0.03, 0.94,
                    f"batch shift +{stats['t180_shift']:.3f}\n"
                    f"article sd {stats['t180_sigma_article']:.3f}",
                    transform=ax.transAxes, fontsize=12.5, va="top",
                    color="#333333")
        else:
            ax.text(0.03, 0.94,
                    f"article sd {stats['reb_sigma_article']:.1f} mJ\n"
                    "pair rank corr "
                    f"{stats['reb_pair_rank_corr']:+.2f}",
                    transform=ax.transAxes, fontsize=12.5, va="top",
                    color="#333333")

    # Panel C/D: probability a pairwise design comparison orders correctly.
    marks = {
        "t180": [("corny7 vs corny8\n(measured gap 0.150)", 0.150),
                 ("held-out model gap 0.006", 0.006)],
        "e_reb_mJ": [("corny8 excess\n(8.2 mJ)", 8.17),
                     ("corny7 vs corny2 (0.1 mJ)", 0.15)],
    }
    for ax, key, sigma, xmax, unit in (
            (axes[1][0], "t180", stats["t180_sigma_article"], 0.16, ""),
            (axes[1][1], "e_reb_mJ", stats["reb_sigma_article"], 12.0,
             " (mJ)")):
        gaps = np.linspace(0, xmax, 400)
        for n in N_PER_DESIGN:
            p = [p_pairwise(g, sigma, n) for g in gaps]
            ax.plot(gaps, p, color=SEQ[n], lw=2.4, zorder=3)
        anchor = {"t180": (0.42, 0.80), "e_reb_mJ": (0.70, 0.72)}[key]
        for i, n in enumerate(N_PER_DESIGN):
            ax.text(anchor[0], anchor[1] - 0.055 * i,
                    f"n = {n} repeat{'s' if n > 1 else ''} per design",
                    color=SEQ[n], fontsize=12.5, transform=ax.transAxes,
                    fontweight="bold")
        ax.axhline(0.95, color=GRAY, lw=1.0, ls=(0, (4, 3)))
        ax.text(xmax * 0.005, 0.955, "95 %", color=GRAY, fontsize=11.5,
                va="bottom")
        for label, gap in marks[key]:
            if gap <= xmax:
                ax.axvline(gap, color=ORANGE, lw=1.4, alpha=0.85)
                ax.text(gap + xmax * 0.012, 0.56, label, color=ORANGE,
                        fontsize=11.5, va="top")
        ax.set_xlim(0, xmax * 1.12)
        ax.set_ylim(0.45, 1.02)
        ax.set_xlabel(f"true design gap{unit}")
        ax.set_ylabel("P(design means order correctly)")
        ax.set_title(
            {"t180": "t180: ordering power vs repeats per design",
             "e_reb_mJ": "Rebound: ordering power vs repeats per design"}[key],
            fontsize=16, pad=10)

    fig.tight_layout(w_pad=3.2, h_pad=3.0)
    FIG_DIR.mkdir(exist_ok=True)
    out = FIG_DIR / "t3-prism-replicate-study-power.png"
    fig.savefig(out, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Figure: {out}")


if __name__ == "__main__":
    raise SystemExit(main())
