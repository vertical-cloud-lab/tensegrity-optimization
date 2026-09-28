"""Build the single sequential search-space GIF for the IDETC slide deck.

One continuous animation instead of five separate loops: the design starts
with every geometry parameter at its lower bound, then each dial is turned
up to its upper bound one after another (triangle radius, height, twist
angle, strut diameter, cable diameter) with no reset in between. Requested
in PR #84 (me-madsen, 2026-08-20): "the dials start at the minimum
parameters and then each one is dialed up one by one", to be spoken over
as "we vary the spread of the base, the height of the structure, the
angle of twist, ...".

Geometry, bounds, colors, and the depth-sorted renderer come from
build_search_space_figure.py; the per-stage dashed guides come from
build_search_space_gifs.py, so all three assets stay consistent. One
camera and one mm scale cover every frame, so the ground plane stays put
while the structure grows.

Revised per PR #84 (me-madsen, 2026-08-20): no caption text on the slide,
no panel header, and each dial carries its bound values at its ends.

Output: presentation/media/gif-param-sequence.gif (16:9, 1920x1080).
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
from build_search_space_gifs import ACCENT, annotate_sweep

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "gif-param-sequence.gif"

FIG_W_IN, FIG_H_IN, DPI = 8.0, 4.5, 240  # 1920 x 1080 px
STEPS = 22            # frames for one lo -> hi traverse
STEP_MS = 70          # per-frame duration mid-sweep
STAGE_HOLD_MS = 650   # pause after each dial reaches its bound
END_HOLD_MS = 1600    # pause at all-min (start) and all-max (end)
PENDING = "#c8c8c8"   # dial track/knob color before a stage runs

# Stage order matches the intended narration, base upward.
STAGES = [
    ("R_mm", "triangle radius R", "{:.0f} mm"),
    ("H_mm", "height H", "{:.0f} mm"),
    ("twist_deg", "twist angle", "{:.0f}\N{DEGREE SIGN}"),
    ("strut_d_mm", "strut diameter", "{:.1f} mm"),
    ("cable_d_mm", "cable diameter", "{:.1f} mm"),
]


def eased(lo, hi):
    """Cosine-eased lo -> hi value sequence, STEPS frames."""
    return [lo + (hi - lo) * (1 - math.cos(math.pi * t / (STEPS - 1))) / 2
            for t in range(STEPS)]


def stage_params(stage, value):
    """Earlier dials sit at their max, later ones at their min."""
    p = {}
    for j, (key, _, _) in enumerate(STAGES):
        lo, hi = BOUNDS[key]
        p[key] = hi if j < stage else lo
    p[STAGES[stage][0]] = value
    return p


def frame_sequence():
    """(stage_index, params, hold_ms) for every frame, no resets."""
    frames = []
    for i, (key, _, _) in enumerate(STAGES):
        lo, hi = BOUNDS[key]
        for t, val in enumerate(eased(lo, hi)):
            hold = STEP_MS
            if i == 0 and t == 0:
                hold = END_HOLD_MS
            elif t == STEPS - 1:
                hold = END_HOLD_MS if i == len(STAGES) - 1 else STAGE_HOLD_MS
            frames.append((i, stage_params(i, val), hold))
    return frames


def union_bbox(frames):
    """(u, v) bounding box over every frame, one camera for the whole run."""
    us, vs = [], []
    for _, params, _ in frames:
        bot, top = nodes(params)
        for pt in bot + top:
            u, v, _ = project(pt)
            us.append(u)
            vs.append(v)
    return min(us), max(us), min(vs), max(vs)


def draw_dial_panel(fig, stage, params):
    """Five stacked dials; done ones full, the active one live, rest empty."""
    sx0, sx1 = 0.685, 0.945
    for j, (key, label, fmt) in enumerate(STAGES):
        lo, hi = BOUNDS[key]
        val = params[key]
        frac = (val - lo) / (hi - lo)
        y = 0.78 - j * 0.14
        active = j == stage
        done = j < stage
        c_track = GUIDE if (active or done) else PENDING
        c_knob = ACCENT if active else (INK2 if done else PENDING)
        c_label = INK if active else INK2
        c_value = ACCENT if active else (INK2 if done else PENDING)
        fig.text(sx0, y + 0.045, label, ha="left", va="bottom",
                 fontsize=10, color=c_label,
                 fontweight="bold" if active else "normal")
        fig.text(sx1, y + 0.045, fmt.format(val), ha="right", va="bottom",
                 fontsize=10, color=c_value,
                 fontweight="bold" if active else "normal")
        fig.add_artist(plt.Line2D([sx0, sx1], [y, y], color=c_track,
                                  lw=2.6, solid_capstyle="round",
                                  transform=fig.transFigure))
        fig.add_artist(plt.Line2D([sx0 + frac * (sx1 - sx0)], [y],
                                  marker="o", markersize=9, color=c_knob,
                                  transform=fig.transFigure))
        # Bound values at the dial ends (lo left, hi right).
        fig.text(sx0, y - 0.032, fmt.format(lo), ha="center", va="top",
                 fontsize=8, color=INK2)
        fig.text(sx1, y - 0.032, fmt.format(hi), ha="center", va="top",
                 fontsize=8, color=INK2)


def render_frame(stage, params, bbox):
    u0, u1, v0, v1 = bbox
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor("white")

    ax = fig.add_axes([0.02, 0.05, 0.62, 0.91])
    center = ((u0 + u1) / 2, (v0 + v1) / 2)
    # Margin for the H dimension line and twist arc outside the structure.
    ppmm = setup_axes(ax, fig, center, (u1 - u0) + 95, (v1 - v0) + 40)
    draw_structure(ax, params, ppmm)
    annotate_sweep(ax, STAGES[stage][0], params)

    draw_dial_panel(fig, stage, params)

    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3])
    plt.close(fig)
    return img


def main():
    frames = frame_sequence()
    bbox = union_bbox(frames)
    imgs = [render_frame(stage, params, bbox)
            for stage, params, _ in frames]
    palette = imgs[-1].quantize(colors=256)
    imgs_q = [f.quantize(colors=256, palette=palette, dither=0)
              for f in imgs]
    durations = [hold for _, _, hold in frames]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    imgs_q[0].save(OUT, save_all=True, append_images=imgs_q[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB, "
          f"{len(imgs_q)} frames)")


if __name__ == "__main__":
    main()
