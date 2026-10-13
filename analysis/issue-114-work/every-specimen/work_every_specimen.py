#!/usr/bin/env python3
"""Justin's work value for every drop-tested specimen, with T180 and the velocity
loss index, and the Pareto fronts between them (issue #114).

Marcus's request (2026-10-13): run the analysis done for the corny batch (the
peak of the total work near 40 ms, commit ``1aff9ff``) and the one being done
for Justin the same day (the work just before lift-off for the specimens with
no peak, commit ``a06be35``) on every specimen that has been drop tested, and
plot the Pareto fronts of work against transmissibility (T180) and against the
velocity loss index (VLI).

Specimens: the 54 sessions of the optimization campaign, all dropped from 60 in
onto the 1/2 in PU mat with the same four channels (see ``fetch_waveforms.py``).

* Work: Justin's ``numaric_work``, compiled unchanged from
  ``justin/implimatation_or_work_2026-10-06.py`` and called as his loop calls it
  (CH4 top, CH5 bottom, G to m/s^2 with 9.81, m = 1, v0 = -5.46).
* Peak rule (``1aff9ff``, unchanged): his pick ``max(work_z[1250:2250])`` (25 to
  45 ms) counts only if it sits at least 0.5 ms inside the window and stands at
  least ``MIN_PROM`` = 0.75 J/kg above the curve on both sides; otherwise the
  most prominent peak between 15 and 70 ms, if it clears ``MIN_PROM``.
* Lift-off rule (``a06be35``, unchanged): the deformation is the running sum of
  his ``dx_top - dx_bottom`` (CH4 minus CH5 integrated twice); the jump is the
  first time it stands ``JUMP_MM`` = 0.25 mm above its lowest so far; the value
  is the total work ``MARGIN_MS`` = 2 ms before the jump.
* A specimen uses the peak rule if at least half of its drops 3 to 20 have a
  peak (the mean then covers those drops, as in ``1aff9ff``), and the lift-off
  rule otherwise (all 18 drops). On the 36 specimens of the two earlier runs
  this is all or nothing, so both runs' numbers come back unchanged.
* T180 and VLI = 1 - e_rebound per drop come from the lab pipeline
  (``lab_metrics.py``), averaged over the same drops 3 to 20.
* Pareto fronts: more negative work (more energy taken in), lower T180 and
  higher VLI are better. A specimen is on a front if no other specimen is at
  least as good on both axes and better on one, judged on specimen means.

Inputs: ``waveforms/<specimen>_waveforms_50kHz.csv`` (``fetch_waveforms.py``),
``results/per_drop_lab_metrics.csv`` (``lab_metrics.py``) and the campaign
tables in ``campaign/``. Outputs go to ``results/`` and ``figures/``.
"""
from __future__ import annotations

import ast
import csv
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import scipy.integrate  # noqa: F401  (Justin's function uses sp.integrate)
from matplotlib.lines import Line2D
from scipy import signal as sig

from fetch_waveforms import BATCHES

HERE = Path(__file__).resolve().parent
JUSTIN = HERE / "justin" / "implimatation_or_work_2026-10-06.py"
WAVES = HERE / "waveforms"
SPECIMENS = [s for b in BATCHES.values() for s in b]
GROUP = {"seed": "seed (Sobol)", "r2d2c": "r2d2c", "drran": "drran", "2dran": "2dran",
         "dran3": "dran3", "corny": "corny"}
