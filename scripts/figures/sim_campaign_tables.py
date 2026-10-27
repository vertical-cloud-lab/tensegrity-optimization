"""Simulation-only BO campaign: main-text table, SI table, SI figure, stats.

Recomputes every number the manuscript quotes for the simulated campaign of
PR #33 from the per-seed run files snapshotted under manuscript/data/sim/
(copied verbatim from origin/copilot/explore-simulations-for-tensegrity at
94e53a8; provenance in figures/sim/README.md). Nothing is read from the
PR #33 write-ups; the committed summaries are used only as cross-checks.

Reads
  manuscript/data/sim/contrast_refs.csv               reference points
  manuscript/data/sim/contrast_front_{envelope,strain}.csv
                                                      polished reference fronts
  manuscript/data/sim/contrast_cloud_ratios.csv.gz    16,384-design Sobol cloud
  manuscript/data/sim/envelope/contrast_bo_envelope_seed<k>.csv
  manuscript/data/sim/envelope/contrast_baseline_<s>_<mode>_envelope_seed<k>.csv
  manuscript/data/sim/strain-era/pr102_*_ratios-strain*_seed<k>.csv
and, for cross-checks only,
  manuscript/data/sim/bo_contrast_envelope_summary.csv
  manuscript/data/sim/bo_contrast_strain_era_rescored_seeds.csv
  manuscript/data/sim/audits/synthetic_audit_physics.csv

Writes
  manuscript/tables/sim-campaign.tex        main-text table (tab:sim-campaign)
  manuscript/tables/si-sim-campaign.tex     SI table (tab:si-sim-campaign)
  manuscript/data/sim/sim-campaign-stats.json   every quoted number
  figures/sim/sim-campaign.png              SI figure (fig:si-sim-campaign)

Scoring. Both objectives are minimized. The hypervolume of a run is the 2-D
dominated hypervolume of its feasible evaluations against the pair's fixed
reference point (1.05 times the componentwise worst value over the feasible
cloud, shared by every method and seed). Each run's final hypervolume is
divided by the pair's best-known reference hypervolume: the hypervolume of
the union of the polished reference front, the feasible cloud, and every
feasible evaluation of the compared runs (BO plus the printability-filtered
baselines for the envelope pair; all five methods for the strain pair). The
polished front alone is reported too, since it was the denominator in the
PR #33 write-up before the Edison 53cfc937 audit.

Tests. One-sided exact Mann-Whitney U (BO greater) on the ten final
hypervolumes of each method, the paired exact Wilcoxon signed-rank test with
repeats paired by seed index, and the count of seeds on which BO beats the
baseline.

Usage: python scripts/figures/sim_campaign_tables.py   (or: make sim)
"""

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import mannwhitneyu, wilcoxon  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "manuscript/data/sim"
TABLES = ROOT / "manuscript/tables"
OUT_JSON = SIM / "sim-campaign-stats.json"
OUT_FIG = ROOT / "figures/sim/sim-campaign.png"

BUDGET = 45
SEEDS = list(range(10))
BASELINES = ["random", "sobol", "lhs", "heuristic"]
LABEL = {"bo": "BO (qNEHVI)", "random": "Random", "sobol": "Sobol",
         "lhs": "Latin hypercube", "heuristic": "Compass search"}
SHORT = {**LABEL, "lhs": "LHS", "heuristic": "Compass"}
PAIRS = {"envelope": ["t180", "envelope_cm3"],
         "strain": ["t180", "peak_tendon_strain"]}
STRAIN_FILES = {"bo": "pr102_sim_bo_botorch_ratios-strain_sobol_seed{k}.csv",
                **{s: f"pr102_baseline_{s}_ratios-strain_seed{{k}}.csv"
                   for s in BASELINES}}
BO_BLUE, INK, MUTED = "#2a78d6", "#0b0b0b", "#52514e"
SAMPLER_GRAY = "#8c8b86"
SAMPLER_DASH = {"random": "-", "sobol": "--", "lhs": "-.", "heuristic": ":"}


