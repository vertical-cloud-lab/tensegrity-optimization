#!/usr/bin/env python3
"""Generate ``notebooks/drop_tower_spot_check.ipynb``.

The notebook is the deliverable; this file exists so it stays regenerable and
reviewable as source rather than as a wall of JSON. Run:

    python notebooks/build_spot_check_notebook.py
"""
from __future__ import annotations

import json
from pathlib import Path

# Commit on ``copilot/add-drop-test-protocol-again`` that the notebook pins its
# raw-data URLs to. Pinned by hash, not by branch, so the notebook keeps
# working (and keeps meaning the same thing) after the branch moves.
DATA_COMMIT = "b6a296ebee685b8eec29c1440b4a80c863c1abaa"

CELLS: list[tuple[str, str]] = []


def md(text: str) -> None:
    CELLS.append(("markdown", text.strip("\n")))


def code(text: str) -> None:
    CELLS.append(("code", text.strip("\n")))


# ---------------------------------------------------------------- intro
md(r"""
# Spot-checking the drop-tower analysis

**Companion to [issue #94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94)**
· data pinned to commit
[`b6a296e`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/b6a296ebee685b8eec29c1440b4a80c863c1abaa)
of `copilot/add-drop-test-protocol-again`

This notebook downloads the **raw** polyurethane-arrangement drop data straight
from GitHub and rebuilds the analysis in
[`docs/drop-test-pu-configs-analysis.md`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/b6a296e/docs/drop-test-pu-configs-analysis.md)
from first principles, so every number in that document can be checked without
trusting any code in the repo.

It is organised around the three things a reader has to accept before the
conclusions mean anything:

| Part | The primitive | The question |
|---|---|---|
| **A** | the SAE J211 CFC filter | is `cfc_filter()` actually a CFC filter? |
| **B** | the baseline / zero offset | which zero are the peaks measured from? |
| **C** | `T = peak(out)/peak(in)` | do the published numbers reproduce, and what moves them? |

**Headline of the spot-check, up front, so you can go looking for the mistake in it:**

1. **Part A finds a real bug.** The repo's CFC filter is about **20 % too narrow in
   every channel class** — what is labelled CFC-180 is really ≈ CFC-146. The
   consequence for issue #94's actual question is direct: the published reason for
   introducing a second, wider filter class was *"CFC-180 attenuates the 550 Hz mode
   by roughly 12×"*, and **12.3× is what the buggy filter does**. A correct J211
   CFC-180 attenuates 550 Hz by **5.7×**.
2. **Part B finds that the baseline dominates everything.** Not just "median vs
   pre-trigger" — the answer swings by up to **38 %** depending on *how much* of the
   0.35 ms of available pre-trigger you average. The effects being argued about are
   1–3 %.
3. **Part C reproduces the published table exactly**, then shows that of the two
   processing errors, the baseline is worth ~10× more than the filter.

Run it top to bottom (Colab: *Runtime → Run all*). It downloads ≈ 21 MB.
""")

# ---------------------------------------------------------------- setup
md(r"""
## 0. Setup

Colorblind-safe categorical palette, fixed hue order, one hue per arrangement —
never recycled, so a colour means the same arrangement in every figure below.
""")

code(r"""
import io, zipfile, urllib.request, hashlib
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, integrate

# categorical slots 1/2/3/7 — validated colorblind-safe as an all-pairs set
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#b8b7b0"

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "grid.color": MUTED, "grid.alpha": 0.45, "grid.linewidth": 0.6,
    "axes.grid": True, "axes.axisbelow": True,
    "lines.linewidth": 2.0, "font.size": 11, "figure.dpi": 120,
})
print("ready")
""")

# ---------------------------------------------------------------- data
md(r"""
## 1. Get the raw data

Four zips, one per sheet arrangement, 10 drops each — the 40 captures the
`pu-configs` analysis is built on. URLs are pinned to a **commit hash**, not a
branch name, so this notebook cannot silently start reading different data.

| | arrangement | signals | trigger |
|---|---|---|---|
| **A** | 1/4 in polyurethane sheet alone | 1–10 | 300 G |
| **B** | 1/2 in sheet alone | 11–20 | 300 G |
| **C** | 1/4 in on top of 1/2 in | 22–31 | 150 G |
| **D** | 1/2 in on top of 1/4 in | 32–41 | 150 G |

Signal 21 is a stray capture between blocks B and C and was excluded by the
operator; it is not in these zips.
""")

