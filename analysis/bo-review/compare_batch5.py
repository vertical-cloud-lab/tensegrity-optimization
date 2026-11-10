"""Compare the batch-5 regenerations of ``regenerate_batch5.py``.

Reads the suggestions CSV of each variant (copied to ``data/batch5/``) and
the archived run-6 batch of the campaign branch, and writes
``data/batch5/comparison.csv`` / ``comparison.md``: per variant, the family
split, the predicted objectives, the printability flags, the filament point,
and the mean matched distance to the archived batch (Hungarian assignment on
the five shape coordinates scaled to their bounds).

Usage::

    python analysis/bo-review/compare_batch5.py --archived /tmp/campaign-me2/bo/t3-prism-bo-suggestions-round6.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "batch5"
SHAPE = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
BOUNDS = {"R_mm": (25, 40), "H_mm": (60, 110), "twist_deg": (40, 80),
          "strut_d_mm": (6, 12), "cable_d_mm": (3, 5.5)}
VARIANTS = ["control", "thresholds", "fixedfil", "both", "fixes"]
LABEL = {"archived": "archived run 6 (campaign branch, f66c363)",
         "control": "control: campaign settings, rerun here",
         "thresholds": "thresholds (1.35, 50 mg) + pinned qLogNEHVI",
         "fixedfil": "filament point fixed first (fixed_features)",
         "both": "thresholds + filament fixed first",
         "fixes": "thresholds + filament fixed first + noise learned"}


def family(r):
    if r.twist_deg >= 70 and r.R_mm >= 35:
        return "wide high-twist"
    if r.twist_deg <= 50 and r.H_mm >= 95:
        return "tall low-twist"
    return "intermediate"


def unit(df):
    return np.column_stack([(df[c] - BOUNDS[c][0]) / (BOUNDS[c][1] - BOUNDS[c][0])
                            for c in SHAPE])


def matched_distance(a, b):
    d = np.linalg.norm(unit(a)[:, None, :] - unit(b)[None, :, :], axis=-1)
    i, j = linear_sum_assignment(d)
    return float(d[i, j].mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archived", type=Path, required=True)
    a = ap.parse_args()
    batches = {"archived": pd.read_csv(a.archived)}
    for v in VARIANTS:
        p = OUT / f"suggestions-{v}.csv"
        if p.exists():
            batches[v] = pd.read_csv(p)
    obj2 = "m_e2_mg" if "pred_m_e2_mg_mean" in batches["archived"] else "e_reb_mJ"
    rows = []
    for name, df in batches.items():
        fam = df.apply(family, axis=1).value_counts()
        rows.append({
            "variant": name, "description": LABEL[name],
            "wide_high_twist": int(fam.get("wide high-twist", 0)),
            "tall_low_twist": int(fam.get("tall low-twist", 0)),
            "intermediate": int(fam.get("intermediate", 0)),
            "pred_t180_min": df.pred_t180_mean.min(), "pred_t180_max": df.pred_t180_mean.max(),
            "pred_t180_sd_mean": df.pred_t180_sd.mean(),
            f"pred_{obj2}_min": df[f"pred_{obj2}_mean"].min(),
            f"pred_{obj2}_max": df[f"pred_{obj2}_mean"].max(),
            f"pred_{obj2}_sd_mean": df[f"pred_{obj2}_sd"].mean(),
            "cable_below_3mm": int((~df.cable_bridge_ok.astype(bool)).sum()),
            "envelope_over_250cm3": int((~df.envelope_ok.astype(bool)).sum()),
            "filament_point": "/".join(f"{df[c].iloc[0]:g}" for c in
                                       ("pla_nozzle_temp_C", "pla_flow_mm3_s",
                                        "tpu_nozzle_temp_C", "tpu_flow_mm3_s")),
            "matched_shape_distance_to_archived": matched_distance(df, batches["archived"]),
            "matched_shape_distance_to_control": (matched_distance(df, batches["control"])
                                                  if "control" in batches else None),
            "identical_to_archived": bool(
                len(df) == len(batches["archived"]) and np.allclose(
                    df[SHAPE].to_numpy(), batches["archived"][SHAPE].to_numpy(), atol=1e-4)),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "comparison.csv", index=False, float_format="%.4g")
    md = ["| variant | wide high-twist / tall low-twist / other | pred. t180 (mean sd) | "
          f"pred. {obj2} (mean sd) | cable < 3 mm | envelope > 250 cm3 | "
          "shape distance to archived | to control |", "|---|---|---|---|---|---|---|---|"]
    for r in out.itertuples():
        md.append(
            f"| {r.description} | {r.wide_high_twist} / {r.tall_low_twist} / {r.intermediate} | "
            f"{r.pred_t180_min:.3f} to {r.pred_t180_max:.3f} ({r.pred_t180_sd_mean:.3f}) | "
            f"{getattr(r, f'pred_{obj2}_min'):.1f} to {getattr(r, f'pred_{obj2}_max'):.1f} "
            f"({getattr(r, f'pred_{obj2}_sd_mean'):.1f}) | {r.cable_below_3mm} | "
            f"{r.envelope_over_250cm3} | {r.matched_shape_distance_to_archived:.3f} | "
            + ("" if r.matched_shape_distance_to_control is None or
               np.isnan(r.matched_shape_distance_to_control)
               else f"{r.matched_shape_distance_to_control:.3f}") + " |")
    (OUT / "comparison.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    for name, df in batches.items():
        print(f"\n{name}:")
        print(df[["trial_index"] + SHAPE + ["strut_infill_pct", "tpu_infill_pct",
                                             "pred_t180_mean", f"pred_{obj2}_mean"]]
              .round(2).to_string(index=False))


if __name__ == "__main__":
    main()
