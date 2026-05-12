"""Generate the tensegrity Bayesian-optimization scaffold via honegumi.

This script wraps :class:`honegumi.core._honegumi.Honegumi` (the engine that
powers the interactive picker at https://honegumi.readthedocs.io/) and renders a
single ``ax-platform``-based BO script tuned to the configuration we want for
the multi-material 3D-printed tensegrity campaign described in
``proposal.tex``:

* ``objective="Multi"``      – minimize peak transmitted force *and*
                                maximize specific energy absorption (SEA).
* ``model="Default"``        – Ax's default GP (BoTorch modular).
* ``task="Single"``          – one experimental task to start (multi-task
                                across rigs/materials can be enabled later).
* ``categorical=True``       – exposes a categorical knob (e.g. base unit cell
                                or TPU shore hardness; see PR #24).
* ``custom_threshold=True``  – allows reference-point thresholds for the MOO
                                hypervolume objective.
* ``existing_data=True``     – seeds the optimizer with previously measured
                                designs (initially synthetic; replace with
                                experimental rows as the campaign progresses).
* ``synchrony="Batch"``      – matches the batch print/test cadence of an
                                undergraduate experimental loop.
* ``visualize=True``         – produces optimization-trace and Pareto plots.

All other knobs (sum/order/linear/composition constraints) default to ``False``
to keep the starter minimal; flip them on by editing ``CONFIG`` below and
re-running this script.

Reproduce with::

    pip install -r bo/requirements.txt
    python bo/generate_scaffold.py                       # writes bo/tensegrity_bo.py
    python bo/generate_scaffold.py --smoke-test -o /tmp/smoke.py  # render short variant
    MPLBACKEND=Agg python /tmp/smoke.py                  # quick smoke run

References
----------
* honegumi tutorials: https://honegumi.readthedocs.io/en/latest/
* honegumi paper:     https://arxiv.org/abs/2502.06815
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import honegumi
import honegumi.core.utils.constants as core_cst
from honegumi.ax._ax import option_rows
from honegumi.core._honegumi import Honegumi
from black import FileMode, format_file_contents

# Configuration matching the picker fields exposed at honegumi.readthedocs.io.
# Only "visible" rows from honegumi.ax._ax.option_rows are valid keys here;
# hidden/derived fields (e.g. ``custom_gen``) are filled in by honegumi.
CONFIG: dict[str, object] = {
    "objective": "Multi",
    "model": "Default",
    "task": "Single",
    "categorical": True,
    "sum_constraint": False,
    "order_constraint": False,
    "linear_constraint": False,
    "composition_constraint": False,
    "custom_threshold": True,
    "existing_data": True,
    "synchrony": "Batch",
    "visualize": True,
}

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "tensegrity_bo.py"


def _template_dirs() -> tuple[str, str]:
    """Return absolute paths to honegumi's bundled Jinja templates."""
    base = Path(honegumi.__file__).resolve().parent
    return str(base / "ax"), str(base / "core")


def build_engine() -> Honegumi:
    """Instantiate :class:`Honegumi` against the installed template files."""
    script_dir, core_dir = _template_dirs()
    return Honegumi(
        cst=core_cst,
        option_rows=option_rows,
        script_template_dir=script_dir,
        script_template_name="main.py.jinja",
        core_template_dir=core_dir,
        core_template_name="honegumi.html.jinja",
    )


def _patch_existing_data_trial_index(script: str) -> str:
    """Use the ``trial_index`` returned by ``attach_trial`` instead of the loop counter.

    Honegumi's ``existing_data`` template assumes Ax assigns trial indices that
    match the loop counter ``i``. That happens in practice today but isn't part
    of Ax's public contract, so we capture the returned index defensively. The
    substitution is idempotent and a no-op when the template changes.
    """
    needle = (
        "    ax_client.attach_trial(parameterization)\n"
        "    ax_client.complete_trial(trial_index=i, raw_data=y_train[i])"
    )
    replacement = (
        "    _, trial_index = ax_client.attach_trial(parameterization)\n"
        "    ax_client.complete_trial(trial_index=trial_index, raw_data=y_train[i])"
    )
    return script.replace(needle, replacement)


def render_script(
    config: dict[str, object] | None = None, smoke_test: bool = False
) -> str:
    """Render and return the BO script for ``config`` (defaults to ``CONFIG``).

    When ``smoke_test`` is True the renderer forces honegumi's ``dummy`` flag,
    which shrinks the BO loop (5 outer iterations instead of 21) so the script
    can be executed quickly to verify it has no errors.
    """
    engine = build_engine()
    options = engine.OptionsModel(**(config or CONFIG))
    if not smoke_test:
        return _patch_existing_data_trial_index(engine.generate(options))

    # Honegumi's public ``generate`` always forces dummy=False on rendered
    # scripts (it only honours SMOKE_TEST for its own test suite). To produce a
    # short script we re-run the same pipeline and override the dummy key.
    selections = engine.process_selections(options)
    selections[core_cst.DUMMY_KEY] = True
    script = engine.template.render(selections)
    formatted = format_file_contents(script, fast=False, mode=FileMode())
    return _patch_existing_data_trial_index(formatted)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination path for the generated BO script "
        f"(default: {DEFAULT_OUTPUT.relative_to(Path.cwd()) if DEFAULT_OUTPUT.is_relative_to(Path.cwd()) else DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the rendered script to stdout instead of (or in addition to) writing it.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Render a short version (~5 BO iterations) intended for fast end-to-end verification.",
    )
    args = parser.parse_args(argv)

    script = render_script(smoke_test=args.smoke_test)

    if script.startswith("INVALID:"):
        # honegumi reports incompatibility via this sentinel string.
        raise SystemExit(script)

    header = (
        "# AUTO-GENERATED by bo/generate_scaffold.py via honegumi "
        f"v{honegumi.__version__}.\n"
        "# Edit bo/generate_scaffold.py and re-run; do not hand-edit unless you\n"
        "# also intend to drop the regeneration workflow.\n"
    )
    rendered = header + script

    if args.print:
        print(rendered)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(f"Wrote {args.output} ({len(rendered.splitlines())} lines).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