code(r"""
COMMIT = "%s"
BASE = f"https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/{COMMIT}/data/drop-tests/pu-configs/raw"

ARRANGEMENTS = [
    dict(key="A", label="A: 1/4 in alone",        zip="quarter-in.zip",              trigger_g=300.0, color=SERIES[0]),
    dict(key="B", label="B: 1/2 in alone",        zip="half-in.zip",                 trigger_g=300.0, color=SERIES[1]),
    dict(key="C", label="C: 1/4 over 1/2",        zip="quarter-top-half-bottom.zip", trigger_g=150.0, color=SERIES[2]),
    dict(key="D", label="D: 1/2 over 1/4",        zip="half-top-quarter-bottom.zip", trigger_g=150.0, color=SERIES[3]),
]

CACHE = Path("pu_configs_raw"); CACHE.mkdir(exist_ok=True)
for a in ARRANGEMENTS:
    dest = CACHE / a["zip"]
    if not dest.exists():
        print("downloading", a["zip"], "...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{BASE}/{a['zip']}", dest)
        print(f"{dest.stat().st_size/1e6:.1f} MB")
    a["path"] = dest

for a in ARRANGEMENTS:
    print(f"{a['key']}  {a['zip']:<32s} sha256 {hashlib.sha256(a['path'].read_bytes()).hexdigest()[:16]}")
""" % DATA_COMMIT)

md(r"""
### 1.1 What one capture looks like

The exports are Vishay/PCB **TP4** time-domain CSVs: a 9-line header, then
`Time (sec), CH2, CH3, CH4, CH5` in **G**.

| channel | what it is | full scale |
|---|---|---|
| CH2 / CH3 / CH4 | tri-axial accelerometer, wax-seated in a printed key-seat at the specimen's **top vertex** — the *output* | 14493 / 14993 / 13624 G |
| CH5 | single-axis accelerometer on the **bottom acrylic plate** — the *input*, and the trigger channel | 9443 G |

1.25 MHz sample rate, 20 ms record.
""")

code(r"""
HDR = 9                    # TP4 header lines before the column row
TOP_COLS, CH5 = (0, 1, 2), 3
FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9}
GRAVITY = 9.80665

def load_zip(path):
    out = []
    with zipfile.ZipFile(path) as zf:
        for m in zf.namelist():
            if "Signal" in m and m.lower().endswith(".csv"):
                n = int(Path(m).name.split("Signal")[1].split(".")[0])
                out.append((n, zf.read(m).decode("latin-1")))
    return sorted(out)

def parse(text):
    d = np.genfromtxt(io.StringIO(text), skip_header=HDR, delimiter=",", usecols=(0, 1, 2, 3, 4))
    t, ch = d[:, 0], d[:, 1:5]
    return t, ch, 1.0 / float(np.median(np.diff(t)))

CAPTURES = {a["key"]: load_zip(a["path"]) for a in ARRANGEMENTS}
t0, ch0, fs = parse(CAPTURES["A"][0][1])
print(f"Signal {CAPTURES['A'][0][0]}: {len(t0):,} samples, fs = {fs:,.0f} Hz, record = {1e3*t0[-1]:.2f} ms")
print(CAPTURES["A"][0][1].splitlines()[0:8])
""")

code(r"""
fig, axes = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True)
names = ["CH2 (top X)", "CH3 (top Y)", "CH4 (top Z)"]
for j, (nm, c) in enumerate(zip(names, SERIES)):
    axes[0].plot(1e3 * t0, ch0[:, j], color=c, lw=1.1, label=nm)
    axes[0].annotate(nm, (1e3 * t0[np.argmax(np.abs(ch0[:, j]))], ch0[np.argmax(np.abs(ch0[:, j])), j]),
                     color=c, fontsize=9, xytext=(6, 0), textcoords="offset points")
axes[0].set(ylabel="acceleration (G)", title="Signal 1, arrangement A — raw, unfiltered")
axes[0].legend(frameon=False, fontsize=9, ncol=3)
axes[1].plot(1e3 * t0, ch0[:, CH5], color=SERIES[3], lw=1.1, label="CH5 (base plate)")
axes[1].set(xlabel="time from trigger (ms)", ylabel="acceleration (G)", xlim=(0, 20))
axes[1].legend(frameon=False, fontsize=9)
fig.tight_layout(); plt.show()
""")

md(r"""
Two things to notice, because both come back later:

* the **raw** signal is dominated by a very short, very high-frequency contact
  spike (this is why anything is filtered at all), and
* the record does not sit on zero and does not return to zero — there is a
  ringdown and a slow settle. **Where "zero" is** is therefore a real choice, not
  a formality. That is Part B.
""")

# ---------------------------------------------------------------- metric
md(r"""
## 2. The metric under review

Every drop in this repo is reduced to one number, the *transmissibility*

$$T \;=\; \frac{\max_t \left\lVert \mathbf{a}_{\text{top}}(t) \right\rVert}{\max_t \left\lvert a_{\text{CH5}}(t) \right\rvert},
\qquad
\left\lVert \mathbf{a}_{\text{top}} \right\rVert = \sqrt{a_{\mathrm{CH2}}^2 + a_{\mathrm{CH3}}^2 + a_{\mathrm{CH4}}^2}$$

with both numerator and denominator low-pass filtered to an SAE J211 channel
frequency class, and the maxima taken inside a ±5 ms window around the input
peak.

Three properties of that definition are worth holding onto:

1. it is a ratio of **peaks**, which generally occur at *different instants* and
   are set by *different frequencies*;
2. the numerator is a **vector magnitude**, a nonlinear function of three
   channels — so a per-axis zero-offset error does **not** propagate linearly
   into it; and
3. it depends on the **filter class**, which is the subject of Part A.
""")

