"""Build the seed-designs tour GIF for the IDETC slide deck.

Same look as gif-param-sequence.gif, continued: the animation starts on
that GIF's end configuration (every geometry parameter at its upper
bound) and then morphs through the nine actual seed designs of the
printed campaign (S0, then Sobol specimens 1 to 8) in specimen order,
all five dials moving together for each transition. Requested in PR #84
(me-madsen, 2026-08-20). No caption text on the slide; the dials carry
their bound values at their ends.

Geometry, bounds, colors, and the depth-sorted renderer come from
build_search_space_figure.py so the assets stay consistent. Seed values
are the nine rows of bo/t3-prism-bo-batch.csv (commit 18c41a6, the batch
that was actually printed and drop-tested). One camera and one mm scale
cover every frame.

Output: presentation/media/gif-designs-tour.gif (16:9, 1920x1080).
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from build_search_space_figure import (
    BOUNDS,
    GUIDE,
    INK,
    INK2,
    draw_structure,
    nodes,
    project,
    setup_axes,
)
from build_search_space_gifs import ACCENT

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "gif-designs-tour.gif"

FIG_W_IN, FIG_H_IN, DPI = 8.0, 4.5, 240  # 1920 x 1080 px
STEPS = 18            # frames for one design-to-design transition
STEP_MS = 70          # per-frame duration mid-transition
DESIGN_HOLD_MS = 950  # pause on each seed design
END_HOLD_MS = 1600    # pause at the all-max start and the last design

DIALS = [
    ("R_mm", "triangle radius R", "{:.0f} mm"),
    ("H_mm", "height H", "{:.0f} mm"),
    ("twist_deg", "twist angle", "{:.0f}\N{DEGREE SIGN}"),
    ("strut_d_mm", "strut diameter", "{:.1f} mm"),
    ("cable_d_mm", "cable diameter", "{:.1f} mm"),
]

# All nine campaign seed designs, in specimen order: S0 (specimen 0),
# then the eight Sobol designs (specimens 1-8). bo/t3-prism-bo-batch.csv.
SEEDS = [
    dict(R_mm=32.1266, H_mm=89.6262, twist_deg=59.7792,
         strut_d_mm=7.8831, cable_d_mm=5.3902),
    dict(R_mm=33.7842, H_mm=80.0836, twist_deg=77.4080,
         strut_d_mm=10.8717, cable_d_mm=3.0003),
    dict(R_mm=38.9665, H_mm=99.9950, twist_deg=47.6915,
         strut_d_mm=7.0737, cable_d_mm=3.9241),
    dict(R_mm=25.1224, H_mm=72.0587, twist_deg=65.1213,
         strut_d_mm=10.1789, cable_d_mm=4.6640),
    dict(R_mm=27.6114, H_mm=104.1304, twist_deg=70.4432,
         strut_d_mm=9.2816, cable_d_mm=4.4922),
    dict(R_mm=36.3001, H_mm=63.2297, twist_deg=52.9940,
         strut_d_mm=6.4571, cable_d_mm=4.0550),
    dict(R_mm=35.9821, H_mm=96.4464, twist_deg=62.1055,
         strut_d_mm=11.6620, cable_d_mm=3.4949),
    dict(R_mm=30.1066, H_mm=74.8199, twist_deg=44.4573,
         strut_d_mm=8.5803, cable_d_mm=4.9377),
    dict(R_mm=29.0207, H_mm=100.8663, twist_deg=63.7624,
         strut_d_mm=6.1990, cable_d_mm=3.1969),
]

ALL_MAX = {k: hi for k, (lo, hi) in BOUNDS.items()}


def eased(a, b):
    """Cosine-eased dict-of-params a -> b sequence, STEPS frames."""
    out = []
    for t in range(STEPS):
        f = (1 - math.cos(math.pi * t / (STEPS - 1))) / 2
        out.append({k: a[k] + (b[k] - a[k]) * f for k in a})
    return out


def frame_sequence():
    """(params, hold_ms) for every frame: all-max, then each seed."""
    frames = []
    waypoints = [ALL_MAX] + SEEDS
    for i in range(len(waypoints) - 1):
        for t, params in enumerate(eased(waypoints[i], waypoints[i + 1])):
            hold = STEP_MS
            if i == 0 and t == 0:
                hold = END_HOLD_MS
            elif t == STEPS - 1:
                hold = (END_HOLD_MS if i == len(waypoints) - 2
                        else DESIGN_HOLD_MS)
            frames.append((params, hold))
    return frames


def union_bbox(frames):
    """(u, v) bounding box over every frame, one camera for the whole run."""
    us, vs = [], []
    for params, _ in frames:
        bot, top = nodes(params)
        for pt in bot + top:
            u, v, _ = project(pt)
            us.append(u)
            vs.append(v)
    return min(us), max(us), min(vs), max(vs)


def draw_dial_panel(fig, params):
    """Five stacked dials, all live: every transition moves all of them."""
    sx0, sx1 = 0.685, 0.945
    for j, (key, label, fmt) in enumerate(DIALS):
        lo, hi = BOUNDS[key]
        val = params[key]
        frac = (val - lo) / (hi - lo)
        y = 0.78 - j * 0.14
        fig.text(sx0, y + 0.045, label, ha="left", va="bottom",
                 fontsize=10, color=INK)
        fig.text(sx1, y + 0.045, fmt.format(val), ha="right", va="bottom",
                 fontsize=10, color=ACCENT, fontweight="bold")
        fig.add_artist(plt.Line2D([sx0, sx1], [y, y], color=GUIDE,
                                  lw=2.6, solid_capstyle="round",
                                  transform=fig.transFigure))
        fig.add_artist(plt.Line2D([sx0 + frac * (sx1 - sx0)], [y],
                                  marker="o", markersize=9, color=ACCENT,
                                  transform=fig.transFigure))
        # Bound values at the dial ends (lo left, hi right).
        fig.text(sx0, y - 0.032, fmt.format(lo), ha="center", va="top",
                 fontsize=8, color=INK2)
        fig.text(sx1, y - 0.032, fmt.format(hi), ha="center", va="top",
                 fontsize=8, color=INK2)


def render_frame(params, bbox):
    u0, u1, v0, v1 = bbox
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor("white")

    ax = fig.add_axes([0.02, 0.05, 0.62, 0.91])
    center = ((u0 + u1) / 2, (v0 + v1) / 2)
    ppmm = setup_axes(ax, fig, center, (u1 - u0) + 40, (v1 - v0) + 30)
    draw_structure(ax, params, ppmm)

    draw_dial_panel(fig, params)

    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3])
    plt.close(fig)
    return img


def main():
    frames = frame_sequence()
    bbox = union_bbox(frames)
    imgs = [render_frame(params, bbox) for params, _ in frames]
    palette = imgs[0].quantize(colors=256)
    imgs_q = [f.quantize(colors=256, palette=palette, dither=0)
              for f in imgs]
    durations = [hold for _, hold in frames]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    imgs_q[0].save(OUT, save_all=True, append_images=imgs_q[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB, "
          f"{len(imgs_q)} frames)")


if __name__ == "__main__":
    main()
