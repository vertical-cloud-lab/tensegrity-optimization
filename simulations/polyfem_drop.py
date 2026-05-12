"""PolyFEM + IPC drop sim — Edison Recommendation A (high-fidelity contact).

Drops a soft NeoHookean cube (TPU 85A) of the crutch-tip prism cell size
onto a horizontal ground plane through PolyFEM's Implicit-Newmark / IPC
barrier-method contact solver. PolyFEM (Schneider et al., ACM TOG 2019)
is the reference Edison Rec A — penalty-free, intersection-free contact
that the rigid-strut MuJoCo / PyBullet / PyChrono engines and the
particle-spring Newton stand-in can't deliver.

The PyPI `polyfempy` sdist is broken (no `CMakeLists.txt`); we build the
C++ binary from `polyfem/polyfem` with CMake + the bundled CPM ipc-toolkit /
suite-sparse / Eigen / hypre dependencies, then call `PolyFEM_bin -j ...`
as a subprocess. ~25 min build (`cmake --build . --target PolyFEM_bin -j4`),
~10 GB build dir, ~160 MB binary. See `simulations/README.md` for the
recipe.

Run:
    export POLYFEM_BIN=/path/to/PolyFEM_bin
    export POLYFEM_DATA_DIR=/path/to/polyfem-data   # for cube.msh + plane.obj
    python simulations/polyfem_drop.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTDIR = Path(__file__).parent / "outputs"
OUTDIR.mkdir(exist_ok=True)


def _resolve_paths() -> tuple[Path, Path, Path]:
    """Locate the PolyFEM binary and the cube.msh / plane.obj meshes."""
    binary = os.environ.get("POLYFEM_BIN") or shutil.which("PolyFEM_bin")
    if not binary:
        for guess in ("/home/runner/builds/polyfem/build/PolyFEM_bin",
                      str(Path.home() / "builds/polyfem/build/PolyFEM_bin")):
            if Path(guess).exists():
                binary = guess
                break
    if not binary or not Path(binary).exists():
        raise SystemExit(
            "PolyFEM_bin not found. Build it from source (see "
            "simulations/README.md 'Edison Rec A' section) and either put it on "
            "$PATH or export POLYFEM_BIN=/path/to/PolyFEM_bin."
        )

    data_dir = Path(os.environ.get("POLYFEM_DATA_DIR")
                    or "/home/runner/builds/polyfem-data")
    cube = data_dir / "contact/meshes/3D/simple/cube.msh"
    plane = data_dir / "contact/meshes/3D/obstacles/plane.obj"
    if not cube.exists() or not plane.exists():
        raise SystemExit(
            f"cube.msh / plane.obj not found under {data_dir}. Clone "
            "https://github.com/polyfem/polyfem-data and export POLYFEM_DATA_DIR."
        )
    return Path(binary), cube, plane


def build_input_json(cube_msh: Path, plane_obj: Path,
                     cell_side_m: float = 0.024,
                     drop_height_m: float = 0.02,
                     E_pa: float = 12e6,
                     nu: float = 0.45,
                     rho: float = 1200.0,
                     dt: float = 1e-3,
                     n_steps: int = 120) -> dict:
    """Build the PolyFEM input JSON (gravity along -y, ground at y=0)."""
    return {
        "geometry": [
            {
                "mesh": str(cube_msh),
                "transformation": {
                    "translation": [0.0, drop_height_m + cell_side_m / 2.0, 0.0],
                    "scale": cell_side_m,
                },
                "volume_selection": 1,
            },
            {
                "mesh": str(plane_obj),
                "is_obstacle": True,
                "transformation": {
                    "translation": [0.0, 0.0, 0.0],
                    "dimensions": [1.0, 0.0, 1.0],
                },
            },
        ],
        "time": {"tend": dt * n_steps, "dt": dt,
                 "integrator": "ImplicitEuler"},
        "contact": {"enabled": True, "dhat": 1e-4},
        "boundary_conditions": {"rhs": [0.0, -9.81, 0.0]},
        "materials": [{
            "id": 1, "type": "NeoHookean",
            "E": E_pa, "nu": nu, "rho": rho,
        }],
        "solver": {
            "linear": {"solver": "Eigen::SimplicialLDLT"},
            "nonlinear": {"line_search": {"method": "Backtracking"}},
            "advanced": {"lump_mass_matrix": True},
        },
        "output": {
            "paraview": {
                "file_name": "drop.pvd",
                "options": {"velocity": True, "acceleration": True,
                            "scalar_values": False, "tensor_values": False,
                            "discretization_order": False, "nodes": False},
            },
            "advanced": {"save_time_sequence": True},
        },
    }


def _read_vtu_points_means(vtu_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read PolyFEM .vtu via meshio: return COM position + mean velocity."""
    import meshio
    m = meshio.read(str(vtu_path))
    pts = m.points
    vel = m.point_data.get("velocity")
    return pts.mean(axis=0), (vel.mean(axis=0) if vel is not None else np.zeros(3))


