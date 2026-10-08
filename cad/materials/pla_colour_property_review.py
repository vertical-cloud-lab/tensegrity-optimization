#!/usr/bin/env python3
"""Does Bambu PLA Basic colour (white vs black) change stiffness or shock transmission?

Collects the published measurements that bear on the question, puts them on one
axis so the colour effect can be compared against the other noise sources in an
FFF print, and derives the elastic-wave quantities that actually govern shock
transmission (longitudinal wave speed, acoustic impedance, interface
reflection) from the stiffness spread.

Nothing here is a new experiment. Every number is either quoted from a cited
source or derived from one by the closed-form relations printed alongside it.

Run:
    python cad/materials/pla_colour_property_review.py \
        --out cad/materials/pla-colour-property-review.png
"""

from __future__ import annotations

import argparse
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------------
# Source data
# ----------------------------------------------------------------------------

# Wittbrodt & Pearce, Additive Manufacturing 8:110-116 (2015). Five colours of
# filament all extruded from the same NatureWorks 4043D resin, printed at 190 C,
# ASTM D638 tension, crystallinity by XRD. This is the only study found that
# holds the base resin fixed AND reports white and black separately.
WITTBRODT = {
    "Natural": {"uts": 57.16, "uts_err": 0.35, "yield": 52.47, "strain": 2.35, "xtal": 0.93, "xtal_err": 0.06, "sd": 1.09},
    "Black":   {"uts": 52.81, "uts_err": 1.18, "yield": 49.23, "strain": 2.02, "xtal": 2.62, "xtal_err": 0.09, "sd": 3.72},
    "Grey":    {"uts": 50.84, "uts_err": 0.23, "yield": 46.08, "strain": 1.98, "xtal": 4.79, "xtal_err": 0.10, "sd": 0.71},
    "Blue":    {"uts": 54.11, "uts_err": 0.30, "yield": 50.10, "strain": 2.13, "xtal": 4.85, "xtal_err": 0.15, "sd": 0.96},
    "White":   {"uts": 53.97, "uts_err": 0.26, "yield": 50.51, "strain": 2.22, "xtal": 5.05, "xtal_err": 0.18, "sd": 0.82},
}
# The same paper's single most relevant sentence for us: modulus did not track
# colour. "all samples had a fairly constant Young's modulus of 2.78 GPa
# (+/- 0.35)" -> a +/- 12.6 % band that spans every colour tested.
WITTBRODT_E_GPA = 2.78
WITTBRODT_E_ERR_GPA = 0.35

# Bambu Lab PLA Basic Technical Data Sheet V3.0. One sheet covers the whole
# colour range; the quoted +/- is Bambu's own reproducibility band.
BAMBU = {
    "E_xy_mpa": (2580.0, 220.0),
    "E_z_mpa": (2060.0, 170.0),
    "uts_xy_mpa": (35.0, 4.0),
    "uts_z_mpa": (31.0, 3.0),
    "impact_xy_kjm2": (26.6, 2.8),
    "impact_xy_notched_kjm2": (7.9, 1.2),
    "density_kgm3": 1240.0,
}

# Spread across a colour set, as a percentage of the minimum, from studies that
# swept many colours of one brand. These bound the worst case; none of them
# isolates white against black.
COLOUR_SPREADS = [
    ("Modulus, 14 colours (Pandzic 2019)", 18.0),
    ("UTS, 14 colours (Pandzic 2019)", 31.0),
    ("UTS, 8 colours (Yao 2022, eSUN)", 32.0),
    ("UTS, 10 colours (CNC Kitchen)", 15.0),
    ("Layer adhesion, 10 colours (CNC Kitchen)", 48.0),
    ("Impact, 10 colours (CNC Kitchen)", 80.0),
]

# Same-material effects that are NOT colour, for scale.
OTHER_EFFECTS = [
    ("Bambu's own modulus band (+/- 220 MPa)", 17.9),   # (2800-2360)/2360
    ("Bambu's own UTS band (+/- 4 MPa)", 25.8),         # (39-31)/31
    ("Print direction, XY vs Z modulus (Bambu)", 25.2), # (2580-2060)/2060
    ("Print direction, XY vs Z impact (Bambu)", 92.8),  # (26.6-13.8)/13.8
    ("Nozzle temp 200-240 C, black PLA (Petousis 2022)", 21.2),
    ("Print speed 100-600 mm/s, natural PLA (2025)", 13.9),
]

WHITE = "White"
BLACK = "Black"


def wave_quantities(e_pa: float, rho: float) -> tuple[float, float]:
    """Longitudinal bar-wave speed c = sqrt(E/rho) and impedance Z = rho*c."""
    c = math.sqrt(e_pa / rho)
    return c, rho * c


def reflection_coefficient(z1: float, z2: float) -> float:
    """Pressure-amplitude reflection at a normal-incidence interface."""
    return (z2 - z1) / (z2 + z1)


