#!/usr/bin/env python3
"""Round-3 three-print comparison: drran / 2dran / dran3 (PR #86, 10-03).

The round-3 plate (trials 28-36) has now been printed three times by the
lab and each print dropped 9 x 20 at the standing SOP (60 in,
arrangement B):

  print 1 = ``drran1``-``drran9``  (printed 09-02, dropped 09-02/03)
  print 2 = ``2dran1``-``2dran9``  (printed 09-05, dropped 09-05/08/09)
  print 3 = ``dran31``-``dran39``  (printed 09-28, dropped 09-28/29, 10-02)

All three are labeled by build-plate cell, so label index N is the same
design in every print (keys: ``params.json`` in each checkin folder; print
3 per PR #102's relabel ``e9f5e2d``, where ``3dranN`` == ``dran3N``).
This extends ``drop_test_round3_per_design_comparison.py`` (two prints)
to three, which turns each design's pair into a triple and lets every
measurement be checked against the median of its two siblings.

Reads the three committed ``campaign_summary.csv`` + ``params.json`` and
emits, next to the dran3 campaign figures:

- per-design T180 for the three prints, the design median, and each
  cell's deviation from that three-print median;
- a measurement-health screen per cell (advisory seat gauge
  T1000/T180 >= 1.145, T-drift-watch flag) and a two-way additive fit
  (design + print offset) on the screened cells: print offsets, design
  means and the residual article+seat sd that the replicate-study plan
  (PR #102, ``bo/t3-prism-replicate-study-plan.md``) pre-registered as
  ~0.013 from the two-print data;
- rank agreement between prints, and of each print / the screened
  design means with the frozen round-3 predictions;
- whether the seat gauge separates the outliers (gauge vs deviation);
- ``12_three_print_comparison.png`` + ``three_print_comparison.json``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402
from drop_test_round3_per_design_comparison import (  # noqa: E402
    GAUGE_HEALTHY, GAUGE_SUSPECT, PRED_T180, agreement, load, pathologies)

OUT = DATA / "dran3-checkin" / "figures"
PRINTS = (("drran", "drran{}", DATA / "drran-checkin", "print 1 (drran, 09-02/03)", "#1f77b4", "o"),
          ("2dran", "2dran{}", DATA / "2dran-checkin", "print 2 (2dran, 09-05/08/09)", "#ff7f0e", "s"),
          ("dran3", "dran3{}", DATA / "dran3-checkin", "print 3 (dran3, 09-28/29, 10-02)", "#2ca02c", "D"))
ARTICLE_SD_PREREG = 0.013   # replicate-study plan, from the drran/2dran pairs


def screened(cell: dict) -> bool:
    """Measurement-health screen: healthy-enough seat and no drift flag."""
    return cell["gauge"] < GAUGE_SUSPECT and not cell["drift_flag"]


def additive_fit(cells: list[tuple[int, int, float]], n_d: int, n_p: int) -> dict:
    """Least-squares design + print-offset fit (print 1 offset fixed at 0)."""
    X, y = [], []
    for d, p, v in cells:
        row = np.zeros(n_d + n_p - 1)
        row[d] = 1.0
        if p > 0:
            row[n_d + p - 1] = 1.0
        X.append(row)
        y.append(v)
    X, y = np.array(X), np.array(y)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    return {"design_mean": beta[:n_d], "print_offset": np.r_[0.0, beta[n_d:]],
            "resid": resid, "dof": int(dof),
            "resid_sd": float(np.sqrt(resid @ resid / dof)) if dof > 0 else None}


def main() -> None:
    data = {key: load(folder) for key, _, folder, *_ in PRINTS}
    specs = [data["drran"][f"drran{n}"]["spec"] for n in range(1, 10)]

    designs = []
    for n, spec in zip(range(1, 10), specs):
        cells = {}
        for key, fmt, *_ in PRINTS:
            c = data[key][fmt.format(n)]
            assert c["spec"] == spec, (key, n)
            cells[key] = {k: c[k] for k in ("t180", "t180_sd", "t1000", "gauge",
                                            "drift_flag", "mass_g", "defects")}
            cells[key]["label"] = fmt.format(n)
            cells[key]["screened"] = screened(c)
            cells[key]["pathologies"] = pathologies(c, key)
        vals = {k: cells[k]["t180"] for k in cells}
        med = float(np.median(list(vals.values())))
        for k in cells:
            # vs the three-print median (the middle print): an outlier sibling
            # cannot drag a clean cell's deviation, as the mean of the other
            # two would (2dran7 would read -10 % against drran7's 1.251)
            cells[k]["dev_from_median_pct"] = round((vals[k] / med - 1) * 100, 2)
        ok = [cells[k]["t180"] for k in cells if cells[k]["screened"]]
        designs.append({
            "spec": spec, "label_index": n, "pred_t180": PRED_T180[spec],
            "prints": cells,
            "median_t180": round(float(np.median(list(vals.values()))), 4),
            "screened_mean_t180": round(float(np.mean(ok)), 4) if ok else None,
            "n_screened": len(ok),
            "range_pct": round((max(vals.values()) / min(vals.values()) - 1) * 100, 2),
        })

    keys = [p[0] for p in PRINTS]
    # -- two-way additive fit: screened cells vs all cells ------------------
    def fit(select) -> dict:
        cells = [(i, j, d["prints"][k]["t180"]) for i, d in enumerate(designs)
                 for j, k in enumerate(keys) if select(d["prints"][k])]
        f = additive_fit(cells, len(designs), len(keys))
        return {"n_cells": len(cells), "dof": f["dof"],
                "resid_sd": round(f["resid_sd"], 4),
                "print_offset": {k: round(float(v), 4) for k, v in zip(keys, f["print_offset"])},
                "design_mean": {d["spec"]: round(float(v), 4)
                                for d, v in zip(designs, f["design_mean"])},
                "max_abs_resid": round(float(np.abs(f["resid"]).max()), 4)}

    fit_screened = fit(lambda c: c["screened"])
    fit_all = fit(lambda c: True)
    dm = fit_screened["design_mean"]
    between_sd = float(np.std(list(dm.values()), ddof=1))

    # -- rank agreement ------------------------------------------------------
    t = {k: {d["spec"]: d["prints"][k]["t180"] for d in designs} for k in keys}
    pair_rho = {}
    for a, b in (("drran", "2dran"), ("drran", "dran3"), ("2dran", "dran3")):
        rho, p = spearmanr([t[a][s] for s in specs], [t[b][s] for s in specs])
        pair_rho[f"{a} vs {b}"] = {"rho": round(float(rho), 3), "p": round(float(p), 3)}

    # model agreement: each print (all nine; and with that print's unscreened
    # cells dropped), plus the screened additive-fit design means
    def agree_screened(k):
        keep = {d["spec"]: d["prints"][k]["t180"] for d in designs if d["prints"][k]["screened"]}
        sp = sorted(keep)
        pred = np.array([PRED_T180[s] for s in sp])
        m = np.array([keep[s] for s in sp])
        rho, p = spearmanr(pred, m)
        return {"n": len(sp), "spearman_rho": round(float(rho), 3),
                "spearman_p": round(float(p), 3),
                "rms_vs_pred": round(float(np.sqrt(np.mean((m - pred) ** 2))), 4)}

    model = {k: {"all9": agreement(t[k]), "screened": agree_screened(k)} for k in keys}
    model["screened_design_means"] = agreement(dm)
    model["three_print_median"] = agreement({d["spec"]: d["median_t180"] for d in designs})

    # -- seat gauge vs deviation from the three-print median -----------------
    gx = np.array([d["prints"][k]["gauge"] for d in designs for k in keys])
    gy = np.array([d["prints"][k]["dev_from_median_pct"] for d in designs for k in keys])
    g_rho, g_p = spearmanr(gx, gy)
    tripped = [{"label": d["prints"][k]["label"], "spec": d["spec"],
                "gauge": round(d["prints"][k]["gauge"], 3),
                "t180": round(d["prints"][k]["t180"], 4),
                "dev_from_median_pct": d["prints"][k]["dev_from_median_pct"],
                "is_design_max": d["prints"][k]["t180"] == max(
                    d["prints"][o]["t180"] for o in keys)}
               for d in designs for k in keys if d["prints"][k]["gauge"] >= GAUGE_SUSPECT]
    healthy_dev = [abs(d["prints"][k]["dev_from_median_pct"]) for d in designs
                   for k in keys if d["prints"][k]["gauge"] <= GAUGE_HEALTHY]

    by = {d["spec"]: d for d in designs}
    summary = {
        "provenance": {
            "keys": "params.json in drran-/2dran-/dran3-checkin (round-3 print key, "
                    "PR #102 branch; dran3N per relabel e9f5e2d, masses from the "
                    "09-28 print log on issue #98)",
            "predictions": "bo/t3-prism-bo-round3-predictions.csv (frozen 09-06)",
            "screen": f"gauge T1000/T180 < {GAUGE_SUSPECT} and no T-drift flag",
        },
        "designs": designs,
        "aggregate": {
            "batch_median_t180": {k: round(float(np.median(list(t[k].values()))), 4) for k in keys},
            "mean_mass_g": {k: round(float(np.mean([d["prints"][k]["mass_g"] for d in designs])), 2)
                            for k in keys},
            "n_screened_cells": fit_screened["n_cells"],
            "additive_fit_screened": fit_screened,
            "additive_fit_all27": fit_all,
            "between_design_sd_screened_means": round(between_sd, 4),
            "article_sd_prereg": ARTICLE_SD_PREREG,
            "rank_agreement_between_prints": pair_rho,
        },
        "model_agreement": model,
        "seat_gauge": {
            "spearman_gauge_vs_dev": {"rho": round(float(g_rho), 3), "p": float(f"{g_p:.3g}")},
            "tripped_cells": tripped,
            "healthy_gauge_cells": {"n": len(healthy_dev),
                                    "max_abs_dev_pct": round(max(healthy_dev), 2),
                                    "median_abs_dev_pct": round(float(np.median(healthy_dev)), 2)},
        },
        "standing_checks": {
            "t36_2dran1_reads_high": {
                "2dran1": by["t36"]["prints"]["2dran"]["t180"],
                "healthy_siblings": {k: by["t36"]["prints"][k]["t180"] for k in ("drran", "dran3")},
                "2dran1_vs_healthy_mean_pct": round(
                    (by["t36"]["prints"]["2dran"]["t180"]
                     / np.mean([by["t36"]["prints"][k]["t180"] for k in ("drran", "dran3")]) - 1) * 100, 2)},
            "t32_drran7_artifact": {k: by["t32"]["prints"][k]["t180"] for k in keys}
                                   | {"pred": PRED_T180["t32"]},
            "t35_lowest": {k: by["t35"]["prints"][k]["t180"] for k in keys}
                          | {"lowest_in_every_print": all(
                              min(t[k], key=t[k].get) == "t35" for k in keys)},
        },
    }
    (OUT / "three_print_comparison.json").write_text(json.dumps(summary, indent=1) + "\n")
    make_figure(designs, keys, summary)
    print(json.dumps(summary["aggregate"], indent=1))
    print(json.dumps(summary["model_agreement"], indent=1))
    print(json.dumps(summary["seat_gauge"], indent=1))
    print(json.dumps(summary["standing_checks"], indent=1))


def make_figure(designs, keys, summary) -> None:
    meta = {p[0]: p for p in PRINTS}
    order = sorted(designs, key=lambda d: d["pred_t180"])
    fig, (ax, axg) = plt.subplots(1, 2, figsize=(14.5, 6.0), width_ratios=[1.75, 1.0])

    ylim = (0.965, 1.105)
    off = {"drran": -0.18, "2dran": 0.0, "dran3": 0.18}
    for i, d in enumerate(order):
        ax.plot([i - 0.32, i + 0.32], [d["median_t180"]] * 2, color="#999999", lw=1.2, zorder=1)
        ax.plot(i, d["pred_t180"], marker="_", ms=20, mew=2.4, color="#333333", zorder=2)
        for k in keys:
            c = d["prints"][k]
            _, _, _, _, col, mk = meta[k]
            y = min(c["t180"], ylim[1] - 0.004)
            face = col if c["screened"] else "white"
            ax.plot(i + off[k], y, mk, ms=8, mfc=face, mec=col, mew=1.6, zorder=3)
            if c["t180"] > ylim[1]:
                right = i < len(order) / 2          # keep the callout inside the axes
                ax.annotate(f"{c['label']} {c['t180']:.3f}\n(off scale, gauge {c['gauge']:.2f})",
                            (i + off[k], ylim[1] - 0.004),
                            xytext=(i + off[k] + (0.3 if right else -0.3), ylim[1] - 0.008),
                            textcoords="data", fontsize=7.5, color=col,
                            ha="left" if right else "right", va="top",
                            arrowprops=dict(arrowstyle="->", color=col, lw=1))
            elif not c["screened"]:
                why = f"gauge {c['gauge']:.2f}" if c["gauge"] >= GAUGE_SUSPECT else "drift flag"
                ax.annotate(why, (i + off[k], c["t180"]), textcoords="offset points",
                            xytext=(5, -3), fontsize=6.8, color=col)
    ax.axhline(1.0, color="#dddddd", lw=1)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([f"{d['spec']}\n#{d['label_index']}" for d in order], fontsize=8.5)
    ax.set_xlabel("design (trial · shared label index), left → right by predicted T")
    ax.set_ylabel("T = TOP/CH5 (CFC-180), stabilized mean")
    ax.grid(axis="y", color="#eeeeee", lw=0.7)
    for k in keys:
        _, _, _, lab, col, mk = meta[k]
        ax.plot([], [], mk, color=col, ms=7, label=lab)
    ax.plot([], [], "o", mfc="white", mec="#555555", ms=7, label="open = fails health screen")
    ax.plot([], [], color="#999999", lw=1.2, label="three-print median")
    ax.plot([], [], marker="_", ms=14, mew=2.2, ls="none", color="#333333",
            label="frozen round-3 prediction")
    ax.legend(loc="lower right", fontsize=7.8, frameon=False, ncol=2)
    agg = summary["aggregate"]["additive_fit_screened"]
    ax.set_title("Round-3 designs, three prints — same label index = same design\n"
                 f"screened fit: article+seat sd {agg['resid_sd']:.4f} (dof {agg['dof']}), "
                 f"print offsets {agg['print_offset']['2dran']:+.4f} / "
                 f"{agg['print_offset']['dran3']:+.4f} vs print 1", fontsize=10.5)

    for d in designs:
        for k in keys:
            c = d["prints"][k]
            _, _, _, _, col, mk = meta[k]
            axg.plot(c["gauge"], c["dev_from_median_pct"], mk, ms=7,
                     mfc=col if c["screened"] else "white", mec=col, mew=1.5)
            if c["gauge"] >= GAUGE_SUSPECT or abs(c["dev_from_median_pct"]) > 3:
                axg.annotate(c["label"], (c["gauge"], c["dev_from_median_pct"]),
                             textcoords="offset points", xytext=(6, -3), fontsize=7.5, color=col)
    axg.axvline(GAUGE_SUSPECT, color="#d62728", lw=1, ls="--")
    axg.axvspan(0.95, GAUGE_HEALTHY, color="tab:green", alpha=0.08, lw=0)
    axg.axhline(0, color="#999999", lw=1)
    axg.set_xscale("log")
    axg.set_xticks([1.0, 1.1, 1.2, 1.5, 2.0, 2.5])
    axg.set_xticklabels(["1.0", "1.1", "1.2", "1.5", "2.0", "2.5"])
    axg.set_xlabel("advisory seat gauge T1000/T180 (log)")
    axg.set_ylabel("T180 vs the design's three-print median (%)")
    sg = summary["seat_gauge"]
    axg.set_title(f"Seat gauge vs outlier size (27 sessions)\nSpearman ρ = "
                  f"{sg['spearman_gauge_vs_dev']['rho']:+.2f}; dashed = suspect threshold "
                  f"{GAUGE_SUSPECT}", fontsize=10.5)
    axg.grid(color="#eeeeee", lw=0.7)

    fig.tight_layout()
    fig.savefig(OUT / "12_three_print_comparison.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
