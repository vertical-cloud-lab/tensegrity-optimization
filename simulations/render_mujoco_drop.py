"""Offscreen 3D animation of the MuJoCo prism drop (Edison Rec C tier).

Re-uses the model from ``mujoco_drop.py`` and renders the drop with the
shared ``render_utils.render_drop`` helper; tendons are recoloured every
frame by their tensile strain (red = high, blue = slack) so the
animation visualises both the rigid-body deformation on impact and the
cable-stress gradient in time.

Outputs (under ``simulations/outputs/``):
  - ``mujoco_drop.gif``  (looping animation, easy to embed in PR replies)
  - ``mujoco_drop.mp4``  (higher-quality video for the README)

Run with ``MUJOCO_GL=osmesa`` on headless runners.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from mujoco_drop import build_mjcf  # noqa: E402
from render_utils import render_drop  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def main() -> None:
    render_drop(
        build_mjcf(),
        out_stem=os.path.join(OUT_DIR, "mujoco_drop"),
        duration_s=1.5,
        cam_lookat=(0.0, 0.0, 0.5),
        cam_distance=1.6,
        title="MuJoCo: 3-bar Snelson prism, 1 m drop (cables coloured by strain)",
    )


if __name__ == "__main__":
    main()
