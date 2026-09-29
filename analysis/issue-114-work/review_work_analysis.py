"""Check Justin's work-done analysis of the corny7 drops (issue #114).

Reproduces the submitted numbers, tests the physical plausibility of every
intermediate quantity, and reruns the same physics with the corrections the
review recommends. Writes figures to ``figures/`` and per-drop results to
``results/``.

Model under review (Justin's derivation, justin/derivation_transcribed.md):
the specimen is a massless spring between the base plate (bottom, CH5) and a
point mass m at the top vertex (triaxial accelerometer CH2/CH3/CH4), with

    F_s = m (g + a_top),    W = integral of F_s (v_top - v_bottom) dt.

Everything is reported per unit top mass (J/kg), as in the submitted plots.

Data: corny7_waveforms_50kHz.csv from the issue #110 export (branch
claude/issue-110-20260928-2047, commit 5cc4b1e). It is downloaded on first use
and cached next to this script (git-ignored).

Run from anywhere:  python analysis/issue-114-work/review_work_analysis.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid, solve_ivp

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
RES = HERE / "results"
DATA = HERE / "data" / "corny7_waveforms_50kHz.csv"
DATA_URL = (
    "https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/"
    "5cc4b1e/data/drop-tests/corny7-export/corny7_waveforms_50kHz.csv"
)

G = 9.81  # m/s^2 per G, and gravity, as in the submitted script
SPECIMEN_HEIGHT_MM = 67.12  # corny7 (design t37) as printed
STABLE_DROPS = range(3, 21)  # the lab treats drops 1 and 2 as warm-up
IMPACT_WINDOW_MS = 15.0  # main impact; the next event on every channel is near 75 ms

# Reference palette (dataviz skill): categorical slots 1 to 3, text and grid tokens
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "legend.frameon": False,
        "lines.linewidth": 1.6,
        "font.size": 10,
    }
)


def load_waveforms() -> pd.DataFrame:
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(DATA_URL, DATA)
    return pd.read_csv(DATA)


def drop_arrays(waves: pd.DataFrame, drop: int) -> dict[str, np.ndarray]:
    x = waves[waves["drop_number"] == drop]
    out = {"t": x["time_ms"].to_numpy() * 1e-3}
    for ch in ("ch2", "ch3", "ch4", "ch5"):
        out[ch] = x[f"{ch}_g"].to_numpy()
    return out


# ---------------------------------------------------------------------------
# The submitted computation, ported line for line (implimatation_or_work.py)
# ---------------------------------------------------------------------------
def submitted_work(t, a_top, a_bottom, m=1.0, g=G, v0=0.0):
    """Same arithmetic as Justin's numaric_work(); a_top and a_bottom in m/s^2."""
    v_top = cumulative_trapezoid(a_top, t, initial=0)
    v_bot = cumulative_trapezoid(a_bottom, t, initial=0)
    dt = np.diff(t)
    dx_top = dt * (0.5 * (v_top[1:] + v_top[:-1]) + v0)
    dx_bot = dt * (0.5 * (v_bot[1:] + v_bot[:-1]) + v0)
    force = m * (g + a_top[1:])  # right-endpoint force, as submitted
    work = np.concatenate([[0.0], np.cumsum(force * (dx_top - dx_bot))])
    return work, v_top - v_bot, np.concatenate([[0.0], np.cumsum(dx_top - dx_bot)])


# ---------------------------------------------------------------------------
# The same physics with the review's corrections
# ---------------------------------------------------------------------------
def vertical_top(d: dict, axis: str) -> np.ndarray:
    """Top-vertex vertical acceleration in G.

    "ch4": CH4 alone, the axis that tracks the base plate (r about 0.93).
    "principal": projection of (CH2, CH3, CH4) onto their dominant direction
    during the pulse (1 to 5 ms), which assumes the sensor is tilted and the
    CH3 content is gravity-direction motion rather than sideways motion.
    """
    if axis == "ch4":
        return d["ch4"]
    tri = np.column_stack([d["ch2"], d["ch3"], d["ch4"]])
    pulse = (d["t"] > 1e-3) & (d["t"] < 5e-3)
    direction = np.linalg.svd(tri[pulse], full_matrices=False)[2][0]
    direction *= np.sign(direction[2])
    return tri @ direction


def zeroed(a: np.ndarray, t: np.ndarray, how: str) -> np.ndarray:
    if how == "raw":
        return a
    if how == "tail":  # the lab's convention: median over 70 to 100 ms
        return a - np.median(a[t >= 0.070])
    raise ValueError(how)


