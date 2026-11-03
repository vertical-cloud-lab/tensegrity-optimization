"""Can e come from integrating the top accelerometer instead of from hop timing?

Question (PR #97, me-madsen, 2026-10-29): why is the return velocity in the
coefficient of restitution not found by integrating the top accelerometer,
and would that be more accurate than the ballistic model
e = g * t_second / (2 * dv) used by the campaign?

Data, downloaded on first use into ``--cache``:

* corny1 to corny9 (round 4), drops 3 to 20: the 50 kHz waveform exports
  committed for issue #114 (branch ``claude/issue-114-20261006-1741`` at
  1aff9ff; the TP4 records resampled 25x, no zeroing, no filtering).
* the 959 fps video tracks of one filmed drop each of corny1 to corny7
  (branch ``claude/issue-114-20261006-2044`` at 0cd50a0): the top of the
  specimen measured against the carriage label, frame by frame, on the
  same time base as the records.

Per drop, with the campaign's conventions (``analyze_capture`` in
``scripts/analysis/drop_test_abc123_blind_analysis.py`` on PR #86: tail
baseline, CFC-180 base pulse, 300-900 Hz top envelope, 15-70 ms search
window):

* ballistic estimate: dv, t_second and e = g t_second / (2 dv). These
  reproduce the round-4 campaign means (``data/bo-campaign-snapshot/``).
* integration estimate: the top vertex's velocity relative to the carriage,
  v_rel(t) = integral of g (CH4 - CH5) dt from 2 ms before impact, read at
  5, 10, 15 and 20 ms after impact, and e_int = v_rel / dv. CH4 is the top
  sensor's vertical axis (issue #114 review: r = 0.92 with CH5).
* where the hop detector lands in its search window. A t_second within
  1.5 ms of either end of the window is the window's edge, not a burst.

Outputs (``docs/figures/``):

* ``top_integration_vs_video.png``: integrated relative velocity and height
  for corny1's filmed drop, against the video and against the size of the
  return velocity the ballistic model infers.
* ``hop_detector_window_edges.png``: every drop's t_second against the
  search window, and three example envelopes.
* ``top_integration_check_per_drop.csv`` and
  ``top_integration_check_specimens.csv``.

Usage (from the repo root)::

    pip install numpy scipy pandas matplotlib
    python scripts/analysis/top_channel_integration_check.py
"""

from __future__ import annotations

import argparse
import tempfile
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import integrate, signal as sig
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs" / "figures"
OUT_VIDEO = OUT_DIR / "top_integration_vs_video.png"
OUT_EDGES = OUT_DIR / "hop_detector_window_edges.png"
OUT_DROPS = OUT_DIR / "top_integration_check_per_drop.csv"
OUT_SPECS = OUT_DIR / "top_integration_check_specimens.csv"
CAMPAIGN = REPO / "data" / "bo-campaign-snapshot" / "t3-prism-bo-round4-drop-results.csv"

RAW = "https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization"
WAVE_SHA = "1aff9ff85da196aba08caa33121c2a7d959a5716"
WAVE_PATH = "analysis/issue-114-work/all-specimens/waveforms/{spec}_waveforms_50kHz.csv"
VIDEO_SHA = "0cd50a069e6c5ac1ac0d89503c16401136d78d7d"
VIDEO_PATH = "analysis/issue-114-work/corny1-6-videos/{clip}_video_track.csv"
VIDEO_CLIPS = {"corny1": 10, "corny2": 10, "corny3": 10, "corny4": 10,
               "corny5": 10, "corny6": 11, "corny7": 11}

SPECIMENS = [f"corny{n}" for n in range(1, 10)]
FIRST_DROP = 3            # drops 1 and 2 are the SOP warm-up drops
G = 9.80665               # m/s^2 per G
FS = 50_000.0             # Hz, the exports' sample rate

