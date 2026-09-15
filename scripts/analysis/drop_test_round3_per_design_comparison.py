#!/usr/bin/env python3
"""Round-3 per-design comparison: drran (print 1) vs 2dran (print 2), PR #86 09-15.

Correction/extension of ``drop_test_2dran_batch_comparison.py``, which
predates the round-3 print key and treated the label correspondence as
unknown (fingerprint best-fit only, reported as candidates).  The BO
branch's ``bo/t3-prism-bo-round3-print-key.csv`` (PR #102, committed
09-06, per-cell photo confirmation) plus its ``bo/README.md`` settle it:

  the round-3 plate (trials 28-36) was printed TWICE by @ctrhjk —
  print 1 = ``drran1``-``drran9`` (print log 09-02, issue #98),
  print 2 = ``2dran1``-``2dran9`` (print log 09-05) — and both plates
  are labeled by build-plate cell under the same back-left ->
  front-right raster.

So ``drranN`` and ``2dranN`` are the *same design* on two different
printed articles: the per-label pairing IS the design pairing, the
batches are a print-to-print (not seat-to-seat) replication test, and
the fingerprint best-fit (which matched hop/broadband lookalikes across
designs) is superseded as a correspondence.  Keys are committed as
``params.json`` in both checkin folders and joined into the campaign
summaries/metrics.

Reads the two committed ``campaign_summary.csv`` + ``params.json`` and
emits, next to the 2dran campaign figures:

- per-design paired T180/T1000 with raw and batch-median-centered
  deltas, plus each side's known measurement pathologies (advisory seat
  gauge T1000/T180 >= 1.15, T-drift-watch flag, logged print defects);
- agreement of each print with the frozen round-3 model predictions
  (Spearman rank + RMS, all nine and excluding t32) — the direct test
  of "print 2 better represents the digital model";
- ``13_per_design_comparison.png`` + ``per_design_comparison.json``.
"""
from __future__ import annotations

import csv
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

OLD_DIR = DATA / "drran-checkin"
NEW_DIR = DATA / "2dran-checkin"
OUT = NEW_DIR / "figures"
C_OLD, C_NEW = "#1f77b4", "#ff7f0e"      # print 1 / print 2 (as in fig 12)
GAUGE_SUSPECT = 1.145                    # advisory seat gauge (CLAUDE.md; counts
                                         # 2dran2's 1.147, listed there as 1.15)
GAUGE_HEALTHY = 1.07                     # top of the healthy band on this mat

# Frozen round-3 predictions (PR #102 branch bo/t3-prism-bo-round3-
# predictions.csv, unchanged since 09-06; pred_t180_sd ~= 0.22-0.24 for
# all nine, so ranks are the meaningful comparison).  t32 was the
# round's best-predicted design.
PRED_T180 = {"t28": 1.0587, "t29": 1.0320, "t30": 1.0580, "t31": 1.0432,
             "t32": 1.0204, "t33": 1.0565, "t34": 1.0650, "t35": 1.0393,
             "t36": 1.0514}
BEST_PREDICTED = "t32"


def load(batch_dir: Path) -> dict:
    rows = {r["specimen"]: r for r in
            csv.DictReader(open(batch_dir / "figures" / "campaign_summary.csv"))}
    params = json.loads((batch_dir / "params.json").read_text())
    out = {}
    for lab, r in rows.items():
        t180, t1000 = float(r["t180_mean"]), float(r["t1000_mean"])
        out[lab] = {
            "t180": t180, "t180_sd": float(r["t180_sd"]), "t1000": t1000,
            "gauge": t1000 / t180, "drift_flag": r["t_drift_flag"] == "True",
            "mass_g": params[lab]["mass_g"], "defects": params[lab]["defects"],
            "spec": params[lab]["spec"], "plate_pos": params[lab]["plate_pos"],
        }
    return out


def pathologies(side: dict, batch: str) -> list[str]:
    p = []
    if side["gauge"] >= GAUGE_SUSPECT:
        p.append(f"{batch} seat gauge {side['gauge']:.2f} (suspect)")
    elif side["gauge"] > GAUGE_HEALTHY:
        p.append(f"{batch} seat gauge {side['gauge']:.2f} (above healthy band)")
    if side["drift_flag"]:
        p.append(f"{batch} T-drift flag")
    if side["defects"] != "none":
        p.append(f"{batch} print defects ({side['defects']})")
    return p


