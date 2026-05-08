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
    run_campaign,
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
def test_run_campaign_short_loop_completes():
    ax_client = run_campaign(n_iterations=2, batch_size=2, random_seed=0)
    df = ax_client.get_trials_data_frame()
    # 5 pilot + 2 iterations * 2 batch = 9 trials.
    assert len(df) == len(PILOT_DESIGNS) + 4
    # All three objectives must be present in the trial data frame.
    for column in (F_PEAK, SEA, ETA):
        assert column in df.columns, column
        assert df[column].notna().all()
