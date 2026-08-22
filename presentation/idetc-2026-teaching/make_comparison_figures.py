"""Side-by-side comparison graphs for two campaign specimens (PR #100).

One clean single-panel graph per specimen, built for the slide that
contrasts a strong attenuator (6lhxfy) with an amplifier (bag26v) from
the SOBOL + S0 drop-test campaign. Style follows the fig1 cleanup rules
from PR #100: short axis labels, no titles, no in-panel callout text,
pure white background, so the slide author can annotate freely.

Each graph shows one representative drop: the stabilized drop whose
CFC 180 transmissibility sits closest to that specimen's session mean
(101 drops, warm-up discarded), so the single trace is an honest stand-in
for the whole session. Both graphs share identical axis limits.

The traces and the printed transmissibility use the campaign pipeline
exactly (scripts/analysis/drop_test_abc123_blind_analysis.py on the
copilot/add-drop-test-protocol-again branch, called with
baseline="tail" as the campaign runner does): TP4 parse, tail baseline
over the final 30 ms, the pipeline's CFC filter (butter2 low-pass at
300 Hz for CFC 180 + filtfilt), top = tri-axis resultant of CH2 to CH4,
T = top peak / base peak in a +/-5 ms window around the impact. The
minimal pieces are vendored below because that module lives on another
branch; each recomputed T is asserted against the per-drop value in
data/drop-tests/sobol-campaign/figures/campaign_metrics.json (same
branch) so any drift from the campaign numbers fails loudly.

Raw Signal CSVs stay on Box (repo convention). This script fetches the
two it needs into an uncommitted cache next to itself, using the file
IDs from the committed box-ids.json manifests.
"""
import json
import urllib.request
from pathlib import Path

import numpy as np
from scipy import signal
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CACHE = HERE / "raw_cache"

# (specimen, Box shared folder, Signal CSV, Box file id,
#  per-drop t180 recorded in campaign_metrics.json, session mean +/- sd)
DROPS = [
    ("6lhxfy", "q5tyg1as1h0pgqrppa8nsuhnllbhjsnu", "6lhxfy_Signal64.csv",
     "f_2417974432525", 0.893268, (0.8931, 0.0042)),
    ("bag26v", "n5fkbur86gzronh04rf3f00diw0yz2es", "bag26v_Signal47.csv",
     "f_2412423530350", 1.061553, (1.0616, 0.0051)),
]

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def fetch(shared_name: str, file_id: str, dest: Path):
    if dest.exists():
        return
    url = ("https://byu.app.box.com/index.php?rm=box_download_shared_file"
           f"&shared_name={shared_name}&file_id={file_id}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=180).read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


# ---- campaign pipeline, vendored (see docstring) -------------------------
TP4_HEADER_LINES = 9
HALF_WIN_S = 0.005
SEARCH_S = 0.015


def cfc_filter(x, fs, cfc):
    cutoff = {1000: 1650.0, 180: 300.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def windowed_peak(a, i_imp, dt):
    half = max(1, int(HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(a), i_imp + half)
    return float(np.max(np.abs(a[lo:hi])))


def analyze(path: Path):
    d = np.loadtxt(path, delimiter=",", skiprows=TP4_HEADER_LINES,
                   usecols=(0, 1, 2, 3, 4))
    t = d[:, 0]
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    base = np.median(d[int(0.070 / dt):, 1:], axis=0)  # tail baseline
    top = d[:, 1:4] - base[:3]
    ch5 = d[:, 4] - base[3]

    ch5_180 = cfc_filter(ch5, fs, 180)
    i_imp = int(np.argmax(np.abs(ch5_180[:int(SEARCH_S / dt)])))
    top180 = np.sqrt(np.sum(np.stack(
        [cfc_filter(top[:, c], fs, 180) for c in range(3)], 1) ** 2, axis=1))

    pk_in = windowed_peak(ch5_180, i_imp, dt)
    pk_out = windowed_peak(top180, i_imp, dt)

    # time zero = smoothed base jolt first reaches 5 % of its peak
    i0 = int(np.argmax(np.abs(ch5_180) > 0.05 * pk_in))
    tm = (t - t[i0]) * 1e3
    return tm, ch5_180, top180, pk_in, pk_out


# ---- style (matches the cleaned fig1: PR #100 guidelines) ----------------
INK = "#0b0b0b"
INK2 = "#52514e"
BLUE = "#2a78d6"    # bottom sensor
ORANGE = "#eb6834"  # top sensor

plt.rcParams.update({
    "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff",
    "savefig.facecolor": "#ffffff",
    "text.color": INK, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "font.size": 15, "axes.labelsize": 16, "xtick.labelsize": 13,
    "ytick.labelsize": 13, "axes.linewidth": 1.0,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "DejaVu Sans",
})

results = []
for spec, shared, csv_name, file_id, t180_ref, (t_mean, t_sd) in DROPS:
    path = CACHE / csv_name
    fetch(shared, file_id, path)
    tm, base180, top180, pk_in, pk_out = analyze(path)
    t180 = pk_out / pk_in
    assert abs(t180 - t180_ref) < 5e-4, (spec, t180, t180_ref)
    results.append((spec, csv_name, tm, base180, top180, pk_in, pk_out, t180,
                    t_mean, t_sd))

ymax = max(max(r[5], r[6]) for r in results)
ylim = (-0.18 * ymax, 1.32 * ymax)

for spec, csv_name, tm, base180, top180, pk_in, pk_out, t180, t_mean, t_sd in results:
    fig, ax = plt.subplots(figsize=(6.2, 5.6), dpi=200)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.13)
    sel = (tm > -2.0) & (tm < 20.0)
    ax.plot(tm[sel], base180[sel], color=BLUE, lw=2.0, label="bottom sensor",
            zorder=3)
    ax.plot(tm[sel], top180[sel], color=ORANGE, lw=2.0, label="top sensor",
            zorder=2)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("acceleration (G)")
    ax.set_xlim(-2.0, 20.0)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_ylim(*ylim)
    ax.grid(axis="y", color="#e6e4de", lw=0.8, zorder=0)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.legend(loc="upper right", frameon=False, fontsize=12.5)
    out = HERE / f"fig3_compare_{spec}.png"
    fig.savefig(out, facecolor="#ffffff")
    plt.close(fig)
    print(f"{spec} ({csv_name}): peak in {pk_in:.1f} G, peak out {pk_out:.1f} G, "
          f"T180 {t180:.3f} (session mean {t_mean:.3f} +/- {t_sd:.4f})  -> {out.name}")