BATCH_OF = {s: b for b, ss in BATCHES.items() for s in ss}
DROPS = range(3, 21)        # Justin's loop: range(3, 21)
WIN = (1250, 2250)          # Justin's window, 25 to 45 ms at 50 kHz
EDGE = 25                   # 0.5 ms: a pick this close to a window edge is the edge
MIN_PROM = 0.75             # J/kg, the 1aff9ff cutoff
FALLBACK_MS = (15.0, 70.0)  # where a corrected search looks
JUMP_MM = 0.25              # the a06be35 jump threshold
MARGIN_MS = 2.0             # "a few milliseconds before" the jump
MARGINS = (1.0, 2.0, 3.0)   # sensitivity check, as in a06be35
V0 = -5.46
G = 9.81
# Column of the top sensor's vertical axis in the waveform CSV (4 = CH4). On
# r2d2c9 the sensor sits rotated a quarter turn: over the first 15 ms CH3 gains
# +6.1 m/s against the base plate's +5.2, and CH4 only +0.5 (CH4 is vertical on
# the other 53), so CH3 stands in for CH4 there.
VERTICAL = {"r2d2c9": 3}
SQUASH_MM = -1.0            # deformation below this before the jump = a real squash
SPRINGBACK_MS = 3.0         # and a jump this long after the base pulse = spring-back, not lift-off

# chart chrome: the dataviz reference palette, light mode
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"
MARK = {"seed": "s", "r2d2c": "^", "drran": "o", "2dran": "o", "dran3": "o", "corny": "D"}
MARK_LABEL = {"s": "seed (Sobol), batch 1", "^": "r2d2c, batch 2",
              "o": "drran, 2dran, dran3, batch 3", "D": "corny, batch 4"}


def load_numaric_work():
    """Compile Justin's ``numaric_work`` from his file without running the rest of it."""
    tree = ast.parse(JUSTIN.read_text())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "numaric_work"]
    ns = {"np": np, "sp": sp}
    exec(compile(ast.Module(fn, type_ignores=[]), str(JUSTIN), "exec"), ns)
    return ns["numaric_work"]


# --- peak rule, as in all-specimens/work_all_specimens.py (1aff9ff) ---------------
def prominence(w: np.ndarray, j: int) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # a non-peak simply gets prominence 0
        return float(sig.peak_prominences(w, [j])[0][0])


def pick_peak(w: np.ndarray, tms: np.ndarray) -> dict:
    j = WIN[0] + int(np.argmax(w[WIN[0]:WIN[1]]))            # Justin's pick
    out = {"justin_max": w[j], "justin_t": tms[j], "justin_prom": prominence(w, j)}
    if WIN[0] + EDGE <= j < WIN[1] - EDGE and out["justin_prom"] >= MIN_PROM:
        return {**out, "status": "peak", "j": j, "prom": out["justin_prom"]}
    lo, hi = np.searchsorted(tms, FALLBACK_MS)
    pk, props = sig.find_peaks(w[lo:hi], prominence=0.0)
    best = int(np.argmax(props["prominences"])) if len(pk) else None
    if best is not None and props["prominences"][best] >= MIN_PROM:
        return {**out, "status": "corrected", "j": lo + int(pk[best]),
                "prom": float(props["prominences"][best])}
    return {**out, "status": "no peak", "j": None,
            "prom": float(props["prominences"][best]) if best is not None else 0.0}


# --- lift-off rule, as in liftoff-work/liftoff_work.py (a06be35) -----------------
def deformation(t: np.ndarray, a_top: np.ndarray, a_bottom: np.ndarray) -> np.ndarray:
    """Running sum of Justin's ``dx_top - dx_bottom``, in mm (+ = specimen taller)."""
    v_top = sp.integrate.cumulative_trapezoid(a_top, t, initial=0)
    v_bottom = sp.integrate.cumulative_trapezoid(a_bottom, t, initial=0)
    dt = np.diff(t)
    dx_top = dt * (0.5 * (v_top[1:] + v_top[:-1]) + V0)
    dx_bottom = dt * (0.5 * (v_bottom[1:] + v_bottom[:-1]) + V0)
    return 1e3 * np.concatenate([[0.0], np.cumsum(dx_top - dx_bottom)])


