"""Find the Tier-C Pareto front over the PR #35 T3-prism box and render it.

Per @sgbaird (PR comment 4760877672):

    > each simulation is so cheap that I'm not sure it's even worth doing a
    > cost-aware, multi-fidelity approach.  Nevertheless, go ahead and run
    > whatever you'd like in a full scenario.  Do your best to find the actual
    > Pareto front within the problem space you've been given.  I want to see
    > renders of these Pareto-front best ones as well as some renders of the
    > worst performing ones and a few mediocre ones.  Maybe call outs with
    > images to an actual Pareto front graph.

Since a Tier-C MuJoCo regime evaluation is ~0.15 s, we skip the
cost-aware / multi-fidelity machinery entirely and instead **densely map the
true Pareto front** with a large Sobol set (default 2048 designs per regime)
scored on the three objectives:

    F_peak_N      (minimize) — peak transmitted force
    SEA_J_per_g   (maximize) — specific energy absorbed (elastic proxy)
    eta           (maximize) — compaction / plateau efficiency

then take the 3-objective non-dominated set as the empirical Pareto front.

For each regime we then pick a handful of **representative designs** — the
Pareto-front winners (max-SEA, max-eta, balanced knee, min-F_peak), a couple of
**worst** dominated designs, and a couple of **mediocre** mid-rank designs — and
render each as a 3-D MuJoCo still (geometry + strain-coloured tendons).  The
stills are then dropped onto the Pareto scatter as **callout thumbnails** with
leader lines to their marker, so the trade-off surface and what the cells
actually look like are in one figure.  The headline best + worst also get full
drop GIF/MP4 animations.

Honest caveat (carried over from ``sobol_t3_analysis.md`` + Edison ``ff8faab3`` /
``491f90ae``): at Tier-C ``F_peak`` is a near-invariant support-load proxy, so
the live trade-off the Pareto front exposes is **SEA vs eta**; ``F_peak`` is
shown as the marker colour and kept as the third (near-degenerate) objective.

Outputs (under ``simulations/outputs/``):
  - ``pareto_<regime>.csv``                 every evaluated design + objectives + pareto flag
  - ``pareto_<regime>_annotated.png``       Pareto scatter with render callouts
  - ``pareto_<regime>_render_<tag>.png``    per-pick 3-D stills
  - ``pareto_<regime>_<best|worst>_drop.{gif,mp4}``  headline animations
  - ``pareto_summary.md``                   table of the picks + their objectives

Run with ``MUJOCO_GL=osmesa`` on headless runners::

    MUJOCO_GL=osmesa python simulations/pareto_render_campaign.py --n 2048
"""
from __future__ import annotations

import argparse
import os
import sys
import warnings
from dataclasses import replace

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from bo_evaluator import evaluate_design, parameterization_to_design  # noqa: E402
from regimes import CRUTCH, NASA_LANDER, Regime  # noqa: E402
from render_regimes import build_render_xml  # noqa: E402
from render_utils import patch_xml, render_drop, strain_to_rgba  # noqa: E402
from sobol_t3_campaign import PARAM_BOUNDS, PARAM_NAMES, sobol_designs  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
REGIMES = {"crutch": CRUTCH, "lander": NASA_LANDER}

OBJECTIVES = ["F_peak_N", "SEA_J_per_g", "eta"]
# True => maximize that objective.
MAXIMIZE = {"F_peak_N": False, "SEA_J_per_g": True, "eta": True}


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------
def evaluate_box(designs: list[dict], regime: Regime) -> list[dict]:
    """Score every design at Tier-C; tag geometric feasibility."""
    rows: list[dict] = []
    for i, d in enumerate(designs):
        design = parameterization_to_design(d)
        feasible = not design.check()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            obj = evaluate_design(d, regime=regime, fidelity="C")
        row = {k: float(d[k]) for k in PARAM_NAMES}
        row.update(obj)
        row["feasible"] = feasible
        rows.append(row)
        if (i + 1) % 256 == 0:
            print(f"  [{regime.name}] {i + 1}/{len(designs)} evaluated")
    return rows


