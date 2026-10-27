#!/usr/bin/env python3
"""Nine Sobol seed designs at one millimetre scale (fig:seed-designs).

Reads the as-printed (post-projection) geometry of specs 00 to 08 from
manuscript/data/t3-prism-bo-batch-print-key.csv and draws each with
t3_prism_render on one set of equal-aspect axes, 3 x 3, portrait, labelled
with the spec number and article ID, plus a shared 20 mm scale bar. Writes
figures/bo/fig-seed-designs.{pdf,png}.

Usage:  python3 scripts/figures/build_seed_designs_figure.py
"""
from __future__ import annotations

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from campaign_data import INK, REPO, STYLE, seed_designs  # noqa: E402
from t3_prism_render import draw_prism  # noqa: E402

AZIM, ELEV = -20.0, 10.0
CELL_W, CELL_H = 86.0, 150.0   # mm per grid cell (widest seed ~ 84 mm; tallest ~ 124 mm
                               # projected plus two label lines)


def main() -> int:
    designs = seed_designs()
    assert len(designs) == 9
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(3.35, 3.35 * 3 * CELL_H / (3 * CELL_W) + 0.05))
        for k, d in enumerate(designs):
            row, col = divmod(k, 3)
            cx = (col + 0.5) * CELL_W
            base = (2 - row) * CELL_H + 32.0
            _, _, vmin, _ = draw_prism(ax, d["R"], d["H"], d["twist"], d["d_s"],
                                       d["d_t"], x0=cx, y0=base, azim=AZIM, elev=ELEV)
            label = f"Spec {d['spec']}  {d['print_id']}"
            ax.text(cx, base + vmin - 2.5, label, ha="center", va="top",
                    fontsize=7.5, color=INK)
            if not d["tested"]:
                ax.text(cx, base + vmin - 11.5, "not drop-tested", ha="center",
                        va="top", fontsize=6.5, color=INK, style="italic")
        # 20 mm scale bar, below the grid at the right
        x1 = 3 * CELL_W - 4.0
        ax.plot([x1 - 20.0, x1], [-2.0, -2.0], color=INK, lw=1.2, solid_capstyle="butt")
        ax.text(x1 - 22.5, -2.0, "20 mm", ha="right", va="center", fontsize=6.5, color=INK)
        ax.set_xlim(0, 3 * CELL_W)
        ax.set_ylim(-6.0, 3 * CELL_H)
        ax.set_aspect("equal")
        ax.axis("off")
        out = REPO / "figures" / "bo" / "fig-seed-designs"
        for ext in ("pdf", "png"):
            fig.savefig(f"{out}.{ext}", bbox_inches="tight", pad_inches=0.01,
                        facecolor="white")
        plt.close(fig)
    for d in designs:
        print(d["spec"], d["print_id"], d["R"], d["H"], d["twist"], d["d_s"], d["d_t"])
    print(f"wrote {out}.pdf and .png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
