#!/usr/bin/env python3
"""Analyze the **burn-in wax** key-seat input-output drop tests (PR #67).

Direct follow-up to ``drop_test_key_mounted_wax_analysis.py``. Same input-output
pair @ctrhjk has been using — a single-axis accelerometer wax-mounted on the
bottom acrylic plate is the **input** (CH5, triggered), a tri-axis accelerometer
in the top-vertex **key-seat** (wax-retained) is the **output** (CH2/CH3/CH4),
bungees removed — and the same deliberately-failed print (``prc1kn``, bubbles in
its TPU cable) used only to exercise the mount/DAQ, not to compare geometry.

The *one* thing under test here is the **burn-in wax protocol**. The prior
wax-retainer run showed a small-but-significant output creep (+0.90 G/drop,
p = 0.005) that read as the wax progressively **seating** over the first few
impacts. The proposed fix: pre-seat the wax with a few unrecorded **burn-in**
drops, then record. @ctrhjk removed the old wax residue, applied fresh wax, and
dropped the specimen **8 times**:

  * drops 1-3 (``Signal1..3``) = **burn-in** phase (no videos), meant to seat the
    fresh wax;
  * drops 4-8 (``Signal4..8``) = **recorded** phase (with videos), the drops that
    would count in a real campaign.

The question: does the wax-seating creep **concentrate in the burn-in drops and
flatten out** in drops 4-8? i.e. is the recorded phase drift-free after the
burn-in, as intended?

Channel map (identical to the input-output / key-seat / wax series):
  * CH5            — single-axis accelerometer wax-mounted on the **base plate**
    = INPUT; the triggered channel (1000 G trigger, 9442.9 G full scale).
  * CH2, CH3, CH4  — tri-axis accelerometer in the vertex **key-seat** (wax-
    retained) = OUTPUT (full scales 14492.8 / 14992.5 / 13624.0 G); trigger OFF.

File-name note: the TP4 ``Signal{n}`` index is the *capture* number. This run is
contiguous — ``Signal{1..8}`` = drops 1..8.

What it does mirrors the wax script: locate the impact on the triggered CH5
within the first 10 ms (windowed, not a global 0.2 s max), baseline-correct,
report raw / SAE J211 CFC-1000 / CFC-180 peaks for input (CH5) and the tri-axis
output resultant, transmissibility T = output / input, input pulse width and
Delta-v. It then splits the 8 drops into burn-in (1-3) and recorded (4-8), runs
an OLS drift trend on **all 8**, on the **burn-in** subset, and on the
**recorded** subset, and loads the prior (no-burn-in) wax run for comparison.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "burn-in-wax" / "raw"
FIG = REPO / "data" / "drop-tests" / "burn-in-wax" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
# prior wax-retainer run (no burn-in), for the burn-in-vs-no-burn-in comparison
PRIOR_RAW = REPO / "data" / "drop-tests" / "key-mounted-wax" / "raw"
PRIOR_SIGNAL_TO_DROP = {7: 1, 8: 2, 9: 3, 10: 4, 11: 5}

GRAVITY = 9.80665  # m/s^2 per G

OUT_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output in the vertex key-seat
CH5 = 3  # single-axis input wax-mounted on the base plate (triggered channel)

IMPACT_SEARCH_S = 0.010  # look for the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

SPECIMEN = "prc1kn"  # the (failed-print) specimen used to exercise the key-seat
# (capture index -> drop number); contiguous this run.
SIGNAL_TO_DROP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
BURN_IN = [1, 2, 3]  # unrecorded seating drops (no videos)
RECORDED = [4, 5, 6, 7, 8]  # the drops that would count in a real campaign


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 4]) = (time, [CH2, CH3, CH4, CH5])."""
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",", usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def impact_index(t: np.ndarray, trig: np.ndarray, dt: float) -> int:
    """Index of the trigger-channel (CH5 input) impact inside the first 10 ms."""
    nb = max(1, int(BASELINE_S / dt))
    base = np.median(trig[:nb])
    search = t < IMPACT_SEARCH_S
    rel = np.abs(trig - base)
    rel[~search] = -np.inf
    return int(np.argmax(rel))


