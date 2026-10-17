"""Build one GIF per geometry parameter for the IDETC slide deck.

Each GIF sweeps a single parameter across its campaign bounds while the
other four stay at the middle of their bounds, so the audience sees what
each number does to the printed structure. Follow-up to the static
search-space figure, requested in PR #84 (sgbaird, 2026-08-20): "a series
of GIF animations visually showing changes to a specific parameter".

Geometry, bounds, colors, and the depth-sorted renderer are imported from
build_search_space_figure.py so the two figures cannot drift apart. All
five GIFs share one camera and one mm scale (sized to the largest design
any sweep can produce), so they are comparable side by side and the
ground plane stays put while a structure grows.

Output: presentation/media/gif-param-{radius,height,twist,strut,cable}.gif
(16:9, 960x540, ~4 s ping-pong loop with holds at the bounds).
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
    C_CABLE,
    C_STRUT,
    GUIDE,
    INK,
    INK2,
    MID,
    draw_structure,
    nodes,
    project,
    setup_axes,
)

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "media"

FIG_W_IN, FIG_H_IN, DPI = 8.0, 4.5, 120  # 960 x 540 px
STEPS = 26          # frames for one lo -> hi traverse
HOLD_MS = 900       # pause at each bound
STEP_MS = 70        # per-frame duration mid-sweep
ACCENT = "#156082"  # EMC accent blue for the value readout and slider

SWEEPS = [
    ("radius", "R_mm", "triangle radius R", "", "{:.0f} mm"),
    ("height", "H_mm", "height H", "", "{:.0f} mm"),
    ("twist", "twist_deg", "twist angle", "", "{:.0f}\N{DEGREE SIGN}"),
    ("strut", "strut_d_mm", "strut diameter", "rigid PLA", "{:.1f} mm"),
    ("cable", "cable_d_mm", "cable diameter", "flexible TPU", "{:.1f} mm"),
]


def sweep_values(key):
    """Cosine-eased lo -> hi -> lo value sequence for one parameter."""
    lo, hi = BOUNDS[key]
    up = [lo + (hi - lo) * (1 - math.cos(math.pi * t / (STEPS - 1))) / 2
          for t in range(STEPS)]
    return up + up[-2:0:-1]  # ping-pong without repeating the endpoints


def frame_params(key, value):
    p = dict(MID)
    p[key] = value
    return p


def union_bbox():
    """(u, v) bounding box over every frame of every sweep, one camera."""
    us, vs = [], []
    for _, key, _, _, _ in SWEEPS:
        for val in sweep_values(key):
            bot, top = nodes(frame_params(key, val))
            for pt in bot + top:
                u, v, _ = project(pt)
                us.append(u)
                vs.append(v)
    return min(us), max(us), min(vs), max(vs)


def annotate_sweep(ax, key, params):
    """Dashed guide showing which feature the swept parameter controls."""
    R, H, tw = params["R_mm"], params["H_mm"], params["twist_deg"]
    bot, top = nodes(params)

    def uv(p):
        u, v, _ = project(p)
        return u, v

    if key == "R_mm":
        ang = np.linspace(0, 2 * math.pi, 120)
        circ = [uv((R * math.cos(a), R * math.sin(a), 0.0)) for a in ang]
        ax.plot([c[0] for c in circ], [c[1] for c in circ],
                ls=(0, (4, 3)), lw=1.2, color=GUIDE, zorder=2)
        c0, b2 = uv((0, 0, 0)), uv(bot[2])
        ax.plot([c0[0], b2[0]], [c0[1], b2[1]], ls=(0, (4, 3)), lw=1.2,
                color=GUIDE, zorder=2)
    elif key == "H_mm":
        u_dim = uv((0, 0, 0))[0] - 62
        v_lo, v_hi = uv((0, 0, 0))[1], uv((0, 0, H))[1]
        ax.annotate("", xy=(u_dim, v_hi), xytext=(u_dim, v_lo),
                    arrowprops=dict(arrowstyle="<->", color=GUIDE, lw=1.2))
        for v in (v_lo, v_hi):
            ax.plot([u_dim - 4, u_dim + 4], [v, v], lw=1.1, color=GUIDE)
    elif key == "twist_deg":
        a0, a1 = math.radians(90), math.radians(90 + tw)
        Ra = R + 12
        ct = uv((0, 0, H))
        for a in (a0, a1):
            sp = uv((Ra * math.cos(a), Ra * math.sin(a), H))
            ax.plot([ct[0], sp[0]], [ct[1], sp[1]], ls=(0, (1.5, 2.5)),
                    lw=1.1, color=GUIDE, zorder=4)
        arc = [uv((Ra * math.cos(a), Ra * math.sin(a), H))
               for a in np.linspace(a0, a1, 40)]
        ax.plot([c[0] for c in arc[:-2]], [c[1] for c in arc[:-2]],
                ls=(0, (4, 3)), lw=1.2, color=GUIDE, zorder=4)
        ax.annotate("", xy=arc[-1], xytext=arc[-4],
                    arrowprops=dict(arrowstyle="->", color=GUIDE, lw=1.2),
                    zorder=4)
    elif key == "strut_d_mm":
        sp = uv(tuple(a + (b - a) * 0.55 for a, b in zip(bot[2], top[2])))
        ax.annotate("", xy=sp, xytext=(sp[0] + 42, sp[1] + 20),
                    arrowprops=dict(arrowstyle="->", color=GUIDE, lw=1.2,
                                    shrinkB=10), zorder=4)
    elif key == "cable_d_mm":
        cm = uv(tuple((a + b) / 2 for a, b in zip(bot[0], bot[1])))
        ax.annotate("", xy=cm, xytext=(cm[0] - 42, cm[1] - 22),
                    arrowprops=dict(arrowstyle="->", color=GUIDE, lw=1.2,
                                    shrinkB=8), zorder=4)


def render_frame(key, label, sub, fmt, value, bbox):
    """Render one frame to a PIL image."""
    lo, hi = BOUNDS[key]
    u0, u1, v0, v1 = bbox
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor("white")

    ax = fig.add_axes([0.02, 0.10, 0.62, 0.86])
    center = ((u0 + u1) / 2, (v0 + v1) / 2)
    # Margin for the H dimension line and twist arc outside the structure.
    ppmm = setup_axes(ax, fig, center, (u1 - u0) + 95, (v1 - v0) + 40)
    params = frame_params(key, value)
    draw_structure(ax, params, ppmm)
    annotate_sweep(ax, key, params)

    # Right-hand panel: parameter name, live value, slider, fixed caption.
    fig.text(0.815, 0.74, label, ha="center", va="bottom",
             fontsize=15, color=INK, fontweight="bold")
    if sub:
        fig.text(0.815, 0.715, sub, ha="center", va="top",
                 fontsize=11, color=INK2, style="italic")
    fig.text(0.815, 0.60, fmt.format(value), ha="center", va="center",
             fontsize=26, color=ACCENT, fontweight="bold")

    sx0, sx1, sy = 0.70, 0.93, 0.47
    frac = (value - lo) / (hi - lo)
    fig.add_artist(plt.Line2D([sx0, sx1], [sy, sy], color=GUIDE, lw=3,
                              solid_capstyle="round",
                              transform=fig.transFigure))
    fig.add_artist(plt.Line2D([sx0 + frac * (sx1 - sx0)], [sy],
                              marker="o", markersize=11, color=ACCENT,
                              transform=fig.transFigure))
    fig.text(sx0, sy - 0.045, fmt.format(lo), ha="center", va="top",
             fontsize=10.5, color=INK2)
    fig.text(sx1, sy - 0.045, fmt.format(hi), ha="center", va="top",
             fontsize=10.5, color=INK2)

    fig.text(0.815, 0.30, "the other four parameters\nstay at mid-range",
             ha="center", va="center", fontsize=10.5, color=INK2,
             style="italic", linespacing=1.5)

    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3])
    plt.close(fig)
    return img


def build_gif(name, key, label, sub, fmt, bbox):
    values = sweep_values(key)
    frames = [render_frame(key, label, sub, fmt, v, bbox) for v in values]
    palette = frames[0].quantize(colors=128)
    frames_q = [f.quantize(colors=128, palette=palette, dither=0)
                for f in frames]
    durations = [STEP_MS] * len(frames_q)
    durations[0] = durations[STEPS - 1] = HOLD_MS  # pause at both bounds
    out = OUT_DIR / f"gif-param-{name}.gif"
    frames_q[0].save(out, save_all=True, append_images=frames_q[1:],
                     duration=durations, loop=0, optimize=True)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB, "
          f"{len(frames_q)} frames)")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bbox = union_bbox()
    for name, key, label, sub, fmt in SWEEPS:
        build_gif(name, key, label, sub, fmt, bbox)


if __name__ == "__main__":
    main()
