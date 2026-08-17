#!/usr/bin/env python3
"""Four-panel explainer figure for issue #94: what "transmissibility" means,
what the CFC filter does, and how the two interact in the drop-tower metric T.

Panel A - one real drop (pu-configs Signal 1, 1/4-in PU): raw base input (CH5)
          and top-vertex output magnitude sqrt(CH2^2+CH3^2+CH4^2).
Panel B - the same output through a correct SAE J211 CFC-180 vs CFC-1000:
          the filter choice decides whether the ~550 Hz specimen ring
          contributes to the peak, which is why T depends on the filter.
Panel C - filter gain vs frequency: correct J211 CFC-180 / CFC-1000 pairs and
          the repo's buggy CFC-180 (~20 % narrow), with the impact-pulse band
          and the specimen ring frequency marked.
Panel D - true mechanical transmissibility |H(f)| of a base-excited SDOF for
          three damping ratios: a curve over frequency, not a single number,
          and not measurable from one transient drop.

Data: downloads the 1/4-in arrangement zip from the pinned commit b6a296e
(same source as notebooks/drop_tower_spot_check.ipynb), cached locally.

Run: python scripts/figures/transmissibility_explainer_figure.py
"""
from __future__ import annotations

import io
import os
import urllib.request
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

DATA_URL = (
    "https://github.com/vertical-cloud-lab/tensegrity-optimization/raw/"
    "b6a296e/data/drop-tests/pu-configs/raw/quarter-in.zip"
)
CACHE = os.path.join(os.path.dirname(__file__), "_cache_quarter-in.zip")
OUT = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "figures",
    "transmissibility_explainer.png",
)

# --- reference palette (dataviz skill, light mode; slots 1-3 validated) -----
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"

SQRT2 = np.sqrt(2.0)


def j211_coeffs(cfc: float, fs: float):
    """SAE J211-1 Appendix C 2-pole coefficients (single pass), scipy (b, a)."""
    wd = 2.0 * np.pi * cfc * 2.0775
    wa = np.tan(wd / (2.0 * fs))
    den = 1.0 + SQRT2 * wa + wa**2
    a0 = wa**2 / den
    b1 = -2.0 * (wa**2 - 1.0) / den
    b2 = (-1.0 + SQRT2 * wa - wa**2) / den
    return np.array([a0, 2.0 * a0, a0]), np.array([1.0, -b1, -b2])


def j211_filter(x: np.ndarray, fs: float, cfc: float) -> np.ndarray:
    b, a = j211_coeffs(cfc, fs)
    return signal.filtfilt(b, a, x)


