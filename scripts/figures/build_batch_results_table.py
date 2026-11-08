"""Build the model-recommended batch-results table (tab:batch-results).

Writes manuscript/tables/batch-results.tex, the tabular that
manuscript-body.tex pulls in with \\input{tables/batch-results}. The caption
and label stay in the body so the prose can be edited there.

Every value is recomputed from the committed snapshots in manuscript/data/
(standard library csv only, no pandas):

    t3-prism-bo-round{1,3,4}-print-key.csv     trial <-> specimen, weighed mass
    t3-prism-bo-round{1,3,4}-drop-results.csv  stabilized t180, sd, e, drift flag
    t3-prism-bo-round{1,3,4}-designs.csv       post-projection (as-printed) geometry
                                               and infill, batch filament settings
    t3-prism-bo-round{1,3,4}-predictions.csv   posterior-mean t180 archived at
                                               recommendation time
    t3-prism-slicer-process-settings.csv       batch-2 filament settings, read back
                                               out of the archived slicer project

File-name convention (campaign branch): round1 = physical batch 2 (r2d2c),
round3 = batch 3 (drran, first prints only), round4 = batch 4 (corny).

The script stops with an error if the inputs disagree with each other: the
print-key mass against the drop-results mass, the drop-results geometry
against the design file's post-projection geometry, the commanded geometry
against the archived predictions, and a batch's filament settings against
themselves (one value per print job). With --compare FILE it also checks every
number against an earlier hand-typed version of the table (matched by trial)
and prints the mismatch count.

The rebound column is the second objective as reported from 2026-10-29, the
mass-weighted rebound index I_reb = m * e**2 in mg (m in grams). The
first-power E_reb = e * m * g * h in mJ per drop (g = 9.80665 m/s^2, h =
1.524 m, the 60 in drop height), which batches 2 to 4 were recommended under,
follows the campaign code (bo/t3_prism_bo_campaign.py at bbf7a62) and is
still computed for --compare against the older hand-typed table.

Usage:
    python scripts/figures/build_batch_results_table.py
    python scripts/figures/build_batch_results_table.py --compare old-body.tex
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "manuscript" / "data"
OUT = ROOT / "manuscript" / "tables" / "batch-results.tex"

G_M_S2 = 9.80665
DROP_H_M = 1.524
# A session counts as erratic (double dagger) when its per-drop coefficient of
# variation in t180 exceeds this and it carries no drift flag (corny6 only).
ERRATIC_CV = 0.015

BATCHES = [
    # physical batch, campaign file tag, mass basis for the group line
    (2, "round1", "constant solid mass, infill not varied"),
    (3, "round3", "constant printed mass (20.23 g)"),
    (4, "round4", "constant printed mass (20.23 g)"),
]
BATCH2_SLICER_PROJECT = "t3-prism-bo-round1.H2D-MM-PLAstruts-TPUcables_manual-supports.3mf"


def read(name):
    with open(DATA / name, newline="") as fh:
        return list(csv.DictReader(fh))


def close(a, b, tol):
    return abs(float(a) - float(b)) <= tol


def fail(msg):
    sys.exit(f"build_batch_results_table: {msg}")


def batch2_filament():
    rows = [r for r in read("t3-prism-slicer-process-settings.csv")
            if r["project"] == BATCH2_SLICER_PROJECT and r["used_on_plate"] == "True"]
    by_type = {r["filament_type"]: r for r in rows}
    if sorted(by_type) != ["PLA", "TPU"] or len(rows) != 2:
        fail("batch-2 slicer project should have exactly one PLA and one TPU slot in use")
    return {
        "pla_T": float(by_type["PLA"]["nozzle_temp_C"]),
        "pla_Q": float(by_type["PLA"]["max_volumetric_mm3_s"]),
        "tpu_T": float(by_type["TPU"]["nozzle_temp_C"]),
        "tpu_Q": float(by_type["TPU"]["max_volumetric_mm3_s"]),
    }


def design_filament(designs):
    out = {}
    for key, col in [("pla_T", "pla_nozzle_temp_C"), ("pla_Q", "pla_flow_mm3_s"),
                     ("tpu_T", "tpu_nozzle_temp_C"), ("tpu_Q", "tpu_flow_mm3_s")]:
        values = {float(d[col]) for d in designs.values()}
        if len(values) != 1:
            fail(f"{col} takes {len(values)} values in one batch; expected one per print job")
        out[key] = values.pop()
    return out


def load_batch(batch, tag):
    key = {r["print_id"]: r for r in read(f"t3-prism-bo-{tag}-print-key.csv")}
    drops = {r["specimen"]: r for r in read(f"t3-prism-bo-{tag}-drop-results.csv")}
    trial_col = "source_trial" if tag == "round1" else "trial_index"
    designs = {int(d[trial_col]): d for d in read(f"t3-prism-bo-{tag}-designs.csv")}
    preds = {int(p["trial_index"]): p for p in read(f"t3-prism-bo-{tag}-predictions.csv")}

    rows = []
    for sid, d in drops.items():
        k = key[sid]
        trial = int(k["source_trial"])
        if "trial" in d and int(d["trial"]) != trial:
            fail(f"{sid}: drop-results trial {d['trial']} != print-key trial {trial}")
        des, pred = designs[trial], preds[trial]
        mass = float(k["mass_g_with_label"])
        if not close(mass, d["mass_g"], 0.005):
            fail(f"{sid}: print-key mass {mass} != drop-results mass {d['mass_g']}")
        # post-projection geometry, cross-checked against the drop-results copy
        geom = {
            "R": float(des["R_print_mm"]), "H": float(des["H_print_mm"]),
            "twist": float(des["twist_deg"]), "ds": float(des["strut_d_print_mm"]),
            "dt": float(des["cable_d_print_mm"]),
        }
        for g, col, tol in [("R", "R_mm", 0.006), ("H", "H_mm", 0.006),
                            ("twist", "twist_deg", 0.05), ("ds", "strut_d_mm", 0.006),
                            ("dt", "cable_d_mm", 0.006)]:
            if not close(geom[g], d[col], tol):
                fail(f"{sid}: design-file {g} {geom[g]} != drop-results {col} {d[col]}")
        # commanded (pre-projection) geometry must match the archived prediction row
        for col in ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"):
            if not close(des[col], pred[col], 1e-3):
                fail(f"trial {trial}: design {col} {des[col]} != prediction {pred[col]}")
        t_mean, t_sd = float(d["t180_mean"]), float(d["t180_sd"])
        e = float(d["e_rebound_mean"])
        drift = d["t_drift_flag"] == "True"
        rows.append({
            "batch": batch, "trial": trial, "specimen": sid, **geom,
            "infill_s": des.get("strut_infill_pct"), "infill_t": des.get("tpu_infill_pct"),
            "mass": mass, "t180": t_mean, "t180_sd": t_sd,
            "e_reb": e * mass * G_M_S2 * DROP_H_M,
            "i_reb": 1000.0 * mass * e ** 2,
            "pred": float(pred["pred_t180_mean"]),
            "drift": drift, "erratic": (not drift) and t_sd / t_mean > ERRATIC_CV,
        })
    if len(rows) != 9 or len({r["trial"] for r in rows}) != 9:
        fail(f"batch {batch}: expected nine first-print specimens on nine trials")
    filament = batch2_filament() if tag == "round1" else design_filament(designs)
    return sorted(rows, key=lambda r: r["trial"]), filament


def fmt_num(x):
    """Drop a trailing .0 so 220.0 prints as 220 and 2.5 stays 2.5."""
    return f"{x:g}"


def group_line(batch, basis, fil, ncol):
    text = (f"Batch {batch}, {basis}. PLA at {fmt_num(fil['pla_T'])}\\,\\si{{\\celsius}} "
            f"and \\SI{{{fmt_num(fil['pla_Q'])}}}{{mm^3/s}}, TPU at "
            f"{fmt_num(fil['tpu_T'])}\\,\\si{{\\celsius}} and "
            f"\\SI{{{fmt_num(fil['tpu_Q'])}}}{{mm^3/s}}.")
    return f"    \\multicolumn{{{ncol}}}{{@{{}}l}}{{\\textit{{{text}}}}} \\\\"


def table_row(r):
    flag = r"$^\dagger$" if r["drift"] else (r"$^\ddagger$" if r["erratic"] else "")
    inf_s = r["infill_s"] if r["infill_s"] is not None else "{-}"
    inf_t = r["infill_t"] if r["infill_t"] is not None else "{-}"
    cells = [
        f"{r['trial']}{flag}", f"{r['R']:.1f}", f"{r['H']:.1f}", f"{r['twist']:.1f}",
        f"{r['ds']:.2f}", f"{r['dt']:.2f}", f"{inf_s}", f"{inf_t}", f"{r['mass']:.2f}",
        f"{r['t180']:.4f}", f"{r['t180_sd']:.4f}", f"{r['i_reb']:.1f}", f"{r['pred']:.3f}",
    ]
    return "    " + " & ".join(cells) + r" \\"


HEADER = r"""% Generated by scripts/figures/build_batch_results_table.py from the CSV
% snapshots in manuscript/data/. Do not edit by hand; rerun the script.
\footnotesize
\setlength{\tabcolsep}{7.5pt}
\begin{tabular}{@{}lS[table-format=2.1]S[table-format=3.1]S[table-format=2.1]S[table-format=2.2]S[table-format=1.2]S[table-format=2.0]S[table-format=2.0]S[table-format=2.2]S[table-format=1.4]@{\,$\pm$\,}S[table-format=1.4]S[table-format=2.1]S[table-format=1.3]@{}}
  \toprule
  Trial & {$R$} & {$H$} & {$\theta$} & {$d_s$} & {$d_t$} &
  \multicolumn{2}{c}{Infill (\%)} & {$m$} & \multicolumn{2}{c}{$t_{180}$} &
  {$I_{\mathrm{reb}}$} & {Pred.} \\
  \cmidrule(lr){7-8}
  & {(mm)} & {(mm)} & {(deg)} & {(mm)} & {(mm)} & {PLA} & {TPU} & {(g)} &
  \multicolumn{2}{c}{mean $\pm$ sd} & {(mg)} & {$t_{180}$} \\"""
NCOL = 13


def build():
    lines = [HEADER]
    all_rows = []
    for batch, tag, basis in BATCHES:
        rows, fil = load_batch(batch, tag)
        all_rows.extend(rows)
        lines.append("  \\midrule")
        lines.append(group_line(batch, basis, fil, NCOL))
        lines.extend(table_row(r) for r in rows)
    lines.append("  \\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n", all_rows


def compare(rows, tex_path):
    """Check each row against an older hand-typed table (Batch & Article & Trial &
    Mass & t180 & sd & E_reb & Pred) in tex_path, matched by trial."""
    text = Path(tex_path).read_text()
    block = text[text.index(r"\label{tab:batch-results}"):]
    block = block[:block.index(r"\end{tabular}")]
    pat = re.compile(r"^\s*(\d)\s*&\s*(\w+)\S*\s*&\s*(\d+)\s*&\s*([\d.]+)\s*&\s*([\d.]+)"
                     r"\s*&\s*([\d.]+)\s*&\s*([\d.]+)\s*&\s*([\d.]+)\s*\\\\", re.M)
    old = {int(m.group(3)): m.groups() for m in pat.finditer(block)}
    mismatches, checked = 0, 0
    for r in rows:
        o = old.get(r["trial"])
        if o is None:
            print(f"trial {r['trial']}: missing from the old table")
            mismatches += 1
            continue
        new = [str(r["batch"]), r["specimen"], str(r["trial"]), f"{r['mass']:.2f}",
               f"{r['t180']:.4f}", f"{r['t180_sd']:.4f}", f"{r['e_reb']:.1f}", f"{r['pred']:.3f}"]
        for name, a, b in zip(["batch", "specimen", "trial", "mass", "t180", "sd", "E_reb", "pred"], o, new):
            checked += 1
            if a != b:
                mismatches += 1
                print(f"trial {r['trial']} {name}: old {a} new {b}")
    if len(old) != len(rows):
        mismatches += abs(len(old) - len(rows))
        print(f"row count: old {len(old)} new {len(rows)}")
    print(f"compared {len(rows)} rows, {checked} values: {mismatches} mismatches")
    return mismatches


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--compare", metavar="TEX", help="older body .tex holding a hand-typed tab:batch-results")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    tex, rows = build()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tex)
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} ({len(rows)} rows)")
    if args.compare:
        sys.exit(1 if compare(rows, args.compare) else 0)


if __name__ == "__main__":
    main()
