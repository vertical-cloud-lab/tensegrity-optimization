"""Smoke tests for the tensegrity-inspired BO campaign script."""

from __future__ import annotations

import numpy as np
import pytest

from bo.tensegrity_campaign import (
    ETA,
    F_PEAK,
    PARAMETERS,
    PILOT_DESIGNS,
    SEA,
    TILINGS,
    TOPOLOGIES,
    main,
    simulate_specimen,
)


def test_simulate_specimen_returns_finite_outcomes():
    rng = np.random.default_rng(0)
    for design in PILOT_DESIGNS:
        response = simulate_specimen(design, rng=rng)
        assert response.f_peak_N > 0
        assert response.sea_J_per_g > 0
        assert 0.0 <= response.eta <= 1.0


def test_search_space_covers_documented_topologies_and_tilings():
    by_name = {p["name"]: p for p in PARAMETERS}
    assert tuple(by_name["topology"]["values"]) == TOPOLOGIES
    assert tuple(by_name["tiling"]["values"]) == TILINGS
    # Required design variables consistent with proposal/abstract/NASA grant.
    for required in (
        "strut_diameter_mm",
        "strut_length_mm",
        "tpu_skin_thickness_mm",
        "tpu_skin_width_mm",
        "struts_per_cell",
    ):
        assert required in by_name, required


@pytest.mark.slow
def test_main_short_run_completes(capsys):
    # The default (no --full) runs 5 BO iterations with batch size 2 on top of
    # the pilot seed. We pass --no-plot to keep the test headless and fast.
    exit_code = main(["--no-plot", "--seed", "0", "--batch-size", "2"])
    assert exit_code == 0
    out = capsys.readouterr().out
    expected = f"Completed {len(PILOT_DESIGNS) + 5 * 2} trials"
    assert expected in out
    for column in (F_PEAK, SEA, ETA):
        assert column in out