# --------------------------------------------------------------------------
# Pareto helpers
# --------------------------------------------------------------------------
def _objective_matrix(rows: list[dict]) -> np.ndarray:
    """Stack objectives as a *maximization* matrix (flip the minimized ones)."""
    cols = []
    for k in OBJECTIVES:
        v = np.array([r[k] for r in rows], dtype=float)
        cols.append(v if MAXIMIZE[k] else -v)
    return np.column_stack(cols)


def pareto_mask(rows: list[dict]) -> np.ndarray:
    """Boolean non-dominated mask (3-objective, maximization after flip)."""
    M = _objective_matrix(rows)
    n = M.shape[0]
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        if not keep[i]:
            continue
        # j dominates i if j is >= on all objectives and > on at least one.
        ge_all = np.all(M >= M[i] - 1e-12, axis=1)
        gt_any = np.any(M > M[i] + 1e-12, axis=1)
        dominators = ge_all & gt_any
        dominators[i] = False
        if np.any(dominators):
            keep[i] = False
    return keep


def _normalized_scores(rows: list[dict]) -> np.ndarray:
    """Per-objective min-max normalized 'higher is better' score in [0, 1]."""
    M = _objective_matrix(rows)  # already maximization-oriented
    lo = M.min(axis=0)
    hi = M.max(axis=0)
    span = np.where(hi - lo > 1e-12, hi - lo, 1.0)
    return (M - lo) / span


# --------------------------------------------------------------------------
# Representative selection
# --------------------------------------------------------------------------
def select_representatives(rows: list[dict]) -> list[dict]:
    """Pick Pareto winners + worst + mediocre designs to render.

    Returns a list of dicts with an added ``tag``/``label``/``group`` so the
    figure and summary can label each callout.  Only geometrically feasible
    designs are eligible (an unprintable cell is not a meaningful 'best').
    """
    feas_idx = [i for i, r in enumerate(rows) if r["feasible"]]
    feas = [rows[i] for i in feas_idx]
    if not feas:
        raise RuntimeError("no feasible designs to render")

    pmask = pareto_mask(feas)
    pareto = [feas[i] for i in np.where(pmask)[0]]
    norm = _normalized_scores(feas)             # aligned with feas
    scalar = norm.mean(axis=1)                  # equal-weight desirability

    picks: list[dict] = []
    seen: set[tuple] = set()

    def _key(r: dict) -> tuple:
        return tuple(round(r[k], 4) for k in PARAM_NAMES)

    def _add(r: dict, tag: str, label: str, group: str) -> None:
        k = _key(r)
        if k in seen:
            return
        seen.add(k)
        picks.append({**r, "tag": tag, "label": label, "group": group})

    # --- Pareto-front winners -------------------------------------------
    def _best_on(metric: str, maximize: bool) -> dict:
        vals = np.array([r[metric] for r in pareto], dtype=float)
        idx = int(np.argmax(vals) if maximize else np.argmin(vals))
        return pareto[idx]

    _add(_best_on("SEA_J_per_g", True), "best_sea", "max SEA", "Pareto")
    _add(_best_on("eta", True), "best_eta", "max eta", "Pareto")
    _add(_best_on("F_peak_N", False), "best_fpeak", "min F_peak", "Pareto")

    # Balanced knee: Pareto point closest to the ideal corner in the
    # normalized SEA/eta plane (F_peak is near-degenerate at Tier-C).
    pareto_keys = {_key(r) for r in pareto}
    pidx = [i for i, r in enumerate(feas) if _key(r) in pareto_keys]
    if pidx:
        sea_eta = norm[pidx][:, [1, 2]]         # SEA, eta normalized
        dist = np.linalg.norm(1.0 - sea_eta, axis=1)
        knee = feas[pidx[int(np.argmin(dist))]]
        _add(knee, "knee", "balanced knee", "Pareto")

    # --- Worst feasible designs (lowest equal-weight desirability) -------
    order = np.argsort(scalar)
    for rank, i in enumerate(order[:4]):
        if len([p for p in picks if p["group"] == "worst"]) >= 2:
            break
        _add(feas[i], f"worst{rank}", "worst", "worst")

    # --- Mediocre designs (mid desirability) ----------------------------
    mid = len(order) // 2
    for off in (0, 1, -1, 2, -2, 3):
        if len([p for p in picks if p["group"] == "mediocre"]) >= 2:
            break
        i = order[mid + off]
        _add(feas[i], f"mid{off}", "mediocre", "mediocre")

    return picks


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def _overridden_regime(params: dict, regime: Regime) -> Regime:
    """Build a Regime whose geometry/stiffness match the BO design."""
    design = parameterization_to_design(params)
    return replace(
        regime,
        radius_m=design.radius_m,
        height_m=design.height_m,
        strut_radius_m=design.strut_diameter_m * 0.5,
        cable_stiffness_Npm=float(design.cable_stiffness_Npm),
        cable_pretension_frac=float(design.prestrain),
    )


