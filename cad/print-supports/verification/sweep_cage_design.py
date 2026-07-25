#!/usr/bin/env python3
# ============================================================================
# Level-1 design-space sweep for the anti-wobble tendon cages.
#
# Why this exists
# ---------------
# `simulate_tendon_wobble.py` proved the cage concept beats upscaling by ~5x.
# This script is the Edison-recommended Level-1 "reduced-order beam/contact
# screening" run over the *whole cage design space*, so the cage parameters
# (`--cage_ring_spacing`, `--cage_ring_gap`, `--cage_opening`, pillar layout)
# are chosen by mechanics instead of by eye. It models the exact cross-section
# geometry `build_tendon_cages()` emits:
#
#   * 3 guard pillars (radius pillar_d/2) at azimuths phi0 + {0,120,240} deg,
#     centres at r_p = r_t + pillar_gap + pillar_d/2 from the tendon axis;
#   * C-rings, inner radius r_in = r_t + ring_gap, sweeping 360-opening deg,
#     the opening centred between pillars k=2 and k=0.
#
# For each lateral direction it computes how far the printed tendon can
# translate before touching cage geometry ("free travel", the restraint
# rose).  The worst direction feeds a growing Euler-Bernoulli cantilever
# model (nozzle force + self-weight sag of the tilted tendon + Newton-cooling
# hot tip) evaluated at every printed height.  Sweeps:
#
#   A. restraint rose — free travel vs azimuth, committed vs recommended cage;
#   B. ring spacing x ring gap — worst-case deflection heatmap;
#   C. ring opening angle — escape-corridor travel vs cage removability
#      (a soft TPU tendon squeezes out of an opening chord slightly *below*
#      its diameter, so the opening can close further than the rigid-body
#      REMOVABLE criterion suggested);
#   D. deflection vs printed height for the design variants.
#
# Writes a JSON with the recommended parameter set consumed by the design
# iteration step (regenerating the cage artefacts).
#
# Requires: numpy, matplotlib.  Reads the committed cage report for the real
# tendon radii/tilt (falls back to Ø4.95 mm / 19.7 deg).
# ============================================================================
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Categorical palette (validated: dataviz reference palette, slots 1-4)
C_BLUE, C_ORANGE, C_AQUA, C_YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"

RHO_TPU = 1210.0e-9   # kg/mm^3
G = 9.81e3            # mm/s^2  (N = kg*mm/s^2 * 1e-3 ... handled via units below)


# ---------------------------------------------------------------------------
# cross-section contact model
# ---------------------------------------------------------------------------
def free_travel(phi_deg: np.ndarray, *, r_t: float, ring_gap: float,
                pillar_gap: float, pillar_d: float, opening_deg: float,
                n_pillars: int = 3, phi0: float = 0.0,
                cap_mm: float = 12.0) -> np.ndarray:
    """Distance the tendon disc can translate along each direction before
    touching a pillar or the C-ring (exact `build_tendon_cages` layout)."""
    pillar_r = pillar_d / 2.0
    r_p = r_t + pillar_gap + pillar_r
    r_in = r_t + ring_gap
    r_out = r_p + pillar_r
    step = 360.0 / n_pillars
    pillars = [np.array([r_p * math.cos(math.radians(phi0 + step * k)),
                         r_p * math.sin(math.radians(phi0 + step * k))])
               for k in range(n_pillars)]
    # ring sweep [a0, a0+sweep], opening centred between pillar n-1 and 0
    sweep = 360.0 - opening_deg
    a0 = phi0 + (360.0 - step) + step / 2.0 + opening_deg / 2.0
    # obstacle point cloud: ring inner arc + the two radial end caps
    angs = np.radians(a0 + np.linspace(0.0, sweep, 720))
    ring_pts = [np.column_stack([r_in * np.cos(angs), r_in * np.sin(angs)])]
    for cap_a in (math.radians(a0), math.radians(a0 + sweep)):
        rr = np.linspace(r_in, r_out, 60)
        ring_pts.append(np.column_stack([rr * math.cos(cap_a),
                                         rr * math.sin(cap_a)]))
    ring_pts = np.vstack(ring_pts)

    out = np.empty_like(phi_deg, dtype=float)
    deltas = np.arange(0.0, cap_mm, 0.02)
    for i, phi in enumerate(np.radians(phi_deg)):
        e = np.array([math.cos(phi), math.sin(phi)])
        # march outward and record the *first* contact (swept translation,
        # not teleport — the disc can't pass through the ring).
        centres = deltas[:, None] * e[None, :]
        d_ring = np.linalg.norm(ring_pts[None, :, :] - centres[:, None, :],
                                axis=2).min(axis=1)
        hit = d_ring < r_t
        for p in pillars:
            hit |= np.linalg.norm(centres - p[None, :], axis=1) < r_t + pillar_r
        idx = np.argmax(hit)
        out[i] = cap_mm if not hit.any() else max(0.0, deltas[idx] - 0.02)
    return out