# ---------------------------------------------------------------- Part A
md(r"""
---

# Part A — is `cfc_filter()` a CFC filter?

SAE J211-1 defines a set of *channel frequency classes* (CFC). The filter is a
**2-pole Butterworth applied forward and then backward** (phaseless / zero
phase), specified in Appendix C by the difference equation

$$Y_i = a_0 X_i + a_1 X_{i-1} + a_2 X_{i-2} + b_1 Y_{i-1} + b_2 Y_{i-2}$$

with, for sample interval $T$,

$$\omega_d = 2\pi \cdot \mathrm{CFC} \cdot 2.0775, \qquad \omega_a = \tan\!\left(\frac{\omega_d T}{2}\right)$$

$$a_0=\frac{\omega_a^2}{1+\sqrt2\,\omega_a+\omega_a^2},\quad a_1=2a_0,\quad a_2=a_0$$

$$b_1=\frac{-2(\omega_a^2-1)}{1+\sqrt2\,\omega_a+\omega_a^2},\qquad
b_2=\frac{-1+\sqrt2\,\omega_a-\omega_a^2}{1+\sqrt2\,\omega_a+\omega_a^2}$$

**The one thing that matters here is which corner the numbers refer to.** The
familiar "CFC-180 is 3 dB down at 300 Hz" figure is $1.65\times\mathrm{CFC}$ and
describes the **forward-backward pair**. The $2.0775$ inside the coefficients is
the **single-pass** corner — it is larger precisely because running the filter
twice squares its amplitude response, and the factor
$2.0775/1.65 = 1.259$ is what puts the *pair* back at $1.65\,\mathrm{CFC}$.

Here is what the repo does, verbatim:

```python
def cfc_filter(x, fs, cfc):
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)
```

`scipy.signal.butter`'s `Wn` is the **single-pass** corner. So `1.65 * CFC` — a
two-pass number — is being handed to a single-pass argument, and then
`filtfilt` squares it. Both filters below are implemented and compared directly.
""")

code(r"""
SQRT2 = np.sqrt(2.0)

def j211_coeffs(cfc, fs):
    "SAE J211-1 Appendix C, in scipy (b, a) convention."
    wd = 2.0 * np.pi * cfc * 2.0775
    wa = np.tan(wd / (2.0 * fs))
    den = 1.0 + SQRT2 * wa + wa ** 2
    a0 = wa ** 2 / den
    b1 = -2.0 * (wa ** 2 - 1.0) / den
    b2 = (-1.0 + SQRT2 * wa - wa ** 2) / den
    return np.array([a0, 2 * a0, a0]), np.array([1.0, -b1, -b2])

def repo_coeffs(cfc, fs):
    "What scripts/analysis/*.py actually build."
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    return signal.butter(2, cutoff / (fs / 2.0), btype="low")

def cfc(x, fs, c, kind="j211"):
    b, a = (j211_coeffs if kind == "j211" else repo_coeffs)(c, fs)
    return signal.filtfilt(b, a, x)

def two_pass_gain(b, a, f, fs):
    "filtfilt applies the filter twice, so the amplitude response is |H|^2."
    _, h = signal.freqz(b, a, worN=2 * np.pi * np.atleast_1d(f) / fs)
    return np.abs(h) ** 2

def corner_3db(b, a, fs):
    f = np.logspace(0, np.log10(0.45 * fs), 400_000)
    return float(f[np.argmin(np.abs(two_pass_gain(b, a, f, fs) - 1 / SQRT2))])

rows = []
for c in (60, 180, 600, 1000):
    fj = corner_3db(*j211_coeffs(c, fs), fs)
    fr = corner_3db(*repo_coeffs(c, fs), fs)
    rows.append((c, 1.65 * c, fj, fr, 100 * (fr / fj - 1), fr / 1.65))

print(f"{'class':>9s} {'spec -3 dB':>11s} {'J211 impl':>11s} {'repo impl':>11s} {'error':>8s} {'effective':>11s}")
for c, spec, fj, fr, err, eff in rows:
    print(f"CFC-{c:<5d} {spec:11.1f} {fj:11.1f} {fr:11.1f} {err:+7.1f}%  {'CFC-%.0f' % eff:>10s}")
""")

