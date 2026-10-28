#!/usr/bin/env python3
# ============================================================================
# Level-2 CalculiX FEA of the growing TPU tendon inside its guide cage.
#
# Why this exists
# ---------------
# The Level-1 sweep (`sweep_cage_design.py`) treats a cage ring as a fresh
# clamp: deflection restarts from the ring clearance. A real ring is a
# *unilateral point stop* — it caps translation at its own height but the
# beam's rotation carries past it, so a single ring barely helps the tip.
# Whether the cage works therefore depends on *multiple rings engaging
# together*, which only a contact FEA resolves. This script is the
# Edison-recommended Level-2 "structural contact FEA" (CalculiX):
#
#   * the partially printed tendon is a tilted quadratic-beam (B32) cantilever
#     clamped at its bonded lower joint, grown over a sweep of printed
#     lengths (element activation by re-meshing per height, as in
#     `fea_support_stability.py`);
#   * geometrically nonlinear *STATIC step with gravity (the tilted tendon
#     sags under its own weight toward its lean side) plus a lateral
#     nozzle/bead-drag force at the print front, worst-case aligned with the
#     sag;
#   * every C-ring below the print front is a unilateral point stop at the
#     ring's radial clearance, solved with an active-set loop (GAPUNI gap
#     elements conflict with the internal MPC "knots" ccx expands beam nodes
#     into and stall at larger models): rings whose node overshoots the
#     clearance get a prescribed displacement at the clearance, and are
#     released again if their reaction force flips into "pulling" — the
#     exact unilateral-contact solution for this monotone loading;
#   * the top `--hot_len` mm of the tendon gets `--hot_frac` x E (material
#     still near melt, Newton cooling; Level 3 refines the length from
#     sliced layer times);
#   * a *BUCKLE step for the bare tendon's self-weight stability.
#
# Compares: bare tendon / committed cage (gap 1.2 mm @ 18 mm) / recommended
# cage from the Level-1 sweep (gap 0.8 mm @ 12 mm), and overlays the Level-1
# analytic curves to quantify how optimistic the fresh-clamp assumption is.
#
# Requires: ccx (CalculiX) on PATH, numpy, matplotlib.
# ============================================================================
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from sweep_cage_design import deflection_curve

C_BLUE, C_ORANGE, C_AQUA, C_YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"

RHO_TPU = 1.21e-9      # tonne/mm^3  (ccx consistent units: N, mm, tonne, s)
G_MMS2 = 9810.0        # mm/s^2


