"""Three prints of the batch-3 designs: repeatability, seat gauge, design-mean front.

Reads only committed snapshots under manuscript/data/:
  t3-prism-bo-round3-drop-results.csv              print 1 (drran1-9)
  t3-prism-bo-round3-reprint-drop-results.csv      print 2 (2dran1-9)
  t3-prism-bo-round3-third-print-drop-results.csv  print 3 (dran31-39)
  t3-prism-bo-round3-predictions.csv               frozen batch-3 predictions
  t3-prism-bo-batch-drop-results.csv               seed batch (physical batch 1)
  t3-prism-bo-round1-drop-results.csv              batch 2 (r2d2c)
  t3-prism-bo-round4-drop-results.csv              batch 4 (corny)
and cross-checks against the check-in's own three-print summary
(t3-prism-bo-round3-three-print-checkin.json).

Writes
  manuscript/data/t3-prism-bo-round3-three-print.csv        one row per design
  manuscript/data/t3-prism-bo-round3-three-print-stats.json every quoted number
  figures/analysis/round3-three-print.png

Health screen (as in the check-in): a session is screened in when its seat
gauge, the ratio of CFC-1000 to CFC-180 transmissibility, is below 1.145
and it carries no transmissibility-drift flag.

E_reb = e_rebound * m * g * h (mJ per drop) with the session's weighed mass,
g = 9.80665 m/s^2 and h = 60 in, the convention of the campaign tables.
VLI = 1 - e_rebound.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "manuscript/data"
OUT_CSV = DATA / "t3-prism-bo-round3-three-print.csv"
OUT_JSON = DATA / "t3-prism-bo-round3-three-print-stats.json"
OUT_FIG = ROOT / "figures/analysis/round3-three-print.png"

G, H = 9.80665, 60 * 0.0254
GAUGE_MAX = 1.145
REF = (1.35, 15.0)  # hypervolume reference (t180, E_reb mJ), as in the paper
PRINTS = [("drran", "t3-prism-bo-round3-drop-results.csv"),
          ("2dran", "t3-prism-bo-round3-reprint-drop-results.csv"),
          ("dran3", "t3-prism-bo-round3-third-print-drop-results.csv")]


def e_reb_mj(df: pd.DataFrame) -> pd.Series:
    return df.e_rebound_mean * df.mass_g / 1000 * G * H * 1000


def load_print(tag: str, fname: str) -> pd.DataFrame:
    d = pd.read_csv(DATA / fname)
    if "trial" not in d:
        d["trial"] = d.spec.str.lstrip("t").astype(int)
    d = d.assign(print_=tag, gauge=d.t1000_mean / d.t180_mean,
                 e_reb_mJ=e_reb_mj(d), vli=1 - d.e_rebound_mean,
                 drift=d.t_drift_flag.astype(str).eq("True"))
    d["screened"] = (d.gauge < GAUGE_MAX) & ~d.drift
    return d[["trial", "print_", "specimen", "mass_g", "n_valid", "t180_mean",
              "t180_sd", "gauge", "drift", "screened", "e_reb_mJ", "vli"]]


def icc_oneway(groups: list[np.ndarray]) -> float:
    """ICC(1) one-way random effects, unbalanced groups allowed."""
    groups = [g for g in groups if len(g) > 0]
    n_i = np.array([len(g) for g in groups])
    allv = np.concatenate(groups)
    a, N, grand = len(groups), len(allv), allv.mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    msb, msw = ssb / (a - 1), ssw / (N - a)
    n0 = (N - (n_i ** 2).sum() / N) / (a - 1)
    return float((msb - msw) / (msb + (n0 - 1) * msw))


def additive_fit(d: pd.DataFrame) -> dict:
    """Least squares t180 ~ design + print offset; returns resid sd and offsets."""
    designs = sorted(d.trial.unique())
    prints = [p for p, _ in PRINTS]
    X = np.zeros((len(d), len(designs) + len(prints) - 1))
    for r, (t, p) in enumerate(zip(d.trial, d.print_)):
        X[r, designs.index(t)] = 1
        if p != prints[0]:
            X[r, len(designs) + prints.index(p) - 1] = 1
    y = d.t180_mean.values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    return {"n_cells": int(len(y)), "dof": int(dof),
            "resid_sd": float(np.sqrt((resid ** 2).sum() / dof)),
            "max_abs_resid": float(np.abs(resid).max()),
            "print_offset": {p: (0.0 if i == 0 else float(beta[len(designs) + i - 1]))
                             for i, p in enumerate(prints)},
            "design_mean": {int(t): float(beta[i] + np.mean(
                [0.0] + list(beta[len(designs):]))) for i, t in enumerate(designs)}}


def pareto(points: pd.DataFrame) -> pd.DataFrame:
    """Non-dominated rows of (t180, e_reb_mJ), both minimized."""
    keep = []
    for i, r in points.iterrows():
        dominated = ((points.t180 <= r.t180) & (points.e_reb_mJ <= r.e_reb_mJ)
                     & ((points.t180 < r.t180) | (points.e_reb_mJ < r.e_reb_mJ))).any()
        if not dominated:
            keep.append(i)
    return points.loc[keep].sort_values("t180")


def hypervolume(front: pd.DataFrame) -> float:
    f = front[(front.t180 < REF[0]) & (front.e_reb_mJ < REF[1])].sort_values("t180")
    t = list(f.t180) + [REF[0]]
    return float(sum((t[i + 1] - t[i]) * (REF[1] - e) for i, e in enumerate(f.e_reb_mJ)))


def main() -> None:
    long = pd.concat([load_print(p, f) for p, f in PRINTS], ignore_index=True)
    pred = pd.read_csv(DATA / "t3-prism-bo-round3-predictions.csv").set_index("trial_index")
    long["pred_t180"] = long.trial.map(pred.pred_t180_mean)
    med = long.groupby("trial").t180_mean.median()
    long["dev_from_median_pct"] = 100 * (long.t180_mean / long.trial.map(med) - 1)

    s = {}
    scr = long[long.screened]
    s["n_sessions"] = int(len(long))
    s["n_screened"] = int(len(scr))
    s["drops_third_print"] = int(long[long.print_ == "dran3"].n_valid.sum())
    s["mean_mass_g"] = long.groupby("print_").mass_g.mean().round(2).to_dict()
    s["batch_median_t180"] = long.groupby("print_").t180_mean.median().round(4).to_dict()
    s["additive_fit_screened"] = additive_fit(scr)
    s["additive_fit_all"] = additive_fit(long)
    dmean_scr = scr.groupby("trial").t180_mean.mean()
    s["screened_design_mean_t180"] = dmean_scr.round(4).to_dict()
    s["between_design_sd_screened"] = float(dmean_scr.std(ddof=1))
    no35 = dmean_scr.drop(35)
    s["screened_means_without_t35"] = {"min": float(no35.min()), "max": float(no35.max()),
                                       "sd": float(no35.std(ddof=1))}

    # Seat gauge against deviation from the design's three-print median.
    g = stats.spearmanr(long.gauge, long.dev_from_median_pct)
    tripped = long[long.gauge >= GAUGE_MAX]
    healthy = long[(long.gauge < GAUGE_MAX)]
    s["seat_gauge"] = {
        "spearman_gauge_vs_dev": {"rho": float(g.statistic), "p": float(g.pvalue)},
        "tripped": tripped[["specimen", "trial", "gauge", "t180_mean",
                            "dev_from_median_pct"]].round(4).to_dict("records"),
        "tripped_is_design_max": bool(all(
            r.t180_mean == long[long.trial == r.trial].t180_mean.max()
            for r in tripped.itertuples())),
        "untripped_abs_dev_pct": {"n": int(len(healthy)),
                                  "median": float(healthy.dev_from_median_pct.abs().median()),
                                  "max": float(healthy.dev_from_median_pct.abs().max())},
        "healthy_band_1p07": {
            "n": int((long.gauge <= 1.07).sum()),
            "median_abs_dev_pct": float(long[long.gauge <= 1.07].dev_from_median_pct.abs().median())},
    }

    # Rank agreement between prints, and with the frozen predictions.
    wide_t = long.pivot(index="trial", columns="print_", values="t180_mean")
    wide_e = long.pivot(index="trial", columns="print_", values="e_reb_mJ")
    pairs = [("drran", "2dran"), ("drran", "dran3"), ("2dran", "dran3")]
    s["rank_between_prints_t180"] = {f"{a}-{b}": float(stats.spearmanr(wide_t[a], wide_t[b]).statistic)
                                     for a, b in pairs}
    s["rank_between_prints_e_reb"] = {f"{a}-{b}": float(stats.spearmanr(wide_e[a], wide_e[b]).statistic)
                                      for a, b in pairs}
    pt = pred.pred_t180_mean.reindex(wide_t.index)
    adj = pd.Series(s["additive_fit_screened"]["design_mean"]).reindex(wide_t.index)
    s["frozen_prediction_agreement"] = {
        **{p: {"rho": float(stats.spearmanr(pt, wide_t[p]).statistic),
               "p": float(stats.spearmanr(pt, wide_t[p]).pvalue)} for p, _ in PRINTS},
        "screened_design_mean": {"rho": float(stats.spearmanr(pt, dmean_scr).statistic),
                                 "p": float(stats.spearmanr(pt, dmean_scr).pvalue),
                                 "rms": float(np.sqrt(((pt - dmean_scr) ** 2).mean()))},
        # Design means from the screened additive fit, i.e. adjusted for the
        # offset between prints (the check-in's own rank statistic).
        "screened_offset_adjusted_design_mean": {
            "rho": float(stats.spearmanr(pt, adj).statistic),
            "p": float(stats.spearmanr(pt, adj).pvalue)}}

    # Test-retest reliability (ICC(1)), all 27 sessions and screened only.
    s["icc_t180"] = {"all": icc_oneway([wide_t.loc[t].values for t in wide_t.index]),
                     "screened": icc_oneway([scr[scr.trial == t].t180_mean.values
                                             for t in wide_t.index])}
    s["icc_e_reb"] = {"all": icc_oneway([wide_e.loc[t].values for t in wide_e.index]),
                      "screened": icc_oneway([scr[scr.trial == t].e_reb_mJ.values
                                              for t in wide_e.index])}
    ratio = wide_e.max(axis=1) / wide_e.min(axis=1)
    s["e_reb_max_over_min_per_design"] = {"min": float(ratio.min()), "max": float(ratio.max()),
                                          "median": float(ratio.median())}
    s["e_reb_range_mJ"] = {"min": float(wide_e.min().min()), "max": float(wide_e.max().max())}
    s["e_reb_between_print_sd_mJ"] = float(np.sqrt(
        ((wide_e.sub(wide_e.mean(axis=1), axis=0)) ** 2).sum().sum()
        / (wide_e.size - len(wide_e))))
    s["e_reb_design_mean_sd_mJ"] = float(wide_e.mean(axis=1).std(ddof=1))
    s["t180_within_session_sem_median"] = float(
        (long.t180_sd / np.sqrt(long.n_valid - 2)).median())

    # Design-mean front over the whole campaign. Batch-3 designs enter once,
    # at the mean of their screened prints (both objectives); every other
    # article enters as measured. amdjwm has no weighed mass and is omitted.
    other = []
    for f, b in [("t3-prism-bo-batch-drop-results.csv", 1),
                 ("t3-prism-bo-round1-drop-results.csv", 2),
                 ("t3-prism-bo-round4-drop-results.csv", 4)]:
        d = pd.read_csv(DATA / f)
        d = d[d.mass_g.notna()]
        other.append(pd.DataFrame({"label": d.specimen, "batch": b,
                                   "t180": d.t180_mean, "e_reb_mJ": e_reb_mj(d)}))
    other = pd.concat(other, ignore_index=True)
    first = long[long.print_ == "drran"]
    first_pts = pd.DataFrame({"label": first.specimen, "batch": 3,
                              "t180": first.t180_mean, "e_reb_mJ": first.e_reb_mJ})
    as_measured = pareto(pd.concat([other, first_pts], ignore_index=True))
    s["front_first_prints"] = {"members": list(as_measured.label),
                               "hv": hypervolume(as_measured)}
    for name, src in [("screened", scr), ("all_prints", long)]:
        dm = src.groupby("trial").agg(t180=("t180_mean", "mean"), e_reb_mJ=("e_reb_mJ", "mean"))
        label = first.set_index("trial").specimen.reindex(dm.index) + "*"
        pts = pd.DataFrame({"label": label.values, "batch": 3, "t180": dm.t180.values,
                            "e_reb_mJ": dm.e_reb_mJ.values})
        fr = pareto(pd.concat([other, pts], ignore_index=True))
        s[f"front_design_means_{name}"] = {"members": list(fr.label), "hv": hypervolume(fr)}
        upto3 = pareto(pd.concat([other[other.batch < 4], pts], ignore_index=True))
        s[f"front_after_batch3_design_means_{name}"] = {"members": list(upto3.label),
                                                        "hv": hypervolume(upto3)}
    upto2 = pareto(other[other.batch < 3])
    s["front_after_batch2"] = {"members": list(upto2.label), "hv": hypervolume(upto2)}

    # Cross-check against the check-in's own summary.
    ck = json.loads((DATA / "t3-prism-bo-round3-three-print-checkin.json").read_text())
    s["checkin_crosscheck"] = {
        "resid_sd_checkin": ck["aggregate"]["additive_fit_screened"]["resid_sd"],
        "resid_sd_here": round(s["additive_fit_screened"]["resid_sd"], 4),
        "rho_pred_screened_checkin": ck["model_agreement"]["screened_design_means"]["spearman_rho"],
        "rho_pred_screened_here": round(s["frozen_prediction_agreement"]["screened_design_mean"]["rho"], 3)}

    # Per-design wide table for the manuscript.
    rows = []
    for t in sorted(wide_t.index):
        r = {"trial": int(t), "pred_t180": round(float(pt[t]), 3)}
        for p, _ in PRINTS:
            c = long[(long.trial == t) & (long.print_ == p)].iloc[0]
            r.update({f"article_{p}": c.specimen, f"mass_g_{p}": c.mass_g,
                      f"t180_{p}": round(c.t180_mean, 4), f"gauge_{p}": round(c.gauge, 3),
                      f"drift_{p}": bool(c.drift), f"screened_{p}": bool(c.screened),
                      f"e_reb_mJ_{p}": round(c.e_reb_mJ, 2), f"vli_{p}": round(c.vli, 4)})
        r["t180_screened_mean"] = round(float(dmean_scr[t]), 4)
        r["e_reb_mJ_mean"] = round(float(wide_e.loc[t].mean()), 2)
        rows.append(r)
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(s, indent=1, default=float) + "\n")

    # Figure: per-design transmissibility and E_reb across the three prints.
    order = dmean_scr.sort_values().index
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), constrained_layout=True)
    marks = {"drran": "o", "2dran": "s", "dran3": "^"}
    names = {"drran": "print 1", "2dran": "print 2", "dran3": "print 3"}
    for ax, col, lab, tag in [(axes[0], "t180_mean", r"transmissibility $t_{180}$", "(a)"),
                              (axes[1], "e_reb_mJ", r"$E_{\mathrm{reb}}$ (mJ per drop)", "(b)")]:
        ax.set_title(tag, loc="left", fontsize=9)
        for k, (p, _) in enumerate(PRINTS):
            d = long[long.print_ == p].set_index("trial").reindex(order)
            x = np.arange(len(order)) + (k - 1) * 0.18
            ok = d.screened.values
            ax.scatter(x[ok], d[col].values[ok], marker=marks[p], color="#1f4e79",
                       s=26, label=names[p], zorder=3)
            ax.scatter(x[~ok], d[col].values[~ok], marker=marks[p], facecolors="white",
                       edgecolors="#c0392b", s=30, linewidths=1.2, zorder=3)
        ax.set_xticks(np.arange(len(order)), [str(t) for t in order], fontsize=8)
        ax.set_xlabel("Ax trial (design), ordered by screened mean $t_{180}$", fontsize=8)
        ax.set_ylabel(lab, fontsize=9)
        ax.grid(axis="y", color="0.9", linewidth=0.6)
        ax.tick_params(labelsize=8)
    axes[0].axhline(1.0, color="0.5", linewidth=0.8, linestyle="--")
    axes[0].scatter([], [], marker="o", facecolors="white", edgecolors="#c0392b",
                    label="seat gauge or drift flag")
    axes[0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.savefig(OUT_FIG, dpi=200)

    print(json.dumps({k: s[k] for k in ["additive_fit_screened", "between_design_sd_screened",
                                        "screened_means_without_t35", "seat_gauge",
                                        "frozen_prediction_agreement", "icc_t180", "icc_e_reb",
                                        "e_reb_max_over_min_per_design", "rank_between_prints_t180",
                                        "rank_between_prints_e_reb", "front_first_prints",
                                        "front_design_means_screened", "front_design_means_all_prints",
                                        "front_after_batch2", "front_after_batch3_design_means_screened",
                                        "front_after_batch3_design_means_all_prints",
                                        "checkin_crosscheck", "mean_mass_g", "batch_median_t180",
                                        "e_reb_between_print_sd_mJ", "e_reb_design_mean_sd_mJ",
                                        "t180_within_session_sem_median", "drops_third_print"]},
                     indent=1, default=float))


if __name__ == "__main__":
    main()
