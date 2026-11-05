"""Draw a T3 prism as a filled 2D projection at true millimetre scale.

Geometry follows cad/t3-prism/t3-prism.scad (campaign branch):

    B_i = (R cos(90 + 120 i),          R sin(90 + 120 i),          0)
    T_i = (R cos(90 + 120 i + twist),  R sin(90 + 120 i + twist),  H)
    strut i: B_i -> T_i            bottom cable i: B_i -> B_{i+1}
    top cable i: T_i -> T_{i+1}    saddle cable i: B_{i+1} -> T_i

Members are drawn as polygons whose width is the member diameter in data
units (mm), so drawings on one set of axes share one scale. Struts are PLA
black, tendons TPU green, and each strut end carries a square housing of
side ``housing`` mm (the printed strut-end cage). Members are painted
back to front under an orthographic view at azimuth ``azim`` and
elevation ``elev`` (degrees).
"""
from __future__ import annotations

import math

from matplotlib.patches import Circle, Polygon, Rectangle

from campaign_data import PLA_BLACK, TPU_GREEN

HOUSING_MM = 10.2  # accelerometer-ready strut-end block: 6.2 mm pocket + 2 x 2 mm walls


def nodes(R, H, twist):
    bot = [(R * math.cos(math.radians(90 + 120 * i)),
            R * math.sin(math.radians(90 + 120 * i)), 0.0) for i in range(3)]
    top = [(R * math.cos(math.radians(90 + 120 * i + twist)),
            R * math.sin(math.radians(90 + 120 * i + twist)), H) for i in range(3)]
    return bot, top


def members(R, H, twist):
    bot, top = nodes(R, H, twist)
    out = []
    for i in range(3):
        j = (i + 1) % 3
        out.append(("strut", bot[i], top[i]))
        out.append(("cable", bot[i], bot[j]))
        out.append(("cable", top[i], top[j]))
        out.append(("cable", bot[j], top[i]))
    return out


def project(p, azim, elev):
    """Orthographic projection: returns (u, v, depth); larger depth is nearer."""
    a, e = math.radians(azim), math.radians(elev)
    x, y, z = p
    d = x * math.cos(a) + y * math.sin(a)
    u = -x * math.sin(a) + y * math.cos(a)
    v = z * math.cos(e) - d * math.sin(e)
    depth = d * math.cos(e) + z * math.sin(e)
    return u, v, depth


def _bar(ax, p, q, width, color, z):
    (u1, v1), (u2, v2) = p, q
    du, dv = u2 - u1, v2 - v1
    n = math.hypot(du, dv) or 1.0
    ou, ov = -dv / n * width / 2, du / n * width / 2
    ax.add_patch(Polygon([(u1 + ou, v1 + ov), (u2 + ou, v2 + ov),
                          (u2 - ou, v2 - ov), (u1 - ou, v1 - ov)],
                         closed=True, facecolor=color, edgecolor="none", zorder=z))
    for (u, v) in (p, q):
        ax.add_patch(Circle((u, v), width / 2, facecolor=color, edgecolor="none", zorder=z))


def draw_prism(ax, R, H, twist, d_s, d_t, *, x0=0.0, y0=0.0, azim=-20.0,
               elev=10.0, housing=HOUSING_MM, zbase=10):
    """Draw one prism with its bottom-centre projected to (x0, y0).

    Returns the projected bounding box (umin, umax, vmin, vmax) in mm,
    relative to (x0, y0), including member widths and housings.
    """
    items = []
    for kind, a, b in members(R, H, twist):
        pa, pb = project(a, azim, elev), project(b, azim, elev)
        depth = (pa[2] + pb[2]) / 2
        width = d_s if kind == "strut" else d_t
        color = PLA_BLACK if kind == "strut" else TPU_GREEN
        items.append((depth, kind, (pa[0], pa[1]), (pb[0], pb[1]), width, color))
    bot, top = nodes(R, H, twist)
    for p in bot + top:
        pp = project(p, azim, elev)
        items.append((pp[2] + 0.01, "housing", (pp[0], pp[1]), None, housing, PLA_BLACK))
    items.sort(key=lambda it: it[0])
    us, vs = [], []
    for k, (depth, kind, p, q, width, color) in enumerate(items):
        z = zbase + k * 0.01
        if kind == "housing":
            u, v = p
            ax.add_patch(Rectangle((x0 + u - width / 2, y0 + v - width / 2), width, width,
                                   facecolor=color, edgecolor="white", linewidth=0.3,
                                   zorder=z))
            us += [u - width / 2, u + width / 2]
            vs += [v - width / 2, v + width / 2]
        else:
            _bar(ax, (x0 + p[0], y0 + p[1]), (x0 + q[0], y0 + q[1]), width, color, z)
            us += [p[0] - width / 2, p[0] + width / 2, q[0] - width / 2, q[0] + width / 2]
            vs += [p[1] - width / 2, p[1] + width / 2, q[1] - width / 2, q[1] + width / 2]
    return min(us), max(us), min(vs), max(vs)
