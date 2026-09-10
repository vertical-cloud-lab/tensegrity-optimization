#!/usr/bin/env python3
"""2dran1..2dran9 vs drran1..drran9 — cross-batch comparison (PR #86, 09-10).

The 2dran batch (recorded 09-05/09-08/09-09) follows the drran batch
(09-02/09-03) by 2-6 days at identical settings (60 in, arrangement B,
SOP capture).  Neither batch's label -> design key is in the repo, and the
labels are evidently re-randomized between batches (no 2dran session
reproduces drran7's T180 = 1.25 signature, and the specimen-hop constants
re-shuffle), so this script does two things with the committed
``campaign_metrics.json`` of both batches:

1. batch-level comparison (T levels, inputs, dv) plus robust per-session
   hop signatures — the secondary-burst detector's argmax flips between
   landings when a specimen double-bounces, so the *first*-landing time is
   estimated as the 25th percentile of the per-drop ``t_second_ms`` series,
   censored-flagged when it sits on the 15 ms search-window floor;
2. a best-fit drran <-> 2dran assignment (Hungarian, standardized
   [log t_hop, T180, log T1000] distance) with per-pair runner-up margins,
   reported as *candidates only* — the margins quantify how far the DAQ
   fingerprints alone can or cannot certify a correspondence.

Outputs ``12_batch_comparison.png`` + ``batch_comparison.json`` next to the
2dran campaign figures.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402

NEW = DATA / "2dran-checkin" / "figures"
OLD = DATA / "drran-checkin" / "figures"
HOP_FLOOR_MS = 15.05        # secondary-burst search starts at 15 ms
HOP_CAP_MS = 69.5           # ... and ends at 70 ms
C_OLD, C_NEW = "#1f77b4", "#ff7f0e"


def hop_first(rows: list[dict]) -> dict:
    """Robust first-landing time from a per-drop t_second series."""
    t = np.array([r["t_second_ms"] for r in rows if np.isfinite(r.get("t_second_ms", np.nan))])
    q25 = float(np.percentile(t, 25))
    return {"t_hop_ms": q25,
            "censored_low": bool(np.mean(t <= HOP_FLOOR_MS) >= 1 / 3),
            "at_cap": bool(np.mean(t >= HOP_CAP_MS) >= 1 / 3),
            "bimodal": bool(np.ptp(t) > 0.8 * q25 and len(t) > 4),
            "spread_ms": float(np.ptp(t))}


def features(metrics_path: Path) -> dict:
    d = json.loads(metrics_path.read_text())
    out = {}
    for s, sp in d["specimens"].items():
        rows = sp["rows"]
        m = sp["metrics"]
        out[s] = {"t180": m["t180"]["mean"], "t180_cv": m["t180"]["cv_pct"],
                  "t180_sd": m["t180"]["sd"],
                  "t1000": m["t1000"]["mean"], "in180": m["in_180_g"]["mean"],
                  "dv": m["in_dv_ms"]["mean"],
                  "e_reb": m["e_rebound"]["mean"],
                  "width": m["in_width_ms"]["mean"],
                  "ch4_fs_pct": 100 * sp["worst_frac_fs"]["CH4"],
                  "flagged": sp["t_drift_watch"]["flagged"],
                  **hop_first(rows)}
    return out


def assignment(old: dict, new: dict) -> dict:
    """Hungarian best-fit old<->new with per-pair runner-up margins."""
    o_ids, n_ids = sorted(old), sorted(new)
    feats = np.array([[np.log(v["t_hop_ms"]), v["t180"], np.log(v["t1000"])]
                      for v in [*(old[s] for s in o_ids), *(new[s] for s in n_ids)]])
    z = (feats - feats.mean(0)) / feats.std(0)
    zo, zn = z[:len(o_ids)], z[len(o_ids):]
    w = np.array([1.0, 0.7, 0.7])       # hop first; T levels session-shiftable
    cost = np.abs(zo[:, None, :] - zn[None, :, :]) @ w
    ri, ci = linear_sum_assignment(cost)
    pairs = {}
    for i, j in zip(ri, ci):
        alt = np.sort(cost[i])
        pairs[o_ids[i]] = {"match": n_ids[j], "cost": float(cost[i, j]),
                           "runner_up_margin": float(alt[1] - alt[0])
                           if cost[i, j] == alt[0] else 0.0}
    return {"pairs": pairs, "total_cost": float(cost[ri, ci].sum()),
            "identity_cost": float(np.trace(cost)),
            "note": "candidates only — standardized [log t_hop, T180, log T1000] "
                    "distance; margins < ~1 z-unit are not decisive"}


def main():
    old, new = features(OLD / "campaign_metrics.json"), features(NEW / "campaign_metrics.json")
    asg = assignment(old, new)

    batch = {}
    for tag, d in (("drran", old), ("2dran", new)):
        t = [v["t180"] for v in d.values()]
        batch[tag] = {"t180_min": min(t), "t180_max": max(t),
                      "t180_median": float(np.median(t)),
                      "in180_mean": float(np.mean([v["in180"] for v in d.values()])),
                      "dv_mean": float(np.mean([v["dv"] for v in d.values()]))}

    out = {"sessions": {"drran": old, "2dran": new}, "batch": batch,
           "assignment": asg}
    (NEW / "batch_comparison.json").write_text(json.dumps(out, indent=1))

    # ---- figure: T levels per batch + the hop/T correspondence map -------
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))

    ax = axes[0]
    yticks, ylabels = [], []
    for row, (tag, d, c) in enumerate((("drran (09-02/03)", old, C_OLD),
                                       ("2dran (09-05/08/09)", new, C_NEW))):
        ids = sorted(d, key=lambda s: d[s]["t180"])
        y = np.arange(len(ids)) + row * (len(ids) + 1.5)
        yticks += list(y)
        ylabels += ids
        for yi, s in zip(y, ids):
            v = d[s]
            ax.errorbar(v["t180"], yi, xerr=v["t180_sd"], fmt="o", ms=5,
                        color=c, ecolor=c, elinewidth=1, capsize=2)
            if v["flagged"]:
                ax.annotate("drift flag", (v["t180"], yi), textcoords="offset points",
                            xytext=(6, -3), fontsize=7, color="tab:red")
        ax.text(1.005, y[-1] + 0.8, tag, fontsize=9, color=c, weight="bold")
    ax.set_yticks(yticks, labels=ylabels, fontsize=8)
    ax.axvline(1.0, color="k", lw=0.8, alpha=0.5)
    ax.set_xlabel("T = TOP/CH5 (CFC-180), stabilized mean ± sd")
    ax.set_title("T levels by session (sorted within batch)", fontsize=9)
    ax.grid(alpha=0.25, axis="x")

    ax = axes[1]
    for tag, d, c in (("drran", old, C_OLD), ("2dran", new, C_NEW)):
        for s, v in d.items():
            open_marker = v["censored_low"] or v["at_cap"] or v["bimodal"]
            ax.scatter(v["t_hop_ms"], v["t180"], s=55, color=c,
                       facecolors="none" if open_marker else c, zorder=3)
            ax.annotate(s.replace("drran", "d").replace("2dran", "2d"),
                        (v["t_hop_ms"], v["t180"]), textcoords="offset points",
                        xytext=(5, 4), fontsize=7.5, color=c)
    ax.set_xlabel("first-landing hop time, ms (open marker = censored/bimodal)")
    ax.set_ylabel("T = TOP/CH5 (CFC-180)")
    ax.set_title("Specimen-hop fingerprint map (candidate correspondences cluster)",
                 fontsize=9)
    ax.grid(alpha=0.25)

    fig.suptitle("2dran vs drran batches — 9 sessions each, 60 in / arrangement B",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(NEW / "12_batch_comparison.png", dpi=150)

    print(json.dumps(batch, indent=1))
    print("\nassignment (drran -> 2dran candidate, runner-up margin in z-units):")
    for o, p in asg["pairs"].items():
        print(f"  {o} -> {p['match']}  cost {p['cost']:.2f}  margin {p['runner_up_margin']:.2f}")
    print(f"total {asg['total_cost']:.2f} vs identity-map {asg['identity_cost']:.2f}")


if __name__ == "__main__":
    main()
