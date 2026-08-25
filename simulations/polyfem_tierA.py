"""Tier-A PolyFEM+IPC drops of the printed articles, with viscoelastic TPU/PLA.

The Tier-A promotion flagged across this PR's zeta / rebound / objective-swap
threads: volumetric PLA struts and TPU tendons (welded mesh from
``tprism_mesh``) impacting a rigid plane through IPC contact, with
**strain-rate viscous damping in both materials** (PolyFEM's per-material
``psi``/``phi`` Kelvin-Voigt-type dissipation) so the article itself carries
a loss mechanism, which is exactly what Tiers B and C lack.

Scope, stated plainly: this is the *article on a rigid floor* at the
campaign's measured impact velocity, not the full tower (no carriage, no PU
mat, no slide rails).  So its observables are article-intrinsic: flexural
ringdown frequency and damping of the free top vertex after the bounce,
COM restitution against a rigid floor (the article's own share of the
rebound, with no mat to hide behind), and peak top-vertex acceleration.
They complement the Tier-B run (which carries the full calibrated rig but
lumps the materials) rather than replacing it.

Material inputs, all derived rather than tuned:

* PLA modulus: wall-aware bending homogenization from
  ``drop_tower_tierB.bending_modulus_MPa`` (perimeter walls carry the outer
  fiber; ~2.8-3.2 GPa depending on strut diameter).
* densities: solved per article so the *meshed* volumes weigh what the
  scale said (the mesh has no joint housings, so PLA density absorbs the
  housing share, keeping total mass and its strut-wise distribution right).
* viscosity: ``psi = tan_delta * G / omega_ref`` at the measured ringdown
  band center (380 Hz), i.e. the same loss-tangent mapping Tier B uses,
  expressed as a continuum shear viscosity: ~430 Pa s for TPU 85A
  (tan delta 0.25), ~27 kPa s for PLA (eta 0.05).

Run::

    python polyfem_tierA.py --limit 4 --workers 3
    python polyfem_tierA.py                # full roster, measured first
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
G = 9.80665

IMPACT_V_MPS = 5.30           # measured campaign mean delta-v (drop_tower_sim)
DT_S = 1.0e-4                 # resolves the 294-468 Hz band (>20 samples/cycle)
N_STEPS = 220                 # 22 ms: impact (~5 ms) + free-flight ringdown
F_REF_HZ = 380.0
TAN_DELTA_TPU = 0.25
ETA_PLA = 0.05


def _viscosities() -> tuple[float, float]:
    """(psi_pla, psi_tpu) in Pa s from the loss tangents at f_ref."""
    from printable_design import PLA, TPU85A
    omega = 2.0 * math.pi * F_REF_HZ
    g_pla = PLA.young_MPa * 1e6 / (2.0 * (1.0 + 0.36))
    g_tpu = TPU85A.young_MPa * 1e6 / (2.0 * (1.0 + 0.45))
    return ETA_PLA * g_pla / omega, TAN_DELTA_TPU * g_tpu / omega


def _analytic_volumes_m3(design) -> tuple[float, float]:
    """(V_pla, V_tpu) of the meshed cylinder primitives, analytically."""
    from tprism_geometry import CABLES, STRUTS, tprism_nodes
    nodes = tprism_nodes(radius=design.radius_m, height=design.height_m,
                         twist=design.twist_rad)
    v_pla = sum(math.pi * (design.strut_diameter_m / 2) ** 2
                * float(np.linalg.norm(nodes[a] - nodes[b]))
                for a, b in STRUTS)
    inset = design.strut_diameter_m * 0.6
    v_tpu = sum(math.pi * (design.tendon_diameter_m / 2) ** 2
                * max(float(np.linalg.norm(nodes[a] - nodes[b])) - 2 * inset, 1e-4)
                for a, b in CABLES)
    return v_pla, v_tpu


def _mesh_masses_m3(msh: Path) -> tuple[float, float]:
    """(V_pla, V_tpu) in m^3 from the physical-volume tags of the mesh."""
    import meshio
    m = meshio.read(msh)
    v = {1: 0.0, 2: 0.0}
    for block, tags in zip(m.cells, m.cell_data.get("gmsh:physical", [])):
        if block.type != "tetra":
            continue
        pts = m.points[block.data]                      # (n, 4, 3)
        d = pts[:, 1:] - pts[:, :1]
        vol = np.abs(np.linalg.det(d)) / 6.0
        for tag in (1, 2):
            v[tag] += float(vol[np.asarray(tags) == tag].sum())
    return v[1], v[2]


def tierA_one(job: tuple) -> dict:
    """Mesh + run one article.  Top-level for pickling."""
    row, workers_tag = job
    import polyfem_drop as pf
    from bo_evaluator import parameterization_to_design
    from drop_tower_tierB import bending_modulus_MPa
    from tprism_mesh import build_tprism_msh
    from zeta_analysis import ringdown_fit

    pid = row["print_id"]
    design = parameterization_to_design(
        {k: float(row[k]) for k in
         ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")})

    mesh_dir = Path(f"/tmp/polyfem_tierA_{pid}_mesh")
    mesh_dir.mkdir(parents=True, exist_ok=True)
    msh = mesh_dir / "tprism.msh"
    # gmsh's OCC fragment is touchy about tendon-strut intersections at some
    # twist/diameter combinations ("1D mesh ... closed loop"); retry across
    # tendon inset factors before giving up
    info = None
    last_err = None
    for inset in (0.6, 0.8, 0.5, 0.7, 1.0):
        try:
            info = build_tprism_msh(
                msh,
                radius=design.radius_m,
                height=design.height_m,
                twist=design.twist_rad,
                strut_d=design.strut_diameter_m,
                tendon_d=design.tendon_diameter_m,
                drop_height=0.0005,
                lc_strut=max(design.strut_diameter_m * 0.5, 0.0015),
                lc_tendon=max(design.tendon_diameter_m * 0.6, 0.001),
                tendon_inset_factor=inset,
            )
            # a failed earlier inset leaves gmsh initialized with a stale
            # model, and the "successful" retry can then write a truncated
            # file ($Entities but no $Nodes/$Elements); validate the write
            if "$Elements" not in msh.read_text(errors="ignore"):
                raise RuntimeError("gmsh wrote a truncated mesh")
            break
        except Exception as exc:               # noqa: BLE001
            info = None
            last_err = exc
            try:
                import gmsh
                gmsh.finalize()
            except Exception:                  # noqa: BLE001
                pass
    if info is None:
        return {"print_id": pid, "ok": False, "err": f"mesh: {last_err}"[:300]}

    # densities solved so the meshed article weighs what the scale said;
    # TPU at its printed density, PLA absorbs the joint/housing share.
    # Volumes are the analytic cylinder volumes of the meshed primitives
    # (meshio chokes on some gmsh-4.1 fragment output, and the welded
    # overlaps are a few percent of the totals).
    v_pla, v_tpu = _analytic_volumes_m3(design)
    rho_tpu = 1200.0 * 0.986
    rho_pla = max((float(row["mass_g"]) * 1e-3 - rho_tpu * v_tpu), 1e-4) / v_pla
    psi_pla, psi_tpu = _viscosities()
    e_pla = bending_modulus_MPa(design.strut_diameter_m) * 1e6

    work = Path(f"/tmp/polyfem_tierA_{pid}")
    cfg = pf.build_prism_input_json(
        msh, pf._resolve_paths()[2],
        E_pla_pa=e_pla, nu_pla=0.36, rho_pla=rho_pla,
        E_tpu_pa=12.0e6, nu_tpu=0.45, rho_tpu=rho_tpu,
        dt=DT_S, n_steps=N_STEPS)
    for mat in cfg["materials"]:
        mat["psi"] = psi_tpu if mat["id"] == 2 else psi_pla
        mat["phi"] = 0.0
    # the 5.3 m/s impact steps are much harder than the settle-under-gravity
    # runs this JSON was written for
    cfg["solver"]["nonlinear"]["max_iterations"] = 200
    cfg["initial_conditions"] = {
        "velocity": [{"id": 1, "value": [0.0, -IMPACT_V_MPS, 0.0]},
                     {"id": 2, "value": [0.0, -IMPACT_V_MPS, 0.0]}]}

    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    cfg_path = work / "drop.json"
    cfg_path.write_text(json.dumps(cfg, indent=2))
    binary = pf._resolve_paths()[0]
    proc = subprocess.run(
        [str(binary), "-j", str(cfg_path), "-o", str(work),
         "--log_level", "error"],
        capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        return {"print_id": pid, "ok": False,
                "err": (proc.stdout + proc.stderr)[-500:]}

    # per-step top-vertex + COM tracks from the .vtu sequence
    import meshio
    import xml.etree.ElementTree as ET
    tops, coms = [], []
    top_idx = None
    for k in range(N_STEPS + 1):
        vtm = work / f"step_{k}.vtm"
        if not vtm.exists():
            continue
        vtu = None
        for da in ET.parse(vtm).getroot().iter("DataSet"):
            f = da.attrib.get("file", "")
            if f.endswith(".vtu"):
                vtu = work / f
                break
        if vtu is None or not vtu.exists():
            continue
        m = meshio.read(vtu)
        pts = m.points
        if top_idx is None:
            top_idx = int(np.argmax(pts[:, 1]))
        tops.append(pts[top_idx].copy())
        coms.append(pts.mean(axis=0))
    tops = np.asarray(tops)
    coms = np.asarray(coms)
    if tops.shape[0] < 50:
        return {"print_id": pid, "ok": False, "err": "too few steps"}

    t = np.arange(tops.shape[0]) * DT_S
    a_top = np.gradient(np.gradient(tops[:, 1], DT_S), DT_S) / G
    v_com = np.gradient(coms[:, 1], DT_S)
    peak_g = float(np.nanmax(np.abs(a_top)))
    # restitution: max upward COM velocity after the impact
    e_reb = float(np.max(v_com[np.argmin(v_com):])) / IMPACT_V_MPS
    # ringdown on the free-flight relative accel: top vertex minus COM
    # (COM is ballistic after the bounce, so the difference is the article's
    # own vibration)
    rel = a_top - np.gradient(np.gradient(coms[:, 1], DT_S), DT_S) / G
    i0 = int(np.argmin(v_com)) + int(0.004 / DT_S)
    fit = (ringdown_fit(t[i0:], rel[i0:], fmin=50.0)
           if tops.shape[0] - i0 > 60 else {})

    np.savez(OUT / f"tierA_{pid}.npz", t=t, top=tops, com=coms, a_top_g=a_top)
    return {
        "print_id": pid, "ok": True, "tets": int(info["tets"]),
        "peak_top_g": peak_g,
        "e_rebound_article": max(e_reb, 0.0),
        "fn_hz": fit.get("fn_hz", float("nan")),
        "zeta_pct": fit.get("zeta_pct", float("nan")),
        "ringdown_r2": fit.get("r2", float("nan")),
        "rho_pla_eff": rho_pla,
    }


PRIORITY = ["bpx68c", "6lhxfy", "9hhbkp", "autv5r", "nvxsrv", "6nheas",
            "bag26v", "r2d2c1", "r2d2c2", "r2d2c3", "r2d2c4", "r2d2c5",
            "r2d2c6", "r2d2c7", "r2d2c8", "r2d2c9", "ebdna8", "1zm8rv",
            "ajhby6", "dea4ls", "ghmj4y"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args(argv)

    from drop_tower_tierB import article_roster
    roster = article_roster().set_index("print_id", drop=False)
    order = [p for p in PRIORITY if p in roster.index]
    if args.only:
        order = [p for p in order if p in set(args.only)]
    if args.limit:
        order = order[:args.limit]

    OUT.mkdir(exist_ok=True)
    out_csv = OUT / "tierA_articles.csv"
    done = []
    if out_csv.exists():
        done = pd.read_csv(out_csv).to_dict("records")
        have = {d["print_id"] for d in done if d.get("ok")}
        order = [p for p in order if p not in have]

    jobs = [(roster.loc[p].to_dict(), "") for p in order]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(tierA_one, j): j[0]["print_id"] for j in jobs}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                res = fut.result()
            except Exception as exc:            # noqa: BLE001
                res = {"print_id": pid, "ok": False, "err": str(exc)[:300]}
            done.append(res)
            pd.DataFrame(done).to_csv(out_csv, index=False)   # incremental
            print(f"{pid}: {res}", flush=True)
    print(f"wrote {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
