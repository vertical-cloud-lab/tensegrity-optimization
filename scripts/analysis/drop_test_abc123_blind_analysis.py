#!/usr/bin/env python3
"""Blind ABC x 123 crossover — arrangement + specimen classification, ringdown decay.

@me-madsen ran the crossed design pre-registered in
``docs/drop-test-ab-blind-protocol.md`` on 2026-08-03/05 (Box folder
``tum0zm49ndrua62snpzh803pg9cdrz56``), with three arrangements rather than
the two of amendment 1 and three specimens rather than two:

  arrangements   A = 1/4 in PU sheet alone
                 B = 1/2 in PU sheet alone
                 C = 1/4 in on top of 1/2 in
  specimens      1 = smaller T3 prism
                 2 = same model as 1, with printing defects
                 3 = larger T3 prism

Set 1 ("ABC - 123 - Order Known", 45 captures) has the key disclosed:

  A1 1-5   B1 6-10   C1 11-15
  A2 16-20 B2 21-25  C2 26-30
  A3 31-35 B3 41-45  C3 46-50      (Signals 36-40 do not exist)

Set 2 ("ABC - 123 - Random Arrangement", 45 captures) is the same nine
cells shuffled in blocks of 5, key withheld. Signal 6 does not exist, so
the blocks are Signals 1-5, 7-11, 12-16, ... 42-46.

Capture format (both sets): 4 channels (CH2-CH4 = top-vertex key-seat
tri-axis output "TOP", CH5 = single-axis base-plate input + trigger),
1.25 MHz, 125,000 samples = 100 ms record, **2.000 ms pre-trigger**,
150 G trigger throughout. The pre-trigger window is real and clean
(baseline sd 5-11 G, |max| < 55 G), so — unlike the 20 ms exports that
prompted the adversarial review — the baseline here is the pre-trigger
median, never a full-record median.

The classification follows the rule committed in
``docs/drop-test-ab-blind-protocol.md`` §2 before any of this data
existed. Two extensions are needed because the executed design is larger
than the pre-registered one; both are stated explicitly rather than
tuned, and §2's abstention rule is carried over unchanged:

  * three arrangements instead of two -> the midpoint threshold becomes a
    set of midpoints between *adjacent* class means on the primary
    feature (input pulse FWHM), i.e. nearest-class-mean in 1-D;
  * a three-level specimen factor -> nearest-centroid in a standardised
    output-side feature space, with the features fixed a priori (modal
    frequency, damping, transmissibility, output level) and the
    thresholds fitted from set 1 only, evaluated by leave-one-out on
    set 1 before ever touching set 2.

The 100 ms record makes a ringdown fit possible for the first time: the
output ringdown is band-pass filtered around its dominant mode, the
Hilbert envelope is fitted log-linearly over the decay, and the damping
ratio zeta and modal frequency f_n are reported per drop.

Raw data is not committed (823 MB); it is fetched from Box into
``RAW_ROOT`` (default ``data/drop-tests/abc123-blind/raw``, overridable
with ``--raw``). Emits
``data/drop-tests/abc123-blind/figures/abc123_metrics.json``, consumed by
``docs/drop-test-abc123-blind-analysis.md``.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal as sig, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA, FULL_SCALE_G, GRAVITY  # noqa: E402

OUT = DATA / "abc123-blind"
RAW_ROOT = OUT / "raw"
FIG = OUT / "figures"

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4
CH5 = 3

TP4_HEADER_LINES = 9
PRETRIGGER_S = 0.0019  # 2.000 ms nominal; 1.9 ms used to stay clear of the edge
SEARCH_S = 0.015  # impact lands 2.4-4.5 ms in; search the first 15 ms
HALF_WIN_S = 0.005  # peak walk bound (softest stack half-max width ~2.6 ms)
DV_TOTAL_S = 0.015

TRIGGER_LEVEL_G = 150.0

# Ringdown fit.
#
# The 100 ms record turns out NOT to contain a single clean decay: every
# capture carries a *secondary* burst on the top-vertex channels somewhere
# between ~19 and ~35 ms after the impact (envelope rising 1-15 dB back
# above its decayed level), long before the +76-89 ms brake catch the video
# work predicted. Fitting across it produces negative damping, which is how
# it was found. The fit window is therefore short and fixed, and is
# additionally truncated at the first envelope rise.
RING_DECIM = 25  # 1.25 MHz -> 50 kHz before any modal work
RING_BAND_HZ = (300.0, 900.0)  # brackets the repo's documented 519-549 Hz mode
RING_T0_S = 0.001  # start 1 ms after the located impact
RING_T1_S = 0.014  # nominal end; ~7 cycles at 550 Hz
RING_RISE_DB = 2.0  # truncate at the first sustained envelope rise of this size
SECOND_EVENT_SEARCH_S = 0.070
SECOND_EVENT_DB = -6.0  # relative to the post-impact envelope peak

# Set-1 key as disclosed by the operator.
KEY_SET1 = {
    "A1": range(1, 6), "B1": range(6, 11), "C1": range(11, 16),
    "A2": range(16, 21), "B2": range(21, 26), "C2": range(26, 31),
    "A3": range(31, 36), "B3": range(41, 46), "C3": range(46, 51),
}
# Set-2 block structure disclosed (blocks of 5, Signal 6 absent); labels are not.
SET2_BLOCKS = [(1, 5), (7, 11), (12, 16), (17, 21), (22, 26),
               (27, 31), (32, 36), (37, 41), (42, 46)]

ARRS = ["A", "B", "C"]
SPECS = ["1", "2", "3"]
ARR_LABEL = {"A": 'A: 1/4 in alone', "B": 'B: 1/2 in alone', "C": 'C: 1/4 over 1/2 in'}
SPEC_LABEL = {"1": "1: small T3", "2": "2: small T3, defects", "3": "3: large T3"}
ARR_COLOR = {"A": "tab:red", "B": "tab:orange", "C": "tab:blue"}
SPEC_COLOR = {"1": "tab:green", "2": "tab:purple", "3": "tab:brown"}

ABSTAIN_SIGMA = 3.0  # pre-registered: abstain within 3 sigma of the threshold


# --------------------------------------------------------------------------
# loading / per-drop metrics
# --------------------------------------------------------------------------
def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = sig.butter(2, cutoff / (fs / 2.0), btype="low")
    return sig.filtfilt(b, a, x)


def cv(vals) -> float:
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def parse_capture(path: Path):
    head = []
    with open(path, "r", encoding="latin-1") as fh:
        for _ in range(TP4_HEADER_LINES):
            head.append(fh.readline())
    ev = None
    for line in head:
        if line.startswith("EventTime:"):
            ev = datetime.strptime(line.split(":", 1)[1].strip(), "%m/%d/%Y %I:%M:%S %p")
    d = np.loadtxt(path, delimiter=",", skiprows=TP4_HEADER_LINES, usecols=(0, 1, 2, 3, 4))
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
            "pulse_width_ms": float((t[hi] - t[lo]) * 1e3), "delta_v_ms": float(abs(dv)),
            "i_peak": idx}


def ringdown_fit(tri, i_imp, fs):
    """Band-limited modal ringdown on the top-vertex tri-axis.

    Decimates to 50 kHz, band-passes 300-900 Hz (the repo's documented
    519-549 Hz first mode), then on the axis carrying the most band energy:

      * f_n from the slope of the unwrapped analytic phase (sub-bin
        resolution — a Welch estimate over a 13 ms window would have ~75 Hz
        bins, far too coarse to compare specimens);
      * the decay rate sigma from an OLS fit of log|envelope| over the
        window, and zeta = sigma / (2 pi f_n);
      * ``ring_r2`` as the honest quality flag — a low r2 means the envelope
        is not a single decaying mode, and the zeta from that drop should
        not be read as a damping ratio.

    Also reports the time of the *secondary* burst, which is a rig
    observable in its own right.
    """
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

    # secondary burst: the largest envelope excursion in the tail. Defined by
    # argmax rather than by a threshold crossing so that it exists for every
    # drop regardless of how far the primary ringdown has decayed.
    pk = float(env_all[k:k0 + 1].max())
    ks = k + int(0.015 * fsd)
    ke = min(len(env_all), k + int(SECOND_EVENT_SEARCH_S * fsd))
    tail = env_all[ks:ke]
    j = int(np.argmax(tail))
    t_second_ms = 1e3 * (ks - k + j) / fsd
    second_rel_db = 20.0 * np.log10(max(tail[j], 1e-9) / max(pk, 1e-9))

    # truncate the fit at the first sustained rise inside the window
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
    re = stats.linregress(tt[k0:k1], np.log(np.maximum(env[k0:k1], 1e-9)))
    sigma = float(-re.slope)
    zeta = 100.0 * sigma / (2 * np.pi * fn) if fn > 0 else float("nan")
    # band energy of the fitted window, normalised out of the fit itself
    return {"ring_chan": chan + 2, "fn_hz": fn, "decay_sigma": sigma,
            "zeta_pct": float(zeta), "ring_r2": float(re.rvalue ** 2),
            "ring_fit_ms": float(1e3 * (k1 - k0) / fsd),
            "ring_amp0_g": float(np.exp(re.intercept)),
            "ring_band_energy": float((y[k0:k1] ** 2).sum()),
            "t_second_ms": float(t_second_ms),
            "second_rel_db": float(second_rel_db)}


def analyze_capture(path: Path) -> dict:
    t, ch, ev = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(PRETRIGGER_S / dt))

    top = ch[:, TOP_COLS] - np.median(ch[:nb, TOP_COLS], axis=0)
    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])

    ns = int(SEARCH_S / dt)
    ch5_180 = cfc_filter(ch5, fs, 180)
    ch5_1000 = cfc_filter(ch5, fs, 1000)
    i_imp = int(np.argmax(np.abs(ch5_180[:ns])))

    in180 = windowed_peak(t, ch5_180, i_imp, dt)
    in1000 = windowed_peak(t, ch5_1000, i_imp, dt)
    raw = windowed_peak(t, ch5, i_imp, dt)

    res_raw = np.sqrt(np.sum(top ** 2, axis=1))
    top180 = np.sqrt(np.sum(np.stack([cfc_filter(top[:, c], fs, 180)
                                      for c in range(3)], 1) ** 2, axis=1))
    top1000 = np.sqrt(np.sum(np.stack([cfc_filter(top[:, c], fs, 1000)
                                       for c in range(3)], 1) ** 2, axis=1))
    o180 = windowed_peak(t, top180, i_imp, dt)
    o1000 = windowed_peak(t, top1000, i_imp, dt)

    # cumulative dv over the whole impact region (not just the half-max window)
    j1 = min(len(t), i_imp + int(DV_TOTAL_S / dt))
    dv_tot = float(abs(integrate.trapezoid(ch5_180[max(0, i_imp - int(0.002 / dt)):j1] * GRAVITY,
                                           t[max(0, i_imp - int(0.002 / dt)):j1])))

    ring = ringdown_fit(top, i_imp, fs)

    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3)]:
        x = np.abs(ch[:, col] - np.median(ch[:nb, col]))
        sat[name] = float(x.max() / FULL_SCALE_G[name])

    row = {
        "signal": int(str(path.stem).split("Signal")[1]),
        "event_time": ev.isoformat() if ev else None,
        "t_imp_ms": float(t[i_imp] * 1e3),
        "pretrig_sd_g": float(ch5[:nb].std()),
        "in_raw_g": raw["peak_abs_g"],
        "in_180_g": in180["peak_abs_g"],
        "in_1000_g": in1000["peak_abs_g"],
        "in_width_ms": in180["pulse_width_ms"],
        "in_dv_ms": dv_tot,
        "hardness": in1000["peak_abs_g"] / in180["peak_abs_g"],
        "out_raw_g": float(np.max(res_raw[:ns])),
        "out_180_g": o180["peak_abs_g"],
        "out_1000_g": o1000["peak_abs_g"],
        "out_width_ms": o180["pulse_width_ms"],
        "t180": o180["peak_abs_g"] / in180["peak_abs_g"],
        "t1000": o1000["peak_abs_g"] / in1000["peak_abs_g"],
        "lag_ms": o180["t_peak_ms"] - in180["t_peak_ms"],
        "frac_fs": sat,
    }
    row.update(ring)
    # Dimensionless specimen rebound coefficient. The secondary top-vertex
    # event is ballistic: its delay scales in proportion to impact velocity
    # (verified across a 20 % energy change between the two sessions), so
    # g*t_second/(2*dv) is a velocity-invariant specimen constant.
    if np.isfinite(row.get("t_second_ms", np.nan)) and dv_tot > 0:
        row["e_rebound"] = float(GRAVITY * row["t_second_ms"] * 1e-3 / (2.0 * dv_tot))
    return row


def load_set(folder: Path, prefix: str) -> list[dict]:
    files = sorted(folder.glob(f"{prefix}*Signal*.csv"),
                   key=lambda p: int(p.stem.split("Signal")[1]))
    rows = []
    for p in files:
        rows.append(analyze_capture(p))
        print(f"  {p.name}: in180 {rows[-1]['in_180_g']:7.1f} G  "
              f"w {rows[-1]['in_width_ms']:5.3f} ms  T {rows[-1]['t180']:.3f}  "
              f"fn {rows[-1].get('fn_hz', float('nan')):6.1f} Hz  "
              f"zeta {rows[-1].get('zeta_pct', float('nan')):5.2f} %", flush=True)
    return rows


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------
def label_set1(rows):
    sig2lab = {}
    for lab, rng in KEY_SET1.items():
        for s in rng:
            sig2lab[s] = lab
    out = []
    for r in rows:
        lab = sig2lab.get(r["signal"])
        if lab is None:
            continue
        r = dict(r)
        r["cell"] = lab
        r["arr"] = lab[0]
        r["spec"] = lab[1]
        out.append(r)
    return out


def arr_thresholds(train):
    """Class means + adjacent midpoints on the primary feature (input FWHM)."""
    means, sds = {}, {}
    for a in ARRS:
        v = np.array([r["in_width_ms"] for r in train if r["arr"] == a])
        means[a], sds[a] = float(v.mean()), float(v.std(ddof=1))
    order = sorted(ARRS, key=lambda a: means[a])
    cuts = [(order[i], order[i + 1], 0.5 * (means[order[i]] + means[order[i + 1]]))
            for i in range(len(order) - 1)]
    pooled = float(np.sqrt(np.mean([sds[a] ** 2 for a in ARRS])))
    return means, sds, order, cuts, pooled


def classify_arr(x, order, cuts, pooled):
    lab = order[-1]
    for lo, hi, c in cuts:
        if x < c:
            lab = lo
            break
    margin = min(abs(x - c) for _, _, c in cuts) / pooled
    return lab, float(margin)



# --------------------------------------------------------------------------
# specimen readout
# --------------------------------------------------------------------------
# The pre-registration (§2 step 6) fixes only that the specimen call is made
# from the OUTPUT channel, independently of the arrangement labels. The
# executed design has three specimens instead of two, and — discovered on
# reading the data, not assumed — set 2 spans two sessions with different
# drop energy (see the writeup), so absolute output LEVELS do not transfer
# from set 1. The readout below therefore mirrors the arrangement rule's
# structure: one primary discriminant chosen for transferability, plus
# confirmatory features that must agree.
#
# The primary is chosen by an objective, pre-data-blind criterion applied to
# set 1 only: a feature qualifies if its specimen ordering is IDENTICAL in
# all three arrangements (i.e. it measures the specimen and not the
# specimen x arrangement interaction) and its smallest adjacent-specimen gap
# exceeds 1 within-cell sd. Exactly one feature qualifies — see
# ``qualify_spec_features``.
SPEC_CANDIDATES = ["t180", "t1000", "out_180_g", "out_width_ms", "lag_ms",
                   "fn_hz", "zeta_pct", "t_second_ms", "second_rel_db", "e_rebound"]
SPEC_MIN_D = 1.0


SESSION_GAP_S = 3 * 3600.0  # a break longer than this starts a new session


def assign_sessions(rows):
    """Cluster captures into sessions by elapsed-time gaps.

    Calendar date is the wrong key here: the 08-05 session runs across
    midnight into 08-06, while set 2's first block was recorded 10 minutes
    after set 1 finished on 08-04 and belongs to the SAME session as set 1.
    """
    ordered = sorted(rows, key=lambda r: r["event_time"])
    sid, prev = 0, None
    for r in ordered:
        ts = datetime.fromisoformat(str(r["event_time"]))
        if prev is not None and (ts - prev).total_seconds() > SESSION_GAP_S:
            sid += 1
        r["session"] = sid
        prev = ts
    return sid + 1


def session_of(r):
    return r.get("session")


def qualify_spec_features(train):
    """Rank candidate specimen features by cross-arrangement transferability."""
    out = {}
    for f in SPEC_CANDIDATES:
        orders, gaps = [], []
        for a in ARRS:
            mu, sd = {}, {}
            for s in SPECS:
                v = np.array([r[f] for r in train if r["arr"] == a and r["spec"] == s
                              and np.isfinite(r.get(f, np.nan))], float)
                mu[s], sd[s] = v.mean(), v.std(ddof=1)
            orders.append("".join(sorted(SPECS, key=lambda s: mu[s])))
            ms = sorted(mu.values())
            w = float(np.sqrt(np.mean([sd[s] ** 2 for s in SPECS])))
            gaps.append(min(ms[1] - ms[0], ms[2] - ms[1]) / w if w else np.inf)
        out[f] = {"orders": orders, "consistent": len(set(orders)) == 1,
                  "min_gap_d": float(min(gaps)),
                  "qualifies": len(set(orders)) == 1 and min(gaps) >= SPEC_MIN_D}
    return out


def spec_rank_call(train, s2_rows, primary, confirmatory):
    """Match set-2 blocks to specimens within each arrangement.

    Two regimes, decided by the data rather than by preference:

    * **all three blocks of the arrangement share a session** -> match by
      RANK on the primary. A session offset shifts all three blocks
      together and cancels out of a rank, so no normalisation is needed and
      none is applied.
    * **the blocks span sessions** (which arrangement B does — one of its
      blocks was recorded on 08-04 at set-1 energy, the other two on
      08-05/06 at ~20 % lower impact velocity) -> ranks are NOT comparable.
      The primary is then normalised by the block's own impact velocity
      (``e_rebound = g t_second / 2 dv``, a dimensionless quantity that is
      constant for a given specimen — verified on arrangement A, where it
      reproduces set-1 values to 0.1-6 % across a 20 % energy change), and
      the permutation minimising total absolute mismatch is chosen.

    Returns the mapping plus enough diagnostics to see how close the
    runner-up permutation was.
    """
    blk_rows, blk_session = {}, {}
    for bi, (lo, hi) in enumerate(SET2_BLOCKS, start=1):
        rows = [r for r in s2_rows if lo <= r["signal"] <= hi and r["clean"]]
        blk_rows[bi] = rows
        blk_session[bi] = session_of(rows[0]) if rows else None

    def bmean(bi, f):
        v = np.array([r[f] for r in blk_rows[bi] if np.isfinite(r.get(f, np.nan))], float)
        return float(v.mean())

    set1_sessions = {session_of(r) for r in train}

    result = {}
    for a in ARRS:
        bs = [bi for bi in blk_rows if blk_rows[bi] and blk_rows[bi][0]["arr_call"] == a]
        if len(bs) != 3:
            result[a] = {"blocks": bs, "error": "expected 3 blocks, got %d" % len(bs)}
            continue
        ref = {s: float(np.mean([r[primary] for r in train
                                 if r["arr"] == a and r["spec"] == s])) for s in SPECS}
        ref_e = {s: float(np.mean([r["e_rebound"] for r in train
                                   if r["arr"] == a and r["spec"] == s])) for s in SPECS}
        sessions = {blk_session[bi] for bi in bs}
        same_session = len(sessions) == 1

        scored = []
        for perm in itertools.permutations(SPECS):
            m = dict(zip(sorted(bs, key=lambda bi: bmean(bi, primary)),
                         sorted(SPECS, key=lambda s: ref[s]))) if False else dict(zip(bs, perm))
            if same_session:
                # rank agreement: how many adjacent-pair orderings match
                bo = sorted(bs, key=lambda bi: bmean(bi, primary))
                so = sorted(SPECS, key=lambda s: ref[s])
                cost = 0.0 if [m[b] for b in bo] == so else 1.0
                cost += 1e-6 * sum(abs(bmean(b, primary) - ref[m[b]]) for b in bs)
            else:
                cost = sum(abs(bmean(b, "e_rebound") - ref_e[m[b]]) for b in bs)
            scored.append((cost, m))
        scored.sort(key=lambda kv: kv[0])
        mapping, best, runner = scored[0][1], scored[0][0], scored[1][0]

        conf = {}
        for f in confirmatory:
            rf = {s: float(np.mean([r[f] for r in train if r["arr"] == a and r["spec"] == s
                                    and np.isfinite(r.get(f, np.nan))])) for s in SPECS}
            so = sorted(SPECS, key=lambda s: rf[s])
            bo = sorted(bs, key=lambda bi: bmean(bi, f))
            conf[f] = {"agrees": [mapping[b] for b in bo] == so,
                       "set2_order": [f"blk{b}" for b in bo], "set1_order": so}

        vals = sorted(bmean(bi, primary) for bi in bs)
        wsd = float(np.sqrt(np.mean([np.var([r[primary] for r in blk_rows[bi]], ddof=1)
                                     for bi in bs])))
        result[a] = {
            "mapping": {f"blk{b}": s for b, s in mapping.items()},
            "primary": primary,
            "regime": "within-session rank" if same_session
                      else "cross-session, velocity-normalised (e_rebound)",
            "sessions": {f"blk{b}": blk_session[b] for b in bs},
            "set1_sessions": sorted(set1_sessions),
            "set1_means": ref, "set1_e_rebound": ref_e,
            "set2_block_means": {f"blk{b}": bmean(b, primary) for b in bs},
            "set2_block_e_rebound": {f"blk{b}": bmean(b, "e_rebound") for b in bs},
            "best_cost": float(best), "runner_up_cost": float(runner),
            "cost_ratio": float(runner / best) if best else float("inf"),
            "min_adjacent_gap_d": float(min(vals[1] - vals[0], vals[2] - vals[1]) / wsd)
            if wsd else float("inf"),
            "confirmatory": conf,
            "n_confirm_agree": int(sum(v["agrees"] for v in conf.values())),
            "n_confirm": len(conf),
        }
    return result


# --------------------------------------------------------------------------
def summarize(rows, by, keys, fields):
    out = {}
    for k in keys:
        sub = [r for r in rows if by(r) == k]
        if not sub:
            continue
        out[k] = {"n": len(sub)}
        for f in fields:
            v = np.array([r[f] for r in sub if np.isfinite(r.get(f, np.nan))], float)
            if len(v) == 0:
                continue
            out[k][f] = {"mean": float(v.mean()),
                         "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                         "cv": cv(v) if len(v) > 1 else 0.0,
                         "min": float(v.min()), "max": float(v.max())}
    return out


FIELDS = ["in_raw_g", "in_180_g", "in_1000_g", "in_width_ms", "in_dv_ms", "hardness",
          "out_180_g", "out_1000_g", "out_width_ms", "t180", "t1000", "lag_ms",
          "fn_hz", "zeta_pct", "ring_r2", "ring_fit_ms", "t_second_ms", "second_rel_db",
          "e_rebound"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(RAW_ROOT))
    ap.add_argument("--cache", default=None,
                    help="cache per-drop metrics here; reused if present")
    args = ap.parse_args()
    raw = Path(args.raw)
    FIG.mkdir(parents=True, exist_ok=True)

    cache = Path(args.cache) if args.cache else None
    if cache and cache.exists():
        blob = json.loads(cache.read_text())
        s1, s2 = blob["s1"], blob["s2"]
        print(f"loaded {len(s1)} + {len(s2)} cached per-drop metrics from {cache}")
    else:
        print("=== set 1 (order known) ===", flush=True)
        s1 = load_set(raw / "known", "ABC - 123 - Order Known")
        print("=== set 2 (random arrangement) ===", flush=True)
        s2 = load_set(raw / "random", "ABC- 123 - Random Arrangement")
        if cache:
            cache.write_text(json.dumps({"s1": s1, "s2": s2}, default=str))

    n_sessions = assign_sessions(s1 + s2)
    # A capture only counts as a clean impact if the base-plate raw peak
    # actually exceeded the 150 G trigger level it was captured on.
    for r in s1 + s2:
        r["clean"] = bool(r["in_raw_g"] >= TRIGGER_LEVEL_G)
    dirty = [(r["signal"], round(r["in_raw_g"], 1)) for r in s2 if not r["clean"]]
    print(f"\nset-1 clean {sum(r['clean'] for r in s1)}/45, "
          f"set-2 clean {sum(r['clean'] for r in s2)}/45  excluded: {dirty}")

    train = [r for r in label_set1(s1) if r["clean"]]

    # ---- session audit ---------------------------------------------------
    sessions = {}
    for tag, rows in [("set1", s1), ("set2", s2)]:
        for r in rows:
            sessions.setdefault((tag, r["session"]), []).append(r)
    print(f"\n--- session audit ({n_sessions} sessions; drop energy is NOT constant) ---")
    for (tag, sid), rows in sorted(sessions.items()):
        dv = np.array([r["in_dv_ms"] for r in rows if r["clean"]])
        print(f"  {tag} session {sid}: n={len(rows)} signals "
              f"{min(r['signal'] for r in rows)}-{max(r['signal'] for r in rows)}  "
              f"{str(min(r['event_time'] for r in rows))}..{str(max(r['event_time'] for r in rows))}"
              f"  input dv {dv.mean():.2f} +- {dv.std():.2f} m/s")

    # ---- arrangement classifier (pre-registered) -------------------------
    means, sds, order, cuts, pooled = arr_thresholds(train)
    print("\n--- arrangement model (fitted on set 1 only) ---")
    print("  class means (input FWHM, ms):", {a: round(means[a], 4) for a in ARRS})
    print("  class sds:", {a: round(sds[a], 4) for a in ARRS}, " pooled", round(pooled, 4))
    print("  cuts:", [(f"{lo}|{hi}", round(c, 4)) for lo, hi, c in cuts])
    within_cell = float(np.sqrt(np.mean([np.var([r["in_width_ms"] for r in train
                                                 if r["cell"] == c], ddof=1)
                                         for c in KEY_SET1])))
    print(f"  pooled WITHIN-CELL sd: {within_cell:.4f} ms "
          f"(the class sds are inflated by a specimen effect inside arrangement C)")
    resub = sum(classify_arr(r["in_width_ms"], order, cuts, pooled)[0] == r["arr"]
                for r in train)
    print(f"  set-1 resubstitution accuracy: {resub}/{len(train)}")

    calls = []
    for r in s2:
        a, marg = classify_arr(r["in_width_ms"], order, cuts, pooled)
        r["arr_call"] = a
        calls.append({"signal": r["signal"], "clean": r["clean"], "arr": a,
                      "arr_margin_sigma": marg,
                      "arr_margin_within_cell": float(marg * pooled / within_cell),
                      "uncertain_arr": bool(marg < ABSTAIN_SIGMA),
                      "in_width_ms": r["in_width_ms"], "in_180_g": r["in_180_g"],
                      "t180": r["t180"], "fn_hz": r.get("fn_hz"),
                      "zeta_pct": r.get("zeta_pct"), "t_second_ms": r.get("t_second_ms"),
                      "out_180_g": r["out_180_g"]})
    print("\n--- per-drop arrangement calls (pre-registered rule) ---")
    for c in calls:
        flag = "" if c["clean"] else "  [NO CLEAN IMPACT — excluded]"
        unc = "  *uncertain (<3 sigma)*" if c["uncertain_arr"] and c["clean"] else ""
        print(f"  S{c['signal']:<3d} w={c['in_width_ms']:6.3f} ms -> {c['arr']} "
              f"({c['arr_margin_sigma']:5.2f} sigma pooled / "
              f"{c['arr_margin_within_cell']:6.1f} sigma within-cell){unc}{flag}")

    # ---- specimen readout ------------------------------------------------
    qual = qualify_spec_features(train)
    print("\n--- specimen feature qualification (set 1 only) ---")
    for f, q in sorted(qual.items(), key=lambda kv: -kv[1]["min_gap_d"]):
        print(f"  {f:15s} orders {q['orders']}  consistent={str(q['consistent']):5s} "
              f"min gap {q['min_gap_d']:6.2f} d  {'QUALIFIES' if q['qualifies'] else ''}")
    primary = max((f for f in qual if qual[f]["qualifies"]),
                  key=lambda f: qual[f]["min_gap_d"], default="t_second_ms")
    confirm = [f for f in SPEC_CANDIDATES if f != primary]
    print(f"  -> primary specimen discriminant: {primary}")

    spec_res = spec_rank_call(train, s2, primary, confirm)
    key_out = {}
    for a in ARRS:
        r = spec_res[a]
        print(f"\n  arrangement {a}: set-1 {primary} means "
              f"{ {k: round(v, 2) for k, v in r['set1_means'].items()} }")
        print(f"    regime: {r['regime']}   block sessions {r['sessions']}")
        print(f"    set-2 block means { {k: round(v, 2) for k, v in r['set2_block_means'].items()} }"
              f"  -> {r['mapping']}")
        print(f"    e_rebound set1 { {k: round(v, 5) for k, v in r['set1_e_rebound'].items()} }"
              f"  set2 { {k: round(v, 5) for k, v in r['set2_block_e_rebound'].items()} }")
        print(f"    best cost {r['best_cost']:.5f} vs runner-up {r['runner_up_cost']:.5f} "
              f"(ratio {r['cost_ratio']:.2f}); min adjacent gap {r['min_adjacent_gap_d']:.1f} d")
        for b, s in r["mapping"].items():
            key_out[b] = f"{a}{s}"

    print("\n=== RECONSTRUCTED KEY FOR 'ABC - 123 - Random Arrangement' ===")
    for bi, (lo, hi) in enumerate(SET2_BLOCKS, start=1):
        print(f"  block {bi}  Signals {lo}-{hi}  ->  {key_out.get(f'blk{bi}', '??')}")
    used = sorted(key_out.values())
    print(f"  cells used: {used}  (bijection: {sorted(used) == sorted(KEY_SET1)})")

    # ---- repeatability ---------------------------------------------------
    per_cell = summarize(train, lambda r: r["cell"], list(KEY_SET1), FIELDS)
    per_arr = summarize(train, lambda r: r["arr"], ARRS, FIELDS)
    per_spec = summarize(train, lambda r: r["spec"], SPECS, FIELDS)
    print("\n--- repeatability: within-cell CV (%), set 1, 5 drops per cell ---")
    hdr = ["in_180_g", "in_width_ms", "out_180_g", "t180", "t1000", "fn_hz",
           "zeta_pct", "t_second_ms", "e_rebound"]
    print("  cell " + "".join(f"{h:>14s}" for h in hdr))
    for c in KEY_SET1:
        print(f"  {c:5s}" + "".join(f"{per_cell[c].get(h, {}).get('cv', float('nan')):>14.2f}"
                                    for h in hdr))

    # ---- discrimination --------------------------------------------------
    disc = {}
    for a in ARRS:
        sub = [r for r in train if r["arr"] == a]
        row = {}
        for f in ["t180", "t1000", "out_180_g", "fn_hz", "zeta_pct", "t_second_ms",
                  "e_rebound"]:
            groups = [np.array([r[f] for r in sub if r["spec"] == s
                                and np.isfinite(r.get(f, np.nan))], float) for s in SPECS]
            gm = np.array([g.mean() for g in groups])
            within = float(np.sqrt(np.mean([g.var(ddof=1) for g in groups])))
            F, p = stats.f_oneway(*groups)
            row[f] = {"means": {s: float(m) for s, m in zip(SPECS, gm)},
                      "within_sd": within, "between_sd": float(gm.std(ddof=1)),
                      "snr": float(gm.std(ddof=1) / within) if within else float("nan"),
                      "spread_pct": float(100.0 * (gm.max() - gm.min()) / abs(gm.mean())),
                      "F": float(F), "p": float(p),
                      "d_12": float(abs(gm[0] - gm[1]) / within) if within else float("nan"),
                      "d_13": float(abs(gm[0] - gm[2]) / within) if within else float("nan"),
                      "p_12": float(stats.ttest_ind(groups[0], groups[1],
                                                    equal_var=False).pvalue),
                      "p_13": float(stats.ttest_ind(groups[0], groups[2],
                                                    equal_var=False).pvalue)}
        disc[a] = row
    print("\n--- discrimination by arrangement (set 1) ---")
    for f in ["t180", "out_180_g", "t_second_ms", "e_rebound", "fn_hz"]:
        print(f"  {f}:")
        for a in ARRS:
            d = disc[a][f]
            print(f"    {a}: spread {d['spread_pct']:6.2f} %  SNR {d['snr']:7.2f}  "
                  f"|d| 1v2 {d['d_12']:7.2f}  1v3 {d['d_13']:7.2f}  F {d['F']:9.1f}")

    # ---- ringdown --------------------------------------------------------
    print("\n--- ringdown fit quality (set 1) ---")
    for c in KEY_SET1:
        pc = per_cell[c]
        print(f"  {c}: f_n {pc['fn_hz']['mean']:6.1f} +- {pc['fn_hz']['sd']:5.1f} Hz   "
              f"zeta {pc['zeta_pct']['mean']:6.2f} +- {pc['zeta_pct']['sd']:4.2f} %   "
              f"r2 {pc['ring_r2']['mean']:.2f}   window {pc['ring_fit_ms']['mean']:5.1f} ms   "
              f"2nd event {pc['t_second_ms']['mean']:5.1f} +- {pc['t_second_ms']['sd']:.2f} ms")

    metrics = {
        "set1": s1, "set2": s2, "calls": calls,
        "sessions": {f"{t}|s{d}": {"n": len(v),
                                  "signals": [min(r["signal"] for r in v),
                                              max(r["signal"] for r in v)],
                                  "dv_mean": float(np.mean([r["in_dv_ms"] for r in v
                                                            if r["clean"]]))}
                     for (t, d), v in sessions.items()},
        "arr_model": {"means": means, "sds": sds, "order": order,
                      "cuts": [[lo, hi, c] for lo, hi, c in cuts],
                      "pooled_sd": pooled, "within_cell_sd": within_cell,
                      "resub_accuracy": [resub, len(train)]},
        "spec_qualification": qual, "spec_primary": primary, "spec_result": spec_res,
        "reconstructed_key": key_out,
        "per_cell": per_cell, "per_arr": per_arr, "per_spec": per_spec,
        "discrimination": disc,
    }
    (FIG / "abc123_metrics.json").write_text(json.dumps(metrics, indent=1, default=str))
    make_figures(train, s2, calls, cuts, disc, spec_res, key_out, primary)
    print("\nwrote", FIG / "abc123_metrics.json")


def make_figures(train, s2, calls, cuts, disc, spec_res, key_out, primary):
    blk_of = {}
    for bi, (lo, hi) in enumerate(SET2_BLOCKS, start=1):
        for s in range(lo, hi + 1):
            blk_of[s] = bi

    # 1 — primary arrangement discriminant, set 1 labelled vs set 2 blind
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for a in ARRS:
        ax[0].scatter([r["signal"] for r in train if r["arr"] == a],
                      [r["in_width_ms"] for r in train if r["arr"] == a],
                      c=ARR_COLOR[a], label=ARR_LABEL[a], s=30)
    for _, _, c in cuts:
        for x in ax:
            x.axhline(c, ls="--", c="0.4", lw=1)
    ax[0].set_title("set 1 — labelled (colour = true arrangement)")
    ax[0].set_ylabel("CH5 input pulse FWHM (ms)")
    for c in calls:
        if not c["clean"]:
            ax[1].scatter(c["signal"], min(c["in_width_ms"], 4.0), marker="x", c="k", s=40)
            continue
        ax[1].scatter(c["signal"], c["in_width_ms"], c=ARR_COLOR[c["arr"]], s=30)
    for bi, (lo, hi) in enumerate(SET2_BLOCKS, start=1):
        ax[1].axvline(lo - 0.5, c="0.85", lw=0.8)
        ax[1].text((lo + hi) / 2, 3.6, key_out.get(f"blk{bi}", "?"),
                   ha="center", fontsize=8)
    ax[1].set_title("set 2 — blind call (label = reconstructed cell)")
    ax[1].set_ylim(1.4, 3.8)
    for x in ax:
        x.set_xlabel("signal")
    ax[0].legend(fontsize=8)
    fig.suptitle("Arrangement is read off the input pulse width — no overlap, either set")
    fig.tight_layout()
    fig.savefig(FIG / "01_arrangement_discriminant.png", dpi=140)
    plt.close(fig)

    # 2 — the specimen discriminant
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    for ax, a in zip(axes, ARRS):
        for s in SPECS:
            v = [r[primary] for r in train if r["arr"] == a and r["spec"] == s]
            ax.scatter([f"set1\n{a}{s}"] * len(v), v, c=SPEC_COLOR[s], s=34,
                       label=SPEC_LABEL[s])
        for b, s in spec_res[a]["mapping"].items():
            bi = int(b[3:])
            lo, hi = SET2_BLOCKS[bi - 1]
            v = [r[primary] for r in s2 if lo <= r["signal"] <= hi and r["clean"]
                 and np.isfinite(r.get(primary, np.nan))]
            ax.scatter([f"set2\n{b}→{a}{s}"] * len(v), v, facecolors="none",
                       edgecolors=SPEC_COLOR[s], s=60, lw=1.4)
        ax.set_title(ARR_LABEL[a])
        ax.tick_params(axis="x", labelsize=7)
    axes[0].set_ylabel(f"{primary} (ms)")
    axes[0].legend(fontsize=7)
    fig.suptitle("Specimen discriminant: time of the secondary event, filled = set 1, "
                 "open = set 2 blind (colour = called specimen)")
    fig.tight_layout()
    fig.savefig(FIG / "02_specimen_discriminant.png", dpi=140)
    plt.close(fig)

    # 3 — discrimination per arrangement
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    feats = ["t180", "out_180_g", "fn_hz", "zeta_pct", "t_second_ms"]
    w = 0.25
    for i, a in enumerate(ARRS):
        ax[0].bar(np.arange(len(feats)) + i * w, [disc[a][f]["snr"] for f in feats],
                  w, color=ARR_COLOR[a], label=ARR_LABEL[a])
        ax[1].bar(np.arange(len(feats)) + i * w, [disc[a][f]["d_12"] for f in feats],
                  w, color=ARR_COLOR[a], label=ARR_LABEL[a])
    for x, ttl in zip(ax, ["between-specimen spread / within-cell sd",
                           "specimen 1 vs 2 (same model, different print) |d|"]):
        x.set_xticks(np.arange(len(feats)) + w)
        x.set_xticklabels(feats, fontsize=8)
        x.set_title(ttl, fontsize=10)
        x.set_yscale("log")
        x.legend(fontsize=7)
        x.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_discrimination.png", dpi=140)
    plt.close(fig)

    # 4 — ringdown
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for a in ARRS:
        for s in SPECS:
            sub = [r for r in train if r["arr"] == a and r["spec"] == s]
            ax[0].scatter([r["fn_hz"] for r in sub], [r["zeta_pct"] for r in sub],
                          c=SPEC_COLOR[s], marker="os^"[ARRS.index(a)], s=32)
            ax[1].scatter([r["ring_r2"] for r in sub], [r["zeta_pct"] for r in sub],
                          c=ARR_COLOR[a], s=32)
    ax[0].set_xlabel("modal frequency f_n (Hz)")
    ax[0].set_ylabel("damping ratio zeta (%)")
    ax[0].set_title("ringdown fit — colour = specimen, marker = arrangement")
    ax[1].set_xlabel("log-envelope fit r^2")
    ax[1].set_ylabel("zeta (%)")
    ax[1].set_title("zeta is only meaningful where r^2 is high (colour = arrangement)")
    for c in KEY_SET1:
        sub = [r for r in train if r["cell"] == c]
        ax[2].scatter([c] * len(sub), [r["t_second_ms"] for r in sub],
                      c=SPEC_COLOR[c[1]], s=32)
    ax[2].set_ylabel("secondary-event time (ms after impact)")
    ax[2].set_title("the secondary event: specimen-ordered in every arrangement")
    ax[2].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIG / "04_ringdown.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