def windowed_peak(t: np.ndarray, a_g: np.ndarray, i_imp: int, dt: float) -> dict:
    """Peak |g|, peak time, half-amplitude width and Delta-v near the impact."""
    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo0, hi0 = max(0, i_imp - half), min(len(a_g), i_imp + half)
    seg = a_g[lo0:hi0]
    j = int(np.argmax(np.abs(seg)))
    idx = lo0 + j
    peak = a_g[idx]
    peak_abs = abs(peak)

    thr = peak_abs / 2.0
    sign = np.sign(peak)
    over = (sign * a_g) >= thr
    lo = idx
    while lo > lo0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < hi0 - 1 and over[hi + 1]:
        hi += 1
    width = t[hi] - t[lo]
    a_ms2 = a_g * GRAVITY
    dv = integrate.trapezoid(a_ms2[lo : hi + 1], t[lo : hi + 1])
    return {
        "peak_abs_g": peak_abs,
        "t_peak_ms": t[idx] * 1e3,
        "pulse_width_ms": width * 1e3,
        "delta_v_ms": abs(dv),
    }


def resultant(out: np.ndarray) -> np.ndarray:
    """Magnitude of the tri-axis (CH2, CH3, CH4) vector at each sample."""
    return np.sqrt(np.sum(out**2, axis=1))


def cv(vals: list[float]) -> float:
    """Coefficient of variation (%) = 100 * std / mean."""
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def analyze_run(raw_dir: Path, sig_to_drop: dict[int, int], fname: str) -> tuple[list[dict], dict]:
    """Return (per-drop rows, traces) for one run directory."""
    rows: list[dict] = []
    traces: dict = {}
    for sig, drop in sorted(sig_to_drop.items(), key=lambda kv: kv[1]):
        path = raw_dir / fname.format(sig=sig)
        if not path.exists():
            print(f"missing {path}")
            continue
        t, ch = load(path)
        dt = float(np.median(np.diff(t)))
        fs = 1.0 / dt
        nb = max(1, int(BASELINE_S / dt))

        ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])  # input (base plate)
        out = ch[:, OUT_COLS] - np.median(ch[:nb, OUT_COLS], axis=0)
        i_imp = impact_index(t, ch5, dt)

        in_raw = windowed_peak(t, ch5, i_imp, dt)["peak_abs_g"]
        ch5_1000 = cfc_filter(ch5, fs, 1000)
        ch5_180 = cfc_filter(ch5, fs, 180)
        m_in_1000 = windowed_peak(t, ch5_1000, i_imp, dt)
        m_in_180 = windowed_peak(t, ch5_180, i_imp, dt)

        res_raw = resultant(out)
        out180 = np.stack([cfc_filter(out[:, j], fs, 180) for j in range(out.shape[1])], axis=1)
        out1000 = np.stack([cfc_filter(out[:, j], fs, 1000) for j in range(out.shape[1])], axis=1)
        res_180 = resultant(out180)
        res_1000 = resultant(out1000)
        out_raw_peak = windowed_peak(t, res_raw, i_imp, dt)["peak_abs_g"]
        m_out_1000 = windowed_peak(t, res_1000, i_imp, dt)
        m_out_180 = windowed_peak(t, res_180, i_imp, dt)

        in180 = m_in_180["peak_abs_g"]
        out180_pk = m_out_180["peak_abs_g"]
        transmiss = out180_pk / in180 if in180 else float("nan")

        rows.append(
            {
                "drop": drop,
                "signal": sig,
                "t_imp_ms": t[i_imp] * 1e3,
                "in_raw_g": in_raw,
                "in_1000_g": m_in_1000["peak_abs_g"],
                "in_180_g": in180,
                "out_raw_g": out_raw_peak,
                "out_1000_g": m_out_1000["peak_abs_g"],
                "out_180_g": out180_pk,
                "transmiss": transmiss,
                "in_width_ms": m_in_180["pulse_width_ms"],
                "in_dv_ms": m_in_180["delta_v_ms"],
            }
        )
        traces[drop] = (t, ch5, ch5_180, res_raw, res_180, i_imp, fs)
    return rows, traces


def ols(drops: np.ndarray, vals: list[float]) -> tuple[float, float]:
    """Return (slope-per-drop, p-value) of an OLS fit vs drop number."""
    sl, _ic, _r, p, _se = stats.linregress(drops, vals)
    return float(sl), float(p)


def subset(rows: list[dict], drops: list[int]) -> list[dict]:
    return [r for r in rows if r["drop"] in drops]