code(r"""
f = np.logspace(1, np.log10(6000), 3000)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
for ax, c in zip(axes, (180, 1000)):
    gj = two_pass_gain(*j211_coeffs(c, fs), f, fs)
    gr = two_pass_gain(*repo_coeffs(c, fs), f, fs)
    ax.semilogx(f, 20 * np.log10(gj), color=SERIES[0], label="SAE J211 App. C")
    ax.semilogx(f, 20 * np.log10(gr), color=SERIES[1], label="repo cfc_filter()")
    ax.axhline(-3, color=MUTED, lw=1.0, ls="--")
    ax.axvline(1.65 * c, color=MUTED, lw=1.0, ls=":")
    ax.axvline(550, color=INK2, lw=1.0)
    ax.annotate("550 Hz\n(claimed mode)", (550, -46), color=INK2, fontsize=8.5,
                xytext=(6, 0), textcoords="offset points")
    ax.annotate(f"spec −3 dB\n{1.65*c:.0f} Hz", (1.65 * c, -3), color=INK2, fontsize=8.5,
                xytext=(-4, 8), textcoords="offset points", ha="right")
    ax.set(xlabel="frequency (Hz)", ylabel="amplitude (dB)", ylim=(-50, 4),
           title=f"CFC-{c}: forward–backward response")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
fig.tight_layout(); plt.show()

probes = np.array([300.0, 500.0, 550.0, 600.0, 800.0, 1000.0])
print("two-pass amplitude gain")
print("      Hz " + " ".join(f"{p:>8.0f}" for p in probes))
for c in (180, 1000):
    for kind, cf in (("J211", j211_coeffs), ("repo", repo_coeffs)):
        g = two_pass_gain(*cf(c, fs), probes, fs)
        print(f"CFC-{c:<4d} {kind}: " + " ".join(f"{v:8.4f}" for v in g))
    gj = two_pass_gain(*j211_coeffs(c, fs), np.array([550.0]), fs)[0]
    gr = two_pass_gain(*repo_coeffs(c, fs), np.array([550.0]), fs)[0]
    print(f"   -> attenuation at 550 Hz:  J211 {1/gj:5.1f}x   repo {1/gr:5.1f}x\n")
""")

md(r"""
### A.1 Why this is the answer to issue #94's actual question

> *it was surprising to me that you went from CFC-180 to suggesting something else*

The recommendation in `drop-test-pu-configs-analysis.md` came down to a criterion
that did not previously exist: **"T computed under CFC-1000 must be as repeatable
as T under CFC-180."** That criterion is what separated arrangement A from
arrangement B — A's T scatters at CV 6.12 % in the wider band, B's at 1.36 %.

And the stated justification for looking at a wider band at all was, verbatim
(§3.2 of that doc):

> *SAE J211's CFC-180 is 3 dB down at 300 Hz, so at the specimens' 550 Hz mode it
> attenuates by roughly **12×**. In other words the metric currently in use
> removes most of the structural response it is meant to be sensitive to.*

The cell above shows **12.3×** is what the *repo's* filter does at 550 Hz. A
correct J211 CFC-180 does **5.7×**. The 12× figure is a property of the bug, not
of J211.

That does not make the argument *wrong* — 5.7× is still substantial attenuation,
and "our headline metric suppresses the band we claim to care about" survives as
a qualitative concern. But the quantity that motivated adding the decisive
criterion was overstated by a factor of ~2, and it was reported as a property of
the standard.

### A.2 Does the bug change the published *numbers*?

Mostly no — which is the honest and slightly boring answer. A peak-to-peak ratio
where **both channels get the same wrong filter** cancels much of the error. The
next cell measures it on real drops rather than arguing about it.
""")

code(r"""
def resultant(a):
    return np.sqrt((a ** 2).sum(axis=1))

SEARCH_S, HALF_WIN_S = 0.012, 0.005

def metrics(t, ch, fs, kind="repo", baseline="median", trigger_g=300.0):
    "One drop -> dict of metrics, under a chosen filter impl and baseline rule."
    dt = 1.0 / fs
    if baseline == "median":
        off = np.median(ch, axis=0)
    else:                                        # pre-trigger mean
        pre0 = np.median(ch[:400], axis=0)
        icross = int(np.argmax(np.abs(ch[:, CH5] - pre0[CH5]) > 0.5 * trigger_g))
        n = int(float(baseline) * 1e-3 * fs)
        lo = max(0, icross - 10 - n)
        off = ch[lo:max(lo + 1, icross - 10)].mean(axis=0)
    x = ch - off
    top, ch5 = x[:, TOP_COLS], x[:, CH5]

    c5_180 = cfc(ch5, fs, 180, kind)
    i = int(np.argmax(np.abs(c5_180[: int(SEARCH_S * fs)])))
    h = int(HALF_WIN_S * fs); lo, hi = max(0, i - h), min(len(t), i + h)

    r180 = resultant(np.stack([cfc(top[:, j], fs, 180, kind) for j in range(3)], 1))
    c5_1k = cfc(ch5, fs, 1000, kind)
    r1k = resultant(np.stack([cfc(top[:, j], fs, 1000, kind) for j in range(3)], 1))

    thr, over = abs(c5_180[i]) / 2, (np.sign(c5_180[i]) * c5_180) >= abs(c5_180[i]) / 2
    l, r = i, i
    while l > lo and over[l - 1]: l -= 1
    while r < hi - 1 and over[r + 1]: r += 1

    return dict(
        input_g=float(abs(c5_180[i])), output_g=float(np.max(r180[lo:hi])),
        width_ms=float(1e3 * (t[r] - t[l])), t_peak_ms=float(1e3 * t[i]),
        T180=float(np.max(r180[lo:hi]) / abs(c5_180[i])),
        T1000=float(np.max(r1k[lo:hi]) / np.max(np.abs(c5_1k[lo:hi]))),
        raw_ch5_g=float(np.max(np.abs(ch5))),
    )

def cv(a):
    a = np.asarray(a, float)
    return 100 * a.std(ddof=1) / a.mean()

PARSED = {a["key"]: [(n,) + parse(txt) for n, txt in CAPTURES[a["key"]]] for a in ARRANGEMENTS}
print("parsed", sum(len(v) for v in PARSED.values()), "captures")
""")