def agreement(meas: dict[str, float], drop: str | None = None) -> dict:
    specs = sorted(k for k in PRED_T180 if k != drop)
    pred = np.array([PRED_T180[s] for s in specs])
    m = np.array([meas[s] for s in specs])
    rho, p = spearmanr(pred, m)
    return {"n": len(specs), "spearman_rho": round(float(rho), 3),
            "spearman_p": round(float(p), 3),
            "rms_vs_pred": round(float(np.sqrt(np.mean((m - pred) ** 2))), 4)}


def main() -> None:
    old, new = load(OLD_DIR), load(NEW_DIR)
    labels = [f"drran{i}" for i in range(1, 10)]

    designs = []
    for lab in labels:
        n = lab.replace("drran", "")
        o, w = old[lab], new[f"2dran{n}"]
        assert o["spec"] == w["spec"] and o["plate_pos"] == w["plate_pos"]
        designs.append({
            "spec": o["spec"], "label_index": int(n), "plate_pos": o["plate_pos"],
            "pred_t180": PRED_T180[o["spec"]],
            "drran": {k: o[k] for k in ("t180", "t180_sd", "t1000", "gauge",
                                        "drift_flag", "mass_g", "defects")},
            "2dran": {k: w[k] for k in ("t180", "t180_sd", "t1000", "gauge",
                                        "drift_flag", "mass_g", "defects")},
            "delta_pct": round((w["t180"] / o["t180"] - 1) * 100, 2),
            "pathologies": pathologies(o, "drran") + pathologies(w, "2dran"),
        })

    deltas = np.array([d["delta_pct"] for d in designs])
    med_off = float(np.median(deltas))
    for d in designs:
        d["centered_delta_pct"] = round(d["delta_pct"] - med_off, 2)
    t_old = {d["spec"]: d["drran"]["t180"] for d in designs}
    t_new = {d["spec"]: d["2dran"]["t180"] for d in designs}
    clone = ["t28", "t30", "t33"]         # parameter clones (infill-only differences)
    clean = [d for d in designs if not d["pathologies"]]

    summary = {
        "provenance": {
            "key": "bo/t3-prism-bo-round3-print-key.csv @ PR #102 branch "
                   "(claude/issue-98-20260821-0103, committed 09-06, photo-"
                   "confirmed per plate cell); prints 1/2 logged on issue #98 "
                   "09-02 / 09-05; reprint stated by @me-madsen on PR #86 09-15",
            "predictions": "bo/t3-prism-bo-round3-predictions.csv (frozen)",
        },
        "designs": designs,
        "aggregate": {
            "median_delta_pct": round(med_off, 2),
            "n_positive": int((deltas > 0).sum()),
            "batch_median_t180": {"drran": round(float(np.median(list(t_old.values()))), 4),
                                  "2dran": round(float(np.median(list(t_new.values()))), 4)},
            "mean_mass_g": {"drran": round(float(np.mean([d["drran"]["mass_g"] for d in designs])), 2),
                            "2dran": round(float(np.mean([d["2dran"]["mass_g"] for d in designs])), 2)},
            "spearman_drran_vs_2dran": round(float(spearmanr(
                [t_old[d["spec"]] for d in designs],
                [t_new[d["spec"]] for d in designs])[0]), 3),
            "clean_pairs": {d["spec"]: d["delta_pct"] for d in clean},
            "max_abs_delta_clean_pct": max(abs(d["delta_pct"]) for d in clean) if clean else None,
            "clone_trio_spread_pct": {
                "drran": round((max(t_old[c] for c in clone) / min(t_old[c] for c in clone) - 1) * 100, 2),
                "2dran": round((max(t_new[c] for c in clone) / min(t_new[c] for c in clone) - 1) * 100, 2),
            },
        },
        "model_agreement": {
            "drran": {"all9": agreement(t_old), "excl_t32": agreement(t_old, drop="t32")},
            "2dran": {"all9": agreement(t_new), "excl_t32": agreement(t_new, drop="t32")},
            "t32_story": {"pred": PRED_T180["t32"], "best_predicted": True,
                          "drran7_t180": t_old["t32"], "2dran7_t180": t_new["t32"],
                          "note": "round 3's best-predicted design measured worst-"
                                  "on-record on the defective print 1 article "
                                  "(bubbled TPU tendons, gauge 2.35) and within "
                                  "0.8 % of prediction on the clean print 2"},
        },
    }
    (OUT / "per_design_comparison.json").write_text(json.dumps(summary, indent=1) + "\n")

    # ---- figure -----------------------------------------------------------
    order = sorted(designs, key=lambda d: d["pred_t180"])
    x = np.arange(len(order))
    fig, (ax, axd) = plt.subplots(
        2, 1, figsize=(10.5, 8.0), height_ratios=[2.1, 1.0], sharex=True)

    ylim = (0.965, 1.115)
    for i, d in enumerate(order):
        lo, hi = d["drran"]["t180"], d["2dran"]["t180"]
        clip_lo = min(lo, ylim[1] - 0.003)
        ax.plot([i, i], [min(clip_lo, hi), min(max(lo, hi), ylim[1] - 0.003)],
                color="#bbbbbb", lw=1.2, zorder=1)
        ax.plot(i, PRED_T180[d["spec"]], marker="_", ms=17, mew=2.2,
                color="#333333", zorder=2)
        ax.plot(i, clip_lo, "o", ms=8, color=C_OLD, zorder=3)
        ax.plot(i, hi, "s", ms=7.5, color=C_NEW, zorder=3)
        if lo > ylim[1]:                                   # drran7 = 1.251
            ax.annotate("drran 1.251 (off scale):\nbubbled TPU tendons,\nseat gauge 2.35",
                        (i + 0.06, ylim[1] - 0.003), xytext=(i + 0.38, ylim[1] - 0.006),
                        textcoords="data", fontsize=7.5, color=C_OLD,
                        ha="left", va="top",
                        arrowprops=dict(arrowstyle="->", color=C_OLD, lw=1))
        for side, key, col, dy in (("drran", "drran", C_OLD, -13), ("2dran", "2dran", C_NEW, 9)):
            g = d[key]["gauge"]
            if g >= 1.10 and d[key]["t180"] <= ylim[1]:
                yy = d[key]["t180"]
                dx = -46 if (key == "2dran" and yy > 1.085) else 6
                ax.annotate(f"gauge {g:.2f}", (i, yy), textcoords="offset points",
                            xytext=(dx, dy), fontsize=7, color=col)
    ax.set_ylim(*ylim)
    ax.set_ylabel("T = TOP/CH5 (CFC-180), stabilized mean")
    ax.axhline(1.0, color="#dddddd", lw=1)
    ax.grid(axis="y", color="#eeeeee", lw=0.7)
    ax.set_title("Round-3 designs, print 1 (drran, 09-02/03) vs print 2 (2dran, 09-05/08/09)\n"
                 "same label = same design (print key, PR #102 09-06) — sorted by model prediction",
                 fontsize=11)
    ax.plot([], [], "o", color=C_OLD, label="print 1 (drran)")
    ax.plot([], [], "s", color=C_NEW, label="print 2 (2dran)")
    ax.plot([], [], marker="_", ms=14, mew=2.2, ls="none", color="#333333",
            label="frozen round-3 prediction (±sd ≈ 0.23 not drawn)")
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)

    bars = axd.bar(x, [d["delta_pct"] for d in order], 0.55, color="#8c8c8c")
    axd.axhline(0, color="#666666", lw=1)
    axd.axhline(med_off, color="#666666", lw=1, ls="--")
    axd.annotate(f"median {med_off:+.1f} %", (0.55, med_off),
                 textcoords="offset points",
                 xytext=(0, 4), fontsize=7.5, color="#555555", ha="left")
    for i, d in enumerate(order):
        tags = []
        for p in d["pathologies"]:
            if "suspect" in p:
                tags.append(("P1" if "drran" in p else "P2") + " gauge")
            elif "drift" in p:
                tags.append(("P1" if "drran" in p else "P2") + " drift")
            elif "defects" in p:
                tags.append(("P1" if "drran" in p else "P2") + " defects")
        if tags:
            yv = d["delta_pct"]
            txt = "\n".join(dict.fromkeys(tags))
            if yv < -5:                       # deep negative bar: tag above zero
                axd.annotate(txt, (i, 0), textcoords="offset points",
                             xytext=(0, 8), fontsize=6.8, ha="center", color="#333333")
            else:
                axd.annotate(txt, (i, max(yv, 0)), textcoords="offset points",
                             xytext=(0, 6), fontsize=6.8, ha="center", color="#333333")
    axd.set_ylim(-20.5, 9.5)
    axd.set_ylabel("print 2 − print 1 (%)")
    axd.set_xticks(x)
    axd.set_xticklabels([f"{d['spec']}\n#{d['label_index']}" for d in order], fontsize=8.5)
    axd.set_xlabel("design (trial · shared label index), left → right by predicted T")
    axd.grid(axis="y", color="#eeeeee", lw=0.7)

    fig.tight_layout()
    fig.savefig(OUT / "13_per_design_comparison.png", dpi=150)
    print(json.dumps(summary["aggregate"], indent=1))
    print(json.dumps(summary["model_agreement"], indent=1))


if __name__ == "__main__":
    main()
