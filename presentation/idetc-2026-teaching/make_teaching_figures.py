"""Teaching figures for the IDETC 2026 talk (issue #94).

Builds two audience-facing figures from one real drop in this repo
(session 57vqhX, 2026-07-28, 60 in drop onto 4 felts + 1 cardboard,
Signal 50). Plain-language annotations, no jargon.

Filtering uses the *corrected* SAE J211 CFC implementation from the
issue #94 audit: butter(2, 2.0775*CFC, fs=fs) + filtfilt (per-pass
corner 2.0775*CFC -> two-pass pair corner 1.6667*CFC), NOT the buggy
1.65*CFC single-pass corner used by older analysis scripts.
"""
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CSV = ROOT / "57vqhX_Signal50.csv"

# palette (dataviz reference, validated 2-slot light mode)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
BLUE = "#2a78d6"    # bottom sensor (the jolt going in)
ORANGE = "#eb6834"  # top sensor (what gets through)
GRAY = "#b9b7b0"    # raw trace

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "font.size": 15, "axes.labelsize": 16, "xtick.labelsize": 13,
    "ytick.labelsize": 13, "axes.linewidth": 1.0,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "DejaVu Sans",
})

d = np.genfromtxt(CSV, delimiter=",", skip_header=10, usecols=(0, 1, 2, 3, 4))
t = d[:, 0]
fs = 1 / np.median(np.diff(t))
ch2, ch3, ch4, ch5 = d[:, 1], d[:, 2], d[:, 3], d[:, 4]

# baseline: median of the quiet pre-trigger window (first 0.18 ms)
pre = t < 0.00018
ch2, ch3, ch4, ch5 = (x - np.median(x[pre]) for x in (ch2, ch3, ch4, ch5))


def j211(x, cfc):
    b, a = signal.butter(2, 2.0775 * cfc, fs=fs)
    return signal.filtfilt(b, a, x)


base180 = j211(ch5, 180)
top180 = np.sqrt(j211(ch2, 180) ** 2 + j211(ch3, 180) ** 2 + j211(ch4, 180) ** 2)
base1000 = j211(ch5, 1000)
top1000 = np.sqrt(j211(ch2, 1000) ** 2 + j211(ch3, 1000) ** 2 + j211(ch4, 1000) ** 2)
ring = j211(ch3, 1000)  # one horizontal axis at the top: the "wobble"

# time zero = when the smoothed base jolt first reaches 5 % of its peak
i0 = np.argmax(np.abs(base1000) > 0.05 * np.max(np.abs(base1000)))
tm = (t - t[i0]) * 1e3  # ms after impact

pk_in = float(np.max(np.abs(base180)))
pk_out = float(np.max(np.abs(top180)))
score = pk_out / pk_in

# ---------------------------------------------------------------- figure 1
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(12.4, 5.6), dpi=200, gridspec_kw={"width_ratios": [1, 1.45]}
)
fig.subplots_adjust(left=0.075, right=0.985, top=0.90, bottom=0.21, wspace=0.18)

sel = (tm > -0.3) & (tm < 2.2)
ax1.plot(tm[sel], base1000[sel], color=BLUE, lw=2.0, label="bottom sensor", zorder=3)
ax1.plot(tm[sel], top1000[sel], color=ORANGE, lw=2.0, label="top sensor", zorder=2)
ax1.set_xlabel("thousandths of a second (ms)\nafter the plate lands")
ax1.set_ylabel("acceleration (G, multiples of gravity)")
ax1.set_title("Part 1: the jolt (first 2 ms)", fontsize=16, color=INK, pad=8)
ax1.grid(axis="y", color="#e6e4de", lw=0.8, zorder=0)
ax1.set_ylim(-350, np.max(top1000) * 1.38)
ax1.axhline(0, color=INK2, lw=0.8)
imax2 = np.argmax(top1000)
ax1.annotate("what arrives\nat the top",
             xy=(tm[imax2] + 0.04, top1000[imax2] * 1.0), xycoords="data",
             xytext=(0.52, 0.74), textcoords="axes fraction",
             color=ORANGE, fontsize=13.5, fontweight="bold", ha="left", va="top",
             arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1.2))
imax = np.argmax(np.abs(base1000))
ax1.annotate("the jolt going in\n(bottom of the structure)",
             xy=(tm[imax] - 0.05, base1000[imax] * 0.92), xycoords="data",
             xytext=(0.40, 0.47), textcoords="axes fraction",
             color=BLUE, fontsize=13.5, fontweight="bold", ha="left", va="top",
             arrowprops=dict(arrowstyle="-", color=BLUE, lw=1.2, relpos=(0.0, 0.8)))

sel2 = (tm > 1.5) & (tm < 18.5)
ax2.plot(tm[sel2], ring[sel2], color=ORANGE, lw=1.0)
bins = np.arange(1.5, 18.5, 0.5)
env_t, env = [], []
for b0 in bins:
    m = (tm >= b0) & (tm < b0 + 0.5)
    if m.any():
        env_t.append(b0 + 0.25)
        env.append(np.max(np.abs(ring[m])))