code(r"""
print("effect of the filter bug alone (full-record median baseline, as published)\n")
print(f"{'arr':<20s} {'T180 repo':>12s} {'T180 J211':>12s} {'Δ':>7s} "
      f"{'T1000 repo':>13s} {'T1000 J211':>13s} {'Δ':>7s}")
FILTER_EFFECT = {}
for a in ARRANGEMENTS:
    rows = {k: [metrics(t, ch, f_, kind=k, baseline="median", trigger_g=a["trigger_g"])
                for _, t, ch, f_ in PARSED[a["key"]]] for k in ("repo", "j211")}
    FILTER_EFFECT[a["key"]] = rows
    g = lambda k, f: np.array([r[f] for r in rows[k]])
    print(f"{a['label']:<20s} {g('repo','T180').mean():12.3f} {g('j211','T180').mean():12.3f} "
          f"{100*(g('j211','T180').mean()/g('repo','T180').mean()-1):+6.1f}% "
          f"{g('repo','T1000').mean():13.3f} {g('j211','T1000').mean():13.3f} "
          f"{100*(g('j211','T1000').mean()/g('repo','T1000').mean()-1):+6.1f}%")
print("\n(the 'repo' columns are the numbers published in docs/drop-test-pu-configs-analysis.md)")
""")

md(r"""
So: **under 1 % on `T` at CFC-180, up to ≈ +9 % on `T` at CFC-1000**, and the
CV ordering that drove the recommendation (A far worse than B in the wide band)
is *unchanged*. The bug should be fixed everywhere and the affected figures
regenerated, but on its own it does not overturn a conclusion.

It matters for a different reason: it is the number that was used to *justify*
looking at CFC-1000 in the first place, and it was attributed to the standard.
""")

# ---------------------------------------------------------------- Part B
md(r"""
---

# Part B — where is zero?

The published analysis subtracts a **full-record median** from every channel, on
this stated premise (module docstring of `drop_test_pu_configs_analysis.py`):

> *the record starts on the trigger, so there is no clean pre-trigger window*

The Edison adversarial review found that premise is false. Check it directly —
find the first sample where raw CH5 crosses half the nominal trigger level:
""")

code(r"""
print(f"{'arrangement':<20s} {'trigger':>8s} {'first crossing (ms)':>22s}   {'range':>16s}")
CROSS = {}
for a in ARRANGEMENTS:
    xs = []
    for _, t, ch, f_ in PARSED[a["key"]]:
        base0 = np.median(ch[:400], axis=0)
        i = int(np.argmax(np.abs(ch[:, CH5] - base0[CH5]) > 0.5 * a["trigger_g"]))
        xs.append(1e3 * t[i])
    CROSS[a["key"]] = np.array(xs)
    print(f"{a['label']:<20s} {a['trigger_g']:7.0f}G {np.mean(xs):22.3f}   "
          f"{np.min(xs):6.3f}–{np.max(xs):.3f}")
print("\n-> there IS pre-trigger data: about 0.35 ms of it, ~430 samples at 1.25 MHz.")
""")

code(r"""
_, t, ch, f_ = PARSED["A"][0]
n = int(0.8e-3 * f_)
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.plot(1e3 * t[:n], ch[:n, CH5], color=SERIES[0], lw=1.4, label="CH5 raw")
ax.axvline(CROSS["A"][0], color=INK2, lw=1.2)
ax.axvspan(0, CROSS["A"][0], color=SERIES[2], alpha=0.13)
ax.annotate(f"real pre-trigger\n{CROSS['A'][0]:.3f} ms", (CROSS['A'][0] / 2, 0.72 * ch[:n, CH5].max()),
            ha="center", color=INK2, fontsize=9.5)
ax.annotate("trigger crossing", (CROSS["A"][0], 0.95 * ch[:n, CH5].max()),
            xytext=(8, 0), textcoords="offset points", color=INK2, fontsize=9.5)
ax.axhline(np.median(ch[:, CH5]), color=SERIES[1], ls="--", lw=1.6)
ax.annotate("full-record median (the published 'zero')", (0.45, np.median(ch[:, CH5])),
            xytext=(0, -30), textcoords="offset points", color=SERIES[1], fontsize=9.5)
ax.set(xlabel="time from record start (ms)", ylabel="CH5 (G)",
       title="Arrangement A, Signal 1 — the first 0.8 ms")
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); plt.show()
""")

