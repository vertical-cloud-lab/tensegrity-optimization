"""Helpers for offscreen 3D rendering of MuJoCo tensegrity drops.

Used by ``render_mujoco_drop.py`` and ``render_regimes.py``; centralises
the lighting/sky/material patches we apply to the lightweight MJCF
strings that the simulation scripts produce, plus the strain-coloured
rendering loop itself.

Run with ``MUJOCO_GL=osmesa`` on headless runners.
"""
from __future__ import annotations

import os
import textwrap
from typing import Callable

import imageio.v2 as imageio
import mujoco
import numpy as np


def strain_to_rgba(strain: np.ndarray, max_strain: float) -> np.ndarray:
    """Map normalised tensile strain to an RGBA (red = high) colour."""
    s = np.clip(strain / max(max_strain, 1e-9), 0.0, 1.0)
    rgba = np.zeros((strain.size, 4))
    rgba[:, 0] = 0.2 + 0.8 * s
    rgba[:, 1] = 0.2 * (1.0 - s)
    rgba[:, 2] = 0.9 * (1.0 - s)
    rgba[:, 3] = 1.0
    return rgba


_VISUAL_PATCH = textwrap.dedent('''
    <visual>
      <global offwidth="800" offheight="600"/>
      <headlight diffuse="0.9 0.9 0.9" ambient="0.4 0.4 0.4"
                 specular="0.2 0.2 0.2"/>
      <rgba haze="0.15 0.25 0.35 1"/>
    </visual>
    <asset>
      <texture name="grid" type="2d" builtin="checker"
               rgb1="0.55 0.55 0.6" rgb2="0.7 0.7 0.75"
               width="300" height="300"/>
      <material name="grid" texture="grid" texrepeat="6 6"
                reflectance="0.05"/>
      <texture name="sky" type="skybox" builtin="gradient"
               rgb1="0.55 0.7 0.9" rgb2="0.85 0.9 1.0"
               width="256" height="256"/>
    </asset>
    ''').strip()


def patch_xml(xml: str, *, floor_size: float = 2.0) -> str:
    """Inject lights / sky / checker floor for a publication-quality render."""
    if '<visual>' in xml:
        # Replace the simulation-script <visual> block with our richer one.
        out = xml
        for snippet in (
            '<visual><global offwidth="800" offheight="600"/></visual>',
            '<visual>\n      <global offwidth="800" offheight="600"/>\n    </visual>',
        ):
            out = out.replace(snippet, _VISUAL_PATCH)
        if out == xml:
            # Generic fallback: insert before <worldbody>.
            out = xml.replace('<worldbody>', _VISUAL_PATCH + '\n  <worldbody>')
    else:
        out = xml.replace('<worldbody>', _VISUAL_PATCH + '\n  <worldbody>')
    # Swap any plain-rgba floor for the checker material + add lights.
    import re

    out = re.sub(
        r'<geom name="floor"[^/]*/>',
        f'<geom name="floor" type="plane" '
        f'size="{floor_size:.2f} {floor_size:.2f} 0.1" material="grid"/>'
        '<light name="top" pos="0 0 2" dir="0 0 -1" diffuse="0.7 0.7 0.7"/>'
        '<light name="side" pos="1.5 1.0 1.2" dir="-0.7 -0.5 -0.7"'
        ' diffuse="0.5 0.5 0.5"/>',
        out,
        count=1,
    )
    return out


