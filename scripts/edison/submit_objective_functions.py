"""Submit + fetch 5 Edison LITERATURE_HIGH queries — one per data source.

Context: issue #51 / issue #36 comment 4509305026. For each of the five
measurement modalities that the lab plans to use on the multi-material
(PETG strut + TPU 85A tendon, Bambu H2D) tensegrity energy-absorber program,
ask Edison to tie the raw signal back to candidate Bayesian-optimization
objectives, constraints, and characterization settings.

Per repo convention:

* edison-client reads ``EDISON_PLATFORM_API_KEY``; we mirror the documented
  ``EDISON_API_KEY`` into that variable so the script runs unmodified in CI.
* Submit all five tasks non-blocking (``create_task``) so we get every
  ``task_id`` up front; then call ``run_tasks_until_done`` once on the full
  list so the polling overlaps. Each result is committed verbatim under
  ``edison-trajectories/objective-functions/<slug>-<task_id>.{md,json}``.
* If a task is still ``in progress`` when the script's wall-clock budget
  expires, the placeholder JSON next to it documents the task_id so a
  follow-up session can ``fetch_task`` and overwrite the placeholder.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY; copilot env exposes
# EDISON_API_KEY. Mirror so EdisonClient() picks it up.
if os.environ.get("EDISON_API_KEY") and not os.environ.get("EDISON_PLATFORM_API_KEY"):
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "objective-functions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Project context block, identical across queries so Edison can disambiguate
# the unusual material/geometry/use-case stack without our re-typing it
# differently each time.
CONTEXT = """\
Project context (identical for every sub-question — answer the per-data-source
question below in light of all of it):

* Specimen: multi-material 3D-printed tensegrity-inspired energy absorber.
  Strut material PETG, tendon/skin material TPU 85A (NinjaFlex-class,
  E ~12 MPa secant, sigma_break ~26 MPa, rho ~1200 kg/m^3, strain-at-break
  ~550-660%). Printed on a Bambu H2D dual-extrusion FFF system. Baseline
  topology is a 3-bar T-prism with stretch goals to a 6-bar SUPERball-style
  icosahedron and stacked / tiled variants. Bounding sphere ~200 mm,
  system mass <= 500 g, relative density ~10-25%.
* Use-case framings: (a) crutch-tip / cane-tip impact attenuator,
  (b) planetary-lander payload cradle (SUPERball lineage), and
  (c) the lab's egg-drop demo (rigid concrete floor, ASTM D5276 worst-case +
  random orientations, drop heights 0.5-3 m, m_egg = 55 +/- 5 g).
