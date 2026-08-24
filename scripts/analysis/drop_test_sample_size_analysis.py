#!/usr/bin/env python3
"""How many drops per specimen? Cross-dataset variance + sample-size analysis.

@me-madsen asked (PR #82 comment 5026945744, re-asked on PR #86 with the
60 in / 5 felts validation, the 5-vs-10-in comparison, and the PR #67 datasets
as explicit references):

  1. Recommend a minimum number of drop tests per specimen to get accurate data.
  2. How much variance have we had per specimen being tested so far?
  3. How long would each set of tests take, given ~42 s/drop at 60 in with
     automatic dropping?

Rather than re-process the ~1,485 committed CSVs, this script aggregates the
**within-specimen coefficients of variation (CV)** that the per-dataset analyses
already emitted, then turns that observed scatter into concrete sample-size and
timing recommendations.

Two kinds of source are read:

  * Large repeatability campaigns that emit ``stabilized_ols`` (mean + CV over the
    post-burn-in window) and ``burn_in_drops`` in their ``figures/*_metrics.json``
    (100drops, 5in-100drops, 200drops, drift-calibration, drift-calibration2,
    30drops-real, ch4-trigger). The felt-sheet sweep emits per-condition CV
    (five drops each) under ``conditions``.
  * The n = 5 mount-validation series (input-output, key-mounted,
    key-mounted-wax, burn-in-wax) whose published CVs live in the docs; those
    values are tabulated here with a citation to the committed writeup so the
    recommendation is traceable end to end.

The "go-forward" objective for the BO campaign is the **top-vertex tri-axis
output CFC-180 peak** (and the derived transmissibility T = output/input); the
base-plate single-axis / input channel is reported separately because it is the
noisier, saturation-prone channel (see the felt-sheet / drop-test-sensors notes).

Sample size is computed two ways:

  * **Precision of the per-specimen mean** — smallest n whose 95% t-CI half-width
    is within a target *relative* margin of error (n = (t_{n-1}*CV / MoE)^2).
  * **Two-design discrimination** — n per specimen to resolve a given relative
    difference between two designs at 80% power (two-sample, alpha = 0.05).

Emits ``figures/sample_size_metrics.json`` consumed by
``docs/drop-test-sample-size-analysis.md``.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
DROP = REPO / "data" / "drop-tests"
FIG = DROP / "sample-size" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# @me-madsen's measured auto-drop cadence at 60 in.
SEC_PER_DROP_60IN = 42.0
# Median measured auto-drop cadence at the lower heights (10-13 in), from the
# committed campaign metrics (cadence_s.median: 12-20 s) — used for context only.
SEC_PER_DROP_LOWH = 16.0

# ---------------------------------------------------------------------------
# 1. Within-specimen CV of the *go-forward* output metric, read from the
#    committed large-campaign metrics JSONs (stabilized_ols) + felt-sheet.
# ---------------------------------------------------------------------------
# Each entry: (dataset, path, output_key, input_key, T_key). Keys index into
# stabilized_ols; a value of None means that channel was not present in the run.
CAMPAIGNS = [
    ("100drops", "100drops/figures/100drops_metrics.json",
     "TOP output", "CH5 plate", "T TOP/CH5"),
    ("5in-100drops", "5in-100drops/figures/5in_100drops_metrics.json",
     "TOP output", "CH5 plate", "T TOP/CH5"),
    ("200drops", "200drops/figures/200drops_metrics.json",
     "TOP output", "CH5 plate", "T TOP/CH5"),
    ("drift-calibration", "drift-calibration/figures/drift_calibration_metrics.json",
     "output", "input", "T"),
    ("drift-calibration2", "drift-calibration2/figures/drift_calibration2_metrics.json",
     "output", "input", "T"),
    # 30drops-real had a suspect CH5 (CV ~29%); its reliable input is the bottom
    # tri-axis, so the BOT pairing is reported for this run.
    ("30drops-real", "30drops-real/figures/30drops_real_metrics.json",
     "TOP output", "BOT input", "T* TOP/BOT"),
    ("ch4-trigger", "ch4-trigger/figures/ch4_trigger_metrics.json",
     "TOP output", "CH5 plate", "T TOP/CH5"),
]


def read_60in_5felts() -> list[dict]:
    """The 60 in / 5 felts validation runs (PR #86): ~100 drops per specimen."""
    d = json.loads((DROP / "60in-5felts-validation/figures/60in_5felts_metrics.json")
                   .read_text())
    rows = []
    for sid, s in d["specimens"].items():
        so = s["stabilized_ols"]
        rows.append({
            "dataset": f"60in-5felts {sid}",
            "n_stable": so["TOP output"]["n"],
            "burn_in_drops": s["burn_in_drops"],
            "output_cv": so["TOP output"]["cv"],
            "input_cv": so["CH5 input"]["cv"],
            "T_cv": so["T TOP/CH5"]["cv"],
            "cadence_median_s": s["cadence_s"]["median"],
        })
    return rows


def read_5vs10() -> list[dict]:
    """The 5-vs-10-in comparison (PR #82 comment 4973983998): 30 drops/height."""
    d = json.loads((DROP / "5vs10/figures/5vs10_metrics.json").read_text())
    rows = []
    for g, gd in d["groups"].items():
        m = gd["cfc180"]
        rows.append({
            "dataset": f"5vs10 {g}",
            "n_stable": m["TOP output"]["n"],
            "burn_in_drops": None,
            "output_cv": m["TOP output"]["cv"],
            "input_cv": m["CH5 input"]["cv"],
            "T_cv": m["T = TOP/CH5"]["cv"],
            "cadence_median_s": gd["cadence_s_median"],
        })
    return rows


def read_campaigns() -> list[dict]:
    rows = []
    for name, rel, out_k, in_k, t_k in CAMPAIGNS:
        d = json.loads((DROP / rel).read_text())
        so = d.get("stabilized_ols", {})
        out = so.get(out_k, {})
        rows.append({
            "dataset": name,
            "n_stable": out.get("n"),
            "burn_in_drops": d.get("burn_in_drops"),
            "output_cv": out.get("cv"),
            "input_cv": (so.get(in_k) or {}).get("cv"),
            "T_cv": (so.get(t_k) or {}).get("cv"),
            "cadence_median_s": (d.get("cadence_s") or {}).get("median"),
        })
    return rows


def read_felt() -> dict:
    d = json.loads((DROP / "felt-sheet/figures/felt_sheet_metrics.json").read_text())
    top = [c["top_180_g"]["cv"] for c in d["conditions"]]
    ch5 = [c["ch5_180_g"]["cv"] for c in d["conditions"]]
    return {"dataset": "felt-sheet (9 conditions x 5)",
            "output_cv_range": [min(top), max(top)],
            "output_cv_median": float(np.median(top)),
            "input_cv_range": [min(ch5), max(ch5)]}


# n = 5 mount-validation series — CVs as published in the committed writeups.
# (input CH5 CFC-180, output tri-axis CFC-180, T = OUT/IN); see citations.
N5_SERIES = [
    # dataset, mount, input_cv, output_cv, T_cv, doc
    ("input-output (4 geom x 5)", "hot-glue vertex", 1.3, 3.5, 4.6,
     "docs/drop-test-input-output-analysis.md (worst-specimen n0jdwk)"),
    ("key-mounted (5)", "key-seat", 2.0, 1.3, 2.4,
     "docs/drop-test-key-mounted-analysis.md"),
    ("key-mounted-wax (5)", "key-seat + wax", 0.5, 0.6, 1.1,
     "docs/drop-test-key-mounted-wax-analysis.md"),
    ("burn-in-wax (5)", "key-seat + wax", 0.47, 0.31, 1.07,
     "docs/drop-test-burn-in-wax-analysis.md (recorded phase)"),
]


# ---------------------------------------------------------------------------
# 2. Sample-size math.
# ---------------------------------------------------------------------------
def n_for_moe(cv_pct: float, moe_pct: float, conf: float = 0.95, nmax: int = 500):
    """Smallest n (>=2) whose 95% t-CI half-width on the mean is <= moe (relative)."""
    for n in range(2, nmax):
        t = stats.t.ppf(1 - (1 - conf) / 2, n - 1)
        if t * cv_pct / np.sqrt(n) <= moe_pct:
            return n
    return None


def n_two_sample(cv_pct: float, delta_rel_pct: float,
                 power: float = 0.80, alpha: float = 0.05) -> int:
    """n per group to resolve a relative difference delta between two designs."""
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return int(np.ceil(2 * (z * cv_pct / delta_rel_pct) ** 2))


def main() -> None:
    campaigns = read_campaigns() + read_60in_5felts() + read_5vs10()
    felt = read_felt()

    # Pool the go-forward output CVs from every controlled repeat-drop dataset.
    out_cvs = [r["output_cv"] for r in campaigns if r["output_cv"]]
    out_cvs += [felt["output_cv_median"]]
    out_cvs += [s[3] for s in N5_SERIES]
    out_cvs = sorted(out_cvs)
    t_cvs = sorted([r["T_cv"] for r in campaigns if r["T_cv"]] +
                   [s[4] for s in N5_SERIES])

    # Representative CVs: median and a conservative (90th-pct) go-forward CV.
    cv_typ = float(np.median(out_cvs))
    cv_cons = float(np.percentile(out_cvs, 90))
    cv_T = float(np.median(t_cvs))

    moes = [1.0, 2.0, 3.0]
    precision = {}
    for cv in [0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0, 6.5]:
        precision[cv] = {f"moe_{m}pct": n_for_moe(cv, m) for m in moes}

    deltas = [5.0, 10.0, 20.0]
    discrimination = {}
    for cv in [1.5, 2.5, 3.5, 6.5]:
        discrimination[cv] = {f"delta_{int(d)}pct": n_two_sample(cv, d)
                              for d in deltas}

    # Recommendation: 2 burn-in (discarded) + 5 recorded baseline; 10 recorded
    # for noisier metrics/mounts.
    plans = {}
    for label, burn, rec in [("minimal (recorded only)", 0, 5),
                             ("baseline", 2, 5),
                             ("conservative", 2, 10)]:
        total = burn + rec
        plans[label] = {
            "burn_in": burn, "recorded": rec, "total": total,
            "min_60in": round(total * SEC_PER_DROP_60IN / 60.0, 1),
            "min_lowh": round(total * SEC_PER_DROP_LOWH / 60.0, 1),
        }

    # Batch timing at 60 in for a few campaign sizes (baseline 7-drop set).
    batch = {}
    for ndes in [10, 20, 48, 96]:
        for total in (7, 12):
            secs = ndes * total * SEC_PER_DROP_60IN
            batch[f"{ndes}designs_x{total}drops"] = round(secs / 3600.0, 2)

    metrics = {
        "ask": "PR #82 comment 5026945744, re-asked PR #86 2026-07-21 (@me-madsen)",
        "sec_per_drop_60in": SEC_PER_DROP_60IN,
        "sec_per_drop_lowh_context": SEC_PER_DROP_LOWH,
        "campaigns": campaigns,
        "felt_sheet": felt,
        "n5_series": [
            {"dataset": s[0], "mount": s[1], "input_cv": s[2],
             "output_cv": s[3], "T_cv": s[4], "source": s[5]}
            for s in N5_SERIES
        ],
        "output_cv_pooled": {
            "values_sorted": out_cvs,
            "median": cv_typ,
            "p90": cv_cons,
            "min": out_cvs[0],
            "max": out_cvs[-1],
        },
        "T_cv_pooled": {"values_sorted": t_cvs, "median": cv_T},
        "precision_n": precision,
        "discrimination_n": discrimination,
        "plans": plans,
        "batch_hours_60in": batch,
        "recommendation": {
            "burn_in_discarded": "2 (hot-glue mounts drift up to 5-10; the wax "
                                 "key-seat mount showed ~0 significant burn-in)",
            "recorded_min": 5,
            "recorded_conservative": 10,
            "rationale": (
                f"Go-forward output CV is {out_cvs[0]:.2f}-{out_cvs[-1]:.2f}% "
                f"(median {cv_typ:.2f}%). At the median CV, 5 recorded drops give "
                f"a 95% CI half-width of ~{stats.t.ppf(0.975,4)*cv_typ/np.sqrt(5):.1f}% "
                "on the per-specimen mean, and easily resolve the >=10% "
                "differences seen between designs. Use 10 recorded drops when the "
                "metric is the noisier input/plate channel or transmissibility on a "
                "hot-glue mount (CV up to ~6.5%)."
            ),
        },
    }

    (FIG / "sample_size_metrics.json").write_text(json.dumps(metrics, indent=2))

    # ---- Figure 1: observed within-specimen CV, output vs input/T -----------
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    labels, out_v, in_v, t_v = [], [], [], []
    for r in campaigns:
        labels.append(r["dataset"])
        out_v.append(r["output_cv"] or np.nan)
        in_v.append(r["input_cv"] or np.nan)
        t_v.append(r["T_cv"] or np.nan)
    for s in N5_SERIES:
        labels.append(s[0].split(" (")[0])
        out_v.append(s[3]); in_v.append(s[2]); t_v.append(s[4])
    x = np.arange(len(labels))
    w = 0.27
    ax.bar(x - w, out_v, w, label="output (go-forward)", color="#2a7")
    ax.bar(x, in_v, w, label="input / plate", color="#c73")
    ax.bar(x + w, t_v, w, label="T = out/in", color="#37c")
    ax.axhline(2.0, ls="--", lw=0.9, color="0.4")
    ax.text(len(labels) - 0.5, 2.1, "2% CV", ha="right", va="bottom", color="0.4")
    ax.set_ylabel("within-specimen CV (%)")
    ax.set_title("Repeat-drop variance per specimen (committed datasets)")
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "01_within_specimen_cv.png", dpi=130)
    plt.close(fig)

    # ---- Figure 2: n vs precision, with recorded=5/10 markers ---------------
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ns = np.arange(2, 21)
    for cv, c in [(1.0, "#2a7"), (2.0, "#37c"), (2.5, "#93a"), (3.5, "#c73")]:
        half = np.array([stats.t.ppf(0.975, n - 1) * cv / np.sqrt(n) for n in ns])
        ax.plot(ns, half, marker="o", ms=3, color=c, label=f"CV = {cv:.1f}%")
    for n in (5, 10):
        ax.axvline(n, ls=":", lw=0.9, color="0.5")
    ax.axhline(2.0, ls="--", lw=0.9, color="0.4")
    ax.set_xlabel("recorded drops per specimen (n)")
    ax.set_ylabel("95% CI half-width on the mean (relative %)")
    ax.set_title("Precision of the per-specimen mean vs number of drops")
    ax.set_ylim(0, 6)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "02_precision_vs_n.png", dpi=130)
    plt.close(fig)

    # ---- console summary ----------------------------------------------------
    print(f"go-forward output CV: {out_cvs[0]:.2f}-{out_cvs[-1]:.2f}% "
          f"(median {cv_typ:.2f}%, p90 {cv_cons:.2f}%)")
    print(f"transmissibility CV: median {cv_T:.2f}%")
    print("plans:", json.dumps(plans, indent=1))
    print("batch hours @60in:", json.dumps(batch))


if __name__ == "__main__":
    main()