# campaign conventions (analyze_capture / ringdown_fit on PR #86)
TAIL_S = 0.070            # tail baseline: median from 70 ms to the end
SEARCH_S = 0.015          # impact = CH5 CFC-180 peak in the first 15 ms
DV_PRE_S, DV_POST_S = 0.002, 0.015
BAND_HZ = (300.0, 900.0)
WIN_S = (0.015, 0.070)    # t_second search window after impact
EDGE_MS = 1.5             # within this of a window end = the window's edge
READ_MS = (5, 10, 15, 20)  # when the integrated relative velocity is read

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"


def fetch(url: str, dest: Path) -> Path:
    if not (dest.exists() and dest.stat().st_size > 0):
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=300) as r:
            data = r.read()
        tmp = dest.with_suffix(dest.suffix + ".part")
        tmp.write_bytes(data)
        tmp.rename(dest)
    return dest


def load_waves(cache: Path, spec: str) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    url = f"{RAW}/{WAVE_SHA}/{WAVE_PATH.format(spec=spec)}"
    d = pd.read_csv(fetch(url, cache / f"{spec}_waveforms_50kHz.csv"))
    return {int(k): (g["time_ms"].to_numpy() * 1e-3,
                     g[["ch2_g", "ch3_g", "ch4_g", "ch5_g"]].to_numpy())
            for k, g in d.groupby("drop_number")}


def cfc180(x: np.ndarray) -> np.ndarray:
    # the campaign's filter as written (single-pass 300 Hz design, run twice)
    b, a = sig.butter(2, 300.0 / (FS / 2.0), btype="low")
    return sig.filtfilt(b, a, x)


def analyze(t: np.ndarray, ch: np.ndarray) -> dict:
    dt = t[1] - t[0]
    x = ch - np.median(ch[int(TAIL_S / dt):], axis=0)
    ch5 = cfc180(x[:, 3])
    i_imp = int(np.argmax(np.abs(ch5[:int(SEARCH_S / dt)])))
    j0, j1 = i_imp - int(DV_PRE_S / dt), i_imp + int(DV_POST_S / dt)
    dv = abs(integrate.trapezoid(ch5[j0:j1] * G, t[j0:j1]))

    # hop timing, as ringdown_fit: largest 300-900 Hz envelope burst 15-70 ms
    b, a = sig.butter(4, [BAND_HZ[0] / (FS / 2), BAND_HZ[1] / (FS / 2)], btype="band")
    top = x[:, :3] - x[:, :3].mean(axis=0)
    env = np.sqrt((np.abs(sig.hilbert(sig.filtfilt(b, a, top, axis=0), axis=0)) ** 2).sum(1))
    ks, ke = i_imp + int(WIN_S[0] / dt), min(len(env), i_imp + int(WIN_S[1] / dt))
    t_second = (ks - i_imp + int(np.argmax(env[ks:ke]))) * dt

    # integration: top vertex (CH4) relative to the carriage (CH5)
    v_rel = integrate.cumulative_trapezoid((x[:, 2] - x[:, 3]) * G, t, initial=0.0)
    v_rel -= v_rel[j0]
    h_rel = integrate.cumulative_trapezoid(v_rel, t, initial=0.0)
    h_rel -= h_rel[j0]
    dv_top = integrate.trapezoid(x[j0:j1, 2] * G, t[j0:j1])
    return {"t": t - t[i_imp], "t_imp_ms": 1e3 * t[i_imp], "dv": dv,
            "dv_top": dv_top, "t_second_ms": 1e3 * t_second,
            "e": G * t_second / (2.0 * dv), "env": env, "v_rel": v_rel,
            "h_rel": h_rel, "i_imp": i_imp}


