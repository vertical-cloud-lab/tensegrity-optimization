#!/usr/bin/env python3
"""Post-reset sensitivity/settings verification — bpx68c before vs after.

The TP4's channel settings were cleared and re-entered by hand on 08-18
(screenshot on PR #86). To verify the re-entered sensitivities, @me-madsen
re-ran the same specimen at the same operating point:

* **before** (Box ``it5499hkyw24twg7179smsn0fv0bodal``) — ``bpx68c``,
  60 in, arrangement B (1/2 in PU mat), 101 drops, recorded 08-17 with
  the original (pre-reset) settings;
* **after** (Box ``4tttcvt6lx008tr05meruslkwasqqskh``) — same specimen
  and operating point, 30 drops, recorded 08-19 with the re-entered
  settings ("calibration testing").

A mis-entered sensitivity is a *per-channel multiplicative* error
(G = volts / sensitivity), so the check compares, per channel:

* level metrics (windowed CFC-180 peak per axis, CH5 input peak, Δv) —
  scale with any sensitivity error but also with real session-to-session
  physics (mat state, tower state);
* **shape metrics** (pulse width, hop delay ``t_second``, ``e_rebound``)
  — invariant to channel scaling; they establish that the two sessions
  are physically comparable, so remaining level shifts bound the
  calibration error;
* **scale-cancelling ratios** (T = out/in, per-axis share of the
  resultant) — sensitive to *relative* channel-scale errors only;
* **pre-trigger noise floors** per channel — electronics noise is fixed
  in volts, so the reported noise in G scales inversely with the entered
  sensitivity, independent of drop physics.

Each observed after/before ratio is compared against the plausible
mis-entry candidates (axis-value swaps between CH2/CH3/CH4, CH5 entered
as 1.000 instead of 1.059 mV/G, a channel left at the 10 mV/G default).

Raw data is not committed (~1.2 GB); fetch from Box into ``--raw``
(default ``data/drop-tests/calibration-check/raw``) as ``before/`` and
``after/`` (``bpx68c_Signal*.csv``). Emits
``data/drop-tests/calibration-check/figures/calibration_check_metrics.json``,
consumed by ``docs/drop-test-calibration-check-analysis.md``.
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
from drop_test_abc123_blind_analysis import (  # noqa: E402
    CH5, PRETRIGGER_S, SEARCH_S, TOP_COLS, analyze_capture, cfc_filter,
    parse_capture, windowed_peak)
from drop_test_60in_5felts_analysis import DATA  # noqa: E402

OUT = DATA / "calibration-check"
RAW_ROOT = OUT / "raw"
FIG = OUT / "figures"

SESSIONS = {"before": "before", "after": "after"}  # name -> subdir

# Sensitivities as re-entered on the settings screen (mV/G). A wrong entry
# on channel c scales that channel's reported G by s_true / s_entered.
SENS = {"CH2": 0.690, "CH3": 0.667, "CH4": 0.734, "CH5": 1.059}
# Candidate mis-entries and the after/before level ratio each would produce.
CANDIDATES = [
    ("CH2<->CH3 values swapped", {"CH2": SENS["CH2"] / SENS["CH3"],
                                  "CH3": SENS["CH3"] / SENS["CH2"]}),
    ("CH2<->CH4 values swapped", {"CH2": SENS["CH2"] / SENS["CH4"],
                                  "CH4": SENS["CH4"] / SENS["CH2"]}),
    ("CH3<->CH4 values swapped", {"CH3": SENS["CH3"] / SENS["CH4"],
                                  "CH4": SENS["CH4"] / SENS["CH3"]}),
    ("CH5 entered as 1.000 mV/G", {"CH5": SENS["CH5"] / 1.000}),
    ("channel left at 10 mV/G default",
     {c: s / 10.0 for c, s in SENS.items()}),
]

LEVEL_KEYS = ("in_raw_g", "in_180_g", "in_dv_ms", "out_180_g",
              "ax_CH2_180_g", "ax_CH3_180_g", "ax_CH4_180_g")
SHAPE_KEYS = ("in_width_ms", "t_second_ms", "e_rebound", "t_imp_ms")
RATIO_KEYS = ("t180", "share_CH2", "share_CH3", "share_CH4")
NOISE_KEYS = ("noise_CH2_g", "noise_CH3_g", "noise_CH4_g", "noise_CH5_g")


def analyze(path: Path) -> dict:
    """abc123 per-capture metrics + per-axis peaks and noise floors."""
    row = analyze_capture(path)
    t, ch, _ = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(PRETRIGGER_S / dt))
    ns = int(SEARCH_S / dt)

    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])
    i_imp = int(np.argmax(np.abs(cfc_filter(ch5, fs, 180)[:ns])))

    axes = {}
    for name, col in zip(("CH2", "CH3", "CH4"), TOP_COLS):
        x = ch[:, col] - np.median(ch[:nb, col])
        pk = windowed_peak(t, cfc_filter(x, fs, 180), i_imp, dt)
        row[f"ax_{name}_180_g"] = pk["peak_abs_g"]
        axes[name] = pk["peak_abs_g"]
        row[f"noise_{name}_g"] = float(x[:nb].std())
    row["noise_CH5_g"] = float(ch5[:nb].std())
    res = float(np.sqrt(sum(v ** 2 for v in axes.values())))
    for name in axes:
        row[f"share_{name}"] = axes[name] / res
    return row


def load_session(raw_root: Path, subdir: str) -> list[dict]:
    d = raw_root / subdir
    files = sorted(d.glob("bpx68c_Signal*.csv"),
                   key=lambda p: int(p.stem.split("Signal")[1]))
    if not files:
        sys.exit(f"no bpx68c_Signal*.csv under {d} "
                 "(fetch from Box first — see the folder README)")
    rows = []
    for p in files:
        r = analyze(p)
        rows.append(r)
        print(f"  S{r['signal']:3d} {r['event_time'][11:19]}  "
              f"in180 {r['in_180_g']:6.1f} G  dv {r['in_dv_ms']:.3f} m/s  "
              f"w {r['in_width_ms']:.3f} ms  T {r['t180']:.3f}  "
              f"CH4ax {r['ax_CH4_180_g']:6.1f} G", flush=True)
    return rows


def cmp_key(a_rows, b_rows, key):
    a = np.array([r[key] for r in a_rows], float)
    b = np.array([r[key] for r in b_rows], float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return {"before_mean": float(a.mean()), "before_cv_pct": float(100 * a.std(ddof=1) / abs(a.mean())),
            "after_mean": float(b.mean()), "after_cv_pct": float(100 * b.std(ddof=1) / abs(b.mean())),
            "ratio": float(b.mean() / a.mean()),
            "change_pct": float(100 * (b.mean() - a.mean()) / a.mean()),
            "p": float(p)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW_ROOT)
    args = ap.parse_args()

    rows = {}
    for name, subdir in SESSIONS.items():
        print(f"== {name}")
        rows[name] = load_session(args.raw, subdir)
    before, after = rows["before"], rows["after"]
    # matched-state window: the first 30 drops of the 08-17 session (mat
    # rested, same warm-up phase as the 30-drop after session)
    before30 = before[:len(after)]

    comparisons = {}
    for scope, ref in (("full_before", before), ("first30_before", before30)):
        comparisons[scope] = {k: cmp_key(ref, after, k)
                              for k in (*LEVEL_KEYS, *SHAPE_KEYS,
                                        *RATIO_KEYS, *NOISE_KEYS)}

    # what each candidate mis-entry would have produced on that channel
    cand = []
    obs = comparisons["first30_before"]
    ch_metric = {"CH2": "ax_CH2_180_g", "CH3": "ax_CH3_180_g",
                 "CH4": "ax_CH4_180_g", "CH5": "in_180_g"}
    for label, effect in CANDIDATES:
        rowsc = {}
        for chn, exp_ratio in effect.items():
            m = ch_metric[chn]
            rowsc[chn] = {"expected_ratio": float(exp_ratio),
                          "observed_ratio": obs[m]["ratio"],
                          "observed_noise_ratio": obs[f"noise_{chn}_g"]["ratio"]}
        cand.append({"candidate": label, "channels": rowsc})

    out = {
        "sessions": {
            "before": "bpx68c - 60 in - 1/2\" mat - 100 drops (08-17, "
                      "pre-reset settings), 101 captures",
            "after": "bpx68c - calibration testing (08-19, re-entered "
                     "settings), 30 captures",
        },
        "sensitivities_mV_per_G": SENS,
        "comparisons": comparisons,
        "candidate_mis_entries": cand,
        "rows": rows,
    }
    FIG.mkdir(parents=True, exist_ok=True)
    with open(FIG / "calibration_check_metrics.json", "w") as fh:
        json.dump(out, fh, indent=1)

    for k in (*LEVEL_KEYS, *RATIO_KEYS, *NOISE_KEYS):
        c = comparisons["first30_before"][k]
        print(f"{k:16s} before {c['before_mean']:9.3f}  after {c['after_mean']:9.3f}  "
              f"ratio {c['ratio']:.4f} ({c['change_pct']:+.2f} %)  p={c['p']:.2g}")

    make_figures(before, after, comparisons)
    print(f"figures + metrics under {FIG}")


def make_figures(before, after, comparisons):
    cb, ca = "tab:blue", "tab:orange"

    def series(rows, key):
        return np.array([r[key] for r in rows], float)

    # -- 01: continuity of the campaign metrics across the reset ----------
    fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
    xb = np.arange(1, len(before) + 1)
    xa = np.arange(1, len(after) + 1) + len(before) + 4
    panels = [("in_180_g", "CH5 input CFC-180 peak (G)"),
              ("out_180_g", "top-vertex resultant CFC-180 peak (G)"),
              ("in_dv_ms", "input Δv (m/s)"),
              ("t180", "T = out/in (CFC-180)")]
    for ax, (key, ylab) in zip(axes, panels):
        ax.plot(xb, series(before, key), "o-", ms=3, lw=0.8, color=cb,
                label="before reset (08-17, 101 drops)")
        ax.plot(xa, series(after, key), "o-", ms=3, lw=0.8, color=ca,
                label="after reset (08-19, 30 drops)")
        ax.axvline(len(before) + 2.5, color="0.6", lw=1.2, ls="--")
        ax.set_ylabel(ylab, fontsize=9)
        ax.grid(alpha=0.25)
    axes[0].text(len(before) + 2.6, axes[0].get_ylim()[1], " settings reset",
                 fontsize=8, color="0.4", va="top")
    axes[0].legend(fontsize=8)
    axes[-1].set_xlabel("drop number (before session then after session)")
    fig.suptitle("Continuity across the TP4 settings reset — bpx68c, 60 in, arrangement B",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "01_continuity.png", dpi=150)
    plt.close(fig)

    # -- 02: per-channel level + noise ratios vs candidate mis-entries ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    obs = comparisons["first30_before"]
    chans = ["CH2", "CH3", "CH4", "CH5"]
    lv = [obs[m]["ratio"] for m in ("ax_CH2_180_g", "ax_CH3_180_g",
                                    "ax_CH4_180_g", "in_180_g")]
    nz = [obs[f"noise_{c}_g"]["ratio"] for c in chans]
    x = np.arange(len(chans))
    ax1.bar(x - 0.18, lv, 0.36, color=cb, label="CFC-180 peak (drop physics + scale)")
    ax1.bar(x + 0.18, nz, 0.36, color=ca,
            label="pre-trigger noise floor (descent vibration + scale)")
    ax1.axhline(1.0, color="k", lw=1)
    for r, lab in ((SENS["CH2"] / SENS["CH3"], "CH2/CH3 swap"),
                   (SENS["CH4"] / SENS["CH2"], "CH2/CH4 swap"),
                   (SENS["CH5"] / 1.000, "CH5 as 1.000")):
        ax1.axhline(r, color="tab:red", ls=":", lw=1)
        ax1.text(3.55, r, lab, fontsize=7, color="tab:red", va="center")
    ax1.set_xticks(x, chans)
    ax1.set_ylabel("after / before ratio")
    ax1.set_ylim(0.35, 1.20)
    ax1.set_title("Per-channel ratios vs smallest candidate mis-entries", fontsize=10)
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.25, axis="y")

    labels = ["T = out/in", "share CH2", "share CH3", "share CH4",
              "pulse width", "t_second", "e_rebound"]
    keys = ["t180", "share_CH2", "share_CH3", "share_CH4",
            "in_width_ms", "t_second_ms", "e_rebound"]
    vals = [100 * (obs[k]["ratio"] - 1) for k in keys]
    ax2.barh(np.arange(len(keys)), vals, color=["tab:purple"] * 4 + ["0.6"] * 3)
    ax2.axvline(0, color="k", lw=1)
    ax2.set_yticks(np.arange(len(keys)), labels)
    ax2.invert_yaxis()
    ax2.set_xlabel("change after vs before (%)")
    ax2.set_title("Scale-cancelling ratios and shape metrics", fontsize=10)
    ax2.grid(alpha=0.25, axis="x")
    fig.suptitle("Sensitivity check — a mis-entered channel would displace exactly "
                 "one bar pair", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "02_channel_ratios.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
