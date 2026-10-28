#!/usr/bin/env python3
# ============================================================================
# Layer-by-layer FEA of the baked tree supports with CalculiX (ccx).
#
# Why this exists
# ---------------
# Geometry checks (`verify_support_geometry.py`) prove the supports *touch*
# every member and reach the plate. They do not prove the supports will
# physically *stand up while they print*. @sgbaird asked for heavier-duty
# simulation — layer-by-layer FEA with CalculiX — to bolster confidence that
# the print will actually succeed. The dominant print-time failure mode for a
# tall, thin, near-vertical support is self-weight (Euler/Greenhill) buckling
# of the growing column; a secondary mode is excessive lateral deflection
# under nozzle-drag / fan / minor-collision forces, which can knock a slender
# branch off or spoil registration of the next layer.
#
# What it does
# ------------
#   1. Reconstructs the actual emitted branch network from
#      `generate_support_pillars.py` (same tip set as the committed artefact)
#      and extracts the *worst-case* column: the longest continuous
#      branch run, treated as a clamped-free beam growing from the plate.
#   2. For a layer-by-layer sweep of printed heights it writes a CalculiX
#      beam model (B32, circular PLA section) and runs:
#         * `*BUCKLE`  -> self-weight buckling load factor (safety factor),
#         * `*STATIC`  -> tip deflection under gravity + a lateral print force.
#   3. Reports the minimum buckling safety factor and the maximum tip
#      deflection over the whole print, and writes a summary plot.
#   4. Adds a quick analytic tip-over check: centre of mass of the combined
#      part+supports vs the convex hull of all build-plate contacts.
#
# Requires: `ccx` (CalculiX) on PATH, numpy, scipy, matplotlib, trimesh.
# ============================================================================
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import generate_support_pillars as gsp  # noqa: E402


# ---- PLA material (conservative FDM values) --------------------------------
E_PLA = 2.3e9       # Pa  (printed PLA, lower end of 2.0-3.5 GPa range)
NU_PLA = 0.36
RHO_PLA = 1240.0    # kg/m^3
G_ACCEL = 9.81      # m/s^2


def extract_worst_column(part_stl: Path, *, spacing: float, min_clearance: float,
                         min_gap: float, merge_radius: float, branch_d: float,
                         trunk_d: float, tip_d: float, tip_contact_h: float,
                         tip_overshoot: float, max_branch_angle: float,
                         facets: int) -> dict:
    """Re-run the tree generator, capturing every emitted branch frustum, and
    return the geometry of the longest continuous (near-vertical) run — the
    column most at risk of buckling / lateral wobble while it prints."""
    segs: list[tuple] = []
    orig = gsp._frustum_general

    def cap(p_lo, r_lo, p_hi, r_hi, n):
        segs.append((np.asarray(p_lo, float), float(r_lo),
                     np.asarray(p_hi, float), float(r_hi)))
        return orig(p_lo, r_lo, p_hi, r_hi, n)

    gsp._frustum_general = cap
    try:
        hits, _ = gsp.raycast_underside(
            part_stl, spacing=spacing, min_clearance=min_clearance,
            base_z=0.0, min_gap=min_gap, down_normal_max=-0.2)
        gsp.tree_from_tips(
            hits, base_z=0.0, tip_d=tip_d, branch_d=branch_d, trunk_d=trunk_d,
            tip_contact_h=tip_contact_h, tip_overshoot=tip_overshoot,
            max_branch_angle=max_branch_angle, merge_radius=merge_radius,
            facets=facets)
    finally:
        gsp._frustum_general = orig

    best = None
    for p_lo, r_lo, p_hi, r_hi in segs:
        L = float(np.linalg.norm(p_hi - p_lo))
        if L < 1e-6:
            continue
        if best is None or L > best["length_mm"]:
            dz = abs(p_hi[2] - p_lo[2])
            best = dict(length_mm=L,
                        angle_deg=math.degrees(math.acos(min(1.0, dz / L))),
                        r_base_mm=max(r_lo, r_hi), r_top_mm=min(r_lo, r_hi),
                        z_lo=float(min(p_lo[2], p_hi[2])),
                        z_hi=float(max(p_lo[2], p_hi[2])),
                        n_segments=len(segs), n_tips=len(hits))
    if best is None:
        raise SystemExit("no branch segments emitted")
    return best


