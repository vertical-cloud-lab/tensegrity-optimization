"""DiffPD soft-body drop sim — Edison Recommendation B (mid-fidelity, differentiable FEM).

Drops a soft hex-mesh "cell" (cube the size of the crutch-tip prism's
bounding box) onto a planar floor and reads back the contact response
through DiffPD's projective-dynamics solver. Material is set to TPU 85A
(E ≈ 12 MPa, nu ≈ 0.45, rho ≈ 1200 kg/m³) per @sgbaird-yolo.

DiffPD (Du et al., SIGGRAPH 2021, MIT GFX) is the original paper Edison
Recommendation B pointed at. It is *not* on PyPI, only as the
`mit-gfx/diff_pd_public` C++ source repo. We build it from source on
the runner (no Pangolin/OpenGL needed for the simulation core, despite
earlier worry — pbrt-v3 is renderer-only) and skip pbrt-v3 entirely.

Run instructions are in `simulations/README.md`. This script expects
DiffPD to be importable, which means `PYTHONPATH` includes
`<diff_pd_public>/python` and the SWIG-built shared lib has been moved
to `<diff_pd_public>/python/py_diff_pd/core/_py_diff_pd_core.so`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

# DiffPD predates NumPy 2.0; np.int was removed there. Patch back.
if not hasattr(np, "int"):
    np.int = int  # type: ignore[attr-defined]

import matplotlib.pyplot as plt  # noqa: E402  (after numpy shim)

OUTDIR = Path(__file__).parent / "outputs"
OUTDIR.mkdir(exist_ok=True)


def _import_diffpd():
    """Import py_diff_pd, with a clear error if the build wasn't set up."""
    try:
        from py_diff_pd.common.common import ndarray  # noqa: F401
        from py_diff_pd.common.hex_mesh import generate_hex_mesh, get_contact_vertex  # noqa: F401
        from py_diff_pd.core.py_diff_pd_core import (  # noqa: F401
            HexMesh3d,
            HexDeformable,
            StdRealVector,
            StdIntVector,
        )
        return generate_hex_mesh, get_contact_vertex, HexMesh3d, HexDeformable, StdRealVector, StdIntVector, ndarray
    except ModuleNotFoundError as e:
        msg = (
            "py_diff_pd is not importable. Build DiffPD from source first:\n"
            "  git clone --recursive https://github.com/mit-gfx/diff_pd_public.git\n"
            "  cd diff_pd_public/cpp/core/src && swig -c++ -python py_diff_pd_core.i\n"
            "  cd ../../ && mkdir -p build && cd build && cmake -DPARDISO_AVAILABLE=OFF .. && make -j4\n"
            "  cd .. && mv core/src/py_diff_pd_core.py ../python/py_diff_pd/core/\n"
            "          mv build/libpy_diff_pd_core.so   ../python/py_diff_pd/core/_py_diff_pd_core.so\n"
            "  printf \"root_path = '$(pwd)/..'\\n\" > ../python/py_diff_pd/common/project_path.py\n"
            "  export PYTHONPATH=<diff_pd_public>/python:$PYTHONPATH\n"
            "Then re-run this script. (See simulations/README.md.)"
        )
        raise SystemExit(f"{msg}\n\nUnderlying error: {e}")