env = np.array(env)
ax2.plot(env_t, env, color=INK2, lw=1.6, ls=(0, (4, 3)))
ax2.plot(env_t, -env, color=INK2, lw=1.6, ls=(0, (4, 3)))
ax2.set_xlabel("thousandths of a second (ms) after the plate lands")
ax2.set_title("Part 2: the ringing (the next 16 ms, top sensor)", fontsize=16, color=INK, pad=8)
ax2.grid(axis="y", color="#e6e4de", lw=0.8, zorder=0)
ax2.set_ylim(-np.max(env) * 1.15, np.max(env) * 1.55)
ax2.axhline(0, color=INK2, lw=0.8)
ax2.annotate("the structure keeps vibrating, like a struck bell\n(about 560 wobbles per second)",
             xy=(5.3, env[7]), xycoords="data",
             xytext=(0.16, 0.965), textcoords="axes fraction",
             color=INK, fontsize=13.5, ha="left", va="top",
             arrowprops=dict(arrowstyle="-", color=INK2, lw=1.2, relpos=(0.15, 0.0)))
ax2.annotate("the fade-out is the structure soaking up the\nshaking energy: a faster fade means\na better shock absorber",
             xy=(13.2, -env[-11] * 1.15), xycoords="data",
             xytext=(0.985, 0.04), textcoords="axes fraction",
             color=INK, fontsize=13.5, ha="right", va="bottom",
             arrowprops=dict(arrowstyle="-", color=INK2, lw=1.2, relpos=(0.85, 1.0)))
ax1.legend(loc="upper right", frameon=False, fontsize=12.5)
fig.text(0.075, 0.015,
         "One real drop from this project (July 28 session, 60-inch drop). Both traces lightly smoothed for display; 1 G = the pull of gravity.",
         color=INK2, fontsize=11.5)
fig.savefig(HERE / "fig1_one_drop_two_parts.png")
plt.close(fig)

# ---------------------------------------------------------------- figure 2
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(12.4, 5.6), dpi=200, gridspec_kw={"width_ratios": [1.7, 1]}
)
fig.subplots_adjust(left=0.09, right=0.985, top=0.90, bottom=0.21, wspace=0.24)

sel = (tm > -0.3) & (tm < 2.2)
ax1.plot(tm[sel], ch5[sel], color=GRAY, lw=0.6, label="raw recording")
ax1.plot(tm[sel], base180[sel], color=BLUE, lw=2.6, label="after standard smoothing")
ax1.set_xlabel("thousandths of a second (ms) after the plate lands")
ax1.set_ylabel("acceleration (G)")
ax1.set_title("Why every lab smooths shock recordings", fontsize=16, color=INK, pad=8)
ax1.grid(axis="y", color="#e6e4de", lw=0.8, zorder=0)
ax1.set_ylim(-2100, 6300)
ax1.axhline(0, color=INK2, lw=0.8)
ax1.annotate("raw trace: dominated by super-fast wiggles of\nthe metal parts and the sensor itself (spikes\npast 5,000 G), not the structure\'s motion",
             xy=(0.42, 4400), xycoords="data",
             xytext=(0.99, 0.72), textcoords="axes fraction",
             color=INK2, fontsize=13, ha="right", va="top",
             arrowprops=dict(arrowstyle="-", color=INK2, lw=1.2, relpos=(0.0, 0.8)))
i180 = np.argmax(np.abs(base180))
ax1.annotate("the push that actually moves the structure,\nrecovered by the same smoothing recipe\ncrash-test labs use (an SAE standard)",
             xy=(tm[i180] + 0.06, base180[i180] * 0.85), xycoords="data",
             xytext=(0.99, 0.045), textcoords="axes fraction",
             color=BLUE, fontsize=13, fontweight="bold", ha="right", va="bottom",
             arrowprops=dict(arrowstyle="-", color=BLUE, lw=1.2, relpos=(0.0, 0.9)))
ax1.legend(loc="upper left", frameon=False, fontsize=12.5)

bars = ax2.bar([0, 1], [pk_in, pk_out], width=0.55, color=[BLUE, ORANGE], zorder=3)
ax2.set_xticks([0, 1])
ax2.set_xticklabels(["biggest jolt\nat the bottom", "biggest jolt\nat the top"], fontsize=13)
ax2.set_ylabel("acceleration (G)")
ax2.set_title("The score for one drop", fontsize=16, color=INK, pad=8)
ax2.grid(axis="y", color="#e6e4de", lw=0.8, zorder=0)
top = max(pk_in, pk_out)
for x, v in zip([0, 1], [pk_in, pk_out]):
    ax2.text(x, v + top * 0.03, f"{v:,.0f} G", ha="center", color=INK, fontsize=15, fontweight="bold")
ax2.set_ylim(0, top * 1.52)
ax2.text(0.5, top * 1.42, f"score = top ÷ bottom = {score:.2f}",
         ha="center", color=INK, fontsize=15, fontweight="bold")
ax2.text(0.5, top * 1.35, "below 1 = the jolt was softened on the way up\nabove 1 = the top shook harder than the base",
         ha="center", va="top", color=INK2, fontsize=12)
fig.text(0.09, 0.015,
         "Same drop as the previous slide. Every recording gets the identical treatment, so dozens of printed designs can be compared fairly.",
         color=INK2, fontsize=11)
fig.savefig(HERE / "fig2_smoothing_and_score.png")
plt.close(fig)

print(f"peak in {pk_in:.0f} G, peak out {pk_out:.0f} G, score {score:.2f}")
print("wrote figures")