def repo_coeffs(cfc: int, fs: float):
    """What scripts/analysis cfc_filter() actually builds (the bug)."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    return signal.butter(2, cutoff / (fs / 2.0), btype="low")


def load_drop() -> tuple[np.ndarray, np.ndarray, float]:
    if not os.path.exists(CACHE):
        urllib.request.urlretrieve(DATA_URL, CACHE)
    with zipfile.ZipFile(CACHE) as zf:
        name = [n for n in zf.namelist() if n.endswith("_Signal1.csv")][0]
        raw = zf.read(name)
    arr = np.genfromtxt(io.BytesIO(raw), delimiter=",", skip_header=9)
    t = arr[:, 0]
    ch = arr[:, 1:5]  # CH2, CH3, CH4 (top vertex tri-axis), CH5 (base)
    fs = 1.0 / np.median(np.diff(t))
    # Baseline: mean of the ~0.35 ms of real pre-trigger data. Adequate for a
    # display figure; see the #94 thread for why it is NOT adequate for 1 %
    # metric comparisons.
    pre = t < 0.30e-3
    ch = ch - ch[pre].mean(axis=0)
    out_mag = np.sqrt((ch[:, 0:3] ** 2).sum(axis=1))
    base = ch[:, 3]
    return t, np.column_stack([base, out_mag]), fs


def style_ax(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=8)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")


def main() -> None:
    t, sig, fs = load_drop()
    base, out = sig[:, 0], sig[:, 1]
    tm = t * 1e3

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    (axA, axB), (axC, axD) = axes

    # ---------- Panel A: what the sensors record ----------
    style_ax(axA, "A.  One real drop (¼-in PU, Signal 1) — the raw record")
    keep = tm <= 12.0
    axA.plot(tm[keep], base[keep], color=BLUE, lw=0.8,
             label="input: base plate (CH5)")
    axA.plot(tm[keep], out[keep], color=ORANGE, lw=0.8,
             label="output: top vertex |a| (CH2–4)")
    axA.set_xlabel("time [ms]", color=INK2, fontsize=9)
    axA.set_ylabel("acceleration [G]", color=INK2, fontsize=9)
    axA.legend(loc="upper right", fontsize=8.5, frameon=False,
               labelcolor=INK2)
    axA.annotate("impact pulse (~2–3 ms)\nburied under kHz-range “hash”",
                 xy=(1.6, 380), xytext=(3.3, 900), fontsize=8.5, color=INK2,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    axA.annotate("specimen “ring” at ~550 Hz\n(free vibration after the pulse)",
                 xy=(5.5, 100), xytext=(6.0, -420), fontsize=8.5, color=INK2,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    axA.set_ylim(-520, 1800)
    axA.text(0.985, 0.52,
             "raw peaks ≈ 1700 G are high-frequency hash,\n"
             "not the pulse — this is why a standardized\n"
             "filter is applied before quoting any peak",
             transform=axA.transAxes, ha="right", va="top", fontsize=8.5,
             color=INK2)

    # ---------- Panel B: the filter sets what survives into "the peak" ----------
    style_ax(axB, "B.  Same output, two filters — the filter sets what "
                  "survives into “the peak”")
    out180 = j211_filter(out, fs, 180.0)
    out1000 = j211_filter(out, fs, 1000.0)
    base180 = j211_filter(base, fs, 180.0)
    base1000 = j211_filter(base, fs, 1000.0)
    axB.plot(tm[keep], out[keep], color=MUTED, lw=0.6, alpha=0.40,
             label="unfiltered (peak ≈ 1717 G, off scale)")
    axB.plot(tm[keep], out1000[keep], color=ORANGE, lw=1.4,
             label="CFC-1000 (passes to 1667 Hz): fast structure + ring kept")
    axB.plot(tm[keep], out180[keep], color=AQUA, lw=1.4,
             label="CFC-180 (passes to 300 Hz): smoothed to the pulse")
    for y, c in ((out1000, ORANGE), (out180, AQUA)):
        i = int(np.argmax(np.abs(y)))
        axB.plot(tm[i], y[i], "o", color=c, ms=6, mec=SURFACE, mew=1.2)
    axB.set_ylim(-60, 1120)
    axB.set_xlabel("time [ms]", color=INK2, fontsize=9)
    axB.set_ylabel("acceleration [G]", color=INK2, fontsize=9)
    axB.legend(loc="upper right", fontsize=8.5, frameon=False,
               labelcolor=INK2)
    T180 = np.max(np.abs(out180)) / np.max(np.abs(base180))
    T1000 = np.max(np.abs(out1000)) / np.max(np.abs(base1000))
    axB.text(0.985, 0.60,
             f"T = peak(out)/peak(in), this drop:\n"
             f"  CFC-180:   T = {T180:.3f}\n"
             f"  CFC-1000: T = {T1000:.3f}\n"
             "(correct J211 filters, 0.30 ms\n pre-trigger baseline)",
             transform=axB.transAxes, ha="right", va="top", fontsize=8.5,
             color=INK, family="monospace")

    # ---------- Panel C: filter gain vs frequency ----------
    style_ax(axC, "C.  The filter itself — gain vs frequency (and the repo bug)")
    f = np.logspace(1, np.log10(5000), 800)
    for cfc, color, lab in ((180.0, AQUA, "CFC-180, correct J211"),
                            (1000.0, ORANGE, "CFC-1000, correct J211")):
        b, a = j211_coeffs(cfc, fs)
        _, h = signal.freqz(b, a, worN=f, fs=fs)
        axC.plot(f, np.abs(h) ** 2, color=color, lw=1.4, label=lab)
    b, a = repo_coeffs(180, fs)
    _, h = signal.freqz(b, a, worN=f, fs=fs)
    axC.plot(f, np.abs(h) ** 2, color=AQUA, lw=1.2, ls="--",
             label="“CFC-180” as coded (~20 % narrow)")
    axC.axvspan(10, 250, color=GRID, alpha=0.55, lw=0)
    axC.text(12, 0.50, "most impact-pulse\nenergy lives here", fontsize=8.5,
             color=INK2)
    axC.axvline(550, color=MUTED, lw=0.9, ls=":")
    axC.text(575, 0.62, "specimen ring\n~550 Hz", fontsize=8.5, color=INK2)
    # gains of the two CFC-180 variants at 550 Hz
    for coeffs, ytxt in ((j211_coeffs(180.0, fs), 0.24),
                         (repo_coeffs(180, fs), 0.10)):
        _, h550 = signal.freqz(*coeffs, worN=[550.0], fs=fs)
        g = np.abs(h550[0]) ** 2
        axC.plot(550, g, "o", color=AQUA, ms=5, mec=SURFACE, mew=1.0)
        axC.annotate(f"{g:.3f} ({1/g:.1f}× down)", xy=(550, g),
                     xytext=(900, ytxt), fontsize=8, color=INK2,
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    axC.set_xscale("log")
    axC.set_xlabel("frequency [Hz]", color=INK2, fontsize=9)
    axC.set_ylabel("two-pass amplitude gain", color=INK2, fontsize=9)
    axC.set_ylim(-0.03, 1.1)
    axC.legend(loc="lower left", fontsize=8.5, frameon=False,
               labelcolor=INK2)

    # ---------- Panel D: true transmissibility ----------
    style_ax(axD, "D.  Actual transmissibility — a curve of the structure, "
                  "not one number")
    r = np.logspace(-1, 1, 600)
    for zeta, color in ((0.05, BLUE), (0.07, ORANGE), (0.20, AQUA)):
        H = np.sqrt((1 + (2 * zeta * r) ** 2)
                    / ((1 - r**2) ** 2 + (2 * zeta * r) ** 2))
        axD.plot(r, H, lw=1.4, color=color,
                 label=f"damping ζ = {zeta:.0%}")
    axD.axhline(1.0, color=MUTED, lw=0.8, ls=":")
    axD.axvline(SQRT2, color=MUTED, lw=0.8, ls=":")
    axD.text(1.5, 4.5, "isolation only\nabove √2·fₙ",
             fontsize=8.5, color=INK2)
    axD.text(0.72, 5.6, "amplification\nnear resonance", fontsize=8.5,
             color=INK2, ha="right")
    axD.annotate("our specimens sit here\n(fₙ·τ ≈ 0.9–1.7)",
                 xy=(1.0, 7.3), xytext=(0.135, 2.6), fontsize=8.5, color=INK2,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    axD.set_xscale("log")
    axD.set_yscale("log")
    axD.set_xlabel("excitation frequency / natural frequency  (f / fₙ)",
                   color=INK2, fontsize=9)
    axD.set_ylabel("|output| / |input|  at each frequency", color=INK2,
                   fontsize=9)
    axD.legend(loc="lower left", fontsize=8.5, frameon=False,
               labelcolor=INK2)

    fig.tight_layout(pad=1.6)
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    fig.savefig(OUT, facecolor=SURFACE, bbox_inches="tight")
    print(f"T(CFC-180) = {T180:.4f}   T(CFC-1000) = {T1000:.4f}")
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
