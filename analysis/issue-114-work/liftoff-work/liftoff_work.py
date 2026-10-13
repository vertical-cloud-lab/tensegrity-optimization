#!/usr/bin/env python3
"""Work done before lift-off for the specimens with no peak near 40 ms (issue #114).

Justin's request (2026-10-13): for the specimens with no significant negative
deformation and no peak to analyze, find an approximate (small) work. The
deformation graph should jump when the specimen lifts off the table, so take
the total work a few milliseconds before the deformation jumps in the positive
direction. Plot these values with the peak values of the well-behaved
specimens, and tabulate each specimen's work and standard deviation.

* Specimens without a peak: the 32 left out by the all-specimens run (commit
  ``1aff9ff``): corny1 to corny5, drran1 to drran9, 2dran1 to 2dran9 and dran31
  to dran39. corny6 to corny9 had a peak in every drop.
* Work: Justin's own ``numaric_work``, compiled unchanged from
  ``justin/implimatation_or_work_2026-10-06.py`` and called exactly as his
  loop calls it (CH4 top, CH5 bottom, G to m/s^2 with 9.81, m = 1, v0 = -5.46).
* Deformation: the running sum of his ``dx_top - dx_bottom``, worked out with
  the same trapezoids as his loop (v0 cancels). Positive is the top moving up
  relative to the base, so the specimen getting taller.
* Jump: the first time the deformation stands ``JUMP_MM`` above the lowest it
  has been so far. 0.25 mm is about one pixel in the drop videos, the smallest
  height change they can see.
* Work before lift-off: the total work ``MARGIN_MS`` (2 ms) before the jump.
  1 and 3 ms are kept as a sensitivity check.
* corny6 to corny9 keep their earlier value, Justin's peak
  ``max(work_z[1250:2250])``; the same lift-off rule is also run on them for
  comparison.
* Drops 3 to 20, as in Justin's loop. Standard deviations use n - 1.

Inputs: ``waveforms/<specimen>_waveforms_50kHz.csv`` from ``fetch_waveforms.py``.
Outputs go to ``results/`` and ``figures/``.
"""
from __future__ import annotations

import ast
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import scipy.integrate  # noqa: F401  (Justin's function uses sp.integrate)

HERE = Path(__file__).resolve().parent
JUSTIN = HERE / "justin" / "implimatation_or_work_2026-10-06.py"
BATCHES = {
    "corny": [f"corny{n}" for n in range(1, 10)],
    "drran": [f"drran{n}" for n in range(1, 10)],
    "2dran": [f"2dran{n}" for n in range(1, 10)],
    "dran3": [f"dran3{n}" for n in range(1, 10)],
}
SPECIMENS = [s for b in BATCHES.values() for s in b]
WELL = {"corny6", "corny7", "corny8", "corny9"}   # a peak in every drop (commit 1aff9ff)
DROPS = range(3, 21)        # Justin's loop: range(3, 21)
WIN = (1250, 2250)          # Justin's peak window, 25 to 45 ms at 50 kHz
JUMP_MM = 0.25              # deformation this far above its lowest so far = the jump
MARGIN_MS = 2.0             # "a few milliseconds before" the jump
MARGINS = (1.0, 2.0, 3.0)   # sensitivity check
V0 = -5.46                  # Justin's default; cancels in the deformation
G = 9.81

# chart chrome (same light palette as the all-specimens figures)
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"


def load_numaric_work():
    """Compile Justin's ``numaric_work`` from his file without running the rest of it."""
    tree = ast.parse(JUSTIN.read_text())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "numaric_work"]
    ns = {"np": np, "sp": sp}
    exec(compile(ast.Module(fn, type_ignores=[]), str(JUSTIN), "exec"), ns)
    return ns["numaric_work"]


def deformation(t: np.ndarray, a_top: np.ndarray, a_bottom: np.ndarray) -> np.ndarray:
    """Running sum of Justin's ``dx_top - dx_bottom``, in mm."""
    v_top = sp.integrate.cumulative_trapezoid(a_top, t, initial=0)
    v_bottom = sp.integrate.cumulative_trapezoid(a_bottom, t, initial=0)
    dt = np.diff(t)
    dx_top = dt * (0.5 * (v_top[1:] + v_top[:-1]) + V0)
    dx_bottom = dt * (0.5 * (v_bottom[1:] + v_bottom[:-1]) + V0)
    return 1e3 * np.concatenate([[0.0], np.cumsum(dx_top - dx_bottom)])