def render_still(params: dict, regime: Regime, out_path: str,
                 *, title: str | None = None, settle_ms: float = 4.0) -> str:
    """Render a single 3-D still of the design's prism (geometry + tendons).

    The cell is dropped a couple of millimetres onto the floor and stepped a
    few ms so the tendons take up their prestrain and colour by strain, giving
    a clean, comparable thumbnail that makes the geometry differences (height,
    strut thickness, radius, twist) legible.
    """
    import mujoco

    os.environ.setdefault("MUJOCO_GL", "osmesa")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    r = _overridden_regime(params, regime)
    cell_extent = max(r.radius_m, r.height_m)
    drop_height = 0.002
    viz_mass = min(r.payload_mass_kg, max(0.5, r.payload_mass_kg))
    # Keep the viz payload light enough that the cell stays visibly intact
    # for the still (mirrors render_regimes' cap).
    max_viz = 0.05 * cell_extent * r.cable_stiffness_Npm / 9.81
    viz_mass = min(r.payload_mass_kg, max(0.5, max_viz))

    floor_size = 4.0 * (cell_extent + drop_height)
    xml = patch_xml(
        build_render_xml(r, drop_height=drop_height, payload_mass_kg=viz_mass),
        floor_size=floor_size,
    )
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    tendon_width = max(0.0006, 0.05 * r.strut_radius_m)
    if model.tendon_width.size:
        model.tendon_width[:] = tendon_width
    L0 = model.tendon_lengthspring[:, 1].copy() if model.ntendon else None

    nsteps = max(1, int(settle_ms * 1e-3 / model.opt.timestep))
    for _ in range(nsteps):
        mujoco.mj_step(model, data)
        if not np.isfinite(data.qpos).all():
            break
    if model.ntendon and L0 is not None:
        strain = np.maximum(data.ten_length - L0, 0.0)
        model.tendon_rgba[:] = strain_to_rgba(strain, max(strain.max(), 1e-4))

    renderer = mujoco.Renderer(model, height=480, width=480)
    cam = mujoco.MjvCamera()
    cam.lookat[:] = (0.0, 0.0, 0.5 * (drop_height + r.height_m))
    cam.distance = 4.6 * cell_extent + 1.5 * drop_height
    cam.elevation = -12.0
    cam.azimuth = 35.0
    renderer.update_scene(data, camera=cam)
    frame = renderer.render()

    if title:
        try:
            from PIL import Image, ImageDraw

            img = Image.fromarray(frame)
            draw = ImageDraw.Draw(img)
            for dy, line in enumerate(title.split("\n")):
                draw.text((8, 8 + 14 * dy), line, fill=(255, 255, 255))
            frame = np.array(img)
        except Exception:
            pass

    try:
        import imageio.v2 as imageio

        imageio.imwrite(out_path, frame)
    except Exception:
        from PIL import Image

        Image.fromarray(frame).save(out_path)
    return out_path