def hypervolume(points, ref):
    """2-D dominated hypervolume of a minimization set against ``ref``.

    The same sweep as hypervolume_2d in PR #33's pr102_sim_campaign.py, which
    the Edison 53cfc937 audit cross-checked against BoTorch's exact routine.
    """
    pts = np.atleast_2d(np.asarray(points, dtype=float))
    pts = pts[np.isfinite(pts).all(axis=1)]
    pts = pts[(pts < ref).all(axis=1)]
    if pts.size == 0:
        return 0.0
    pts = pts[np.argsort(pts[:, 0], kind="stable")]
    hv, best_y = 0.0, ref[1]
    for x, y in pts:
        if y < best_y:
            hv += (ref[0] - x) * (best_y - y)
            best_y = y
    return float(hv)


def feasible_points(df, objs):
    col = "pair_feasible" if "pair_feasible" in df else "feasible"
    mask = df[col].astype(bool).to_numpy().copy()
    if "ok" in df:
        mask &= df["ok"].astype(bool).to_numpy()
    return df.loc[mask, objs].to_numpy(dtype=float)


def load_runs(pattern):
    runs = []
    for k in SEEDS:
        f = Path(str(pattern).format(k=k))
        df = pd.read_csv(f)
        assert len(df) == BUDGET, f"{f.name}: {len(df)} evaluations"
        runs.append(df)
    return runs


def exact_tests(bo, other):
    return {
        "mannwhitney_exact_p": float(mannwhitneyu(
            bo, other, alternative="greater", method="exact").pvalue),
        "wilcoxon_paired_exact_p": float(wilcoxon(
            bo, other, alternative="greater", method="exact").pvalue),
        "paired_wins": int((bo > other).sum()),
    }


def score_pair(pair, runs, union_keys, cloud, refs):
    objs = PAIRS[pair]
    ref = refs.loc[pair, ["ref_obj1", "ref_obj2"]].to_numpy(dtype=float)
    front = pd.read_csv(SIM / f"contrast_front_{pair}.csv")[objs].to_numpy(float)
    cloud_pts = cloud.loc[cloud["feasible"].astype(bool), objs].to_numpy(float)
    polished = hypervolume(front, ref)
    cloud_hv = hypervolume(cloud_pts, ref)
    for name, mine, theirs in (
            ("polished", polished, refs.loc[pair, "ceiling_hv_polished"]),
            ("cloud", cloud_hv, refs.loc[pair, "ceiling_hv_cloud"])):
        assert abs(mine / theirs - 1) < 1e-4, (pair, name, mine, theirs)
    base = [front, cloud_pts]
    union = [feasible_points(df, objs) for k in union_keys for df in runs[k]]
    best_known = hypervolume(np.vstack(base + union), ref)
    bo_only = hypervolume(
        np.vstack(base + [feasible_points(df, objs) for df in runs["bo"]]), ref)

    finals = {k: np.array([hypervolume(feasible_points(df, objs), ref)
                           for df in v]) for k, v in runs.items()}
    methods = {}
    for k, fin in finals.items():
        frac = 100 * fin / best_known
        best = np.array([feasible_points(df, objs).min(axis=0) for df in runs[k]])
        row = {"final_hv": fin.tolist(),
               "pct_best_known_mean": float(frac.mean()),
               "pct_best_known_sd": float(frac.std(ddof=1)),
               "pct_best_known_min": float(frac.min()),
               "pct_best_known_max": float(frac.max()),
               "pct_polished_mean": float(100 * fin.mean() / polished),
               f"best_{objs[0]}_mean": float(best[:, 0].mean()),
               f"best_{objs[1]}_mean": float(best[:, 1].mean())}
        if k != "bo":
            row.update(exact_tests(finals["bo"], fin))
        methods[k] = row
    return {"objectives": objs, "reference_point": ref.tolist(),
            "polished_front_hv": polished, "cloud_hv": cloud_hv,
            "best_known_reference_hv": best_known,
            "best_known_over_polished": best_known / polished,
            "hv_added_by_bo_points": bo_only - hypervolume(np.vstack(base), ref),
            "n_cloud": int(len(cloud)),
            "n_cloud_feasible": int(cloud["feasible"].astype(bool).sum()),
            "methods": methods}, finals, best_known


