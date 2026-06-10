#!/usr/bin/env python3
"""Standalone *example* of a mechanism-oriented results figure for the manuscript.

This is a side-task mock-up requested in PR review (comment 4664748222), then
revised per Edison ANALYSIS feedback (task ``e0c4e062-15c7-4a62-b931-1746211fe8b1``,
folded back via PR comment 4664958219): a worked example of the kind of data
figure the manuscript currently lacks -- processed drop-test acceleration curves
annotated so the reader can connect the measured signal to the *mechanism* of
energy absorption.

IMPORTANT: the curves here are SYNTHETIC. They are generated from the documented
qualitative behaviour of the real drop-test campaign (issue #36 analysis: 125 kHz
TP4 capture (the lab's PicoScope-class digital scope export; 4 channels, 0.2 s
window), SAE J211 CFC-180 filtering, impact at t ~ 4.2 ms, control CFC-180
peak ~1792 G, 'audrey' tensegrity CFC-180 peak ~370-463 G => ~74-79 % reduction)
purely to illustrate layout and annotation. No experimental file is read or
implied; replace the ``synthetic_*`` calls with the real processed channels before
any figure like this is used in the manuscript.

Edison feedback addressed in this revision:
  * The two traces are now *impulse-consistent*: the control and tensegrity
    accelerations integrate to the same mass-normalized velocity change (Delta v),
    so the lower peak comes from spreading the same impulse over time rather than
    from inventing/destroying impulse. A cumulative-impulse subpanel (sharing the
    main panel's x-axis) makes this conservation check visible.
  * The tensegrity "plateau" is now a delayed rise + flat shoulder (not a centered
    Gaussian), peaking after -- not before -- the control, with a realistic (not
    over-extreme) duration contrast.
  * Three synchronized event markers (contact / plateau / rebound) sit on the
    tensegrity curve and key the matching frame placeholders, each with a timestamp.
  * Phases use event-based labels (first contact, strut rotation + cable
    redistribution, peak compression plateau, rebound) instead of generic A/B/C.
  * A representative-vs-replicate uncertainty band (+/- 1 s.d. over n synthetic
    replicates) is drawn, and the filtering details live in the caption.
  * Colorblind-safer control/tensegrity pair (dark gray vs. blue-green), lighter
    phase shading, and the legend/phase key kept off the data field.

Run:
    python scripts/figures/mechanistic_data_figure_example.py
Outputs:
    figures/examples/mechanistic-data-figure-example.png
    figures/examples/mechanistic-data-figure-example.pdf
"""
from __future__ import annotations

import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "figures", "examples")
OUT_BASE = os.path.join(OUT_DIR, "mechanistic-data-figure-example")

# ---------------------------------------------------------------------------
# Synthetic, physically-plausible drop-test signals (NOT real data).
#
# Both traces are built so that the integral of the (mass-normalized)
# deceleration over the impact is identical -- i.e. they transfer the same
# velocity change Delta v -- which is the conservation-level consistency an
# impact-mechanics reviewer checks first.
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(36)
G_TO_MS2 = 9.80665  # 1 G in m/s^2


def _trapz(y, x):
    """np.trapezoid (NumPy >= 2) with np.trapz fallback for older NumPy."""
    fn = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    return fn(y, x)
T_CONTACT_MS = 4.2  # documented first-contact time in the real TP4 captures
CTRL_PEAK_G = 1792.0  # documented control CFC-180 peak; anchors the shared impulse
N_REPLICATES = 5  # synthetic replicate count used for the uncertainty band

# Event markers (ms) keyed to the synchronized frame placeholders.
T_MARK_CONTACT = 4.7
T_MARK_PLATEAU = 6.4
T_MARK_REBOUND = 8.4


def _control_shape(t_ms: np.ndarray) -> np.ndarray:
    """Rigid control: a single sharp, short half-sine deceleration pulse (unit peak)."""
    tau = t_ms - T_CONTACT_MS
    width = 0.9  # ms; narrow, hard contact
    shape = np.where((tau >= 0) & (tau <= width), np.sin(np.pi * tau / width), 0.0)
    return shape


def _control_ring(t_ms: np.ndarray) -> np.ndarray:
    """Decaying structural/mount ringing (~550 Hz); integrates to ~0 (zero net impulse)."""
    tau = t_ms - T_CONTACT_MS
    ring = np.exp(-np.clip(tau, 0, None) / 2.5) * np.sin(2 * np.pi * 0.55 * tau)
    ring[tau < 0] = 0.0
    return ring


