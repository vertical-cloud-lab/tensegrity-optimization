"""Reconcile the round-2 short sessions (19-20 scored drops) with round 1 (~99).

The two rounds average over different windows of a session, and specimens
drift within a session, so a 19-drop mean is a slightly different measurement
than a 99-drop mean, not just a noisier one. This script quantifies that in
both directions, using only committed per-drop data:

1. Round-1 window ratios. For each round-1 specimen, the ratio of the
   full-session mean to the first-19-drop mean, per objective ingredient
   (t180 and the e_rebound fraction). The pooled distribution of those nine
   ratios is the empirical answer to "what would 80 more drops change".
2. Extrapolation of round 2 to 100-drop behavior. Each round-2 article's
   measured window mean times the pooled ratio, with a 1 sd band from the
   ratio spread combined with the article's own SEM, plus a min/max envelope.
   This is an estimate built on the assumption that round-2 articles drift
   like round-1 articles did; it is analysis, not measurement, so it is not
   written into any ingestion file.
3. The matched-window alternative (the direction Edison recommended for any
   refit): round 1 re-summarized over its own first 19 scored drops, emitted
   in the ingestion schema as t3-prism-bo-batch-drop-results-first19.csv via
   the emit_truncated helper of t3_prism_drop_count_sensitivity.py.
4. Pareto-front membership under three windowing conventions: (i) mixed, as
   committed (round-1 full vs round-2 short); (ii) matched first-19 windows
   in both rounds; (iii) full-equivalent (round-2 extrapolated to a full
   session). If the front holds under all three, no headline claim rests on
   the window mismatch.
5. The frozen plate predictions (7a048ee) re-scored against the extrapolated
   values, to check whether the round-2 calibration verdicts (9/9 t180 high,
   9/9 rebound low) survive the window correction.

Findings from the committed data (regenerate with no arguments to reprint):
the t180 window effect is tiny (pooled full/first-19 ratio 0.9985, sd
0.0033, per-specimen range -0.7 to +0.4 percent), so it cannot explain the
round-2 t180 misses of +0.04 to +0.42, and the round-1 t180 ranking is
preserved at 19 drops (Spearman +0.98; the single swap is ajhby6 vs bpx68c,
whose first-19 means differ by 0.00003). The rebound fraction is where a
short window can mislead: pooled ratio 1.041, sd 0.086, with the worst
documented case amdjwm at +26.7 percent (a late burst), so a 19-drop
rebound mean carries a +/- 8 percent band and a +27 percent tail.
Consequences, computed below: the calibration verdicts survive
extrapolation (9/9 t180 above the frozen prediction and 9/9 rebound below
at the central estimate; 6/9 rebound still below even at the worst-case
burst envelope); the round-2 core of the front (6lhxfy, r2d2c7, r2d2c1,
r2d2c2, r2d2c6) is identical under all three conventions, and the window
choice only decides whether the low-rebound round-1 anchors also sit on it
(ajhby6 joins under matched first-19; ajhby6 and bpx68c both join under
full-equivalent). The one claim that does not survive every convention is
"r2d2c1 strictly dominates bpx68c": true as committed and under matched
windows, but r2d2c1's extrapolated full-session rebound (6.21 +/- 0.51 mJ)
edges 0.03 mJ above bpx68c's measured 6.18, so state the dominance as a
short-window result.

Outputs: t3-prism-drop-window-ratios.csv (per round-1 specimen),
t3-prism-drop-window-extrapolation.csv (per round-2 article, measured vs
extrapolated), t3-prism-drop-window-front-robustness.csv (17 articles x 3
conventions), t3-prism-bo-batch-drop-results-first19.csv (ingestion-ready
matched window) and figures/t3-prism-drop-window-extrapolation.png.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BO_DIR = Path(__file__).resolve().parent
R1_PER_DROP = BO_DIR / "t3-prism-per-drop-metrics.csv"
R2_PER_DROP = BO_DIR / "t3-prism-bo-round1-per-drop-metrics.csv"
R1_SUMMARY = BO_DIR / "t3-prism-bo-batch-drop-results.csv"
R2_SUMMARY = BO_DIR / "t3-prism-bo-round1-drop-results.csv"
R2_PREDICTIONS = BO_DIR / "t3-prism-bo-round1-predictions.csv"

OUT_RATIOS = BO_DIR / "t3-prism-drop-window-ratios.csv"
OUT_EXTRAP = BO_DIR / "t3-prism-drop-window-extrapolation.csv"
OUT_FRONTS = BO_DIR / "t3-prism-drop-window-front-robustness.csv"
OUT_FIRST19 = BO_DIR / "t3-prism-bo-batch-drop-results-first19.csv"
OUT_PNG = BO_DIR / "figures" / "t3-prism-drop-window-extrapolation.png"

G_M_S2 = 9.80665
DROP_H_M = 1.524  # 60 in, issue #98 campaign protocol
MJ_PER_G = G_M_S2 * DROP_H_M  # e_reb_mJ = e_rebound * mass_g * this

WINDOW = 19  # scored drops per round-2 session (one session has 20)


def window_ratios(per_drop: pd.DataFrame, w: int) -> pd.DataFrame:
    """Full-session mean over first-w mean, per specimen and objective."""
    rows = []
    for sid, g in per_drop.groupby("specimen", sort=True):
        g = g.sort_values("drop_index")
        t = g["t180"].to_numpy(float)
        e = g["e_rebound"].to_numpy(float)
        rows.append(
            {
                "specimen": sid,
                "n_full": len(t),
                "t180_first_w": float(np.mean(t[:w])),
                "t180_full": float(np.mean(t)),
                "ratio_t180": float(np.mean(t) / np.mean(t[:w])),
                "e_rebound_first_w": float(np.mean(e[:w])),
                "e_rebound_full": float(np.mean(e)),
                "ratio_e_rebound": float(np.mean(e) / np.mean(e[:w])),
            }
        )
    return pd.DataFrame(rows)


def pooled(ratios: pd.Series) -> dict:
    r = ratios.to_numpy(float)
    return {
        "mean": float(np.mean(r)),
        "sd": float(np.std(r, ddof=1)),
        "min": float(np.min(r)),
        "max": float(np.max(r)),
    }


def extrapolate_round2(
    per_drop: pd.DataFrame, summary: pd.DataFrame, pool_t: dict, pool_e: dict
) -> pd.DataFrame:
    """Project each short round-2 session to a full-session equivalent."""
    mass = summary.set_index("specimen")["mass_g"]
    rows = []
    for sid, g in per_drop.groupby("specimen", sort=True):
        g = g.sort_values("drop_index")
        t = g["t180"].to_numpy(float)
        e = g["e_rebound"].to_numpy(float)
        n = len(t)
        t_m, t_sem = float(np.mean(t)), float(np.std(t, ddof=1) / np.sqrt(n))
        e_m, e_sem = float(np.mean(e)), float(np.std(e, ddof=1) / np.sqrt(n))
        m_g = float(mass[sid])
        row = {"specimen": sid, "n_scored": n, "mass_g": m_g}
        for name, val, sem, pool in (
            ("t180", t_m, t_sem, pool_t),
            ("e_rebound", e_m, e_sem, pool_e),
        ):
            hat = val * pool["mean"]
            sd = float(np.hypot(val * pool["sd"], pool["mean"] * sem))
            row.update(
                {
                    f"{name}_measured": val,
                    f"{name}_measured_sem": sem,
                    f"{name}_extrap_mean": hat,
                    f"{name}_extrap_sd": sd,
                    f"{name}_extrap_lo": val * pool["min"],
                    f"{name}_extrap_hi": val * pool["max"],
                }
            )
        for tag in ("measured", "extrap_mean", "extrap_sd",
                    "extrap_lo", "extrap_hi"):
            row[f"e_reb_mJ_{tag}"] = row[f"e_rebound_{tag}"] * m_g * MJ_PER_G
        rows.append(row)
    return pd.DataFrame(rows)


def front_mask(t: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Non-dominated mask, both objectives minimized."""
    n = len(t)
    keep = np.ones(n, bool)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if (
                t[j] <= t[i]
                and e[j] <= e[i]
                and (t[j] < t[i] or e[j] < e[i])
            ):
                keep[i] = False
                break
    return keep


