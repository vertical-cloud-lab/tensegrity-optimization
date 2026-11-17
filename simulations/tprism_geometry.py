"""Geometry of a classical 3-bar tensegrity T-prism (Snelson prism).

Returns six node positions and the canonical connectivity of three rigid
struts plus nine cables (3 top, 3 bottom, 3 vertical / saddle).

The prism is parameterised by:
    radius r:    radius of the circumscribing cylinder
    height h:    axial distance between top and bottom triangles
    twist phi:   relative twist (rad) between top and bottom triangles.
                 The equilibrium twist for a regular T-3 prism is 5*pi/6
                 (i.e. 150 deg) per Skelton & de Oliveira (2009).

References
----------
- Skelton, R. E., & de Oliveira, M. C. (2009). Tensegrity systems. Springer.
- Snelson, K. (1965). Continuous Tension, Discontinuous Compression Structures.
"""
from __future__ import annotations

import numpy as np

EQUILIBRIUM_TWIST = 5.0 * np.pi / 6.0  # 150 deg


def tprism_nodes(radius: float = 0.10, height: float = 0.20,
                 twist: float = EQUILIBRIUM_TWIST,
                 z0: float = 0.0) -> np.ndarray:
    """Return (6, 3) array of node positions (3 bottom then 3 top)."""
    bot_angles = np.array([0.0, 2 * np.pi / 3, 4 * np.pi / 3])
    top_angles = bot_angles + twist
    bot = np.stack([radius * np.cos(bot_angles),
                    radius * np.sin(bot_angles),
                    np.full(3, z0)], axis=1)
    top = np.stack([radius * np.cos(top_angles),
                    radius * np.sin(top_angles),
                    np.full(3, z0 + height)], axis=1)
    return np.vstack([bot, top])


# Node indices: 0,1,2 bottom triangle ; 3,4,5 top triangle.
STRUTS = [(0, 4), (1, 5), (2, 3)]            # 3 rigid bars
BOTTOM_CABLES = [(0, 1), (1, 2), (2, 0)]      # base triangle
TOP_CABLES = [(3, 4), (4, 5), (5, 3)]         # top triangle
VERT_CABLES = [(0, 3), (1, 4), (2, 5)]        # saddle (vertical) cables
CABLES = BOTTOM_CABLES + TOP_CABLES + VERT_CABLES


def edge_length(nodes: np.ndarray, edge: tuple[int, int]) -> float:
    a, b = edge
    return float(np.linalg.norm(nodes[a] - nodes[b]))


if __name__ == "__main__":
    n = tprism_nodes()
    print(f"Nodes:\n{n}")
    print(f"Strut length:  {edge_length(n, STRUTS[0]):.4f} m")
    print(f"Bottom cable:  {edge_length(n, BOTTOM_CABLES[0]):.4f} m")
    print(f"Top cable:     {edge_length(n, TOP_CABLES[0]):.4f} m")
    print(f"Vertical cable:{edge_length(n, VERT_CABLES[0]):.4f} m")
