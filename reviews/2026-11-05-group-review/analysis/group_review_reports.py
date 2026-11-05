#!/usr/bin/env python3
"""Numbers and figure behind the reports in the 2026-11-05 group review sheet.

Reads only committed snapshots under manuscript/data/ and writes, next to this
script:
  seat-gauge-sessions.csv   every drop session with its seat gauge
  seat-gauge.png            gauge by batch, and gauge against deviation (batch 3)
  noise-model-terms.csv     the two terms of the rebound noise model, per specimen
  report-numbers.json       every number quoted in the review sheet

Seat gauge = (CFC-1000 transmissibility) / (CFC-180 transmissibility), from the
session means t1000_mean and t180_mean. Noise model as coded in
bo/t3_prism_bo_campaign.py on the campaign branch: relative standard error of
the rebound objective = hypot(p * sigma_e / e, sigma_m / m), p = 1 for
E_reb = e m g h and p = 2 for I_reb = m e^2, with sigma_e = sd(e) / sqrt(n_valid)
and sigma_m = 0.457 g.

Usage: python3 reviews/2026-11-05-group-review/analysis/group_review_reports.py
"""
import csv
import json
import math
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = REPO / "manuscript" / "data"
SIGMA_M = 0.457
# Same cutoff as scripts/figures/round3_three_print_analysis.py: a gauge of
# 1.145 or more reads 1.15 at two decimals and counts as a re-seat candidate.
GAUGE_MAX = 1.145

SESSIONS = [  # (batch label, print, file)
    ("seed", 1, "t3-prism-bo-batch-drop-results.csv"),
    ("batch 2", 1, "t3-prism-bo-round1-drop-results.csv"),
    ("batch 3", 1, "t3-prism-bo-round3-drop-results.csv"),
    ("batch 3", 2, "t3-prism-bo-round3-reprint-drop-results.csv"),
    ("batch 3", 3, "t3-prism-bo-round3-third-print-drop-results.csv"),
    ("batch 4", 1, "t3-prism-bo-round4-drop-results.csv"),
]
WARMUP = 2


