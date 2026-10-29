#!/usr/bin/env python3
"""Per-drop payload-protection metrics from the campaign TP4 waveforms.

Answers the PR #111 question (sgbaird, 2026-09-23): what happens if the
objective is not the peak of the initial transmitted shock but the
maximum acceleration sustained over a longer, organ-relevant averaging
window; the car-crash distinction between the structure-borne shock wave
and the slower bulk deceleration a payload's "internal organs" feel.

For every capture this script first reproduces the campaign pipeline's
own metrics bit-for-bit (same code path as ``analyze_capture`` in
``scripts/analysis/drop_test_abc123_blind_analysis.py`` on the
``copilot/add-drop-test-protocol-again`` branch: tail baseline, SAE J211
CFC-180/CFC-1000 2-pole ``filtfilt`` Butterworth at the native 1.25 MHz,
tri-axis resultant, +-5 ms peak window, ringdown/second-event fit) so
the new columns can be cross-checked against the committed drop-results
tables, then adds the windowed dose metrics, all computed on a 50 kHz
decimated copy (FIR ``scipy.signal.decimate``, factor 25) where the
low-frequency filters are numerically safe:

* ``out_avg{W}ms_g`` / ``in_avg{W}ms_g``: maximum over the record of the
  W-ms moving average of the CFC-1000-filtered resultant (top tri-axis)
  and |CH5|, W in {1, 3, 5, 10, 15, 36} ms. The 36 ms window is the
  HIC36 timescale; 3 ms matches the automotive chest-clip timescale.
* ``out_clip3ms_g``: the classic 3 ms clip (highest level sustained
  continuously for 3 ms = max of the 3 ms moving *minimum*).
* ``hic15_out``, ``hic36_out`` (and ``_in``): the Head Injury Criterion
  functional max (t2-t1) [mean a]^2.5 over windows up to 15/36 ms
  (a in g, t in s). Reported as the standard functional; no injury-limit
  reading is implied for a 20 g structure.
* ``out_cfc60_g``, ``t60``: the CFC-60 (100 Hz) extension of the
  campaign's own t1000 -> t180 filter ladder, the "bulk deceleration"
  band fully below the 300-550 Hz structural mode.
* ``late_avg3ms_g``, ``late_avg10ms_g``, ``t_late_ms``: the same moving
  averages restricted to >= 15 ms after impact - the severity of the
  *second* event (the specimen-hop landing), i.e. what remains once the
  initial shock is excluded outright.
* ``tavg{W}ms`` = out/in ratio per window (rig-normalized
  transmissibility analogue), plus ``hic15_ratio``.

Validity and aggregation follow the campaign SOP exactly: a capture is
valid if raw CH5 >= 150 G, the first two valid drops are warm-up and are
excluded from specimen aggregates (computed downstream).

Usage:
    python compute_drop_metrics.py --raw /tmp/waveforms \
        --out data/per-drop-payload-metrics.csv [--procs 4]
"""
from __future__ import annotations

import argparse
import csv
import multiprocessing
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate, signal as sig, stats

GRAVITY = 9.80665
TP4_HEADER_LINES = 9
PRETRIGGER_S = 0.0019
SEARCH_S = 0.015
HALF_WIN_S = 0.005
DV_TOTAL_S = 0.015
TRIGGER_LEVEL_G = 150.0
FULL_SCALE_G = {"CH2": 500.0, "CH3": 500.0, "CH4": 500.0, "CH5": 500.0}

# ringdown/second-event constants, verbatim from the abc123 pipeline
RING_DECIM = 25
RING_BAND_HZ = (300.0, 900.0)
RING_T0_S = 0.001
RING_T1_S = 0.014
RING_RISE_DB = 2.0
SECOND_EVENT_SEARCH_S = 0.070
SECOND_EVENT_DB = -6.0

TOP_COLS = (0, 1, 2)
CH5 = 3

