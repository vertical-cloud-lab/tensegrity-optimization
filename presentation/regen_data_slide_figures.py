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
from scipy.signal import filtfilt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import build_search_space_figure as ssf

# Colors: EMC-adjacent blue/orange, adjusted to pass the palette validator
# (chroma floor and 3:1 surface contrast) while staying near the deck theme.
BLUE = "#1878B8"    # bottom (input) sensor, CH5
ORANGE = "#D96A24"  # top-vertex sensor, CH4 vertical / CH2 lateral
GRAY = "#9a9a9a"    # raw recording
GUIDE_GRAY = "#8c8c8c"  # schematic leader lines
INK = "#333333"
INK2 = "#595959"
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
    """SAE J211-1 Appendix C channel-class filter: the standard's 2-pole
    coefficients (single-pass corner at 2.0775x the class number), run
    forward and backward (phaseless) so the double pass lands at the
    class's -3 dB point. A plain Butterworth at 1.65x the class and then
    filtfilt ends up about 20 percent narrow (the issue #94 finding)."""
    wa = np.tan(np.pi * cls * 2.0775 / fs)
    den = 1.0 + np.sqrt(2.0) * wa + wa * wa
    a0 = wa * wa / den
    b1 = -2.0 * (wa * wa - 1.0) / den
    b2 = (-1.0 + np.sqrt(2.0) * wa - wa * wa) / den
    return filtfilt(np.array([a0, 2.0 * a0, a0]),
                    np.array([1.0, -b1, -b2]), x)


def windowed_peak(tm, x, half_ms=1.5):
    """|peak| within +/-1.5 ms of the largest excursion, as the campaign
    analysis does (drop_test_60in_5felts_analysis.py windowed_peak);
    returns (peak_abs, t_peak_ms, signed value at the peak)."""
    i_imp = int(np.argmax(np.abs(x)))
    m = np.abs(tm - tm[i_imp]) <= half_ms
    seg, seg_t = x[m], tm[m]
    j = int(np.argmax(np.abs(seg)))
    return abs(seg[j]), seg_t[j], seg[j]


def contact_time(t, input_filtered, frac=0.2):
    """First time the filtered input trace reaches frac of its own peak."""
    idx = np.argmax(np.abs(input_filtered) > frac * np.max(np.abs(input_filtered)))
    return t[idx]


def caption(fig, text):
    fig.text(0.5, 0.014, text, ha="center", va="bottom", fontsize=16,
             color=MUTED)


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
    # Panel deliberately untitled (me-madsen, PR #84, 2026-08-20).
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


def draw_sensor_schematic(ax, fig):
    """Left panel: where the two sensors sit on the drop stack (mid-range
    T3 prism from the search-space figure, so the styles match)."""
    params = dict(ssf.MID)
    cu, cv = ssf.struct_center(params)
    # Extra room below the structure for the base plate and impact arrow.
    ppmm = ssf.setup_axes(ax, fig, (cu, cv - 16.0), 128.0, 168.0)
    ssf.draw_structure(ax, params, ppmm)

    bot, top = ssf.nodes(params)
    v_bot = min(ssf.project(p)[1] for p in bot)
    plate_top = v_bot - 6.0
    ax.add_patch(plt.Rectangle((cu - 46.0, plate_top - 8.0), 92.0, 8.0,
                               facecolor="#b8b8b8", edgecolor="none", zorder=2))

    # Sensor dots: blue input sensor on the base plate, orange tri-axis
    # sensor at a top vertex (the nearest one, so the dot reads in front).
    u_top, v_top, _ = max((ssf.project(p) for p in top), key=lambda q: q[2])
    v_rim = max(ssf.project(p)[1] for p in top)
    for (u, v, color) in [(cu - 36.0, plate_top - 4.0, BLUE),
                          (u_top, v_top, ORANGE)]:
        ax.plot([u], [v], marker="o", ms=13, color=color,
                markeredgecolor="white", markeredgewidth=2, zorder=6)
    ax.text(cu - 36.0, plate_top - 16.0, "bottom sensor\n(input)",
            ha="center", va="top", fontsize=18, color=INK)
    ax.annotate("top sensor", xy=(u_top, v_top + 4.0),
                xytext=(u_top, v_rim + 13.0), ha="center", va="bottom",
                fontsize=18, color=INK, zorder=6,
                arrowprops=dict(arrowstyle="-", lw=1.4, color=GUIDE_GRAY,
                                shrinkA=2, shrinkB=6))

    ax.annotate("", xy=(cu + 30.0, plate_top - 10.0),
                xytext=(cu + 30.0, plate_top - 30.0),
                arrowprops=dict(arrowstyle="-|>", lw=3.5, color=INK2,
                                mutation_scale=28), zorder=6)
    ax.text(cu + 30.0, plate_top - 36.0, "impact", ha="center", va="top",
            fontsize=18, color=INK2)