def summarize(label: str, rows: list[dict]) -> dict:
    """Print + return mean/CV/OLS summary for a subset of drops."""
    ins = [r["in_180_g"] for r in rows]
    outs = [r["out_180_g"] for r in rows]
    ts = [r["transmiss"] for r in rows]
    d = np.array([r["drop"] for r in rows], float)
    out = {"n": len(rows)}
    print(f"\n  [{label}]  (drops {[r['drop'] for r in rows]})")
    print(f"    input  CH5 : {np.mean(ins):6.1f} ± {np.std(ins, ddof=1):4.1f} G   (CV {cv(ins):.2f}%)")
    print(f"    output tri : {np.mean(outs):6.1f} ± {np.std(outs, ddof=1):4.1f} G   (CV {cv(outs):.2f}%)")
    print(f"    T = OUT/IN : {np.mean(ts):6.3f} ± {np.std(ts, ddof=1):.3f}    (CV {cv(ts):.2f}%)")
    for name, v in [("input", ins), ("output", outs), ("T", ts)]:
        if len(rows) >= 3:
            sl, p = ols(d, v)
            flag = "significant" if p < 0.05 else "n.s."
            pct = 100.0 * sl / np.mean(v)
            print(f"    {name:7s} slope = {sl:+8.4f}/drop ({pct:+.2f}%/drop)  p = {p:.3f}  ({flag})")
            out[name] = {"slope": sl, "p": p, "pct": pct, "mean": float(np.mean(v)), "cv": cv(v)}
        else:
            out[name] = {"mean": float(np.mean(v)), "cv": cv(v)}
    return out


def report(label: str, rows: list[dict]) -> None:
    hdr = (
        f"{'drop':>4s} {'sig':>4s} {'phase':>7s} {'t_imp':>6s} "
        f"{'IN raw':>7s} {'IN 1k':>6s} {'IN 180':>7s} "
        f"{'OUT raw':>8s} {'OUT 1k':>7s} {'OUT 180':>8s} "
        f"{'T(180)':>7s} {'wid[ms]':>8s} {'Δv':>6s}"
    )
    print(f"\n=== {label} ===\n")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        phase = "burn-in" if r["drop"] in BURN_IN else "rec"
        print(
            f"{r['drop']:4d} {r['signal']:4d} {phase:>7s} {r['t_imp_ms']:6.2f} "
            f"{r['in_raw_g']:7.0f} {r['in_1000_g']:6.0f} {r['in_180_g']:7.0f} "
            f"{r['out_raw_g']:8.0f} {r['out_1000_g']:7.0f} {r['out_180_g']:8.0f} "
            f"{r['transmiss']:7.2f} {r['in_width_ms']:8.2f} {r['in_dv_ms']:6.2f}"
        )
    summarize("ALL 8 drops", rows)
    summarize("BURN-IN (drops 1-3)", subset(rows, BURN_IN))
    summarize("RECORDED (drops 4-8)", subset(rows, RECORDED))