def find_jump(tms: np.ndarray, dmm: np.ndarray) -> int | None:
    """Index where the deformation first stands JUMP_MM above its lowest so far."""
    above = dmm - np.minimum.accumulate(dmm) >= JUMP_MM
    return int(np.argmax(above)) if above.any() else None


def analyze(numaric_work) -> tuple[list[dict], dict]:
    rows, curves = [], {}
    for spec in SPECIMENS:
        data = np.loadtxt(HERE / "waveforms" / f"{spec}_waveforms_50kHz.csv",
                          delimiter=",", skiprows=1)
        for k in DROPS:
            d = data[data[:, 0] == k]
            tms = d[:, 1]
            a_top, a_bottom = d[:, 4] * G, d[:, 5] * G
            # exactly as Justin's loop calls it
            work_z, _, _ = numaric_work(tms * 1e-3, a_top, a_bottom)
            dmm = deformation(tms * 1e-3, a_top, a_bottom)
            j = find_jump(tms, dmm)
            ipk = int(np.argmax(np.where(tms < 15.0, d[:, 5], -np.inf)))   # base pulse peak
            iend = ipk + int(np.argmax(d[ipk:, 5] < 0.05 * d[ipk, 5]))      # pulse over
            row = {"specimen_id": spec, "drop": k,
                   "group": "peak near 40 ms" if spec in WELL else "no peak",
                   "jump_time_ms": tms[j] if j is not None else np.nan,
                   "base_pulse_peak_ms": tms[ipk],
                   "base_pulse_end_ms": tms[iend],
                   "base_at_jump_pct_of_peak": (100 * d[j, 5] / d[ipk, 5]
                                                if j is not None else np.nan)}
            for m in MARGINS:
                i = int(np.searchsorted(tms, tms[j] - m)) if j is not None else None
                row[f"work_{m:.0f}ms_before_jump_J_per_kg"] = (work_z[i] if i is not None
                                                               else np.nan)
            row["eval_time_ms"] = tms[j] - MARGIN_MS if j is not None else np.nan
            row["deformation_at_eval_mm"] = (dmm[int(np.searchsorted(tms, tms[j] - MARGIN_MS))]
                                             if j is not None else np.nan)
            row["min_work_before_jump_J_per_kg"] = (work_z[:j + 1].min() if j is not None
                                                    else np.nan)
            row["justin_peak_25to45ms_J_per_kg"] = work_z[WIN[0]:WIN[1]].max()
            row["justin_peak_time_ms"] = tms[WIN[0] + int(np.argmax(work_z[WIN[0]:WIN[1]]))]
            rows.append(row)
            curves[(spec, k)] = (tms, work_z, dmm, d[:, 5], j)
    return rows, curves


def reported(r: dict) -> float:
    """The value Justin asked for: peak for corny6-9, work before lift-off otherwise."""
    return (r["justin_peak_25to45ms_J_per_kg"] if r["specimen_id"] in WELL
            else r[f"work_{MARGIN_MS:.0f}ms_before_jump_J_per_kg"])