def build_front_table(
    r1_ratio: pd.DataFrame,
    r1_summary: pd.DataFrame,
    extrap: pd.DataFrame,
) -> pd.DataFrame:
    """The 17 mapped articles under the three windowing conventions."""
    r1 = r1_summary.dropna(subset=["mass_g"]).set_index("specimen")
    rr = r1_ratio.set_index("specimen")
    frames = []
    for convention in ("mixed (committed)", "matched first-19",
                       "full-equivalent"):
        rows = []
        for sid in r1.index:
            t_full = float(r1.loc[sid, "t180_mean"])
            e_full = float(r1.loc[sid, "e_rebound_mean"])
            m_g = float(r1.loc[sid, "mass_g"])
            if convention == "matched first-19":
                t, e = rr.loc[sid, "t180_first_w"], rr.loc[sid, "e_rebound_first_w"]
            else:
                t, e = t_full, e_full
            rows.append(
                {"specimen": sid, "round": 1, "t180": t,
                 "e_reb_mJ": e * m_g * MJ_PER_G}
            )
        for _, x in extrap.iterrows():
            if convention == "full-equivalent":
                t, e_mj = x["t180_extrap_mean"], x["e_reb_mJ_extrap_mean"]
            else:
                t, e_mj = x["t180_measured"], x["e_reb_mJ_measured"]
            rows.append(
                {"specimen": x["specimen"], "round": 2, "t180": t,
                 "e_reb_mJ": e_mj}
            )
        f = pd.DataFrame(rows)
        f["convention"] = convention
        f["on_front"] = front_mask(
            f["t180"].to_numpy(float), f["e_reb_mJ"].to_numpy(float)
        )
        frames.append(f)
    return pd.concat(frames, ignore_index=True)