def cross_checks(env_runs, env_stats, strain_finals, strain_runs):
    """Compare the recomputation with the committed PR #33 artifacts."""
    out = {}
    objs = PAIRS["envelope"]
    worst = 0.0
    for runs in env_runs.values():
        for df in runs:
            mine = hypervolume(feasible_points(df, objs),
                               np.array(env_stats["reference_point"]))
            worst = max(worst, abs(mine - df["hv"].iloc[-1]) / max(mine, 1e-12))
    assert worst < 1e-5, worst
    out["envelope_max_rel_diff_vs_committed_running_hv"] = worst

    summ = pd.read_csv(SIM / "bo_contrast_envelope_summary.csv")
    key = {"botorch": "bo", **{s: f"{s}_printable" for s in BASELINES}}
    worst = 0.0
    for _, r in summ.iterrows():
        mine = np.mean([hypervolume(feasible_points(df, objs),
                                    np.array(env_stats["reference_point"]))
                        for df in env_runs[key[r["strategy"]]]])
        worst = max(worst, abs(mine / r["final_hv_mean"] - 1))
    assert worst < 1e-5, worst
    out["envelope_max_rel_diff_vs_committed_summary"] = worst

    seeds = pd.read_csv(SIM / "bo_contrast_strain_era_rescored_seeds.csv")
    worst = 0.0
    for k, fin in strain_finals.items():
        theirs = seeds.loc[seeds["strategy"] == ("botorch" if k == "bo" else k),
                           "final_hv"].to_numpy()
        worst = max(worst, float(np.max(np.abs(np.sort(theirs) - np.sort(fin)))))
    assert worst < 1e-6, worst
    out["strain_max_abs_diff_vs_committed_rescore"] = worst

    audit = pd.read_csv(SIM / "audits/synthetic_audit_physics.csv").iloc[0]
    rel = abs(env_stats["best_known_reference_hv"]
              / audit["best_known_reference_hv"] - 1)
    assert rel < 1e-6, rel
    out["envelope_best_known_rel_diff_vs_audit"] = rel

    names = ["H_over_R", "H_over_strut_d", "cable_over_strut_d", "twist_deg"]
    r0 = [df.loc[df["round"] == 0, names].to_numpy().round(9)
          for df in env_runs["bo"]]
    dup = sum(np.array_equal(a, b) for i, a in enumerate(r0) for b in r0[i + 1:])
    assert dup == 0
    out["identical_round0_batches_across_bo_seeds"] = dup
    out["evaluations_per_run"] = BUDGET
    return out


def fmt_p(p):
    if p < 1e-3:
        mant, ex = f"{p:.1e}".split("e")
        return rf"${mant}\times10^{{{int(ex)}}}$"
    return f"{p:.2g}"


def main_table(env, strain):
    rows = []
    for k in ["bo"] + BASELINES:
        e = env["methods"][k if k == "bo" else f"{k}_printable"]
        s = strain["methods"][k]
        if k == "bo":
            cells = [SHORT[k], rf"{e['pct_best_known_mean']:.1f} $\pm$ "
                     rf"{e['pct_best_known_sd']:.1f}", "", "",
                     rf"{s['pct_best_known_mean']:.1f} $\pm$ "
                     rf"{s['pct_best_known_sd']:.1f}", ""]
        else:
            cells = [SHORT[k], rf"{e['pct_best_known_mean']:.1f} $\pm$ "
                     rf"{e['pct_best_known_sd']:.1f}",
                     fmt_p(e["mannwhitney_exact_p"]), f"{e['paired_wins']}/10",
                     rf"{s['pct_best_known_mean']:.1f} $\pm$ "
                     rf"{s['pct_best_known_sd']:.1f}",
                     fmt_p(s["mannwhitney_exact_p"])]
        rows.append(" & ".join(cells) + r" \\")
    return "\n".join([
        "% Generated by scripts/figures/sim_campaign_tables.py; do not edit.",
        r"\begin{tabular}{@{}lccccc@{}}",
        r"  \toprule",
        r"  & \multicolumn{3}{c}{$t_{180}$ + envelope} "
        r"& \multicolumn{2}{c}{$t_{180}$ + strain} \\",
        r"  \cmidrule(lr){2-4}\cmidrule(l){5-6}",
        r"  Method & HV (\%) & $p$ & Wins & HV (\%) & $p$ \\",
        r"  \midrule",
        *["  " + r for r in rows],
        r"  \bottomrule",
        r"\end{tabular}", ""])


