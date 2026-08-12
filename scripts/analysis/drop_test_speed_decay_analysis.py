#!/usr/bin/env python3
"""Drop Speed Decay 2 + 3 — does impact velocity decay over 100 drops?

Follow-up to the guide-rod cleaning/greasing A/B (08-10, ``Drop Speed
Decay``): @me-madsen ran two longer campaigns at the same operating point
(60 in, arrangement B = 1/2 in PU sheet alone, specimen 2) to see whether
the detected end velocity trends with drop count:

* **session 2** (08-11, Box ``i2hpksf19h9w84bk26ed2n91tf7i4cnm``) —
  55 drops, interrupted by a 9.7 min pause after drop 39;
* **session 3** (08-12, Box ``cy7ijzs8cx4gkhic133z1zoaecwsl350``) —
  100 drops, uninterrupted, ~41 s cadence.

Capture format matches the abc123 campaign (4 channels, 1.25 MHz,
125,000 samples = 100 ms, 2 ms pre-trigger, 150 G trigger on CH5), so
per-drop metrics come from ``analyze_capture`` in
``drop_test_abc123_blind_analysis`` unchanged.

Velocity attribution follows the greasing analysis: ``in_dv_ms`` mixes
arrival + rebound, so a Delta-v trend is read against two witnesses —
``t_second_ms`` (ballistic specimen-hop delay, tracks arrival velocity,
blind to mat rebound state) and ``in_width_ms`` (input pulse FWHM,
tracks mat state, blind to arrival velocity). Estimated arrival speed is
calibrated against the healthy B2 reference exactly as before.

Raw data is not committed (~1.4 GB); fetch from Box into ``--raw``
(default ``data/drop-tests/speed-decay/raw``) as ``session2/`` and
``session3/`` — the folder README records the per-file Box IDs. Emits
``data/drop-tests/speed-decay/figures/speed_decay_metrics.json``,
consumed by ``docs/drop-test-speed-decay-analysis.md``.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_abc123_blind_analysis import analyze_capture  # noqa: E402
from drop_test_60in_5felts_analysis import DATA, GRAVITY  # noqa: E402

OUT = DATA / "speed-decay"
RAW_ROOT = OUT / "raw"
FIG = OUT / "figures"

SESSIONS = {  # name -> (subdir, filename prefix)
    "session2": ("session2", "data"),
    "session3": ("session3", "dropdata"),
}
PAUSE_S = 120.0  # an inter-drop gap larger than this marks an interruption

DROP_HEIGHT_M = 60 * 0.0254
V_FREEFALL = float(np.sqrt(2.0 * GRAVITY * DROP_HEIGHT_M))  # 5.468 m/s

# Matched B2 references (same arrangement, specimen, capture settings).
HEALTHY_B2_DV = (5.276, 5.347)      # abc123 healthy tower, 08-04
DAMAGED_B_DV = (4.269, 4.382)       # abc123 damaged tower, 08-05/06
GREASE_DV = {"pre": 4.439, "post": 4.679}   # 08-10 greasing A/B (5+5 drops)
GREASE_TSEC = {"pre": 18.01, "post": 18.94}
DV_TO_ARRIVAL = float(np.mean(HEALTHY_B2_DV) / V_FREEFALL)

TREND_KEYS = ("in_dv_ms", "t_second_ms", "in_width_ms", "in_180_g",
              "in_raw_g", "e_rebound", "t180")


def ols(rows, key):
    y = np.array([r[key] for r in rows], float)
    x = np.arange(len(y), dtype=float)
    sl, _, r, p, _ = stats.linregress(x, y)
    return {"mean": float(y.mean()), "sd": float(y.std(ddof=1)),
            "cv_pct": float(100 * y.std(ddof=1) / y.mean()),
            "slope_pct_per_drop": float(100 * sl / y.mean()),
            "end_to_end_pct": float(100 * sl * (len(y) - 1) / y.mean()),
            "p": float(p), "r2": float(r * r), "n": len(y)}


def welch(a_rows, b_rows, key):
    a = np.array([r[key] for r in a_rows], float)
    b = np.array([r[key] for r in b_rows], float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return {"a_mean": float(a.mean()), "b_mean": float(b.mean()),
            "change_pct": float(100 * (b.mean() - a.mean()) / a.mean()),
            "p": float(p)}


def arrival(dv_mean):
    v = dv_mean / DV_TO_ARRIVAL
    return {"v_ms": float(v), "frac_freefall": float(v / V_FREEFALL),
            "energy_frac": float((v / V_FREEFALL) ** 2),
            "equiv_height_in": float(60.0 * (v / V_FREEFALL) ** 2)}


def load_session(raw_root, subdir, prefix):
    d = raw_root / subdir
    files = sorted(d.glob(f"{prefix}_Signal*.csv"),
                   key=lambda p: int(p.stem.split("Signal")[1]))
    if not files:
        sys.exit(f"no {prefix}_Signal*.csv under {d} "
                 "(fetch from Box first — see the folder README)")
    rows = []
    for p in files:
        r = analyze_capture(p)
        rows.append(r)
        print(f"  S{r['signal']:3d} {r['event_time'][11:19]}  dv {r['in_dv_ms']:.3f} m/s  "
              f"in180 {r['in_180_g']:6.1f} G  w {r['in_width_ms']:.3f} ms  "
              f"t_sec {r.get('t_second_ms', float('nan')):6.2f} ms", flush=True)
    return rows


def pauses(rows):
    et = [datetime.fromisoformat(r["event_time"]) for r in rows]
    return [{"after_drop": i + 1, "gap_min": float((b - a).total_seconds() / 60)}
            for i, (a, b) in enumerate(zip(et[:-1], et[1:]))
            if (b - a).total_seconds() > PAUSE_S]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW_ROOT)
    args = ap.parse_args()

    sessions = {}
    for name, (subdir, prefix) in SESSIONS.items():
        print(f"== {name}")
        rows = load_session(args.raw, subdir, prefix)
        gaps = pauses(rows)
        seg = {"all": {k: ols(rows, k) for k in TREND_KEYS}}
        # split session 2 at its interruption to separate the settling
        # transient from the steady state
        if gaps:
            cut = gaps[0]["after_drop"]
            seg["pre_pause"] = {k: ols(rows[:cut], k) for k in TREND_KEYS}
            seg["post_pause"] = {k: ols(rows[cut:], k) for k in TREND_KEYS}
        sessions[name] = {"rows": rows, "pauses": gaps, "trends": seg,
                          "arrival": arrival(seg["all"]["in_dv_ms"]["mean"])}

    s2, s3 = sessions["session2"]["rows"], sessions["session3"]["rows"]
    out = {
        "sessions": {
            "session2": "Drop Speed Decay 2 (08-11-2026), 55 drops, pause after 39",
            "session3": "Drop Speed Decay 3 (08-12-2026), 100 drops uninterrupted",
        },
        "config": "60 in, arrangement B (1/2 in PU), specimen 2",
        "v_freefall_ms": V_FREEFALL,
        "dv_to_arrival_cal": DV_TO_ARRIVAL,
        "references": {"healthy_B2_dv": HEALTHY_B2_DV, "damaged_B_dv": DAMAGED_B_DV,
                       "grease_dv": GREASE_DV, "grease_t_second_ms": GREASE_TSEC},
        "cross_session": {k: welch(s2, s3, k)
                          for k in ("in_dv_ms", "t_second_ms", "in_width_ms",
                                    "e_rebound", "t180")},
        **{name: {k: v for k, v in d.items() if k != "rows"}
           for name, d in sessions.items()},
        "rows": {name: d["rows"] for name, d in sessions.items()},
    }
    FIG.mkdir(parents=True, exist_ok=True)
    with open(FIG / "speed_decay_metrics.json", "w") as fh:
        json.dump(out, fh, indent=1)

    for name, d in sessions.items():
        a = d["trends"]["all"]["in_dv_ms"]
        print(f"{name}: dv {a['mean']:.3f} m/s (CV {a['cv_pct']:.2f} %), "
              f"slope {a['slope_pct_per_drop']:+.4f} %/drop "
              f"(end-to-end {a['end_to_end_pct']:+.1f} %, p = {a['p']:.1e})")

    make_figures(sessions)
    print(f"figures + metrics under {FIG}")


def make_figures(sessions):
    s2, s3 = sessions["session2"]["rows"], sessions["session3"]["rows"]
    c2, c3 = "tab:red", "tab:blue"
    x2 = np.arange(1, len(s2) + 1)
    x3 = np.arange(1, len(s3) + 1) + len(s2) + 4   # visual gap between sessions
    gap2 = sessions["session2"]["pauses"]

    def series(rows, key):
        return np.array([r[key] for r in rows], float)

    def fitline(ax, x, y, color):
        sl, ic = np.polyfit(np.arange(len(y)), y, 1)
        ax.plot([x[0], x[-1]], [ic, ic + sl * (len(y) - 1)],
                "--", color=color, lw=1, alpha=0.8)

    # -- 01: the requested graph — Delta-v over drop number ----------------
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.axhspan(*HEALTHY_B2_DV, color="tab:green", alpha=0.15, lw=0)
    ax.text(1, np.mean(HEALTHY_B2_DV), "healthy tower, B2 (08-04: 5.28-5.35)",
            va="center", fontsize=8, color="tab:green")
    ax.axhspan(*DAMAGED_B_DV, color="0.6", alpha=0.25, lw=0)
    ax.text(1, np.mean(DAMAGED_B_DV), "damaged tower, B blocks (08-05/06: 4.27-4.38)",
            va="center", fontsize=8, color="0.4")
    for lvl, lab in ((GREASE_DV["pre"], "08-10 pre-grease (4.44)"),
                     (GREASE_DV["post"], "08-10 post-grease (4.68)")):
        ax.axhline(lvl, color="tab:orange", ls=":", lw=1)
        ax.text(len(s2) + len(s3) + 5, lvl, lab, va="bottom", ha="right",
                fontsize=7, color="tab:orange")
    ax.plot(x2, series(s2, "in_dv_ms"), "o-", ms=3, lw=0.8, color=c2,
            label="session 2 (08-11, 55 drops, interrupted)")
    ax.plot(x3, series(s3, "in_dv_ms"), "o-", ms=3, lw=0.8, color=c3,
            label="session 3 (08-12, 100 drops uninterrupted)")
    for g in gap2:
        ax.axvline(g["after_drop"] + 0.5, color=c2, ls="--", lw=1, alpha=0.6)
        ax.text(g["after_drop"] + 1, 4.42, f"{g['gap_min']:.0f} min pause",
                fontsize=7, color=c2, rotation=90, va="bottom")
    ax.axvline(len(s2) + 2.5, color="0.75", lw=1)
    ax.text(len(s2) + 2.5, 5.15, "overnight", fontsize=7, color="0.5",
            rotation=90, va="bottom", ha="center")
    cut = gap2[0]["after_drop"] if gap2 else len(s2)
    fitline(ax, x2[:cut], series(s2[:cut], "in_dv_ms"), c2)
    fitline(ax, x3, series(s3, "in_dv_ms"), c3)
    ax.set_xlabel("drop number (cumulative across the two sessions)")
    ax.set_ylabel("base-plate impact Δv (m/s)")
    ax.set_title("Impact Δv vs drop count — 60 in, arrangement B, specimen 2 (08-11 / 08-12)")
    ax.legend(loc="center left", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "01_dv_trend.png", dpi=150)
    plt.close(fig)

    # -- 02: witness channels — arrival (hop) vs mat (width, raw spike) ----
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    panels = [
        ("t_second_ms", "specimen-hop delay t_second (ms)",
         "Arrival-velocity witness (blind to mat rebound state)"),
        ("in_width_ms", "input pulse FWHM (ms)",
         "Mat-state witness: pulse width"),
        ("in_raw_g", "CH5 raw |peak| (G)",
         "Mat-state witness: unfiltered contact spike"),
    ]
    for ax, (key, ylab, title) in zip(axes, panels):
        ax.plot(x2, series(s2, key), "o-", ms=3, lw=0.8, color=c2,
                label="session 2 (08-11)")
        ax.plot(x3, series(s3, key), "o-", ms=3, lw=0.8, color=c3,
                label="session 3 (08-12)")
        for g in gap2:
            ax.axvline(g["after_drop"] + 0.5, color=c2, ls="--", lw=1, alpha=0.6)
        ax.axvline(len(s2) + 2.5, color="0.75", lw=1)
        ax.set_ylabel(ylab, fontsize=9)
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.25)
    axes[0].legend(fontsize=8)
    axes[-1].set_xlabel("drop number (cumulative across the two sessions)")
    fig.suptitle("Trend attribution — hop delay tracks arrival velocity; "
                 "width and raw spike track the mat", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "02_witness_channels.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