DECIM = 25                      # 1.25 MHz -> 50 kHz for the dose metrics
WINDOWS_MS = (1, 3, 5, 10, 15, 36)
LATE_START_S = 0.015            # "beyond the initial shock": >= 15 ms after impact
HIC_WIDTH_STEP_S = 0.0002      # scan HIC window widths on a 0.2 ms grid
SRS_FN_HZ = (30, 60, 120, 250, 520, 1000)   # SDOF "payload/organ" frequencies
SRS_Q = 10.0                    # MIL-STD-810 convention (zeta = 5 %)


# ---------------------------------------------------------------- legacy path
def cfc_filter(x, fs, cfc):
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = sig.butter(2, cutoff / (fs / 2.0), btype="low")
    return sig.filtfilt(b, a, x)


def parse_capture(path: Path):
    ev = None
    with open(path, "r", encoding="latin-1") as fh:
        first = fh.readline()
        if "Series Table" in first:
            raise ValueError("series table, not a time-domain capture")
        for _ in range(TP4_HEADER_LINES - 1):
            line = fh.readline()
            if line.startswith("EventTime:"):
                ev = datetime.strptime(line.split(":", 1)[1].strip(),
                                       "%m/%d/%Y %I:%M:%S %p")
    d = pd.read_csv(path, skiprows=TP4_HEADER_LINES, header=None,
                    usecols=(0, 1, 2, 3, 4), dtype=float).to_numpy()
    return d[:, 0], d[:, 1:], ev


def windowed_peak(t, a_g, i_imp, dt, half_s=HALF_WIN_S):
    half = max(1, int(half_s / dt))
    lo0, hi0 = max(0, i_imp - half), min(len(a_g), i_imp + half)
    seg = a_g[lo0:hi0]
    j = int(np.argmax(np.abs(seg)))
    idx = lo0 + j
    peak = a_g[idx]
    thr = abs(peak) / 2.0
    s = np.sign(peak)
    over = (s * a_g) >= thr
    lo = idx
    while lo > lo0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < hi0 - 1 and over[hi + 1]:
        hi += 1
    dv = integrate.trapezoid(a_g[lo:hi + 1] * GRAVITY, t[lo:hi + 1])
    return {"peak_abs_g": float(abs(peak)), "t_peak_ms": float(t[idx] * 1e3),
            "pulse_width_ms": float((t[hi] - t[lo]) * 1e3),
            "delta_v_ms": float(abs(dv)), "i_peak": idx}


def ringdown_fit(tri, i_imp, fs):
    q = RING_DECIM
    fsd = fs / q
    y = np.stack([sig.decimate(tri[:, c] - tri[:, c].mean(), q, ftype="fir")
                  for c in range(tri.shape[1])], axis=1)
    b, a = sig.butter(4, [RING_BAND_HZ[0] / (fsd / 2), RING_BAND_HZ[1] / (fsd / 2)],
                      btype="band")
    y = sig.filtfilt(b, a, y, axis=0)
    an = sig.hilbert(y, axis=0)
    env_all = np.sqrt((np.abs(an) ** 2).sum(1))

    k = int(round(i_imp / q))
    k0 = k + int(RING_T0_S * fsd)
    k1n = k + int(RING_T1_S * fsd)
    if k1n >= len(env_all) - 2:
        return {}

    pk = float(env_all[k:k0 + 1].max())
    ks = k + int(0.015 * fsd)
    ke = min(len(env_all), k + int(SECOND_EVENT_SEARCH_S * fsd))
    tail = env_all[ks:ke]
    j = int(np.argmax(tail))
    t_second_ms = 1e3 * (ks - k + j) / fsd
    second_rel_db = 20.0 * np.log10(max(tail[j], 1e-9) / max(pk, 1e-9))

    seg = env_all[k0:k1n]
    run_min = np.minimum.accumulate(seg)
    rise = np.where(seg > run_min * 10 ** (RING_RISE_DB / 20.0))[0]
    k1 = k0 + (int(rise[0]) if len(rise) and rise[0] > int(0.004 * fsd) else len(seg))
    if k1 - k0 < int(0.004 * fsd):
        k1 = k0 + int(0.004 * fsd)

    chan = int(np.argmax((y[k0:k1] ** 2).sum(0)))
    env = np.abs(an[:, chan])
    ph = np.unwrap(np.angle(an[:, chan]))
    tt = np.arange(len(env)) / fsd
    rf = stats.linregress(tt[k0:k1], ph[k0:k1])
    fn = float(rf.slope / (2 * np.pi))
    re_ = stats.linregress(tt[k0:k1], np.log(np.maximum(env[k0:k1], 1e-9)))
    sigma = float(-re_.slope)
    zeta = 100.0 * sigma / (2 * np.pi * fn) if fn > 0 else float("nan")
    return {"fn_hz": fn, "zeta_pct": float(zeta), "ring_r2": float(re_.rvalue ** 2),
            "t_second_ms": float(t_second_ms), "second_rel_db": float(second_rel_db)}


