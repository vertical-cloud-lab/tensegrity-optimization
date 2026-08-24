#!/usr/bin/env python3
"""Absorber-stack (4 felt + 1 cardboard) compaction analysis, CH5-only.

@me-madsen (PR #86) asked how the compaction of the shared absorber stack
grows with each drop, whether/when the sheets become unusable, and whether
transmissibility stays consistent for a specimen at different compaction
levels.  Issue #88 documents the visible thickness loss of the one physical
stack the lab owns (4 felt sheets + 1 cardboard — there is no spare, so
every 60 in campaign since 07-20 ran on this same stack).

No raw data of its own: everything is re-aggregated from the per-capture
records already emitted by the committed campaign analyses —

  * ``60in-5felts-validation/figures/60in_5felts_metrics.json``  (07-20)
  * ``prc1kn-60in-5felt/figures/prc1kn_60in_metrics.json``       (07-21)
  * ``7-22 - 7-27 Drop Tests/figures/batch_722_727_metrics.json``(07-22..27)

giving 704 drops on the stack across seven sessions.  The compaction proxy
is the CH5 base-plate **raw** |peak| (the filtered CFC-180 input barely
moves with wear; compaction shows up as high-frequency spike content that
eats the 9,442.9 G full-scale head-room).

Emits ``data/drop-tests/compaction/figures/compaction_metrics.json``
consumed by ``docs/drop-test-compaction-analysis.md``.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

DATA = Path(__file__).resolve().parents[2] / "data" / "drop-tests"
OUT = DATA / "compaction"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

FS_G = 9442.9          # CH5 single-axis full scale (TP4 channel map)
BURN_IN = 5            # SOP burn-in drops excluded from stabilized stats
COLORS = {"7xadt6": "tab:red", "9GMQYQ": "tab:blue", "prc1kn": "tab:green",
          "RW5F61": "tab:purple"}


def load_sessions():
    """Chronological (label, specimen, per-capture list) on the shared stack."""
    d20 = json.load(open(DATA / "60in-5felts-validation" / "figures"
                         / "60in_5felts_metrics.json"))["per_capture"]
    d21 = json.load(open(DATA / "prc1kn-60in-5felt" / "figures"
                         / "prc1kn_60in_metrics.json"))["per_capture"]
    d22 = json.load(open(DATA / "7-22 - 7-27 Drop Tests" / "figures"
                         / "batch_722_727_metrics.json"))["per_capture"]
    raw = [
        ("7xadt6 07-20", "7xadt6", d20["7xadt6"]),
        ("9GMQYQ 07-20", "9GMQYQ", d20["9GMQYQ"]),
        ("prc1kn 07-21", "prc1kn", d21),
        ("prc1kn 07-22", "prc1kn", d22["prc1kn"]),
        ("RW5F61 07-23", "RW5F61", d22["RW5F61"]),
        ("7xadt6 07-27", "7xadt6", d22["7xadt6"]),
        ("9GMQYQ 07-27", "9GMQYQ", d22["9GMQYQ"]),
    ]
    return [(lab, sp, [c for c in pc if c.get("real_impact")])
            for lab, sp, pc in raw]


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    res = stats.linregress(x, y)
    return {"slope": res.slope, "intercept": res.intercept, "p": res.pvalue,
            "r2": res.rvalue ** 2, "stderr": res.stderr}


def main():
    sessions = load_sessions()

    # ---------------- per-session wear metrics -------------------------
    per_session = []
    cum = 0
    prev_end_t = prev_end_raw = None
    for lab, sp, pc in sessions:
        raws = np.array([c["ch5_raw_g"] for c in pc])
        drops = np.array([c["drop"] for c in pc], float)
        t0 = datetime.fromisoformat(pc[0]["event_time"])
        t1 = datetime.fromisoformat(pc[-1]["event_time"])
        stab = drops > BURN_IN
        in180 = np.array([c["ch5_180_g"] for c in pc])
        width = np.array([c.get("ch5_width_ms", np.nan) for c in pc], float)
        dv = np.array([c.get("ch5_dv_ms", np.nan) for c in pc], float)
        wear = ols(drops, raws)  # G/drop, whole session (wear is monotonic)
        rest_h = ((t0 - prev_end_t).total_seconds() / 3600
                  if prev_end_t else None)
        start5, end5 = raws[:5].mean(), raws[-5:].mean()
        rec = per_session and {
            "rest_h": rest_h,
            "prev_end_raw_g": prev_end_raw,
            "recovered_g": prev_end_raw - start5,
            "recovered_frac": (prev_end_raw - start5) / prev_end_raw,
        }
        per_session.append({
            "label": lab, "specimen": sp, "n": len(pc),
            "start": t0.isoformat(), "end": t1.isoformat(),
            "cum_start": cum + 1, "cum_end": cum + len(pc),
            "raw_first5_g": start5, "raw_last5_g": end5,
            "frac_fs_first5": start5 / FS_G, "frac_fs_last5": end5 / FS_G,
            "raw_max_g": raws.max(), "frac_fs_max": raws.max() / FS_G,
            "wear_g_per_drop": wear["slope"], "wear_p": wear["p"],
            "wear_r2": wear["r2"],
            "in180_stab_mean_g": in180[stab].mean(),
            "in180_stab_cv_pct": 100 * in180[stab].std(ddof=1)
            / in180[stab].mean(),
            "width_stab_ms": float(np.nanmean(width[stab])),
            "dv_stab_ms": float(np.nanmean(dv[stab])),
            "recovery": rec or None,
        })
        cum += len(pc)
        prev_end_t, prev_end_raw = t1, end5

    # wear-rate acceleration for the repeat specimens (same article,
    # same nominal session shape, one week apart)
    accel = {}
    for sp in ("7xadt6", "9GMQYQ"):
        pair = [s for s in per_session if s["specimen"] == sp]
        accel[sp] = {"early_g_per_drop": pair[0]["wear_g_per_drop"],
                     "late_g_per_drop": pair[1]["wear_g_per_drop"],
                     "ratio": pair[1]["wear_g_per_drop"]
                     / pair[0]["wear_g_per_drop"]}

    # clipping projection: from the latest session-start levels and the
    # latest observed wear rates, drops until a session crosses 95 % FS
    latest = per_session[-1]
    proj = {}
    for s in per_session[-2:]:
        margin = 0.95 * FS_G - s["raw_first5_g"]
        proj[s["label"]] = {
            "start_frac_fs": s["frac_fs_first5"],
            "wear_g_per_drop": s["wear_g_per_drop"],
            "drops_to_95fs_from_start": margin / s["wear_g_per_drop"],
        }

    # ---------------- T vs compaction ----------------------------------
    t_sessions = []
    for lab, sp, pc in sessions:
        if "t_ch5" not in pc[0]:
            continue
        drops = np.array([c["drop"] for c in pc], float)
        stab = drops > BURN_IN
        fs_pct = 100 * np.array([c["ch5_raw_g"] for c in pc]) / FS_G
        t = np.array([c["t_ch5"] for c in pc])
        sens = ols(fs_pct[stab], t[stab])  # dT per +1 % FS within session
        t_sessions.append({
            "label": lab, "specimen": sp,
            "fs_pct_range": [fs_pct[stab].min(), fs_pct[stab].max()],
            "t_mean": t[stab].mean(),
            "t_cv_pct": 100 * t[stab].std(ddof=1) / t[stab].mean(),
            "dT_per_10pct_fs": 10 * sens["slope"], "sens_p": sens["p"],
            "sens_r2": sens["r2"],
            "_fs": fs_pct[stab], "_t": t[stab],
        })

    prc = [s for s in t_sessions if s["specimen"] == "prc1kn"]
    prc_pair = {
        "t_0721": prc[0]["t_mean"], "t_0722": prc[1]["t_mean"],
        "delta_pct": 100 * (prc[1]["t_mean"] / prc[0]["t_mean"] - 1),
        "fs_pct_0721": np.mean(prc[0]["fs_pct_range"]),
        "fs_pct_0722": np.mean(prc[1]["fs_pct_range"]),
    }

    # ---------------- figures ------------------------------------------
    starts = [s["cum_start"] for s in per_session]

    # 01: the requested graph — raw CH5 peak vs cumulative drops on stack
    fig, ax = plt.subplots(figsize=(13, 6))
    cum = 0
    seen = set()
    for (lab, sp, pc), s in zip(sessions, per_session):
        xs = np.arange(cum + 1, cum + len(pc) + 1)
        fr = 100 * np.array([c["ch5_raw_g"] for c in pc]) / FS_G
        ax.plot(xs, fr, "o", ms=2.5, color=COLORS[sp],
                label=sp if sp not in seen else None)
        seen.add(sp)
        rec = s["recovery"]
        if rec and rec["rest_h"] > 1:
            ax.annotate(f"{rec['rest_h']:.0f} h rest\n−{100*rec['recovered_frac']:.0f} %",
                        xy=(xs[0], fr[:5].mean()), xytext=(xs[0] - 4, fr[:5].mean() + 14),
                        fontsize=7.5, ha="right",
                        arrowprops=dict(arrowstyle="->", lw=0.8, color="gray"))
        ax.annotate(lab.split()[1], xy=(xs[0] + len(xs) / 2, 3),
                    fontsize=7.5, ha="center", color=COLORS[sp])
        cum += len(pc)
    for x in starts[1:]:
        ax.axvline(x - 0.5, color="gray", ls="--", lw=0.8, alpha=0.6)
    ax.axhline(100, color="k", lw=1.4, label="CH5 full scale (9,443 G)")
    ax.axhline(95, color="tab:orange", ls="--", lw=1.2, label="95 % FS (clip risk)")
    ax.axhline(100 / 3, color="k", ls=":", lw=1.2, label="FS/3 head-room target")
    ax.set(xlabel="cumulative drops on the shared 4-felt + 1-cardboard stack",
           ylabel="CH5 raw |peak| (% of full scale)", ylim=(0, 105),
           title="Stack compaction over 704 drops: monotonic within-session "
                 "wear, largely reset between sessions")
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_compaction_timeline.png", dpi=130)
    plt.close(fig)

    # 02: wear rate per session + recovery vs rest time
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5))
    ax = axes[0]
    labs = [s["label"] for s in per_session]
    rates = [s["wear_g_per_drop"] for s in per_session]
    cols = [COLORS[s["specimen"]] for s in per_session]
    ax.bar(range(len(labs)), rates, color=cols)
    for i, r in enumerate(rates):
        ax.annotate(f"{r:.1f}", (i, r), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels([l.replace(" ", "\n") for l in labs], fontsize=8)
    ax.set(ylabel="within-session wear rate (G/drop, OLS)",
           title="Within-session wear rate by session\n"
                 f"(7xadt6, matched fresh start, one week apart: "
                 f"×{accel['7xadt6']['ratio']:.1f})")
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1]
    order = ["7xadt6", "9GMQYQ", "prc1kn", "RW5F61"]
    seen_x = {}
    for s in per_session:
        x = order.index(s["specimen"])
        dodge = seen_x.get(x, 0)
        seen_x[x] = dodge + 1
        ax.plot(x, 100 * s["frac_fs_first5"], "o", ms=10,
                color=COLORS[s["specimen"]])
        ax.annotate(s["label"].split()[1],
                    (x, 100 * s["frac_fs_first5"]),
                    textcoords="offset points",
                    xytext=(9, -3 + 9 * dodge), fontsize=8.5)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order)
    ax.set_xlim(-0.5, len(order) - 0.3)
    ax.set(ylabel="session-start CH5 raw |peak| (first 5 drops, % FS)",
           title="Session-start level is specimen-reproducible a week apart\n"
                 "(prc1kn's back-to-back pair is the one unrecovered case)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "02_wear_and_recovery.png", dpi=130)
    plt.close(fig)

    # 03: severity invariance — filtered input + Δv flat while raw triples
    fig, axes = plt.subplots(3, 1, figsize=(12.5, 9), sharex=True)
    cum = 0
    for lab, sp, pc in sessions:
        xs = np.arange(cum + 1, cum + len(pc) + 1)
        for ax, key, scale in ((axes[0], "ch5_raw_g", 1 / 1000),
                               (axes[1], "ch5_180_g", 1),
                               (axes[2], "ch5_dv_ms", 1)):
            y = np.array([c.get(key, np.nan) for c in pc], float) * scale
            ax.plot(xs, y, "o", ms=2.2, color=COLORS[sp])
        cum += len(pc)
    for ax in axes:
        for x in starts[1:]:
            ax.axvline(x - 0.5, color="gray", ls="--", lw=0.8, alpha=0.6)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("CH5 raw |peak| (kG)")
    axes[0].set_title("What compaction changes — and what it doesn't")
    axes[1].set_ylabel("CH5 CFC-180 input (G)")
    axes[1].set_ylim(300, 550)
    axes[1].annotate("RW5F61's lower level is a specimen effect\n"
                     "(420 G, vs its own prior-session levels at 5/13 in)",
                     xy=(0.62, 0.12), xycoords="axes fraction", fontsize=8)
    axes[2].set_ylabel("CH5 Δv (m/s)")
    axes[2].set_xlabel("cumulative drops on stack")
    axes[2].annotate("step is an export artifact: 07-23+ sessions were "
                     "captured in a 20 ms window\n(partial ringdown "
                     "integration), not a severity change",
                     xy=(0.45, 0.15), xycoords="axes fraction", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "03_severity_invariance.png", dpi=130)
    plt.close(fig)

    # 04: transmissibility vs compaction level
    fig, ax = plt.subplots(figsize=(10.5, 6))
    markers = {"7xadt6 07-20": "o", "9GMQYQ 07-20": "o",
               "prc1kn 07-21": "o", "prc1kn 07-22": "s"}
    for s in t_sessions:
        ax.plot(s["_fs"], s["_t"], markers[s["label"]], ms=3.2, alpha=0.6,
                color=COLORS[s["specimen"]],
                label=f"{s['label']}  (T̄ = {s['t_mean']:.3f})")
        fit = np.poly1d([s["dT_per_10pct_fs"] / 10,
                         s["t_mean"] - s["dT_per_10pct_fs"] / 10
                         * np.mean(s["fs_pct_range"])])
        xr = np.array(s["fs_pct_range"])
        ax.plot(xr, fit(xr), "-", lw=1.6, color=COLORS[s["specimen"]])
    ax.axhline(1.0, color="k", ls=":", lw=1.2)
    ax.annotate("prc1kn day-to-day: +1.5 % T for +19 %-FS compaction\n"
                "(mount re-seating confounded — see doc §4)",
                xy=(0.03, 0.96), xycoords="axes fraction", fontsize=8.5,
                va="top")
    ax.set(xlabel="CH5 raw |peak| (% FS) — compaction proxy",
           ylabel="T = TOP/CH5 (CFC-180)",
           title="Transmissibility vs stack compaction: within a session T is "
                 "nearly flat\nacross large compaction swings")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "04_transmissibility_vs_compaction.png", dpi=130)
    plt.close(fig)

    # ---------------- metrics JSON -------------------------------------
    for s in t_sessions:
        s.pop("_fs"), s.pop("_t")
        s["fs_pct_range"] = [float(v) for v in s["fs_pct_range"]]
    out = {
        "stack": "4 felt + 1 cardboard (single physical stack, issue #88)",
        "full_scale_g": FS_G,
        "total_drops": sum(s["n"] for s in per_session),
        "per_session": per_session,
        "wear_acceleration": accel,
        "clip_projection": proj,
        "t_vs_compaction": t_sessions,
        "prc1kn_cross_session": prc_pair,
    }
    (FIG / "compaction_metrics.json").write_text(
        json.dumps(out, indent=1, default=float))

    for s in per_session:
        print(f"{s['label']}: {100*s['frac_fs_first5']:.0f}→"
              f"{100*s['frac_fs_last5']:.0f} % FS, wear "
              f"{s['wear_g_per_drop']:.1f} G/drop, input "
              f"{s['in180_stab_mean_g']:.0f} G, Δv {s['dv_stab_ms']:.2f} m/s")
    print("wear acceleration:", {k: round(v["ratio"], 2)
                                 for k, v in accel.items()})
    print("clip projection:", {k: round(v["drops_to_95fs_from_start"])
                               for k, v in proj.items()})
    print("prc1kn cross-session T:", prc_pair)
    print(f"wrote figures + metrics to {FIG}")


if __name__ == "__main__":
    main()