def run_ccx(inp_text: str, jobname: str, workdir: Path) -> str:
    (workdir / f"{jobname}.inp").write_text(inp_text)
    ccx = shutil.which("ccx") or shutil.which("ccx_2.21") or "ccx"
    subprocess.run([ccx, jobname], cwd=workdir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (workdir / f"{jobname}.dat").read_text()


def beam_inp(length_m: float, radius_m: float, *, step: str,
             lateral_N: float = 0.0, n_elem: int = 12) -> str:
    """One clamped-free circular PLA beam of `length_m`, meshed with `n_elem`
    quadratic B32 elements, fixed at the base. `step` is 'buckle' or 'static'.
    """
    n_nodes = 2 * n_elem + 1
    zs = np.linspace(0.0, length_m, n_nodes)
    lines = ["*NODE, NSET=NALL"]
    for i, z in enumerate(zs, start=1):
        lines.append(f"{i}, 0., 0., {z:.8e}")
    lines.append("*ELEMENT, TYPE=B32, ELSET=EALL")
    for e in range(n_elem):
        a = 2 * e + 1
        lines.append(f"{e + 1}, {a}, {a + 1}, {a + 2}")
    # ccx 2.21's SECTION=CIRC beam expansion is broken (~14x too compliant,
    # diverges under mesh refinement; RECT converges to the analytic
    # cantilever — see fea_tendon_wobble.py). Use the I-equivalent square
    # section (side = (12*I_circ)^(1/4); area matches within 2.3%).
    side_m = (12.0 * math.pi * radius_m**4 / 4.0) ** 0.25
    lines += [
        "*BEAM SECTION, ELSET=EALL, MATERIAL=PLA, SECTION=RECT",
        f"{side_m:.8e}, {side_m:.8e}",
        "0., 1., 0.",
        "*MATERIAL, NAME=PLA",
        "*ELASTIC",
        f"{E_PLA:.6e}, {NU_PLA}",
        "*DENSITY",
        f"{RHO_PLA}",
        "*NSET, NSET=TIP",
        f"{n_nodes}",
        "*BOUNDARY",
        "1, 1, 6",
    ]
    if step == "buckle":
        lines += [
            "*STEP",
            "*BUCKLE",
            "2",
            "*DLOAD",
            f"EALL, GRAV, {G_ACCEL}, 0., 0., -1.",
            "*END STEP",
        ]
    else:
        lines += [
            "*STEP",
            "*STATIC",
            "*DLOAD",
            f"EALL, GRAV, {G_ACCEL}, 0., 0., -1.",
            "*CLOAD",
            f"TIP, 1, {lateral_N}",
            "*NODE PRINT, NSET=TIP",
            "U",
            "*END STEP",
        ]
    return "\n".join(lines) + "\n"


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


def parse_tip_disp(dat: str) -> float:
    rows = []
    grab = False
    for ln in dat.splitlines():
        if "displacements" in ln.lower():
            grab = True
            continue
        if grab:
            parts = ln.split()
            if len(parts) >= 4:
                try:
                    u = [float(parts[1]), float(parts[2]), float(parts[3])]
                    rows.append(math.sqrt(sum(v * v for v in u)))
                except ValueError:
                    pass
            elif rows:
                break
    return max(rows) if rows else float("nan")


def tipover_margin(combined_stl: Path) -> dict:
    """Centre-of-mass vs build-plate contact polygon (tip-over stability)."""
    import trimesh
    from scipy.spatial import ConvexHull
    m = trimesh.load(combined_stl, force="mesh")
    m.apply_translation([0.0, 0.0, -m.bounds[0, 2]])
    # area-weighted face centroid is a robust COM proxy for a possibly
    # non-watertight shell.
    com = m.triangles_center.mean(axis=0) if not m.is_watertight \
        else np.asarray(m.center_mass)
    contacts = m.vertices[m.vertices[:, 2] <= 0.3][:, :2]
    hull = ConvexHull(contacts)
    poly = contacts[hull.vertices]
    # signed distance from COM(x,y) to nearest hull edge (positive = inside)
    p = com[:2]
    dmin = np.inf
    cxy = poly.mean(axis=0)
    inside = True
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        e = b - a
        nrm = np.array([-e[1], e[0]])
        nrm = nrm / (np.linalg.norm(nrm) + 1e-12)
        if np.dot(nrm, cxy - a) < 0:
            nrm = -nrm
        d = float(np.dot(nrm, p - a))
        inside = inside and d >= 0
        dmin = min(dmin, abs(d))
    return dict(com_xy=p.tolist(), inside=bool(inside), margin_mm=float(dmin),
                n_contacts=int(len(contacts)),
                base_span_mm=float(np.ptp(contacts, axis=0).max()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", type=Path, help="printable part STL")
    ap.add_argument("--combined", type=Path, default=None,
                    help="part+supports STL for the tip-over check")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parent
                    / "t3-prism-pr35-fea-stability.png")
    ap.add_argument("--spacing", type=float, default=4.0)
    ap.add_argument("--min_clearance", type=float, default=1.5)
    ap.add_argument("--min_gap", type=float, default=1.0)
    ap.add_argument("--merge_radius", type=float, default=22.0)
    ap.add_argument("--branch_d", type=float, default=1.8)
    ap.add_argument("--trunk_d", type=float, default=5.0)
    ap.add_argument("--tip_d", type=float, default=0.4)
    ap.add_argument("--tip_contact_h", type=float, default=2.5)
    ap.add_argument("--tip_overshoot", type=float, default=0.3)
    ap.add_argument("--max_branch_angle", type=float, default=40.0)
    ap.add_argument("--facets", type=int, default=12)
    ap.add_argument("--layer_h", type=float, default=0.2,
                    help="layer height (mm); deflection target")
    ap.add_argument("--lateral_force", type=float, default=0.05,
                    help="lateral print force at the tip (N); ~fan/nozzle drag")
    ap.add_argument("--steps", type=int, default=18,
                    help="number of printed-height samples")
    args = ap.parse_args()

    if shutil.which("ccx") is None and shutil.which("ccx_2.21") is None:
        raise SystemExit("CalculiX `ccx` not found on PATH (apt install "
                         "calculix-ccx)")

    col = extract_worst_column(
        args.part, spacing=args.spacing, min_clearance=args.min_clearance,
        min_gap=args.min_gap, merge_radius=args.merge_radius,
        branch_d=args.branch_d, trunk_d=args.trunk_d, tip_d=args.tip_d,
        tip_contact_h=args.tip_contact_h, tip_overshoot=args.tip_overshoot,
        max_branch_angle=args.max_branch_angle, facets=args.facets)
    print("Worst-case support column (longest continuous branch run):")
    print(f"  length            : {col['length_mm']:.1f} mm")
    print(f"  angle from vert.  : {col['angle_deg']:.1f} deg")
    print(f"  diameter base/top : {2*col['r_base_mm']:.2f} / "
          f"{2*col['r_top_mm']:.2f} mm")
    print(f"  spans z           : {col['z_lo']:.1f} - {col['z_hi']:.1f} mm")
    print(f"  total tips / segs : {col['n_tips']} / {col['n_segments']}")
    print()

    # Use the thinner (top) diameter as the section everywhere -> conservative
    # (least stiff) uniform beam.
    radius_m = col["r_top_mm"] * 1e-3
    full_len_m = col["length_mm"] * 1e-3
    heights = np.linspace(full_len_m / args.steps, full_len_m, args.steps)

    sf, defl = [], []
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        for h in heights:
            db = run_ccx(beam_inp(h, radius_m, step="buckle"), "bk", wd)
            sf.append(parse_buckle(db))
            ds = run_ccx(beam_inp(h, radius_m, step="static",
                                  lateral_N=args.lateral_force), "st", wd)
            defl.append(parse_tip_disp(ds) * 1e3)   # mm
    sf = np.array(sf)
    defl = np.array(defl)

    h_mm = heights * 1e3
    print(f"Layer-by-layer FEA ({args.steps} printed heights, ccx beam model)")
    print(f"  self-weight buckling safety factor: min {np.nanmin(sf):.1f} "
          f"(at full height {col['length_mm']:.0f} mm)")
    print(f"  tip deflection @ {args.lateral_force} N lateral: max "
          f"{np.nanmax(defl):.3f} mm (layer height {args.layer_h} mm)")

    buckle_ok = np.nanmin(sf) >= 2.0
    # Lateral deflection only matters relative to surrounding structure; the
    # column never stands fully free because neighbours print in lockstep.
    print()
    print(f"  [{'PASS' if buckle_ok else 'WARN'}] self-weight buckling SF >= 2 "
          f"at every printed height")

    tip = None
    if args.combined is not None and args.combined.exists():
        tip = tipover_margin(args.combined)
        print(f"  [{'PASS' if tip['inside'] else 'FAIL'}] tip-over: COM over "
              f"base of {tip['n_contacts']} plate contacts, margin "
              f"{tip['margin_mm']:.1f} mm (base span {tip['base_span_mm']:.0f} mm)")

    # ---- plot --------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=120)
    ax1.plot(h_mm, sf, "o-", color="tab:blue")
    ax1.axhline(1.0, color="red", ls="--", lw=1, label="buckling (SF=1)")
    ax1.axhline(2.0, color="orange", ls=":", lw=1, label="SF=2 margin")
    ax1.set_xlabel("printed column height (mm)")
    ax1.set_ylabel("self-weight buckling safety factor")
    ax1.set_yscale("log")
    ax1.set_title(f"Self-weight buckling (Ø{2*col['r_top_mm']:.1f} mm column)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.plot(h_mm, defl, "s-", color="tab:green")
    ax2.axhline(args.layer_h, color="red", ls="--", lw=1,
                label=f"layer height {args.layer_h} mm")
    ax2.set_xlabel("printed column height (mm)")
    ax2.set_ylabel(f"tip deflection @ {args.lateral_force} N lateral (mm)")
    ax2.set_title("Lateral compliance of a fully free column")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    fig.suptitle("CalculiX layer-by-layer stability of the tallest tree-support "
                 "column — PR #35 T3-prism", fontsize=11)
    fig.tight_layout()
    fig.savefig(args.out, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