# ------------------------------------------------------------- dose metrics
def moving_avg_max(x, fsd, win_s, start=0):
    n = int(round(win_s * fsd))
    if n < 1 or n > len(x) - start:
        return float("nan"), float("nan")
    c = np.convolve(x[start:], np.ones(n) / n, mode="valid")
    j = int(np.argmax(c))
    return float(c[j]), float((start + j + 0.5 * n) / fsd)


def clip_level(x, fsd, win_s):
    """Highest level sustained continuously for win_s (moving-minimum max)."""
    from scipy.ndimage import minimum_filter1d
    n = int(round(win_s * fsd))
    if n < 1 or n > len(x):
        return float("nan")
    mm = minimum_filter1d(x, size=n, mode="nearest")
    h = n // 2
    return float(mm[h:len(x) - h].max()) if len(x) > 2 * h else float(mm.max())


def hic(x, fsd, max_win_s):
    """max over windows (t2-t1) <= max_win_s of (t2-t1) * mean(a)^2.5."""
    cs = np.concatenate([[0.0], np.cumsum(x)]) / fsd
    best = 0.0
    step = max(1, int(round(HIC_WIDTH_STEP_S * fsd)))
    for n in range(step, int(round(max_win_s * fsd)) + 1, step):
        if n >= len(x):
            break
        w = n / fsd
        means = (cs[n:] - cs[:-n]) / w
        m = float(means.max())
        val = w * m ** 2.5
        if val > best:
            best = val
    return float(best)


def srs_maximax(x_axes, fsd, fn):
    """Absolute-acceleration maximax SRS via the Smallwood ramp-invariant
    filter (ISO 18431-4 / MIL-STD-810 practice), Q = SRS_Q. ``x_axes`` is
    (n, k): each signed axis drives its own SDOF; the max over axes and
    time is returned (dominant-axis convention)."""
    zeta = 1.0 / (2.0 * SRS_Q)
    dt = 1.0 / fsd
    wn = 2 * np.pi * fn
    wd = wn * np.sqrt(1 - zeta ** 2)
    E = np.exp(-zeta * wn * dt)
    K = wd * dt
    C = E * np.cos(K)
    S = E * np.sin(K)
    Sp = S / K
    b = [1 - Sp, 2 * (Sp - C), E * E - Sp]
    a = [1.0, -2 * C, E * E]
    best = 0.0
    for c in range(x_axes.shape[1]):
        r = sig.lfilter(b, a, x_axes[:, c])
        best = max(best, float(np.max(np.abs(r))))
    return best