def summarize(rows: list[dict]) -> list[dict]:
    out = []
    for spec in SPECIMENS:
        r = [x for x in rows if x["specimen_id"] == spec]
        ok = [x for x in r if np.isfinite(x["jump_time_ms"]) or spec in WELL]
        w = np.array([reported(x) for x in ok])
        s = {"specimen_id": spec, "n_drops": len(ok),
             "rule": "peak near 40 ms" if spec in WELL else f"{MARGIN_MS:.0f} ms before jump",
             "work_J_per_kg": w.mean(), "sd_J_per_kg": w.std(ddof=1)}
        for m in MARGINS:
            v = np.array([x[f"work_{m:.0f}ms_before_jump_J_per_kg"] for x in r])
            s[f"mean_{m:.0f}ms_before_jump"] = np.nanmean(v)
            s[f"sd_{m:.0f}ms_before_jump"] = np.nanstd(v, ddof=1)
        jt = np.array([x["jump_time_ms"] for x in r])
        s["jump_time_mean_ms"], s["jump_time_sd_ms"] = np.nanmean(jt), np.nanstd(jt, ddof=1)
        s["base_at_jump_pct_mean"] = np.nanmean([x["base_at_jump_pct_of_peak"] for x in r])
        s["base_pulse_end_mean_ms"] = np.mean([x["base_pulse_end_ms"] for x in r])
        s["min_work_before_jump_mean"] = np.nanmean([x["min_work_before_jump_J_per_kg"]
                                                     for x in r])
        s["justin_peak_mean"] = np.mean([x["justin_peak_25to45ms_J_per_kg"] for x in r])
        out.append(s)
    return out


def write_csv(path: Path, rows: list[dict], digits: int = 3) -> None:
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


def fig_all(rows, summ, png: Path) -> None:
    fig, ax = plt.subplots(figsize=(15, 5.6), facecolor=SURFACE)
    rng = np.random.default_rng(0)
    ax.axhline(0.0, color=AXIS, lw=1.0, zorder=1)
    x = np.arange(len(summ)) + np.repeat(np.arange(len(BATCHES)), 9) * 0.8
    for xi, s in zip(x, summ):
        spec = s["specimen_id"]
        well = spec in WELL
        w = [reported(r) for r in rows if r["specimen_id"] == spec
             and (np.isfinite(r["jump_time_ms"]) or well)]
        ax.plot(xi + rng.uniform(-0.18, 0.18, len(w)), w, "o", ms=2.8, color=MUTED,
                alpha=0.5, mew=0, zorder=2)
        ax.errorbar(xi, s["work_J_per_kg"], yerr=s["sd_J_per_kg"], fmt="D" if well else "o",
                    ms=7 if well else 6.5, color=ORANGE if well else BLUE, mec=SURFACE,
                    mew=1.2, elinewidth=1.6, capsize=4, capthick=1.6, zorder=3)
    for b, (name, specs) in enumerate(BATCHES.items()):
        xs = x[9 * b:9 * b + 9]
        ax.text(xs.mean(), 0.42, {"corny": "corny (round 4)", "drran": "drran (round 3)",
                                  "2dran": "2dran (round 3)", "dran3": "dran3 (round 3)"}[name],
                ha="center", va="bottom", color=INK2, fontsize=9.5)
    ax.set_xticks(x, [s["specimen_id"] for s in summ], rotation=60, ha="right")
    ax.set_xlim(x[0] - 0.7, x[-1] + 0.7)
    ax.set_ylim(-3.0, 0.6)
    ax.set_ylabel("Work (J per kg of top mass)")
    ax.errorbar([], [], yerr=[], fmt="o", ms=6.5, color=BLUE, mec=SURFACE, capsize=4,
                label=f"no peak: total work {MARGIN_MS:.0f} ms before the deformation jump "
                      "(this run)")
    ax.errorbar([], [], yerr=[], fmt="D", ms=7, color=ORANGE, mec=SURFACE, capsize=4,
                label="peak near 40 ms: corny6 to corny9 (earlier run, 1aff9ff)")
    ax.plot([], [], "o", ms=3.5, color=MUTED, alpha=0.6, label="single drops")
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=INK2)
    ax.set_title("Mean work per specimen, drops 3 to 20. Bars: ±1 standard deviation",
                 loc="left", color=INK, fontsize=11)
    style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_method(curves, png: Path) -> None:
    """How the jump and the cutoff are picked, on four example drops."""
    ex = [("corny1", 10), ("corny5", 10), ("drran8", 10), ("corny7", 11)]
    fig, axs = plt.subplots(2, len(ex), figsize=(4.2 * len(ex), 6.4), facecolor=SURFACE,
                            sharex=True, sharey="row")
    for c, (spec, k) in enumerate(ex):
        tms, w, dmm, base, j = curves[(spec, k)]
        i = int(np.searchsorted(tms, tms[j] - MARGIN_MS))
        for ax in axs[:, c]:
            on = base > 0.05 * base.max()
            ax.fill_between(tms, 0, 1, where=on & (tms < 15), transform=ax.get_xaxis_transform(),
                            color=GRID, alpha=0.7, lw=0, zorder=0)
            ax.axvline(tms[j], color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=2)
            ax.axvline(tms[i], color=BLUE, lw=1.2, zorder=2)
        axs[0, c].plot(tms, dmm, color=INK, lw=1.4, zorder=3)
        axs[0, c].plot(tms[j], dmm[j], "o", ms=6, color=INK2, mec=SURFACE, zorder=4)
        axs[1, c].plot(tms, w, color=INK, lw=1.4, zorder=3)
        axs[1, c].plot(tms[i], w[i], "o", ms=8, color=BLUE, mec=SURFACE, mew=1.2, zorder=4)
        axs[1, c].annotate(f"{w[i]:+.2f} J/kg", (tms[i], w[i]),
                           xytext=(6, 8) if w[i] < -3 else (6, -14),
                           textcoords="offset points", color=INK, fontsize=9)
        axs[0, c].set_title(f"{spec} drop {k}" + ("  (has a peak)" if spec in WELL else ""),
                            loc="left", color=INK, fontsize=10.5)
        axs[0, c].text(tms[j] + 0.3, 3.3, f"jump {tms[j]:.1f} ms", color=INK2, fontsize=8.5)
        axs[1, c].set_xlabel("Time in record (ms)")
    axs[0, 0].set_ylabel("Deformation (mm)\n(+ = specimen taller)")
    axs[1, 0].set_ylabel("Total work (J/kg)")
    axs[0, 0].set_ylim(-8, 4)
    axs[1, 0].set_ylim(-4.6, 1.0)
    axs[0, 0].set_xlim(0, 20)
    axs[0, 0].set_xticks([0, 5, 10, 15, 20])
    axs[0, 2].plot([], [], color=INK2, lw=1.0, ls=(0, (4, 3)),
                   label=f"jump: {JUMP_MM} mm above its lowest so far")
    axs[0, 2].plot([], [], color=BLUE, lw=1.2, label=f"{MARGIN_MS:.0f} ms before the jump")
    axs[0, 2].fill_between([], [], color=GRID, label="base-plate pulse (CH5 > 5% of peak)")
    axs[0, 2].legend(loc="lower right", frameon=False, fontsize=8, labelcolor=INK2)
    for ax in axs.flat:
        style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=140, facecolor=SURFACE)
    plt.close(fig)


