#!/usr/bin/env python3
"""Standalone *example* of a mechanism-oriented results figure for the manuscript.

This is a side-task mock-up requested in PR review (comment 4664748222): a worked
example of the kind of data figure the manuscript currently lacks -- processed
drop-test acceleration curves annotated with callouts to the specific structural
features being exercised, so the reader can connect the measured signal to the
*mechanism* of energy absorption.

IMPORTANT: the curves here are SYNTHETIC. They are generated from the documented
qualitative behaviour of the real drop-test campaign (issue #36 analysis: 125 kHz
TP4 capture, SAE J211 CFC-180 filtering, impact at t ~ 4.2 ms, control CFC-180
peak ~1792 G, 'audrey' tensegrity CFC-180 peak ~370-463 G => ~74-79 % reduction)
purely to illustrate layout and annotation. No experimental file is read or
implied; replace the `synthetic_*` calls with the real processed channels before
any figure like this is used in the manuscript.

Run:
    python scripts/figures/mechanistic_data_figure_example.py
Outputs:
    figures/examples/mechanistic-data-figure-example.png
    figures/examples/mechanistic-data-figure-example.pdf
"""
from __future__ import annotations

import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "figures", "examples")
OUT_BASE = os.path.join(OUT_DIR, "mechanistic-data-figure-example")

# ---------------------------------------------------------------------------
# Synthetic, physically-plausible drop-test signals (NOT real data).
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(36)
T_IMPACT_MS = 4.2  # documented impact time in the real TP4 captures


def synthetic_control(t_ms: np.ndarray) -> np.ndarray:
    """Rigid control: a single sharp, short-duration spike + decaying ringing."""
    tau = t_ms - T_IMPACT_MS
    # main half-sine-ish pulse, ~0.9 ms wide, ~1792 G peak
    width = 0.9
    pulse = 1792.0 * np.exp(-(tau ** 2) / (2 * (width / 2.355) ** 2))
    pulse[tau < 0] *= 0.0
    # structural ringing (~550 Hz dominant) decaying after the hit
    ring = 180.0 * np.exp(-np.clip(tau, 0, None) / 2.5) * np.sin(2 * np.pi * 0.55 * tau)
    ring[tau < 0] = 0.0
    noise = RNG.normal(0, 6, size=t_ms.shape)
    return pulse + ring + noise


def synthetic_tensegrity(t_ms: np.ndarray) -> np.ndarray:
    """Tensegrity: lower, broadened, longer-duration plateau (energy spread in time)."""
    tau = t_ms - T_IMPACT_MS
    # broad, lower plateau ~430 G spread over ~6 ms
    plateau = 430.0 * np.exp(-(tau ** 2) / (2 * (3.0) ** 2))
    plateau[tau < -0.5] *= 0.0
    # gentle secondary bump from cable re-tensioning / rebound
    rebound = 120.0 * np.exp(-((tau - 7.5) ** 2) / (2 * (2.0) ** 2))
    noise = RNG.normal(0, 4, size=t_ms.shape)
    return plateau + rebound + noise


