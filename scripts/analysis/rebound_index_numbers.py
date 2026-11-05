"""Every rebound-objective number the manuscript quotes, in both forms.

The campaign generated batches 2 to 4 minimizing the first-power form
E_reb = e * m * g * h (mJ per drop). From 2026-10-29 the second objective
is the mass-weighted rebound index I_reb = m * e**2 (mg). This script
recomputes, from the committed snapshots under manuscript/data/ only:

* per-specimen values of both forms (seed-batch table, quoted specimens);
* the cumulative first-print front and its dominated hypervolume after
  each batch (as in fig:front-evolution);
* the design-mean fronts, with each batch-3 design at the mean of its
  screened prints (seat gauge below 1.145, no drift flag), after batch 3
  and after batch 4 (as in the three-print analysis);
* the extremes the text quotes.

The "me" numbers are checked against the committed first-power results
(t3-prism-bo-front-evolution.csv and t3-prism-bo-round3-three-print-stats.json)
and the script exits non-zero on any mismatch, so the "me2" numbers come
from the same code path. Hypervolume reference points: (1.35, 15 mJ) for
E_reb, the reference of every first-power number on the campaign branch, and
(1.35, 50 mg) for I_reb, the same construction (6lhxfy, the worst specimen
through batch 2 under either form, at 13.93 mJ and 46.95 mg).

Writes manuscript/data/t3-prism-rebound-index-numbers.json.

Usage:  python scripts/analysis/rebound_index_numbers.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "manuscript/data"
OUT_JSON = DATA / "t3-prism-rebound-index-numbers.json"

G, H = 9.80665, 60 * 0.0254
GAUGE_MAX = 1.145
FORMS = {
    # name: (value from e and m in g, hypervolume reference, unit)
    "E_reb": (lambda e, m: e * m * G * H, (1.35, 15.0), "mJ"),
    "I_reb": (lambda e, m: 1000.0 * m * e ** 2, (1.35, 50.0), "mg"),
}
BATCHES = [(1, "t3-prism-bo-batch-drop-results.csv", None),
           (2, "t3-prism-bo-round1-drop-results.csv", None),
           (3, "t3-prism-bo-round3-drop-results.csv", "drran"),
           (3, "t3-prism-bo-round3-reprint-drop-results.csv", "2dran"),
           (3, "t3-prism-bo-round3-third-print-drop-results.csv", "dran3"),
           (4, "t3-prism-bo-round4-drop-results.csv", None)]


def load() -> pd.DataFrame:
    """One row per tested specimen with a weighed mass (53 of 54)."""
    frames = []
    for batch, fname, print_tag in BATCHES:
        d = pd.read_csv(DATA / fname)
        d = d[d.mass_g.notna()].copy()
        d["batch"] = batch
        d["print_"] = print_tag or "only"
        if batch == 3:
            if "trial" not in d:
                d["trial"] = d.spec.astype(str).str.lstrip("t").astype(int)
            d["gauge"] = d.t1000_mean / d.t180_mean
            d["drift"] = d.t_drift_flag.astype(str).eq("True")
            d["screened"] = (d.gauge < GAUGE_MAX) & ~d.drift
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    for name, (fn, _, _) in FORMS.items():
        d[name] = fn(d.e_rebound_mean, d.mass_g)
    return d


def pareto(points: pd.DataFrame, col: str) -> pd.DataFrame:
    t, y = points.t180.to_numpy(), points[col].to_numpy()
    keep = [not np.any((t <= t[i]) & (y <= y[i]) & ((t < t[i]) | (y < y[i])))
            for i in range(len(points))]
    return points[keep].sort_values("t180")


def hypervolume(front: pd.DataFrame, col: str, ref) -> float:
    f = front[(front.t180 < ref[0]) & (front[col] < ref[1])].sort_values("t180")
    t = list(f.t180) + [ref[0]]
    return float(sum((t[i + 1] - t[i]) * (ref[1] - y)
                     for i, y in enumerate(f[col])))


def front_summary(points, col, ref):
    fr = pareto(points, col)
    return {"members": list(fr.label), "hv": round(hypervolume(fr, col, ref), 4)}


def repeatability(d: pd.DataFrame, col: str) -> dict:
    """Print-to-print repeatability of the batch-3 designs (three prints)."""
    b3 = d[d.batch == 3]
    wide = b3.pivot(index="trial", columns="print_", values=col)
    ratio = wide.max(axis=1) / wide.min(axis=1)
    worst = int(ratio.idxmax())
    pairs = [("drran", "2dran"), ("drran", "dran3"), ("2dran", "dran3")]
    return {
        "max_over_min_per_design": {"min": round(float(ratio.min()), 3),
                                    "max": round(float(ratio.max()), 3)},
        "worst_trial": {"trial": worst,
                        "min": round(float(wide.loc[worst].min()), 2),
                        "max": round(float(wide.loc[worst].max()), 2)},
        "rank_between_prints": {
            f"{a}-{b}": round(float(stats.spearmanr(wide[a], wide[b]).statistic), 3)
            for a, b in pairs},
        "between_print_sd": round(float(np.sqrt(
            ((wide.sub(wide.mean(axis=1), axis=0)) ** 2).sum().sum()
            / (wide.size - len(wide)))), 3),
        "design_mean_sd": round(float(wide.mean(axis=1).std(ddof=1)), 3),
    }


def form_numbers(d: pd.DataFrame, col: str, ref, unit: str) -> dict:
    out = {"unit": unit, "hv_reference": list(ref)}
    pts = d.assign(label=d.specimen, t180=d.t180_mean)
    first = pts[pts.print_.isin(["only", "drran"])]
    # cumulative first-print fronts (fig:front-evolution convention)
    evo, prev = [], None
    for b in (1, 2, 3, 4):
        s = front_summary(first[first.batch <= b], col, ref)
        s["after_batch"] = b
        s["gain_pct"] = None if prev is None else round(100 * (s["hv"] / prev - 1), 1)
        evo.append(s)
        prev = s["hv"]
    out["first_print_evolution"] = evo
    out["first_print_total_gain_pct"] = round(100 * (evo[-1]["hv"] / evo[0]["hv"] - 1), 1)
    # design means: batch-3 designs at the mean of their screened prints
    b3 = d[(d.batch == 3) & d.screened]
    dm = b3.groupby("trial").agg(t180=("t180_mean", "mean"), y=(col, "mean"))
    first_lab = d[(d.batch == 3) & (d.print_ == "drran")].set_index("trial").specimen
    dm_pts = pd.DataFrame({"label": first_lab.reindex(dm.index).to_numpy() + "*",
                           "batch": 3, "t180": dm.t180.to_numpy(), col: dm.y.to_numpy()})
    other = pts[pts.batch != 3][["label", "batch", "t180", col]]
    combined = pd.concat([other, dm_pts], ignore_index=True)
    out["design_mean_front_after_batch2"] = front_summary(
        combined[combined.batch <= 2], col, ref)
    out["design_mean_front_after_batch3"] = front_summary(
        combined[combined.batch <= 3], col, ref)
    out["design_mean_front_after_batch4"] = front_summary(combined, col, ref)
    a2 = out["design_mean_front_after_batch2"]["hv"]
    a3 = out["design_mean_front_after_batch3"]["hv"]
    out["design_mean_batch3_gain_pct"] = round(100 * (a3 / a2 - 1), 1)
    out["batch3_repeatability"] = repeatability(d, col)
    # per-specimen values and extremes
    out["specimens"] = {r.specimen: round(float(r[col]), 2) for _, r in d.iterrows()}
    lo = d.loc[d[col].idxmin()]
    out["lowest"] = {"specimen": lo.specimen, "value": round(float(lo[col]), 2)}
    seed = d[d.batch == 1]
    hi = seed.loc[seed[col].idxmax()]
    out["seed_highest"] = {"specimen": hi.specimen, "value": round(float(hi[col]), 2)}
    return out


def check_first_power(out: dict) -> int:
    """Compare the E_reb numbers with the committed first-power results."""
    bad = 0
    evo = pd.read_csv(DATA / "t3-prism-bo-front-evolution.csv")
    for row, mine in zip(evo.itertuples(), out["first_print_evolution"], strict=True):
        if abs(row._3 - mine["hv"]) > 6e-4:
            bad += 1
            print(f"MISMATCH front evolution after batch {mine['after_batch']}: "
                  f"committed {row._3}, here {mine['hv']}")
    stats_json = json.loads((DATA / "t3-prism-bo-round3-three-print-stats.json").read_text())
    for key, mine in [("front_design_means_screened", "design_mean_front_after_batch4"),
                      ("front_after_batch3_design_means_screened",
                       "design_mean_front_after_batch3")]:
        ref, here = stats_json[key], out[mine]
        if [m.rstrip("*") for m in ref["members"]] != [m.rstrip("*") for m in here["members"]] \
                or abs(ref["hv"] - here["hv"]) > 1e-3:
            bad += 1
            print(f"MISMATCH {key}: committed {ref}, here {here}")
    rep = out["batch3_repeatability"]
    for key, mine, tol in [
            ("e_reb_between_print_sd_mJ", rep["between_print_sd"], 1e-3),
            ("e_reb_design_mean_sd_mJ", rep["design_mean_sd"], 1e-3)]:
        if abs(stats_json[key] - mine) > tol:
            bad += 1
            print(f"MISMATCH {key}: committed {stats_json[key]}, here {mine}")
    for pair, rho in rep["rank_between_prints"].items():
        if abs(stats_json["rank_between_prints_e_reb"][pair] - rho) > 1e-3:
            bad += 1
            print(f"MISMATCH rank {pair}: here {rho}")
    print(f"first-power numbers vs committed results: {bad} mismatches")
    return bad


def main() -> int:
    d = load()
    out = {name: form_numbers(d, name, ref, unit)
           for name, (_, ref, unit) in FORMS.items()}
    bad = check_first_power(out["E_reb"])
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    for name in FORMS:
        o = out[name]
        print(f"\n{name} ({o['unit']}), reference {tuple(o['hv_reference'])}")
        for s in o["first_print_evolution"]:
            gain = "baseline" if s["gain_pct"] is None else f"{s['gain_pct']:+.1f}%"
            print(f"  after batch {s['after_batch']}: HV {s['hv']:.3f} ({gain}), "
                  f"front {' '.join(s['members'])}")
        print(f"  total first-print gain {o['first_print_total_gain_pct']:+.1f}%")
        for k in ("design_mean_front_after_batch2", "design_mean_front_after_batch3",
                  "design_mean_front_after_batch4"):
            print(f"  {k}: HV {o[k]['hv']:.3f}, {' '.join(o[k]['members'])}")
        print(f"  design-mean batch-3 gain {o['design_mean_batch3_gain_pct']:+.1f}%")
        print(f"  lowest on record: {o['lowest']}; seed highest: {o['seed_highest']}")
        print(f"  batch-3 repeatability: {o['batch3_repeatability']}")
    print(f"\nwrote {OUT_JSON.relative_to(ROOT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
