"""Violin plots (with jittered raw points) of the Sobol T3-prism measurements.

The Sobol T3-prism campaign (``sobol_t3_campaign.py``) writes one CSV of raw
simulation measurements per engine/tier under ``outputs/``.  This script reads
those CSVs back and renders Plotly violin plots that overlay *every raw point*
as a jittered swarm next to the distribution, which is the view asked for in
PR comment 4700384140 ("show some violin plots of the raw measurements ... use
jitter for the plots, plotting the raw points").

The Plotly call is ``plotly.express.violin(..., points="all", box=True)`` with
a non-zero ``jitter`` -- ``points="all"`` draws every underlying measurement
and ``jitter`` spreads them sideways so overlapping points stay visible.

Two figures are produced (PNG via kaleido + interactive HTML):

* ``sobol_t3_violin_objectives`` -- the Tier-C MuJoCo objectives the BO loop
  actually optimises (``F_peak``, ``SEA``, ``eta``), one violin per regime,
  faceted by objective so each keeps its own y-scale.
* ``sobol_t3_violin_engines`` -- the per-engine peak deceleration (g) across
  the C->B->A ladder (MuJoCo / PyBullet / PyChrono / Newton / PolyFEM) on a log
  y-axis, since the engines span ~1 g (PolyFEM, settles below the IPC barrier)
  to ~10^5 g (Newton/Warp).

Usage::

    python simulations/sobol_t3_violins.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px

_HERE = Path(__file__).resolve().parent
OUT_DIR = _HERE / "outputs"

# Consistent colours for the two load regimes.
REGIME_COLORS = {"crutch": "#1f77b4", "lander": "#d62728"}


def _read(name: str) -> pd.DataFrame | None:
    path = OUT_DIR / name
    if not path.exists():
        print(f"  (skip) {name} not found")
        return None
    return pd.read_csv(path)


# --------------------------------------------------------------------------
# Figure 1: Tier-C objectives, one violin per regime, faceted by objective.
# --------------------------------------------------------------------------
def violin_objectives() -> None:
    df = _read("sobol_t3_tierC.csv")
    if df is None:
        return
    if "feasible" in df.columns:
        df = df[df["feasible"] == 1]

    objectives = [
        ("F_peak_N", "F_peak (N)"),
        ("SEA_J_per_g", "SEA (J/g)"),
        ("eta", "eta (compaction efficiency)"),
    ]
    rows = []
    for regime in ("crutch", "lander"):
        for col, label in objectives:
            src = f"{regime}_{col}"
            if src not in df.columns:
                continue
            for val in df[src].dropna():
                rows.append({"regime": regime, "objective": label,
                             "value": float(val)})
    long = pd.DataFrame(rows)
    if long.empty:
        print("  (skip) no Tier-C objective columns found")
        return

    fig = px.violin(
        long, x="regime", y="value", color="regime",
        facet_col="objective", box=True, points="all",
        color_discrete_map=REGIME_COLORS,
        category_orders={"regime": ["crutch", "lander"]},
        title=(f"Tier-C MuJoCo objectives over {df.shape[0]} feasible Sobol "
               "T3-prism designs (raw points, jittered)"),
    )
    # points="all" + jitter spreads the raw measurements sideways.
    fig.update_traces(jitter=0.4, pointpos=0, marker=dict(size=3, opacity=0.5),
                      meanline_visible=True)
    fig.update_yaxes(matches=None, showticklabels=True)
    for ann in fig.layout.annotations:
        ann.text = ann.text.split("=")[-1]
    fig.update_layout(showlegend=False, width=1100, height=480,
                      template="plotly_white")
    _save(fig, "sobol_t3_violin_objectives")


# --------------------------------------------------------------------------
# Figure 2: per-engine peak deceleration (g) across the C->B->A ladder.
# --------------------------------------------------------------------------
def violin_engines() -> None:
    # (csv, column, engine label, tier)
    sources = [
        ("sobol_t3_pybullet.csv", "pybullet_peak_g", "PyBullet", "C"),
        ("sobol_t3_pychrono.csv", "pychrono_peak_g", "PyChrono", "C"),
        ("sobol_t3_tierB.csv", "newton_peak_g", "Newton/Warp", "B"),
        ("sobol_t3_tierA.csv", "polyfem_peak_g", "PolyFEM+IPC", "A"),
    ]
    rows = []
    for csv_name, col, engine, tier in sources:
        df = _read(csv_name)
        if df is None or col not in df.columns:
            continue
        for val in df[col].dropna():
            if float(val) > 0:  # log axis: drop non-positive
                rows.append({"engine": engine, "tier": tier,
                             "peak_g": float(val)})
    long = pd.DataFrame(rows)
    if long.empty:
        print("  (skip) no per-engine peak_g columns found")
        return

    order = [e for e in ["PyBullet", "PyChrono", "Newton/Warp", "PolyFEM+IPC"]
             if e in set(long["engine"])]
    fig = px.violin(
        long, x="engine", y="peak_g", color="tier",
        box=True, points="all", log_y=True,
        category_orders={"engine": order},
        labels={"peak_g": "peak deceleration (g)", "tier": "tier"},
        title=("Per-engine peak deceleration over the Sobol T3-prism subsets "
               "(raw points, jittered, log scale)"),
    )
    fig.update_traces(jitter=0.4, pointpos=0, marker=dict(size=4, opacity=0.6),
                      meanline_visible=True)
    fig.update_layout(width=900, height=520, template="plotly_white")
    _save(fig, "sobol_t3_violin_engines")


def _save(fig, stem: str) -> None:
    png = OUT_DIR / f"{stem}.png"
    html = OUT_DIR / f"{stem}.html"
    fig.write_image(str(png), scale=2)
    fig.write_html(str(html), include_plotlyjs="cdn")
    print(f"  wrote {png.relative_to(_HERE.parent)} and "
          f"{html.relative_to(_HERE.parent)}")


def main(argv=None) -> int:
    print("== Sobol T3-prism violin plots (raw measurements, jittered) ==")
    violin_objectives()
    violin_engines()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
