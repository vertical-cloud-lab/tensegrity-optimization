"""Collect every result of this directory into ``results.md``.

Usage::

    python analysis/bo-review/summarize.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
BASE = HERE.parent / "logocv-baselines"
SPACE_LABEL = {"six": "6 orig.", "six-sim": "6 orig. + sim", "eight": "6 orig. + 2 infill",
               "twelve": "12 campaign"}


def fmt(v, p=None):
    s = f"{v:+.2f}"
    return s + ("" if p is None else (" (<0.001)" if p < 0.001 else f" ({p:.3f})"))


def noise_table(model):
    rows = []
    for space in ("six", "six-sim", "eight", "twelve"):
        for noise in ("fixed", "learned", "replicate"):
            p = DATA / "logocv" / f"{model}-{noise}-{space}" / "state.json"
            if not p.exists():
                continue
            s = json.loads(p.read_text())["stats"]
            rows.append((space, noise, s))
    if not rows:
        return []
    out = [f"| space | noise | t180 rho_s (p) | t180 R2_oos | t180 MAPE | t180 cov. | "
           "E_reb rho_s (p) | E_reb R2_oos | E_reb MAPE | E_reb cov. |",
           "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for space, noise, s in rows:
        a, b = s["t180"], s["e_reb_mJ"]
        out.append(f"| {SPACE_LABEL[space]} | {noise} | {fmt(a['spearman'], a['perm_p'])} | "
                   f"{a['R2_oos']:+.2f} | {a['MAPE_pct']:.1f}% | {a['coverage_1.96sd_pct']:.0f}% | "
                   f"{fmt(b['spearman'], b['perm_p'])} | {b['R2_oos']:+.2f} | "
                   f"{b['MAPE_pct']:.1f}% | {b['coverage_1.96sd_pct']:.0f}% |")
    return out


def batch_term_tables():
    p = DATA / "batch-term" / "batch-term.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text())
    out = ["Filament settings by session (PLA temp / PLA flow / TPU temp / TPU flow):", ""]
    out += ["| session | PLA C | PLA mm3/s | TPU C | TPU mm3/s |", "|---|--:|--:|--:|--:|"]
    for r in d["filament_settings_by_session"]:
        out.append(f"| {r['session']} | {r['pla_nozzle_temp_C']} | {r['pla_flow_mm3_s']} | "
                   f"{r['tpu_nozzle_temp_C']} | {r['tpu_flow_mm3_s']} |")
    term_label = {"none": "design inputs only", "ri": "+ session random intercept",
                  "ord": "+ session order as an input"}
    for scheme, title in (("logo", "LOGO (35 design folds)"),
                          ("lobo", "Leave one print session out (5 folds)")):
        out += ["", f"**{title}** (MAP GP, noise learned)", "",
                "| space | batch term | t180 rho_s (p) | t180 R2_oos | E_reb rho_s (p) | E_reb R2_oos |",
                "|---|---|--:|--:|--:|--:|"]
        for key, s in d["cv"].items():
            sch, space, term = key.split("/")
            if sch != scheme:
                continue
            a, b = s["t180"], s["e_reb_mJ"]
            out.append(f"| {SPACE_LABEL[space]} | {term_label[term]} | "
                       f"{fmt(a['spearman'], a['perm_p'])} | {a['R2_oos']:+.2f} | "
                       f"{fmt(b['spearman'], b['perm_p'])} | {b['R2_oos']:+.2f} |")
    out += ["", "**Session random intercepts, all 44 articles** (posterior mean +/- sd, "
            "MAP GP with the six or eight design inputs)", "",
            "| space / objective | session sd | noise sd | seed | r2d2c | drran | 2dran | corny |",
            "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for key, e in d["batch_effects"].items():
        sess = [f"{e[s]['effect']:+.3g} +/- {e[s]['sd']:.2g}" for s in
                ("seed", "r2d2c", "drran", "2dran", "corny")]
        out.append(f"| {key} | {e['_session_sd']:.3g} | {e['_noise_sd']:.3g} | " + " | ".join(sess) + " |")
    return out


def importance_tables():
    p = DATA / "importances" / "summary.json"
    if not p.exists():
        return []
    s = json.loads(p.read_text())
    out = ["| dataset | noise | NUTS budget | objective | posterior-mean sd over the space (data sd) | "
           "learned noise sd | largest importance (seed-to-seed sd) | top input by seed | "
           "max split-R-hat, log lengthscales |", "|---|---|---|---|--:|--:|---|---|--:|"]
    for r in s:
        imp = r["importance_mean"]
        top = next(iter(imp.items()))
        flat = ", ".join(f"{v:.3g}" for v in r["posterior_mean_sd_over_space_by_seed"])
        noise = ("" if not r["noise_sd_median_by_seed"] else
                 ", ".join(f"{v:.3g}" for v in r["noise_sd_median_by_seed"]))
        out.append(f"| {r['dataset']} | {r['noise']} | {r['budget']} | {r['metric']} | "
                   f"{flat} ({r['y_std']:.3g}) | {noise} | {top[0]} {top[1]:.2f} "
                   f"({r['importance_seed_sd_max']:.2f}) | {', '.join(r['top_parameter_per_seed'])} | "
                   f"{r['split_rhat_log_lengthscale_max']:.2f} |")
    return out


def lengthscale_table(dataset, budget="512/256"):
    p = DATA / "importances" / "lengthscales-importances.csv"
    if not p.exists():
        return []
    d = pd.read_csv(p)
    d = d[(d.dataset == dataset) & (d.budget == budget)]
    if d.empty:
        return []
    g = d.groupby(["noise", "metric", "parameter"], sort=False).agg(
        ls=("lengthscale_median", "median"), imp=("ax_importance", "mean")).reset_index()
    params = list(dict.fromkeys(g.parameter))
    out = ["| noise | objective | " + " | ".join(params) + " |",
           "|---|---|" + "--:|" * len(params)]
    for (noise, metric), gg in g.groupby(["noise", "metric"], sort=False):
        gg = gg.set_index("parameter")
        out.append(f"| {noise} | {metric} | " + " | ".join(
            f"{gg.ls[c]:.2g} ({gg.imp[c]:.2f})" for c in params) + " |")
    return out


def main():
    md = ["# Results tables (generated by `summarize.py`)", ""]
    md += ["## 1. Noise models under LOGO-CV", "", "### SAAS (NUTS 512 warmup / 256 samples)", ""]
    md += noise_table("saas") or ["(not run)"]
    md += ["", "### MAP GP (BoTorch default SingleTaskGP)", ""]
    md += noise_table("map") or ["(not run)"]
    p = DATA / "batch5" / "comparison.md"
    md += ["", "## 2 and 3. Batch 5 regenerated", ""]
    md += p.read_text().splitlines() if p.exists() else ["(not run)"]
    md += ["", "## 4. Batch terms", ""] + (batch_term_tables() or ["(not run)"])
    md += ["", "## 6 to 8. Lengthscales, importances, MCMC stability", ""]
    md += importance_tables() or ["(not run)"]
    for ds in ("round2-six", "all-twelve"):
        t = lengthscale_table(ds)
        if t:
            md += ["", f"Median lengthscale on the unit cube (Ax importance in brackets), "
                       f"{ds}, NUTS 512/256, medians over seeds:", ""] + t
    (HERE / "results.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
