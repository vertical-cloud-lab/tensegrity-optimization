#!/usr/bin/env python3
"""corny1..corny9 vs drran/2dran — three-seat cross-batch comparison (PR #86, 09-15).

Third randomized batch at identical settings (60 in, arrangement B, SOP
capture).  @ctrhjk's 09-12 unblinding established that drran and 2dran
are the same nine structures re-tested; if the corny batch is that set
again (to be confirmed — asked in the check-in), the program now holds a
9-article x 3-seat reproducibility dataset.  This script extends the
2dran comparison to three batches using the committed
``campaign_metrics.json`` of each:

1. batch-level comparison (T levels, inputs, dv) + robust per-session
   hop signatures (``hop_first`` from the 2dran comparison unchanged);
2. Hungarian best-fit assignments drran <-> corny and 2dran <-> corny
   (same standardized [log t_hop, T180, log T1000] distance), with the
   committed drran <-> 2dran assignment loaded for a cycle-consistency
   check: drran -> 2dran -> corny composed vs the direct drran -> corny
   map.  Consistent cycles are the strongest DAQ-only evidence a
   correspondence is real; margins < ~1 z-unit remain candidates only;
3. the advisory T1000/T180 seat gauge (CLAUDE.md: healthy ~1.00-1.07,
   suspect >= ~1.15) per corny session, and the on-record 09-12
   prediction test — "2dran1 (ratio 1.37) reads high at 1.079 and
   should come down on re-seat" — evaluated both under the best-fit
   pairing and assignment-free (against the corny batch max).

Outputs ``12_batch_comparison.png`` + ``batch_comparison.json`` next to
the corny campaign figures.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402
from drop_test_2dran_batch_comparison import assignment, features  # noqa: E402

NEW = DATA / "corny-checkin" / "figures"
B1 = DATA / "drran-checkin" / "figures"
B2 = DATA / "2dran-checkin" / "figures"
GAUGE_SUSPECT = 1.15            # advisory T1000/T180 seat gauge (CLAUDE.md)
PRED_2DRAN1_T180 = 1.0791       # the on-record 09-12 prediction target
C1, C2, C3 = "#1f77b4", "#ff7f0e", "#2ca02c"


def batch_stats(d: dict) -> dict:
    t = [v["t180"] for v in d.values()]
    return {"t180_min": min(t), "t180_max": max(t),
            "t180_median": float(np.median(t)),
            "in180_mean": float(np.mean([v["in180"] for v in d.values()])),
            "dv_mean": float(np.mean([v["dv"] for v in d.values()]))}


def main():
    drran, dran2, corny = (features(p / "campaign_metrics.json")
                           for p in (B1, B2, NEW))
    prev = json.loads((B2 / "batch_comparison.json").read_text())
    d1_to_d2 = {o: p["match"] for o, p in prev["assignment"]["pairs"].items()}

    asg_d1 = assignment(drran, corny)      # drran -> corny
    asg_d2 = assignment(dran2, corny)      # 2dran -> corny

    # cycle consistency: drran -> 2dran -> corny vs direct drran -> corny
    cycles = {}
    for o in sorted(drran):
        via = asg_d2["pairs"][d1_to_d2[o]]["match"]
        direct = asg_d1["pairs"][o]["match"]
        cycles[o] = {"via_2dran": via, "direct": direct,
                     "consistent": via == direct}
    n_cons = sum(c["consistent"] for c in cycles.values())

    # advisory seat gauge + the on-record 2dran1 prediction
    gauge = {s: {"ratio": round(v["t1000"] / v["t180"], 3),
                 "suspect": v["t1000"] / v["t180"] >= GAUGE_SUSPECT}
             for s, v in corny.items()}
    part = asg_d2["pairs"]["2dran1"]
    corny_max = max(v["t180"] for v in corny.values())
    prediction = {
        "statement": "2dran1 (T180 1.0791, gauge 1.37) reads high and should "
                     "come down on re-seat (CLAUDE.md, on record 09-12)",
        "best_fit_partner": part["match"],
        "partner_t180": corny[part["match"]]["t180"],
        "partner_margin_z": part["runner_up_margin"],
        "corny_batch_max_t180": corny_max,
        "holds_under_any_pairing": bool(corny_max < PRED_2DRAN1_T180),
        "holds_under_best_fit": bool(corny[part["match"]]["t180"] < PRED_2DRAN1_T180),
    }

    out = {"sessions": {"drran": drran, "2dran": dran2, "corny": corny},
           "batch": {tag: batch_stats(d) for tag, d in
                     (("drran", drran), ("2dran", dran2), ("corny", corny))},
           "assignment_drran_to_corny": asg_d1,
           "assignment_2dran_to_corny": asg_d2,
           "cycle_consistency": {"pairs": cycles, "n_consistent": n_cons,
                                 "note": "drran->2dran map from the committed "
                                         "2dran batch_comparison.json"},
           "seat_gauge": gauge, "prediction_2dran1": prediction}
    (NEW / "batch_comparison.json").write_text(json.dumps(out, indent=1))

    # ---- figure: T levels per batch + the hop/T correspondence map -------
    batches = (("drran (09-02/03)", drran, C1),
               ("2dran (09-05/08/09)", dran2, C2),
               ("corny (this batch)", corny, C3))
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.0))

    ax = axes[0]
    yticks, ylabels = [], []
    y0 = 0.0
    for tag, d, c in batches:
        ids = sorted(d, key=lambda s: d[s]["t180"])
        y = np.arange(len(ids)) + y0
        y0 = y[-1] + 2.5
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
    ax.set_yticks(yticks, labels=ylabels, fontsize=7.5)
    ax.axvline(1.0, color="k", lw=0.8, alpha=0.5)
    ax.set_xlabel("T = TOP/CH5 (CFC-180), stabilized mean ± sd")
    ax.set_title("T levels by session (sorted within batch)", fontsize=9)
    ax.grid(alpha=0.25, axis="x")

    ax = axes[1]
    short = {"drran": "d", "2dran": "2d", "corny": "c"}
    for tag, d, c in batches:
        key = tag.split()[0]
        for s, v in d.items():
            open_marker = v["censored_low"] or v["at_cap"] or v["bimodal"]
            ax.scatter(v["t_hop_ms"], v["t180"], s=55, color=c,
                       facecolors="none" if open_marker else c, zorder=3)
            ax.annotate(s.replace(key, short[key]), (v["t_hop_ms"], v["t180"]),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=7.5, color=c)
    ax.set_xlabel("first-landing hop time, ms (open marker = censored/bimodal)")
    ax.set_ylabel("T = TOP/CH5 (CFC-180)")
    ax.set_title("Specimen-hop fingerprint map (candidate correspondences cluster)",
                 fontsize=9)
    ax.grid(alpha=0.25)

    fig.suptitle("corny vs 2dran vs drran batches — 9 sessions each, "
                 "60 in / arrangement B", fontsize=10)
    fig.tight_layout()
    fig.savefig(NEW / "12_batch_comparison.png", dpi=150)

    print(json.dumps(out["batch"], indent=1))
    for name, asg in (("drran -> corny", asg_d1), ("2dran -> corny", asg_d2)):
        print(f"\n{name} (candidate, runner-up margin in z-units):")
        for o, p in asg["pairs"].items():
            print(f"  {o} -> {p['match']}  cost {p['cost']:.2f}  "
                  f"margin {p['runner_up_margin']:.2f}")
        print(f"  total {asg['total_cost']:.2f} vs identity-map "
              f"{asg['identity_cost']:.2f}")
    print(f"\ncycle consistency (drran -> 2dran -> corny vs direct): "
          f"{n_cons}/9 consistent")
    print(f"seat gauge (T1000/T180): "
          + ", ".join(f"{s} {g['ratio']}{' *SUSPECT*' if g['suspect'] else ''}"
                      for s, g in sorted(gauge.items())))
    print(f"\nprediction test: 2dran1 (1.0791) -> best-fit {part['match']} "
          f"T180 {prediction['partner_t180']:.4f} "
          f"(margin {part['runner_up_margin']:.2f} z); corny max "
          f"{corny_max:.4f}; holds under any pairing: "
          f"{prediction['holds_under_any_pairing']}")


if __name__ == "__main__":
    main()