def render_drop_animation(params: dict, regime: Regime, out_stem: str,
                          *, title: str | None = None) -> str:
    """Full free-fall → impact drop GIF/MP4 for a headline pick."""
    r = _overridden_regime(params, regime)
    cell_extent = max(r.radius_m, r.height_m)
    drop_height = min(0.20, max(0.04, 1.5 * cell_extent))
    free_fall_s = float(np.sqrt(2.0 * drop_height / 9.81))
    duration = free_fall_s + 0.20
    max_viz = 0.05 * cell_extent * r.cable_stiffness_Npm / 9.81
    viz_mass = min(r.payload_mass_kg, max(0.5, max_viz))
    z0 = drop_height + 2.0 * r.strut_radius_m
    distance = 5.0 * cell_extent + 1.5 * drop_height
    lookat_z = 0.5 * (drop_height + z0 + r.height_m)
    floor_size = 4.0 * (cell_extent + drop_height)

    xml = build_render_xml(r, drop_height=drop_height, payload_mass_kg=viz_mass)
    return render_drop(
        xml,
        out_stem=out_stem,
        duration_s=duration,
        cam_lookat=(0.0, 0.0, lookat_z),
        cam_distance=distance,
        cam_elevation=-12.0,
        cam_azimuth=35.0,
        n_frames=60,
        playback_fps=24,
        tendon_width=max(0.0006, 0.05 * r.strut_radius_m),
        floor_size=floor_size,
        title=title,
    )


# --------------------------------------------------------------------------
# Annotated Pareto figure
# --------------------------------------------------------------------------
_GROUP_STYLE = {
    "Pareto": dict(color="#1a9850", marker="*", s=130, label="Pareto front"),
    "mediocre": dict(color="#fdae61", marker="o", s=70, label="mediocre pick"),
    "worst": dict(color="#d73027", marker="X", s=90, label="worst pick"),
}


