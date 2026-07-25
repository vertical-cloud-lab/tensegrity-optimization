#!/usr/bin/env python3
# ============================================================================
# Level-3 G-code-driven thermo-mechanical wobble analysis of the TPU tendons.
#
# Why this exists
# ---------------
# Levels 1-2 (`sweep_cage_design.py`, `fea_tendon_wobble.py`) assume a fixed
# "hot tip" length. This script closes the loop with the real machine
# schedule, per the Edison Level-3 recommendation ("G-code-driven
# thermo-mechanical FEA with element activation"):
#
#   1. parses the actual Bambu Studio H2D g-code (produced by
#      `slice_bambu_h2d.py`) into per-layer print times by integrating every
#      move's distance/feedrate (accel ignored; the sum is rescaled to the
#      slicer's own total-time estimate to compensate);
#   2. runs a Newton-cooling model of the tendon: when the print front is at
#      layer N, layer k has been cooling for the sum of the layer times in
#      between, giving a temperature - and with an engineering E(T) map for
#      TPU 85A, a modulus - profile E(z) down the tendon;
#   3. feeds that profile into the Level-2 CalculiX growing-tendon contact
#      FEA (one material band per element) and compares the g-code-driven
#      result against the constant-E + fixed-hot-tip assumption;
#   4. repeats for two what-if schedules: the multi-material PLA+TPU print
#      (measured single-material layer times scaled to the 21.4 h MM slice)
#      and a worst-case "tendon-only" schedule (nozzle returns after just
#      the tendon perimeter, ~3 s) - the case Edison's "print several parts
#      at once / add a cooling tower" advice (#10) protects against.
#
# E(T) map (engineering estimate, documented caveat): printed TPU 85A
# E = 15 MPa at 25 C, halving by ~60 C, ~10% by 120 C, ~1% near the melt.
# The absolute numbers matter less than the *length* of tendon that is
# still soft when the nozzle returns - which is what this script measures.
#
# Requires: ccx on PATH, numpy, matplotlib, a g-code file from
# `slice_bambu_h2d.py` (45 MB one for the committed combined mesh is not
# committed; re-slice per the README recipe).
# ============================================================================
from __future__ import annotations

import argparse
import json
import math
import re
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fea_tendon_wobble import run_ccx, parse_ux_all, parse_rf

C_BLUE, C_ORANGE, C_AQUA, C_YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"

RHO_TPU = 1.21e-9      # tonne/mm^3
G_MMS2 = 9810.0

RE_MOVE = re.compile(
    r"^G[01]\s(?=[^;]*[XYZEF])(?:[^;]*?X(?P<x>-?\d+\.?\d*))?"
    r"(?:[^;]*?Y(?P<y>-?\d+\.?\d*))?(?:[^;]*?Z(?P<z>-?\d+\.?\d*))?"
    r"(?:[^;]*?E(?P<e>-?\.?\d+\.?\d*))?(?:[^;]*?F(?P<f>\d+\.?\d*))?")