def run_drop(youngs_modulus_pa: float = 12e6,
             poissons_ratio: float = 0.45,
             density_kgm3: float = 1200.0,
             cell_side_m: float = 0.024,  # crutch-tip prism cell
             drop_height_m: float = 0.10,  # crutch-regime ΔV ≈ 1.4 m/s
             refinement: int = 4,
             dt: float = 2e-3,
             frames: int = 80) -> dict:
    """Drop a soft-body hex cube and return summary stats."""
    (
        generate_hex_mesh,
        get_contact_vertex,
        HexMesh3d,
        HexDeformable,
        StdRealVector,
        StdIntVector,
        ndarray,
    ) = _import_diffpd()

    # Hex mesh: refinement^3 voxels of size dx = cell_side / refinement.
    voxels = np.ones((refinement, refinement, refinement), dtype=int)
    dx = cell_side_m / refinement
    tmp_bin = "/tmp/_diffpd_cell.bin"
    generate_hex_mesh(voxels, dx, (0.0, 0.0, drop_height_m), tmp_bin)

    mesh = HexMesh3d()
    mesh.Initialize(tmp_bin)

    # Lame parameters from E, nu.
    la = youngs_modulus_pa * poissons_ratio / (
        (1.0 + poissons_ratio) * (1.0 - 2.0 * poissons_ratio)
    )
    mu = youngs_modulus_pa / (2.0 * (1.0 + poissons_ratio))

    deformable = HexDeformable()
    deformable.Initialize(tmp_bin, density_kgm3, "none", youngs_modulus_pa, poissons_ratio)
    deformable.AddStateForce("gravity", ndarray([0.0, 0.0, -9.81]))
    deformable.AddPdEnergy("corotated", [2.0 * mu], [])
    deformable.AddPdEnergy("volume", [la], [])

    contact_idx = get_contact_vertex(mesh)
    deformable.SetFrictionalBoundary("planar", [0.0, 0.0, 1.0, 0.0], contact_idx)

    dofs = deformable.dofs()
    q = ndarray(mesh.py_vertices()).copy()
    v = np.zeros(dofs)

    pd_opt = {
        "max_pd_iter": 200, "max_ls_iter": 10, "abs_tol": 1e-6, "rel_tol": 1e-3,
        "verbose": 0, "thread_ct": 4, "use_bfgs": 1, "bfgs_history_size": 10,
    }

    com_z = []
    com_vz = []
    com_az = []
    times = []
    active = StdIntVector(0)
    prev_vz = 0.0
    for k in range(frames):
        q_next = StdRealVector(dofs)
        v_next = StdRealVector(dofs)
        a = StdRealVector(0)
        f = StdRealVector(np.zeros(dofs))
        deformable.PyForward("pd_eigen", q, v, a, f, dt, pd_opt,
                             q_next, v_next, active)
        q = ndarray(q_next).copy()
        v = ndarray(v_next).copy()
        cz = q.reshape(-1, 3)[:, 2].mean()
        cvz = v.reshape(-1, 3)[:, 2].mean()
        com_z.append(cz)
        com_vz.append(cvz)
        com_az.append((cvz - prev_vz) / dt)
        prev_vz = cvz
        times.append(k * dt)

    os.unlink(tmp_bin)

    com_z = np.asarray(com_z)
    com_vz = np.asarray(com_vz)
    com_az = np.asarray(com_az)
    times = np.asarray(times)

    peak_g = float(np.max(np.abs(com_az)) / 9.81)
    settled_z = float(com_z[-1])
    return {
        "t": times, "com_z": com_z, "com_vz": com_vz, "com_az": com_az,
        "peak_g": peak_g, "settled_z": settled_z, "dofs": dofs,
        "elements": mesh.NumOfElements(), "contact_verts": len(contact_idx),
    }


def main():
    print("[diffpd] running TPU-85A soft-body drop ...")
    res = run_drop()
    print(f"  DOFs={res['dofs']}, elements={res['elements']}, contact verts={res['contact_verts']}")
    print(f"  peak |COM accel|: {res['peak_g']:.1f} g")
    print(f"  settled COM z   : {res['settled_z'] * 1e3:.2f} mm")

    fig, axes = plt.subplots(3, 1, figsize=(7, 8), sharex=True)
    axes[0].plot(res["t"] * 1e3, res["com_z"] * 1e3)
    axes[0].set_ylabel("COM z (mm)")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(res["t"] * 1e3, res["com_vz"])
    axes[1].set_ylabel("COM vz (m/s)")
    axes[1].grid(True, alpha=0.3)
    axes[2].plot(res["t"] * 1e3, res["com_az"] / 9.81)
    axes[2].set_ylabel("COM az (g)")
    axes[2].set_xlabel("time (ms)")
    axes[2].grid(True, alpha=0.3)
    fig.suptitle(
        f"DiffPD TPU-85A soft cube drop "
        f"(peak {res['peak_g']:.1f} g, {res['dofs']} DoFs)"
    )
    fig.tight_layout()
    out = OUTDIR / "diffpd_drop.png"
    fig.savefig(out, dpi=120)
    print(f"  wrote {out}")

    np.savez(OUTDIR / "diffpd_drop.npz",
             t=res["t"], com_z=res["com_z"],
             com_vz=res["com_vz"], com_az=res["com_az"])


if __name__ == "__main__":
    main()
