#!/usr/bin/env python3
"""Rail cleaning/greasing A/B — does impact velocity recover? (8-10-2026)

@me-madsen ran 10 drops on 2026-08-10 (Box folder
``m3jsyavz2h2c7ck8pe496j6x8utm8bll``, session ID "Drop Speed Decay"):
Signals 1-5 before cleaning and greasing the guide rods, Signals 6-10
after, with a 6.4 min pause between for the maintenance itself. All drops
at 60 in, arrangement B (1/2 in PU sheet alone), specimen 2 (small T3
prism with printing defects) — i.e. exactly the ``B2`` cell of the
abc123 blind crossover, which supplies matched references on both the
healthy tower (08-04: Delta-v 5.276-5.347 m/s) and the damaged tower
(08-05/06 B blocks: 4.27-4.38 m/s).

Capture format matches the abc123 campaign (4 channels, 1.25 MHz,
125,000 samples = 100 ms, 2 ms pre-trigger, 150 G trigger on CH5), so
the per-drop metrics are computed by importing ``analyze_capture`` from
``drop_test_abc123_blind_analysis`` unchanged — same windowed CH5 peak,
same pre-trigger-median baseline, same Delta-v integration, same
secondary-event (specimen hop) detection.

Velocity attribution uses two channels deliberately:

* ``in_dv_ms`` — base-plate Delta-v over the impact (arrival + rebound);
* ``t_second_ms`` — the ballistic specimen-hop delay, which scales with
  arrival velocity and is independent of the mat's rebound state.

A Delta-v change that the hop timing reproduces is an arrival-velocity
change (rails); a Delta-v change with flat hop timing is rebound-side
(mat state). Estimated arrival speed is calibrated against the healthy
B2 reference (dv/arrival = mean(5.276, 5.347)/5.468).

Raw data is not committed (~95 MB); fetch it from Box into ``--raw``
(default ``data/drop-tests/pre-post-grease/raw``) — the folder README
records the per-file Box IDs. Emits
``data/drop-tests/pre-post-grease/figures/pre_post_grease_metrics.json``,
consumed by ``docs/drop-test-pre-post-grease-analysis.md``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_abc123_blind_analysis import analyze_capture  # noqa: E402
from drop_test_60in_5felts_analysis import DATA, GRAVITY  # noqa: E402

OUT = DATA / "pre-post-grease"
RAW_ROOT = OUT / "raw"
FIG = OUT / "figures"

PREFIX = "pre-post-grease"
PRE = range(1, 6)
POST = range(6, 11)

DROP_HEIGHT_M = 60 * 0.0254
V_FREEFALL = float(np.sqrt(2.0 * GRAVITY * DROP_HEIGHT_M))  # 5.468 m/s

# Matched B2 references from the abc123 blind crossover (same arrangement,
# same specimen, same capture settings; abc123_metrics.json).
HEALTHY_B2_DV = (5.276, 5.347)   # set1 B2 (08-04), set2 blk1 = B2 (08-04)
DAMAGED_B_DV = (4.269, 4.382)    # set2 B3 / B1 blocks (08-05/06, specimens 3 and 1)
DV_TO_ARRIVAL = float(np.mean(HEALTHY_B2_DV) / V_FREEFALL)


def group(rows, sigs):
    return [r for r in rows if r["signal"] in sigs]


def gstats(rows, key):
    a = np.array([r[key] for r in rows], float)
    return {"mean": float(a.mean()), "sd": float(a.std(ddof=1)),
            "cv_pct": float(100 * a.std(ddof=1) / a.mean()),
            "values": [float(v) for v in a]}


def welch(pre, post, key):
    a = np.array([r[key] for r in pre], float)
    b = np.array([r[key] for r in post], float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return {"pre": gstats(pre, key), "post": gstats(post, key),
            "change_pct": float(100 * (b.mean() - a.mean()) / a.mean()),
            "welch_t": float(t), "p": float(p)}


def slope(rows, key):
    y = np.array([r[key] for r in rows], float)
    x = np.arange(len(y), dtype=float)
    sl, _, r, p, se = stats.linregress(x, y)
    return {"slope_per_drop": float(sl), "slope_pct_per_drop": float(100 * sl / y.mean()),
            "p": float(p), "r2": float(r * r)}


def arrival(dv_mean):
    v = dv_mean / DV_TO_ARRIVAL
    return {"v_ms": float(v), "frac_freefall": float(v / V_FREEFALL),
            "energy_frac": float((v / V_FREEFALL) ** 2),
            "equiv_height_in": float(60.0 * (v / V_FREEFALL) ** 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW_ROOT)
    args = ap.parse_args()

    files = sorted(args.raw.glob(f"{PREFIX}_Signal*.csv"),
                   key=lambda p: int(p.stem.split("Signal")[1]))
    if len(files) != 10:
        sys.exit(f"expected 10 captures under {args.raw}, found {len(files)} "
                 "(fetch from Box first — see the folder README)")
    rows = []
    for p in files:
        r = analyze_capture(p)
        rows.append(r)
        print(f"  S{r['signal']:2d} {r['event_time'][11:19]}  dv {r['in_dv_ms']:.3f} m/s  "
              f"in180 {r['in_180_g']:6.1f} G  w {r['in_width_ms']:.3f} ms  "
              f"t_sec {r.get('t_second_ms', float('nan')):6.2f} ms", flush=True)

    pre, post = group(rows, PRE), group(rows, POST)
    keys = ["in_dv_ms", "t_second_ms", "in_width_ms", "in_180_g", "in_raw_g",
            "t180", "e_rebound", "out_180_g"]
    comparison = {k: welch(pre, post, k) for k in keys}
    trends = {name: {k: slope(g, k) for k in ("in_dv_ms", "in_width_ms", "t_second_ms")}
              for name, g in (("pre", pre), ("post", post))}
    arrivals = {name: arrival(comparison["in_dv_ms"][name]["mean"])
                for name in ("pre", "post")}
    healthy = arrival(float(np.mean(HEALTHY_B2_DV)))

    dv = comparison["in_dv_ms"]
    deficit_pre = np.mean(HEALTHY_B2_DV) - dv["pre"]["mean"]
    recovered = (dv["post"]["mean"] - dv["pre"]["mean"]) / deficit_pre

    out = {
        "session": "Drop Speed Decay (08-10-2026), 60 in, arrangement B, specimen 2",
        "v_freefall_ms": V_FREEFALL,
        "dv_to_arrival_cal": DV_TO_ARRIVAL,
        "references": {"healthy_B2_dv": HEALTHY_B2_DV, "damaged_B_dv": DAMAGED_B_DV},
        "rows": rows,
        "comparison": comparison,
        "trends": trends,
        "arrival_estimates": {**arrivals, "healthy_B2": healthy},
        "deficit_recovered_frac": float(recovered),
    }
    FIG.mkdir(parents=True, exist_ok=True)
    with open(FIG / "pre_post_grease_metrics.json", "w") as fh:
        json.dump(out, fh, indent=1)

    print(f"\npre  dv {dv['pre']['mean']:.3f} +- {dv['pre']['sd']:.3f} m/s"
          f"  post dv {dv['post']['mean']:.3f} +- {dv['post']['sd']:.3f} m/s"
          f"  ({dv['change_pct']:+.2f} %, p = {dv['p']:.1e})")
    print(f"healthy B2 reference {np.mean(HEALTHY_B2_DV):.3f} m/s -> "
          f"{100 * recovered:.0f} % of the deficit recovered")

    make_figures(rows, pre, post)
    print(f"figures + metrics under {FIG}")


def make_figures(rows, pre, post):
    sig = [r["signal"] for r in rows]
    dv = [r["in_dv_ms"] for r in rows]
    tsec = [r["t_second_ms"] for r in rows]
    wid = [r["in_width_ms"] for r in rows]

    c_pre, c_post = "tab:red", "tab:blue"

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axhspan(*HEALTHY_B2_DV, color="tab:green", alpha=0.15, lw=0)
    ax.axhline(V_FREEFALL, color="tab:green", ls=":", lw=1)
    ax.text(10.4, V_FREEFALL, "free fall from 60 in (5.47)", va="bottom", fontsize=8, color="tab:green")
    ax.text(10.4, np.mean(HEALTHY_B2_DV), "healthy tower, B2\n(08-04: 5.28-5.35)",
            va="center", fontsize=8, color="tab:green")
    ax.axhspan(*DAMAGED_B_DV, color="0.6", alpha=0.25, lw=0)
    ax.text(10.4, np.mean(DAMAGED_B_DV), "damaged tower, B blocks\n(08-05/06: 4.27-4.38)",
            va="center", fontsize=8, color="0.4")
    ax.plot(sig[:5], dv[:5], "o-", color=c_pre, label="before cleaning/greasing")
    ax.plot(sig[5:], dv[5:], "o-", color=c_post, label="after cleaning/greasing")
    ax.axvline(5.5, color="0.7", ls="--", lw=1)
    ax.text(5.6, 5.05, "rails cleaned + greased\n(6.4 min pause)", fontsize=8, color="0.4")
    ax.set_xlabel("drop (signal)")
    ax.set_ylabel("base-plate impact Δv (m/s)")
    ax.set_title("Impact Δv before vs after guide-rod cleaning/greasing — 60 in, arrangement B, specimen 2")
    ax.set_xticks(sig)
    ax.set_xlim(0.5, 13.5)
    ax.legend(loc="center right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "01_dv_pre_post.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    ax = axes[0]
    ax.plot(sig[:5], tsec[:5], "o-", color=c_pre)
    ax.plot(sig[5:], tsec[5:], "o-", color=c_post)
    ax.axvline(5.5, color="0.7", ls="--", lw=1)
    ax.set_xlabel("drop (signal)")
    ax.set_ylabel("specimen-hop delay t_second (ms)")
    ax.set_title("Arrival-velocity witness: hop delay\n(+5.1 % step, flat within blocks)")
    ax.grid(alpha=0.25)
    ax = axes[1]
    ax.plot(sig[:5], wid[:5], "o-", color=c_pre, label="before")
    ax.plot(sig[5:], wid[5:], "o-", color=c_post, label="after")
    ax.axvline(5.5, color="0.7", ls="--", lw=1)
    ax.set_xlabel("drop (signal)")
    ax.set_ylabel("input pulse FWHM (ms)")
    ax.set_title("Mat-state witness: pulse width\n(monotone growth straight through the pause)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "02_witness_channels.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