def per_drop(cache: Path) -> tuple[pd.DataFrame, dict]:
    rows, keep = [], {}
    lo, hi = 1e3 * WIN_S[0], 1e3 * WIN_S[1]
    for spec in SPECIMENS:
        for drop, (t, ch) in sorted(load_waves(cache, spec).items()):
            if drop < FIRST_DROP:
                continue
            r = analyze(t, ch)
            keep[(spec, drop)] = r
            row = {"specimen": spec, "drop": drop, "dv_m_s": r["dv"],
                   "dv_top_ch4_m_s": r["dv_top"], "t_second_ms": r["t_second_ms"],
                   "e_ballistic": r["e"],
                   "v_sep_ballistic_m_s": G * r["t_second_ms"] * 1e-3 / 2.0,
                   "window_edge": ("floor" if r["t_second_ms"] - lo < EDGE_MS
                                   else "ceiling" if hi - r["t_second_ms"] < EDGE_MS
                                   else "")}
            for ms in READ_MS:
                v = float(r["v_rel"][r["i_imp"] + int(ms * 1e-3 * FS)])
                row[f"v_rel_{ms}ms_m_s"] = v
                row[f"e_int_{ms}ms"] = v / r["dv"]
            rows.append(row)
    return pd.DataFrame(rows), keep


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    camp = pd.read_csv(CAMPAIGN).set_index("specimen")
    agg = {"n_drops": ("drop", "size"), "dv_m_s": ("dv_m_s", "mean"),
           "t_second_ms": ("t_second_ms", "mean"), "e_ballistic": ("e_ballistic", "mean"),
           "e_ballistic_sd": ("e_ballistic", "std"),
           "n_floor": ("window_edge", lambda s: int((s == "floor").sum())),
           "n_ceiling": ("window_edge", lambda s: int((s == "ceiling").sum()))}
    for ms in READ_MS:
        agg[f"v_rel_{ms}ms_m_s"] = (f"v_rel_{ms}ms_m_s", "mean")
        agg[f"v_rel_{ms}ms_sd"] = (f"v_rel_{ms}ms_m_s", "std")
        agg[f"e_int_{ms}ms"] = (f"e_int_{ms}ms", "mean")
    s = df.groupby("specimen").agg(**agg).reindex(SPECIMENS)
    s["e_campaign"] = camp.loc[SPECIMENS, "e_rebound_mean"].to_numpy()
    s["t180_campaign"] = camp.loc[SPECIMENS, "t180_mean"].to_numpy()
    return s


def video_track(cache: Path, spec: str) -> pd.DataFrame:
    clip = f"{spec}_drop{VIDEO_CLIPS[spec]}"
    url = f"{RAW}/{VIDEO_SHA}/{VIDEO_PATH.format(clip=clip)}"
    return pd.read_csv(fetch(url, cache / f"{clip}_video_track.csv"))


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=10)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def plot_video(cache: Path, keep: dict, spec: str = "corny1") -> dict:
    drop = VIDEO_CLIPS[spec]
    r = keep[(spec, drop)]
    vid = video_track(cache, spec)
    tv = vid["t_ms"].to_numpy() - r["t_imp_ms"]
    hv = vid["video_height_change_mm"].to_numpy()
    t_ms = 1e3 * r["t"]
    z0 = 1.0                                   # zero both heights 1 ms after impact
    h_int = 1e3 * (r["h_rel"] - np.interp(z0, t_ms, r["h_rel"]))
    hv0 = hv - np.interp(z0, tv, hv)
    v_sep = G * r["t_second_ms"] * 1e-3 / 2.0

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.4), sharex=True)
    m = (t_ms >= 0) & (t_ms <= 45)
    a1.axhspan(-v_sep, v_sep, color=AQUA, alpha=0.18, lw=0)
    a1.axhline(0, color=INK2, lw=0.8)
    a1.plot(t_ms[m], r["v_rel"][m], color=ORANGE, lw=2)
    a1.text(44, v_sep + 0.03, f"size of the return velocity the hop timing infers\n"
            f"(±{v_sep:.2f} m/s)", color=INK2, fontsize=9.5, ha="right", va="bottom")
    a1.text(2.0, float(np.max(r["v_rel"][m])) * 0.98, "integrated CH4 − CH5", color=INK,
            fontsize=10, ha="left", va="top")
    a1.set_ylabel("top vertex velocity relative to carriage (m/s)", color=INK, fontsize=10.5)
    a1.set_title("Velocity", loc="left", color=INK, fontsize=11.5)

    mv = (tv >= 2.0) & (tv <= 45)
    a2.axhline(0, color=INK2, lw=0.8)
    a2.plot(t_ms[m], h_int[m], color=ORANGE, lw=2)
    a2.plot(tv[mv], hv0[mv], "o", ms=4, color=INK2, mfc="white", mew=1.2)
    a2.text(44, h_int[m][-1], "integrated CH4 − CH5", color=INK, fontsize=10,
            ha="right", va="bottom")
    a2.text(44, 2.0, "video, 959 fps", color=INK2, fontsize=10, ha="right", va="bottom")
    a2.set_ylabel("top vertex height relative to carriage (mm)", color=INK, fontsize=10.5)
    a2.set_title("Height", loc="left", color=INK, fontsize=11.5)
    for ax in (a1, a2):
        style(ax)
        ax.set_xlabel("time after impact (ms)", color=INK, fontsize=10.5)
        ax.set_xlim(0, 45)
    fig.suptitle(f"{spec}, drop {drop}: integrating CH4 minus CH5 swings by more than twice the "
                 "return velocity we want to measure,\nwhile the video shows the top staying "
                 "within 2 mm of the carriage", x=0.01, ha="left", color=INK, fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT_VIDEO, dpi=160)
    plt.close(fig)
    i5, i15 = (int(np.argmin(np.abs(t_ms - k))) for k in (5, 15))
    j41 = int(np.argmin(np.abs(tv - 41)))
    return {"v_rel_5": float(r["v_rel"][i5]), "v_rel_15": float(r["v_rel"][i15]),
            "h_int_41": float(np.interp(41, t_ms, h_int)), "h_vid_41": float(hv0[j41]),
            "h_vid_range": (float(hv0[mv].min()), float(hv0[mv].max())), "v_sep": v_sep}