def fig_attenuation(drops, out):
    """The attenuation slide: same drop conditions for two specimens, peak
    markers on both sensors, and the metric the campaign computes,
    T = peak top acceleration / peak bottom acceleration
    (drop_test_60in_5felts_analysis.py: t_ch5 = top CFC-180 tri-axis
    resultant peak / CH5 CFC-180 peak, each within +/-1.5 ms of impact)."""
    fig = plt.figure(figsize=(13.2, 7.0), dpi=200)
    gs = fig.add_gridspec(1, 3, width_ratios=[0.92, 1.5, 1.5],
                          left=0.045, right=0.985, top=0.875, bottom=0.245,
                          wspace=0.24)
    ax_s = fig.add_subplot(gs[0])
    draw_sensor_schematic(ax_s, fig)

    axes = [fig.add_subplot(gs[1])]
    axes.append(fig.add_subplot(gs[2], sharey=axes[0]))
    for ax, (label, (t, ch, fs)) in zip(axes, drops.items()):
        bottom = cfc(ch["CH5"], fs, 180)
        top = np.sqrt(sum(cfc(ch[c], fs, 180) ** 2
                          for c in ("CH2", "CH3", "CH4")))
        tm = rel_ms(t, ch, fs)
        m = (tm > -1) & (tm < 8)
        ax.plot(tm[m], bottom[m], color=BLUE, lw=2.2, label="bottom sensor")
        ax.plot(tm[m], top[m], color=ORANGE, lw=2.2, label="top sensor")
        ax.set_title(label, fontsize=20, color=MUTED, loc="left", pad=10)
        ax.axhline(0, color="#bbbbbb", lw=1)

        pk_b, t_b, y_b = windowed_peak(tm[m], bottom[m])
        pk_t, t_t, y_t = windowed_peak(tm[m], top[m])
        for t_pk, y_pk, pk, color, name, dy in [
                (t_t, y_t, pk_t, ORANGE, "top", 60.0),
                (t_b, y_b, pk_b, BLUE, "bottom", -60.0)]:
            ax.plot([t_pk], [y_pk], marker="o", ms=9, color=color,
                    markeredgecolor="white", markeredgewidth=1.5, zorder=5)
            ax.plot([t_pk, 7.8], [y_pk, y_pk], ls=(0, (4, 3)), lw=1.4,
                    color=color, zorder=4)
            ax.text(7.7, y_pk + dy,
                    rf"$\hat{{a}}_\mathrm{{{name}}}$ = {pk:.0f} G",
                    ha="right", va="center", fontsize=19, color=INK)
        ax.text(3.5, 880.0,
                rf"$T = \hat{{a}}_\mathrm{{top}} \,/\, "
                rf"\hat{{a}}_\mathrm{{bottom}}$ = {pk_t / pk_b:.2f}",
                ha="center", va="top", fontsize=21, color=INK)
        ax.set_ylim(-170, 900)

    axes[0].set_ylabel("acceleration (G)")
    plt.setp(axes[1].get_yticklabels(), visible=False)
    fig.text(0.63, 0.145, "time (ms) after the plate lands", ha="center",
             fontsize=23, color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=2, frameon=False, loc="upper center",
               bbox_to_anchor=(0.63, 1.005))
    caption(fig, "Two printed specimens, 60 in onto the same felt stack, "
                 "same day; SAE J211 CFC-180 filter,\n"
                 "the class the campaign metric uses. The top trace combines "
                 "the top sensor's three axes;\n"
                 "peaks are the largest excursion within 1.5 ms of impact. "
                 "T > 1 amplified, T < 1 attenuated.")
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
