"""Regenerate the three data-slide figures in idetc-2026.pptx.

Feedback items 22-24b from presentation/feedback-video-2026-08-18.md: the two
data slides were too dense, and the attenuation slide plotted raw traces. These
figures are the replacements: fewer annotation layers, axis labels that say
"time (ms)" instead of "thousandths of a second (ms)", and filtered data on the
attenuation comparison.

Data: the 60 in validation campaigns committed at the root of the main branch
(Marcus_1.zip = specimen 7xadt6, jin_1.zip = specimen 9GMQYQ; TP4 exports,
200 ms at 125 kHz). Channel map per docs/drop-test-60in-5felts-analysis.md on
the PR #86 branch: CH2/CH3/CH4 = top-vertex tri-axis (X/Y/Z), CH5 = single-axis
input sensor on the base plate (also the trigger). Both campaigns ran
back-to-back on the same 4 felt + 1 cardboard stack on 2026-07-20.

Usage: python regen_data_slide_figures.py --data-dir <dir with the zips>
e.g. populated via:  git show "origin/main:Marcus_1.zip" > <dir>/Marcus_1.zip
"""

import argparse
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Colors: EMC-adjacent blue/orange, adjusted to pass the palette validator
# (chroma floor and 3:1 surface contrast) while staying near the deck theme.
BLUE = "#1878B8"    # bottom (input) sensor, CH5
ORANGE = "#D96A24"  # top-vertex sensor, CH4 vertical / CH2 lateral
GRAY = "#9a9a9a"    # raw recording
INK = "#333333"
MUTED = "#707070"

plt.rcParams.update({
    "font.size": 22,
    "axes.titlesize": 25,
    "axes.labelsize": 23,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 21,
    "axes.edgecolor": "#cccccc",
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "figure.facecolor": "white",
})


def load_tp4(source):
    """Parse a TP4 CSV (path or bytes) -> (t seconds, {channel: G}, fs)."""
    if isinstance(source, (str, Path)):
        df = pd.read_csv(source, skiprows=8)
    else:
        df = pd.read_csv(io.BytesIO(source), skiprows=8)
    df.columns = [c.strip().rstrip(",").strip() for c in df.columns]
    df = df.dropna(axis=1, how="all")
    t = df.iloc[:, 0].values.astype(float)
    fs = 1.0 / np.median(np.diff(t))
    chans = {}
    for c in df.columns[1:]:
        x = df[c].values.astype(float)
        x -= np.median(x[: int(0.0002 * fs)])  # baseline: first 0.2 ms
        chans[c.split()[0]] = x
    return t, chans, fs


def cfc(x, fs, cls):
    """SAE J211-1 channel-class filter: 2-pole Butterworth, run forward and
    backward (phaseless), corner at 1.65x the class number in Hz."""
    b, a = butter(2, cls * 1.65 / (fs / 2))
    return filtfilt(b, a, x)


def contact_time(t, input_filtered, frac=0.2):
    """First time the filtered input trace reaches frac of its own peak."""
    idx = np.argmax(np.abs(input_filtered) > frac * np.max(np.abs(input_filtered)))
    return t[idx]


def caption(fig, text):
    fig.text(0.5, 0.014, text, ha="center", fontsize=16, color=MUTED)


def rel_ms(t, ch, fs):
    return (t - contact_time(t, cfc(ch["CH5"], fs, 1000))) * 1000.0