def _smootherstep(x: np.ndarray) -> np.ndarray:
    """C2-continuous 0->1 ramp on [0,1] (Perlin smootherstep)."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)


def _tensegrity_shape(t_ms: np.ndarray) -> np.ndarray:
    """Tensegrity: delayed rise + flat shoulder + gentle fall (unit-ish peak).

    A trapezoid with smootherstep edges -- a true shoulder, not a centered
    Gaussian -- whose peak occurs *after* the control's, modelling load
    redistribution by the strut/cable network.
    """
    # delayed rise relative to first contact -> flat shoulder -> unloading
    t0, t1 = T_CONTACT_MS + 0.5, T_CONTACT_MS + 1.6  # delayed rise (~1.1 ms)
    t2, t3 = T_CONTACT_MS + 2.8, T_CONTACT_MS + 4.4  # shoulder end / fall end
    rise = _smootherstep((t_ms - t0) / (t1 - t0))
    fall = 1.0 - _smootherstep((t_ms - t2) / (t3 - t2))
    shape = np.minimum(rise, fall)
    shape[t_ms < t0] = 0.0
    shape[t_ms > t3] = 0.0
    return shape


def synthetic_traces(t_ms: np.ndarray):
    """Return impulse-matched control & tensegrity CFC-180 decelerations (in G).

    The tensegrity shoulder is scaled so its impulse equals the control pulse's,
    so both transfer the same Delta v; the resulting tensegrity peak (and hence the
    reduction) is an *output* of that constraint, not an arbitrary input.
    """
    t_s = t_ms / 1000.0
    ctrl = CTRL_PEAK_G * _control_shape(t_ms)
    # impulse (mass-normalized Delta v) of the control main pulse
    j_ctrl = _trapz(ctrl * G_TO_MS2, t_s)
    tens_unit = _tensegrity_shape(t_ms)
    j_tens_unit = _trapz(tens_unit * G_TO_MS2, t_s)
    scale = j_ctrl / j_tens_unit  # match impulse exactly
    tens = scale * tens_unit
    return ctrl, tens, j_ctrl


def cumulative_dv(accel_g: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
    """Cumulative mass-normalized velocity change, J(t)=int a dt, in m/s."""
    from scipy.integrate import cumulative_trapezoid  # optional dependency

    return cumulative_trapezoid(accel_g * G_TO_MS2, t_ms / 1000.0, initial=0.0)


def _cumtrapz_fallback(accel_g: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
    a = accel_g * G_TO_MS2
    t_s = t_ms / 1000.0
    out = np.zeros_like(a)
    out[1:] = np.cumsum(0.5 * (a[1:] + a[:-1]) * np.diff(t_s))
    return out


def cumulative_impulse(accel_g: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
    try:
        return cumulative_dv(accel_g, t_ms)
    except Exception:
        return _cumtrapz_fallback(accel_g, t_ms)


def _replicate_band(base_g: np.ndarray, t_ms: np.ndarray, peak_jitter: float,
                    noise_g: float):
    """Synthesize n replicates (small peak/timing jitter + noise) -> mean, std."""
    reps = []
    peak0 = base_g.max()
    for _ in range(N_REPLICATES):
        gain = 1.0 + RNG.normal(0, peak_jitter)
        shift = RNG.normal(0, 0.05)  # ms timing jitter
        shifted = np.interp(t_ms, t_ms + shift, base_g, left=0.0, right=0.0)
        reps.append(gain * shifted + RNG.normal(0, noise_g, size=t_ms.shape))
    reps = np.array(reps)
    return reps.mean(axis=0), reps.std(axis=0), peak0


# ---------------------------------------------------------------------------
# Small schematic of a T3 tensegrity prism used for the synchronized frames.
# ---------------------------------------------------------------------------
def draw_t3_prism(ax, compression: float = 0.0, highlight_joint: bool = False):
    """Cartoon T3 prism. `compression` in [0,1] squashes height; struts=PLA, cables=TPU."""
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.axis("off")

    h = 1.0 * (1.0 - 0.45 * compression)
    twist = np.deg2rad(50)  # near equilibrium prism twist
    ang = np.array([90, 210, 330]) * np.pi / 180.0
    bottom = np.c_[np.cos(ang), np.sin(ang) - 0.0] * 0.85
    top = np.c_[np.cos(ang + twist), np.sin(ang + twist)] * 0.85
    bottom = np.c_[bottom[:, 0], bottom[:, 1] * 0.45 - h]
    top = np.c_[top[:, 0], top[:, 1] * 0.45 + h]

    # cables (TPU) -- horizontal triangles + saddle cables
    cab = dict(color="#1f77b4", lw=1.8, solid_capstyle="round", zorder=1)
    for i in range(3):
        j = (i + 1) % 3
        ax.plot(*zip(bottom[i], bottom[j]), **cab)
        ax.plot(*zip(top[i], top[j]), **cab)
    for i in range(3):
        ax.plot(*zip(bottom[i], top[(i + 1) % 3]), **cab)

    # struts (PLA) -- the three crossing compression members
    strut = dict(color="#d62728", lw=3.4, solid_capstyle="round", zorder=2)
    pairs = [(0, 0), (1, 1), (2, 2)]
    for b, t in pairs:
        ax.plot(*zip(bottom[b], top[t]), **strut)

    if highlight_joint:
        # circle one strut end to mark the internal-anchor joint callout
        ax.add_patch(plt.Circle(top[0], 0.22, fill=False, color="#ff7f0e", lw=2.5, zorder=5))


def draw_internal_anchor_inset(ax):
    """Schematic of the corrected joint: cables anchor INSIDE the strut end (cage)."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # PLA strut end shell (cage)
    ax.add_patch(FancyBboxPatch((0.30, 0.08), 0.40, 0.72,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="#f4c7c3", ec="#d62728", lw=2.0))
    ax.text(0.5, 0.90, "PLA strut end\n(rigid cage)", ha="center", va="bottom",
            fontsize=7.0, color="#a01717")
    # internal junction node where TPU cables meet
    ax.add_patch(plt.Circle((0.5, 0.42), 0.07, fc="#1f77b4", ec="k", lw=0.8, zorder=4))
    # cables exiting through discrete outlets
    for dx in (-0.18, 0.0, 0.18):
        ax.plot([0.5, 0.5 + dx], [0.42, 0.10], color="#1f77b4", lw=2.0,
                solid_capstyle="round", zorder=3)
    ax.text(0.5, 0.02, "TPU cables join inside,\nexit via outlets",
            ha="center", va="top", fontsize=7.0, color="#11557c")


