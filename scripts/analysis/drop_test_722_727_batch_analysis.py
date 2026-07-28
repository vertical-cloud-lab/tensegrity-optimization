#!/usr/bin/env python3
"""7-22 -> 7-27 second-batch 60 in campaigns + batch-1 consistency comparison.

@me-madsen uploaded four new 60 in / 4 felt + 1 cardboard campaigns under
``data/drop-tests/7-22 - 7-27 Drop Tests/`` (PR #86):

  * ``prc1kn``  2026-07-22, 100 captures (``prc1kn100_{1..4}.zip``) —
    full 4-channel format (CH2-4 top-vertex tri-axis + CH5 base plate,
    200 ms / 125 kHz), identical zips to ``7-22-2026 prc1kn 100drops/``;
  * ``RW5F61``  2026-07-23, 101 captures — **CH5 only** (20 ms / 1.25 MHz);
  * ``7xadt6``  2026-07-27, 100 captures — **CH5 only**;
  * ``9GMQYQ``  2026-07-27, 101 captures — **CH5 only**.

The three later sessions were exported with a single channel (the base-plate
single-axis input), so transmissibility T = TOP/CH5 is only computable for
the ``prc1kn`` session in this batch; the others are analyzed as
input-channel consistency checks against batch 1 (the 7-20/7-21 campaigns).

Pipeline conventions are inherited from ``drop_test_60in_5felts_analysis.py``
(imported, not copied): windowed peak on the triggered CH5, SAE J211
CFC-1000/CFC-180 filtering, burn-in changepoint scan, stabilized OLS.
Batch-1 references are reloaded from the committed metrics JSONs.

Emits ``data/drop-tests/7-22 - 7-27 Drop Tests/figures/batch_722_727_metrics.json``
consumed by ``docs/drop-test-7-22-7-27-batch-analysis.md``.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import (  # noqa: E402
    DATA,
    FULL_SCALE_G,
    REAL_IMPACT_FLOOR_G,
    TP4_HEADER_LINES,
    analyze_specimen,
    arr,
    cfc_filter,
    cv,
    ols_full,
    windowed_peak,
)

BATCH = DATA / "7-22 - 7-27 Drop Tests"
FIG = BATCH / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# CH5-only captures pre-trigger is only ~0.6 ms, so the baseline window is
# shorter than the 4-channel format's 2.8 ms.
CH5_ONLY_BASELINE_S = 0.0004

PRC1KN_B2 = {
    "id": "prc1kn",
    "dir": BATCH / "7-22-2026 prc1kn - 4 felt 1 crdbrd",
    "zips": [f"prc1kn100_{k}.zip" for k in (1, 2, 3, 4)],
    "prefix": "prc1kn100",
}

CH5_ONLY = [
    {"id": "RW5F61", "date": "2026-07-23",
     "dir": BATCH / "7-23-2026 RW5F61 - 60in - 4 felt- 1 cardboard",
     "zips": [f"RW5F61 7-23-2026_{k}.zip" for k in (1, 2, 3, 4)]},
    {"id": "7xadt6", "date": "2026-07-27",
     "dir": BATCH / "7-27-2026 7xadt6 60 in - 4 felt 1 cardbrd",
     "zips": [f"7xadt6 - 7-27-2026_{k}.zip" for k in (1, 2, 3, 4)]},
    {"id": "9GMQYQ", "date": "2026-07-27",
     "dir": BATCH / "7-27-2026 9GMQYQ 60 in - 4 felt 1 cardbrd",
     "zips": [f"9GMQYQ 7-27-2026_{k}.zip" for k in (1, 2, 3, 4)]},
]

B1_60IN = DATA / "60in-5felts-validation" / "figures" / "60in_5felts_metrics.json"
B1_PRC1KN = DATA / "prc1kn-60in-5felt" / "figures" / "prc1kn_60in_metrics.json"

COLORS = {"7xadt6": "tab:red", "9GMQYQ": "tab:blue", "prc1kn": "tab:green",
          "RW5F61": "tab:purple"}


def load_ch5_captures(spec: dict) -> list[tuple[int, str]]:
    caps = []
    for zname in spec["zips"]:
        with zipfile.ZipFile(spec["dir"] / zname) as zf:
            for member in zf.namelist():
                stem = Path(member).name
                if not stem.lower().endswith(".csv"):
                    continue
                sig = int(stem.split("Signal")[1].split(".")[0])
                caps.append((sig, zf.read(member).decode("latin-1")))
    caps.sort(key=lambda c: c[0])
    return caps


def analyze_ch5_capture(sig: int, text: str) -> dict:
    ev = None
    for line in text.splitlines()[:TP4_HEADER_LINES]:
        if line.startswith("EventTime:"):
            ev = datetime.strptime(line.split(":", 1)[1].strip(),
                                   "%m/%d/%Y %I:%M:%S %p")
    d = np.genfromtxt(io.StringIO(text), skip_header=TP4_HEADER_LINES,
                      delimiter=",", usecols=(0, 1))
    t, ch5 = d[:, 0], d[:, 1]
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(CH5_ONLY_BASELINE_S / dt))
    ch5 = ch5 - np.median(ch5[:nb])

    i_imp = int(np.argmax(np.abs(ch5)))
    ch5_raw_pk = float(np.abs(ch5[i_imp]))
    is_real = ch5_raw_pk >= REAL_IMPACT_FLOOR_G

    row = {
        "signal": sig,
        "event_time": ev.isoformat(),
        "real_impact": bool(is_real),
        "t_imp_ms": float(t[i_imp] * 1e3),
        "window_ms": float(t[-1] * 1e3),
        "fs_khz": float(fs / 1e3),
        "ch5_raw_g": ch5_raw_pk,
        "ch5_frac_fs": ch5_raw_pk / FULL_SCALE_G["CH5"],
    }
    if not is_real:
        return row
    m180 = windowed_peak(t, cfc_filter(ch5, fs, 180), i_imp, dt)
    m1000 = windowed_peak(t, cfc_filter(ch5, fs, 1000), i_imp, dt)
    row.update({
        "ch5_180_g": m180["peak_abs_g"],
        "ch5_1000_g": m1000["peak_abs_g"],
        "ch5_width_ms": m180["pulse_width_ms"],
        "ch5_dv_ms": m180["delta_v_ms"],
    })
    return row


def analyze_ch5_specimen(spec: dict) -> dict:
    caps = load_ch5_captures(spec)
    rows = [analyze_ch5_capture(sig, text) for sig, text in caps]
    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    real = [r for r in rows if r["real_impact"]]
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])

    print(f"\n{'=' * 70}\n=== {spec['id']} ({spec['date']}, CH5 only) ===\n{'=' * 70}")
    print(f"captures: {len(rows)} total = {len(real)} real drops"
          f" + {len(spurious)} spurious {spurious}")
    print(f"format: {rows[0]['window_ms']:.0f} ms window @ {rows[0]['fs_khz']:.0f} kHz "
          f"(single channel)")
    print(f"cadence: median {np.median(gaps):.0f} s "
          f"(range {gaps.min():.0f}-{gaps.max():.0f} s); span "
          f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min")
    t_imps = arr(real, "t_imp_ms")
    print(f"impact lands at {t_imps.mean():.2f} +- {t_imps.std():.2f} ms into the record")

    fr = arr(rows, "ch5_frac_fs")
    print(f"CH5 raw |peak|: median {100 * np.median(fr):.1f}% FS, "
          f"max {100 * fr.max():.1f}% FS, over FS on {int((fr > 1).sum())} captures")

    drops = arr(real, "drop")
    ch5v = arr(real, "ch5_180_g")
    last = int(drops[-1])

    # burn-in changepoint scan on the CH5 CFC-180 input
    scan = {}
    burn_in_k = None
    for k in range(0, 21):
        m = drops > k
        if m.sum() < 5:
            break
        o = ols_full(drops[m], ch5v[m])
        scan[k] = o
        if burn_in_k is None and o["p"] > 0.05:
            burn_in_k = k
            print(f"burn-in scan: k = {k} first n.s. "
                  f"(slope {o['slope_pct']:+.3f}%/drop, p = {o['p']:.3f})")
    if burn_in_k is None:
        burn_in_k = 5
        print(f"burn-in scan: no k in 0..20 n.s.; using SOP burn-in = {burn_in_k}")

    stable = drops > burn_in_k
    xs = drops[stable]
    results = {}
    print(f"stabilized-phase OLS (drops {burn_in_k + 1}..{last}, n = {int(stable.sum())}):")
    for name, key in [("CH5 input", "ch5_180_g"), ("CH5 raw", "ch5_raw_g"),
                      ("plate dv", "ch5_dv_ms"), ("pulse width", "ch5_width_ms")]:
        o = ols_full(xs, arr(real, key)[stable])
        results[name] = o
        print(f"  {name:11s}: mean {o['mean']:8.3f}  CV {o['cv']:5.2f}%   "
              f"slope {o['slope_pct']:+.3f}%/drop   p = {o['p']:.2e}  "
              f"R² = {o['r2']:.3f}  DW = {o['dw']:.2f}")

    return {
        "id": spec["id"],
        "date": spec["date"],
        "rows": rows,
        "real": real,
        "n_captures": len(rows),
        "spurious_captures": spurious,
        "cadence_s": {"median": float(np.median(gaps)), "min": float(gaps.min()),
                      "max": float(gaps.max())},
        "span_min": float((times[-1] - times[0]).total_seconds() / 60.0),
        "ch5_max_frac_fs": float(fr.max()),
        "burn_in_drops": burn_in_k,
        "stabilized_window": [int(burn_in_k) + 1, last],
        "stabilized_ols": results,
    }


def stab(real: list[dict], burn_in: int, key: str) -> np.ndarray:
    drops = arr(real, "drop")
    return arr(real, key)[drops > burn_in]


def welch(a: np.ndarray, b: np.ndarray) -> dict:
    tt = stats.ttest_ind(a, b, equal_var=False)
    sp = np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 2.0)
    return {
        "batch1": {"n": int(len(a)), "mean": float(a.mean()),
                   "sd": float(a.std(ddof=1)), "cv": cv(a)},
        "batch2": {"n": int(len(b)), "mean": float(b.mean()),
                   "sd": float(b.std(ddof=1)), "cv": cv(b)},
        "diff_pct": float(100.0 * (b.mean() - a.mean()) / a.mean()),
        "welch_p": float(tt.pvalue),
        "cohens_d": float((b.mean() - a.mean()) / sp) if sp else float("nan"),
    }


def main() -> int:
    # ---------------- batch 2 ------------------------------------------
    s_prc = analyze_specimen(PRC1KN_B2)
    ch5_specs = [analyze_ch5_specimen(s) for s in CH5_ONLY]

    # ---------------- batch 1 references -------------------------------
    b1_60 = json.loads(B1_60IN.read_text())
    b1_prc = json.loads(B1_PRC1KN.read_text())
    batch1 = {}
    for sid in ("7xadt6", "9GMQYQ"):
        batch1[sid] = {
            "real": [r for r in b1_60["per_capture"][sid] if r["real_impact"]],
            "burn_in": b1_60["specimens"][sid]["burn_in_drops"],
        }
    batch1["prc1kn"] = {
        "real": [r for r in b1_prc["per_capture"] if r["real_impact"]],
        "burn_in": b1_prc["specimen"]["burn_in_drops"],
    }

    # ---------------- prc1kn: full T comparison ------------------------
    print(f"\n{'=' * 70}\n=== prc1kn batch 1 (07-21) vs batch 2 (07-22) ===\n{'=' * 70}")
    prc_cmp = {}
    for key, label in [("t_ch5", "T = TOP/CH5"), ("top_180_g", "TOP CFC-180 (G)"),
                       ("ch5_180_g", "CH5 input (G)")]:
        a = stab(batch1["prc1kn"]["real"], batch1["prc1kn"]["burn_in"], key)
        b = stab(s_prc["real"], s_prc["burn_in_drops"], key)
        prc_cmp[key] = welch(a, b)
        c = prc_cmp[key]
        print(f"  {label:16s}: {a.mean():8.3f} (CV {cv(a):.2f}%)  ->  "
              f"{b.mean():8.3f} (CV {cv(b):.2f}%)   diff {c['diff_pct']:+.2f}%   "
              f"Welch p = {c['welch_p']:.1e}   d = {c['cohens_d']:+.1f}")

    # ---------------- input-channel consistency (all four) -------------
    print(f"\n{'=' * 70}\n=== CH5 input consistency vs batch 1 ===\n{'=' * 70}")
    input_cmp = {}
    b2_by_id = {s["id"]: s for s in ch5_specs}
    b2_by_id["prc1kn"] = s_prc
    for sid in ("prc1kn", "7xadt6", "9GMQYQ"):
        a = stab(batch1[sid]["real"], batch1[sid]["burn_in"], "ch5_180_g")
        s2 = b2_by_id[sid]
        b = stab(s2["real"], s2["burn_in_drops"], "ch5_180_g")
        input_cmp[sid] = welch(a, b)
        c = input_cmp[sid]
        print(f"  {sid:8s}: batch1 {a.mean():6.1f} G (CV {cv(a):.2f}%)  ->  "
              f"batch2 {b.mean():6.1f} G (CV {cv(b):.2f}%)   diff {c['diff_pct']:+.1f}%   "
              f"p = {c['welch_p']:.1e}")
    rw = b2_by_id["RW5F61"]
    rw_ch5 = stab(rw["real"], rw["burn_in_drops"], "ch5_180_g")
    print(f"  RW5F61  : no 60 in batch-1 campaign; batch2 {rw_ch5.mean():.1f} G "
          f"(CV {cv(rw_ch5):.2f}%)")

    # ---------------- figures ------------------------------------------
    all_b2 = [("prc1kn", s_prc)] + [(s["id"], s) for s in ch5_specs]

    # Fig 1: full series, raw CH5 as % FS
    fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=False)
    for ax, (sid, s) in zip(axes, all_b2):
        rows = s["rows"]
        sigs = arr(rows, "signal")
        if sid == "prc1kn":
            fr = np.array([r["sat"]["CH5"]["frac_fs"] for r in rows]) * 100
        else:
            fr = arr(rows, "ch5_frac_fs") * 100
        ax.plot(sigs, fr, "o-", ms=3, color=COLORS[sid])
        ax.axhline(100 / 3, color="k", ls=":", lw=1.2, label="FS/3 head-room target")
        for sp_sig in s["spurious_captures"]:
            ax.axvline(sp_sig, color="gray", ls="--", lw=1)
        date = s.get("date", "2026-07-22")
        ax.set(ylabel="CH5 raw |peak| (% FS)",
               title=f"{sid} ({date}): {len(s['real'])} real drops / {s['n_captures']} "
                     f"captures (median cadence {s['cadence_s']['median']:.0f} s)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("capture (Signal #)")
    fig.suptitle("7-22 -> 7-27 batch: base-plate raw peak vs full scale")
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: stabilized CH5 CFC-180 input per session with OLS fit
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    for ax, (sid, s) in zip(axes.flat, all_b2):
        real = s["real"]
        drops = arr(real, "drop")
        stable = drops > s["burn_in_drops"]
        xs = drops[stable]
        y = arr(real, "ch5_180_g")[stable]
        o = ols_full(xs, y)
        ax.plot(xs, y, "o", ms=3.5, color=COLORS[sid])
        fit = o["mean"] - o["slope"] * xs.mean() + o["slope"] * xs
        ax.plot(xs, fit, "k-", lw=1.5,
                label=f"OLS {o['slope_pct']:+.3f}%/drop, p = {o['p']:.1e}, R² = {o['r2']:.2f}")
        ax.set(xlabel="drop #", ylabel="CH5 input CFC-180 (G)",
               title=f"{sid} (drops {s['stabilized_window'][0]}-{s['stabilized_window'][1]})")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.suptitle("stabilized-phase CH5 input — 7-22 -> 7-27 batch")
    fig.tight_layout()
    fig.savefig(FIG / "02_stabilized_input.png", dpi=130)
    plt.close(fig)

    # Fig 3: batch-1 vs batch-2 CH5 input per specimen
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data, labels, cols = [], [], []
    for sid in ("prc1kn", "7xadt6", "9GMQYQ"):
        data.append(stab(batch1[sid]["real"], batch1[sid]["burn_in"], "ch5_180_g"))
        labels.append(f"{sid}\nbatch 1")
        cols.append(COLORS[sid])
        s2 = b2_by_id[sid]
        data.append(stab(s2["real"], s2["burn_in_drops"], "ch5_180_g"))
        labels.append(f"{sid}\nbatch 2")
        cols.append(COLORS[sid])
    data.append(rw_ch5)
    labels.append("RW5F61\nbatch 2")
    cols.append(COLORS["RW5F61"])
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch, c in zip(bp["boxes"], cols):
        patch.set_facecolor(c)
        patch.set_alpha(0.4)
    ax.set(ylabel="CH5 input CFC-180 (G)",
           title="base-plate input level: batch 1 (07-20/07-21) vs batch 2 (07-22/07-23/07-27)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "03_input_batch_comparison.png", dpi=130)
    plt.close(fig)

    # Fig 4: prc1kn transmissibility batch 1 vs batch 2
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (key, name) in zip(axes, [("t_ch5", "T = TOP/CH5 (CFC-180)"),
                                      ("top_180_g", "TOP output CFC-180 (G)")]):
        a = stab(batch1["prc1kn"]["real"], batch1["prc1kn"]["burn_in"], key)
        b = stab(s_prc["real"], s_prc["burn_in_drops"], key)
        bp = ax.boxplot([a, b], tick_labels=["batch 1 (07-21)", "batch 2 (07-22)"],
                        patch_artist=True, widths=0.5)
        for patch in bp["boxes"]:
            patch.set_facecolor(COLORS["prc1kn"])
            patch.set_alpha(0.4)
        if key == "t_ch5":
            ax.axhline(1.0, color="k", ls=":", lw=1.2, label="T = 1 (no attenuation)")
            ax.legend(fontsize=8)
        c = prc_cmp[key]
        ax.set(ylabel=name,
               title=f"diff {c['diff_pct']:+.2f}%  Welch p = {c['welch_p']:.1e}  "
                     f"d = {c['cohens_d']:+.1f}")
        ax.grid(alpha=0.3, axis="y")
    fig.suptitle("prc1kn back-to-back campaigns: the only batch-2 session with a "
                 "top-vertex channel")
    fig.tight_layout()
    fig.savefig(FIG / "04_prc1kn_transmissibility.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary --------------------------
    summary = {
        "condition": {"height_in": 60, "stack": "4 felt + 1 cardboard"},
        "sessions": {
            "prc1kn": {k: v for k, v in s_prc.items() if k not in ("rows", "real")},
            **{s["id"]: {k: v for k, v in s.items() if k not in ("rows", "real")}
               for s in ch5_specs},
        },
        "per_capture": {sid: s["rows"] for sid, s in all_b2},
        "prc1kn_batch_comparison": prc_cmp,
        "input_batch_comparison": input_cmp,
        "rw5f61_input": {"mean": float(rw_ch5.mean()), "cv": cv(rw_ch5),
                         "n": int(len(rw_ch5))},
    }
    with open(FIG / "batch_722_727_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