* Optimization framing: a hand-customized Ax / BoTorch multi-objective
  Bayesian-optimization campaign (qNEHVI) is already scaffolded (PR #30 +
  PR #33). Design space includes strut diameter, strut length, TPU cable
  diameter, twist angle, prestress, PETG infill %, interface wrap thickness,
  struts per cell, topology (T-prism, simplex-4-strut, truncated octahedron,
  stacked-prism, ...), tiling (1x1x1 - 3x3x2), TPU shore (85A/95A), infill
  pattern, build orientation. Current placeholder objectives:
  min F_peak_N, max SEA_J_per_g, max efficiency eta. Cycle / reuse count
  N_reuse is a candidate secondary objective.
* Companion sim ladder (PR #33): MuJoCo (regime C) -> NVIDIA Newton/Warp
  (regime B, differentiable XPBD) -> PolyFEM+IPC or DiffPD (regime A,
  high-fidelity). Sim and experiment are intended to be co-trained via a
  MultiTaskGP / multifidelity BO loop.
* Already in the lab and recently observed in person on 2026-05-21
  (video https://youtu.be/RNjpAmWWmkQ): a Lansmont Model 23 shock test
  system, a Polytec VibroFlex QTec single-point LDV, a small electrodynamic
  shaker, and a "slug firing" / pneumatic gas-gun setup adjacent to the LDV.
  High-speed camera is checked out from PSC; slow-motion phone capture is
  the preliminary fallback.

For the data source described below, answer each lettered sub-question
explicitly and with primary, peer-reviewed citations (DOIs where available).
Where you must give a recommended numeric value, justify it from a cited
source rather than rule-of-thumb.

Sub-questions (answer ALL of them):

  (a) What raw observable(s) does this data source produce on a tensegrity
      energy-absorber specimen, and what physical quantities can be derived
      from those observables (with the integration / filtering / windowing
      step required for each)?

  (b) Which of those derived quantities are the most defensible candidates
      for use as Bayesian-optimization OBJECTIVES (to minimize or maximize)?
      Discuss at minimum: peak transmitted force / acceleration g_max,
      specific energy absorption SEA, plateau / crush efficiency eta,
      densification strain, transmissibility / loss factor, settling time
      / damping ratio zeta, cycle / reuse count N_reuse, and any other
      figure of merit specific to this modality. Comment on noise floors,
      repeatability (CoV across nominally identical specimens), and units.

  (c) Which derived quantities are better cast as CONSTRAINTS (hard cutoffs
      or chance-constraints in qNEHVI / NEHVI), and what threshold values
      have been used in peer-reviewed studies on comparable architected
      materials / tensegrity / foams / honeycomb?

  (d) What CHARACTERIZATION SETTINGS does the literature recommend for this
      modality on architected polymer impact absorbers? Be specific:
      sampling rate, anti-alias filter, transducer range / sensitivity,
      mounting / standoff, trigger / pretrigger, frame rate + shutter +
      aperture (if optical), excitation profile, window length, number of
      averages, ASTM / ISO / JEDEC standards the protocol should follow.

  (e) How should the resulting per-specimen measurements be integrated into
      the BO campaign in (PR #30 + PR #33)? Specifically: which Ax
      `Metric` / `Objective` shape, observation_noise (heteroscedastic
      vs. homoscedastic), per-trial cost / wall-clock budget, fidelity
      tier in the multifidelity ladder, and how the modality complements
      or substitutes for the other four data sources in the lab.

  (f) Top gotchas, failure modes, and cross-talk artifacts that would
      silently corrupt the BO objectives if ignored (e.g. accelerometer
      ringing above its resonance, LDV speckle dropout, high-speed-camera
      rolling shutter, shaker-fixture resonance, gas-gun barrel friction
      jitter). Give 5-10 ranked items.

  (g) A numbered references section (DOI when available) supporting every
      quantitative claim in (a)-(f).

Cite only primary, peer-reviewed sources or established standards
(ASTM, ISO, JEDEC, NASA / NIST technical reports). Do NOT fabricate DOIs.
"""

QUERIES: list[dict[str, str]] = [
    {
        "slug": "01-accelerometer",
        "headline": (
            "Accelerometer-based shock + ringdown measurement on a "
            "Lansmont M23 drop tower"
        ),
        "data_source": """\
Data source 1 of 5 — Accelerometer-based shock + free-decay measurement on
a Lansmont Model 23 (M23) shock test system.

Configuration as discussed with Jeff in the 2026-05-21 walkthrough:
  * One accelerometer rigidly mounted to the M23 drop table / waveform-
    programmer plate.
  * A second accelerometer mounted to a custom plate that sits on top of
    the tensegrity specimen, sandwiching the specimen between the two
    plates (analogous to ASTM D1596 / D4168 / D5276 / D6537 cushion-test
    geometry).
  * Lansmont Test Partner DAQ + TouchTest Shock II controller.
  * Specimen mass ~5-30 g (PETG+TPU cells well below the 80 lb / 36 kg
    payload limit), worst-case drop height 0.61 m (24 in) per ASTM D5276
    "free fall on hard surface" baseline, ramping up to 3 m for the
    egg-drop framing.
  * Critically: we want BOTH the initial ~200 ms half-sine shock pulse
    (peak g, pulse duration, DeltaV) AND the subsequent ~10 s of free
    decay / ringdown to extract damping and the lowest specimen
    eigenfrequencies. The default Lansmont post-trigger window is too
    short for the ringdown portion -- comment on appropriate capture
    length and sample-rate settings.
""",
    },
    {
        "slug": "02-high-speed-camera",
        "headline": (
            "High-speed (or slow-motion phone) video of the drop event "
            "for DIC-style strain mapping and densification tracking"
        ),
        "data_source": """\
Data source 2 of 5 — High-speed video of the drop / crush event on the M23.

Two tiers are available:
  * High end: a high-speed camera checked out from the PSC (typical
    spec: monochrome, global shutter, 1-5 kfps at usable resolution,
    LED area lights).
  * Preliminary: a smartphone slow-motion setting (typically 240-960 fps
    rolling shutter, color, ~1080p).

Use cases we care about:
  * Visual confirmation of failure mode (strut fracture vs. tendon
    snap vs. joint pull-out vs. plate spall-back).
  * Frame-by-frame measurement of densification strain / crush
    displacement of the specimen plate-to-plate gap, then sync that
    against the accelerometer-derived force-displacement curve.
  * Optional 2D digital image correlation (DIC) on a speckle-painted
    face of the specimen to estimate full-field strain and bar
    buckling onset.
  * Reusability / re-deployability scoring: did the specimen return
    to its original shape between drops? Frame-comparison metric.
""",
    },
    {
        "slug": "03-shaker-transfer-function",
        "headline": (
            "Electrodynamic shaker + base accelerometer + top accelerometer "
            "for transmissibility / transfer-function measurement"
        ),
        "data_source": """\
Data source 3 of 5 — Electrodynamic shaker with the specimen sandwiched
between a base accelerometer (on the shaker armature) and a tip
accelerometer (on a fixture plate at the specimen top), used to measure
the base-to-top transmissibility T(f) = |X_top(f) / X_base(f)| and
extract modal parameters.

Configuration:
  * Small lab shaker (~10-50 N rated, +/-1 g sine sweep capability),
    typical electrodynamic class (e.g. Bruel & Kjaer 4810 / TIRA
    TV-50018 / Modal Shop 2007E / equivalent -- recommend a reasonable
    choice from the literature if a specific model is preferred for
    polymer architected-material modal testing).
  * Sine sweep, broadband random, and / or chirp excitation.
  * Frequency range of interest: ~10 Hz to ~10 kHz (covering the
    structural modes of a 200 mm tensegrity cell as well as the
    cushioning-attenuation band of interest at 30-500 Hz).
  * Specimen prestress is a design variable in our BO campaign, so the
    transfer function must be repeated at multiple prestress points
    per specimen.

What we want from this modality, beyond the time-domain shock test:
  * Linear / quasi-linear identification of the lowest natural
    frequencies and damping ratios (and how they shift with prestress
    and tiling), as a low-amplitude / non-destructive proxy that can
    rank designs cheaply before committing a destructive drop or
    slug-gun shot.
  * Loss factor eta and storage modulus E'(f) for the assembled cell.
""",
    },
    {
        "slug": "04-slug-firing-gas-gun",
        "headline": (
            "Pneumatic slug-firing / gas-gun system for longer-duration "
            "impulse on tiled small-cell specimens"
        ),
        "data_source": """\
Data source 4 of 5 — Pneumatic "slug firing" / gas-gun system observed
adjacent to the Polytec LDV in the lab walkthrough. Jeff noted this
system produces a LONGER shock impulse than the M23 drop tower (so it
probes a different time-scale regime), and that an interesting variant
would be a tessellated small-unit-cell specimen with a hard plate in
front (i.e. a sacrificial / armour-plate framing).

Configuration as we understand it:
  * Compressed-gas reservoir + barrel, firing a metallic or polymer
    "slug" at a target plate held in a catch frame.
  * Velocities typically ~10-200 m/s (intermediate / sub-ordnance
    regime between drop tower (~5-10 m/s) and split-Hopkinson /
    Taylor-impact (~100-2000 m/s)).
  * Diagnostics: in-line photogate or laser tripwire for slug
    velocity; force on backing plate via piezo load washer or
    derived from the LDV signal (data source 5); high-speed camera
    side view.

Use cases we care about:
  * Probing strain-rate sensitivity of TPU 85A and PETG that is NOT
    observable on the M23 drop tower (the slug delivers a higher peak
    pressure and a longer impulse than free-fall from the M23's
    24-32 ft/s DeltaV).
  * Evaluating tiled / foam-like cell arrays (Pajunen-style or
    truncated-octahedron tilings from PR #24) as armour-style
    energy absorbers behind a sacrificial plate.
  * Generating a higher-energy data point for the multifidelity BO
    so the GP is informed beyond the M23 energy envelope.
""",
    },
    {
        "slug": "05-polytec-qtec-ldv",
        "headline": (
            "Polytec VibroFlex QTec single-point laser Doppler vibrometer "
            "for non-contact velocity / displacement"
        ),
        "data_source": """\
Data source 5 of 5 — Polytec VibroFlex QTec single-point laser Doppler
vibrometer (100 kHz configuration; sub-pm displacement resolution,
+-30 m/s velocity range, 1550 nm IR measurement laser + 520 nm
targeting laser, VibroFlex Connect VFX-F-110 front-end; closest
literature analogue is Gretarsson & Lindell 2023 with NI 9223 1 MS/s
DAQ -- previously surveyed in edison-trajectories/
2026-05-08-equipment-m23-qtec-1a0f4a70.{md,json}).

Two intended deployments:
  * On the drop-tower side: pointed at the specimen-top plate to give
    a non-contact velocity history that doubly checks the top-mounted
    accelerometer (data source 1). Removes the +/-200 g range / mass-
    loading bias of an attached IEPE accelerometer for very small or
    very compliant cells.
  * On the slug-firing / gas-gun side (data source 4): pointed at the
    back face of the target plate to give a high-bandwidth particle-
    velocity history during the longer impulse event, from which the
    transmitted pressure-time profile can be back-computed.

Because the QTec is non-contact and non-mass-loading, it can also be
swept across multiple measurement points on the same specimen between
shots (poor-man's scanning LDV) to estimate operating deflection
shapes.
""",
    },
]


def build_prompt(q: dict[str, str]) -> str:
    """Combine the per-query data-source block with the shared context."""
    return f"""\
{q['headline']}.

{q['data_source']}
{CONTEXT}
"""


def main() -> int:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )

    submitted: list[dict] = []
    print(f"[submit] {len(QUERIES)} LITERATURE_HIGH tasks ->", flush=True)
    for q in QUERIES:
        placeholder = OUT_DIR / f"{q['slug']}-SUBMITTED.json"
        if placeholder.exists():
            existing = json.loads(placeholder.read_text())
            task_id = existing.get("task_id")
            print(f"  - {q['slug']}: reusing prior task_id={task_id}", flush=True)
            submitted.append({**q, "task_id": task_id})
            continue
        task = {"name": JobNames.LITERATURE_HIGH, "query": build_prompt(q)}
        resp = client.create_task(task)
        # create_task returns trajectory_id as a plain string (per repo memory)
        task_id = resp if isinstance(resp, str) else getattr(
            resp, "task_id", None
        ) or getattr(resp, "trajectory_id", None) or str(resp)
        print(f"  - {q['slug']}: task_id={task_id}", flush=True)
        submitted.append({**q, "task_id": task_id})
        # SUBMITTED placeholder so the trajectory dir is non-empty even if we
        # hit the session wall-clock before fetch.
        placeholder = OUT_DIR / f"{q['slug']}-SUBMITTED.json"
        placeholder.write_text(
            json.dumps(
                {
                    "slug": q["slug"],
                    "headline": q["headline"],
                    "task_id": task_id,
                    "job": "LITERATURE_HIGH",
                    "status": "submitted",
                    "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
                indent=2,
            )
            + "\n"
        )

    # Poll each task with get_task(task_id) until it reaches a terminal
    # state. run_tasks_until_done() rebuilds + resubmits TaskRequests rather
    # than fetching by task_id, so we cannot reuse it here.
    TERMINAL = {"success", "failed", "cancelled", "error", "crashed"}
    POLL_INTERVAL_S = 30
    PER_TASK_BUDGET_S = 30 * 60  # 30 min per task

    results: list = []
    for q in submitted:
        task_id = q["task_id"]
        print(f"[fetch] polling {q['slug']} ({task_id})", flush=True)
        deadline = time.time() + PER_TASK_BUDGET_S
        res = None
        last_status = None
        while time.time() < deadline:
            try:
                res = client.get_task(task_id=task_id)
            except Exception as exc:
                print(f"  ! get_task raised: {exc!r}; retrying", flush=True)
                time.sleep(POLL_INTERVAL_S)
                continue
            status = (getattr(res, "status", "") or "").lower()
            if status != last_status:
                print(f"  - status={status}", flush=True)
                last_status = status
            if status in TERMINAL:
                break
            time.sleep(POLL_INTERVAL_S)
        if res is None:
            print(f"  ! never got a response for {task_id}", flush=True)
        results.append(res)

    print(f"[fetch] got {len(results)} result objects", flush=True)
    for q, res in zip(submitted, results):
        if res is None:
            print(f"  - {q['slug']}: skipped (no response)", flush=True)
            continue
        slug = q["slug"]
        task_id = getattr(res, "task_id", None) or q["task_id"]
        status = getattr(res, "status", None) or "unknown"
        formatted = getattr(res, "formatted_answer", None) or ""
        md_path = OUT_DIR / f"{slug}-{task_id}.md"
        json_path = OUT_DIR / f"{slug}-{task_id}.json"

        header = (
            f"# Edison LITERATURE_HIGH — {q['headline']}\n\n"
            f"- task_id: `{task_id}`\n"
            f"- slug: `{slug}` (data source {slug.split('-')[0]} of 5)\n"
            f"- job: `LITERATURE_HIGH`\n"
            f"- status: `{status}`\n"
            f"- fetched_at: `{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}`\n"
            f"- source issue: vertical-cloud-lab/tensegrity-optimization#51 "
            f"(parent #36 comment 4509305026)\n\n"
            f"---\n\n"
        )
        md_path.write_text(header + (formatted or "(empty formatted_answer)\n"))

        try:
            dumped = res.model_dump_json(indent=2)  # pydantic v2
        except Exception:
            try:
                dumped = json.dumps(res.model_dump(), indent=2, default=str)
            except Exception:
                dumped = json.dumps({"task_id": task_id, "status": status}, indent=2)
        json_path.write_text(dumped + "\n")

        # Remove SUBMITTED placeholder now that we have the real artifacts.
        placeholder = OUT_DIR / f"{slug}-SUBMITTED.json"
        if placeholder.exists():
            placeholder.unlink()
        print(f"  - wrote {md_path.name} + {json_path.name}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