def dose_metrics(top, ch5, i_imp, fs):
    """Windowed metrics on 50 kHz decimated, CFC-1000-filtered signals."""
    fsd = fs / DECIM
    topd = np.stack([sig.decimate(top[:, c], DECIM, ftype="fir")
                     for c in range(3)], axis=1)
    ch5d = sig.decimate(ch5, DECIM, ftype="fir")
    kimp = int(round(i_imp / DECIM))

    def lp(x, hz, order=2):
        sos = sig.butter(order, hz / (fsd / 2), btype="low", output="sos")
        return sig.sosfiltfilt(sos, x)

    # CFC-1000 resultant (J211 convention) for the dose metrics
    out_1000 = np.sqrt(np.sum(np.stack([lp(topd[:, c], 1650.0)
                                        for c in range(3)], 1) ** 2, axis=1))
    in_1000 = np.abs(lp(ch5d, 1650.0))
    # CFC-60 = the 100 Hz rung of the pipeline's own filter ladder
    out_60 = np.sqrt(np.sum(np.stack([lp(topd[:, c], 100.0)
                                      for c in range(3)], 1) ** 2, axis=1))
    in_60 = np.abs(lp(ch5d, 100.0))

    ns = int(SEARCH_S * fsd)
    row = {
        "out_cfc60_g": float(out_60[:max(ns, kimp + int(0.010 * fsd))].max()),
        "in_cfc60_g": float(in_60[:max(ns, kimp + int(0.010 * fsd))].max()),
    }
    row["t60"] = row["out_cfc60_g"] / row["in_cfc60_g"]

    for w in WINDOWS_MS:
        ov, ot = moving_avg_max(out_1000, fsd, w * 1e-3)
        iv, _ = moving_avg_max(in_1000, fsd, w * 1e-3)
        row[f"out_avg{w}ms_g"] = ov
        row[f"in_avg{w}ms_g"] = iv
        row[f"tavg{w}ms"] = ov / iv if iv else float("nan")
        if w == 10:
            row["t_at_out_avg10_ms"] = (ot - kimp / fsd) * 1e3
    row["out_clip3ms_g"] = clip_level(out_1000, fsd, 3e-3)
    row["in_clip3ms_g"] = clip_level(in_1000, fsd, 3e-3)
    row["hic15_out"] = hic(out_1000, fsd, 15e-3)
    row["hic36_out"] = hic(out_1000, fsd, 36e-3)
    row["hic15_in"] = hic(in_1000, fsd, 15e-3)
    row["hic36_in"] = hic(in_1000, fsd, 36e-3)
    row["hic15_ratio"] = row["hic15_out"] / row["hic15_in"] if row["hic15_in"] else float("nan")

    for fn in SRS_FN_HZ:
        so = srs_maximax(topd, fsd, fn)
        si = srs_maximax(ch5d[:, None], fsd, fn)
        row[f"srs{fn}_out_g"] = so
        row[f"srs{fn}_in_g"] = si
        row[f"srs{fn}_ratio"] = so / si if si else float("nan")

    late0 = kimp + int(LATE_START_S * fsd)
    if late0 < len(out_1000) - int(0.010 * fsd):
        lv3, lt = moving_avg_max(out_1000, fsd, 3e-3, start=late0)
        lv10, _ = moving_avg_max(out_1000, fsd, 10e-3, start=late0)
        row["late_avg3ms_g"] = lv3
        row["late_avg10ms_g"] = lv10
        row["t_late_ms"] = (lt - kimp / fsd) * 1e3
    return row