def fig_grid(curves, summ, png: Path, what: str) -> None:
    specs = [s for s in summ if s["specimen_id"] not in WELL]
    fig, axs = plt.subplots(4, 8, figsize=(26, 12), facecolor=SURFACE, sharex=True,
                            sharey=True)
    for ax, s in zip(axs.flat, specs):
        spec = s["specimen_id"]
        for k in DROPS:
            tms, w, dmm, _, j = curves[(spec, k)]
            y = dmm if what == "deformation" else w
            ax.plot(tms, y, color=BLUE if what == "work" else INK2, lw=0.8, alpha=0.35,
                    zorder=2)
            if what == "work":
                i = int(np.searchsorted(tms, tms[j] - MARGIN_MS))
                ax.plot(tms[i], w[i], "o", ms=3.5, color=ORANGE, mec=SURFACE, mew=0.5,
                        zorder=4)
            else:
                ax.plot(tms[j], dmm[j], "o", ms=3.5, color=ORANGE, mec=SURFACE, mew=0.5,
                        zorder=4)
        label = (f"{s['work_J_per_kg']:+.2f} ± {s['sd_J_per_kg']:.2f} J/kg" if what == "work"
                 else f"jump {s['jump_time_mean_ms']:.1f} ± {s['jump_time_sd_ms']:.1f} ms")
        ax.set_title(f"{spec}: {label}", loc="left", color=INK, fontsize=9.5)
        style(ax)
    axs[0, 0].set_xlim(0, 15)
    axs[0, 0].set_xticks([0, 5, 10, 15])
    if what == "work":
        axs[0, 0].set_ylim(-2.0, 1.3)
        ylab, mark = "Total work (J/kg)", f"work {MARGIN_MS:.0f} ms before the jump"
    else:
        axs[0, 0].set_ylim(-1.5, 3.0)
        ylab, mark = "Deformation (mm)", f"jump ({JUMP_MM} mm above lowest so far)"
    for ax in axs[:, 0]:
        ax.set_ylabel(ylab)
    for ax in axs[-1]:
        ax.set_xlabel("Time in record (ms)")
    axs[0, 0].plot([], [], color=BLUE if what == "work" else INK2, lw=1.5,
                   label="one line per drop (3 to 20)")
    axs[0, 0].plot([], [], "o", color=ORANGE, ms=5, label=mark)
    axs[0, 0].legend(loc="upper left", frameon=False, fontsize=8, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(png, dpi=110, facecolor=SURFACE)
    plt.close(fig)


def fig_margin(summ, png: Path) -> None:
    specs = [s for s in summ if s["specimen_id"] not in WELL]
    fig, ax = plt.subplots(figsize=(13, 4.6), facecolor=SURFACE)
    ax.axhline(0.0, color=AXIS, lw=1.0)
    x = np.arange(len(specs))
    shades = {1.0: "#86b6ef", 2.0: BLUE, 3.0: "#104281"}
    for m, dx, mk in zip(MARGINS, (-0.22, 0.0, 0.22), ("v", "o", "^")):
        ax.plot(x + dx, [s[f"mean_{m:.0f}ms_before_jump"] for s in specs], mk, ms=6,
                color=shades[m], mec=SURFACE, mew=0.8, ls="none",
                label=f"{m:.0f} ms before the jump" + ("  (reported)" if m == MARGIN_MS else ""))
    ax.set_xticks(x, [s["specimen_id"] for s in specs], rotation=60, ha="right")
    ax.set_ylabel("Mean total work (J/kg)")
    ax.legend(loc="lower left", frameon=False, fontsize=9, labelcolor=INK2)
    ax.set_title("How much the cutoff matters: mean work 1, 2 and 3 ms before the jump",
                 loc="left", color=INK, fontsize=11)
    style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def main():
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    rows, curves = analyze(load_numaric_work())
    summ = summarize(rows)

    write_csv(HERE / "results" / "per_drop_liftoff_work.csv", rows, digits=4)
    write_csv(HERE / "results" / "work_summary.csv",
              [{"specimen_id": s["specimen_id"], "work_J_per_kg": s["work_J_per_kg"],
                "sd_J_per_kg": s["sd_J_per_kg"], "rule": s["rule"]} for s in summ])
    write_csv(HERE / "results" / "specimen_details.csv", summ)

    fig_all(rows, summ, HERE / "figures" / "01_work_all_36_specimens.png")
    fig_method(curves, HERE / "figures" / "02_how_the_cutoff_is_picked.png")
    fig_grid(curves, summ, HERE / "figures" / "03_work_curves_32_specimens.png", "work")
    fig_grid(curves, summ, HERE / "figures" / "04_deformation_curves_32_specimens.png",
             "deformation")
    fig_margin(summ, HERE / "figures" / "05_cutoff_sensitivity.png")

    for s in summ:
        print(f"{s['specimen_id']:7s} n={s['n_drops']:2d} {s['rule']:17s} "
              f"{s['work_J_per_kg']:+.3f} ± {s['sd_J_per_kg']:.3f}   jump "
              f"{s['jump_time_mean_ms']:.2f} ± {s['jump_time_sd_ms']:.2f} ms  base at jump "
              f"{s['base_at_jump_pct_mean']:.0f}%  pulse end {s['base_pulse_end_mean_ms']:.2f}"
              f"   1/2/3 ms: "
              + " ".join(f"{s[f'mean_{m:.0f}ms_before_jump']:+.3f}" for m in MARGINS)
              + f"   min before jump {s['min_work_before_jump_mean']:+.3f}"
              f"   Justin peak {s['justin_peak_mean']:+.3f}")
    nojump = [r for r in rows if not np.isfinite(r["jump_time_ms"])]
    print(f"drops with no jump: {len(nojump)}")


if __name__ == "__main__":
    main()