def corrected_work(d: dict, axis="ch4", zero="tail", window_ms=IMPACT_WINDOW_MS, g=G):
    """Energy bookkeeping over the main impact, trapezoid rule throughout."""
    t = d["t"]
    a_top = zeroed(vertical_top(d, axis), t, zero) * G
    a_bot = zeroed(d["ch5"], t, zero) * G
    keep = t <= window_ms * 1e-3
    t, a_top, a_bot = t[keep], a_top[keep], a_bot[keep]
    v_rel = cumulative_trapezoid(a_top - a_bot, t, initial=0)
    delta = cumulative_trapezoid(v_rel, t, initial=0)  # top minus base, m
    force = g + a_top  # spring force per unit top mass, N/kg
    work = cumulative_trapezoid(force * v_rel, t, initial=0)  # J/kg
    return {"t": t, "work": work, "delta": delta, "v_rel": v_rel, "force": force}


# ---------------------------------------------------------------------------
# Verification on a problem with a known answer that looks like the real one
# ---------------------------------------------------------------------------
def synthetic_check(d: dict, freq_hz=100.0, zeta=0.15, offset_g=(0.0, 0.5, 1.0, 2.0, 4.0)):
    """Drive a damped point-mass/spring with the measured base-plate pulse.

    The dissipated energy per unit mass is known exactly (integral of
    c/m * v_rel^2). The pipeline is then fed the simulated top acceleration,
    with and without a constant offset of the size seen in the raw channels,
    and integrated over 15 ms and over the full 100 ms record.
    """
    t = d["t"]
    a_bot = zeroed(d["ch5"], t, "tail") * G
    wn = 2 * np.pi * freq_hz
    k_m, c_m = wn**2, 2 * zeta * wn

    def rhs(tt, y):  # y = [delta, v_rel]; delta = top minus base, compression negative
        ab = np.interp(tt, t, a_bot)
        f_s = -k_m * y[0] - c_m * y[1]  # spring force per unit mass, up positive
        a_top = f_s - G
        return [y[1], a_top - ab]

    sol = solve_ivp(rhs, (t[0], t[-1]), [0.0, 0.0], t_eval=t, max_step=5e-6, rtol=1e-9, atol=1e-12)
    delta, v_rel = sol.y
    f_s = -k_m * delta - c_m * v_rel
    a_top = f_s - G
    dissipated = cumulative_trapezoid(c_m * v_rel**2, t, initial=0)
    stored = 0.5 * k_m * delta**2
    rows = []
    for off in offset_g:
        sim = {"t": t, "ch2": 0 * t, "ch3": 0 * t, "ch4": a_top / G + off, "ch5": d["ch5"]}
        for window in (IMPACT_WINDOW_MS, 100.0):
            # "raw" here means no further zeroing: the synthetic top channel is
            # exact apart from the injected offset, and CH5 is tail-zeroed first.
            sim_zeroed_base = dict(sim, ch5=zeroed(d["ch5"], t, "tail"))
            out = corrected_work(sim_zeroed_base, axis="ch4", zero="raw", window_ms=window)
            i = len(out["t"]) - 1
            rows.append(
                {
                    "offset_g": off,
                    "window_ms": window,
                    "true_dissipated_J_per_kg": dissipated[i],
                    "true_minus_work_J_per_kg": dissipated[i] + stored[i],
                    "pipeline_minus_work_J_per_kg": -out["work"][-1],
                    "max_compression_mm": -out["delta"].min() * 1e3,
                    "true_max_compression_mm": -delta[: i + 1].min() * 1e3,
                }
            )
    return pd.DataFrame(rows), {"t": t, "delta": delta, "f_s": f_s, "dissipated": dissipated}


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def fig_submitted(waves: pd.DataFrame):
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.3))
    d = drop_arrays(waves, 2)
    t_ms = d["t"] * 1e3

    ax = axs[0]
    win = t_ms <= 10
    ax.plot(t_ms[win], d["ch5"][win], color=INK2, label="CH5, base plate (input)")
    ax.plot(t_ms[win], d["ch4"][win], color=BLUE, label="CH4, top vertex")
    ax.plot(t_ms[win], d["ch2"][win], color=ORANGE, label="CH2, top vertex (used as a_top)")
    ax.set(xlabel="time (ms)", ylabel="acceleration (G)", title="A. Which top channel follows the drop axis")
    ax.legend(loc="upper right", fontsize=8.5)

    ax = axs[1]
    w_sub, _, dl_sub = submitted_work(d["t"], d["ch2"] * G, d["ch5"] * G)
    ax.plot(t_ms, dl_sub * 1e3, color=ORANGE, label="as submitted (CH2 top, raw, 100 ms)")
    fixed = corrected_work(d, "ch4", "tail", IMPACT_WINDOW_MS)
    ax.plot(fixed["t"] * 1e3, fixed["delta"] * 1e3, color=BLUE, label="CH4, tail-zeroed, 15 ms")
    ax.axhline(-SPECIMEN_HEIGHT_MM, color=INK2, lw=1.0, ls="--")
    ax.annotate("specimen height, 67 mm", (60, -SPECIMEN_HEIGHT_MM), xytext=(0, 5),
                textcoords="offset points", color=INK2, fontsize=8.5, ha="center")
    ax.set(xlabel="time (ms)", ylabel="top minus base displacement (mm)",
           title="B. Implied compression of the specimen")
    ax.legend(loc="lower left", fontsize=8.5)

    ax = axs[2]
    ax.plot(t_ms, w_sub, color=ORANGE, label="as submitted")
    ax.plot(fixed["t"] * 1e3, fixed["work"], color=BLUE, label="CH4, tail-zeroed, 15 ms")
    ax.axvline(75, color=INK2, lw=1.0, ls=":")
    ax.annotate("second impact\non every channel", (75, -2), xytext=(-6, 0), textcoords="offset points",
                color=INK2, fontsize=8.5, ha="right")
    ax.set(xlabel="time (ms)", ylabel="work per unit top mass (J/kg)", title="C. Work curve, corny7 drop 2")
    ax.legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(FIG / "01_submitted_vs_corrected_drop2.png", dpi=150)
    plt.close(fig)


