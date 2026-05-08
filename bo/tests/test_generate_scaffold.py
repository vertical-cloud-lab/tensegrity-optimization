"""Smoke tests for the honegumi-based BO scaffold generator."""

from __future__ import annotations

from bo.generate_scaffold import CONFIG, build_engine, render_script


def test_engine_builds_with_installed_templates():
    engine = build_engine()
    # Each visible CONFIG key must correspond to a known honegumi option row.
    known = {row["name"] for row in engine.option_rows}
    assert set(CONFIG).issubset(known), set(CONFIG) - known


def test_render_script_matches_expected_config():
    script = render_script()
    assert not script.startswith("INVALID:"), script
    # Basic structural assertions for the multi-objective + categorical +
    # batch + visualize + existing-data + custom-threshold combo.
    for fragment in (
        "from ax.service.ax_client import AxClient, ObjectiveProperties",
        "import matplotlib.pyplot as plt",
        "ax_client.create_experiment(",
        "ObjectiveProperties(minimize=True, threshold=",
        "batch_size = 2",
        "ax_client.attach_trial(",
        "ax_client.get_pareto_optimal_parameters(",
    ):
        assert fragment in script, fragment


def test_smoke_render_shrinks_iteration_count():
    full = render_script()
    smoke = render_script(smoke_test=True)
    assert "for i in range(21):" in full
    assert "for i in range(5):" in smoke