def read(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den


def main():
    out = {}
    rows = []
    for batch, pr, name in SESSIONS:
        for r in read(name):
            t180, t1000 = float(r["t180_mean"]), float(r["t1000_mean"])
            n = int(r["n_valid"])
            rows.append(dict(batch=batch, print=pr, specimen=r["specimen"],
                             n_recorded=n, n_stabilized=n - WARMUP,
                             t180=round(t180, 4), t1000=round(t1000, 4),
                             gauge=round(t1000 / t180, 3),
                             mass_g=float(r["mass_g"]) if r.get("mass_g") else None,
                             e=float(r["e_rebound_mean"]), e_sd=float(r["e_rebound_sd"])))
    with open(HERE / "seat-gauge-sessions.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["batch", "print", "specimen", "n_recorded", "n_stabilized",
                    "t180", "t1000", "seat_gauge", "gauge_ge_1p15"])
        for r in rows:
            w.writerow([r["batch"], r["print"], r["specimen"], r["n_recorded"],
                        r["n_stabilized"], r["t180"], r["t1000"], r["gauge"],
                        r["gauge"] >= GAUGE_MAX])
    g = [r["gauge"] for r in rows]
    out["seat_gauge"] = dict(
        n_sessions=len(g), min=min(g), max=max(g), median=st.median(g),
        n_le_1p07=sum(x <= 1.07 for x in g),
        n_between=sum(1.07 < x < GAUGE_MAX for x in g),
        n_ge_1p15=sum(x >= GAUGE_MAX for x in g),
        flagged=[(r["batch"], r["print"], r["specimen"], r["gauge"], r["t180"])
                 for r in rows if r["gauge"] >= GAUGE_MAX])
    by = {}
    for r in rows:
        by.setdefault(r["batch"], []).append(r["gauge"])
    out["seat_gauge"]["per_batch"] = {
        k: dict(n=len(v), n_ge_1p15=sum(x >= GAUGE_MAX for x in v)) for k, v in by.items()}
    # front attenuators of batch 4
    out["seat_gauge"]["batch4"] = {r["specimen"]: r["gauge"] for r in rows if r["batch"] == "batch 4"}

    # Batch 3: gauge against deviation from design median over the three prints
    tp = read("t3-prism-bo-round3-three-print.csv")
    dev, gau, lab = [], [], []
    for r in tp:
        vals = [float(r[f"t180_{s}"]) for s in ("drran", "2dran", "dran3")]
        med = st.median(vals)
        for s in ("drran", "2dran", "dran3"):
            dev.append(100 * (float(r[f"t180_{s}"]) - med) / med)
            gau.append(float(r[f"gauge_{s}"]))
            lab.append(r[f"article_{s}"])
    out["batch3_gauge_vs_deviation"] = dict(
        n=len(dev), spearman_gauge_vs_signed_dev=round(spearman(gau, dev), 3),
        flagged=[(lab[i], gau[i], round(dev[i], 1)) for i in range(len(dev)) if gau[i] >= GAUGE_MAX],
        median_abs_dev_unflagged=round(st.median(abs(dev[i]) for i in range(len(dev)) if gau[i] < GAUGE_MAX), 2))

    # Drop counts
    cnt = {}
    for r in rows:
        cnt.setdefault((r["batch"], r["print"]), set()).add((r["n_recorded"], r["n_stabilized"]))
    out["drop_counts"] = {f"{b} print {p}": sorted(v) for (b, p), v in cnt.items()}

    # Noise model terms (first-print and reprint specimens, all with a mass)
    nm = []
    for r in rows:
        if r["mass_g"] is None:
            continue
        n = r["n_recorded"]
        rel_e = (r["e_sd"] / math.sqrt(n)) / r["e"]
        rel_m = SIGMA_M / r["mass_g"]
        for form, p in (("E_reb", 1), ("I_reb", 2)):
            tot = math.hypot(p * rel_e, rel_m)
            nm.append(dict(batch=r["batch"], print=r["print"], specimen=r["specimen"], form=form,
                           rel_drop_term_pct=round(100 * p * rel_e, 3), rel_mass_term_pct=round(100 * rel_m, 3),
                           rel_total_pct=round(100 * tot, 3),
                           mass_share_of_variance=round(rel_m ** 2 / tot ** 2, 3)))
    with open(HERE / "noise-model-terms.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(nm[0]))
        w.writeheader()
        w.writerows(nm)
    for form in ("E_reb", "I_reb"):
        sub = [x for x in nm if x["form"] == form]
        out[f"noise_{form}"] = dict(
            n=len(sub),
            median_rel_drop_term_pct=st.median(x["rel_drop_term_pct"] for x in sub),
            median_rel_mass_term_pct=st.median(x["rel_mass_term_pct"] for x in sub),
            median_rel_total_pct=st.median(x["rel_total_pct"] for x in sub),
            n_mass_term_dominant=sum(x["mass_share_of_variance"] > 0.5 for x in sub))
    trip = [22.29, 21.42, 22.10]
    out["sigma_m_check"] = dict(masses_g=trip, sample_sd_g=round(st.stdev(trip), 4))
    js = json.load(open(DATA / "t3-prism-bo-round3-three-print-stats.json"))
    out["e_reb_between_print_sd_mJ"] = js.get("e_reb_between_print_sd_mJ")

    # t180 vs rebound objective over the 35 first-print campaign specimens
    first = [r for r in rows if r["print"] == 1 and r["mass_g"] is not None]
    t = [r["t180"] for r in first]
    i_reb = [1000 * r["mass_g"] * r["e"] ** 2 for r in first]
    e_reb = [r["e"] * r["mass_g"] * 9.80665 * 1.524 for r in first]
    out["objective_correlation_first_prints"] = dict(
        n=len(first), spearman_t180_vs_I_reb=round(spearman(t, i_reb), 3),
        spearman_t180_vs_E_reb=round(spearman(t, e_reb), 3))
    json.dump(out, open(HERE / "report-numbers.json", "w"), indent=1)
    print(json.dumps(out, indent=1)[:4000])

    # Figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    blue, orange, gray, ink = "#2a78d6", "#eb6834", "#8c8b86", "#0b0b0b"
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
    order = ["seed", "batch 2", "batch 3", "batch 4"]
    for k, b in enumerate(order):
        sub = [r for r in rows if r["batch"] == b]
        for j, r in enumerate(sub):
            x = k + (j - len(sub) / 2) * 0.025
            flag = r["gauge"] >= GAUGE_MAX
            a1.plot(x, r["gauge"], "o", ms=6, color=orange if flag else gray,
                    mec="white", mew=0.8, zorder=3)
            if flag:
                dy = {"bag26v": -5, "nvxsrv": 4}.get(r["specimen"], 0)
                a1.annotate(r["specimen"], (x, r["gauge"]), xytext=(5, dy),
                            textcoords="offset points", fontsize=7, color=ink, va="center")
    a1.axhline(1.15, color=orange, lw=1, ls="--")
    a1.axhline(1.07, color=gray, lw=1, ls=":")
    a1.text(3.45, 1.15, "re-seat\ncandidate\n(1.15)", fontsize=7, va="bottom", ha="left", color=ink)
    a1.text(3.45, 1.07, "typical\nupper\n(1.07)", fontsize=7, va="top", ha="left", color=ink)
    a1.set_xticks(range(4), [f"{b}\n(n={len([r for r in rows if r['batch']==b])})" for b in order])
    a1.set_xlim(-0.5, 3.9)
    a1.set_ylabel("seat gauge = CFC-1000 / CFC-180 transmissibility")
    a1.set_title("(a) Seat gauge of every drop session (54)", fontsize=10, loc="left")
    for i in range(len(dev)):
        flag = gau[i] >= GAUGE_MAX
        a2.plot(dev[i], gau[i], "o", ms=6, color=orange if flag else blue, mec="white", mew=0.8, zorder=3)
        if flag:
            a2.annotate(lab[i], (dev[i], gau[i]), xytext=(-6, 4), textcoords="offset points",
                        fontsize=7, ha="right", color=ink)
    a2.axhline(1.15, color=orange, lw=1, ls="--")
    a2.axvline(0, color=gray, lw=0.8)
    a2.set_xlabel("t180 deviation from design median, 3 prints (%)")
    a2.set_ylabel("seat gauge")
    a2.set_title("(b) Batch 3, three prints of 9 designs (27)", fontsize=10, loc="left")
    for a in (a1, a2):
        a.spines[["top", "right"]].set_visible(False)
        a.grid(axis="y", color="#e6e5e1", lw=0.6)
        a.set_axisbelow(True)
    h = [plt.Line2D([], [], marker="o", ls="", color=orange, mec="white", label="gauge 1.15 or more (re-seat candidate)"),
         plt.Line2D([], [], marker="o", ls="", color=gray, mec="white", label="gauge below 1.15 (a)"),
         plt.Line2D([], [], marker="o", ls="", color=blue, mec="white", label="gauge below 1.15 (b)")]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(HERE / "seat-gauge.png", dpi=170)
    print("wrote", HERE / "seat-gauge.png")


if __name__ == "__main__":
    main()
