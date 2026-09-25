"""How many drops per specimen does the campaign actually need?

Replays the round-1 campaign as if each session had been stopped after the
first N drops, using the committed per-drop snapshot
``bo/t3-prism-per-drop-metrics.csv`` (extracted from ``campaign_metrics.json``
on the PR #86 branch ``copilot/add-drop-test-protocol-again``; the 2 warmup
drops per specimen are already discarded upstream, so drop_index 0 is the
first scored drop). For each N it reports the first-N mean of both objective
ingredients (t180 and the e_rebound fraction), the deviation from the full
~99-drop value, and the standard error at that N.

Outputs:

- ``bo/t3-prism-drop-count-sensitivity.csv``: the table, one row per
  (specimen, N) for N in {10, 20, 30, 50, full}.
- ``bo/figures/t3-prism-drop-count-sensitivity.png``: running first-N
  estimate vs N, one line per specimen, deviation from the full-campaign
  value, with guides at N = 20 and N = 50.
- ``--emit-truncated N``: a results CSV in the same schema as
  ``t3-prism-bo-batch-drop-results.csv`` but with n_valid, t180 and
  e_rebound statistics recomputed over the first N drops only. Feed it to
  ``t3_prism_bo_campaign.py --results ...`` so that when a shorter round-2
  session (say 20 drops) is ingested, round 1 is averaged over the same
  early-session window and both rounds estimate the same quantity. That
  matters because most specimens drift slightly over a session (t180
  typically falls by 0.002 to 0.013 from the first 20 drops to the last 20),
  so a first-N mean is a slightly different measurement than a full-session
  mean, not just a noisier one.

Findings from the round-1 replay (see the committed CSV for the numbers):
the t180 ranking of all 8 tested specimens is identical at N = 20, N = 50
and the full session; the worst first-20 t180 deviation is +0.008 (bag26v)
against design-to-design differences of 0.007 to 0.087. The e_rebound
fraction is the fragile one: mid-pack specimens sit 0.024 to 0.027 apart
and a first-20 estimate can be off by 20 percent (amdjwm), so short
sessions preserve the extremes but can shuffle the middle of that ranking.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BO_DIR = Path(__file__).resolve().parent
PER_DROP_CSV = BO_DIR / "t3-prism-per-drop-metrics.csv"
FULL_RESULTS_CSV = BO_DIR / "t3-prism-bo-batch-drop-results.csv"
OUT_CSV = BO_DIR / "t3-prism-drop-count-sensitivity.csv"
OUT_PNG = BO_DIR / "figures" / "t3-prism-drop-count-sensitivity.png"

N_GRID = (10, 20, 30, 50)


def first_n_stats(values: np.ndarray, n: int | None) -> tuple[int, float, float]:
    """(count, mean, sd) over the first n values (all values when n is None)."""
    v = values if n is None else values[:n]
    return len(v), float(np.mean(v)), float(np.std(v, ddof=1))


def build_table(per_drop: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sid, g in per_drop.groupby("specimen", sort=True):
        g = g.sort_values("drop_index")
        t = g["t180"].to_numpy(dtype=float)
        e = g["e_rebound"].to_numpy(dtype=float)
        _, t_full, _ = first_n_stats(t, None)
        _, e_full, _ = first_n_stats(e, None)
        for n in (*N_GRID, None):
            cnt, t_m, t_sd = first_n_stats(t, n)
            _, e_m, e_sd = first_n_stats(e, n)
            rows.append(
                {
                    "specimen": sid,
                    "n_drops": cnt,
                    "window": "full" if n is None else f"first-{n}",
                    "t180_mean": t_m,
                    "t180_sem": t_sd / np.sqrt(cnt),
                    "t180_dev_from_full": t_m - t_full,
                    "e_rebound_mean": e_m,
                    "e_rebound_sem": e_sd / np.sqrt(cnt),
                    "e_rebound_dev_pct": (e_m - e_full) / e_full * 100.0,
                }
            )
    return pd.DataFrame(rows)


def emit_truncated(per_drop: pd.DataFrame, n: int, out_path: Path) -> None:
    """Rewrite the campaign summary with statistics over the first n drops.

    Only the columns the BO ingestion reads (n_valid, t180_mean/sd,
    e_rebound_mean/sd) are recomputed; everything else (mass, spec mapping,
    geometry) is carried from the full-session summary unchanged.
    """
    full = pd.read_csv(FULL_RESULTS_CSV, dtype={"spec": "string"})
    full = full.set_index("specimen")
    for sid, g in per_drop.groupby("specimen", sort=True):
        g = g.sort_values("drop_index")
        cnt, t_m, t_sd = first_n_stats(g["t180"].to_numpy(dtype=float), n)
        _, e_m, e_sd = first_n_stats(g["e_rebound"].to_numpy(dtype=float), n)
        full.loc[sid, ["n_valid", "t180_mean", "t180_sd"]] = [cnt, t_m, t_sd]
        full.loc[sid, ["e_rebound_mean", "e_rebound_sd"]] = [e_m, e_sd]
    full.reset_index().to_csv(out_path, index=False)
    print(f"wrote {out_path} (round-1 summary over the first {n} drops)")


def render_figure(per_drop: pd.DataFrame, out_png: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from t3_prism_bo_campaign import FIG_RC, FIGURE_DPI, INK, LABEL_GRAY, FRONT_BLUE

    rc = dict(FIG_RC)
    rc.update({"font.size": 15, "axes.labelsize": 16,
               "xtick.labelsize": 14, "ytick.labelsize": 14})

    # One highlighted specimen per panel: the worst first-20 case, named in
    # ink; the rest stay gray and are identified by the label at line end.
    highlight = {"t180": "bag26v", "e_rebound": "amdjwm"}

    with plt.rc_context(rc):
        fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.6), dpi=FIGURE_DPI)
        panels = (
            ("t180", axes[0], "Shock transmissibility t180:\nfirst-N mean minus full-session mean", 1.0),
            ("e_rebound", axes[1], "Rebound fraction e_rebound:\nfirst-N mean vs full session (%)", 100.0),
        )
        for col, ax, title, scale in panels:
            for sid, g in per_drop.groupby("specimen", sort=True):
                g = g.sort_values("drop_index")
                v = g[col].to_numpy(dtype=float)
                full_mean = float(np.mean(v))
                ns = np.arange(5, len(v) + 1)
                run = np.cumsum(v)[4:] / ns
                dev = run - full_mean
                if scale != 1.0:
                    dev = dev / full_mean * scale
                hot = sid == highlight[col]
                ax.plot(
                    ns, dev,
                    color=FRONT_BLUE if hot else LABEL_GRAY,
                    lw=2.6 if hot else 1.4,
                    alpha=1.0 if hot else 0.75,
                    zorder=3 if hot else 2,
                )
                if hot:
                    ax.annotate(
                        sid, (ns[0], dev[0]), xytext=(4, 10),
                        textcoords="offset points", color=FRONT_BLUE,
                        fontsize=13,
                    )
            ax.axhline(0, color=INK, lw=1.0, alpha=0.35, zorder=1)
            for n_mark in (20, 50):
                ax.axvline(n_mark, color=LABEL_GRAY, lw=1.0, ls=(0, (4, 4)),
                           alpha=0.6, zorder=1)
                ax.annotate(f"N = {n_mark}", (n_mark, 1.0),
                            xycoords=("data", "axes fraction"),
                            xytext=(4, -2), textcoords="offset points",
                            color=LABEL_GRAY, fontsize=12, va="top")
            ax.set_title(title, fontsize=15, loc="left", pad=10)
            ax.set_xlabel("Drops used (first N of the session)")
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
        axes[0].set_ylim(-0.015, 0.015)
        axes[1].set_ylim(-25, 25)
        fig.tight_layout()
        out_png.parent.mkdir(exist_ok=True)
        fig.savefig(out_png, dpi=FIGURE_DPI, facecolor="white",
                    bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out_png}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--emit-truncated", type=int, metavar="N", default=None,
        help="also write t3-prism-bo-batch-drop-results-firstN.csv with "
        "round-1 statistics recomputed over the first N drops",
    )
    ap.add_argument("--no-figure", action="store_true")
    args = ap.parse_args(argv)

    per_drop = pd.read_csv(PER_DROP_CSV)
    table = build_table(per_drop)
    table.to_csv(OUT_CSV, index=False)
    print(f"wrote {OUT_CSV}")

    pd.set_option("display.width", 200)
    view = table[table["window"].isin(["first-20", "first-50", "full"])]
    print(view.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    if args.emit_truncated:
        n = args.emit_truncated
        emit_truncated(
            per_drop, n,
            BO_DIR / f"t3-prism-bo-batch-drop-results-first{n}.csv",
        )
    if not args.no_figure:
        render_figure(per_drop, OUT_PNG)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(BO_DIR))
    main()