md(r"""
### B.1 The part that should change how much you trust *any* of these numbers

The obvious fix is "use the pre-trigger window as the baseline instead". But
0.35 ms is not much of a window, and the answer depends on how much of it you
average. Below, the same 40 drops, the same everything, varying only the length
of the pre-trigger averaging window:
""")

code(r"""
WINDOWS = [0.05, 0.10, 0.20, 0.30]
BASE_SWEEP = {}
print(f"{'arrangement':<20s} {'median':>14s} " + " ".join(f"{f'pre {w:.2f}ms':>14s}" for w in WINDOWS))
for a in ARRANGEMENTS:
    row = {}
    for key in ["median"] + [str(w) for w in WINDOWS]:
        Ts = [metrics(t, ch, f_, kind="repo", baseline=key, trigger_g=a["trigger_g"])["T180"]
              for _, t, ch, f_ in PARSED[a["key"]]]
        row[key] = np.array(Ts)
    BASE_SWEEP[a["key"]] = row
    print(f"{a['label']:<20s} " + " ".join(
        f"{row[k].mean():.3f} [{cv(row[k]):.2f}]".rjust(14)
        for k in ["median"] + [str(w) for w in WINDOWS]))
print("\nformat: mean T (CFC-180) [within-arrangement CV %]")
""")

code(r"""
keys = ["median"] + [str(w) for w in WINDOWS]
xlab = ["full-record\nmedian"] + [f"pre-trigger\n{w:.2f} ms" for w in WINDOWS]
x = np.arange(len(keys)); w = 0.2

fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
for i, a in enumerate(ARRANGEMENTS):
    m = [BASE_SWEEP[a["key"]][k].mean() for k in keys]
    c = [cv(BASE_SWEEP[a["key"]][k]) for k in keys]
    axes[0].bar(x + (i - 1.5) * w, m, w * 0.9, color=a["color"], label=a["label"])
    axes[1].bar(x + (i - 1.5) * w, c, w * 0.9, color=a["color"])
axes[0].axhline(1.0, color=INK2, lw=1.2, ls=":", label="T = 1 (no amplification)")
axes[0].set(xticks=x, ylabel="mean T (CFC-180)", ylim=(0.9, 1.52),
            title="the same 40 drops, four zeros")
axes[0].set_xticklabels(xlab, fontsize=9)
axes[0].legend(frameon=False, fontsize=8.5, ncol=2, loc="upper left")
axes[1].axhline(2.0, color=INK2, lw=1.2, ls=":", label="2 % acceptance limit")
axes[1].set(xticks=x, ylabel="within-arrangement CV of T (%)", ylim=(0, 8.6),
            title="…and four different repeatability verdicts")
axes[1].set_xticklabels(xlab, fontsize=9)
axes[1].legend(frameon=False, fontsize=8.5, loc="upper right")
fig.tight_layout(); plt.show()
""")

md(r"""
Read the left panel against the differences the analysis was trying to resolve.
The **between-arrangement** spread in `T` that the whole document argues about is
**1–3 %**. Changing nothing but the length of the baseline window moves `T` by up
to **38 %**, and reorders the arrangements.

The right panel matters just as much: the *repeatability* criterion — the thing
the recommendation was actually decided on — flips too. Under the published
baseline every arrangement passes CV ≤ 2 %; under a 0.05 ms pre-trigger baseline
every arrangement fails.

**So the correct conclusion is stronger than "the published baseline was wrong."**
It is: *with 0.35 ms of pre-trigger, no baseline estimator is defensible at the
1 % level this comparison needs.* The Edison review's verdict — "none of these,
the sweep cannot decide" — is right, but its *replacement* numbers are
window-dependent in the same way and should not be treated as the corrected truth
either.

Why is `T` so baseline-sensitive when the peaks are hundreds of G? Because of
property (2) in §2: the numerator is $\sqrt{x^2+y^2+z^2}$. A per-axis offset error
$\delta$ does not cancel in a magnitude the way it does in a signed peak — near
the peak it enters as a projection onto the instantaneous direction, and it biases
numerator and denominator differently. Small DC errors on three channels do not
average out; they rectify.
""")

# ---------------------------------------------------------------- Part C
md(r"""
---

# Part C — reproduce the published table, then break it down

First: does this notebook, written from scratch, get the same numbers as the
document? If it does not, everything above is moot.
""")