def tendon_inp(length: float, *, radius: float, tilt_deg: float,
               e_tpu: float, nu: float, elem_len: float,
               ring_spacing: float | None, ring_clearance: float,
               force_n: float, hot_len: float, hot_frac: float,
               step: str, active: dict[int, float] | None = None
               ) -> tuple[str, int, list[int]]:
    """CalculiX input for a printed length of the tilted tendon.

    Beam axis u = (sin t, 0, cos t); lateral load +x (adds to gravity sag).
    Rings are beam nodes at every `ring_spacing` of printed arc length;
    `active` maps ring node id -> prescribed ux (the active contact set).
    Returns (inp text, tip node id, ring node ids).
    """
    t = math.radians(tilt_deg)
    u = np.array([math.sin(t), 0.0, math.cos(t)])
    n_elem = max(4, int(round(length / elem_len)))
    n_nodes = 2 * n_elem + 1
    s = np.linspace(0.0, length, n_nodes)
    lines = ["*NODE, NSET=NALL"]
    for i, si in enumerate(s, start=1):
        p = si * u
        lines.append(f"{i}, {p[0]:.6e}, {p[1]:.6e}, {p[2]:.6e}")

    # hot (near-melt) top segment vs cooled body
    hot_from = length - min(hot_len, length)
    cold, hot = [], []
    for e in range(n_elem):
        a = 2 * e + 1
        mid_s = s[a]          # centre node arc-length
        (hot if mid_s >= hot_from and hot_len > 0 else cold).append(
            (e + 1, a, a + 1, a + 2))
    for name, elems in (("COLD", cold), ("HOT", hot)):
        if not elems:
            continue
        lines.append(f"*ELEMENT, TYPE=B32, ELSET={name}")
        for eid, a, b, c in elems:
            lines.append(f"{eid}, {a}, {b}, {c}")

    # ring stop locations = beam nodes nearest each ring height
    ring_nodes: list[int] = []
    if ring_spacing is not None:
        h = ring_spacing
        while h < length - 1e-6:
            k = int(np.argmin(np.abs(s - h)))
            if k > 0:
                ring_nodes.append(k + 1)
            h += ring_spacing

    # ccx 2.21's SECTION=CIRC beam expansion is broken (~14x too compliant,
    # diverges under mesh refinement; RECT converges to the analytic
    # cantilever). Use the I-equivalent square: side = (12*I_circ)^(1/4),
    # which also matches the circular area within 2.3% (gravity load).
    i_circ = math.pi * radius**4 / 4.0
    side = (12.0 * i_circ) ** 0.25
    for name in ("COLD", "HOT"):
        if any(ln.endswith(f"ELSET={name}") for ln in lines):
            lines += [f"*BEAM SECTION, ELSET={name}, MATERIAL="
                      f"{'TPUHOT' if name == 'HOT' else 'TPU'}, SECTION=RECT",
                      f"{side:.6f}, {side:.6f}", "0., 1., 0."]
    lines += ["*MATERIAL, NAME=TPU", "*ELASTIC", f"{e_tpu}, {nu}",
              "*DENSITY", f"{RHO_TPU}",
              "*MATERIAL, NAME=TPUHOT", "*ELASTIC",
              f"{e_tpu * hot_frac}, {nu}", "*DENSITY", f"{RHO_TPU}"]
    lines += ["*NSET, NSET=TIP", f"{n_nodes}"]
    if ring_nodes:
        lines.append("*NSET, NSET=RINGS")
        lines.append(", ".join(str(r) for r in ring_nodes))
    lines += ["*BOUNDARY", "1, 1, 6"]
    for nid, ux in (active or {}).items():
        lines.append(f"{nid}, 1, 1, {ux}")

    if step == "buckle":
        lines += ["*STEP", "*BUCKLE", "2",
                  "*DLOAD", f"COLD, GRAV, {G_MMS2}, 0., 0., -1.",
                  "*END STEP"]
    else:
        lines += ["*STEP, NLGEOM", "*STATIC", "0.1, 1.0",
                  "*DLOAD", f"COLD, GRAV, {G_MMS2}, 0., 0., -1."]
        if any("ELSET=HOT" in ln for ln in lines):
            lines += ["*DLOAD", f"HOT, GRAV, {G_MMS2}, 0., 0., -1."]
        lines += ["*CLOAD", f"TIP, 1, {force_n}",
                  "*NODE PRINT, NSET=NALL", "U"]
        if active:
            lines += ["*NODE PRINT, NSET=RINGS", "RF"]
        lines += ["*END STEP"]
    return "\n".join(lines) + "\n", n_nodes, ring_nodes


def solve_with_rings(L: float, wd: Path, *, ring_clearance: float,
                     **kw) -> float:
    """Active-set unilateral contact: prescribe ux = clearance at every ring
    node that overshoots it; release rings whose reaction force pulls
    (+x, i.e. the ring would have to hold the tendon back from returning).
    Returns tip |ux|."""
    active: dict[int, float] = {}
    for _ in range(12):
        inp, tip, rings = tendon_inp(L, ring_clearance=ring_clearance,
                                     step="static", active=active, **kw)
        dat = run_ccx(inp, wd, "st")
        ux = parse_ux_all(dat)
        rf = parse_rf(dat) if active else {}
        changed = False
        for r in rings:
            if r not in active and ux.get(r, 0.0) > ring_clearance + 1e-6:
                active[r] = ring_clearance
                changed = True
        for r in list(active):
            if rf.get(r, -1.0) > 1e-9:      # ring pulling -> release
                del active[r]
                changed = True
        if not changed:
            return abs(ux.get(tip, float("nan")))
    return abs(ux.get(tip, float("nan")))


