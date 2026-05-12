"""Application regimes informing simulation parameters.

The repository targets two qualitatively different operating envelopes for
the same multi-material 3D-printed tensegrity-inspired absorber:

* **Crutch tip (issue #18, follow-on tasks 39708fbc / 9832f01a / f21cf79c
  / 7a21d00e).**  A small unit (≤25 mm envelope per task 7a21d00e) bonded
  to the bottom of a forearm crutch. Each foot-strike during gait
  delivers a vertical impulse comparable to the user's body weight at
  hand-strike velocities of ~1–1.5 m/s (≈ a 0.10 m equivalent free-fall
  drop). The clinically relevant figures of merit are (a) peak
  hand-transmitted acceleration (HAVS regime, ISO 5349 weighted 8 Hz to
  1 kHz) and (b) specific energy absorbed per gait cycle.

* **NASA lander / CubeSat shock isolator (issues #14, #16).**  Same unit
  cell, scaled-up sample, used as a deployable crush core or shock
  isolator.  Heritage benchmarks are the MER airbag campaign (~25 m/s
  impact) and SUPERball (~15 m/s impact survival).  GSFC GEVS (GSFC-STD-
  7000B) gives the shock-spectrum target for CubeSats: peak ≤ ~1500 g
  half-sine.

Both regimes are constrained by the **Lansmont M23 drop tower**
(issue #28) which we use for experimental validation:

* peak shock          ≤ 5,000 g
* min half-sine pulse ≥ 0.25 ms
* delta-V             ≤ 9.8 m/s   (32 ft/s)
* payload             ≤ 36 kg     (80 lb)

The two regime dictionaries below are consumed by ``run_regimes.py``.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Regime:
    """Frozen bundle of physics + material + test parameters for one regime."""
    name: str
    description: str
    payload_mass_kg: float       # mass riding on the absorber (mounted above)
    drop_velocity_mps: float      # impact velocity at first contact
    target_peak_g: float          # design target -- not exceeded if successful
    target_pulse_ms: float        # desired half-sine pulse width
    radius_m: float               # T-prism circumscribing radius
    height_m: float               # T-prism height
    strut_radius_m: float         # strut cross-section radius
    strut_density_kgm3: float     # PLA ≈ 1240 (default per #45), PETG ≈ 1270
    cable_stiffness_Npm: float    # representative TPU tendon spring const.
    cable_damping_Nspm: float
    cable_pretension_frac: float   # rest = (1 - frac) * L0; frac=0 -> slack
    sim_duration_s: float
    sim_dt_s: float


# Crutch tip: 75 kg user, ~1.4 m/s hand-strike velocity (≈ 0.10 m drop),
# small 12 mm radius x 25 mm tall unit, soft TPU tendons.
CRUTCH = Regime(
    name="crutch_tip",
    description=("Forearm-crutch tip on standard 75 kg user; foot-strike "
                 "velocity 1.4 m/s, target hand-transmitted shock ≤ 8 g "
                 "with ≥ 5 ms pulse (HAVS-friendly)."),
    payload_mass_kg=75.0,
    drop_velocity_mps=1.4,        # ≈ sqrt(2 g h) for h = 0.10 m
    target_peak_g=8.0,
    target_pulse_ms=5.0,
    radius_m=0.012,               # 24 mm OD envelope (issue #18 task 7a21d00e)
    height_m=0.025,
    strut_radius_m=0.0015,
    strut_density_kgm3=1240.0,    # PLA (per #45; peer-reviewed PLA-TPU bond
                                  # data exists, no published PETG-TPU data)
    cable_stiffness_Npm=2.0e3,    # soft TPU tendon
    cable_damping_Nspm=4.0,
    cable_pretension_frac=0.05,   # 5% prestrain; engages tendons in compression
    sim_duration_s=0.025,
    sim_dt_s=2.0e-5,
)


# NASA CubeSat / small-lander crush core: 5 kg payload, 9.8 m/s impact
# (top of Lansmont M23 envelope; also brackets the SUPERball survival
# velocity), GEVS-style ≤ 1500 g target with ≥ 0.5 ms half-sine.
NASA_LANDER = Regime(
    name="nasa_lander",
    description=("Deployable crush core / CubeSat shock isolator; payload "
                 "5 kg, impact 9.8 m/s (Lansmont M23 max ΔV), target peak "
                 "shock ≤ 1500 g per GSFC GEVS."),
    payload_mass_kg=5.0,
    drop_velocity_mps=9.8,        # 32 ft/s — M23 max ΔV
    target_peak_g=1500.0,
    target_pulse_ms=0.5,
    radius_m=0.10,                # ≈ deployable / 1U CubeSat scale
    height_m=0.20,
    strut_radius_m=0.006,
    strut_density_kgm3=1240.0,    # PLA (per #45; printability stand-in for
                                   # heritage NASA PEI/PEKK; PETG/PEEK Phase-2)
    cable_stiffness_Npm=8.0e3,
    cable_damping_Nspm=5.0,
    cable_pretension_frac=0.05,
    sim_duration_s=0.040,
    sim_dt_s=5.0e-5,
)


REGIMES = {r.name: r for r in (CRUTCH, NASA_LANDER)}


# Lansmont M23 envelope (issue #28) — used to assert each simulated
# scenario is reproducible on the actual lab hardware.
M23 = {
    "peak_g_max": 5000.0,
    "min_pulse_ms": 0.25,
    "max_dV_mps": 9.8,
    "max_payload_kg": 36.0,
}


def assert_within_m23(r: Regime) -> None:
    """Raise AssertionError if a regime falls outside the M23 envelope."""
    assert r.payload_mass_kg <= M23["max_payload_kg"], (
        f"{r.name}: {r.payload_mass_kg} kg exceeds M23 80 lb limit; "
        "scale the test article down for benchtop validation."
    )
    assert r.drop_velocity_mps <= M23["max_dV_mps"], (
        f"{r.name}: ΔV {r.drop_velocity_mps} m/s > M23 max 9.8 m/s."
    )


if __name__ == "__main__":
    for r in REGIMES.values():
        print(f"== {r.name} ==")
        print(f"  {r.description}")
        try:
            assert_within_m23(r)
            print(f"  Lansmont M23: OK")
        except AssertionError as e:
            print(f"  Lansmont M23: NEEDS SCALING -- {e}")
