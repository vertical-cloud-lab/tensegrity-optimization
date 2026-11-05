"""Measured campaign record for the manuscript figures, from manuscript/data/.

Reads only the committed snapshots in ``manuscript/data/`` (no Ax, no
refit) and reproduces the campaign branch's own bookkeeping
(``bo/t3_prism_bo_campaign.py`` on ``claude/issue-98-20260821-0103`` at
65ff978):

* the 35 articles of the four measured batches, each repeated batch-3
  design at its first print (drran), and the unmapped seed article amdjwm
  left out because it has no weighed mass;
* the second objective, the mass-weighted rebound index I_reb = m * e**2
  in mg, where e is the session's mean rebound fraction (column
  ``e_rebound_mean``) and m the article's weighed mass, and its first-power
  form E_reb = e * m * g * h in mJ per drop (g = 9.80665 m/s^2, h = 1.524 m,
  60 in), which batches 2 to 4 were recommended under and which the
  archived predictions are in;
* the print geometry of each article (post-projection R, H, twist, strut
  and cable diameters), taken from the drop-results tables, which carry the
  as-printed design values.

Used by build_front_evolution_figure.py, build_batch4_pred_vs_meas_figure.py,
build_design_space_figure.py and build_seed_designs_figure.py.
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "manuscript" / "data"

G_M_S2 = 9.80665
DROP_H_M = 1.524

# (batch number, drop-results file, print-key file or None)
BATCH_FILES = [
    (1, "t3-prism-bo-batch-drop-results.csv", None),
    (2, "t3-prism-bo-round1-drop-results.csv", "t3-prism-bo-round1-print-key.csv"),
    (3, "t3-prism-bo-round3-drop-results.csv", "t3-prism-bo-round3-print-key.csv"),
    (4, "t3-prism-bo-round4-drop-results.csv", "t3-prism-bo-round4-print-key.csv"),
]


def read_csv(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _num(text: str) -> float | None:
    text = (text or "").strip()
    return float(text) if text else None


def load_articles() -> list[dict]:
    """All articles that enter the campaign front, in batch then file order.

    Each dict carries: print_id, batch, spec (seed only), trial (batches
    2 to 4), mass_g, t180, t180_sd, i_reb_mg, e_reb_mJ, drift (bool), and
    the print geometry R, H, twist, d_s, d_t (mm, degrees).
    """
    seed_key = {r["print_id"]: r for r in read_csv("t3-prism-bo-batch-print-key.csv")}
    out = []
    for batch, results_name, key_name in BATCH_FILES:
        key = ({r["print_id"]: r for r in read_csv(key_name)} if key_name else {})
        for row in read_csv(results_name):
            pid = row["specimen"].strip()
            mass = _num(row["mass_g"])
            spec = (row.get("spec") or "").strip()
            if batch == 1 and (not spec or mass is None):
                continue  # amdjwm: no design mapping and no weighed mass
            if batch > 1 and pid not in key:
                continue
            e = float(row["e_rebound_mean"])
            art = {
                "print_id": pid,
                "batch": batch,
                "spec": spec if batch == 1 else None,
                "trial": int(key[pid]["source_trial"]) if batch > 1 else None,
                "mass_g": mass,
                "t180": float(row["t180_mean"]),
                "t180_sd": float(row["t180_sd"]),
                "i_reb_mg": 1000.0 * mass * e ** 2,
                "e_reb_mJ": e * mass * G_M_S2 * DROP_H_M,
                "drift": (row.get("t_drift_flag") or "").strip() == "True",
            }
            if batch == 1:
                k = seed_key[pid]
                art.update(R=float(k["R_print_mm"]), H=float(k["H_print_mm"]),
                           twist=float(k["twist_deg"]),
                           d_s=float(k["strut_d_print_mm"]),
                           d_t=float(k["cable_d_print_mm"]))
            else:
                art.update(R=float(row["R_mm"]), H=float(row["H_mm"]),
                           twist=float(row["twist_deg"]),
                           d_s=float(row["strut_d_mm"]),
                           d_t=float(row["cable_d_mm"]))
            out.append(art)
    return out


def seed_designs() -> list[dict]:
    """The nine Sobol seed designs (specs 00 to 08) as printed.

    One row per spec from the seed print key, preferring the article that was
    drop-tested (spec 08 was printed three times; bag26v is the tested one).
    """
    tested = {r["specimen"].strip() for r in read_csv("t3-prism-bo-batch-drop-results.csv")}
    by_spec: dict[str, dict] = {}
    for r in read_csv("t3-prism-bo-batch-print-key.csv"):
        spec = r["specimen"].strip()
        if spec == "S0":
            continue
        prev = by_spec.get(spec)
        if prev is None or (r["print_id"] in tested and prev["print_id"] not in tested):
            by_spec[spec] = r
    rows = []
    for spec in sorted(by_spec, key=int):
        r = by_spec[spec]
        rows.append({
            "spec": f"{int(spec):02d}", "print_id": r["print_id"],
            "tested": r["print_id"] in tested,
            "R": float(r["R_print_mm"]), "H": float(r["H_print_mm"]),
            "twist": float(r["twist_deg"]), "d_s": float(r["strut_d_print_mm"]),
            "d_t": float(r["cable_d_print_mm"]),
        })
    return rows


def pareto_mask(t: list[float], e: list[float]) -> list[bool]:
    """Non-dominated mask for joint minimization of (t, e)."""
    keep = []
    for i in range(len(t)):
        dominated = any(
            t[j] <= t[i] and e[j] <= e[i] and (t[j] < t[i] or e[j] < e[i])
            for j in range(len(t)))
        keep.append(not dominated)
    return keep


def hypervolume(t: list[float], e: list[float], ref=(1.35, 15.0)) -> float:
    """Dominated hypervolume under minimization (same staircase as the campaign)."""
    keep = pareto_mask(t, e)
    pts = sorted((ti, ei) for ti, ei, k in zip(t, e, keep) if k)
    hv = 0.0
    for i, (ti, ei) in enumerate(pts):
        if ti >= ref[0] or ei >= ref[1]:
            continue
        nxt = min(ref[0], pts[i + 1][0]) if i + 1 < len(pts) else ref[0]
        hv += max(0.0, nxt - ti) * (ref[1] - ei)
    return hv


# Shared look for the manuscript figures: Times-like text and math to match
# the asmejour body font, ink-black axes, no top/right spines.
STYLE = {
    "font.family": "STIXGeneral",
    "mathtext.fontset": "stix",
    "font.size": 8.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 400,
}

INK = "#0b0b0b"
GRAY = "#83827d"
FRONT_BLUES = ["#c3d7f0", "#8fb6e4", "#5b93da", "#2a78d6"]
PRED_ORANGE = "#eb6834"
PLA_BLACK = "#1f1f1f"
TPU_GREEN = "#2e9e4f"