def rescore_predictions(extrap: pd.DataFrame, r2_summary: pd.DataFrame) -> pd.DataFrame:
    """Frozen plate predictions vs measured and vs extrapolated values."""
    preds = pd.read_csv(R2_PREDICTIONS)
    spec_of = r2_summary.set_index("specimen")["spec"].astype(int)
    preds = preds.set_index(preds["trial_index"].astype(int) - 10)
    rows = []
    for _, x in extrap.iterrows():
        p = preds.loc[int(spec_of[x["specimen"]])]
        rows.append(
            {
                "specimen": x["specimen"],
                "pred_t180": float(p["pred_t180_mean"]),
                "t180_measured": x["t180_measured"],
                "t180_extrap": x["t180_extrap_mean"],
                "pred_e_reb_mJ": float(p["pred_e_reb_mJ_mean"]),
                "e_reb_mJ_measured": x["e_reb_mJ_measured"],
                "e_reb_mJ_extrap": x["e_reb_mJ_extrap_mean"],
                "e_reb_mJ_extrap_hi": x["e_reb_mJ_extrap_hi"],
            }
        )
    return pd.DataFrame(rows)


def render_figure(
    r1_ratio: pd.DataFrame,
    pool_t: dict,
    pool_e: dict,
    fronts: pd.DataFrame,
    extrap: pd.DataFrame,
    out_png: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from t3_prism_bo_campaign import (
        ARROW_DOWN, FIG_RC, FIGURE_DPI, FRONT_BLUE, INK, LABEL_GRAY,
        PRIOR_FRONT_GRAY, SUGGEST_ORANGE, X_LABEL, Y_LABEL,
    )

    rc = dict(FIG_RC)
    rc.update({"font.size": 15, "axes.labelsize": 16,
               "xtick.labelsize": 14, "ytick.labelsize": 14})

    with plt.rc_context(rc):
        fig, (axA, axB) = plt.subplots(
            1, 2, figsize=(14.4, 6.2), dpi=FIGURE_DPI,
            gridspec_kw={"width_ratios": [1.0, 1.25]},
        )

        # Panel A: what 80 more drops changed in round 1, per specimen
        rows = (("ratio_t180", 1.0, "t180"),
                ("ratio_e_rebound", 0.0, "rebound\nfraction"))
        rng = np.random.default_rng(7)
        for col, ypos, name in rows:
            pool = pool_t if col == "ratio_t180" else pool_e
            band = plt.Rectangle(
                (100 * (pool["mean"] - pool["sd"] - 1), ypos - 0.28),
                100 * 2 * pool["sd"], 0.56,
                fc=FRONT_BLUE, alpha=0.14, ec="none", zorder=1,
            )
            axA.add_patch(band)
            axA.plot(
                [100 * (pool["mean"] - 1)] * 2, [ypos - 0.28, ypos + 0.28],
                color=FRONT_BLUE, lw=2.4, zorder=3,
            )
            for _, r in r1_ratio.iterrows():
                x = 100 * (r[col] - 1)
                jitter = float(rng.uniform(-0.10, 0.10))
                axA.plot(
                    x, ypos + jitter, "o", ms=8, mfc="none", mec=INK,
                    mew=1.6, zorder=4,
                )
                if abs(x) > 3.5:
                    axA.annotate(
                        r["specimen"], (x, ypos + jitter),
                        xytext=(0, 11), textcoords="offset points",
                        ha="center", fontsize=12.5, color=LABEL_GRAY,
                    )
        axA.axvline(0, color=INK, lw=1.0, alpha=0.35, zorder=2)
        axA.set_yticks([1.0, 0.0])
        axA.set_yticklabels([r[2] for r in rows])
        axA.set_ylim(-0.6, 1.6)
        axA.set_xlim(-6, 30)
        axA.set_xlabel(
            "Change from first-19-drop mean to full-session mean (%)"
        )
        axA.set_title(
            "Round 1: what the last ~80 drops change\n"
            "(band: pooled mean ± 1 sd, the factor applied to round 2)",
            fontsize=15, loc="left", pad=10,
        )

        # Panel B: objective space, short-window points extrapolated out
        conv = {
            name: fronts[fronts["convention"] == name]
            for name in fronts["convention"].unique()
        }
        mixed = conv["mixed (committed)"]
        fullq = conv["full-equivalent"]
        for name, sub, color, ls in (
            ("mixed (committed)", mixed, PRIOR_FRONT_GRAY, "-"),
            ("full-equivalent", fullq, FRONT_BLUE, "-"),
        ):
            fr = sub[sub["on_front"]].sort_values("t180")
            axB.plot(
                fr["t180"], fr["e_reb_mJ"], color=color, lw=2.6, ls=ls,
                zorder=2 if color == PRIOR_FRONT_GRAY else 3, alpha=0.9,
            )
        r1_pts = mixed[mixed["round"] == 1]
        axB.plot(
            r1_pts["t180"], r1_pts["e_reb_mJ"], "o", ms=8, mfc="none",
            mec=LABEL_GRAY, mew=1.6, ls="none", zorder=3,
        )
        for _, x in extrap.iterrows():
            axB.annotate(
                "",
                (x["t180_extrap_mean"], x["e_reb_mJ_extrap_mean"]),
                (x["t180_measured"], x["e_reb_mJ_measured"]),
                arrowprops=dict(
                    arrowstyle="-|>", color=SUGGEST_ORANGE, lw=1.6,
                    shrinkA=6, shrinkB=2, alpha=0.9,
                ),
                zorder=4,
            )
            axB.plot(
                [x["t180_extrap_mean"]] * 2,
                [
                    x["e_reb_mJ_extrap_mean"] - x["e_reb_mJ_extrap_sd"],
                    x["e_reb_mJ_extrap_mean"] + x["e_reb_mJ_extrap_sd"],
                ],
                color=SUGGEST_ORANGE, lw=1.4, alpha=0.45, zorder=3,
            )
            axB.plot(
                x["t180_extrap_mean"], x["e_reb_mJ_extrap_mean"], "D",
                ms=7, mfc="white", mec=SUGGEST_ORANGE, mew=1.6, zorder=5,
            )
            axB.plot(
                x["t180_measured"], x["e_reb_mJ_measured"], "o", ms=9,
                mfc="none", mec=INK, mew=1.8, zorder=5,
            )
            ox, oy, ha = {
                "r2d2c1": (-12, -6, "right"),
                "r2d2c2": (0, -26, "center"),
                "r2d2c3": (12, -6, "left"),
                "r2d2c4": (12, -18, "left"),
                "r2d2c5": (12, 6, "left"),
                "r2d2c6": (12, -14, "left"),
                "r2d2c7": (-12, -10, "right"),
                "r2d2c8": (12, -4, "left"),
                "r2d2c9": (12, -18, "left"),
            }[x["specimen"]]
            axB.annotate(
                x["specimen"],
                (x["t180_measured"], x["e_reb_mJ_measured"]),
                xytext=(ox, oy), textcoords="offset points", ha=ha,
                fontsize=12, color=LABEL_GRAY,
            )
        for sid, (ox, oy, ha) in (
            ("6lhxfy", (10, -4, "left")),
            ("6nheas", (10, 2, "left")),
        ):
            r = r1_pts[r1_pts["specimen"] == sid].iloc[0]
            axB.annotate(
                sid, (r["t180"], r["e_reb_mJ"]), xytext=(ox, oy),
                textcoords="offset points", ha=ha, fontsize=12,
                color=LABEL_GRAY,
            )
        # bpx68c and ajhby6 nearly coincide at this scale; one shared label
        pair = r1_pts[r1_pts["specimen"].isin(["bpx68c", "ajhby6"])]
        axB.annotate(
            "bpx68c, ajhby6",
            (float(pair["t180"].mean()), float(pair["e_reb_mJ"].mean())),
            xytext=(14, 8), textcoords="offset points", ha="left",
            fontsize=12, color=LABEL_GRAY,
        )
        handles = [
            plt.Line2D([], [], marker="o", ls="none", mfc="none", mec=INK,
                       mew=1.8, ms=9, label="round 2, measured (19-20 drops)"),
            plt.Line2D([], [], marker="D", ls="none", mfc="white",
                       mec=SUGGEST_ORANGE, mew=1.6, ms=7,
                       label="extrapolated to a full session ± 1 sd"),
            plt.Line2D([], [], marker="o", ls="none", mfc="none",
                       mec=LABEL_GRAY, mew=1.6, ms=8,
                       label="round 1 (~99 drops)"),
            plt.Line2D([], [], color=PRIOR_FRONT_GRAY, lw=2.6,
                       label="front, windows as committed"),
            plt.Line2D([], [], color=FRONT_BLUE, lw=2.6,
                       label="front, round 2 extrapolated"),
        ]
        # the upper-right region (poor on both objectives at once) is empty
        # in this data, so the legend cannot cover anything there
        axB.legend(handles=handles, loc="upper right", frameon=False,
                   fontsize=12.5, handletextpad=0.6, borderaxespad=0.1)
        axB.set_xlabel(X_LABEL.replace("Shock transmissibility ", ""))
        axB.set_ylabel(
            f"Rebound energy (mJ per drop, {ARROW_DOWN} is better)"
        )
        axB.set_xlim(0.86, 1.40)
        axB.set_ylim(3.0, 15.0)
        axB.set_title(
            "Objective space: where a full session would likely land",
            fontsize=15, loc="left", pad=10,
        )

        for ax in (axA, axB):
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
        fig.tight_layout()
        out_png.parent.mkdir(exist_ok=True)
        fig.savefig(out_png, dpi=FIGURE_DPI, facecolor="white",
                    bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out_png}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--no-figure", action="store_true")
    args = ap.parse_args(argv)
    w = args.window

    r1_per_drop = pd.read_csv(R1_PER_DROP)
    r2_per_drop = pd.read_csv(R2_PER_DROP)
    r1_summary = pd.read_csv(R1_SUMMARY, dtype={"spec": "string"})
    r2_summary = pd.read_csv(R2_SUMMARY)

    ratios = window_ratios(r1_per_drop, w)
    ratios.to_csv(OUT_RATIOS, index=False, float_format="%.6f")
    print(f"wrote {OUT_RATIOS}")
    pool_t = pooled(ratios["ratio_t180"])
    pool_e = pooled(ratios["ratio_e_rebound"])
    no_burst = ratios[ratios["specimen"] != "amdjwm"]
    print(f"\nround-1 full/first-{w} ratios, n = {len(ratios)}:")
    for name, pool in (("t180", pool_t), ("e_rebound", pool_e)):
        print(
            f"  {name}: mean {pool['mean']:.4f}, sd {pool['sd']:.4f}, "
            f"range [{pool['min']:.4f}, {pool['max']:.4f}]"
        )
    print(
        "  e_rebound without amdjwm (the burst case): "
        f"mean {no_burst['ratio_e_rebound'].mean():.4f}, "
        f"sd {no_burst['ratio_e_rebound'].std(ddof=1):.4f}"
    )
    rt = ratios.set_index("specimen")
    for col_w, col_f, name in (
        ("t180_first_w", "t180_full", "t180"),
        ("e_rebound_first_w", "e_rebound_full", "e_rebound"),
    ):
        rw = rt[col_w].rank()
        rf = rt[col_f].rank()
        rho = float(np.corrcoef(rw, rf)[0, 1])
        print(f"  round-1 {name} ranking, first-{w} vs full: "
              f"Spearman {rho:+.2f}")

    extrap = extrapolate_round2(r2_per_drop, r2_summary, pool_t, pool_e)
    extrap.to_csv(OUT_EXTRAP, index=False, float_format="%.6f")
    print(f"\nwrote {OUT_EXTRAP}")
    view = extrap[
        ["specimen", "n_scored", "t180_measured", "t180_extrap_mean",
         "t180_extrap_sd", "e_reb_mJ_measured", "e_reb_mJ_extrap_mean",
         "e_reb_mJ_extrap_sd", "e_reb_mJ_extrap_hi"]
    ]
    print(view.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    fronts = build_front_table(ratios, r1_summary, extrap)
    fronts.to_csv(OUT_FRONTS, index=False, float_format="%.5f")
    print(f"\nwrote {OUT_FRONTS}")
    for convention, sub in fronts.groupby("convention", sort=False):
        members = sub[sub["on_front"]].sort_values("t180")["specimen"]
        print(f"  front under {convention}: {', '.join(members)}")

    # does the window mismatch move the calibration verdicts?
    scored = rescore_predictions(extrap, r2_summary)
    t_above = int((scored["t180_extrap"] > scored["pred_t180"]).sum())
    e_below = int((scored["e_reb_mJ_extrap"] < scored["pred_e_reb_mJ"]).sum())
    e_below_worst = int(
        (scored["e_reb_mJ_extrap_hi"] < scored["pred_e_reb_mJ"]).sum()
    )
    print(
        f"\nfrozen plate predictions vs full-session-extrapolated values: "
        f"{t_above}/9 t180 above prediction, {e_below}/9 rebound below "
        f"prediction ({e_below_worst}/9 even at the +{100 * (pool_e['max'] - 1):.0f}% "
        "worst-case burst envelope)"
    )

    from t3_prism_drop_count_sensitivity import emit_truncated

    emit_truncated(r1_per_drop, w, OUT_FIRST19)

    if not args.no_figure:
        render_figure(ratios, pool_t, pool_e, fronts, extrap, OUT_PNG)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(BO_DIR))
    main()