def fig_corrected(waves: pd.DataFrame, drop=5):
    d = drop_arrays(waves, drop)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
    for axis, color, label in (("ch4", BLUE, "CH4 as vertical"), ("principal", AQUA, "tilt-corrected axis")):
        out = corrected_work(d, axis, "tail", IMPACT_WINDOW_MS)
        axs[0].plot(out["t"] * 1e3, out["work"], color=color, label=label)
        axs[1].plot(-out["delta"] * 1e3, out["force"] / G, color=color, label=label)
    axs[0].set(xlabel="time (ms)", ylabel="work per unit top mass (J/kg)",
               title=f"A. Work over the main impact, drop {drop}")
    axs[0].legend(loc="upper right", fontsize=8.5)
    axs[1].set(xlabel="compression, base to top (mm)", ylabel="spring force per unit top mass (G)",
               title="B. Force against compression (loop area = energy)")
    axs[1].legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(FIG / "02_corrected_work_and_loop_drop5.png", dpi=150)
    plt.close(fig)


def fig_sensitivity(per_drop: pd.DataFrame):
    order = [
        ("submitted", "As submitted\n(CH2, raw, 100 ms)"),
        ("ch4_raw_15", "CH4\nraw, 15 ms"),
        ("ch4_tail_15", "CH4\ntail-zeroed, 15 ms"),
        ("ch4_tail_30", "CH4\ntail-zeroed, 30 ms"),
        ("principal_raw_15", "Tilt-corrected\nraw, 15 ms"),
        ("principal_tail_15", "Tilt-corrected\ntail-zeroed, 15 ms"),
    ]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    rng = np.random.default_rng(0)
    for i, (key, _) in enumerate(order):
        y = per_drop.loc[per_drop["drop"].isin(STABLE_DROPS), key].to_numpy()
        color = ORANGE if key == "submitted" else BLUE
        ax.scatter(i + rng.uniform(-0.12, 0.12, y.size), y, s=22, color=color, edgecolor=SURFACE, linewidth=0.6)
        ax.annotate(f"{y.mean():.2f}", (i, y.max()), xytext=(0, 7), textcoords="offset points",
                    ha="center", color=INK, fontsize=9)
    ax.set_xticks(range(len(order)), [lab for _, lab in order], fontsize=8.5)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set(ylabel="work per unit top mass (J/kg)",
           title="Drops 3 to 20: the analysis choices move the answer far more than the drops do")
    fig.tight_layout()
    fig.savefig(FIG / "03_sensitivity_drops3to20.png", dpi=150)
    plt.close(fig)


def fig_synthetic(syn: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4.3))
    for window, color in ((IMPACT_WINDOW_MS, BLUE), (100.0, ORANGE)):
        s = syn[syn["window_ms"] == window]
        ax.plot(s["offset_g"], s["pipeline_minus_work_J_per_kg"], "o-", color=color, ms=6,
                label=f"pipeline, {window:.0f} ms window")
        ax.plot(s["offset_g"], s["true_minus_work_J_per_kg"], color=color, lw=1.0, ls="--",
                label=f"true answer, {window:.0f} ms window")
    ax.set(xlabel="constant offset added to the top channel (G)", ylabel="energy absorbed per unit top mass (J/kg)",
           title="Known-answer test: measured base pulse driving a damped spring")
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(FIG / "04_synthetic_offset_check.png", dpi=150)
    plt.close(fig)


