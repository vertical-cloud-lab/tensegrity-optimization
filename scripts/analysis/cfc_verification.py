#!/usr/bin/env python3
"""Verify the repo's ``cfc_filter`` against the SAE J211-1 Appendix C filter.

Issue #94 asked for the drop-tower analysis to be made spot-checkable. This
script checks the lowest-level primitive every drop-test script depends on: the
channel-frequency-class (CFC) low-pass filter.

J211-1 Appendix C specifies a 2-pole Butterworth applied forward and then
backward (phaseless / zero-phase), with

    wd = 2*pi*CFC*2.0775
    wa = tan(wd*T/2)                       T = 1/fs
    a0 = wa**2 / (1 + sqrt(2)*wa + wa**2)
    a1 = 2*a0                              a2 = a0
    b1 = -2*(wa**2 - 1) / (1 + sqrt(2)*wa + wa**2)
    b2 = (-1 + sqrt(2)*wa - wa**2) / (1 + sqrt(2)*wa + wa**2)

    Y(i) = a0*X(i) + a1*X(i-1) + a2*X(i-2) + b1*Y(i-1) + b2*Y(i-2)

The 2.0775 factor is the *single-pass* corner. Because the forward pass and the
backward pass multiply, the *pair* is -3 dB at 1.65*CFC -- that 1.65*CFC figure
is the one usually quoted for a channel class (CFC-180 -> 300 Hz).

The repo's implementation hands 1.65*CFC to ``scipy.signal.butter``, whose Wn
argument is the *single-pass* corner, and then runs ``filtfilt``. So the
two-pass corner lands at 0.802*1.65*CFC instead of 1.65*CFC and every class is
about 20 % narrower than its label.

Run: ``python scripts/analysis/cfc_verification.py``
"""
from __future__ import annotations

import numpy as np
from scipy import signal

SQRT2 = np.sqrt(2.0)


def j211_coeffs(cfc: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """SAE J211-1 Appendix C coefficients, in scipy (b, a) convention."""
    wd = 2.0 * np.pi * cfc * 2.0775
    wa = np.tan(wd / (2.0 * fs))
    den = 1.0 + SQRT2 * wa + wa**2
    a0 = wa**2 / den
    b1 = -2.0 * (wa**2 - 1.0) / den
    b2 = (-1.0 + SQRT2 * wa - wa**2) / den
    # J211 writes Y(i) = a0 X(i) + a1 X(i-1) + a2 X(i-2) + b1 Y(i-1) + b2 Y(i-2);
    # scipy's denominator carries the opposite sign on the recursive terms.
    return np.array([a0, 2.0 * a0, a0]), np.array([1.0, -b1, -b2])


def j211_filter(x: np.ndarray, fs: float, cfc: float) -> np.ndarray:
    b, a = j211_coeffs(cfc, fs)
    return signal.filtfilt(b, a, x)


def repo_coeffs(cfc: int, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """What ``cfc_filter`` in scripts/analysis/ actually builds."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    return signal.butter(2, cutoff / (fs / 2.0), btype="low")


def two_pass_gain(b, a, f, fs):
    """Amplitude response of a forward-backward (filtfilt) application."""
    _, h = signal.freqz(b, a, worN=2.0 * np.pi * np.atleast_1d(f) / fs)
    return np.abs(h) ** 2


def corner_3db(b, a, fs, fmax):
    f = np.logspace(0.0, np.log10(fmax), 400_000)
    g = two_pass_gain(b, a, f, fs)
    return float(f[np.argmin(np.abs(g - 1.0 / SQRT2))])


def main() -> int:
    probes = np.array([300.0, 500.0, 550.0, 600.0, 800.0, 1000.0, 1650.0])
    for fs in (1.25e6, 125e3):
        print(f"\n=== fs = {fs:,.0f} Hz ===")
        print(f"{'class':>9s} {'spec -3dB':>10s} {'J211 impl':>10s} {'repo impl':>10s} "
              f"{'error':>8s} {'effective':>10s}")
        for cfc in (60, 180, 600, 1000):
            bj, aj = j211_coeffs(cfc, fs)
            br, ar = repo_coeffs(cfc, fs)
            fj, fr = corner_3db(bj, aj, fs, fs * 0.45), corner_3db(br, ar, fs, fs * 0.45)
            print(f"CFC-{cfc:<5d} {1.65 * cfc:10.1f} {fj:10.1f} {fr:10.1f} "
                  f"{100 * (fr / fj - 1):+7.1f}% {'CFC-%.0f' % (fr / 1.65):>10s}")

        print(f"\n  two-pass amplitude gain (Hz -> gain)")
        print("  " + " ".join(f"{p:>8.0f}" for p in probes))
        for cfc in (180, 1000):
            bj, aj = j211_coeffs(cfc, fs)
            br, ar = repo_coeffs(cfc, fs)
            print(f"  CFC-{cfc} J211 : " + " ".join(f"{g:8.4f}" for g in two_pass_gain(bj, aj, probes, fs)))
            print(f"  CFC-{cfc} repo : " + " ".join(f"{g:8.4f}" for g in two_pass_gain(br, ar, probes, fs)))
            gj = two_pass_gain(bj, aj, np.array([550.0]), fs)[0]
            gr = two_pass_gain(br, ar, np.array([550.0]), fs)[0]
            print(f"    -> attenuation at 550 Hz: J211 {1 / gj:.1f}x, repo {1 / gr:.1f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