def render_drop(
    xml: str,
    *,
    out_stem: str,
    duration_s: float,
    cam_lookat=(0.0, 0.0, 0.5),
    cam_distance: float = 1.6,
    cam_elevation: float = -10.0,
    cam_azimuth: float = 35.0,
    width: int = 640,
    height: int = 480,
    target_fps: int = 60,
    n_frames: int | None = None,
    playback_fps: int | None = None,
    tendon_width: float = 0.004,
    floor_size: float = 2.0,
    title: str | None = None,
    setup: Callable[[mujoco.MjModel, mujoco.MjData], None] | None = None,
) -> str:
    """Run + render the prism drop described by ``xml``.

    For short sims (e.g. 25 ms regime drops) pass ``n_frames`` to fix the
    number of captured frames + ``playback_fps`` to control the on-screen
    speed (slow motion).  ``setup`` is called once after the model is
    built (e.g. to set initial velocities).  Returns the path to the GIF.
    """
    os.environ.setdefault("MUJOCO_GL", "osmesa")
    out_dir = os.path.dirname(out_stem)
    os.makedirs(out_dir, exist_ok=True)

    xml = patch_xml(xml, floor_size=floor_size)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    if model.tendon_width.size:
        model.tendon_width[:] = tendon_width
    if setup is not None:
        setup(model, data)

    renderer = mujoco.Renderer(model, height=height, width=width)
    cam = mujoco.MjvCamera()
    cam.lookat[:] = list(cam_lookat)
    cam.distance = cam_distance
    cam.elevation = cam_elevation
    cam.azimuth = cam_azimuth

    masses = np.array([model.body_mass[i] for i in range(1, model.nbody)])
    total_mass = max(masses.sum(), 1e-9)
    L0 = model.tendon_lengthspring[:, 1].copy() if model.ntendon else None

    # Pre-pass to find max strain so the colour scale is consistent.
    pre_data = mujoco.MjData(model)
    if setup is not None:
        setup(model, pre_data)
    max_strain = 0.0
    nsteps = int(duration_s / model.opt.timestep)
    if model.ntendon:
        for _ in range(nsteps):
            mujoco.mj_step(model, pre_data)
            strain = np.maximum(pre_data.ten_length - L0, 0.0)
            max_strain = max(max_strain, float(strain.max()))
            if not np.isfinite(pre_data.qpos).all():
                break
    max_strain = max(max_strain, 1e-4)

    frame_interval = max(1, int(round(1.0 / target_fps / model.opt.timestep)))
    if n_frames is not None:
        # Slow-motion mode: aim for exactly n_frames over the sim duration.
        frame_interval = max(1, int(round(nsteps / n_frames)))
    frames: list[np.ndarray] = []

    mujoco.mj_resetData(model, data)
    if setup is not None:
        setup(model, data)
    step = 0
    while data.time < duration_s:
        mujoco.mj_step(model, data)
        step += 1
        if step % frame_interval:
            continue
        if not np.isfinite(data.qpos).all():
            break
        if model.ntendon:
            strain = np.maximum(data.ten_length - L0, 0.0)
            model.tendon_rgba[:] = strain_to_rgba(strain, max_strain)
        zs = np.array([data.xpos[i, 2] for i in range(1, model.nbody)])
        com_z = float(np.dot(masses, zs) / total_mass)
        cam.lookat[2] = 0.7 * cam.lookat[2] + 0.3 * com_z
        renderer.update_scene(data, camera=cam)
        frame = renderer.render()
        frames.append(frame.copy())

    if title:
        try:
            from PIL import Image, ImageDraw

            for i, f in enumerate(frames):
                img = Image.fromarray(f)
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), title, fill=(255, 255, 255))
                draw.text((10, 26),
                          f"t = {i * frame_interval * model.opt.timestep * 1e3:6.1f} ms",
                          fill=(255, 255, 255))
                frames[i] = np.array(img)
        except Exception:
            pass

    gif_path = f"{out_stem}.gif"
    mp4_path = f"{out_stem}.mp4"
    fps_out = playback_fps if playback_fps is not None else target_fps
    # Quantise each frame to a 128-colour palette so the GIF stays small
    # enough to embed inline in PR replies (uncompressed RGB GIFs blow
    # past 5 MB at 640×480).
    try:
        from PIL import Image

        gif_frames = [
            np.array(Image.fromarray(f).convert("P", palette=Image.ADAPTIVE,
                                                colors=128).convert("RGB"))
            for f in frames
        ]
    except Exception:
        gif_frames = frames
    imageio.mimsave(gif_path, gif_frames, duration=1.0 / fps_out, loop=0)
    try:
        imageio.mimsave(mp4_path, frames, fps=fps_out,
                        codec="libx264", quality=8)
    except Exception as exc:  # pragma: no cover - ffmpeg may be missing
        print(f"  (mp4 skipped for {out_stem}: {exc})")
    print(f"wrote {gif_path} ({len(frames)} frames, "
          f"max strain {max_strain * 1e3:.2f} mm)")
    return gif_path
