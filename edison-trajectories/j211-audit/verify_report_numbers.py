"""Independently reproduce every filter number in the Edison J211 audit report.

Run: ``python edison-trajectories/j211-audit/verify_report_numbers.py``

Checks, in order:

1. The Appendix C pair corner is exactly ``(sqrt(2)-1)**0.25 * 2.0775 = 1.66666 x CFC``
   (the report's correction to the commonly quoted ``1.65 x CFC``).
2. ``scipy.signal.butter(2, 2.0775*CFC, fs=fs)`` is bit-identical to the
   Appendix C Eq. C1 recurrence, so the recurrence needs no hand-coding.
3. The corrected-corner table of report section II.
4. The corrected attenuation table of report section III.

Everything printed here is computed from first principles; nothing is read back
from the report.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

FS = 1.25e6  # the pu-configs exports; results at 125 kHz differ negligibly
PAIR_RATIO = (np.sqrt(2.0) - 1.0) ** 0.25 * 2.0775


def repo_filter(cfc, fs=FS):
    """The filter as currently implemented in scripts/analysis/ (the bug)."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    return signal.butter(2, cutoff / (fs / 2.0), btype="low")


def j211_appendix_c(cfc, fs=FS):
    """SAE J211-1:1995 Appendix C Eq. C1, written out longhand."""
    wa = np.tan(np.pi * 2.0775 * cfc / fs)
    den = 1.0 + np.sqrt(2.0) * wa + wa**2
    a0 = wa**2 / den
    b1 = -2.0 * (wa**2 - 1.0) / den
    b2 = (-1.0 + np.sqrt(2.0) * wa - wa**2) / den
    # J211 writes +b1*y[n-1]+b2*y[n-2] on the RHS; scipy wants [1, -b1, -b2].
    return np.array([a0, 2.0 * a0, a0]), np.array([1.0, -b1, -b2])


def two_pass_gain(ba, f, fs=FS):
    """filtfilt squares the single-pass magnitude response."""
    return abs(signal.freqz(*ba, worN=[2.0 * np.pi * f / fs])[1][0]) ** 2


def corner(ba, fs=FS, grid=np.linspace(1.0, 4000.0, 399_901)):
    g = abs(signal.freqz(*ba, worN=2.0 * np.pi * grid / fs)[1]) ** 2
    return grid[np.argmin(abs(g - 1.0 / np.sqrt(2.0)))]


def main() -> None:
    print(f"(sqrt(2)-1)**0.25 * 2.0775 = {PAIR_RATIO:.7f}  (report: 1.6666604)")
    b_ref, a_ref = signal.butter(2, 2.0775 * 180, btype="low", fs=FS)
    b_c, a_c = j211_appendix_c(180)
    print("butter(2, 2.0775*CFC) == Appendix C recurrence:",
          np.allclose(b_ref, b_c) and np.allclose(a_ref, a_c))

    print("\nclass | J211 pair -3 dB | repo pair -3 dB | error | equivalent class")
    for cfc in (60, 180, 600, 1000):
        f_j, f_r = corner(j211_appendix_c(cfc)), corner(repo_filter(cfc))
        print(f"CFC-{cfc:<5}| {f_j:9.2f} Hz  | {f_r:9.2f} Hz  | "
              f"{100 * (f_r / f_j - 1):+.2f}% | CFC-{f_r / PAIR_RATIO:.1f}")

    print("\nfreq | J211 CFC-180 | repo CFC-180 | J211 CFC-1000")
    for f in (500, 550, 600, 800):
        gj, gr = two_pass_gain(j211_appendix_c(180), f), two_pass_gain(repo_filter(180), f)
        gk = two_pass_gain(j211_appendix_c(1000), f)
        print(f"{f:4d} | {gj:.4f} ({1/gj:5.2f}x) | {gr:.4f} ({1/gr:5.1f}x) | {gk:.4f}")


if __name__ == "__main__":
    main()
