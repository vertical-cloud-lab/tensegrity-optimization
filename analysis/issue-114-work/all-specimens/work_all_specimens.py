#!/usr/bin/env python3
"""Justin's peak work near 40 ms for every drop of every specimen (issue #114).

Justin's request (2026-10-06): run his updated code on every drop of every
specimen, take the peak of the total work near 40 ms, correct the peak finder
for any specimen where it misses, leave out trials or specimens with no such
peak, and report each specimen's mean and standard deviation.

Specimens: corny1 to corny9 (corny7's batch, round 4) and the 27 specimens
of round 3 dropped the same way (drran1 to drran9, 2dran1 to 2dran9, dran31
to dran39): 60 in onto the 1/2 in PU mat, 20 drops each, same four channels.

* The work curve is Justin's own ``numaric_work``, pulled unchanged out of
  ``justin/implimatation_or_work_2026-10-06.py`` (it is compiled from his file,
  not copied), called exactly as his loop calls it: CH4 as the top, CH5 as the
  bottom, G to m/s^2 with 9.81, and his defaults m = 1, g = 9.81, v0 = -5.46.
* His peak is ``max(work_z[1250:2250])``, the largest total work between 25 and
  45 ms. A pick only counts as a peak if it is a real local maximum: at least
  0.5 ms inside the window and standing at least ``MIN_PROM`` above the curve
  on both sides (``scipy.signal.peak_prominences``). Every peak on corny6 to
  corny9 stands 0.96 J/kg or more; the largest bump on any other specimen's
  curve is 0.54 J/kg, so ``MIN_PROM`` sits between the two.
* If a pick fails that test, the script looks for the most prominent peak
  between 15 and 70 ms instead and marks the drop "corrected". If there is
  none, the drop is marked "no peak" and left out of the averages.
* Drops 3 to 20, as in Justin's loop (drops 1 and 2 are the warm-up drops).
  Standard deviations use n - 1.

Inputs: ``waveforms/corny<n>_waveforms_50kHz.csv``, written by
``fetch_waveforms.py``. Outputs go to ``results/`` and ``figures/``.
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
from scipy import signal as sig

HERE = Path(__file__).resolve().parent
JUSTIN = HERE / "justin" / "implimatation_or_work_2026-10-06.py"
BATCHES = {
    "corny": [f"corny{n}" for n in range(1, 10)],
    "drran": [f"drran{n}" for n in range(1, 10)],
    "2dran": [f"2dran{n}" for n in range(1, 10)],
    "dran3": [f"dran3{n}" for n in range(1, 10)],
}
SPECIMENS = [s for b in BATCHES.values() for s in b]
DROPS = range(3, 21)        # Justin's loop: range(3, 21)
WIN = (1250, 2250)          # Justin's window, 25 to 45 ms at 50 kHz
EDGE = 25                   # 0.5 ms: a pick this close to a window edge is the edge
MIN_PROM = 0.75             # J/kg; peaks on corny6-9 stand 0.96 or more, other bumps 0.54 or less
FALLBACK_MS = (15.0, 70.0)  # where a corrected search looks
G = 9.81

# chart chrome (same light palette as the corny7 export figures)
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


def t180(tms: np.ndarray, ch: np.ndarray) -> float:
    """T180 by the corny7 export's recipe (matches the lab pipeline to 0.06 %)."""
    fs = 1e3 / float(np.median(np.diff(tms)))
    z = ch - np.median(ch[tms >= 70.0], axis=0)
    b, a = sig.butter(2, 300.0 / (fs / 2.0), btype="low")
    f = sig.filtfilt(b, a, z, axis=0)
    inp, out = np.abs(f[:, 3]), np.sqrt((f[:, :3] ** 2).sum(axis=1))
    i = int(np.argmax(np.where(tms < 15.0, inp, 0.0)))
    near = np.abs(tms - tms[i]) <= 5.0
    return float(out[near].max() / inp[near].max())


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