def layer_times(gcode: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """Integrate per-layer durations from the g-code.

    Returns (layer z array, layer duration array (s), slicer total est. s).
    """
    zs: list[float] = []
    times: list[float] = []
    cur_t = 0.0
    x = y = 0.0
    z = 0.0
    feed = 3000.0   # mm/min
    est_total = 0.0
    n_layer = -1
    for ln in gcode.open():
        if ln.startswith("; CHANGE_LAYER"):
            if n_layer >= 0:
                times.append(cur_t)
            cur_t = 0.0
            n_layer += 1
            continue
        if ln.startswith("; Z_HEIGHT:"):
            try:
                zval = float(ln.split(":")[1])
                if n_layer >= 0:
                    if len(zs) == n_layer:
                        zs.append(zval)
            except ValueError:
                pass
            continue
        if ln.startswith("; total estimated time:") or \
                ("total estimated time" in ln and est_total == 0.0):
            m = re.findall(r"(?:(\d+)h\s*)?(?:(\d+)m\s*)?(\d+)s", ln)
            if m:
                h, mnt, s = (int(v) if v else 0 for v in m[-1])
                est_total = h * 3600 + mnt * 60 + s
            continue
        if not (ln.startswith("G1 ") or ln.startswith("G0 ")):
            continue
        m = RE_MOVE.match(ln)
        if not m:
            continue
        if m.group("f"):
            feed = float(m.group("f"))
        nx = float(m.group("x")) if m.group("x") else x
        ny = float(m.group("y")) if m.group("y") else y
        nz = float(m.group("z")) if m.group("z") else z
        dist = math.dist((x, y, z), (nx, ny, nz))
        if dist > 0 and feed > 0:
            cur_t += dist / (feed / 60.0)
        x, y, z = nx, ny, nz
    if cur_t > 0:
        times.append(cur_t)
    t = np.array(times)
    zarr = np.array(zs[:len(t)]) if len(zs) >= len(t) else \
        np.arange(1, len(t) + 1) * 0.2
    if est_total > 0 and t.sum() > 0:
        t *= est_total / t.sum()     # fold in accel/misc the integral misses
    return zarr, t, est_total


def e_of_t(temp_c: np.ndarray, e_cold: float) -> np.ndarray:
    """Engineering E(T) map for printed TPU 85A (log-linear between knots)."""
    knots_t = np.array([25.0, 60.0, 120.0, 170.0, 230.0])
    knots_f = np.log(np.array([1.0, 0.5, 0.10, 0.03, 0.01]))
    f = np.interp(temp_c, knots_t, knots_f)
    return e_cold * np.exp(f)


def modulus_profile(ages_s: np.ndarray, *, tau: float, t_noz: float,
                    t_amb: float, e_cold: float) -> np.ndarray:
    temp = t_amb + (t_noz - t_amb) * np.exp(-np.maximum(ages_s, 0.0) / tau)
    return e_of_t(temp, e_cold)


def banded_inp(length: float, *, radius: float, tilt_deg: float, nu: float,
               elem_len: float, e_elems: np.ndarray,
               ring_spacing: float | None, force_n: float,
               active: dict[int, float] | None) -> tuple[str, int, list[int]]:
    """Level-2 beam model with per-element modulus bands from the g-code."""
    t = math.radians(tilt_deg)
    u = np.array([math.sin(t), 0.0, math.cos(t)])
    n_elem = len(e_elems)
    n_nodes = 2 * n_elem + 1
    s = np.linspace(0.0, length, n_nodes)
    lines = ["*NODE, NSET=NALL"]
    for i, si in enumerate(s, start=1):
        p = si * u
        lines.append(f"{i}, {p[0]:.6e}, {p[1]:.6e}, {p[2]:.6e}")
    # quantize moduli into <=12 bands (log-spaced) -> element sets
    logs = np.log(e_elems)
    nb = min(12, len(np.unique(np.round(logs, 2))))
    edges = np.linspace(logs.min() - 1e-9, logs.max() + 1e-9, nb + 1)
    band = np.clip(np.digitize(logs, edges) - 1, 0, nb - 1)
    e_band = [float(np.exp(logs[band == b].mean())) if (band == b).any()
              else None for b in range(nb)]
    for b in range(nb):
        elems = [e for e in range(n_elem) if band[e] == b]
        if not elems:
            continue
        lines.append(f"*ELEMENT, TYPE=B32, ELSET=BAND{b}")
        for e in elems:
            aa = 2 * e + 1
            lines.append(f"{e + 1}, {aa}, {aa + 1}, {aa + 2}")
    ring_nodes: list[int] = []
    if ring_spacing is not None:
        h = ring_spacing
        while h < length - 1e-6:
            k = int(np.argmin(np.abs(s - h)))
            if k > 0:
                ring_nodes.append(k + 1)
            h += ring_spacing
    i_circ = math.pi * radius**4 / 4.0
    side = (12.0 * i_circ) ** 0.25          # ccx CIRC defect workaround
    for b in range(nb):
        if e_band[b] is None:
            continue
        lines += [f"*BEAM SECTION, ELSET=BAND{b}, MATERIAL=M{b}, "
                  "SECTION=RECT", f"{side:.6f}, {side:.6f}", "0., 1., 0.",
                  ]
    for b in range(nb):
        if e_band[b] is None:
            continue
        lines += [f"*MATERIAL, NAME=M{b}", "*ELASTIC",
                  f"{e_band[b]:.6f}, {nu}", "*DENSITY", f"{RHO_TPU}"]
    lines += ["*NSET, NSET=TIP", f"{n_nodes}"]
    if ring_nodes:
        lines += ["*NSET, NSET=RINGS",
                  ", ".join(str(r) for r in ring_nodes)]
    lines += ["*BOUNDARY", "1, 1, 6"]
    for nid, ux in (active or {}).items():
        lines.append(f"{nid}, 1, 1, {ux}")
    lines += ["*STEP, NLGEOM", "*STATIC", "0.1, 1.0"]
    for b in range(nb):
        if e_band[b] is None:
            continue
        lines += ["*DLOAD", f"BAND{b}, GRAV, {G_MMS2}, 0., 0., -1."]
    lines += ["*CLOAD", f"TIP, 1, {force_n}",
              "*NODE PRINT, NSET=NALL", "U"]
    if active:
        lines += ["*NODE PRINT, NSET=RINGS", "RF"]
    lines += ["*END STEP"]
    return "\n".join(lines) + "\n", n_nodes, ring_nodes


def solve_banded(length: float, wd: Path, *, ring_clearance: float,
                 ring_spacing: float | None, **kw) -> float:
    active: dict[int, float] = {}
    for _ in range(12):
        inp, tip, rings = banded_inp(length, ring_spacing=ring_spacing,
                                     active=active, **kw)
        dat = run_ccx(inp, wd, "l3")
        ux = parse_ux_all(dat)
        rf = parse_rf(dat) if active else {}
        changed = False
        for r in rings:
            if r not in active and ux.get(r, 0.0) > ring_clearance + 1e-6:
                active[r] = ring_clearance
                changed = True
        for r in list(active):
            if rf.get(r, -1.0) > 1e-9:
                del active[r]
                changed = True
        if not changed:
            break
    return abs(ux.get(tip, float("nan")))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    ap.add_argument("gcode", type=Path, help="g-code from slice_bambu_h2d.py")
    ap.add_argument("--tendon_z", type=float, nargs=2, default=(22.0, 100.0),
                    help="tendon z range in the print frame (cage report)")
    ap.add_argument("--tendon_d", type=float, default=4.95)
    ap.add_argument("--tilt", type=float, default=19.7)
    ap.add_argument("--force", type=float, default=0.01)
    ap.add_argument("--e_tpu", type=float, default=15.0)
    ap.add_argument("--nu", type=float, default=0.48)
    ap.add_argument("--elem_len", type=float, default=1.0)
    ap.add_argument("--tau", type=float, default=73.0,
                    help="Newton-cooling time constant, s (rho*cp*(d/4)/h, "
                         "h~35 W/m2K at 30-40%% fan)")
    ap.add_argument("--t_noz", type=float, default=230.0)
    ap.add_argument("--t_amb", type=float, default=30.0)
    ap.add_argument("--mm_total_h", type=float, default=21.35,
                    help="est. duration of the PLA+TPU multi-material slice "
                         "(h); scales the measured layer times")
    ap.add_argument("--out", type=Path,
                    default=here / "t3-prism-pr35-gcode-thermal-wobble.png")
    ap.add_argument("--out_json", type=Path,
                    default=here / "t3-prism-pr35-gcode-thermal-wobble.json")
    a = ap.parse_args()

    zarr, tlay, est = layer_times(a.gcode)
    print(f"parsed {len(tlay)} layers, slicer total {est/3600:.2f} h, "
          f"mean layer {tlay.mean():.1f} s")
    # layers spanning the tendon
    sel = (zarr >= a.tendon_z[0]) & (zarr <= a.tendon_z[1])
    t_tendon = tlay[sel]
    print(f"tendon layers: {sel.sum()} (z {a.tendon_z[0]:g}-{a.tendon_z[1]:g}"
          f" mm), mean layer time {t_tendon.mean():.1f} s, "
          f"min {t_tendon.min():.1f} s")

    span = (a.tendon_z[1] - a.tendon_z[0]) / math.cos(math.radians(a.tilt))
    radius = a.tendon_d / 2.0

    schedules = [
        ("single-material schedule (this g-code)", C_BLUE, t_tendon.copy()),
        (f"PLA+TPU schedule (×{a.mm_total_h*3600/est:.1f} layer times)",
         C_YELLOW, t_tendon * (a.mm_total_h * 3600.0 / est)),
        ("worst case: tendon-only schedule (3 s/layer)", C_ORANGE,
         np.full_like(t_tendon, 3.0)),
    ]

    configs = [("bare", None, 0.0),
               ("committed cage (1.2 @ 18)", 18.0, 1.2),
               ("recommended cage (0.8 @ 12)", 12.0, 0.8)]

    lengths = np.linspace(span / 8, span, 8)
    layer_h_along = 0.2 / math.cos(math.radians(a.tilt))

    results: dict[str, dict[str, list[float]]] = {}
    soft_lens: dict[str, float] = {}
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        for sched_label, _, times in schedules:
            per_layer = np.interp(
                np.linspace(0, len(times) - 1, 400), np.arange(len(times)),
                times)
            results[sched_label] = {}
            for cfg_label, spacing, gap in configs:
                vals = []
                for L in lengths:
                    n_elem = max(4, int(round(L / a.elem_len)))
                    s_mid = (np.arange(n_elem) + 0.5) * (L / n_elem)
                    # age of material at arc position s when front is at L:
                    # sum of layer times between its layer and the front
                    frac_front = L / span
                    frac = s_mid / span
                    idx_front = frac_front * (len(per_layer) - 1)
                    idxs = frac * (len(per_layer) - 1)
                    cum = np.concatenate([[0.0], np.cumsum(per_layer)])
                    ages = np.interp(idx_front, np.arange(len(cum)), cum) - \
                        np.interp(idxs, np.arange(len(cum)), cum)
                    e_elems = modulus_profile(
                        ages, tau=a.tau, t_noz=a.t_noz, t_amb=a.t_amb,
                        e_cold=a.e_tpu)
                    vals.append(solve_banded(
                        float(L), wd, ring_clearance=gap,
                        ring_spacing=spacing, radius=radius,
                        tilt_deg=a.tilt, nu=a.nu, elem_len=a.elem_len,
                        e_elems=e_elems, force_n=a.force))
                results[sched_label][cfg_label] = vals
                print(f"  {sched_label:45s} {cfg_label:28s} "
                      f"max {max(vals):6.2f} mm")
            # soft length at full height (E < 0.5 E_cold)
            ages_full = np.cumsum(per_layer[::-1])[::-1]
            e_full = modulus_profile(ages_full, tau=a.tau, t_noz=a.t_noz,
                                     t_amb=a.t_amb, e_cold=a.e_tpu)
            frac_soft = float((e_full < 0.5 * a.e_tpu).mean())
            soft_lens[sched_label] = frac_soft * span
            print(f"  {sched_label:45s} soft length (E<E/2): "
                  f"{soft_lens[sched_label]:.2f} mm")

    # ---- figure -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(16.0, 5.0), facecolor=SURFACE)
    for ax in axes:
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(INK2)
        ax.tick_params(colors=INK2)

    ax = axes[0]
    ax.plot(zarr, tlay, color=C_BLUE, linewidth=1.0)
    ax.axvspan(a.tendon_z[0], a.tendon_z[1], color=C_AQUA, alpha=0.12)
    ax.annotate("tendon span", (a.tendon_z[0] + 2, tlay.max() * 0.9),
                color=C_AQUA, fontsize=9)
    ax.set_xlabel("layer z (mm)", color=INK)
    ax.set_ylabel("layer print time (s)", color=INK)
    ax.set_title("A — per-layer times from the H2D g-code", color=INK,
                 fontsize=10)

    ax = axes[1]
    dz = np.linspace(0.0, 20.0, 300)
    for sched_label, color, times in schedules:
        mean_t = float(np.mean(times))
        ages = dz / layer_h_along * mean_t
        e_prof = modulus_profile(ages, tau=a.tau, t_noz=a.t_noz,
                                 t_amb=a.t_amb, e_cold=a.e_tpu)
        ax.plot(dz, e_prof / a.e_tpu, color=color, linewidth=2,
                label=f"{sched_label} (soft {soft_lens[sched_label]:.1f} mm)")
    ax.axhline(0.5, color=INK2, linestyle="--", linewidth=1)
    ax.set_xlabel("distance below print front (mm)", color=INK)
    ax.set_ylabel("E / E_cold when nozzle returns", color=INK)
    ax.set_title("B — modulus profile down the tendon", color=INK,
                 fontsize=10)
    ax.legend(fontsize=7, framealpha=0, labelcolor=INK)

    ax = axes[2]
    for sched_label, color, _ in schedules:
        for cfg_label, ls, mk in (("bare", ":", "o"),
                                  ("committed cage (1.2 @ 18)", "--", "s"),
                                  ("recommended cage (0.8 @ 12)", "-", "D")):
            ax.plot(lengths, results[sched_label][cfg_label], ls, marker=mk,
                    markersize=4, color=color, linewidth=1.4,
                    label=f"{sched_label.split(' (')[0]} — {cfg_label}")
    ax.axhline(0.2, color=INK2, linestyle=":", linewidth=1)
    ax.set_yscale("log")
    ax.set_xlabel("printed tendon length (mm)", color=INK)
    ax.set_ylabel(f"print-front deflection (mm) @ {a.force*1e3:g} mN",
                  color=INK)
    ax.set_title("C — g-code-driven contact FEA", color=INK, fontsize=10)
    ax.legend(fontsize=6, framealpha=0, labelcolor=INK)

    fig.suptitle(
        f"Level-3 g-code-driven thermo-mechanical wobble — τ={a.tau:g} s, "
        f"T_noz={a.t_noz:g} °C, E(T) engineering map, "
        f"{len(tlay)} layers parsed", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(a.out, dpi=140, facecolor=SURFACE)
    print(f"wrote {a.out}")

    out = dict(
        n_layers=len(tlay), slicer_total_s=est,
        tendon_layer_time_mean_s=float(t_tendon.mean()),
        soft_length_mm={k: float(v) for k, v in soft_lens.items()},
        lengths_mm=[float(v) for v in lengths],
        max_deflection_mm={
            s: {c: float(max(v)) for c, v in cfgs.items()}
            for s, cfgs in results.items()},
        tau_s=a.tau, t_noz_c=a.t_noz, e_tpu_mpa=a.e_tpu,
    )
    a.out_json.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {a.out_json}")


if __name__ == "__main__":
    main()
