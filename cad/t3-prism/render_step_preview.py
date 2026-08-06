"""Headless PNG preview of the STEP output, for PR/issue comments.

There is no OpenGL on a CI runner, so this tessellates the B-rep with OCCT and
draws the triangles with matplotlib rather than using a real viewer. The mesh
is for *display only* -- the STEP itself stays analytic.

    python3 cad/t3-prism/render_step_preview.py \
        --struts cad/t3-prism/step/t3-prism-struts.step \
        --cables cad/t3-prism/step/t3-prism-cables.step \
        --out cad/t3-prism/t3-prism-step-preview.png
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from OCP.BRep import BRep_Tool  # noqa: E402
from OCP.BRepMesh import BRepMesh_IncrementalMesh  # noqa: E402
from OCP.TopAbs import TopAbs_FACE  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopLoc import TopLoc_Location  # noqa: E402
from OCP.TopoDS import TopoDS  # noqa: E402
from build123d import import_step  # noqa: E402


def triangles(path: pathlib.Path, deflection: float = 0.15) -> np.ndarray:
    shape = import_step(str(path)).wrapped
    BRepMesh_IncrementalMesh(shape, deflection, False, 0.5, True)
    tris: list[list[tuple[float, float, float]]] = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            nodes = [tri.Node(i).Transformed(trsf)
                     for i in range(1, tri.NbNodes() + 1)]
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                tris.append([(nodes[a - 1].X(), nodes[a - 1].Y(), nodes[a - 1].Z()),
                             (nodes[b - 1].X(), nodes[b - 1].Y(), nodes[b - 1].Z()),
                             (nodes[c - 1].X(), nodes[c - 1].Y(), nodes[c - 1].Z())])
        exp.Next()
    return np.array(tris)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    here = pathlib.Path(__file__).resolve().parent
    ap.add_argument("--struts", default=str(here / "step/t3-prism-struts.step"))
    ap.add_argument("--cables", default=str(here / "step/t3-prism-cables.step"))
    ap.add_argument("--out", default=str(here / "t3-prism-step-preview.png"))
    ap.add_argument("--title", default="T3-prism, B-rep STEP from build123d "
                                       "(147 analytic faces, not 65,170 triangles)",
                    help="figure title; override when previewing something "
                         "other than the committed default geometry")
    args = ap.parse_args(argv)

    parts = [("PLA struts / joints / housings", args.struts, "#4C6EF5"),
             ("TPU cables + captive cores", args.cables, "#F08C00")]
    meshes = [(label, triangles(pathlib.Path(p)), color)
              for label, p, color in parts]

    allpts = np.vstack([m.reshape(-1, 3) for _, m, _ in meshes])
    lo, hi = allpts.min(0), allpts.max(0)
    mid, span = (lo + hi) / 2, (hi - lo).max() / 2

    # Flat shading: matplotlib's 3D axes do no lighting, so brightness is
    # applied per triangle from the angle between its normal and a fixed key
    # light. Without this the model reads as a flat silhouette.
    light = np.array([0.4, -0.8, 0.45])
    light = light / np.linalg.norm(light)

    def shade(tris: np.ndarray, base: str) -> np.ndarray:
        n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
        norm = np.linalg.norm(n, axis=1, keepdims=True)
        n = n / np.where(norm == 0, 1, norm)
        lam = 0.35 + 0.65 * np.abs(n @ light)
        rgb = np.array(matplotlib.colors.to_rgb(base))
        return np.clip(lam[:, None] * rgb, 0, 1)

    fig = plt.figure(figsize=(11, 5.5))
    for k, (elev, azim, title) in enumerate(
            [(18, -60, "isometric"), (0, -90, "front elevation")]):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        for label, tris, color in meshes:
            coll = Poly3DCollection(tris, alpha=1.0, edgecolor="none",
                                    facecolors=shade(tris, color), label=label)
            coll.set_zsort("average")
            ax.add_collection3d(coll)
        ax.set_xlim(mid[0] - span, mid[0] + span)
        ax.set_ylim(mid[1] - span, mid[1] + span)
        ax.set_zlim(mid[2] - span, mid[2] + span)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, fontsize=10)
        ax.set_axis_off()
        ax.dist = 7.5 if hasattr(ax, "dist") else None

    handles = [plt.Line2D([0], [0], marker="s", linestyle="", markersize=9,
                          color=c, label=l) for l, _, c in meshes]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False)
    fig.suptitle(args.title, fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(args.out, dpi=140)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