def _frame_inset(ax, compression, marker_no, t_ms, title, highlight_joint=False):
    draw_t3_prism(ax, compression=compression, highlight_joint=highlight_joint)
    # registration badge: matches the numbered marker on the curve
    ax.text(-1.32, 1.25, str(marker_no), ha="center", va="center", fontsize=10,
            fontweight="bold", color="white",
            bbox=dict(boxstyle="circle,pad=0.25", fc="#222222", ec="none"))
    ax.text(1.32, 1.25, f"{t_ms:.1f} ms", ha="right", va="center", fontsize=7.5,
            color="#333333")
    ax.set_title(title, fontsize=8.0, loc="left")


# ---------------------------------------------------------------------------
# Build the figure.
# ---------------------------------------------------------------------------
# Colorblind-safer pair (Okabe-Ito): control = dark gray, tensegrity = blue-green.
C_CTRL = "#555555"
C_TENS = "#009E73"
C_TENS_RAW = "#7fd9bf"
_ROMAN = ["i", "ii", "iii", "iv"]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t = np.linspace(0, 22, 6000)  # ms

    ctrl, tens, dv = synthetic_traces(t)

    # raw tensegrity (faint) to motivate CFC-180 filtering: HF ringing on top
    hf = 60.0 * np.sin(2 * np.pi * 4.5 * t) * np.exp(-np.clip(t - T_CONTACT_MS, 0, None) / 6.0)
    tens_raw = tens + hf + RNG.normal(0, 10, size=t.shape)

    ctrl_mean, ctrl_std, ctrl_peak = _replicate_band(ctrl, t, 0.05, 6.0)
    tens_mean, tens_std, tens_peak = _replicate_band(tens, t, 0.06, 4.0)
    reduction = 100 * (1 - tens_peak / ctrl_peak)

    # cumulative mass-normalized velocity change (impulse consistency)
    j_ctrl = cumulative_impulse(ctrl, t)
    j_tens = cumulative_impulse(tens, t)

    fig = plt.figure(figsize=(12.6, 8.0), dpi=150)
    gs = fig.add_gridspec(
        4, 2,
        width_ratios=[2.85, 1.0],
        height_ratios=[1.0, 1.0, 1.0, 1.15],
        hspace=0.45, wspace=0.20,
        left=0.07, right=0.985, top=0.905, bottom=0.135,
    )
    ax = fig.add_subplot(gs[0:3, 0])          # main time-history
    ax_imp = fig.add_subplot(gs[3, 0], sharex=ax)  # cumulative-impulse subpanel

    # --- main time-history panel (a) --------------------------------------
    ax.plot(t, tens_raw, color=C_TENS_RAW, lw=0.7, alpha=0.7, zorder=1,
            label="Tensegrity, raw (125 kHz)")
    ax.plot(t, ctrl_mean, color=C_CTRL, lw=2.0, zorder=4, label="Rigid control, CFC-180")
    ax.fill_between(t, ctrl_mean - ctrl_std, ctrl_mean + ctrl_std,
                    color=C_CTRL, alpha=0.18, lw=0, zorder=2)
    ax.plot(t, tens_mean, color=C_TENS, lw=2.4, zorder=5, label="Tensegrity, CFC-180")
    ax.fill_between(t, tens_mean - tens_std, tens_mean + tens_std,
                    color=C_TENS, alpha=0.22, lw=0, zorder=3)

    ax.axhline(ctrl_peak, color=C_CTRL, ls=":", lw=1.0, alpha=0.6)
    ax.axhline(tens_peak, color=C_TENS, ls=":", lw=1.0, alpha=0.6)

    # peak-reduction annotation
    ax.annotate("", xy=(T_CONTACT_MS + 0.45, tens_peak),
                xytext=(T_CONTACT_MS + 0.45, ctrl_peak),
                arrowprops=dict(arrowstyle="<->", color="k", lw=1.4))
    ax.text(T_CONTACT_MS + 0.8, (ctrl_peak + tens_peak) / 2,
            f"peak transmitted\ndeceleration\n-{reduction:.0f}%",
            fontsize=9, va="center", fontweight="bold")

    # event-based phase shading (lightened) keyed to observable kinematics
    phases = [
        (T_CONTACT_MS, T_CONTACT_MS + 0.8, "#fff2cc", "first\ncontact"),
        (T_CONTACT_MS + 0.8, T_CONTACT_MS + 1.8, "#d9ead3", "strut rotation +\ncable redistribution"),
        (T_CONTACT_MS + 1.8, T_CONTACT_MS + 3.0, "#cfe2f3", "peak compression\nplateau"),
        (T_CONTACT_MS + 3.0, T_CONTACT_MS + 5.6, "#f0e0ef", "rebound /\nunloading"),
    ]
    for k, (x0, x1, col, lab) in enumerate(phases, start=1):
        ax.axvspan(x0, x1, color=col, alpha=0.30, zorder=0)
        # roman-numeral tick keyed to the phase key (kept off the data field)
        ax.text((x0 + x1) / 2, ctrl_peak * 1.02, _ROMAN[k - 1], ha="center",
                va="bottom", fontsize=8.5, color="#555555", fontweight="bold")
    # event-based phase key, placed in the empty upper region (off the curves)
    key = "\n".join(f"{_ROMAN[k]}  {lab.replace(chr(10), ' ')}"
                     for k, (_, _, _, lab) in enumerate(phases))
    ax.text(9.1, ctrl_peak * 0.86, key, fontsize=7.8, va="top", ha="left",
            linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#cccccc", alpha=0.95))

    # synchronized event markers on the tensegrity curve (key the frames)
    marks = [(1, T_MARK_CONTACT), (2, T_MARK_PLATEAU), (3, T_MARK_REBOUND)]
    for no, tm in marks:
        ym = np.interp(tm, t, tens_mean)
        ax.plot(tm, ym, "o", ms=11, mfc="#222222", mec="white", mew=1.2, zorder=6)
        ax.text(tm, ym, str(no), ha="center", va="center", fontsize=8,
                color="white", fontweight="bold", zorder=7)

    ax.set_ylabel("Transmitted base deceleration (G)")
    ax.set_xlim(0, 14)
    ax.set_ylim(-60, ctrl_peak * 1.16)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.95)
    ax.set_title("(a)  Processed drop-test response  (markers 1-3 key the frames at right)",
                 fontsize=10.5, loc="left")
    plt.setp(ax.get_xticklabels(), visible=False)

    # --- cumulative-impulse subpanel (a2): conservation check -------------
    ax_imp.plot(t, j_ctrl, color=C_CTRL, lw=2.0, label="Rigid control")
    ax_imp.plot(t, j_tens, color=C_TENS, lw=2.4, label="Tensegrity")
    dv_final = max(j_ctrl[-1], j_tens[-1])
    ax_imp.axhline(dv_final, color="#999999", ls="--", lw=1.0, alpha=0.8)
    ax_imp.text(0.3, dv_final, f"matched $\\Delta v\\approx{dv_final:.1f}$ m/s",
                fontsize=8, va="bottom", color="#444444")
    for no, tm in marks:
        ax_imp.axvline(tm, color="#bbbbbb", lw=0.8, ls=":", zorder=0)
    ax_imp.set_xlabel("Time (ms)")
    ax_imp.set_ylabel("Cumulative\n$\\Delta v$ (m/s)", fontsize=9)
    ax_imp.set_xlim(0, 14)
    ax_imp.set_ylim(0, dv_final * 1.18)
    ax_imp.legend(loc="lower right", fontsize=7.5, ncol=2, framealpha=0.9)
    ax_imp.set_title("(a2)  Cumulative impulse (same $\\Delta v$ \u21d2 peak cut by temporal "
                     "redistribution, not inconsistent loading)",
                     fontsize=8.5, loc="left")

    # --- synchronized frame placeholders on the right ---------------------
    ax_f1 = fig.add_subplot(gs[0, 1])
    _frame_inset(ax_f1, compression=0.05, marker_no=1, t_ms=T_MARK_CONTACT,
                 title="(b) 1: first contact",
                 highlight_joint=True)
    ax_f2 = fig.add_subplot(gs[1, 1])
    _frame_inset(ax_f2, compression=0.8, marker_no=2, t_ms=T_MARK_PLATEAU,
                 title="(c) 2: peak compression")
    ax_f3 = fig.add_subplot(gs[2, 1])
    _frame_inset(ax_f3, compression=0.35, marker_no=3, t_ms=T_MARK_REBOUND,
                 title="(d) 3: rebound / unloading")

    ax_j = fig.add_subplot(gs[3, 1])
    draw_internal_anchor_inset(ax_j)
    ax_j.set_title("(e)  joint callout (circled in frame 1)", fontsize=8.0, loc="left")

    fig.suptitle(
        "EXAMPLE (mock-up, synthetic data): mechanism-oriented drop-test figure",
        fontsize=12.5, fontweight="bold",
    )

    # caption with measurement / filtering / replicate disclosure (Edison ask 4 & 6)
    caption = (
        "Synthetic illustration. In a real figure: transmitted base deceleration "
        "of a rigid control vs. T3-prism tensegrity, both SAE J211 CFC-180 filtered "
        "(125 kHz raw shown faint), zero-phase (filtfilt), time-aligned on the "
        "CH4 first-contact index. Curves are the mean of n=" f"{N_REPLICATES}"
        " replicates; bands are \u00b11 s.d. Frames 1-3 are high-speed/DIC stills at "
        "markers 1-3; (e) shows the internal cable-anchor joint that spreads the impulse."
    )
    fig.text(0.5, 0.012, caption, ha="center", va="bottom", fontsize=7.3,
             color="#333333", wrap=True)

    # visible mock-up watermark (lightened so data/markers read first)
    fig.text(0.40, 0.55, "ILLUSTRATIVE EXAMPLE\nSYNTHETIC DATA",
             fontsize=30, color="gray", alpha=0.10, ha="center", va="center",
             rotation=18, zorder=10)

    fig.savefig(OUT_BASE + ".png", dpi=150)
    fig.savefig(OUT_BASE + ".pdf")
    print("wrote", OUT_BASE + ".png", "and", OUT_BASE + ".pdf")
    print(f"control peak={ctrl_peak:.0f} G, tensegrity peak={tens_peak:.0f} G, "
          f"reduction={reduction:.0f}%, matched dv={dv:.2f} m/s, "
          f"final dv ctrl/tens={j_ctrl[-1]:.2f}/{j_tens[-1]:.2f} m/s")


if __name__ == "__main__":
    main()