def annotated_pareto_figure(rows: list[dict], picks: list[dict],
                            thumbs: dict[str, str], regime: Regime,
                            out_path: str) -> str:
    """Pareto scatter (SEA↔eta, colour=F_peak) with render thumbnails."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage

    feas = [r for r in rows if r["feasible"]]
    pmask = pareto_mask(feas)
    sea = np.array([r["SEA_J_per_g"] for r in feas]) * 1e3   # mJ/g
    eta = np.array([r["eta"] for r in feas])
    fpk = np.array([r["F_peak_N"] for r in feas])

    fig, ax = plt.subplots(figsize=(13, 9))
    sc = ax.scatter(sea, eta, c=fpk, cmap="viridis", s=14, alpha=0.55,
                    edgecolors="none", zorder=1)
    cb = fig.colorbar(sc, ax=ax, pad=0.02, fraction=0.04)
    cb.set_label("F_peak (N)  — near-invariant support-load proxy at Tier-C")

    # Faint markers for the full 3-objective non-dominated set.
    pf3 = np.where(pmask)[0]
    ax.scatter(sea[pf3], eta[pf3], facecolors="none", edgecolors="#1a9850",
               s=30, linewidths=0.8, alpha=0.5, zorder=2,
               label="3-objective Pareto set")

    # Clean 2-D SEA↔eta frontier (the live trade-off): the upper-right
    # staircase of points not dominated in the SEA/eta plane.  Drawing the
    # full 3-objective set as a sorted line is misleading because eta is
    # near-degenerate, so connect only the genuine SEA/eta frontier.
    f2 = np.ones(len(feas), dtype=bool)
    for i in range(len(feas)):
        dominated = (sea >= sea[i] - 1e-12) & (eta >= eta[i] - 1e-12) \
            & ((sea > sea[i] + 1e-12) | (eta > eta[i] + 1e-12))
        dominated[i] = False
        if np.any(dominated):
            f2[i] = False
    front = np.where(f2)[0]
    front = front[np.argsort(sea[front])]
    ax.plot(sea[front], eta[front], "-", color="#1a9850", lw=2.0, alpha=0.95,
            zorder=4, label="SEA↔eta frontier")
    ax.scatter(sea[front], eta[front], color="#1a9850", s=46,
               edgecolors="black", linewidths=0.7, zorder=5)

    # Thumbnail callouts arranged around the axes border (axes-fraction
    # coords just outside [0, 1] so leader lines stay readable and the
    # thumbnails clear the plot, title, and colorbar).
    ring = [(0.30, 1.13), (0.70, 1.13),                 # top
            (1.22, 0.82), (1.22, 0.50), (1.22, 0.16),   # right
            (0.70, -0.15), (0.30, -0.15),               # bottom
            (-0.24, 0.82), (-0.24, 0.50), (-0.24, 0.16)]  # left
    for i, p in enumerate(picks):
        style = _GROUP_STYLE.get(p["group"], _GROUP_STYLE["mediocre"])
        ax.scatter([p["SEA_J_per_g"] * 1e3], [p["eta"]],
                   color=style["color"], marker=style["marker"],
                   s=style["s"] * 1.4, edgecolors="black", linewidths=0.8,
                   zorder=5)
        thumb = thumbs.get(p["tag"])
        if not thumb or not os.path.exists(thumb):
            continue
        try:
            import imageio.v2 as imageio

            img = imageio.imread(thumb)
        except Exception:
            continue
        oimg = OffsetImage(img, zoom=0.165)
        fx, fy = ring[i % len(ring)]
        cap = (f"{p['label']}\nR{p['R_mm']:.0f} H{p['H_mm']:.0f} "
               f"tw{p['twist_deg']:.0f}\nds{p['strut_d_mm']:.1f} "
               f"dc{p['cable_d_mm']:.1f}\nSEA {p['SEA_J_per_g'] * 1e3:.2f} mJ/g  "
               f"eta {p['eta']:.2f}")
        ab = AnnotationBbox(
            oimg, (p["SEA_J_per_g"] * 1e3, p["eta"]),
            xybox=(fx, fy), xycoords="data", boxcoords="axes fraction",
            pad=0.2, arrowprops=dict(arrowstyle="-|>", color=style["color"],
                                     lw=1.3, connectionstyle="arc3,rad=0.15"),
            bboxprops=dict(edgecolor=style["color"], lw=1.5),
            zorder=6,
        )
        ax.add_artist(ab)
        ax.annotate(cap, (fx, fy), xycoords="axes fraction",
                    xytext=(0, -34), textcoords="offset points",
                    ha="center", va="top", fontsize=6.5,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec=style["color"], lw=0.8), zorder=6)

    # Legend for groups.
    from matplotlib.lines import Line2D

    handles = [
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#1a9850",
               markeredgecolor="black", markersize=14, label="Pareto-front pick"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#fdae61",
               markeredgecolor="black", markersize=10, label="mediocre pick"),
        Line2D([0], [0], marker="X", color="w", markerfacecolor="#d73027",
               markeredgecolor="black", markersize=11, label="worst pick"),
        Line2D([0], [0], color="#1a9850", lw=2.0, label="SEA↔eta frontier"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="none",
               markeredgecolor="#1a9850", markersize=8,
               label="3-objective Pareto set"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8, framealpha=0.9)

    ax.set_xlabel("SEA (mJ/g)  →  better")
    ax.set_ylabel("eta (compaction efficiency)  →  better")
    fig.suptitle(
        f"Tier-C Pareto front over the PR #35 T3-prism box — {regime.name}\n"
        f"{len(feas)} feasible designs; SEA↔eta is the live trade-off "
        f"(F_peak ~ constant)", fontsize=12, y=0.98)
    ax.margins(0.30)
    fig.subplots_adjust(left=0.21, right=0.80, top=0.84, bottom=0.16)
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"wrote {out_path}")
    return out_path


# --------------------------------------------------------------------------
# CSV + summary
# --------------------------------------------------------------------------
def write_csv(rows: list[dict], pmask: np.ndarray, path: str) -> None:
    import csv

    feas = [r for r in rows if r["feasible"]]
    pareto_keys = {tuple(round(feas[i][k], 6) for k in PARAM_NAMES)
                   for i in np.where(pmask)[0]}
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(PARAM_NAMES + OBJECTIVES + ["feasible", "pareto"])
        for r in rows:
            key = tuple(round(r[k], 6) for k in PARAM_NAMES)
            is_pareto = r["feasible"] and key in pareto_keys
            w.writerow([r[k] for k in PARAM_NAMES]
                       + [r[k] for k in OBJECTIVES]
                       + [int(r["feasible"]), int(is_pareto)])
    print(f"wrote {path} ({len(rows)} rows)")


def append_summary(lines: list[str], regime_key: str, picks: list[dict]) -> None:
    lines.append(f"\n### {regime_key}\n")
    lines.append("| group | label | R_mm | H_mm | twist | strut_d | cable_d "
                 "| F_peak_N | SEA_mJ/g | eta |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    order = {"Pareto": 0, "mediocre": 1, "worst": 2}
    for p in sorted(picks, key=lambda r: (order.get(r["group"], 9),
                                          -r["SEA_J_per_g"])):
        lines.append(
            f"| {p['group']} | {p['label']} | {p['R_mm']:.1f} | {p['H_mm']:.1f} "
            f"| {p['twist_deg']:.0f} | {p['strut_d_mm']:.1f} "
            f"| {p['cable_d_mm']:.1f} | {p['F_peak_N']:.0f} "
            f"| {p['SEA_J_per_g'] * 1e3:.3f} | {p['eta']:.3f} |")


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def run_regime(regime_key: str, *, n: int, seed: int,
               summary: list[str]) -> None:
    regime = REGIMES[regime_key]
    print(f"\n=== {regime_key} ({regime.name}): {n} Sobol designs ===")
    designs = sobol_designs(n, seed=seed)
    rows = evaluate_box(designs, regime)

    feas = [r for r in rows if r["feasible"]]
    pmask = pareto_mask(feas)
    print(f"  feasible {len(feas)}/{len(rows)}; "
          f"Pareto-front size {int(pmask.sum())}")

    write_csv(rows, pmask, os.path.join(OUT_DIR, f"pareto_{regime_key}.csv"))

    picks = select_representatives(rows)
    print(f"  selected {len(picks)} representative designs to render")

    # Stills for every pick (callout thumbnails).
    thumbs: dict[str, str] = {}
    for p in picks:
        out = os.path.join(OUT_DIR, f"pareto_{regime_key}_render_{p['tag']}.png")
        title = (f"{p['label']}\nSEA {p['SEA_J_per_g'] * 1e3:.2f} mJ/g "
                 f"eta {p['eta']:.2f}")
        render_still({**p}, regime, out, title=title)
        thumbs[p["tag"]] = out
        print(f"    still: {os.path.basename(out)}")

    annotated_pareto_figure(
        rows, picks, thumbs, regime,
        os.path.join(OUT_DIR, f"pareto_{regime_key}_annotated.png"))

    # Headline drop animations: best SEA + worst.
    best = next((p for p in picks if p["tag"] == "best_sea"), None)
    worst = next((p for p in picks if p["group"] == "worst"), None)
    for p, kind in ((best, "best"), (worst, "worst")):
        if p is None:
            continue
        stem = os.path.join(OUT_DIR, f"pareto_{regime_key}_{kind}_drop")
        title = (f"{regime.name} {kind}: {p['label']} "
                 f"SEA {p['SEA_J_per_g'] * 1e3:.2f} mJ/g")
        try:
            render_drop_animation({**p}, regime, stem, title=title)
        except Exception as exc:  # pragma: no cover
            print(f"    (drop animation skipped for {kind}: {exc})")

    append_summary(summary, regime_key, picks)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=2048,
                    help="Sobol designs per regime (default 2048)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--regimes", nargs="+", default=["crutch", "lander"],
                    choices=list(REGIMES))
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    summary = ["# Tier-C Pareto-front render campaign (PR #35 T3-prism box)\n",
               f"Sobol designs per regime: {args.n}\n"]
    for rk in args.regimes:
        run_regime(rk, n=args.n, seed=args.seed, summary=summary)

    with open(os.path.join(OUT_DIR, "pareto_summary.md"), "w") as fh:
        fh.write("\n".join(summary) + "\n")
    print(f"\nwrote {os.path.join(OUT_DIR, 'pareto_summary.md')}")


if __name__ == "__main__":
    main()