def find_jump(dmm: np.ndarray) -> int | None:
    """Index where the deformation first stands JUMP_MM above its lowest so far."""
    above = dmm - np.minimum.accumulate(dmm) >= JUMP_MM
    return int(np.argmax(above)) if above.any() else None


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def lab_table() -> dict:
    out = {}
    for r in read_csv(HERE / "results" / "per_drop_lab_metrics.csv"):
        out[(r["specimen_id"], int(r["drop"]))] = {k: float(r[k]) for k in
                                                   ("t180", "VLI", "e_rebound", "t_second_ms")}
    return out


def campaign_table() -> dict:
    """Official per-session means from the campaign tables (``campaign/``)."""
    out = {}
    for p in sorted((HERE / "campaign").glob("t3-prism-bo-*-drop-results.csv")):
        for r in read_csv(p):
            out[r["specimen"]] = {"t180": float(r["t180_mean"]),
                                  "VLI": 1.0 - float(r["e_rebound_mean"]),
                                  "mass_g": float(r["mass_g"]) if r["mass_g"] else np.nan,
                                  "n_valid": int(r["n_valid"]), "table": p.name}
    return out


def analyze(numaric_work, lab: dict) -> tuple[list[dict], dict]:
    rows, curves = [], {}
    for spec in SPECIMENS:
        data = np.loadtxt(WAVES / f"{spec}_waveforms_50kHz.csv", delimiter=",", skiprows=1)
        for k in DROPS:
            d = data[data[:, 0] == k]
            tms = d[:, 1]
            a_top, a_bottom = d[:, VERTICAL.get(spec, 4)] * G, d[:, 5] * G
            work_z, _, _ = numaric_work(tms * 1e-3, a_top, a_bottom)   # as Justin's loop
            p = pick_peak(work_z, tms)
            dmm = deformation(tms * 1e-3, a_top, a_bottom)
            j = find_jump(dmm)
            ipk = int(np.argmax(np.where(tms < 15.0, d[:, 5], -np.inf)))   # base pulse peak
            iend = ipk + int(np.argmax(d[ipk:, 5] < 0.05 * d[ipk, 5]))      # pulse over
            row = {"specimen_id": spec, "batch": BATCH_OF[spec], "drop": k,
                   "peak_status": p["status"],
                   "peak_work_J_per_kg": work_z[p["j"]] if p["j"] is not None else np.nan,
                   "peak_time_ms": tms[p["j"]] if p["j"] is not None else np.nan,
                   "peak_prominence_J_per_kg": p["prom"],
                   "justin_window_max_J_per_kg": p["justin_max"],
                   "jump_time_ms": tms[j] if j is not None else np.nan,
                   "base_pulse_end_ms": tms[iend],
                   "min_deformation_before_jump_mm": dmm[:j + 1].min() if j is not None
                   else np.nan}
            for m in MARGINS:
                i = int(np.searchsorted(tms, tms[j] - m)) if j is not None else None
                row[f"work_{m:.0f}ms_before_jump_J_per_kg"] = (work_z[i] if i is not None
                                                               else np.nan)
            row["work_at_15ms_J_per_kg"] = work_z[int(np.searchsorted(tms, 15.0))]
            row.update({k2: lab[(spec, k)][k2] for k2 in ("t180", "VLI", "t_second_ms")})
            rows.append(row)
            curves[(spec, k)] = (tms, work_z, dmm, p, j)
    return rows, curves