def _collect_timeseries(out_dir: Path, n_steps: int, dt: float) -> dict:
    """Walk step_*.vtm/.vtu files written by PolyFEM and build COM time-series."""
    com_y = []
    com_vy = []
    times = []
    for k in range(n_steps + 1):
        # PolyFEM writes a .vtm multiblock per step that points to .vtu(s).
        # The deformable body is the first vtu in the multiblock; read it directly.
        vtm = out_dir / f"step_{k}.vtm"
        if not vtm.exists():
            continue
        vtu = None
        for da in ET.parse(vtm).getroot().iter("DataSet"):
            f = da.attrib.get("file", "")
            if f.endswith(".vtu"):
                vtu = out_dir / f
                break
        if vtu is None or not vtu.exists():
            continue
        c, v = _read_vtu_points_means(vtu)
        com_y.append(float(c[1]))
        com_vy.append(float(v[1]))
        times.append(k * dt)
    com_y = np.asarray(com_y)
    com_vy = np.asarray(com_vy)
    times = np.asarray(times)
    com_ay = np.concatenate([[0.0], np.diff(com_vy) / dt]) if len(com_vy) > 1 else np.zeros_like(com_vy)
    return {"t": times, "com_y": com_y, "com_vy": com_vy, "com_ay": com_ay}


def run_drop(work_dir: Path | None = None, **kwargs) -> dict:
    binary, cube, plane = _resolve_paths()
    work_dir = Path(work_dir or "/tmp/polyfem_drop")
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    cfg = build_input_json(cube, plane, **kwargs)
    cfg_path = work_dir / "drop.json"
    cfg_path.write_text(json.dumps(cfg, indent=2))

    print(f"[polyfem] running {binary} on {cfg_path} -> {work_dir}")
    proc = subprocess.run(
        [str(binary), "-j", str(cfg_path), "-o", str(work_dir),
         "--log_level", "warning"],
        capture_output=True, text=True, timeout=900,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-2000:])
        sys.stderr.write(proc.stderr[-2000:])
        raise SystemExit(f"PolyFEM_bin returned {proc.returncode}")

    n_steps = int(cfg["time"]["tend"] / cfg["time"]["dt"])
    series = _collect_timeseries(work_dir, n_steps, cfg["time"]["dt"])
    return series


def main():
    res = run_drop()
    if res["t"].size == 0:
        raise SystemExit("PolyFEM produced no time-step output.")

    peak_g = float(np.max(np.abs(res["com_ay"])) / 9.81)
    settled_y = float(res["com_y"][-1])
    print(f"  steps recovered: {res['t'].size}")
    print(f"  peak |COM accel|: {peak_g:.1f} g")
    print(f"  settled COM y   : {settled_y * 1e3:.2f} mm")

    fig, axes = plt.subplots(3, 1, figsize=(7, 8), sharex=True)
    axes[0].plot(res["t"] * 1e3, res["com_y"] * 1e3)
    axes[0].set_ylabel("COM y (mm)")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(res["t"] * 1e3, res["com_vy"])
    axes[1].set_ylabel("COM vy (m/s)")
    axes[1].grid(True, alpha=0.3)
    axes[2].plot(res["t"] * 1e3, res["com_ay"] / 9.81)
    axes[2].set_ylabel("COM ay (g)")
    axes[2].set_xlabel("time (ms)")
    axes[2].grid(True, alpha=0.3)
    fig.suptitle(f"PolyFEM + IPC TPU-85A cube drop (peak {peak_g:.1f} g)")
    fig.tight_layout()
    out_png = OUTDIR / "polyfem_drop.png"
    fig.savefig(out_png, dpi=120)
    print(f"  wrote {out_png}")

    np.savez(OUTDIR / "polyfem_drop.npz",
             t=res["t"], com_y=res["com_y"],
             com_vy=res["com_vy"], com_ay=res["com_ay"])


if __name__ == "__main__":
    main()
