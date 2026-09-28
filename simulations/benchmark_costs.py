"""Wall-clock cost of the tensegrity simulation tiers (for BO budgeting).

@sgbaird asked (PR comment 4663414812): "what is the cost of running these
simulations? (i.e., CPU time for a given CPU architecture)".  This script
answers that empirically so the number used in BO acquisition cost models
(e.g. cost-aware / multi-fidelity qNEHVI) is measured, not guessed.

It times the *Tier-C* MuJoCo path that ``bo_evaluator.evaluate_design`` calls
(a single regime drop = one BO objective evaluation) and the full
``run_regimes`` sweep, and prints the CPU model so the figure is portable.

Run::

    python simulations/benchmark_costs.py            # human-readable table
    python simulations/benchmark_costs.py --json     # machine-readable

Tier-B (Newton/Warp) and Tier-A (PolyFEM+IPC) wall-clock numbers are quoted
from the PR history (they need a GPU / a ~25 min source build and are not
re-timed here); see ``simulations/bo_integration.md`` for the full ladder.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
import sys

if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def _cpu_model() -> str:
    """Best-effort human-readable CPU model string."""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine() or "unknown"


def _time(fn, repeats: int) -> dict[str, float]:
    fn()  # warm-up (JIT / import / model compile)
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    return {
        "mean_s": statistics.mean(samples),
        "stdev_s": statistics.pstdev(samples) if len(samples) > 1 else 0.0,
        "min_s": min(samples),
        "repeats": repeats,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    args = ap.parse_args()

    from regimes import CRUTCH, NASA_LANDER
    from run_regimes import simulate
    import bo_evaluator as be

    t3_design = {
        "R_mm": 37.5, "H_mm": 105.0, "twist_deg": 60.0,
        "strut_d_mm": 9.0, "cable_d_mm": 4.5, "topology": "t3_prism",
    }

    results = {
        "cpu": _cpu_model(),
        "cpu_count": __import__("os").cpu_count(),
        "benchmarks": {
            "single_simulate_crutch": _time(lambda: simulate(CRUTCH),
                                             args.repeats),
            "single_simulate_nasa": _time(lambda: simulate(NASA_LANDER),
                                          args.repeats),
            "evaluate_design_tierC": _time(
                lambda: be.evaluate_design(t3_design, regime=CRUTCH),
                args.repeats),
        },
    }

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"CPU: {results['cpu']}  ({results['cpu_count']} logical cores)")
    print(f"{'benchmark':<28} {'mean':>9} {'stdev':>9} {'min':>9}")
    for name, b in results["benchmarks"].items():
        print(f"{name:<28} {b['mean_s']*1e3:>7.1f}ms {b['stdev_s']*1e3:>7.1f}ms "
              f"{b['min_s']*1e3:>7.1f}ms")
    # A BO iteration evaluates one design against one regime = one
    # evaluate_design call; a full 2-regime, 14-run sweep per design costs
    # ~28× a single simulate.
    single = results["benchmarks"]["evaluate_design_tierC"]["mean_s"]
    print()
    print(f"=> Tier-C BO objective eval  ≈ {single*1e3:.0f} ms/design "
          f"(one regime, embarrassingly parallel across the batch).")
    print(f"=> A 9-specimen Sobol batch  ≈ {single*9:.1f} s single-threaded, "
          f"<{single*9/ (results['cpu_count'] or 1):.1f} s on "
          f"{results['cpu_count']} cores.")


if __name__ == "__main__":
    main()
