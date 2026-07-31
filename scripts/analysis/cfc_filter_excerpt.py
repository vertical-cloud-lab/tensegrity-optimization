"""The CFC filter as it is actually implemented across this repo's drop-test
analyses, extracted verbatim for audit.

Defined in ``scripts/analysis/drop_test_60in_5felts_analysis.py`` and imported
unchanged by every other ``drop_test_*_analysis.py``. Reproduced here (not
re-exported) so that an external reviewer can see exactly what runs, without
needing the rest of the repo.
"""
from scipy import signal


def cfc_filter(x, fs, cfc):
    """SAE J211 channel-frequency-class low pass, as currently implemented."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)