def summarize(rows: list[dict], camp: dict) -> list[dict]:
    out = []
    for spec in SPECIMENS:
        r = [x for x in rows if x["specimen_id"] == spec]
        with_peak = [x for x in r if x["peak_status"] != "no peak"]
        rule = "peak" if 2 * len(with_peak) >= len(r) else "lift-off"
        w = np.array([x["peak_work_J_per_kg"] for x in with_peak] if rule == "peak" else
                     [x[f"work_{MARGIN_MS:.0f}ms_before_jump_J_per_kg"] for x in r])
        t180 = np.array([x["t180"] for x in r])
        vli = np.array([x["VLI"] for x in r])
        c = camp.get(spec, {})
        s = {"specimen_id": spec, "batch": BATCH_OF[spec], "rule": rule,
             "n_drops": len(w), "n_with_peak": len(with_peak),
             "n_corrected": sum(x["peak_status"] == "corrected" for x in r),
             "work_J_per_kg": w.mean(), "sd_J_per_kg": w.std(ddof=1),
             "T180_mean": t180.mean(), "T180_sd": t180.std(ddof=1),
             "VLI_mean": vli.mean(), "VLI_sd": vli.std(ddof=1)}
        for m in MARGINS:
            v = np.array([x[f"work_{m:.0f}ms_before_jump_J_per_kg"] for x in r])
            s[f"mean_{m:.0f}ms_before_jump"] = np.nanmean(v)
        s["mean_peak_if_any"] = (np.mean([x["peak_work_J_per_kg"] for x in with_peak])
                                 if with_peak else np.nan)
        s["peak_time_mean_ms"] = (np.mean([x["peak_time_ms"] for x in with_peak])
                                  if with_peak else np.nan)
        s["max_prominence_J_per_kg"] = max(x["peak_prominence_J_per_kg"] for x in r)
        s["jump_time_mean_ms"] = np.nanmean([x["jump_time_ms"] for x in r])
        s["jump_after_pulse_end_ms"] = np.nanmean([x["jump_time_ms"] - x["base_pulse_end_ms"]
                                                   for x in r])
        s["min_deformation_before_jump_mean_mm"] = np.nanmean(
            [x["min_deformation_before_jump_mm"] for x in r])
        s["jump_is_springback"] = bool(s["jump_after_pulse_end_ms"] > SPRINGBACK_MS and
                                       s["min_deformation_before_jump_mean_mm"] < SQUASH_MM)
        s["top_channel"] = f"CH{VERTICAL.get(spec, 4)}"
        s["work_at_15ms_mean"] = np.mean([x["work_at_15ms_J_per_kg"] for x in r])
        s["T180_campaign"] = c.get("t180", np.nan)
        s["VLI_campaign"] = c.get("VLI", np.nan)
        s["campaign_n_valid"] = c.get("n_valid", "")
        s["mass_g"] = c.get("mass_g", np.nan)
        out.append(s)
    for key, sense in (("T180_mean", 1.0), ("VLI_mean", -1.0)):
        for wkey, tag in (("work_J_per_kg", ""), (f"mean_{MARGIN_MS:.0f}ms_before_jump", "_liftoff_all")):
            front = pareto([(s[wkey], sense * s[key]) for s in out])
            for s, f in zip(out, front):
                s[f"front_work_{key.split('_')[0]}{tag}"] = f
    return out


def pareto(points: list[tuple[float, float]]) -> list[bool]:
    """True where no other point is <= on both coordinates and < on one (minimizing)."""
    p = np.asarray(points)
    return [not any(np.all(q <= x) and np.any(q < x) for q in p) for x in p]


def write_csv(path: Path, rows: list[dict], digits: int = 4) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if isinstance(v, float) and not np.isfinite(v)
                            else (f"{v:.{digits}f}" if isinstance(v, (float, np.floating))
                                  else v)) for k, v in r.items()})


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelcolor=INK2, labelsize=9)
    ax.xaxis.label.set_color(INK2)
    ax.yaxis.label.set_color(INK2)


def value(r: dict, rule: str) -> float:
    return (r["peak_work_J_per_kg"] if rule == "peak"
            else r[f"work_{MARGIN_MS:.0f}ms_before_jump_J_per_kg"])