def si_table(env):
    rows = []
    for k in ["bo"] + BASELINES:
        modes = ["bo"] if k == "bo" else [f"{k}_printable", f"{k}_plain"]
        for key in modes:
            m = env["methods"][key]
            mode = ("" if k == "bo" else
                    ("filtered" if key.endswith("printable") else "plain"))
            p = "" if k == "bo" else fmt_p(m["mannwhitney_exact_p"])
            wins = "" if k == "bo" else f"{m['paired_wins']}/10"
            rows.append(" & ".join([
                LABEL[k] if (k == "bo" or key.endswith("printable")) else "",
                mode,
                rf"{m['pct_best_known_mean']:.1f} $\pm$ {m['pct_best_known_sd']:.1f}",
                rf"{m['pct_best_known_min']:.1f} to {m['pct_best_known_max']:.1f}",
                f"{m['best_t180_mean']:.3f}",
                f"{m['best_envelope_cm3_mean']:.1f}", p, wins]) + r" \\")
    return "\n".join([
        "% Generated by scripts/figures/sim_campaign_tables.py; do not edit.",
        r"\begin{tabular}{@{}llcccccc@{}}",
        r"  \toprule",
        r"  Method & Mode & HV (\%) & Range (\%) & Best $t_{180}$ "
        r"& Min.\ envelope (cm$^3$) & $p$ & Wins \\",
        r"  \midrule",
        *["  " + r for r in rows],
        r"  \bottomrule",
        r"\end{tabular}", ""])