# ---------------------------------------------------------------------------
# growing-cantilever wobble (nozzle force + self-weight sag + hot tip)
# ---------------------------------------------------------------------------
def bending_ei(e_mpa: float, d_mm: float) -> float:
    return e_mpa * math.pi * d_mm**4 / 64.0            # N*mm^2


def deflection_curve(lengths: np.ndarray, *, force_n: float, e_mpa: float,
                     d_mm: float, tilt_deg: float,
                     clearance: float | None, ring_spacing: float | None,
                     hot_len: float = 0.0, hot_frac: float = 0.1
                     ) -> np.ndarray:
    """Tip deflection (mm) at each printed length.

    force term      F*L^3/(3EI)  (lateral nozzle/bead-drag force at the front)
    self-weight sag q_perp*L^4/(8EI), q_perp = rho*A*g*sin(tilt)
    hot tip         the top `hot_len` mm at `hot_frac`*E adds
                    F*hot_len^3/(3*E_hot*I) local compliance
    rings           free travel `clearance`, highest ring one spacing below
                    the front; the braced expression restarts from the ring.
    """
    ei = bending_ei(e_mpa, d_mm)
    area = math.pi * (d_mm / 2.0) ** 2
    q_perp = RHO_TPU * area * 9.81 * math.sin(math.radians(tilt_deg))  # N/mm
    hot = np.minimum(hot_len, lengths)
    local_hot = force_n * hot**3 / (3.0 * bending_ei(e_mpa * hot_frac, d_mm))

    def free(li: np.ndarray) -> np.ndarray:
        return force_n * li**3 / (3.0 * ei) + q_perp * li**4 / (8.0 * ei)

    if ring_spacing is None or clearance is None:
        return free(lengths) + local_hot
    n_rings = np.floor(lengths / ring_spacing)
    h_ring = n_rings * ring_spacing
    braced = clearance + free(lengths - h_ring)
    return np.where(n_rings > 0, np.minimum(free(lengths), braced),
                    free(lengths)) + local_hot