code(r"""
PUBLISHED = {  # docs/drop-test-pu-configs-analysis.md §2
    "A": dict(input_g=370.6, output_g=378.8, width_ms=1.66, T180=1.022, T180_cv=0.43, T1000=1.163, T1000_cv=6.12),
    "B": dict(input_g=261.4, output_g=260.5, width_ms=2.25, T180=0.996, T180_cv=0.34, T1000=0.990, T1000_cv=1.36),
    "C": dict(input_g=174.3, output_g=171.9, width_ms=3.37, T180=0.986, T180_cv=0.95, T1000=1.074, T1000_cv=0.93),
    "D": dict(input_g=183.5, output_g=181.4, width_ms=3.35, T180=0.989, T180_cv=0.49, T1000=1.074, T1000_cv=1.19),
}

cols = [("input G", 16), ("output G", 16), ("width ms", 14), ("T180", 16),
        ("T180 CV%", 14), ("T1000", 16), ("T1000 CV%", 14)]
print(f"{'':<20s}" + " ".join(f"{n:>{w}s}" for n, w in cols))
print(f"{'(ours / published)':<20s}" + " ".join(f"{'-' * w:>{w}s}" for _, w in cols))
for a in ARRANGEMENTS:
    r = FILTER_EFFECT[a["key"]]["repo"]          # published settings: repo filter, median baseline
    p = PUBLISHED[a["key"]]
    g = lambda f: np.array([x[f] for x in r])
    print(f"{a['label']:<20s} "
          f"{g('input_g').mean():7.1f} /{p['input_g']:7.1f}  "
          f"{g('output_g').mean():7.1f} /{p['output_g']:7.1f}  "
          f"{g('width_ms').mean():6.2f} /{p['width_ms']:5.2f}  "
          f"{g('T180').mean():7.3f} /{p['T180']:7.3f}  "
          f"{cv(g('T180')):6.2f} /{p['T180_cv']:5.2f}  "
          f"{g('T1000').mean():7.3f} /{p['T1000']:7.3f}  "
          f"{cv(g('T1000')):6.2f} /{p['T1000_cv']:5.2f}")
""")

md(r"""
Exact match on all seven quantities for all four arrangements. **The published
numbers are what the published code computes** — the disagreement is entirely
about the processing choices, not about arithmetic. That is worth stating plainly,
because it means a reader can focus their scepticism on the two choices in Parts A
and B rather than on whether anything was mis-tabulated.

Now the 2 × 2: which of the two processing errors is actually worth more?
""")

code(r"""
GRID = {}
print("T (CFC-180): mean [CV %]\n")
hdr = f"{'arrangement':<20s}" + "".join(f"{h:>20s}" for h in
      ["median / repo", "median / J211", "pre-0.30 / repo", "pre-0.30 / J211"])
print(hdr)
for a in ARRANGEMENTS:
    cells, store = [], {}
    for base in ("median", "0.30"):
        for kind in ("repo", "j211"):
            v = np.array([metrics(t, ch, f_, kind=kind, baseline=base, trigger_g=a["trigger_g"])["T180"]
                          for _, t, ch, f_ in PARSED[a["key"]]])
            store[(base, kind)] = v
            cells.append(f"{v.mean():.3f} [{cv(v):.2f}]")
    GRID[a["key"]] = store
    print(f"{a['label']:<20s}" + "".join(f"{c:>20s}" for c in cells))

ref = {k: GRID[k][("median", "repo")].mean() for k in GRID}
print("\nshift in mean T relative to the published cell:")
print(f"{'arrangement':<20s} {'filter fix alone':>18s} {'baseline fix alone':>20s}")
for a in ARRANGEMENTS:
    k = a["key"]
    print(f"{a['label']:<20s} "
          f"{100*(GRID[k][('median','j211')].mean()/ref[k]-1):+17.1f}% "
          f"{100*(GRID[k][('0.30','repo')].mean()/ref[k]-1):+19.1f}%")
""")

md(r"""
The baseline is worth roughly **an order of magnitude more** than the filter. If
only one thing gets fixed, fix the capture settings.
""")

