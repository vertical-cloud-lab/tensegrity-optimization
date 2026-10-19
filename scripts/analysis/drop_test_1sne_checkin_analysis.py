#!/usr/bin/env python3
"""1sne21..1sne83 check-in: plate 1 of the replicate study (PR #86, 10-19).

Nine 20-drop sessions recorded 10-17 by @ctrhjk (60 in, arrangement B =
1/2 in PU mat, current SOP capture settings) and posted as subfolders of
the standing public Box share.  The articles are **plate 1 of the
pre-registered replicate study** (PR #102,
``bo/t3-prism-replicate-study-plan.md``): three copies each of corny7
(trial 37, the 0.803 record), corny8 (trial 39, its near-twin) and corny2
(trial 38), labeled ``1sne[design digit][copy]`` (key: ``params.json``).

The standing campaign pipeline (``drop_test_campaign_analysis.py``) gives
the per-session metrics.  This script adds what the batch needed on top:

- the requested fifth-drop figures (``02``-``10``, the r2d2 figure);
- a census of all 180 captures (``capture_census.json``): the pipeline's
  plausibility screen, the per-drop seat gauge T1000/T180, the TP4 series
  table's own CH4/CH5 peaks, a CH5 baseline-step indicator, the
  top-sensor noise floor, and the velocity change seen by the top Z axis
  against CH5's (a sensor-gain check that a mount knock cannot fake,
  because momentum is conserved through a knock);
- ``12_capture_timeline.png``: the evening in capture order;
- ``13_fault_waveforms.png``: one capture of each kind;
- ``14_t180_vs_gauge.png``: T180 against the per-drop gauge, with the
  pooled within-session slope over the knocking sessions;
- ``15_replicate_interim.png`` + ``replicate_interim.json``: plate 1
  against the first articles and the frozen references, under three
  readings (all valid drops, low-gauge drops only, gauge-adjusted).

Usage:
    python scripts/analysis/drop_test_1sne_checkin_analysis.py --raw ROOT \\
        [--ref REF]
where ROOT holds one subfolder per session (``1sne21`` .. ``1sne83``) with
the ``*_Signal<k>.csv`` captures and the TP4 series table, and REF
(optional) holds the original ``corny2``/``corny7``/``corny8`` sessions
(Box ids in ``data/drop-tests/corny-checkin/raw/<id>/box-ids.json``) for
the waveform and sensor-gain comparison.  Run the campaign pipeline on
ROOT first; this script reads its ``campaign_metrics.json``.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA, GRAVITY  # noqa: E402
from drop_test_abc123_blind_analysis import (  # noqa: E402
    analyze_capture, cfc_filter, parse_capture)
from drop_test_campaign_analysis import find_captures, screen_reason  # noqa: E402
from drop_test_r2d2_checkin_analysis import DROP_NO, fifth_drop_figure  # noqa: E402
from drop_test_round3_per_design_comparison import GAUGE_HEALTHY, GAUGE_SUSPECT  # noqa: E402

OUT = DATA / "1sne-checkin"
FIG = OUT / "figures"
CORNY = DATA / "corny-checkin"

DESIGNS = ("corny7", "corny8", "corny2")          # replicate-plan order
DIGIT = {"7": "corny7", "8": "corny8", "2": "corny2"}
# categorical slots 1-3 (validated all-pairs, light surface); text stays in ink
COLOR = {"corny7": "#2a78d6", "corny8": "#eb6834", "corny2": "#1baf7a"}
MARK = {"1": "o", "2": "s", "3": "^"}             # copy digit = plate row
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
CH_COLOR = {"CH5": INK, "CH4": "#2a78d6", "CH2": "#eb6834", "CH3": "#1baf7a"}

# Frozen pre-registered references (PR #102 bo/t3-prism-replicate-study-
# picks.csv, frozen 09-23): measured first article, round-5 LOGO-CV held-out
# model, frozen round-4 acquisition model (mean, 1 sd).
REFS = {
    "first article": {"corny7": (0.8031, None), "corny8": (0.9535, None),
                      "corny2": (1.0846, None)},
    "held-out model (LOGO-CV)": {"corny7": (0.9784, 0.0852), "corny8": (0.9722, 0.1343),
                                 "corny2": (1.0501, 0.0705)},
    "frozen round-4 model": {"corny7": (0.9344, 0.1311), "corny8": (0.9535, 0.1529),
                             "corny2": (1.0077, 0.1471)},
}
ARTICLE_SD_ROUND3 = (0.0087, 10)   # screened article+seat sd, dof (dran3 checkin)
GAP_REPRODUCES, GAP_COLLAPSES = 0.10, 0.05   # pre-registered decision rule
GAUGE_REF = 1.03   # median gauge of this batch's healthy (corny2) sessions
LIVE_KNOCK_RATIO = 2.0   # TP4 CH4 peak / CH5 peak above this: knocking seat


# --------------------------------------------------------------------------
# capture census
# --------------------------------------------------------------------------
def series_table(folder: Path) -> dict[int, dict]:
    """TP4 series-table rows by event number (local event time, raw peaks)."""
    tab = next(p for p in folder.glob("*.csv") if "Signal" not in p.name)
    rows = {}
    for line in tab.read_text(encoding="latin-1").splitlines()[6:]:
        c = [x.strip() for x in line.split(",")]
        if len(c) > 15 and c[1].isdigit():
            rows[int(c[1])] = {
                "local_time": datetime.strptime(c[2], "%m/%d/%Y %I:%M:%S %p").isoformat(),
                "tp4_ch4_g": float(c[10]), "tp4_ch4_ms": float(c[11]),
                "tp4_ch5_g": float(c[13]), "tp4_ch5_ms": float(c[14]),
                "tp4_ch5_dv_in_s": float(c[15])}
    return rows


def census_capture(path: Path) -> dict:
    r = analyze_capture(path, baseline="tail")
    r["reason"] = screen_reason(r)
    t, ch, _ = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    tail = np.median(ch[int(0.070 / dt):], axis=0)
    x = ch - tail
    i = int(round(r["t_imp_ms"] * 1e-3 / dt))
    lo, hi = max(0, i - int(0.003 / dt)), min(len(t), i + int(0.015 / dt))
    dv = integrate.trapezoid(x[lo:hi] * GRAVITY, t[lo:hi], axis=0)
    r.update({
        "gauge": r["t1000"] / r["t180"] if r["t180"] > 0 else None,
        # velocity change over the impact (-3..+15 ms), top Z vs base CH5
        "dv_top_z_ms": float(dv[2]), "dv_top_lateral_ms": float(np.hypot(dv[0], dv[1])),
        "dv_ch5_ms": float(dv[3]),
        "dv_ratio_z": float(dv[2] / dv[3]) if dv[3] else None,
        # a step in CH5's baseline mid-record (intermittent connection)
        "ch5_offset_g": float(np.median(x[int(0.020 / dt):int(0.060 / dt), 3])),
        # white-noise floor of each channel over the last 10 ms
        "noise_floor_g": [float(v) for v in
                          np.diff(ch[int(0.090 / dt):], axis=0).std(0) / np.sqrt(2)],
    })
    r.pop("frac_fs", None)
    return r


def census(raw: Path, procs: int) -> list[dict]:
    jobs, meta = [], []
    with tempfile.TemporaryDirectory() as td:
        for folder in sorted(p for p in raw.iterdir() if p.is_dir()):
            tab = series_table(folder)
            for p in find_captures(folder, Path(td)):
                jobs.append(p)
                meta.append((folder.name.split()[0].lower(), tab))
        with Pool(procs) as pool:
            rows = pool.map(census_capture, jobs)
    out = []
    for r, (sess, tab) in zip(rows, meta):
        r["session"] = sess
        r["design"] = DIGIT[sess[4]]
        r.update(tab.get(r["signal"], {}))
        if "tp4_ch5_g" in r and r["tp4_ch5_g"]:
            r["tp4_ch4_over_ch5"] = abs(r["tp4_ch4_g"]) / abs(r["tp4_ch5_g"])
        out.append(r)
    out.sort(key=lambda r: r.get("local_time") or "")
    return out


def classify(r: dict) -> str:
    if r["reason"] is None:
        return "knock" if r["gauge"] >= GAUGE_SUSPECT else "valid"
    if r["t180"] < 0.5:      # whatever else is wrong, no impact reached the top
        return "mistimed"
    return "glitch" if "glitch" in r["reason"] else "bad input"


# --------------------------------------------------------------------------
# per-article readings
# --------------------------------------------------------------------------
def pooled_slope(sessions: dict) -> dict:
    """T180 vs per-drop gauge, session-demeaned, over the knocking sessions
    (>= 6 stabilized drops, median per-drop gauge at or above 1.145)."""
    xs, ys, used = [], [], []
    for s, rows in sessions.items():
        g = np.array([r["t1000"] / r["t180"] for r in rows])
        y = np.array([r["t180"] for r in rows])
        if len(rows) >= 6 and np.median(g) >= GAUGE_SUSPECT:
            xs.append(g - g.mean())
            ys.append(y - y.mean())
            used.append(s)
    x, y = np.concatenate(xs), np.concatenate(ys)
    b = float((x * y).sum() / (x * x).sum())
    dof = len(x) - 1 - len(used)
    se = float(np.sqrt(((y - b * x) ** 2).sum() / dof / (x * x).sum()))
    return {"slope_t180_per_gauge": b, "se": se, "t": b / se, "n_drops": int(len(x)),
            "sessions": used, "gauge_ref": GAUGE_REF}


def article_readings(rows: list[dict], slope: float) -> dict:
    t = np.array([r["t180"] for r in rows])
    g = np.array([r["t1000"] / r["t180"] for r in rows])
    low = g < GAUGE_SUSPECT
    adj = t - slope * np.maximum(g - GAUGE_REF, 0.0)
    return {
        "n": int(len(t)), "signals": [r["signal"] for r in rows],
        "t180_all": float(t.mean()), "t180_sd": float(t.std(ddof=1)) if len(t) > 1 else None,
        "gauge_session": float(np.mean([r["t1000"] for r in rows]) / t.mean()),
        "n_low_gauge": int(low.sum()),
        "t180_low_gauge": float(t[low].mean()) if low.any() else None,
        "t180_adjusted": float(adj.mean()),
        "gauge_min_drop": float(g.min()), "t180_at_min_gauge": float(t[np.argmin(g)]),
    }


def design_summary(arts: dict, key: str) -> dict:
    out = {}
    for d in DESIGNS:
        v = [a[key] for a in arts.values() if a["design"] == d and a.get(key) is not None]
        out[d] = {"n_articles": len(v), "mean": float(np.mean(v)) if v else None,
                  "sd": float(np.std(v, ddof=1)) if len(v) > 1 else None,
                  "values": [round(x, 4) for x in v]}
    m7, m8 = out["corny7"]["mean"], out["corny8"]["mean"]
    gap = None if m7 is None or m8 is None else m7 - m8
    order = sorted((d for d in DESIGNS if out[d]["mean"] is not None),
                   key=lambda d: out[d]["mean"])
    return {"designs": out, "gap_corny7_minus_corny8": gap, "ordering_low_to_high": order}


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def style(ax):
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#c3c2b7")
    ax.tick_params(colors=INK2, labelsize=8)


def fig_timeline(cen: list[dict], path: Path):
    idx = np.arange(len(cen))
    fig, axes = plt.subplots(3, 1, figsize=(13, 8.2), sharex=True,
                             gridspec_kw={"height_ratios": [2.2, 1.3, 1.3]})
    sess = [r["session"] for r in cen]
    spans, start = [], 0
    for k in range(1, len(sess) + 1):
        if k == len(sess) or sess[k] != sess[start]:
            spans.append((sess[start], start, k - 1))
            start = k
    for ax in axes:
        for j, (s, a, b) in enumerate(spans):
            if j % 2 == 0:
                ax.axvspan(a - 0.5, b + 0.5, color="#f0efec", lw=0, zorder=0)
        style(ax)
    for s, a, b in spans:
        r0 = cen[a]
        axes[0].text((a + b) / 2, 1.165, f"{s}\n{r0['local_time'][11:16]}", ha="center",
                     va="bottom", fontsize=7.5, color=INK2)

    ax = axes[0]
    for d in DESIGNS:
        for cls, face in (("valid", True), ("knock", False)):
            sel = [i for i, r in enumerate(cen) if r["design"] == d and classify(r) == cls]
            if sel:
                ax.scatter(idx[sel], [cen[i]["t180"] for i in sel], s=22, lw=1.1,
                           marker="o", color=COLOR[d] if face else "none",
                           edgecolors=COLOR[d], zorder=3,
                           label=f"{d} copies, {'gauge < 1.145' if face else 'knock drop (gauge >= 1.145)'}")
    bad = [i for i, r in enumerate(cen) if classify(r) in ("mistimed", "glitch", "bad input")]
    ax.scatter(idx[bad], np.full(len(bad), 0.775), marker="x", s=26, color=MUTED, lw=1.2,
               zorder=3, label=f"screened out ({len(bad)}): no usable impact in the record "
                               f"(plotted at the bottom, true T180 < 0.12)")
    for d, (v, _) in REFS["first article"].items():
        ax.axhline(v, color=COLOR[d], lw=0.9, ls=":", zorder=1)
        ax.text(len(cen) - 0.5, v + 0.003, f"{d} first article {v:.3f}", ha="right",
                fontsize=7, color=INK2)
    ax.set_ylim(0.755, 1.16)
    ax.set_ylabel("T180 = TOP/CH5 (CFC-180)", fontsize=9, color=INK)
    handles, labels = ax.get_legend_handles_labels()

    ax = axes[1]
    ok = [i for i, r in enumerate(cen) if r["reason"] is None]
    ax.scatter(idx[ok], [cen[i]["gauge"] for i in ok], s=14, color=INK2, zorder=3)
    ax.axhline(GAUGE_SUSPECT, color="#d03b3b", lw=0.9, ls="--")
    ax.text(0, 2.55, "advisory seat gauge 1.145 (dashed); healthy band 1.00-1.07 (green)",
            fontsize=7, color=INK2, ha="left")
    ax.axhspan(1.0, GAUGE_HEALTHY, color="#0ca30c", alpha=0.10, lw=0)
    ax.set_ylabel("per-drop seat gauge\nT1000/T180", fontsize=9, color=INK)
    ax.set_ylim(0.9, 2.8)

    ax = axes[2]
    off = np.array([r["ch5_offset_g"] for r in cen])
    ax.scatter(idx, np.clip(off, -150, 150), s=12, color=INK2, zorder=3)
    ax.set_ylim(-160, 160)
    ax.set_ylabel("CH5 baseline step\n20-60 ms (G, clipped)", fontsize=9, color=INK)
    ax.set_xlabel("capture, in recording order (10-17, local time at session start)",
                  fontsize=9, color=INK)
    fig.suptitle("1sne plate 1, 10-17: every capture in recording order", fontsize=11,
                 color=INK, y=0.995)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=7.5, frameon=False)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def load_window(path: Path, t0=0.0, t1=12.0):
    t, ch, _ = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    x = ch - np.median(ch[int(0.070 / dt):], axis=0)
    m = (t * 1e3 >= t0) & (t * 1e3 <= t1)
    return t[m] * 1e3, x[m]


def fig_waveforms(raw: Path, ref: Path | None, cen: list[dict], path: Path):
    by = {(r["session"], r["signal"]): r for r in cen}
    picks = [("1sne21", 5, "healthy seat (corny2 copy)"),
             ("1sne22", 10, "fault onset: first knock of the evening"),
             ("1sne71", 10, "mistimed: no impact in the record"),
             ("1sne23", 18, "electrical glitch on all three top axes"),
             ("1sne83", 16, "strongest knock (corny8 copy)"),
             ("1sne73", 17, "lowest-gauge corny7 copy drop")]
    fig, axes = plt.subplots(3, 2, figsize=(13, 9.5))
    for ax, (s, k, title) in zip(axes.ravel(), picks):
        p = next((raw / s).glob(f"*_Signal{k}.csv"))
        tm, x = load_window(p)
        for c, name in ((1, "CH3"), (0, "CH2"), (2, "CH4"), (3, "CH5")):
            ax.plot(tm, x[:, c], lw=0.8 if name != "CH5" else 1.1, color=CH_COLOR[name],
                    label={"CH5": "CH5 base (input)", "CH4": "CH4 top Z",
                           "CH2": "CH2 top X", "CH3": "CH3 top Y"}[name])
        r = by[(s, k)]
        note = (f"T180 {r['t180']:.3f}, gauge {r['gauge']:.2f}" if r["reason"] is None
                else f"screened: {r['reason']}")
        if s == "1sne73" and ref is not None and (ref / "corny7").is_dir():
            q = next((ref / "corny7").glob("*_Signal5.csv"))
            tq, xq = load_window(q)
            ax.plot(tq, xq[:, 3], lw=1.1, ls="--", color=CH_COLOR["CH5"],
                    label="CH5, original corny7 drop 5")
            ax.plot(tq, xq[:, 2], lw=1.1, ls="--", color=CH_COLOR["CH4"],
                    label="CH4, original corny7 drop 5 (T180 0.80)")
        ax.set_title(f"{s} drop {k}: {title}\n{note}", fontsize=8.5, color=INK, loc="left")
        style(ax)
        ax.set_ylabel("G", fontsize=8, color=INK2)
        lim = np.percentile(np.abs(x), 99.95)
        if lim > 1200:
            ax.set_ylim(-0.75 * lim, 1.05 * lim)
    axes[0, 0].legend(fontsize=7, frameon=False, loc="upper right")
    axes[2, 1].legend(fontsize=7, frameon=False, loc="upper right")
    for ax in axes[-1]:
        ax.set_xlabel("time in record (ms; trigger at 2 ms)", fontsize=8, color=INK2)
    fig.suptitle("One capture of each kind (raw, tail baseline, first 12 ms of the 100 ms record)",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_gauge(sessions: dict, slope: dict, path: Path):
    fig, ax = plt.subplots(figsize=(9.5, 6))
    style(ax)
    for s, rows in sessions.items():
        d = DIGIT[s[4]]
        g = np.array([r["t1000"] / r["t180"] for r in rows])
        y = np.array([r["t180"] for r in rows])
        ax.scatter(g, y, s=30, marker=MARK[s[5]], color=COLOR[d], edgecolors="white",
                   lw=0.6, zorder=3, label=f"{s} ({d}, copy {s[5]})")
        if s in slope["sessions"]:
            xx = np.linspace(g.min(), g.max(), 2)
            ax.plot(xx, y.mean() + slope["slope_t180_per_gauge"] * (xx - g.mean()),
                    color=COLOR[d], lw=1.0, alpha=0.8)
    ax.axvline(GAUGE_SUSPECT, color="#d03b3b", lw=0.9, ls="--")
    ax.axvspan(1.0, GAUGE_HEALTHY, color="#0ca30c", alpha=0.10, lw=0)
    ax.text(GAUGE_SUSPECT + 0.01, 0.865, "1.145 advisory\nseat gauge", fontsize=7.5,
            color="#d03b3b")
    ax.text(1.0, 1.104, "healthy band", fontsize=7.5, color=INK2)
    ax.text(1.95, 0.875, f"pooled within-session slope\n"
                         f"{slope['slope_t180_per_gauge']:+.3f} T180 per unit gauge "
                         f"(t = {slope['t']:.1f}, {slope['n_drops']} drops,\n"
                         f"{', '.join(slope['sessions'])})", fontsize=8, color=INK)
    for d in DESIGNS:
        v = REFS["first article"][d][0]
        ax.axhline(v, color=COLOR[d], ls=":", lw=0.9)
        ax.text(2.68, v - 0.009, f"{d} first article {v:.3f}", fontsize=7, color=INK2,
                ha="right")
    ax.set_xlabel("per-drop seat gauge T1000/T180", fontsize=9, color=INK)
    ax.set_ylabel("T180", fontsize=9, color=INK)
    ax.set_xlim(0.95, 2.7)
    ax.legend(fontsize=7, frameon=False, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.11))
    ax.set_title("Valid stabilized drops: a knocking seat reads high", fontsize=10,
                 color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_interim(arts: dict, first: dict, path: Path):
    fig, ax = plt.subplots(figsize=(10.5, 6))
    style(ax)
    for j, d in enumerate(DESIGNS):
        x0 = j * 1.0
        # frozen references, left of the design slot
        for k, (name, mk) in enumerate((("held-out model (LOGO-CV)", "s"),
                                        ("frozen round-4 model", "D"))):
            m, sd = REFS[name][d]
            ax.errorbar(x0 - 0.36 + 0.08 * k, m, yerr=sd, fmt=mk, ms=5, color=MUTED,
                        mfc="white", capsize=2, lw=0.9, zorder=2,
                        label=f"{name}, mean ± 1 sd" if j == 0 else None)
        ax.scatter(x0 - 0.14, first[d]["t180"], marker="*", s=150, color=INK, zorder=4,
                   label="first article (one print, one seat)" if j == 0 else None)
        ax.text(x0 - 0.14, first[d]["t180"] - 0.012, f"{first[d]['t180']:.3f}", ha="center",
                va="top", fontsize=7.5, color=INK)
        reps = sorted((s, a) for s, a in arts.items() if a["design"] == d)
        for i, (s, a) in enumerate(reps):
            xi = x0 + 0.06 + 0.11 * i
            healthy = a["gauge_session"] < GAUGE_SUSPECT
            ax.errorbar(xi, a["t180_all"], yerr=a["t180_sd"] or 0, fmt=MARK[s[5]], ms=7,
                        color=COLOR[d], mfc=COLOR[d] if healthy else "white",
                        mew=1.4, capsize=2, lw=1.0, zorder=3)
            ax.scatter(xi, a["t180_adjusted"], marker="_", s=140, color=INK, lw=1.4, zorder=4)
            ax.text(xi, max(a["t180_all"] + (a["t180_sd"] or 0), a["t180_adjusted"]) + 0.008,
                    f"{s}\nn={a['n']}", ha="center", fontsize=6.5, color=INK2)
    ax.scatter([], [], marker="o", color=INK2, label="plate-1 copy, all valid drops (± sd)")
    ax.scatter([], [], marker="o", color="none", edgecolors=INK2,
               label="hollow: session fails the 1.145 seat gauge")
    ax.scatter([], [], marker="_", s=140, color=INK, lw=1.4,
               label=f"gauge-adjusted to {GAUGE_REF} (pooled slope)")
    ax.set_xticks(range(len(DESIGNS)))
    ax.set_xticklabels([f"{d} (t{first[d]['spec'][1:]})" for d in DESIGNS], fontsize=9)
    ax.set_ylabel("T180", fontsize=9, color=INK)
    ax.set_xlim(-0.55, 2.55)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("Replicate study, plate 1 (interim): copies vs first articles and the "
                 "frozen references", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True,
                    help="root with one subfolder per 1sne session")
    ap.add_argument("--ref", type=Path, default=None,
                    help="optional root with the original corny2/7/8 sessions")
    ap.add_argument("--out", type=Path, default=FIG)
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    # -- fifth-drop figures (02..10), the standing check-in format ---------
    for i, folder in enumerate(sorted(p for p in args.raw.iterdir() if p.is_dir())):
        specimen = folder.name.split()[0].lower()
        hit = sorted(folder.rglob(f"*Signal{DROP_NO}.csv"))
        m = fifth_drop_figure(hit[0], specimen, args.out / f"{i + 2:02d}_{specimen}_drop5.png")
        print(f"{specimen} drop {DROP_NO}: T180 {m['t180']:.4f}  in {m['in_180_g']:.1f} G  "
              f"out {m['out_180_g']:.1f} G  [{screen_reason(m) or 'valid'}]")

    # -- census --------------------------------------------------------------
    cen = census(args.raw, args.procs)
    kinds = {}
    for r in cen:
        kinds.setdefault(classify(r), []).append(f"{r['session']}:S{r['signal']}")
    print({k: len(v) for k, v in kinds.items()})
    valid = [r for r in cen if r["reason"] is None]
    dev = [100 * (r["in_raw_g"] / abs(r["tp4_ch5_g"]) - 1) for r in valid if r.get("tp4_ch5_g")]
    bad = [r for r in cen if r["reason"] and r["reason"].startswith("no top-vertex")]
    nf = np.array([r["noise_floor_g"] for r in cen])
    nf_bad = np.array([r["noise_floor_g"] for r in bad])
    live = [r for r in valid if "tp4_ch4_over_ch5" in r]
    flag = np.array([r["tp4_ch4_over_ch5"] > LIVE_KNOCK_RATIO for r in live])
    knock = np.array([r["gauge"] >= GAUGE_SUSPECT for r in live])
    checks = {
        "n_captures": len(cen), "classes": {k: len(v) for k, v in kinds.items()},
        "screened": {k: v for k, v in kinds.items() if k not in ("valid", "knock")},
        "tp4_ch5_peak_agreement_valid_pct": {"median_abs": float(np.median(np.abs(dev))),
                                             "max_abs": float(np.max(np.abs(dev)))},
        "mistimed_tp4_ch4_peak_g_max": float(max(abs(r["tp4_ch4_g"]) for r in bad)),
        "mistimed_top_dv_ms_max": float(max(abs(r["dv_top_z_ms"]) for r in bad)),
        "noise_floor_g_all_median": [float(v) for v in np.median(nf, axis=0)],
        "noise_floor_g_mistimed_median": [float(v) for v in np.median(nf_bad, axis=0)],
        "live_knock_rule": {"rule": f"TP4 CH4 peak > {LIVE_KNOCK_RATIO} x CH5 peak",
                            "knock_drops": int(knock.sum()),
                            "caught": int((flag & knock).sum()),
                            "false_flags": int((flag & ~knock).sum()),
                            "non_knock_drops": int((~knock).sum())},
    }

    # -- per-article readings from the pipeline's stabilized rows ---------
    cm = json.loads((OUT / "figures" / "campaign_metrics.json").read_text())
    sessions = {s: v["rows"] for s, v in cm["specimens"].items()}
    slope = pooled_slope(sessions)
    params = json.loads((OUT / "params.json").read_text())
    arts = {}
    for s, v in cm["specimens"].items():
        a = article_readings(v["rows"], slope["slope_t180_per_gauge"])
        a.update({"design": params[s]["design"], "spec": params[s]["spec"],
                  "mass_g": params[s]["mass_g"], "plate_pos": params[s]["plate_pos"],
                  "n_captures": v["n_captures"], "n_valid": v["n_valid"],
                  "screened": v["screened"], "t_drift_watch": v["t_drift_watch"],
                  "passes_gauge_screen": a["gauge_session"] < GAUGE_SUSPECT,
                  "dv_ratio_z": float(np.median([r["dv_ratio_z"] for r in cen
                                                 if r["session"] == s and r["reason"] is None])),
                  "dv_top_lateral_ms": float(np.median([r["dv_top_lateral_ms"] for r in cen
                                                        if r["session"] == s and r["reason"] is None]))})
        # rebound energy as the BO loader builds it (PR #102): e_rebound * m * g * h
        a["e_reb_mJ"] = float(v["metrics"]["e_rebound"]["mean"] * params[s]["mass_g"]
                              * GRAVITY * 60 * 0.0254)
        arts[s] = a

    first = {}
    for r in csv.DictReader(open(CORNY / "figures" / "campaign_summary.csv")):
        if r["specimen"] in DESIGNS:
            first[r["specimen"]] = {"t180": float(r["t180_mean"]),
                                    "gauge": float(r["t1000_mean"]) / float(r["t180_mean"]),
                                    "spec": json.loads((CORNY / "params.json").read_text())
                                    [r["specimen"]]["spec"],
                                    "mass_g": float(r["mass_g"])}
    if args.ref is not None:
        for d in DESIGNS:
            caps = [p for p in find_captures(args.ref / d, args.ref / d)
                    if int(p.stem.split("Signal")[1]) > 2]
            with Pool(args.procs) as pool:
                rr = pool.map(census_capture, caps)
            first[d]["raw_check"] = {
                "n": len(rr), "t180": float(np.mean([r["t180"] for r in rr])),
                "dv_ratio_z": float(np.median([r["dv_ratio_z"] for r in rr])),
                "knock_drops_gauge": int(sum(r["gauge"] >= GAUGE_SUSPECT for r in rr))}
    readings = {key: design_summary(arts, key)
                for key in ("t180_all", "t180_low_gauge", "t180_adjusted")}
    c2 = [arts[s]["t180_low_gauge"] for s in sorted(arts) if arts[s]["design"] == "corny2"]
    sd2 = float(np.std(c2, ddof=1))
    sd_r3, dof_r3 = ARTICLE_SD_ROUND3
    pooled_sd = float(np.sqrt((dof_r3 * sd_r3 ** 2 + 2 * sd2 ** 2) / (dof_r3 + 2)))
    endpoints = {
        "E1_article_sd_corny2_healthy_seats": {
            "values": [round(v, 4) for v in c2], "sd": sd2, "dof": 2,
            "pooled_with_round3": pooled_sd, "decision_threshold": 0.015},
        "E2_gap_corny7_minus_corny8": {
            k: readings[k]["gap_corny7_minus_corny8"] for k in readings},
        "E2_first_article_gap": first["corny7"]["t180"] - first["corny8"]["t180"],
        "E2_rule": {"reproduces_if_abs_gap_at_least": GAP_REPRODUCES,
                    "collapses_if_abs_gap_at_most": GAP_COLLAPSES},
        "E3_rebound": {
            "status": "not scoreable on plate 1: the hop detector sits at its 15 ms floor "
                      "or is multimodal on all six corny7/corny8 sessions (the knock ring "
                      "outlasts the 15 ms search start)",
            "corny2_e_reb_mJ": {s: round(arts[s]["e_reb_mJ"], 2) for s in sorted(arts)
                                if arts[s]["design"] == "corny2"},
            "corny2_first_article_e_reb_mJ": 9.22},
        "E4_ordering_low_to_high": {k: readings[k]["ordering_low_to_high"] for k in readings},
        "E4_reference_orderings": {
            name: sorted(DESIGNS, key=lambda d: REFS[name][d][0]) for name in REFS},
        "E5_regression_to_mean": "deferred to plates 2-3 (needs healthy corny7/corny8 seats)",
    }
    out = {"note": "INTERIM, plate 1 of 3. Every corny7/corny8 session fails the seat "
                   "gauge, so their values are not design values; see README.",
           "references": {k: {d: list(v) for d, v in r.items()} for k, r in REFS.items()},
           "first_articles": first, "pooled_gauge_slope": slope,
           "articles": arts, "readings": readings, "endpoints": endpoints,
           "census_checks": checks}
    (args.out / "replicate_interim.json").write_text(json.dumps(out, indent=1))
    (args.out / "capture_census.json").write_text(json.dumps(
        [{**{k: v for k, v in r.items() if k not in ("event_time",)},
          "class": classify(r)} for r in cen], indent=0))

    fig_timeline(cen, args.out / "12_capture_timeline.png")
    fig_waveforms(args.raw, args.ref, cen, args.out / "13_fault_waveforms.png")
    fig_gauge(sessions, slope, args.out / "14_t180_vs_gauge.png")
    fig_interim(arts, first, args.out / "15_replicate_interim.png")

    print(json.dumps(checks, indent=1))
    print(f"pooled slope {slope['slope_t180_per_gauge']:+.4f} ± {slope['se']:.4f} "
          f"(t {slope['t']:.1f}, n {slope['n_drops']})")
    for s, a in arts.items():
        print(f"{s} [{a['design']}]: n {a['n']:2d}  all {a['t180_all']:.4f}  "
              f"low-gauge {a['t180_low_gauge'] if a['t180_low_gauge'] is None else round(a['t180_low_gauge'], 4)} "
              f"(n {a['n_low_gauge']})  adjusted {a['t180_adjusted']:.4f}  "
              f"gauge {a['gauge_session']:.2f}  dv_ratio_z {a['dv_ratio_z']:.3f}  "
              f"lateral {a['dv_top_lateral_ms']:.2f} m/s")
    for k, rd in readings.items():
        print(k, {d: (None if v["mean"] is None else round(v["mean"], 4))
                  for d, v in rd["designs"].items()},
              "gap7-8", None if rd["gap_corny7_minus_corny8"] is None
              else round(rd["gap_corny7_minus_corny8"], 4), rd["ordering_low_to_high"])
    print("E1", endpoints["E1_article_sd_corny2_healthy_seats"])
    print(f"figures + json -> {args.out}")


if __name__ == "__main__":
    main()
