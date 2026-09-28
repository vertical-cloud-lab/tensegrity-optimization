"""Build the two search-space MP4 videos for the IDETC slide deck.

Video versions of gif-param-sequence.gif and gif-designs-tour.gif,
requested in PR #84 (me-madsen, 2026-08-20): "make the first two gifs
into videos", with the prism in the same place, size, and orientation at
the end of the first video and the start of the second so the presenter
can cut between them without the audience noticing.

How the seamless join is guaranteed rather than eyeballed:

- One camera covers both videos: the (u, v) bounding box is the union
  over every frame of *both* animations, and both use the same axes
  rectangle and margin, so the ground plane and the mm scale never move
  between files.
- The boundary frame is shared code, not matched styling: video 1 ends
  on, and video 2 opens on, a frame rendered by the same function with
  the same parameters (every dial at its upper bound, tour-style panel,
  no sweep annotation). The script asserts the two renders are
  pixel-identical before encoding.

Motion frames land on the 30 fps output grid (one render per tick), so
the videos are smoother than the 70 ms-per-frame GIFs while keeping the
same pacing. Encoded H.264 / yuv420p / faststart so PowerPoint plays
them without re-encoding.

Outputs:
- presentation/media/video-param-sequence.mp4 (1920x1080)
- presentation/media/video-designs-tour.mp4   (1920x1080)
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import build_designs_tour_gif as tour
import build_search_space_sequence_gif as seq
from build_search_space_figure import (
    BOUNDS,
    draw_structure,
    nodes,
    project,
    setup_axes,
)
from build_search_space_gifs import annotate_sweep

HERE = Path(__file__).resolve().parent
OUT_SEQ = HERE / "media" / "video-param-sequence.mp4"
OUT_TOUR = HERE / "media" / "video-designs-tour.mp4"

FIG_W_IN, FIG_H_IN, DPI = 8.0, 4.5, 240  # 1920 x 1080 px
FPS = 30
TICK_MS = 1000.0 / FPS

# One render per output tick: double the GIFs' step counts and put each
# motion frame on the 30 fps grid, so pacing matches the approved GIFs
# (sequence 22 x 70 ms ~ 1.5 s per dial, tour 18 x 70 ms ~ 1.3 s per
# design) while the motion is twice as smooth.
seq.STEPS, seq.STEP_MS = 44, TICK_MS
tour.STEPS, tour.STEP_MS = 38, TICK_MS

BOUNDARY_HOLD_MS = 1200  # static all-max hold on each side of the cut
ALL_MAX = {k: hi for k, (lo, hi) in BOUNDS.items()}


def union_bbox(param_sets):
    us, vs = [], []
    for params in param_sets:
        bot, top = nodes(params)
        for pt in bot + top:
            u, v, _ = project(pt)
            us.append(u)
            vs.append(v)
    return min(us), max(us), min(vs), max(vs)


def render(params, bbox, stage=None):
    """One 1920x1080 frame. stage=None renders the tour/boundary style
    (all dials live, no sweep annotation); an integer renders the
    sequence style for that active dial."""
    u0, u1, v0, v1 = bbox
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.02, 0.05, 0.62, 0.91])
    center = ((u0 + u1) / 2, (v0 + v1) / 2)
    # Margin for the H dimension line and twist arc outside the
    # structure (used by the sequence video; the tour shares it so the
    # prism does not move at the cut).
    ppmm = setup_axes(ax, fig, center, (u1 - u0) + 95, (v1 - v0) + 40)
    draw_structure(ax, params, ppmm)
    if stage is None:
        tour.draw_dial_panel(fig, params)
    else:
        annotate_sweep(ax, seq.STAGES[stage][0], params)
        seq.draw_dial_panel(fig, stage, params)
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3])
    plt.close(fig)
    return img


def encode(frames, out_path):
    """frames: list of (PIL image, hold_ms). Encode via ffmpeg concat."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        lines = ["ffconcat version 1.0"]
        for i, (img, hold_ms) in enumerate(frames):
            p = tdp / f"f{i:05d}.png"
            img.save(p)
            lines.append(f"file '{p}'")
            lines.append(f"duration {hold_ms / 1000.0:.6f}")
        # Concat demuxer ignores the last entry's duration unless the
        # final file is listed once more.
        lines.append(f"file '{tdp / f'f{len(frames) - 1:05d}.png'}'")
        (tdp / "list.txt").write_text("\n".join(lines) + "\n")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
             "-safe", "0", "-i", str(tdp / "list.txt"),
             "-vf", f"fps={FPS},format=yuv420p",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium",
             "-movflags", "+faststart", str(out_path)],
            check=True)
    print(f"wrote {out_path} ({out_path.stat().st_size / 1e6:.2f} MB, "
          f"{len(frames)} source frames)")


def main():
    seq_frames = seq.frame_sequence()          # (stage, params, hold_ms)
    tour_frames = tour.frame_sequence()        # (params, hold_ms)
    bbox = union_bbox([p for _, p, _ in seq_frames]
                      + [p for p, _ in tour_frames])

    # Video 1: the five dials turned up one by one, then settle on the
    # shared boundary frame (all-max, all dials live, no annotation).
    v1 = []
    for i, (stage, params, hold) in enumerate(seq_frames):
        if i == len(seq_frames) - 1:
            hold = seq.STAGE_HOLD_MS  # settle replaces the long end hold
        v1.append((render(params, bbox, stage=stage), hold))
    boundary_v1 = render(ALL_MAX, bbox)
    v1.append((boundary_v1, BOUNDARY_HOLD_MS))

    # Video 2: opens on the same boundary frame, then tours the seeds.
    v2 = []
    for i, (params, hold) in enumerate(tour_frames):
        if i == 0:
            hold = BOUNDARY_HOLD_MS
        v2.append((render(params, bbox), hold))

    # The join must be pixel-identical, not merely close.
    if not np.array_equal(np.asarray(boundary_v1), np.asarray(v2[0][0])):
        raise SystemExit("boundary frames differ; videos would pop")
    print("boundary check: last frame of video 1 == first frame of "
          "video 2 (pixel-exact)")

    encode(v1, OUT_SEQ)
    encode(v2, OUT_TOUR)


if __name__ == "__main__":
    main()