code(r"""
fig, ax = plt.subplots(figsize=(9.5, 4.8))
x = np.arange(len(ARRANGEMENTS)); w = 0.34
fil = [100 * (GRID[a["key"]][("median", "j211")].mean() / ref[a["key"]] - 1) for a in ARRANGEMENTS]
bas = [100 * (GRID[a["key"]][("0.30", "repo")].mean() / ref[a["key"]] - 1) for a in ARRANGEMENTS]
ax.bar(x - w / 2, fil, w * 0.92, color=SERIES[0], label="fixing the CFC filter")
ax.bar(x + w / 2, bas, w * 0.92, color=SERIES[1], label="fixing the baseline")
for xi, v in zip(x - w / 2, fil):
    ax.annotate(f"{v:+.1f}%", (xi, v), ha="center", xytext=(0, 4), textcoords="offset points", fontsize=9, color=INK2)
for xi, v in zip(x + w / 2, bas):
    ax.annotate(f"{v:+.1f}%", (xi, v), ha="center", xytext=(0, 4), textcoords="offset points", fontsize=9, color=INK2)
ax.axhspan(-3, 3, color=MUTED, alpha=0.28)
ax.annotate("shaded band = the effect sizes this analysis argues about (1–3 %)",
            (-0.45, -5.4), ha="left", fontsize=9, color=INK2)
ax.set(xticks=x, xticklabels=[a["label"] for a in ARRANGEMENTS], ylim=(-7, 26),
       ylabel="change in mean T (CFC-180), %",
       title="Which processing error is worth more?")
ax.legend(frameon=False, fontsize=9.5)
fig.tight_layout(); plt.show()
""")

# ---------------------------------------------------------------- close
md(r"""
---

## What a reader should take away

**Reproducibility.** Everything published in `drop-test-pu-configs-analysis.md`
reproduces exactly from the raw CSVs. Nothing was mis-transcribed.

**Two defects in the processing, of very different size.**

| | what | size | status |
|---|---|---|---|
| A | `cfc_filter()` is ~20 % narrow in every class — "CFC-180" is really ≈ CFC-146 | < 1 % on `T`(CFC-180), up to +9 % on `T`(CFC-1000) | new here; needs a repo-wide fix |
| B | full-record-median baseline, on a false "no pre-trigger" premise | up to +38 % on `T`, and it reorders arrangements | found by the Edison adversarial review; confirmed and **extended** here |

**The extension of B is the important part.** It is not just that the published
baseline was wrong — it is that with 0.35 ms of pre-trigger *no* baseline choice is
defensible at the 1 % level, so the corrected numbers are not a corrected truth
either. Both the original conclusion and its replacement are downstream of a
capture setting.

**On issue #94's specific question — why the filter class changed.** The move to
CFC-1000 was motivated by a "12× attenuation at 550 Hz" figure attributed to SAE
J211. That figure came from the buggy filter; the standard's value is 5.7×. The
underlying worry (a CFC-180 peak ratio is largely insensitive to the structure it
is supposed to measure) is legitimate and independent of the bug — but the
specific criterion that decided A vs B was introduced on an overstated premise,
after the fact, and its inputs move by more than the effect under a different
baseline. That is enough reason not to act on it.

**What would actually settle it** — unchanged from the adversarial review, and
this notebook only strengthens the first item:

1. **≥ 2 ms pre-trigger and 50–100 ms post-impact capture.** This is the single
   change that retires Part B entirely and makes ringdown-based metrics possible.
2. One common trigger level across all conditions.
3. A randomised, interleaved crossover over ≥ 2 distinct geometries — arrangement
   blocks run back-to-back cannot separate arrangement from drift.
4. Prespecified outcomes (input-conditioned SRS, band-limited transfer with
   coherence) rather than a peak ratio chosen after seeing the data.

## Sources

* **SAE J211-1**, *Instrumentation for Impact Test — Part 1: Electronic
  Instrumentation.* Appendix C gives the CFC digital filter (the 2.0775 factor,
  the difference equation, the forward-and-backward application). The
  $1.65\times\mathrm{CFC}$ −3 dB relation applies to the two-pass pair.
* **ISO 6487**, *Road vehicles — Measurement techniques in impact tests —
  Instrumentation* — the ISO counterpart of the CFC classes, incl. zero-offset
  practice.
* **ISO 5348**, *Mechanical vibration and shock — Mechanical mounting of
  accelerometers.* Note: repo documents have cited "ISO 5347" (calibration
  methods); 5348 is the mounting standard.
* **MIL-STD-810 method 516**, **ASTM D3332 / D7136**, **IEST** shock practice —
  for shock-response-spectrum and drop-test conventions.
* In-repo: [`scripts/analysis/cfc_verification.py`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/HEAD/scripts/analysis/cfc_verification.py)
  (the Part A check as a standalone script) and
  [`edison-trajectories/pu-configs/report/adversarial-review.md`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/b6a296e/edison-trajectories/pu-configs/report/adversarial-review.md)
  (the review that found the baseline problem).
""")

# ---------------------------------------------------------------- emit
nb = {
    "cells": [
        {"cell_type": kind, "id": f"cell-{i:02d}", "metadata": {},
         **({"source": src.splitlines(keepends=True)} if kind == "markdown"
            else {"source": src.splitlines(keepends=True), "outputs": [], "execution_count": None})}
        for i, (kind, src) in enumerate(CELLS)
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": [], "toc_visible": True},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = Path(__file__).resolve().parent / "drop_tower_spot_check.ipynb"
out.write_text(json.dumps(nb, indent=1) + "\n")
print(f"wrote {out} ({len(CELLS)} cells)")