def shock_analysis() -> dict:
    """Derive the shock-transmission consequences of the stiffness spread.

    Shock/stress-wave propagation in a slender member is set by the wave speed
    and the acoustic impedance, both of which depend on E only through a square
    root. That square root is why a stiffness spread that looks large in a
    tensile table is small in a shock problem.
    """
    rho = BAMBU["density_kgm3"]
    e_nom, e_tol = BAMBU["E_xy_mpa"]
    e_lo, e_hi = (e_nom - e_tol) * 1e6, (e_nom + e_tol) * 1e6

    c_lo, z_lo = wave_quantities(e_lo, rho)
    c_hi, z_hi = wave_quantities(e_hi, rho)
    c_nom, z_nom = wave_quantities(e_nom * 1e6, rho)

    # Worst case: one member at the bottom of the band, its neighbour at the
    # top. This is a deliberately pessimistic stand-in for a white part bonded
    # to a black part.
    r = reflection_coefficient(z_lo, z_hi)

    return {
        "density_kgm3": rho,
        "E_nom_mpa": e_nom,
        "E_band_mpa": [e_nom - e_tol, e_nom + e_tol],
        "E_band_spread_pct": 100.0 * (e_hi - e_lo) / e_lo,
        "wave_speed_nom_ms": c_nom,
        "wave_speed_band_ms": [c_lo, c_hi],
        "wave_speed_spread_pct": 100.0 * (c_hi - c_lo) / c_lo,
        "impedance_nom_mrayl": z_nom / 1e6,
        "impedance_band_mrayl": [z_lo / 1e6, z_hi / 1e6],
        "reflection_amplitude": r,
        "reflected_energy_fraction": r * r,
        "transmitted_energy_fraction": 1.0 - r * r,
    }


def wittbrodt_deltas() -> dict:
    """White against black in the one study that controls the base resin."""
    w, b = WITTBRODT[WHITE], WITTBRODT[BLACK]
    return {
        "uts_white_mpa": w["uts"],
        "uts_black_mpa": b["uts"],
        "uts_white_over_black_pct": 100.0 * (w["uts"] - b["uts"]) / b["uts"],
        "yield_white_over_black_pct": 100.0 * (w["yield"] - b["yield"]) / b["yield"],
        "crystallinity_white_pct": w["xtal"],
        "crystallinity_black_pct": b["xtal"],
        "scatter_sd_white_mpa": w["sd"],
        "scatter_sd_black_mpa": b["sd"],
        "modulus_gpa": WITTBRODT_E_GPA,
        "modulus_band_gpa": WITTBRODT_E_ERR_GPA,
        "modulus_band_pct": 100.0 * WITTBRODT_E_ERR_GPA / WITTBRODT_E_GPA,
    }


