"""Offscreen 3D animation of the regime drops (crutch tip + NASA lander).

Uses ``run_regimes.build_xml`` to construct the prism+payload MJCF for
each regime and renders it through ``render_utils.render_drop`` with
strain-coloured tendons.  Both regimes start with the prism + payload
moving at the regime impact velocity, so the GIFs capture only the
~10–40 ms ground-contact event — slow-motion impact + tendon stretch.

Outputs (under ``simulations/outputs/``):
  - ``regime_crutch_tip_drop.{gif,mp4}``
  - ``regime_nasa_lander_drop.{gif,mp4}``

Run with ``MUJOCO_GL=osmesa`` on headless runners.
"""
from __future__ import annotations

import os
import sys

import mujoco

sys.path.insert(0, os.path.dirname(__file__))
from regimes import CRUTCH, NASA_LANDER, Regime  # noqa: E402
from render_utils import render_drop  # noqa: E402
from run_regimes import build_xml  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def _initial_velocity_setup(r: Regime):
    """Reproduce ``run_regimes.simulate``'s initial-condition setup."""
    def setup(model: mujoco.MjModel, data: mujoco.MjData) -> None:
        for i in range(1, model.nbody):
            addr = model.body_dofadr[i]
            data.qvel[addr + 2] = -r.drop_velocity_mps
    return setup


def render_regime(r: Regime) -> None:
    xml = build_xml(r)
    # Camera tuned to each regime's spatial scale.
    cell_extent = max(r.radius_m, r.height_m)
    distance = 6.0 * cell_extent
    lookat_z = 0.6 * r.height_m
    render_drop(
        xml,
        out_stem=os.path.join(OUT_DIR, f"regime_{r.name}_drop"),
        duration_s=r.sim_duration_s,
        cam_lookat=(0.0, 0.0, lookat_z),
        cam_distance=distance,
        cam_elevation=-12.0,
        cam_azimuth=35.0,
        n_frames=80,
        playback_fps=20,           # ~4 s on-screen → strong slow-mo of impact
        tendon_width=max(0.0008, 0.06 * r.strut_radius_m),
        floor_size=max(0.5, 6.0 * cell_extent),
        title=f"{r.name}: payload {r.payload_mass_kg:g} kg @ "
              f"{r.drop_velocity_mps:g} m/s impact (slow-mo)",
        setup=_initial_velocity_setup(r),
    )


def main() -> None:
    for r in (CRUTCH, NASA_LANDER):
        render_regime(r)


if __name__ == "__main__":
    main()