def worst_deflection(span: float, **kw) -> float:
    lengths = np.linspace(1.0, span, 300)
    return float(deflection_curve(lengths, **kw).max())


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    ap.add_argument("--report", type=Path,
                    default=here / "t3-prism-pr35-cage-report.json")
    ap.add_argument("--force", type=float, default=0.01,
                    help="lateral nozzle/bead-drag force, N")
    ap.add_argument("--e_tpu", type=float, default=15.0,
                    help="printed TPU 85A modulus, MPa")
    ap.add_argument("--span", type=float, default=80.0,
                    help="printed tendon length, mm")
    ap.add_argument("--layer_time", type=float, default=120.0,
                    help="s between visits to the tendon (Level-3 refines)")
    ap.add_argument("--tau_cool", type=float, default=80.0,
                    help="Newton-cooling time constant of the tendon, s")
    ap.add_argument("--layer_h", type=float, default=0.2)
    ap.add_argument("--out", type=Path,
                    default=here / "t3-prism-pr35-cage-design-sweep.png")
    ap.add_argument("--out_json", type=Path,
                    default=here / "t3-prism-pr35-cage-design-recommendation.json")
    a = ap.parse_args()

    rep = json.loads(a.report.read_text())
    r_t = max(t["r"] for t in rep["tendons"])
    tilt = max(t["tilt"] for t in rep["tendons"])
    committed = dict(ring_gap=rep["ring_gap"], pillar_gap=rep["pillar_gap"],
                     pillar_d=rep["pillar_d"], opening=120.0,
                     spacing=rep["ring_spacing"])
    d_t = 2.0 * r_t

    # hot-tip extent: layers deposited within ~tau of the front are still
    # soft; that is (tau/layer_time) layers of layer_h each.
    hot_len = a.tau_cool / a.layer_time * a.layer_h

    phis = np.linspace(0.0, 360.0, 361)

    def rose(**kw):
        return free_travel(phis, r_t=r_t, **kw)

    rose_committed = rose(ring_gap=committed["ring_gap"],
                          pillar_gap=committed["pillar_gap"],
                          pillar_d=committed["pillar_d"],
                          opening_deg=committed["opening"])

    # ---- sweep C: opening angle --------------------------------------------
    rec_gap = 0.8   # from sweep B: clearance floor dominates; 0.8 mm still
    #                 clears TPU surface bulges (bubble scars are ~0.3 mm)
    openings = np.arange(40.0, 130.0, 5.0)
    corridor = []
    squeeze = []
    for op in openings:
        r_in = r_t + rec_gap
        chord = 2.0 * r_in * math.sin(math.radians(op / 2.0))
        squeeze.append(chord / d_t)
        corridor.append(rose(ring_gap=rec_gap,
                             pillar_gap=committed["pillar_gap"],
                             pillar_d=committed["pillar_d"],
                             opening_deg=op).max())
    corridor = np.array(corridor)
    squeeze = np.array(squeeze)
    # recommended opening: largest travel reduction that still lets the soft
    # TPU tendon squeeze out (chord >= 0.75*d, TPU 85A compresses easily).
    ok = squeeze >= 0.75
    rec_opening = float(openings[ok][np.argmin(corridor[ok])])

    rec = dict(ring_gap=rec_gap, pillar_gap=committed["pillar_gap"],
               pillar_d=committed["pillar_d"], opening=rec_opening)
    rose_rec = rose(ring_gap=rec["ring_gap"], pillar_gap=rec["pillar_gap"],
                    pillar_d=rec["pillar_d"], opening_deg=rec["opening"])

    # ---- sweep B: ring spacing x ring gap ----------------------------------
    spacings = np.linspace(6.0, 36.0, 25)
    gaps = np.linspace(0.4, 2.0, 17)
    heat = np.empty((len(gaps), len(spacings)))
    for gi, g in enumerate(gaps):
        for si, s in enumerate(spacings):
            heat[gi, si] = worst_deflection(
                a.span, force_n=a.force, e_mpa=a.e_tpu, d_mm=d_t,
                tilt_deg=tilt, clearance=g, ring_spacing=s,
                hot_len=hot_len)

    # ---- panel D curves -----------------------------------------------------
    lengths = np.linspace(1.0, a.span, 300)
    base_kw = dict(force_n=a.force, e_mpa=a.e_tpu, d_mm=d_t, tilt_deg=tilt,
                   hot_len=hot_len)
    curves = [
        ("bare tendon", C_ORANGE,
         deflection_curve(lengths, clearance=None, ring_spacing=None,
                          **base_kw)),
        (f"committed cage (gap {committed['ring_gap']:g} @ "
         f"{committed['spacing']:g} mm)", C_YELLOW,
         deflection_curve(lengths, clearance=committed["ring_gap"],
                          ring_spacing=committed["spacing"], **base_kw)),
        (f"recommended (gap {rec['ring_gap']:g} @ 12 mm, "
         f"opening {rec_opening:g}°)", C_AQUA,
         deflection_curve(lengths, clearance=rec["ring_gap"],
                          ring_spacing=12.0, **base_kw)),
    ]

    # ---- figure -------------------------------------------------------------
    fig = plt.figure(figsize=(14.5, 10.5), facecolor=SURFACE)
    axA = fig.add_subplot(2, 2, 1, projection="polar")
    axB = fig.add_subplot(2, 2, 2)
    axC = fig.add_subplot(2, 2, 3)
    axD = fig.add_subplot(2, 2, 4)
    for ax in (axB, axC, axD):
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        for s_ in ("left", "bottom"):
            ax.spines[s_].set_color(INK2)
        ax.tick_params(colors=INK2)
    axA.set_facecolor(SURFACE)

    axA.plot(np.radians(phis), np.minimum(rose_committed, 8.0), color=C_ORANGE,
             linewidth=2, label=f"committed (opening 120°): worst "
             f"{'escapes' if rose_committed.max() >= 12.0 else f'{rose_committed.max():.1f} mm'}")
    axA.plot(np.radians(phis), np.minimum(rose_rec, 8.0), color=C_AQUA,
             linewidth=2, label=f"recommended (opening {rec_opening:g}°): worst "
             f"{rose_rec.max():.1f} mm")
    axA.set_title("A — free travel before cage contact, by direction\n"
                  "(plotted cap 8 mm; committed opening corridor escapes)",
                  color=INK, fontsize=10)
    axA.tick_params(colors=INK2)
    axA.legend(loc="lower left", bbox_to_anchor=(-0.12, -0.18), fontsize=8,
               framealpha=0, labelcolor=INK)

    pc = axB.pcolormesh(spacings, gaps, heat, cmap="viridis", shading="auto")
    fig.colorbar(pc, ax=axB, label="worst tip deflection (mm)")
    axB.plot([committed["spacing"]], [committed["ring_gap"]], "o",
             color=C_ORANGE, markersize=9, label="committed (18, 1.2)")
    axB.plot([12.0], [rec["ring_gap"]], "o", color="white", markersize=9,
             markeredgecolor=INK, label="recommended (12, 0.8)")
    axB.set_xlabel("ring spacing (mm)", color=INK)
    axB.set_ylabel("ring radial gap = closed-direction clearance (mm)", color=INK)
    axB.set_title("B — worst deflection: ring spacing × ring gap\n"
                  f"(F={a.force*1e3:g} mN + self-weight sag, tilt {tilt:.0f}°)",
                  color=INK, fontsize=10)
    axB.legend(fontsize=8, framealpha=0.8)

    axC.plot(openings, np.minimum(corridor, 12.0), color=C_BLUE, linewidth=2,
             label="max travel through opening corridor")
    axC.axhline(committed["ring_gap"], color=INK2, linestyle="--", linewidth=1)
    axC.annotate("closed-direction clearance", (openings[0], committed["ring_gap"]),
                 xytext=(4, 4), textcoords="offset points", color=INK2, fontsize=8)
    ax2 = axC.twinx()
    ax2.plot(openings, squeeze, color=C_YELLOW, linewidth=2)
    ax2.axhline(1.0, color=C_YELLOW, linestyle=":", linewidth=1)
    ax2.axhline(0.75, color=C_YELLOW, linestyle="--", linewidth=1)
    ax2.set_ylabel("opening chord / tendon Ø (removability)", color=C_YELLOW)
    ax2.tick_params(axis="y", colors=C_YELLOW)
    ax2.spines["top"].set_visible(False)
    axC.axvline(rec_opening, color=C_AQUA, linewidth=2, alpha=0.6)
    axC.annotate(f"recommended {rec_opening:g}°\n(soft-TPU squeeze-out ≥ 0.75×Ø)",
                 (rec_opening, 6.0), xytext=(6, 0), textcoords="offset points",
                 color=C_AQUA, fontsize=9)
    axC.set_xlabel("C-ring opening angle (deg)", color=INK)
    axC.set_ylabel("corridor free travel (mm, cap 12 = escapes)", color=INK)
    axC.set_title("C — opening angle: restraint vs removability", color=INK,
                  fontsize=10)
    axC.legend(fontsize=8, framealpha=0, labelcolor=INK, loc="upper left")

    for label, color, d in curves:
        axD.plot(lengths, d, color=color, linewidth=2, label=label)
    axD.axhline(a.layer_h, color=INK2, linestyle="--", linewidth=1)
    axD.annotate(f"layer height ({a.layer_h:g} mm)", (2, a.layer_h),
                 xytext=(2, 3), textcoords="offset points", color=INK2,
                 fontsize=8)
    axD.set_yscale("log")
    axD.set_xlabel("printed tendon length (mm)", color=INK)
    axD.set_ylabel(f"tip deflection (mm) @ {a.force*1e3:g} mN + gravity",
                   color=INK)
    axD.set_title("D — wobble growth while printing (closed direction)",
                  color=INK, fontsize=10)
    axD.legend(fontsize=8, framealpha=0, labelcolor=INK)

    fig.suptitle(
        f"Level-1 cage design sweep — tendon Ø{d_t:.2f} mm, tilt {tilt:.1f}°, "
        f"E_TPU {a.e_tpu:g} MPa, hot tip {hot_len:.2f} mm "
        f"(τ={a.tau_cool:g}s / layer {a.layer_time:g}s)",
        color=INK, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(a.out, dpi=130, facecolor=SURFACE)
    print(f"wrote {a.out}")

    result = dict(
        tendon_d=d_t, tilt_deg=tilt, force_n=a.force, e_tpu_mpa=a.e_tpu,
        hot_tip_mm=hot_len,
        committed=dict(**committed,
                       worst_corridor_travel_mm=float(rose_committed.max()),
                       worst_closed_deflection_mm=float(curves[1][2].max())),
        recommended=dict(ring_gap=rec["ring_gap"], ring_spacing=12.0,
                         opening=rec_opening,
                         pillar_gap=rec["pillar_gap"],
                         pillar_d=rec["pillar_d"],
                         worst_corridor_travel_mm=float(rose_rec.max()),
                         worst_closed_deflection_mm=float(curves[2][2].max()),
                         squeeze_ratio=float(
                             2.0 * (r_t + rec["ring_gap"])
                             * math.sin(math.radians(rec_opening / 2.0)) / d_t)),
        bare=dict(worst_deflection_mm=float(curves[0][2].max())),
    )
    a.out_json.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {a.out_json}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