def figure(env, env_finals, env_runs, strain, strain_finals, cloud):
    objs = PAIRS["envelope"]
    ref = np.array(env["reference_point"])
    bk = env["best_known_reference_hv"]
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED,
                         "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6), dpi=300,
                             gridspec_kw={"width_ratios": [1.15, 1.0, 1.15]})

    # (a) running hypervolume of the envelope pair
    ax = axes[0]
    x = np.arange(1, BUDGET + 1)
    for k in BASELINES + ["bo"]:
        key = k if k == "bo" else f"{k}_printable"
        traces = np.vstack([[100 * hypervolume(
            feasible_points(df.iloc[:i], objs), ref) / bk for i in x]
            for df in env_runs[key]])
        mean, sd = traces.mean(axis=0), traces.std(axis=0, ddof=1)
        if k == "bo":
            ax.fill_between(x, mean - sd, mean + sd, color=BO_BLUE, alpha=0.18,
                            lw=0)
            ax.plot(x, mean, color=BO_BLUE, lw=2, label=LABEL[k])
        else:
            ax.plot(x, mean, color=SAMPLER_GRAY, lw=1.3, ls=SAMPLER_DASH[k],
                    label=LABEL[k])
    ax.axvline(9.5, color=MUTED, lw=0.6, ls=(0, (2, 2)))
    ax.text(10.4, 97, "model batches begin", fontsize=6.3, color=MUTED,
            va="top")
    ax.set_xlim(1, BUDGET)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Simulated designs evaluated")
    ax.set_ylabel("Hypervolume (% of best-known)")
    ax.legend(fontsize=6.3, frameon=False, loc="lower right",
              bbox_to_anchor=(1.0, 0.04))
    ax.grid(alpha=0.25, lw=0.4)
    ax.set_title("(a)", loc="left", fontsize=8.5, fontweight="bold")

    # (b) final hypervolume per seed, both objective pairs
    ax = axes[1]
    rng = np.random.default_rng(7)
    order = ["bo"] + BASELINES
    for j, (pair_finals, stats, tag, offset) in enumerate((
            ({k: env_finals[k if k == "bo" else f"{k}_printable"]
              for k in order}, env, "envelope", -0.19),
            (strain_finals, strain, "strain", 0.19))):
        for i, k in enumerate(order):
            v = 100 * pair_finals[k] / stats["best_known_reference_hv"]
            colour = BO_BLUE if k == "bo" else SAMPLER_GRAY
            marker = "o" if tag == "envelope" else "^"
            face = colour if tag == "envelope" else "white"
            xs = i + offset + rng.uniform(-0.07, 0.07, len(v))
            ax.scatter(xs, v, s=9, marker=marker, facecolor=face,
                       edgecolor=colour, lw=0.7, zorder=3)
            ax.hlines(v.mean(), i + offset - 0.13, i + offset + 0.13,
                      color=INK, lw=1.2, zorder=4)
    ax.scatter([], [], s=12, marker="o", color=SAMPLER_GRAY,
               label="$t_{180}$ + envelope")
    ax.scatter([], [], s=12, marker="^", facecolor="white",
               edgecolor=SAMPLER_GRAY, label="$t_{180}$ + strain (control)")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["BO", "Random", "Sobol", "LHS", "Compass"],
                       fontsize=6.5, rotation=30, ha="right",
                       rotation_mode="anchor")
    ax.set_ylim(50, 100)
    ax.set_ylabel("Final hypervolume (% of best-known)")
    ax.legend(fontsize=6.3, frameon=False, loc="lower left")
    ax.grid(alpha=0.25, lw=0.4, axis="y")
    ax.set_title("(b)", loc="left", fontsize=8.5, fontweight="bold")

    # (c) where the budget went, envelope pair, all seeds pooled
    ax = axes[2]
    feas = cloud[cloud["feasible"].astype(bool)]
    ax.scatter(feas[objs[0]], feas[objs[1]], s=1, color="#d5d4cf", alpha=0.35,
               lw=0, rasterized=True, label="Reference cloud")
    samp = np.vstack([feasible_points(df, objs) for k in BASELINES
                      for df in env_runs[f"{k}_printable"]])
    ax.scatter(samp[:, 0], samp[:, 1], s=4, color=SAMPLER_GRAY, alpha=0.6,
               lw=0, label="Samplers (pooled)")
    bo = np.vstack([feasible_points(df, objs) for df in env_runs["bo"]])
    ax.scatter(bo[:, 0], bo[:, 1], s=4, color=BO_BLUE, alpha=0.7, lw=0,
               label="BO")
    front = pd.read_csv(SIM / "contrast_front_envelope.csv")
    front = front.sort_values(objs[0])
    ax.step(front[objs[0]], front[objs[1]], where="post", color=INK, lw=1.0,
            label="Reference front")
    ax.set_xlabel("$t_{180}$ (simulated)")
    ax.set_ylabel("Envelope volume (cm$^3$)")
    ax.set_ylim(0, 260)
    ax.legend(fontsize=6.3, loc="upper right", markerscale=2.0,
              frameon=True, facecolor="white", edgecolor="none",
              framealpha=0.9)
    ax.grid(alpha=0.25, lw=0.4)
    ax.set_title("(c)", loc="left", fontsize=8.5, fontweight="bold")

    fig.tight_layout(w_pad=1.2)
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def main():
    refs = pd.read_csv(SIM / "contrast_refs.csv").set_index("pair")
    cloud = pd.read_csv(SIM / "contrast_cloud_ratios.csv.gz")

    env_runs = {"bo": load_runs(SIM / "envelope/contrast_bo_envelope_seed{k}.csv")}
    for mode in ("printable", "plain"):
        for s in BASELINES:
            env_runs[f"{s}_{mode}"] = load_runs(
                SIM / f"envelope/contrast_baseline_{s}_{mode}_envelope_seed{{k}}.csv")
    strain_runs = {k: load_runs(SIM / "strain-era" / pat)
                   for k, pat in STRAIN_FILES.items()}

    env, env_finals, _ = score_pair(
        "envelope", env_runs, ["bo"] + [f"{s}_printable" for s in BASELINES],
        cloud, refs)
    strain, strain_finals, _ = score_pair(
        "strain", strain_runs, ["bo"] + BASELINES, cloud, refs)

    objs = PAIRS["envelope"]
    ref = np.array(env["reference_point"])
    r0 = 100 * np.array([hypervolume(feasible_points(
        df[df["round"] == 0], objs), ref) for df in env_runs["bo"]]) \
        / env["best_known_reference_hv"]
    env["bo_round0_pct_best_known_range"] = [float(r0.min()), float(r0.max())]
    union_all = np.vstack(
        [pd.read_csv(SIM / "contrast_front_envelope.csv")[objs].to_numpy(float),
         cloud.loc[cloud["feasible"].astype(bool), objs].to_numpy(float)]
        + [feasible_points(df, objs) for v in env_runs.values() for df in v])
    env["best_known_including_plain_mode_hv"] = hypervolume(union_all, ref)

    screen = pd.read_csv(SIM / "contrast_screen.csv").set_index("pair")
    stats = {"source": "origin/copilot/explore-simulations-for-tensegrity @ 94e53a8",
             "budget": BUDGET, "seeds": SEEDS,
             "envelope": env, "strain_control": strain,
             "screen": screen.reset_index().to_dict(orient="records"),
             "cross_checks": cross_checks(env_runs, env, strain_finals,
                                          strain_runs)}
    printable = [env["methods"][f"{s}_printable"]["pct_best_known_mean"]
                 for s in BASELINES]
    stats["headline"] = {
        "bo_pct": env["methods"]["bo"]["pct_best_known_mean"],
        "baseline_pct_range": [min(printable), max(printable)],
        "exact_mannwhitney_p_max": max(env["methods"][f"{s}_printable"]
                                       ["mannwhitney_exact_p"] for s in BASELINES),
        "paired_wins_min": min(env["methods"][f"{s}_printable"]["paired_wins"]
                               for s in BASELINES),
        "strain_bo_pct": strain["methods"]["bo"]["pct_best_known_mean"],
        "strain_baseline_pct_range": [
            min(strain["methods"][s]["pct_best_known_mean"] for s in BASELINES),
            max(strain["methods"][s]["pct_best_known_mean"] for s in BASELINES)],
        "strain_exact_mannwhitney_p_range": [
            min(strain["methods"][s]["mannwhitney_exact_p"] for s in BASELINES),
            max(strain["methods"][s]["mannwhitney_exact_p"] for s in BASELINES)],
    }
    OUT_JSON.write_text(json.dumps(stats, indent=2) + "\n")

    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "sim-campaign.tex").write_text(main_table(env, strain))
    (TABLES / "si-sim-campaign.tex").write_text(si_table(env))
    figure(env, env_finals, env_runs, strain, strain_finals, cloud)

    h = stats["headline"]
    print(f"envelope pair: BO {h['bo_pct']:.1f}% of best-known "
          f"({env['best_known_reference_hv']:.3f}); samplers "
          f"{h['baseline_pct_range'][0]:.1f} to {h['baseline_pct_range'][1]:.1f}%; "
          f"exact p <= {h['exact_mannwhitney_p_max']:.3g}; "
          f"wins >= {h['paired_wins_min']}/10")
    print(f"strain control: BO {h['strain_bo_pct']:.1f}%; samplers "
          f"{h['strain_baseline_pct_range'][0]:.1f} to "
          f"{h['strain_baseline_pct_range'][1]:.1f}%; exact p "
          f"{h['strain_exact_mannwhitney_p_range'][0]:.3g} to "
          f"{h['strain_exact_mannwhitney_p_range'][1]:.3g}")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}, manuscript/tables/sim-campaign.tex, "
          f"manuscript/tables/si-sim-campaign.tex, {OUT_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