# ------------------------------------------------------------------ per file
def analyze(path: Path) -> dict:
    t, ch, ev = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(PRETRIGGER_S / dt))

    base = np.median(ch[int(0.070 / dt):], axis=0)      # tail baseline (SOP)
    top = ch[:, TOP_COLS] - base[list(TOP_COLS)]
    ch5 = ch[:, CH5] - base[CH5]

    ns = int(SEARCH_S / dt)
    ch5_180 = cfc_filter(ch5, fs, 180)
    ch5_1000 = cfc_filter(ch5, fs, 1000)
    i_imp = int(np.argmax(np.abs(ch5_180[:ns])))

    in180 = windowed_peak(t, ch5_180, i_imp, dt)
    in1000 = windowed_peak(t, ch5_1000, i_imp, dt)
    raw = windowed_peak(t, ch5, i_imp, dt)

    top180 = np.sqrt(np.sum(np.stack([cfc_filter(top[:, c], fs, 180)
                                      for c in range(3)], 1) ** 2, axis=1))
    top1000 = np.sqrt(np.sum(np.stack([cfc_filter(top[:, c], fs, 1000)
                                       for c in range(3)], 1) ** 2, axis=1))
    o180 = windowed_peak(t, top180, i_imp, dt)
    o1000 = windowed_peak(t, top1000, i_imp, dt)

    j0 = max(0, i_imp - int(0.002 / dt))
    j1 = min(len(t), i_imp + int(DV_TOTAL_S / dt))
    dv_tot = float(abs(integrate.trapezoid(ch5_180[j0:j1] * GRAVITY, t[j0:j1])))

    row = {
        # last SignalN in the stem: the r2d2c8 Box upload nests its captures
        # as "..._Signal9_SignalN.csv", so the first match is not the event
        "signal": int(re.findall(r"Signal(\d+)", path.stem)[-1]),
        "event_time": ev.isoformat() if ev else None,
        "in_raw_g": raw["peak_abs_g"],
        "in_180_g": in180["peak_abs_g"],
        "in_1000_g": in1000["peak_abs_g"],
        "in_width_ms": in180["pulse_width_ms"],
        "in_dv_ms": dv_tot,
        "out_raw_g": float(np.max(np.sqrt(np.sum(top ** 2, axis=1))[:ns])),
        "out_180_g": o180["peak_abs_g"],
        "out_1000_g": o1000["peak_abs_g"],
        "t180": o180["peak_abs_g"] / in180["peak_abs_g"],
        "t1000": o1000["peak_abs_g"] / in1000["peak_abs_g"],
    }
    row.update(ringdown_fit(top, i_imp, fs))
    if np.isfinite(row.get("t_second_ms", np.nan)) and dv_tot > 0:
        row["e_rebound"] = float(GRAVITY * row["t_second_ms"] * 1e-3 / (2.0 * dv_tot))
    row.update(dose_metrics(top, ch5, i_imp, fs))
    return row


def one_file(args):
    batch, spec, path = args
    try:
        row = analyze(path)
    except Exception as e:                      # noqa: BLE001
        return {"batch": batch, "specimen": spec, "file": path.name, "error": str(e)}
    row.update({"batch": batch, "specimen": spec, "file": path.name})
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("/tmp/waveforms"))
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "data" / "per-drop-payload-metrics.csv")
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()

    jobs = []
    for batch_dir in sorted(args.raw.iterdir()):
        if not batch_dir.is_dir():
            continue
        for spec_dir in sorted(batch_dir.iterdir()):
            m = re.search(r"(r2d2c\d|drran\d|2dran\d|corny\d)", spec_dir.name, re.I)
            spec = m.group(1).lower() if m else spec_dir.name.lower()
            sigs = sorted(spec_dir.glob("*Signal*.csv"),
                          key=lambda p: int(re.findall(r"Signal(\d+)", p.stem)[-1]))
            jobs.extend((batch_dir.name, spec, p) for p in sigs)
    print(f"{len(jobs)} captures")

    with multiprocessing.Pool(args.procs) as pool:
        rows = []
        for n, row in enumerate(pool.imap(one_file, jobs, chunksize=4), 1):
            rows.append(row)
            if n % 100 == 0 or n == len(jobs):
                print(f"  {n}/{len(jobs)}", flush=True)

    errs = [r for r in rows if "error" in r]
    for r in errs:
        print(f"  !! {r['specimen']} {r['file']}: {r['error']}")
    rows = [r for r in rows if "error" not in r]

    cols = ["batch", "specimen", "signal", "file", "event_time"]
    rest = sorted({k for r in rows for k in r} - set(cols))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols + rest)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["batch"], r["specimen"], r["signal"])):
            w.writerow(r)
    print(f"-> {args.out}  ({len(rows)} rows, {len(errs)} errors)")


if __name__ == "__main__":
    main()