def fig_all(rows, summ, png: Path) -> None:
    fig, ax = plt.subplots(figsize=(17, 5.8), facecolor=SURFACE)
    rng = np.random.default_rng(0)
    ax.axhline(0.0, color=AXIS, lw=1.0, zorder=1)
    x = np.arange(len(summ)) + np.repeat(np.arange(len(BATCHES)), 9) * 0.9
    for xi, s in zip(x, summ):
        peak = s["rule"] == "peak"
        w = [value(r, s["rule"]) for r in rows if r["specimen_id"] == s["specimen_id"]
             and (r["peak_status"] != "no peak" or not peak)]
        ax.plot(xi + rng.uniform(-0.18, 0.18, len(w)), w, "o", ms=2.6, color=MUTED,
                alpha=0.5, mew=0, zorder=2)
        ax.errorbar(xi, s["work_J_per_kg"], yerr=s["sd_J_per_kg"], fmt="D" if peak else "o",
                    ms=6.5 if peak else 6, color=ORANGE if peak else BLUE, mec=SURFACE,
                    mew=1.2, elinewidth=1.5, capsize=3.5, capthick=1.5, zorder=3)
    for b, name in enumerate(BATCHES):
        xs = x[9 * b:9 * b + 9]
        ax.text(xs.mean(), 0.55, GROUP[name], ha="center", va="bottom", color=INK2,
                fontsize=10)
    ax.set_xticks(x, [s["specimen_id"] for s in summ], rotation=60, ha="right", fontsize=8.5)
    ax.set_xlim(x[0] - 0.7, x[-1] + 0.7)
    lo = min(s["work_J_per_kg"] - s["sd_J_per_kg"] for s in summ)
    ax.set_ylim(min(-3.0, lo - 0.3), 0.8)
    ax.set_ylabel("Work (J per kg of top mass)")
    ax.errorbar([], [], yerr=[], fmt="o", ms=6, color=BLUE, mec=SURFACE, capsize=3.5,
                label=f"no peak: total work {MARGIN_MS:.0f} ms before the deformation jump")
    ax.errorbar([], [], yerr=[], fmt="D", ms=6.5, color=ORANGE, mec=SURFACE, capsize=3.5,
                label="peak near 40 ms")
    ax.plot([], [], "o", ms=3.5, color=MUTED, alpha=0.6, label="single drops")
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=INK2)
    ax.set_title("Mean work per specimen, drops 3 to 20, all 54 drop-tested specimens. "
                 "Bars: ±1 standard deviation", loc="left", color=INK, fontsize=11)
    style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_pareto(summ, png: Path) -> None:
    """Top row: the requested value (peak near 40 ms where there is one, the
    lift-off rule otherwise). Bottom row: the lift-off rule on every specimen."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 12), facecolor=SURFACE)
    rows_spec = (("work_J_per_kg", "", "Work as requested"),
                 (f"mean_{MARGIN_MS:.0f}ms_before_jump", "_liftoff_all",
                  f"One rule for all 54: work {MARGIN_MS:.0f} ms before the deformation jump"))
    cols_spec = (("T180", "T180, mean of drops 3 to 20", "lower"),
                 ("VLI", "Velocity loss index (VLI), mean of drops 3 to 20", "higher"))
    for r, (wkey, tag, rtitle) in enumerate(rows_spec):
        for c, (key, ylab, better) in enumerate(cols_spec):
            ax = axs[r, c]
            flag = f"front_work_{key}{tag}"
            for s in summ:
                peak = s["rule"] == "peak" and not tag
                on = s[flag]
                col = ORANGE if peak else BLUE
                xerr = s["sd_J_per_kg"] if not tag else None
                ax.errorbar(s[wkey], s[f"{key}_mean"], xerr=xerr, yerr=s[f"{key}_sd"],
                            fmt="none", ecolor=AXIS, elinewidth=0.9, zorder=1)
                ax.plot(s[wkey], s[f"{key}_mean"], MARK[s["batch"]], ms=8.5 if on else 6.5,
                        color=col, mfc=col if on else SURFACE, mew=1.4, zorder=3)
            f = sorted((s for s in summ if s[flag]), key=lambda s: s[wkey])
            ax.step([s[wkey] for s in f], [s[f"{key}_mean"] for s in f], where="post",
                    color=INK, lw=1.4, zorder=2)
            for i, s in enumerate(f):
                dy = (7 if key == "T180" else -13) if i % 2 == 0 else (-13 if key == "T180" else 7)
                ax.annotate(s["specimen_id"], (s[wkey], s[f"{key}_mean"]), xytext=(6, dy),
                            textcoords="offset points", color=INK, fontsize=9)
            ax.set_xlabel("Work (J per kg of top mass); more negative = more energy taken in")
            ax.set_ylabel(ylab)
            ax.set_title(f"{rtitle}\nagainst {key} ({better} is better). Front: black line, "
                         "filled markers", loc="left", color=INK, fontsize=10.5)
            style(ax)
    handles = [Line2D([], [], ls="none", marker=m, ms=7, mfc=SURFACE, mec=INK2, mew=1.3,
                      label=lab) for m, lab in MARK_LABEL.items()]
    handles += [Line2D([], [], ls="none", marker="o", ms=7, color=BLUE,
                       label=f"work {MARGIN_MS:.0f} ms before the deformation jump"),
                Line2D([], [], ls="none", marker="o", ms=7, color=ORANGE,
                       label="peak near 40 ms (top row only)"),
                Line2D([], [], color=INK, lw=1.4, label="Pareto front")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9.5,
               labelcolor=INK2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(png, dpi=140, facecolor=SURFACE)
    plt.close(fig)


def fig_grid(curves, summ, specs: list[str], png: Path, what: str) -> None:
    ss = [s for s in summ if s["specimen_id"] in specs]
    fig, axs = plt.subplots(len(ss) // 9, 9, figsize=(27, 3.0 * (len(ss) // 9) + 0.6),
                            facecolor=SURFACE, sharex=True, sharey=True, squeeze=False)
    for ax, s in zip(axs.flat, ss):
        spec = s["specimen_id"]
        for k in DROPS:
            tms, w, dmm, p, j = curves[(spec, k)]
            if what == "work":
                ax.plot(tms, w, color=BLUE, lw=0.8, alpha=0.35, zorder=2)
                if s["rule"] == "peak" and p["j"] is not None:
                    ax.plot(tms[p["j"]], w[p["j"]], "D", ms=3.5, color=ORANGE, mec=SURFACE,
                            mew=0.5, zorder=4)
                elif s["rule"] == "lift-off" and j is not None:
                    i = int(np.searchsorted(tms, tms[j] - MARGIN_MS))
                    ax.plot(tms[i], w[i], "o", ms=3.5, color=ORANGE, mec=SURFACE, mew=0.5,
                            zorder=4)
            else:
                ax.plot(tms, dmm, color=INK2, lw=0.8, alpha=0.35, zorder=2)
                if j is not None:
                    ax.plot(tms[j], dmm[j], "o", ms=3.5, color=ORANGE, mec=SURFACE,
                            mew=0.5, zorder=4)
        lab = (f"{s['work_J_per_kg']:+.2f} ± {s['sd_J_per_kg']:.2f} ({s['rule']})"
               if what == "work" else f"jump {s['jump_time_mean_ms']:.1f} ms")
        ax.set_title(f"{spec}: {lab}", loc="left", color=INK, fontsize=9)
        style(ax)
    if what == "work":
        axs[0, 0].set_xlim(0, 60)
        axs[0, 0].set_ylim(-4.5, 2.0)
        ylab = "Total work (J/kg)"
    else:
        axs[0, 0].set_xlim(0, 20)
        axs[0, 0].set_ylim(-8, 6)
        ylab = "Deformation (mm)"
    for ax in axs[:, 0]:
        ax.set_ylabel(ylab)
    for ax in axs[-1]:
        ax.set_xlabel("Time in record (ms)")
    fig.tight_layout()
    fig.savefig(png, dpi=110, facecolor=SURFACE)
    plt.close(fig)


def fig_lab_check(summ, png: Path) -> None:
    """T180 and VLI over drops 3 to 20 here against the campaign tables."""
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), facecolor=SURFACE)
    for ax, key in ((axs[0], "T180"), (axs[1], "VLI")):
        for s in summ:
            ax.plot(s[f"{key}_campaign"], s[f"{key}_mean"], MARK[s["batch"]], ms=6.5,
                    mfc=SURFACE, mec=BLUE if s["batch"] != "seed" else ORANGE, mew=1.3)
        lim = [min(min(s[f"{key}_campaign"], s[f"{key}_mean"]) for s in summ),
               max(max(s[f"{key}_campaign"], s[f"{key}_mean"]) for s in summ)]
        pad = 0.04 * (lim[1] - lim[0])
        lim = [lim[0] - pad, lim[1] + pad]
        ax.plot(lim, lim, color=AXIS, lw=1.0, zorder=0)
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_xlabel(f"{key}, campaign table (seed batch: all 101 drops)")
        ax.set_ylabel(f"{key}, this run (drops 3 to 20)")
        style(ax)
    axs[0].set_title("Lab metrics here against the campaign tables (orange: seed batch)",
                     loc="left", color=INK, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def main():
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    rows, curves = analyze(load_numaric_work(), lab_table())
    summ = summarize(rows, campaign_table())

    write_csv(HERE / "results" / "per_drop_work.csv", rows)
    write_csv(HERE / "results" / "work_summary.csv",
              [{"specimen_id": s["specimen_id"], "rule": s["rule"],
                "work_J_per_kg": s["work_J_per_kg"], "sd_J_per_kg": s["sd_J_per_kg"],
                "T180": s["T180_mean"], "VLI": s["VLI_mean"],
                "on_work_T180_front": s["front_work_T180"],
                "on_work_VLI_front": s["front_work_VLI"]} for s in summ], digits=3)
    write_csv(HERE / "results" / "specimen_details.csv", summ)

    fig_all(rows, summ, HERE / "figures" / "01_work_all_54_specimens.png")
    fig_pareto(summ, HERE / "figures" / "02_pareto_work_vs_t180_and_vli.png")
    new = BATCHES["seed"] + BATCHES["r2d2c"]
    fig_grid(curves, summ, new, HERE / "figures" / "03_work_curves_seed_r2d2c.png", "work")
    fig_grid(curves, summ, new, HERE / "figures" / "04_deformation_curves_seed_r2d2c.png",
             "deformation")
    fig_lab_check(summ, HERE / "figures" / "05_lab_metrics_vs_campaign_tables.png")

    for s in summ:
        print(f"{s['specimen_id']:7s} {s['rule']:8s} peak {s['n_with_peak']:2d}/18 "
              f"(corr {s['n_corrected']})  W {s['work_J_per_kg']:+.3f} ± {s['sd_J_per_kg']:.3f}"
              f"  1/2/3ms " + " ".join(f"{s[f'mean_{m:.0f}ms_before_jump']:+.3f}"
                                       for m in MARGINS)
              + f"  pk {s['mean_peak_if_any']:+.3f}  prom {s['max_prominence_J_per_kg']:.2f}"
              f"  jump {s['jump_time_mean_ms']:5.2f}  dmin {s['min_deformation_before_jump_mean_mm']:+.2f}"
              f"  T180 {s['T180_mean']:.4f}/{s['T180_campaign']:.4f}"
              f"  VLI {s['VLI_mean']:.4f}/{s['VLI_campaign']:.4f}"
              f"  front T {int(s['front_work_T180'])} V {int(s['front_work_VLI'])}"
              f" | liftoff-all T {int(s['front_work_T180_liftoff_all'])} V {int(s['front_work_VLI_liftoff_all'])}"
              f"  after-pulse {s['jump_after_pulse_end_ms']:+.1f} ms{' SPRINGBACK' if s['jump_is_springback'] else ''}")
    nojump = [r for r in rows if not np.isfinite(r["jump_time_ms"])]
    print(f"drops with no jump: {len(nojump)}")


if __name__ == "__main__":
    main()