def make_figure(out_png: str, shock: dict, deltas: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.4),
                             gridspec_kw={"width_ratios": [1.0, 1.25, 1.35]})

    # --- Panel A: white vs black, base resin held fixed ---------------------
    ax = axes[0]
    colours = ["Natural", "Black", "Grey", "Blue", "White"]
    face = ["#e8e2d0", "#2b2b2b", "#8d8d8d", "#3b6fb6", "#f2f2f2"]
    uts = [WITTBRODT[c]["uts"] for c in colours]
    err = [WITTBRODT[c]["uts_err"] for c in colours]
    sd = [WITTBRODT[c]["sd"] for c in colours]
    x = np.arange(len(colours))
    ax.bar(x, uts, yerr=sd, capsize=5, color=face, edgecolor="#333", linewidth=1.1,
           error_kw={"ecolor": "#c1440e", "lw": 1.6})
    for xi, c in enumerate(colours):
        u = WITTBRODT[c]["uts"]
        ax.text(xi, u + WITTBRODT[c]["sd"] + 0.8, f"{u:.1f}", ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{c}\n{WITTBRODT[c]['xtal']:.2f}%" for c in colours], fontsize=9)
    ax.set_xlabel("colour, and its XRD crystallinity", fontsize=9)
    ax.set_ylabel("Ultimate tensile strength (MPa)")
    ax.set_ylim(0, 72)
    ax.set_title("A. One resin, five colours, 190 C\n"
                 f"White is {deltas['uts_white_over_black_pct']:+.1f}% on black; "
                 "modulus was colour-independent",
                 fontsize=10)
    ax.axhspan(WITTBRODT[BLACK]["uts"] - WITTBRODT[BLACK]["sd"],
               WITTBRODT[BLACK]["uts"] + WITTBRODT[BLACK]["sd"],
               color="#c1440e", alpha=0.10, zorder=0)
    ax.text(0.02, 0.28,
            f"E = {deltas['modulus_gpa']:.2f} +/- {deltas['modulus_band_gpa']:.2f} GPa\n"
            "for every colour (one band)\n"
            f"black scatter SD {deltas['scatter_sd_black_mpa']:.2f} MPa\n"
            f"vs white {deltas['scatter_sd_white_mpa']:.2f} MPa",
            transform=ax.transAxes, va="top", fontsize=8.2,
            bbox={"facecolor": "white", "edgecolor": "#bbb", "alpha": 0.95})
    ax.text(0.5, -0.19, "Wittbrodt & Pearce, Addit. Manuf. 8:110 (2015)",
            transform=ax.transAxes, ha="center", fontsize=7, color="#888")

    # --- Panel B: is colour big compared with everything else? --------------
    ax = axes[1]
    labels = [l for l, _ in COLOUR_SPREADS] + [l for l, _ in OTHER_EFFECTS]
    vals = [v for _, v in COLOUR_SPREADS] + [v for _, v in OTHER_EFFECTS]
    kind = ["colour"] * len(COLOUR_SPREADS) + ["other"] * len(OTHER_EFFECTS)
    order = np.argsort(vals)
    y = np.arange(len(labels))
    bar_colour = ["#c1440e" if kind[i] == "colour" else "#3b6fb6" for i in order]
    ax.barh(y, [vals[i] for i in order], color=bar_colour, edgecolor="#333", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([labels[i] for i in order], fontsize=8)
    for yi, i in enumerate(order):
        ax.text(vals[i] + 1.2, yi, f"{vals[i]:.0f}%", va="center", fontsize=8)
    ax.set_xlabel("Spread, max over min (%)")
    ax.set_xlim(0, 105)
    ax.set_title("B. Colour spread (orange) against the other\n"
                 "noise sources in the same print (blue)", fontsize=10)

    # --- Panel C: what that means for a shock ------------------------------
    ax = axes[2]
    ax.axis("off")
    lo, hi = shock["E_band_mpa"]
    clo, chi = shock["wave_speed_band_ms"]
    zlo, zhi = shock["impedance_band_mrayl"]
    lines = [
        ("Shock transmission follows sqrt(E), not E", True),
        ("", False),
        (f"Bambu PLA Basic, every colour   E = {shock['E_nom_mpa']:.0f} +/- 220 MPa", False),
        (f"                                rho = {shock['density_kgm3']:.0f} kg/m3", False),
        (f"Stiffness band                  {lo:.0f} to {hi:.0f} MPa  ({shock['E_band_spread_pct']:.1f}%)", False),
        (f"c = sqrt(E/rho)                 {clo:.0f} to {chi:.0f} m/s  ({shock['wave_speed_spread_pct']:.1f}%)", False),
        (f"Z = rho c                       {zlo:.2f} to {zhi:.2f} MRayl", False),
        ("", False),
        ("Worst-case white-to-black joint (band edge to band edge):", True),
        (f"  amplitude reflection R        {shock['reflection_amplitude']:.3f}", False),
        (f"  energy reflected              {100 * shock['reflected_energy_fraction']:.2f}%", False),
        (f"  energy transmitted            {100 * shock['transmitted_energy_fraction']:.2f}%", False),
        ("", False),
        ("Damping:", True),
        ("Room-temperature tan(delta) of glassy PLA is set by the", False),
        ("polymer, roughly 0.01 to 0.03. A 1 to 3 wt% pigment", False),
        ("loading cannot move it the way infill, wall count and", False),
        ("interlayer bonding do. No study was found that measures", False),
        ("damping as a function of filament colour.", False),
    ]
    yy = 0.97
    for text, bold in lines:
        ax.text(0.0, yy, text, transform=ax.transAxes, va="top", fontsize=8.6,
                family="monospace" if "  " in text else None,
                fontweight="bold" if bold else "normal")
        yy -= 0.047
    ax.set_title("C. Derived consequence for shock and vibration", fontsize=10, loc="left")

    fig.suptitle("White vs black Bambu PLA Basic: what the published data supports",
                 fontsize=13, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_png, dpi=150)
    print(f"wrote {out_png}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="cad/materials/pla-colour-property-review.png")
    p.add_argument("--json_out", default="cad/materials/pla-colour-property-review.json")
    args = p.parse_args()

    shock = shock_analysis()
    deltas = wittbrodt_deltas()

    for k, v in {**deltas, **shock}.items():
        print(f"{k:38s} {v}")

    make_figure(args.out, shock, deltas)
    with open(args.json_out, "w") as fh:
        json.dump({"wittbrodt_white_vs_black": deltas,
                   "shock_transmission": shock,
                   "colour_spreads_pct": dict(COLOUR_SPREADS),
                   "other_effects_pct": dict(OTHER_EFFECTS),
                   "bambu_pla_basic_tds_v3": BAMBU},
                  fh, indent=2)
    print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