def synthetic_tensegrity_raw(filtered: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
    """Add high-frequency mount/structural ringing on top of the CFC-180 signal."""
    hf = 70.0 * np.sin(2 * np.pi * 4.5 * t_ms) * np.exp(-t_ms / 18.0)
    return filtered + hf + RNG.normal(0, 12, size=t_ms.shape)


# ---------------------------------------------------------------------------
# Small schematic of a T3 tensegrity prism used for the callout insets.
# ---------------------------------------------------------------------------
def draw_t3_prism(ax, compression: float = 0.0, highlight_joint: bool = False):
    """Cartoon T3 prism. `compression` in [0,1] squashes height; struts=PLA, cables=TPU."""
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.axis("off")

    h = 1.0 * (1.0 - 0.45 * compression)
    twist = np.deg2rad(50)  # near equilibrium prism twist
    ang = np.array([90, 210, 330]) * np.pi / 180.0
    bottom = np.c_[np.cos(ang), np.sin(ang) - 0.0] * 0.85
    top = np.c_[np.cos(ang + twist), np.sin(ang + twist)] * 0.85
    bottom = np.c_[bottom[:, 0], bottom[:, 1] * 0.45 - h]
    top = np.c_[top[:, 0], top[:, 1] * 0.45 + h]

    # cables (TPU) -- horizontal triangles + saddle cables
    cab = dict(color="#1f77b4", lw=2.0, solid_capstyle="round", zorder=1)
    for i in range(3):
        j = (i + 1) % 3
        ax.plot(*zip(bottom[i], bottom[j]), **cab)
        ax.plot(*zip(top[i], top[j]), **cab)
    for i in range(3):
        ax.plot(*zip(bottom[i], top[(i + 1) % 3]), **cab)

    # struts (PLA) -- the three crossing compression members
    strut = dict(color="#d62728", lw=4.0, solid_capstyle="round", zorder=2)
    pairs = [(0, 0), (1, 1), (2, 2)]
    for b, t in pairs:
        ax.plot(*zip(bottom[b], top[t]), **strut)

    if highlight_joint:
        # circle one strut end to mark the internal-anchor joint callout
        ax.add_patch(plt.Circle(top[0], 0.22, fill=False, color="#ff7f0e", lw=2.5, zorder=5))


def draw_internal_anchor_inset(ax):
    """Schematic of the corrected joint: cables anchor INSIDE the strut end (cage)."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # PLA strut end shell (cage)
    ax.add_patch(FancyBboxPatch((0.30, 0.05), 0.40, 0.78,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="#f4c7c3", ec="#d62728", lw=2.0))
    ax.text(0.5, 0.90, "PLA strut end\n(rigid cage)", ha="center", va="bottom",
            fontsize=7.5, color="#a01717")
    # internal junction node where TPU cables meet
    ax.add_patch(plt.Circle((0.5, 0.40), 0.075, fc="#1f77b4", ec="k", lw=0.8, zorder=4))
    ax.text(0.5, 0.40, "", ha="center")
    # cables exiting through discrete outlets
    for dx in (-0.18, 0.0, 0.18):
        ax.plot([0.5, 0.5 + dx], [0.40, 0.06], color="#1f77b4", lw=2.2,
                solid_capstyle="round", zorder=3)
    ax.text(0.5, -0.02, "TPU cables join inside,\nexit via outlets",
            ha="center", va="top", fontsize=7.5, color="#11557c")


# ---------------------------------------------------------------------------
# Build the figure.
# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t = np.linspace(0, 22, 4000)  # ms

    ctrl = synthetic_control(t)
    tens = synthetic_tensegrity(t)
    tens_raw = synthetic_tensegrity_raw(tens, t)

    ctrl_peak = ctrl.max()
    tens_peak = tens.max()
    reduction = 100 * (1 - tens_peak / ctrl_peak)

    fig = plt.figure(figsize=(11, 6.6), dpi=150)
    gs = fig.add_gridspec(
        3, 3,
        width_ratios=[2.6, 1.0, 1.0],
        height_ratios=[1, 1, 1],
        hspace=0.55, wspace=0.30,
        left=0.07, right=0.985, top=0.90, bottom=0.10,
    )
    ax = fig.add_subplot(gs[:, 0])  # main curve panel spans all rows

    # raw tensegrity (faint) to motivate CFC-180 filtering
    ax.plot(t, tens_raw, color="#9ecae1", lw=0.8, alpha=0.8,
            label="Tensegrity, raw (125 kHz)")
    ax.plot(t, ctrl, color="#d62728", lw=2.0, label="Rigid control, CFC-180")
    ax.plot(t, tens, color="#1f77b4", lw=2.4, label="Tensegrity, CFC-180")

    ax.axhline(ctrl_peak, color="#d62728", ls=":", lw=1.0, alpha=0.7)
    ax.axhline(tens_peak, color="#1f77b4", ls=":", lw=1.0, alpha=0.7)

    # peak-reduction annotation
    ax.annotate(
        "", xy=(T_IMPACT_MS, tens_peak), xytext=(T_IMPACT_MS, ctrl_peak),
        arrowprops=dict(arrowstyle="<->", color="k", lw=1.4),
    )
    ax.text(T_IMPACT_MS + 0.4, (ctrl_peak + tens_peak) / 2,
            f"peak transmitted\nacceleration\n-{reduction:.0f}%",
            fontsize=9, va="center", fontweight="bold")

    # mechanistic phase shading + compact letter labels along the curve
    phases = [
        (4.0, 5.2, "#fff2cc", "A"),
        (5.2, 9.5, "#d9ead3", "B"),
        (9.5, 14.0, "#cfe2f3", "C"),
    ]
    for x0, x1, col, lab in phases:
        ax.axvspan(x0, x1, color=col, alpha=0.55, zorder=0)
        ax.text((x0 + x1) / 2, -55, lab, ha="center", va="center",
                fontsize=12, fontweight="bold", color="#555555")
    # phase key (kept off the curves)
    ax.text(9.0, ctrl_peak * 0.92,
            "A  contact / cable pre-tension\n"
            "B  strut+cable load redistribution (energy plateau)\n"
            "C  recovery / rebound",
            fontsize=8.0, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbbbbb", alpha=0.9))

    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Deceleration (G)")
    ax.set_xlim(0, 18)
    ax.set_ylim(-80, ctrl_peak * 1.12)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.95)
    ax.set_title("(a)  Processed drop-test response", fontsize=11, loc="left")

    # --- callout insets on the right column -------------------------------
    ax_b = fig.add_subplot(gs[0, 1:])
    draw_t3_prism(ax_b, compression=0.05, highlight_joint=True)
    ax_b.set_title("(b)  Specimen under test (T3 prism)", fontsize=9.5, loc="left")

    ax_c = fig.add_subplot(gs[1, 1])
    draw_internal_anchor_inset(ax_c)
    ax_c.set_title("(c)  Joint callout", fontsize=9.5, loc="left")

    ax_d = fig.add_subplot(gs[1, 2])
    draw_t3_prism(ax_d, compression=0.85)
    ax_d.set_title("(d)  Phase B: compressed", fontsize=9.5, loc="left")

    # caption-row note spanning the two inset columns
    ax_note = fig.add_subplot(gs[2, 1:])
    ax_note.axis("off")
    ax_note.text(
        0.0, 0.95,
        "Callouts link the signal to the mechanism:\n"
        "  \u2022 (b) red = PLA struts (compression), blue = TPU cables (tension);\n"
        "    circled strut end is detailed in (c).\n"
        "  \u2022 (c) cables anchor INSIDE the strut end, which acts as a rigid\n"
        "    cage \u2014 the load path that flattens the peak in phase B.\n"
        "  \u2022 (d) snapshot at the phase-B plateau, where strut buckling and\n"
        "    cable re-tensioning spread the impulse over time.",
        fontsize=7.8, va="top", ha="left", family="monospace",
    )

    fig.suptitle(
        "EXAMPLE (mock-up, synthetic data): mechanism-oriented drop-test figure",
        fontsize=12.5, fontweight="bold",
    )
    # visible mock-up watermark so this is never mistaken for real results
    fig.text(0.5, 0.5, "ILLUSTRATIVE EXAMPLE\nSYNTHETIC DATA",
             fontsize=34, color="gray", alpha=0.12, ha="center", va="center",
             rotation=18, zorder=10)

    fig.savefig(OUT_BASE + ".png", dpi=150)
    fig.savefig(OUT_BASE + ".pdf")
    print("wrote", OUT_BASE + ".png", "and", OUT_BASE + ".pdf")
    print(f"control peak={ctrl_peak:.0f} G, tensegrity peak={tens_peak:.0f} G, "
          f"reduction={reduction:.0f}%")


if __name__ == "__main__":
    main()