def analyze(numaric_work) -> tuple[list[dict], dict]:
    rows, curves = [], {}
    for spec in SPECIMENS:
        data = np.loadtxt(HERE / "waveforms" / f"{spec}_waveforms_50kHz.csv",
                          delimiter=",", skiprows=1)
        for k in range(1, 21):
            d = data[data[:, 0] == k]
            tms = d[:, 1]
            # exactly as Justin's loop calls it
            work_z, _, _ = numaric_work(tms * 1e-3, d[:, 4] * G, d[:, 5] * G)
            p = pick_peak(work_z, tms)
            vt = sp.integrate.trapezoid(d[tms <= 15.0, 4] * G, tms[tms <= 15.0] * 1e-3)
            vb = sp.integrate.trapezoid(d[tms <= 15.0, 5] * G, tms[tms <= 15.0] * 1e-3)
            rows.append({
                "specimen_id": spec, "drop": k, "warmup": k < DROPS.start,
                "status": p["status"],
                "peak_work_J_per_kg": work_z[p["j"]] if p["j"] is not None else np.nan,
                "peak_time_ms": tms[p["j"]] if p["j"] is not None else np.nan,
                "peak_prominence_J_per_kg": p["prom"],
                "justin_window_max_J_per_kg": p["justin_max"],
                "justin_window_max_time_ms": p["justin_t"],
                "first_impact_min_J_per_kg": work_z[tms < 25.0].min(),
                "dv_top_ch4_0to15ms_m_s": vt, "dv_base_ch5_0to15ms_m_s": vb,
                "T180": t180(tms, d[:, 2:6]),
            })
            curves[(spec, k)] = (tms, work_z, p)
    return rows, curves


def summarize(rows: list[dict]) -> list[dict]:
    out = []
    for spec in SPECIMENS:
        r = [x for x in rows if x["specimen_id"] == spec and not x["warmup"]]
        ok = [x for x in r if x["status"] != "no peak"]
        w = np.array([x["peak_work_J_per_kg"] for x in ok])
        tp = np.array([x["peak_time_ms"] for x in ok])
        t = np.array([x["T180"] for x in r])
        dvr = np.mean([x["dv_top_ch4_0to15ms_m_s"] / x["dv_base_ch5_0to15ms_m_s"] for x in r])
        out.append({
            "specimen_id": spec, "n_drops": len(r), "n_with_peak": len(ok),
            "n_corrected": sum(x["status"] == "corrected" for x in r),
            "mean_J_per_kg": w.mean() if len(w) > 1 else np.nan,
            "sd_J_per_kg": w.std(ddof=1) if len(w) > 1 else np.nan,
            "peak_time_mean_ms": tp.mean() if len(tp) else np.nan,
            "peak_time_sd_ms": tp.std(ddof=1) if len(tp) > 1 else np.nan,
            "first_impact_min_mean_J_per_kg": np.mean([x["first_impact_min_J_per_kg"] for x in r]),
            "dv_ratio_top_over_base": dvr,
            "justin_window_max_mean_J_per_kg": np.mean([x["justin_window_max_J_per_kg"] for x in r]),
            "T180_mean": t.mean(), "T180_sd": t.std(ddof=1),
        })
    return out


def write_csv(path: Path, rows: list[dict], fmt: dict) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if isinstance(v, float) and not np.isfinite(v)
                            else (f"{v:.{fmt[k]}f}" if k in fmt and isinstance(v, float) else v))
                        for k, v in r.items()})


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