def fig_jolt_and_ringing(t, ch, fs, out):
    """Slides 16/17: the impact pulse (both sensors) and the ring-down (top)."""
    bottom = cfc(ch["CH5"], fs, 1000)
    top_z = cfc(ch["CH4"], fs, 1000)
    top_x = cfc(ch["CH2"], fs, 1000)
    tm = rel_ms(t, ch, fs)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 5.6), dpi=200)

    m = (tm > -0.3) & (tm < 2.0)
    ax1.plot(tm[m], bottom[m], color=BLUE, lw=2.5, label="bottom sensor")
    ax1.plot(tm[m], top_z[m], color=ORANGE, lw=2.5, label="top sensor")
    ax1.set_title("The jolt (first 2 ms)")
    ax1.set_xlabel("time (ms) after the plate lands")
    ax1.set_ylabel("acceleration (G)")
    ax1.legend(frameon=False)
    ax1.axhline(0, color="#bbbbbb", lw=1)

    m2 = (tm > 2.0) & (tm < 20.0)
    ax2.plot(tm[m2], top_x[m2], color=ORANGE, lw=1.6)
    ax2.set_title("The ringing that follows")
    ax2.set_xlabel("time (ms) after the plate lands")
    ax2.set_ylabel("acceleration (G)")
    ax2.axhline(0, color="#bbbbbb", lw=1)

    caption(fig, "One drop, 60 in onto the felt stack (specimen 7xadt6); SAE J211 "
                 "CFC-1000 filter.\nRinging shown on the top sensor's side-to-side "
                 "axis.")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(out)
    plt.close(fig)


def fig_standard_filter(t, ch, fs, out):
    """Slide 18: the raw recording vs the same trace after the J211 filter."""
    raw = ch["CH5"]
    filt = cfc(raw, fs, 180)
    tm = rel_ms(t, ch, fs)

    fig, ax = plt.subplots(figsize=(12.4, 5.6), dpi=200)
    m = (tm > -0.3) & (tm < 2.2)
    ax.plot(tm[m], raw[m], color=GRAY, lw=0.9, label="raw recording")
    ax.plot(tm[m], filt[m], color=BLUE, lw=3.0,
            label="after the standard filter (SAE J211, CFC-180)")
    ax.set_xlabel("time (ms) after the plate lands")
    ax.set_ylabel("acceleration (G)")
    ax.legend(frameon=False, loc="upper right")
    ax.axhline(0, color="#bbbbbb", lw=1)

    caption(fig, "Bottom (input) sensor, same drop as the previous slide; the "
                 "same filter is applied to every drop.")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(out)
    plt.close(fig)


def fig_attenuation(drops, out):
    """Slide 19: filtered traces for two specimens under the same conditions."""
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 6.0), dpi=200, sharey=True)
    for ax, (label, (t, ch, fs)) in zip(axes, drops.items()):
        bottom = cfc(ch["CH5"], fs, 1000)
        top_z = cfc(ch["CH4"], fs, 1000)
        tm = rel_ms(t, ch, fs)
        m = (tm > -1) & (tm < 20)
        ax.plot(tm[m], bottom[m], color=BLUE, lw=1.8, label="bottom sensor")
        ax.plot(tm[m], top_z[m], color=ORANGE, lw=1.8, label="top sensor")
        ax.set_title(label)
        ax.set_xlabel("time (ms) after the plate lands")
        ax.axhline(0, color="#bbbbbb", lw=1)
    axes[0].set_ylabel("acceleration (G)")
    axes[0].legend(frameon=False, loc="upper right")
    caption(fig, "Two printed specimens, 60 in onto the same felt stack, same "
                 "day; SAE J211 CFC-1000 filter.")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(out)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="/tmp/drops")
    p.add_argument("--out-dir", default=str(Path(__file__).parent / "media"))
    args = p.parse_args()
    data, out = Path(args.data_dir), Path(args.out_dir)
    out.mkdir(exist_ok=True)

    def first_drop(zname, index=1):
        z = zipfile.ZipFile(data / zname)
        return load_tp4(z.read(sorted(z.namelist())[index]))

    t, ch, fs = first_drop("Marcus_1.zip")
    fig_jolt_and_ringing(t, ch, fs, out / "fig-jolt-and-ringing.png")
    fig_standard_filter(t, ch, fs, out / "fig-standard-filter.png")

    drops = {"specimen 7xadt6": (t, ch, fs),
             "specimen 9GMQYQ": first_drop("jin_1.zip")}
    fig_attenuation(drops, out / "fig-attenuation-filtered.png")
    print("wrote 3 figures to", out)


if __name__ == "__main__":
    main()