def main() -> int:
    rows, traces = analyze_run(RAW, SIGNAL_TO_DROP, "burn_in_wax_Signal{sig}.csv")
    report("burn-in wax key-seat (this run, prc1kn)", rows)

    # prior wax-retainer run WITHOUT burn-in, for comparison
    prior_rows, _prior_traces = analyze_run(
        PRIOR_RAW, PRIOR_SIGNAL_TO_DROP, "key_mounted_wax_Signal{sig}.csv"
    )
    if prior_rows:
        print("\n\n=== prior wax-retainer run, NO burn-in (5 drops, prc1kn) ===")
        summarize("all 5 drops", prior_rows)

    drops = np.array([r["drop"] for r in rows], float)
    ins = [r["in_180_g"] for r in rows]
    outs = [r["out_180_g"] for r in rows]
    ts = [r["transmiss"] for r in rows]

    # ---- Fig 1: input vs output impact window, 8 drops overlaid -----
    fig, ax = plt.subplots(figsize=(10, 5))
    for drop in sorted(traces):
        t, _c5, c5_180, _rr, res_180, i_imp, _fs = traces[drop]
        t0 = t[i_imp] * 1e3
        w = (t * 1e3 > t0 - 4) & (t * 1e3 < t0 + 10)
        burn = drop in BURN_IN
        ax.plot(t[w] * 1e3, c5_180[w], lw=1.0, color="tab:blue",
                alpha=0.35 if burn else 0.7, ls="--" if burn else "-",
                label="input CH5 (base, wax)" if drop == 1 else None)
        ax.plot(t[w] * 1e3, res_180[w], lw=1.0, color="tab:red",
                alpha=0.35 if burn else 0.7, ls="--" if burn else "-",
                label="output |tri-axis| (key-seat + wax)" if drop == 1 else None)
    ax.plot([], [], color="0.4", ls="--", label="burn-in (drops 1-3)")
    ax.plot([], [], color="0.4", ls="-", label="recorded (drops 4-8)")
    ax.set(xlabel="time (ms)", ylabel="CFC-180 a (G)",
           title=f"{SPECIMEN}: input vs output CFC-180 — burn-in (dashed) vs recorded (solid)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_input_output_impact.png", dpi=130)
    plt.close(fig)

    # ---- Fig 2: drift — input, output, T per drop, burn-in shaded ---
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    for ax in (a1, a2):
        ax.axvspan(0.5, 3.5, color="0.85", label="burn-in (discarded)")
    a1.plot(drops, ins, "o-", color="tab:blue", label="input CH5")
    a1.plot(drops, outs, "s-", color="tab:red", label="output tri-axis")
    a1.set(xlabel="drop #", ylabel="CFC-180 peak |g| (G)",
           title="Input / output peak per drop", xticks=range(1, 9))
    a1.legend()
    a1.grid(alpha=0.3)
    a2.plot(drops, ts, "D-", color="tab:purple")
    # OLS on recorded-only vs all-8
    rec = np.array(RECORDED, float)
    rec_ts = [r["transmiss"] for r in subset(rows, RECORDED)]
    sl_r, p_r = ols(rec, rec_ts)
    a2.plot(rec, np.polyval(np.polyfit(rec, rec_ts, 1), rec), "-", color="tab:green", lw=2,
            label=f"recorded OLS {sl_r:+.4f}/drop (p={p_r:.2f})")
    sl_a, p_a = ols(drops, ts)
    a2.plot(drops, np.polyval(np.polyfit(drops, ts, 1), drops), "--", color="0.5",
            label=f"all-8 OLS {sl_a:+.4f}/drop (p={p_a:.2f})")
    a2.axhline(1.0, color="0.4", ls=":", lw=1)
    a2.set(xlabel="drop #", ylabel="T = OUT/IN (CFC-180)",
           title="Transmissibility per drop", xticks=range(1, 9))
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig.suptitle(f"{SPECIMEN}: burn-in wax — does creep flatten after drops 1-3?")
    fig.tight_layout()
    fig.savefig(FIG / "02_drift_per_drop.png", dpi=130)
    plt.close(fig)

    # ---- Fig 3: burn-in vs prior no-burn-in output-per-drop ---------
    if prior_rows:
        pdrops = np.array([r["drop"] for r in prior_rows], float)
        pout = [r["out_180_g"] for r in prior_rows]
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.axvspan(0.5, 3.5, color="0.85", label="this-run burn-in (discarded)")
        ax.plot(pdrops, pout, "s--", color="0.55",
                label="prior wax run, NO burn-in (drops 1-5)")
        ax.plot(drops, outs, "s-", color="tab:red",
                label="this run, fresh wax + burn-in (drops 1-8)")
        ax.set(xlabel="drop # (since fresh wax applied)", ylabel="output CFC-180 peak |g| (G)",
               title=f"{SPECIMEN}: output creep — burn-in vs no-burn-in", xticks=range(1, 9))
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(FIG / "04_burnin_vs_noburnin.png", dpi=130)
        plt.close(fig)

    # ---- Fig 3: output PSD (recorded drop 4) ------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    _t, _c5, _c5180, res_raw, _r180, _i, fs = traces[4]
    f, pxx = signal.welch(res_raw, fs, nperseg=4096)
    ax.semilogy(f, pxx, lw=0.9, color="tab:red", label="output (vertex key-seat + wax)")
    ax.axvline(1650, color="tab:blue", ls="--", lw=1, label="CFC 1000 (1650 Hz)")
    ax.axvline(300, color="0.4", ls="--", lw=1, label="CFC 180 (300 Hz)")
    ax.set(xlabel="frequency (Hz)", ylabel="PSD (G²/Hz)", xlim=(0, 25000),
           title=f"{SPECIMEN} output (tri-axis resultant) PSD — recorded drop 4")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_output_psd.png", dpi=130)
    plt.close(fig)

    print(f"\nwrote figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