def main() -> None:
    FIG.mkdir(exist_ok=True)
    RES.mkdir(exist_ok=True)
    waves = load_waveforms()

    rows = []
    for drop in range(1, 21):
        d = drop_arrays(waves, drop)
        w_sub, v_sub, dl_sub = submitted_work(d["t"], d["ch2"] * G, d["ch5"] * G)
        row = {
            "drop": drop,
            "submitted": w_sub[-1],
            "submitted_min_rel_disp_mm": dl_sub.min() * 1e3,
            "submitted_end_rel_vel_m_s": v_sub[-1],
            "corr_ch2_ch5": np.corrcoef(d["ch2"], d["ch5"])[0, 1],
            "corr_ch3_ch5": np.corrcoef(d["ch3"], d["ch5"])[0, 1],
            "corr_ch4_ch5": np.corrcoef(d["ch4"], d["ch5"])[0, 1],
        }
        for axis in ("ch4", "principal"):
            for zero in ("raw", "tail"):
                for window in (8.0, 15.0, 30.0):
                    out = corrected_work(d, axis, zero, window)
                    key = f"{axis}_{zero}_{window:.0f}"
                    row[key] = out["work"][-1]
                    row[f"{key}_max_compression_mm"] = -out["delta"].min() * 1e3
                    row[f"{key}_end_rel_vel_m_s"] = out["v_rel"][-1]
        # CH4 put on CH5's scale with the side-by-side ratio from PR #74 (CH5 = 0.953 x CH4)
        rescaled = dict(d, ch4=0.953 * d["ch4"])
        out = corrected_work(rescaled, "ch4", "raw", IMPACT_WINDOW_MS)
        row["ch4_pr74scale_raw_15"] = out["work"][-1]
        row["ch4_pr74scale_raw_15_end_rel_vel_m_s"] = out["v_rel"][-1]
        # gravity term switched off, to size its contribution
        out = corrected_work(d, "ch4", "tail", IMPACT_WINDOW_MS, g=0.0)
        row["ch4_tail_15_no_g"] = out["work"][-1]
        # right-endpoint force (as submitted) versus trapezoid, same corrected inputs
        out = corrected_work(d, "ch4", "tail", IMPACT_WINDOW_MS)
        a_top = zeroed(d["ch4"], d["t"], "tail")[: len(out["t"])] * G
        a_bot = zeroed(d["ch5"], d["t"], "tail")[: len(out["t"])] * G
        row["ch4_tail_15_right_endpoint"] = submitted_work(out["t"], a_top, a_bot)[0][-1]
        rows.append(row)
    per_drop = pd.DataFrame(rows)
    per_drop.round(5).to_csv(RES / "per_drop_work.csv", index=False)

    syn, _ = synthetic_check(drop_arrays(waves, 5))
    syn.round(5).to_csv(RES / "synthetic_offset_check.csv", index=False)

    fig_submitted(waves)
    fig_corrected(waves)
    fig_sensitivity(per_drop)
    fig_synthetic(syn)

    stable = per_drop[per_drop["drop"].isin(STABLE_DROPS)]
    cols = [c for c in per_drop.columns if c == "submitted" or c.count("_") == 2]
    summary = {
        "submitted_drop1_drop2": per_drop.loc[per_drop["drop"] <= 2, "submitted"].round(3).tolist(),
        "submitted_min_rel_disp_mm_drop1_drop2": per_drop.loc[per_drop["drop"] <= 2, "submitted_min_rel_disp_mm"].round(1).tolist(),
        "corr_with_ch5_mean": stable[["corr_ch2_ch5", "corr_ch3_ch5", "corr_ch4_ch5"]].mean().round(3).to_dict(),
        "drops3to20_mean": stable[cols].mean().round(3).to_dict(),
        "drops3to20_sd": stable[cols].std().round(3).to_dict(),
        "ch4_tail_15_max_compression_mm_mean": round(stable["ch4_tail_15_max_compression_mm"].mean(), 2),
        "ch4_tail_15_end_rel_vel_m_s_mean": round(stable["ch4_tail_15_end_rel_vel_m_s"].mean(), 3),
        "ch4_tail_15_right_endpoint_mean": round(stable["ch4_tail_15_right_endpoint"].mean(), 3),
        "ch4_tail_15_no_g_mean": round(stable["ch4_tail_15_no_g"].mean(), 3),
        "ch4_pr74scale_raw_15_mean": round(stable["ch4_pr74scale_raw_15"].mean(), 3),
        "ch4_pr74scale_raw_15_end_rel_vel_m_s_mean": round(stable["ch4_pr74scale_raw_15_end_rel_vel_m_s"].mean(), 3),
        "ch4_raw_15_max_compression_mm_mean": round(stable["ch4_raw_15_max_compression_mm"].mean(), 2),
        "ch4_raw_15_end_rel_vel_m_s_mean": round(stable["ch4_raw_15_end_rel_vel_m_s"].mean(), 3),
        "synthetic": syn.round(3).to_dict(orient="records"),
    }
    (RES / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