def run_ccx(inp: str, wd: Path, job: str) -> str:
    (wd / f"{job}.inp").write_text(inp)
    subprocess.run(["ccx", job], cwd=wd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (wd / f"{job}.dat").read_text()


def _parse_blocks(dat: str, header: str) -> dict[int, float]:
    """Last block whose header contains `header`: node id -> x component."""
    out: dict[int, float] = {}
    cur: dict[int, float] | None = None
    for ln in dat.splitlines():
        low = ln.strip().lower()
        if header in low:
            cur = {}
            continue
        if cur is not None:
            parts = ln.split()
            if len(parts) >= 4:
                try:
                    cur[int(parts[0])] = float(parts[1])
                    out = cur
                    continue
                except ValueError:
                    pass
            if cur:
                cur = None
    return out


def parse_ux_all(dat: str) -> dict[int, float]:
    return _parse_blocks(dat, "displacements")


def parse_rf(dat: str) -> dict[int, float]:
    return _parse_blocks(dat, "forces")


def parse_buckle(dat: str) -> float:
    factors = []
    grab = False
    for ln in dat.splitlines():
        if "BUCKLING" in ln:
            grab = True
            continue
        if grab:
            parts = ln.split()
            if len(parts) == 2 and parts[0].isdigit():
                try:
                    factors.append(abs(float(parts[1])))
                except ValueError:
                    pass
            elif factors:
                break
    return min(factors) if factors else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    ap.add_argument("--tendon_d", type=float, default=4.95)
    ap.add_argument("--tilt", type=float, default=19.7)
    ap.add_argument("--span", type=float, default=80.0)
    ap.add_argument("--force", type=float, default=0.01,
                    help="lateral nozzle/bead-drag force at the front, N")
    ap.add_argument("--e_tpu", type=float, default=15.0)
    ap.add_argument("--nu", type=float, default=0.48)
    ap.add_argument("--elem_len", type=float, default=1.0)
    ap.add_argument("--hot_len", type=float, default=0.5,
                    help="near-melt top length, mm (Level 3 refines)")
    ap.add_argument("--hot_frac", type=float, default=0.1)
    ap.add_argument("--steps", type=int, default=16)
    ap.add_argument("--layer_h", type=float, default=0.2)
    ap.add_argument("--out", type=Path,
                    default=here / "t3-prism-pr35-fea-tendon-wobble.png")
    ap.add_argument("--out_json", type=Path,
                    default=here / "t3-prism-pr35-fea-tendon-wobble.json")
    a = ap.parse_args()

    if shutil.which("ccx") is None:
        raise SystemExit("CalculiX `ccx` not found (apt install calculix-ccx)")

    radius = a.tendon_d / 2.0
    lengths = np.linspace(a.span / a.steps, a.span, a.steps)
    configs = [
        ("bare tendon", C_ORANGE, None, 0.0),
        ("committed cage (gap 1.2 @ 18 mm)", C_YELLOW, 18.0, 1.2),
        ("recommended cage (gap 0.8 @ 12 mm)", C_AQUA, 12.0, 0.8),
    ]

    results: dict[str, list[float]] = {}
    buckle_sf: list[float] = []
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        for label, _, spacing, gap in configs:
            vals = []
            for L in lengths:
                vals.append(solve_with_rings(
                    float(L), wd, ring_clearance=gap, radius=radius,
                    tilt_deg=a.tilt, e_tpu=a.e_tpu, nu=a.nu,
                    elem_len=a.elem_len, ring_spacing=spacing,
                    force_n=a.force, hot_len=a.hot_len,
                    hot_frac=a.hot_frac))
            results[label] = vals
            print(f"{label:38s} tip deflection @ {a.span:g} mm: "
                  f"{vals[-1]:.2f} mm (max during print {max(vals):.2f} mm)")
        for L in lengths:
            inp, _, _ = tendon_inp(
                float(L), radius=radius, tilt_deg=a.tilt, e_tpu=a.e_tpu,
                nu=a.nu, elem_len=a.elem_len, ring_spacing=None,
                ring_clearance=0.0, force_n=0.0, hot_len=0.0,
                hot_frac=a.hot_frac, step="buckle")
            buckle_sf.append(parse_buckle(run_ccx(inp, wd, "bk")))
    print(f"bare-tendon self-weight buckling SF: min "
          f"{np.nanmin(buckle_sf):.1f} at full height")

    # analytic (Level-1) overlays
    dense = np.linspace(1.0, a.span, 300)
    analytic = {
        "bare tendon": deflection_curve(
            dense, force_n=a.force, e_mpa=a.e_tpu, d_mm=a.tendon_d,
            tilt_deg=a.tilt, clearance=None, ring_spacing=None,
            hot_len=a.hot_len, hot_frac=a.hot_frac),
        "committed cage (gap 1.2 @ 18 mm)": deflection_curve(
            dense, force_n=a.force, e_mpa=a.e_tpu, d_mm=a.tendon_d,
            tilt_deg=a.tilt, clearance=1.2, ring_spacing=18.0,
            hot_len=a.hot_len, hot_frac=a.hot_frac),
        "recommended cage (gap 0.8 @ 12 mm)": deflection_curve(
            dense, force_n=a.force, e_mpa=a.e_tpu, d_mm=a.tendon_d,
            tilt_deg=a.tilt, clearance=0.8, ring_spacing=12.0,
            hot_len=a.hot_len, hot_frac=a.hot_frac),
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.4),
                                   facecolor=SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(INK2)
        ax.tick_params(colors=INK2)

    for label, color, _, _ in configs:
        ax1.plot(lengths, results[label], "o", color=color, markersize=6,
                 label=f"{label} — ccx contact FEA")
        ax1.plot(dense, analytic[label], "--", color=color, linewidth=1.4,
                 alpha=0.7, label=f"{label} — Level-1 analytic")
    ax1.axhline(a.layer_h, color=INK2, linestyle=":", linewidth=1)
    ax1.annotate(f"layer height ({a.layer_h:g} mm)", (2, a.layer_h),
                 xytext=(2, 3), textcoords="offset points",
                 color=INK2, fontsize=8)
    ax1.set_yscale("log")
    ax1.set_xlabel("printed tendon length (mm)", color=INK)
    ax1.set_ylabel(f"print-front lateral deflection (mm) @ "
                   f"{a.force*1e3:g} mN + gravity", color=INK)
    ax1.set_title("A — growing-tendon contact FEA vs analytic model",
                  color=INK, fontsize=10)
    ax1.legend(fontsize=7, framealpha=0, labelcolor=INK)

    ax2.plot(lengths, buckle_sf, "o-", color=C_BLUE)
    ax2.axhline(1.0, color="red", linestyle="--", linewidth=1,
                label="buckling (SF = 1)")
    ax2.set_yscale("log")
    ax2.set_xlabel("printed tendon length (mm)", color=INK)
    ax2.set_ylabel("self-weight buckling safety factor", color=INK)
    ax2.set_title("B — bare-tendon self-weight buckling (ccx *BUCKLE)",
                  color=INK, fontsize=10)
    ax2.legend(fontsize=8, framealpha=0, labelcolor=INK)

    fig.suptitle(
        f"Level-2 CalculiX growing-tendon FEA — Ø{a.tendon_d:g} mm TPU 85A, "
        f"tilt {a.tilt:g}°, E={a.e_tpu:g} MPa, hot tip {a.hot_len:g} mm "
        f"@ {a.hot_frac:g}×E, active-set ring contacts", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(a.out, dpi=140, facecolor=SURFACE)
    print(f"wrote {a.out}")

    out = dict(
        lengths_mm=[float(v) for v in lengths],
        buckling_sf=[float(v) for v in buckle_sf],
        force_n=a.force, tendon_d=a.tendon_d, tilt_deg=a.tilt,
        e_tpu_mpa=a.e_tpu, hot_len_mm=a.hot_len, hot_frac=a.hot_frac,
        tip_deflection_mm={k: [float(x) for x in v]
                           for k, v in results.items()},
    )
    a.out_json.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {a.out_json}")


if __name__ == "__main__":
    main()
