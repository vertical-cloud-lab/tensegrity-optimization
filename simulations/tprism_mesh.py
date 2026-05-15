"""Build a volumetric tet mesh of a 3-bar Snelson T-prism for PolyFEM + IPC.

The prism consists of three PLA strut cylinders (Ø ``strut_d``) and nine TPU
85A tendon cylinders (Ø ``tendon_d``) following the canonical connectivity
from :mod:`tprism_geometry`.

To get the tendons *welded* to the struts (so a downstream PolyFEM run sees
one continuous deformable body with two material regions instead of nine
floating tendon segments), each tendon is shortened by ``strut_d *
tendon_inset_factor`` at each end so its cylinder side wall fuses with the
strut side wall instead of trying to coincide with the strut endcap (which
hits a tetgen PLC error).  ``gmsh.model.occ.fragment`` then splits the
overlap into shared-face sub-volumes; the original input volumes' fragment
maps tell us which sub-volumes came from struts (-> physical group 1, PLA)
versus tendons (-> physical group 2, TPU 85A).

The output is a Gmsh 4.1 ``.msh`` file with two physical-volume groups
(``PLA_strut`` = 1, ``TPU_tendon`` = 2) consumable by PolyFEM via the
``volume_selection`` field on the geometry block.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from tprism_geometry import CABLES, STRUTS, tprism_nodes


def build_tprism_msh(out_msh: str | Path,
                     radius: float = 0.012,
                     height: float = 0.025,
                     strut_d: float = 0.003,
                     tendon_d: float = 0.0015,
                     drop_height: float = 0.005,
                     lc_strut: float = 0.0015,
                     lc_tendon: float = 0.001,
                     tendon_inset_factor: float = 0.6,
                     verbose: bool = False) -> dict:
    """Generate the prism mesh and return ``{'msh': out_msh, 'tets': N, ...}``.

    Parameters mirror :func:`tprism_geometry.tprism_nodes` plus the strut /
    tendon cross-section diameters in metres.  ``drop_height`` sets the
    bottom of the prism above the ground plane (gmsh +y is up); the prism is
    centred on the y axis.
    """
    import gmsh  # local import: gmsh requires libGLU and is a heavy dep

    # Note: tprism_nodes uses +z as up; PolyFEM/our JSON also uses +y as up.
    # We rotate (x, y, z) -> (x, z, y) so the prism height is along +y.
    raw = tprism_nodes(radius=radius, height=height, z0=drop_height + height / 2.0)
    nodes = raw[:, [0, 2, 1]]
    inset = strut_d * tendon_inset_factor

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1 if verbose else 0)
    gmsh.model.add("tprism")

    def add_cyl(p1: np.ndarray, p2: np.ndarray, rad: float) -> int:
        v = p2 - p1
        return gmsh.model.occ.addCylinder(
            float(p1[0]), float(p1[1]), float(p1[2]),
            float(v[0]), float(v[1]), float(v[2]), rad)

    strut_tags = [add_cyl(nodes[a], nodes[b], strut_d / 2.0) for a, b in STRUTS]
    tendon_tags: list[int] = []
    for a, b in CABLES:
        p1, p2 = nodes[a], nodes[b]
        u = (p2 - p1) / np.linalg.norm(p2 - p1)
        tendon_tags.append(add_cyl(p1 + u * inset, p2 - u * inset, tendon_d / 2.0))

    gmsh.model.occ.synchronize()

    all_vols = [(3, t) for t in strut_tags + tendon_tags]
    _, out_map = gmsh.model.occ.fragment(all_vols, [])
    gmsh.model.occ.synchronize()

    n_struts = len(strut_tags)
    pla, tpu = [], []
    for i, frags in enumerate(out_map):
        for dim, tag in frags:
            if dim != 3:
                continue
            (pla if i < n_struts else tpu).append(tag)
    pla = sorted(set(pla))
    tpu = sorted(t for t in set(tpu) if t not in set(pla))

    gmsh.model.addPhysicalGroup(3, pla, tag=1, name="PLA_strut")
    gmsh.model.addPhysicalGroup(3, tpu,  tag=2, name="TPU_tendon")

    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 4)
    gmsh.option.setNumber("Mesh.MeshSizeMin", lc_tendon)
    gmsh.option.setNumber("Mesh.MeshSizeMax", lc_strut)
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # Delaunay
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 4.1)
    gmsh.write(str(out_msh))

    elem_types, elem_tags, _ = gmsh.model.mesh.getElements(3)
    nelem = sum(len(t) for t in elem_tags)
    nodes_arr, _, _ = gmsh.model.mesh.getNodes()
    n_nodes = len(nodes_arr)
    gmsh.finalize()

    return {
        "msh": str(out_msh),
        "pla_volumes": len(pla),
        "tpu_volumes": len(tpu),
        "tets": nelem,
        "nodes": n_nodes,
        "y_min": float(nodes[:, 1].min()) - strut_d / 2.0,
        "y_max": float(nodes[:, 1].max()) + strut_d / 2.0,
    }


if __name__ == "__main__":
    info = build_tprism_msh("/tmp/tprism.msh", verbose=True)
    print(info)