def plot_edges(df: pd.DataFrame, keep: dict) -> None:
    lo, hi = 1e3 * WIN_S[0], 1e3 * WIN_S[1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6),
                                 gridspec_kw={"width_ratios": [1.15, 1]})
    rng = np.random.default_rng(0)
    for k, spec in enumerate(SPECIMENS):
        d = df[df.specimen == spec]
        edge = d.window_edge != ""
        xj = k + rng.uniform(-0.18, 0.18, len(d))
        a1.plot(xj[~edge], d.t_second_ms[~edge], "o", ms=5, color=BLUE, alpha=0.85)
        a1.plot(xj[edge], d.t_second_ms[edge], "o", ms=5, color=ORANGE, alpha=0.85)
    for y, lab in ((lo, "search window starts, 15 ms"), (hi, "search window ends, 70 ms")):
        a1.axhline(y, color=INK2, lw=1, ls="--")
        a1.text(8.45, y + (1.2 if y == lo else -1.2), lab, color=INK2, fontsize=9.5,
                ha="right", va="bottom" if y == lo else "top")
    a1.text(-0.3, 50, "inside the window", color=BLUE, fontsize=10, ha="left")
    a1.text(-0.3, 46, "within 1.5 ms of an edge", color=ORANGE, fontsize=10, ha="left")
    a1.set_xticks(range(len(SPECIMENS)), SPECIMENS, rotation=0, fontsize=9.5)
    a1.set_ylim(8, 76)
    a1.set_ylabel("t_second, drops 3 to 20 (ms after impact)", color=INK, fontsize=10.5)
    a1.set_title("Where the detector lands", loc="left", color=INK, fontsize=11.5)
    style(a1)

    t_ms = None
    for spec, col in (("corny1", BLUE), ("corny4", ORANGE), ("corny8", INK2)):
        r = keep[(spec, 10)]
        t_ms = 1e3 * r["t"]
        m = (t_ms >= 2) & (t_ms <= 95)
        db = 20 * np.log10(np.maximum(r["env"][m], 1e-6) / r["env"][m].max())
        a2.plot(t_ms[m], db, color=col, lw=1.6)
        a2.plot(r["t_second_ms"], np.interp(r["t_second_ms"], t_ms[m], db), "o", ms=8,
                color=col, mfc="white", mew=2)
        a2.text(96, db[-1], spec, color=INK, fontsize=10, ha="left", va="center")
    a2.axvspan(lo, hi, color=GRID, alpha=0.45, lw=0)
    a2.text((lo + hi) / 2, 1.5, "search window", color=INK2, fontsize=9.5, ha="center")
    a2.set_xlim(0, 108)
    a2.set_ylim(-62, 5)
    a2.set_xlabel("time after impact (ms), drop 10", color=INK, fontsize=10.5)
    a2.set_ylabel("top vertex 300-900 Hz envelope (dB re peak)", color=INK, fontsize=10.5)
    a2.set_title("Drop 10 envelopes (circle = detected t_second)", loc="left",
                 color=INK, fontsize=11.5)
    style(a2)
    fig.suptitle("Round 4: on five of the nine designs the hop time sits at an edge of the "
                 "15 to 70 ms search window\nin some or all drops (corny4, corny6, corny7, "
                 "corny8, corny9)", x=0.01, ha="left", color=INK, fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT_EDGES, dpi=160)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache", type=Path,
                    default=Path(tempfile.gettempdir()) / "top-integration-check")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df, keep = per_drop(args.cache)
    s = summarize(df)
    df.to_csv(OUT_DROPS, index=False, float_format="%.5g")
    s.to_csv(OUT_SPECS, float_format="%.5g")

    pd.set_option("display.width", 220)
    print("Ballistic estimate vs the campaign means (round 4):")
    print(s[["n_drops", "dv_m_s", "t_second_ms", "e_ballistic", "e_campaign",
             "n_floor", "n_ceiling"]].round(4).to_string())
    print("\nIntegrated relative velocity v_rel = int g (CH4 - CH5) dt, mean over drops (m/s):")
    print(s[[f"v_rel_{ms}ms_m_s" for ms in READ_MS]
            + [f"v_rel_{ms}ms_sd" for ms in READ_MS]].round(3).to_string())
    print("\nSpearman rho across the 9 designs, e_int(read time) vs e_ballistic:")
    for ms in READ_MS:
        rho = spearmanr(s[f"e_int_{ms}ms"], s["e_ballistic"]).statistic
        print(f"  {ms:2d} ms: {rho:+.2f}")
    print("Spearman rho between e_int read at different times:")
    for a, b in ((5, 10), (10, 15), (15, 20), (10, 20)):
        rho = spearmanr(s[f"e_int_{a}ms"], s[f"e_int_{b}ms"]).statistic
        print(f"  {a} vs {b} ms: {rho:+.2f}")
    print("\nPulse velocity change over -2 to +15 ms, CH4 vs CH5 (m/s):")
    g = df.groupby("specimen")[["dv_top_ch4_m_s", "dv_m_s"]].mean().reindex(SPECIMENS)
    g["ch4_minus_ch5_pct"] = 100 * (g.dv_top_ch4_m_s / g.dv_m_s - 1)
    print(g.round(3).to_string())
    print("\nWindow-edge drops (t_second within 1.5 ms of 15 or 70 ms):")
    print(df[df.window_edge != ""].groupby(["specimen", "window_edge"]).size().to_string())

    v = plot_video(args.cache, keep)
    print("\ncorny1 drop 10 (filmed): v_rel at 5 ms {v_rel_5:+.3f}, at 15 ms {v_rel_15:+.3f} m/s;"
          " ballistic v_sep {v_sep:.3f} m/s; height at 41 ms: integrated {h_int_41:+.1f} mm,"
          " video {h_vid_41:+.1f} mm; video range 2-45 ms {h_vid_range}".format(**v))
    plot_edges(df, keep)
    print(f"\nwrote {OUT_VIDEO.name}, {OUT_EDGES.name}, {OUT_DROPS.name}, {OUT_SPECS.name}")


if __name__ == "__main__":
    main()