def fig_mean_sd(rows, summ, png: Path) -> None:
    summ = [s for s in summ if s["specimen_id"] in BATCHES["corny"]]
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor=SURFACE)
    rng = np.random.default_rng(0)
    ax.axhline(0.0, color=AXIS, lw=1.0)
    for i, s in enumerate(summ, start=1):
        if np.isfinite(s["mean_J_per_kg"]):
            w = [x["peak_work_J_per_kg"] for x in rows
                 if x["specimen_id"] == s["specimen_id"] and not x["warmup"]
                 and x["status"] != "no peak"]
            ax.plot(i + rng.uniform(-0.12, 0.12, len(w)), w, "o", ms=3.5, color=MUTED,
                    alpha=0.55, mew=0, zorder=2)
            ax.errorbar(i, s["mean_J_per_kg"], yerr=s["sd_J_per_kg"], fmt="o", ms=8,
                        color=BLUE, mec=SURFACE, mew=1.5, elinewidth=2, capsize=8,
                        capthick=2, zorder=3)
            ax.text(i + 0.2, s["mean_J_per_kg"],
                    f"{s['mean_J_per_kg']:.2f} ± {s['sd_J_per_kg']:.2f}",
                    va="center", ha="left", color=INK, fontsize=9)
        else:
            ax.text(i, -0.25, "no peak:\nleft out", ha="center", va="top",
                    color=MUTED, fontsize=8.5)
    ax.set_xticks(range(1, len(summ) + 1), [s["specimen_id"] for s in summ])
    ax.set_xlim(0.4, len(summ) + 0.9)
    ax.set_ylim(-3.2, 0.3)
    ax.set_ylabel("Peak total work near 40 ms (J per kg of top mass)")
    ax.set_title("Mean peak work per specimen, drops 3 to 20. Bars: ±1 standard deviation; "
                 "gray dots: single drops", loc="left", color=INK, fontsize=10.5)
    style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_curves(curves, summ, png: Path, ncols: int = 3) -> None:
    nrows = -(-len(summ) // ncols)
    fig, axs = plt.subplots(nrows, ncols, figsize=(4.67 * ncols, 3.5 * nrows),
                            facecolor=SURFACE, sharex=True, squeeze=False)
    for ax, s in zip(axs.flat, summ):
        spec = s["specimen_id"]
        ax.axvspan(WIN[0] / 50, WIN[1] / 50, color=GRID, alpha=0.6, lw=0, zorder=0)
        for k in DROPS:
            tms, w, p = curves[(spec, k)]
            ax.plot(tms, w, color=BLUE, lw=0.8, alpha=0.35, zorder=2)
            if p["j"] is not None:
                ax.plot(tms[p["j"]], w[p["j"]], "o", ms=4, color=ORANGE, mec=SURFACE,
                        mew=0.6, zorder=4)
            else:
                ax.plot(p["justin_t"], p["justin_max"], "x", ms=4.5, color=INK2, mew=1.0,
                        zorder=4)
        note = (f"peak in {s['n_with_peak']} of {s['n_drops']} drops" if s["n_with_peak"]
                else "no peak in any drop")
        ax.set_title(f"{spec}  (T180 {s['T180_mean']:.3f}): {note}", loc="left",
                     color=INK, fontsize=10 if ncols <= 3 else 9)
        ax.set_xlim(0, 100)
        style(ax)
    for ax in axs[-1]:
        ax.set_xlabel("Time in record (ms)")
    for ax in axs[:, 0]:
        ax.set_ylabel("Total work (J/kg)")
    axs.flat[0].plot([], [], color=BLUE, lw=1.5, label="total work, one line per drop (3 to 20)")
    axs.flat[0].plot([], [], "o", color=ORANGE, ms=5, label="peak used")
    axs.flat[0].plot([], [], "x", color=INK2, ms=5, label="max of Justin's window, not a peak")
    axs.flat[0].fill_between([], [], color=GRID, label="Justin's window, 25 to 45 ms")
    axs.flat[0].legend(loc="upper left", frameon=False, fontsize=8, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(png, dpi=130, facecolor=SURFACE)
    plt.close(fig)


def fig_vs_t180(rows, summ, png: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.6), facecolor=SURFACE)
    for s in summ:
        if not np.isfinite(s["mean_J_per_kg"]):
            continue
        r = [x for x in rows if x["specimen_id"] == s["specimen_id"] and not x["warmup"]]
        ax.plot([x["T180"] for x in r], [x["peak_work_J_per_kg"] for x in r], "o", ms=3.5,
                color=MUTED, alpha=0.5, mew=0, zorder=2)
        ax.errorbar(s["T180_mean"], s["mean_J_per_kg"], xerr=s["T180_sd"],
                    yerr=s["sd_J_per_kg"], fmt="o", ms=8, color=BLUE, mec=SURFACE, mew=1.5,
                    elinewidth=1.5, capsize=5, capthick=1.5, zorder=3)
        ax.annotate(s["specimen_id"], (s["T180_mean"], s["mean_J_per_kg"]),
                    xytext=(8, 6), textcoords="offset points", color=INK, fontsize=9)
    ax.set_xlabel("T180, mean of drops 3 to 20 (lower attenuates more)")
    ax.set_ylabel("Peak total work near 40 ms (J/kg)")
    ax.set_title("Peak work against T180, the specimens with a peak", loc="left",
                 color=INK, fontsize=10.5)
    style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_prominence(rows, summ, png: Path) -> None:
    """Largest peak on each specimen's curves (15 to 70 ms) against T180."""
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=SURFACE)
    ax.axhline(MIN_PROM, color=ORANGE, lw=1.2, ls=(0, (4, 3)))
    ax.text(1.255, MIN_PROM + 0.03, f"cutoff {MIN_PROM} J/kg", ha="right", va="bottom",
            color=INK2, fontsize=9)
    for s in summ:
        r = [x for x in rows if x["specimen_id"] == s["specimen_id"] and not x["warmup"]]
        prom = [x["peak_prominence_J_per_kg"] for x in r]
        has = s["n_with_peak"] > 0
        ax.errorbar(s["T180_mean"], np.median(prom),
                    yerr=[[np.median(prom) - min(prom)], [max(prom) - np.median(prom)]],
                    fmt="o", ms=7 if has else 5.5, color=BLUE if has else MUTED,
                    mec=SURFACE, mew=1.0, elinewidth=1.2, capsize=3, zorder=3 if has else 2)
        if has or s["specimen_id"] in ("2dran8", "drran7", "dran35"):
            ax.annotate(s["specimen_id"], (s["T180_mean"], max(prom)), xytext=(4, 4),
                        textcoords="offset points", color=INK2, fontsize=8.5)
    ax.plot([], [], "o", color=BLUE, ms=7, label="peak in every drop: corny6 to corny9")
    ax.plot([], [], "o", color=MUTED, ms=5.5, label="no peak: the other 32 specimens")
    ax.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=INK2)
    ax.set_ylim(-0.05, 1.45)
    ax.set_xlabel("T180, mean of drops 3 to 20")
    ax.set_ylabel("Height of the peak (prominence, J/kg)")
    ax.set_title("Tallest peak on each specimen's work curve, drops 3 to 20 "
                 "(dot: median, bar: range)", loc="left", color=INK, fontsize=10.5)
    style(ax)
    fig.tight_layout()
    fig.savefig(png, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def main():
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    rows, curves = analyze(load_numaric_work())
    summ = summarize(rows)

    write_csv(HERE / "results" / "per_drop_peak_work.csv", rows,
              {"peak_work_J_per_kg": 4, "peak_time_ms": 2, "peak_prominence_J_per_kg": 4,
               "justin_window_max_J_per_kg": 4, "justin_window_max_time_ms": 2,
               "first_impact_min_J_per_kg": 4, "dv_top_ch4_0to15ms_m_s": 3,
               "dv_base_ch5_0to15ms_m_s": 3, "T180": 4})
    write_csv(HERE / "results" / "peak_work_summary.csv",
              [{"specimen_id": s["specimen_id"], "mean_J_per_kg": s["mean_J_per_kg"],
                "sd_J_per_kg": s["sd_J_per_kg"]} for s in summ
               if np.isfinite(s["mean_J_per_kg"])],
              {"mean_J_per_kg": 3, "sd_J_per_kg": 3})
    write_csv(HERE / "results" / "specimen_details.csv", summ,
              {k: 3 for k in summ[0] if k.endswith(("_kg", "_ms", "_base"))}
              | {"T180_mean": 4, "T180_sd": 4})

    fig_mean_sd(rows, summ, HERE / "figures" / "01_mean_peak_work_by_specimen.png")
    corny = [s for s in summ if s["specimen_id"] in BATCHES["corny"]]
    fig_curves(curves, corny, HERE / "figures" / "02_work_curves_corny.png")
    fig_vs_t180(rows, summ, HERE / "figures" / "03_peak_work_vs_t180.png")
    fig_prominence(rows, summ, HERE / "figures" / "04_peak_height_all_36_specimens.png")
    fig_curves(curves, [s for s in summ if s not in corny],
               HERE / "figures" / "05_work_curves_round3.png", ncols=9)

    for s in summ:
        print(f"{s['specimen_id']}: peak in {s['n_with_peak']}/{s['n_drops']} "
              f"(corrected {s['n_corrected']})  mean {s['mean_J_per_kg']:+.3f}  "
              f"sd {s['sd_J_per_kg']:.3f}  t_pk {s['peak_time_mean_ms']:.1f} ± "
              f"{s['peak_time_sd_ms']:.1f} ms  dip {s['first_impact_min_mean_J_per_kg']:+.2f}  "
              f"dv ratio {s['dv_ratio_top_over_base']:.3f}  Justin-window mean "
              f"{s['justin_window_max_mean_J_per_kg']:+.3f}  T180 {s['T180_mean']:.4f}")
    bad = [r for r in rows if not r["warmup"] and r["status"] == "no peak"]
    prom_ok = [r["peak_prominence_J_per_kg"] for r in rows
               if not r["warmup"] and r["status"] != "no peak"]
    print(f"drops with no peak: {len(bad)}; smallest prominence among peaks used "
          f"{min(prom_ok):.3f}; largest bump on a no-peak drop "
          f"{max(r['peak_prominence_J_per_kg'] for r in bad):.3f} J/kg")


if __name__ == "__main__":
    main()
