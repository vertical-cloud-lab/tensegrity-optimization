"""Visualize the T3-prism BO search space and its first Sobol batch.

Summarizes the *restricted* T3-prism-only design space defined in
``bo/t3_prism_sobol_batch.py`` on the PR #35 branch
(``copilot/get-bambu-sliced-print-t3-prism``): five continuous geometric
parameters, everything else frozen. Overlays the n=9, seed=0 Sobol batch
from ``bo/t3-prism-bo-batch.csv`` on that branch.

Top panel: per-parameter bound strips with the 9 sampled values.
Bottom panel: parallel coordinates linking each specimen across all five
parameters (lines shaded light-to-dark by specimen index, labeled at both
ends so identity never rides on color alone).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

# ---- Search space (bo/t3_prism_sobol_batch.py PARAMETERS) ------------------
PARAMS = [
    ("R_mm",       "Radius R",          25.0,  40.0, "mm"),
    ("H_mm",       "Height H",          60.0, 110.0, "mm"),
    ("twist_deg",  "Twist",             40.0,  80.0, "deg"),
    ("strut_d_mm", "Strut diameter",     6.0,  12.0, "mm"),
    ("cable_d_mm", "Cable diameter",     3.0,   5.5, "mm"),
]

# ---- Sobol batch (bo/t3-prism-bo-batch.csv, n=9 seed=0) --------------------
SPECIMENS = np.array([
    [32.1266,  89.6262, 59.7792,  7.8831, 5.3902],
    [33.7842,  80.0836, 77.4080, 10.8717, 3.0003],
    [38.9665,  99.9950, 47.6915,  7.0737, 3.9241],
    [25.1224,  72.0587, 65.1213, 10.1789, 4.6640],
    [27.6114, 104.1304, 70.4432,  9.2816, 4.4922],
    [36.3001,  63.2297, 52.9940,  6.4571, 4.0550],
    [35.9821,  96.4464, 62.1055, 11.6620, 3.4949],
    [30.1066,  74.8199, 44.4573,  8.5803, 4.9377],
    [29.0207, 100.8663, 63.7624,  6.1990, 3.1969],
])

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
BLUE = "#2a78d6"
BAND = "#eceae6"
# Ordinal blue ramp, steps 250 -> 650 (light -> dark) by specimen index.
RAMP = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
        "#256abf", "#1c5cab", "#184f95", "#104281"]


def norm(col: int, v: np.ndarray) -> np.ndarray:
    lo, hi = PARAMS[col][2], PARAMS[col][3]
    return (v - lo) / (hi - lo)


def main() -> None:
    fig, (ax_strip, ax_par) = plt.subplots(
        2, 1, figsize=(11.5, 9.2), height_ratios=[1.0, 1.15],
        facecolor=SURFACE,
    )
    fig.subplots_adjust(left=0.16, right=0.91, top=0.865, bottom=0.125, hspace=0.46)

    fig.suptitle(
        "T3-prism BO campaign — search space and first Sobol batch (n = 9, seed = 0)",
        x=0.16, y=0.975, ha="left", fontsize=14, fontweight="bold", color=INK,
    )
    fig.text(
        0.16, 0.935,
        "5 tunable geometric parameters (bo/t3_prism_sobol_batch.py, PR #35); "
        "all other variables frozen",
        fontsize=9.5, color=INK2,
    )

    # ---- Top: bound strips with sampled values -----------------------------
    ax_strip.set_facecolor(SURFACE)
    n_par = len(PARAMS)
    for i, (_, label, lo, hi, unit) in enumerate(PARAMS):
        y = n_par - 1 - i
        ax_strip.barh(y, 1.0, left=0.0, height=0.52, color=BAND, zorder=1)
        ax_strip.scatter(
            norm(i, SPECIMENS[:, i]), np.full(len(SPECIMENS), y),
            s=64, color=BLUE, edgecolors=SURFACE, linewidths=1.5, zorder=3,
        )
        fmt = "g"
        ax_strip.text(-0.015, y, f"{lo:{fmt}}", ha="right", va="center",
                      fontsize=9, color=INK2)
        ax_strip.text(1.015, y, f"{hi:{fmt}} {unit}", ha="left", va="center",
                      fontsize=9, color=INK2)
        ax_strip.text(-0.155, y, label, ha="left", va="center",
                      fontsize=10.5, color=INK, transform=ax_strip.get_yaxis_transform())
    # Constraint annotation: the cable_d lower bound is a printability floor.
    ax_strip.annotate(
        "lower bound = TPU self-bridging floor\n(3.0 mm; below it, prints failed without supports)",
        xy=(0.0, 0.0), xytext=(0.09, -0.72), fontsize=8.5, color=INK2,
        arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8),
        annotation_clip=False,
    )
    ax_strip.set_xlim(-0.02, 1.02)
    ax_strip.set_ylim(-0.65, n_par - 0.35)
    ax_strip.set_title("Parameter bounds with the 9 Sobol samples",
                       loc="left", fontsize=11, color=INK, pad=10)
    for s in ax_strip.spines.values():
        s.set_visible(False)
    ax_strip.set_xticks([])
    ax_strip.set_yticks([])

    # ---- Bottom: parallel coordinates --------------------------------------
    ax_par.set_facecolor(SURFACE)
    xs = np.arange(n_par)

    def spread(vals: list[float], min_gap: float = 0.045) -> list[float]:
        """Nudge label y-positions apart so close-together labels don't collide."""
        order = np.argsort(vals)
        out = list(vals)
        prev = -np.inf
        for k in order:
            out[k] = max(out[k], prev + min_gap)
            prev = out[k]
        return out

    left_y = spread([norm(0, SPECIMENS[j, 0]) for j in range(len(SPECIMENS))])
    right_y = spread([norm(n_par - 1, SPECIMENS[j, n_par - 1])
                      for j in range(len(SPECIMENS))])
    for j in range(len(SPECIMENS)):
        ys = [norm(i, SPECIMENS[j, i]) for i in range(n_par)]
        ax_par.plot(xs, ys, color=RAMP[j], lw=2, zorder=2, solid_capstyle="round")
        ax_par.text(-0.1, left_y[j], str(j), ha="right", va="center",
                    fontsize=8.5, color=INK2)
        ax_par.text(n_par - 1 + 0.1, right_y[j], str(j), ha="left", va="center",
                    fontsize=8.5, color=INK2)
    for i, (_, label, lo, hi, unit) in enumerate(PARAMS):
        ax_par.axvline(i, color="#d8d6d0", lw=1, zorder=1)
        ax_par.text(i, -0.09, f"{label}", ha="center", fontsize=9.5, color=INK)
        ax_par.text(i, -0.16, f"[{lo:g}, {hi:g}] {unit}", ha="center",
                    fontsize=8.5, color=INK2)
        ax_par.text(i, 1.03, f"{hi:g}", ha="center", fontsize=8, color=INK2)
        ax_par.text(i, -0.045, f"{lo:g}", ha="center", fontsize=8, color=INK2)
    ax_par.set_xlim(-0.45, n_par - 0.55)
    ax_par.set_ylim(-0.02, 1.02)
    ax_par.set_title(
        "Parallel coordinates — specimens 0–8 (lines shaded light→dark "
        "by specimen index; numbers label each line)",
        loc="left", fontsize=11, color=INK, pad=14,
    )
    for s in ax_par.spines.values():
        s.set_visible(False)
    ax_par.set_xticks([])
    ax_par.set_yticks([])

    fig.text(
        0.16, 0.048,
        "Frozen context: topology = t3_prism · tiling = 1×1×1 · struts/cell = 3 · "
        "build orientation = vertical",
        fontsize=9, color=INK2,
    )
    fig.text(
        0.16, 0.024,
        "PLA struts (extruder 1) · TPU 85A cables (extruder 2) · "
        "supports = manual-painted · joint Ø ≥ 7 mm",
        fontsize=9, color=INK2,
    )

    out = "bo/t3-prism-search-space.png"
    fig.savefig(out, dpi=200, facecolor=SURFACE)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
