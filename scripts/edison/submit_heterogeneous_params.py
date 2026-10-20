"""Submit + fetch one Edison LITERATURE_HIGH query — per-member (heterogeneous) BO parameters.

Context: PR #24 comment 4520542433 (sgbaird relaying @me-madsen):

    "noting that we could also allow for diameters of individual
    struts/cables to vary, rather than assuming a fixed diameter.
    Similar for other parameters perhaps. Mostly thinking in context
    of #35 right now"

PR #35 currently sweeps a *single* ``strut_d_mm`` and a single
``cable_d_mm`` per T3-prism specimen (i.e. all 3 struts share one diameter
and all 9 cables share one diameter). The proposal here is to expose
per-member diameters (and possibly per-member length, prestress, twist,
material, etc.) as independent BO axes, taking the dimensionality of the
search space from O(5) per specimen to O(N_members) per specimen for a
T3-prism (3 struts, 9 cables = 12 members → ~12 diameter axes alone).

This script asks Edison for a peer-reviewed literature synthesis on:
(i) when and why peer-reviewed tensegrity / lattice / truss work allows
heterogeneous (per-member) parameters, (ii) what the manufacturing /
mechanical / form-finding / prestress-feasibility consequences are, and
(iii) how high-dimensional BO campaigns over per-member design vectors
have been structured in published work (random embeddings, sparse / SAAS
GPs, additive / decomposition kernels, latent / generative parameterizations,
trust-region / TuRBO, symmetry / permutation-invariance priors, hierarchical
search spaces a la Ax #140, etc.).

Per repo convention:

* edison-client reads ``EDISON_PLATFORM_API_KEY``; we mirror the documented
  ``EDISON_API_KEY`` into that variable so the script runs unmodified in CI.
* Submit non-blocking (``create_task``), then poll ``get_task`` until terminal.
  ``run_tasks_until_done()`` rebuilds + resubmits TaskRequests rather than
  fetching by task_id, so we cannot reuse it here.
* Commit verbatim under
  ``edison-trajectories/heterogeneous-params/heterogeneous-params-<task_id>.{md,json}``.
* If the task is still in progress when the wall-clock budget expires, a
  ``-SUBMITTED.json`` placeholder records the task_id so a follow-up session
  can resume with ``client.get_task``.
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
OUT_DIR = REPO_ROOT / "edison-trajectories" / "heterogeneous-params"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SLUG = "heterogeneous-params"
HEADLINE = (
    "Per-member (heterogeneous) design parameters in tensegrity / lattice BO "
    "campaigns — when to vary strut and cable diameters independently, and "
    "how to keep the resulting high-dimensional search space tractable"
)

QUERY = f"""\
{HEADLINE}.

Project context (read in full before answering):

* Hardware: multi-material 3D-printed tensegrity-inspired energy absorber.
  Strut material PETG (or PLA in the current PR #35 batch), tendon material
  TPU 85A (NinjaFlex-class, E ~12 MPa secant, sigma_break ~26 MPa, rho
  ~1200 kg/m^3, strain-at-break ~550-660%). Printed on a Bambu H2D
  dual-extrusion FFF system with manual-painted supports. Baseline topology
  is a T3-prism (3 struts, 9 cables = 3 saddle + 3 top + 3 bottom). Stretch
  goals: 6-bar SUPERball icosahedron, stacked / tiled prisms, Pajunen
  truncated-octa.
* Existing BO setup (PR #30 + PR #33 + PR #35): an Ax / BoTorch qNEHVI
  multi-objective campaign. PR #35 specifically — `bo/t3_prism_sobol_batch.py`
  — currently sweeps FIVE T3-prism design variables as a single Sobol batch
  of 9 specimens on the H2D plate:
    - `R_mm` (cell radius)
    - `H_mm` (cell height)
    - `twist_deg` (rotation between top and bottom triangles)
    - `strut_d_mm`  (ONE diameter — applies to all 3 struts)
    - `cable_d_mm`  (ONE diameter — applies to all 9 cables)
  Frozen: topology=t3_prism, tiling=1x1x1, joint geometry (captive TPU core
  inside hollow PLA shell), build_orientation=vertical, tpu_shore=85A.
* Proposal under discussion (PR #24 comment 4520542433): allow the diameter
  of every individual strut and every individual cable to vary independently
  (so a T3-prism specimen would have ~3 strut-diameter axes + 9 cable-
  diameter axes = 12 diameter axes, instead of 2). The user also asks
  "similar for other parameters perhaps" — i.e. per-member length,
  per-cable prestress, per-member material assignment, per-cable shore,
  per-strut layer-height, etc.
* Companion PR #24 design-space docs already encode a hierarchical
  `topology_family` -> conditional child parameters search space (per
  facebook/Ax#140). The per-member proposal sits one level below that —
  inside any chosen topology family, expand selected scalar parameters into
  vector / per-member parameters.

Answer EVERY sub-question below with primary, peer-reviewed citations
(DOIs where available). When recommending a numeric value or a default
choice, justify from a cited source rather than rule-of-thumb. Do not
fabricate DOIs.

(a) MOTIVATION / LITERATURE PRECEDENT. In peer-reviewed tensegrity, cable
    dome, deployable space-structure, lattice-metamaterial, and ground-
    structure topology optimization work, when have authors deliberately
    allowed individual struts and individual cables to have heterogeneous
    (per-member) cross-section, length, prestress, or material — vs.
    enforcing a uniform value across the cell? Identify the canonical
    references (e.g. Skelton & de Oliveira 2009 minimal-mass tensegrity
    sizing; Masic, Skelton & Gill 2006 form-finding with member-wise force
    densities; Adam & Smith active-tensegrity bridges; Pellegrino &
    Calladine self-stress; Tibert & Pellegrino reviews; Achtziger /
    Bendsoe / Sigmund ground-structure topology optimization; Zegard &
    Paulino GRAND/Polytop; Hanaor double-layer grids; Goyal & Skelton
    minimum-mass tensegrity dynamics; Bel Hadj Ali, Rhode-Barbarigos,
    Smith active control; Wang, Senatore, Marano 2021+ optimal tensegrity
    sizing under impact; Veuve, Safaei, Smith deployable tensegrity).
    For each, summarise: what was varied per-member, what objective was
    optimized, what variation actually emerged at the optimum (i.e. do
    the per-member sizes converge to a few discrete clusters, or do they
    populate a continuum?), and how the heterogeneity compared
    quantitatively against a uniform-member baseline.

(b) MECHANICAL / FORM-FINDING IMPLICATIONS. For a class-1 prismatic
    tensegrity (T3-prism, T4-prism), what is the literature on the
    feasibility envelope of heterogeneous member properties?
    Specifically:
      - Form-finding & self-stress: does varying individual cable
        cross-sections break the symmetric self-stress state, force an
        unsymmetric prestress distribution, or shift the cell's
        equilibrium geometry (R, H, twist)? Cite force-density-method
        and dynamic-relaxation references.
      - Buckling: per-strut diameter governs Euler buckling at known
        slenderness; what is the published trade-off between SEA and
        peak-force when individual struts are deliberately under-sized
        to act as sacrificial buckling fuses?
      - Bistability / multistability (Schenk & Guest 2014; Defossez 2003;
        Sumi & Miyashita): does per-member heterogeneity unlock bistable
        modes not accessible to uniform cells?
      - Anisotropy: how much directional stiffness / energy-absorption
        tailoring can be achieved by per-cable cross-section selection
        in a single T-prism vs. by going to multi-cell tilings?
      - Cycle life / fatigue: per-tendon shore / cross-section
        heterogeneity in TPU-tendon tensegrities — any reuse-count
        data?
    Cite numbers (peak-force reduction %, SEA gain %, prestress shift
    in % of uniform self-stress) where available.

(c) MANUFACTURABILITY ON FFF MULTI-MATERIAL FDM (BAMBU H2D / IDEX).
    The lab prints PETG struts + TPU 85A cables in a single multi-
    material job. Per the PR #35 captive-TPU-core-inside-PLA-shell
    joint design, every joint shell has a uniform bore size set by
    the (currently single) cable diameter. If individual cables get
    independent diameters, what manufacturability gotchas appear?
    Specifically:
      - Bore tolerance: how many distinct cable diameters can a single
        joint sphere accommodate before the PLA shell becomes
        impractically thick (cable_d + 0.8 mm bore clearance, then
        +3 mm core, then +3.2 mm PLA wall)?
      - TPU bridging: can a 1.5 mm cable transition mid-print into a
        4.5 mm cable on the same TPU extruder pass, or does the
        extruder retraction / line-width mismatch force a layer
        boundary at the transition?
      - Strut diameter discretization: PETG FFF practical strut
        diameters quantize on the 0.4 mm nozzle line-width. Cite
        published recommendations (Khatri 2024; Yavas 2022; Lopes
        2018; Ye 2023; Bambu Lab / Prusa application notes) for
        discrete-set vs. continuous treatment.
      - Print time: how does the H2D wipe-tower volume scale with
        N_distinct_filament_diameters?
      - Variability noise: if the BO can request 12 different cable
        diameters per specimen but FFF reliably resolves only 3-4
        bins, the additional "axes" are noise. Cite repeatability /
        CoV numbers (Khatri 2024; Yavas 2022 PLA+TPU FFF tensile;
        Intrigila 2022; Davami 2025 SLA Tough 2000 + double-T3).

(d) HIGH-DIMENSIONAL BO METHODOLOGY. Once the per-member expansion is
    taken, the design vector becomes O(10) to O(30) dimensional for a
    single T3-prism cell, and O(100+) for a 3x3x2 tiling. Survey peer-
    reviewed and well-cited workshop / preprint methodology for high-
    dim BO over structured design vectors. Cover at minimum:
      - Random embeddings (REMBO — Wang et al. 2016; BOCK; ALEBO —
        Letham et al. 2020).
      - Sparse / SAASBO (Eriksson & Jankowiak 2021) — strong fit
        for "most members do not matter, a few do" sparse-effect
        regimes. Recommend specific Ax / BoTorch hooks.
      - Additive / decomposed GPs (Kandasamy 2015; Gardner 2017;
        Wang & Jegelka 2018) — natural fit when per-member effects
        are largely independent.
      - Trust-region BO (TuRBO — Eriksson 2019) and SCBO — strong
        empirical performance in O(100+) dims, especially on
        physically-constrained problems.
      - Hierarchical / conditional search spaces (Ax HierarchicalSearch
        Space, facebook/Ax#140; SMAC; Auto-WEKA; HyperBand) — the
        natural way to nest per-member parameters under a topology
        choice.
      - Latent / generative parameterizations (VAE-BO; LSO — Tripp 2020;
        Maus et al. 2022 LOL-BO; differentiable-CAD or differentiable
        physics priors). Particularly relevant when there are physically
        meaningful symmetries (the 3-fold T-prism is permutation-
        invariant; the 9 cables decompose into 3 saddle + 3 top + 3
        bottom orbits — encode that symmetry explicitly).
      - Symmetry-aware / permutation-invariant kernels (Cohen & Welling;
        Bronstein et al. geometric deep learning; cited in
        Bayesian-optimization-with-symmetry preprints if any).
      - Multi-fidelity / multi-task GPs (PR #33 sim ladder maps
        cleanly onto MTGP / MF-GP — Kandasamy 2017; Wu 2020; Astudillo &
        Frazier 2021) as a way to amortize the high-dim cost.
      - Constraint handling: heterogeneity often introduces feasibility
        constraints (TPU bore set must be ≤4, strut slenderness L/D ≤
        some max, mass ≤ 500 g). Cite NEI / SCBO / cNEHVI.
    For each method, recommend whether to adopt it as the primary BO
    engine for PR #35, as a fallback if dimensionality blows up, or as
    a wrong-fit. Give a concrete recommended progression starting from
    the current 5-D Sobol → next-step BO step.

(e) SYMMETRY EXPLOITATION. The T3-prism has a natural C3 rotational
    symmetry (rotate by 120 deg). All 3 struts are in one orbit; the 9
    cables decompose into 3 orbits of 3 (saddle, top, bottom triangles).
    Under that symmetry, the "12 diameter axes" reduce to 4 orbit
    diameters (1 strut orbit + 3 cable orbits). What does the literature
    say about exploiting this symmetry in BO, in form-finding, and in
    optimal-control of tensegrity? Cite Sultan & Skelton symmetry-
    decomposed self-stress; group-theoretic stability (Kangwai & Guest);
    invariant / equivariant GPs (van der Wilk 2018; Holderrieth, Hutchinson
    & Teh 2021). Recommend whether to (i) hard-enforce orbit symmetry as
    the default search space (so the BO never sees a symmetry-broken
    design), (ii) use orbit symmetry only as a kernel prior so symmetry
    breaking can emerge when warranted, or (iii) ignore symmetry and
    let the per-member axes float independently. Justify quantitatively
    in terms of expected sample efficiency given the lab's 50-100
    specimen budget.

(f) NUMERIC RECOMMENDATIONS for the lab's next BO batch (PR #35 follow-on).
    For a single T3-prism cell on the H2D, recommend:
      - Which scalar parameters to keep scalar (R, H, twist, infill %).
      - Which scalar parameters to expand to per-orbit (strut diameter,
        cable diameter — recommend per-orbit, not per-member, for the
        first heterogeneous batch).
      - Which scalar parameters to expand to fully per-member
        (per-cable prestress fraction is the strongest candidate —
        cite Skelton's minimum-mass prestress optimization).
      - Recommended bounds and discretization for each new axis
        (e.g. strut_orbit_d_mm ∈ [3.5, 9.0] continuous; cable_orbit_d_mm
        ∈ {1.2, 1.8, 2.4, 3.0, 4.5} categorical for FFF resolvability;
        per-cable prestress fraction simplex with sum = 1).
      - Recommended BO engine + acquisition + batch size for the
        50-100 specimen total budget. Give a specific Ax / BoTorch
        configuration recipe (model_class, surrogate_spec,
        acquisition_function_class, batch_size, n_init_sobol).
      - Recommended sample-efficiency analytic: how many specimens does
        SAASBO / TuRBO / orbit-symmetric GP each need on a published
        problem of comparable dimension to reach within 10% of the
        Pareto-front hypervolume? Cite the benchmark.

(g) FAILURE MODES AND OPEN QUESTIONS. Top 5-10 ranked gotchas /
    pitfalls of adopting per-member heterogeneous BO axes for the
    lab's PETG + TPU 85A tensegrity-on-H2D context. For each: cite
    the failure mode from peer-reviewed work and propose a mitigation.

(h) NUMBERED REFERENCES section (DOI when available) supporting every
    quantitative claim in (a)-(g).

Cite only primary, peer-reviewed sources or established standards
(ASTM, ISO, JEDEC, NASA / NIST technical reports, well-cited workshop
papers at NeurIPS / ICML / AISTATS). Do NOT fabricate DOIs.
"""


def main() -> int:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )

    placeholder = OUT_DIR / f"{SLUG}-SUBMITTED.json"
    if placeholder.exists():
        existing = json.loads(placeholder.read_text())
        task_id = existing.get("task_id")
        print(f"[submit] reusing prior task_id={task_id}", flush=True)
    else:
        task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}
        print("[submit] creating LITERATURE_HIGH task...", flush=True)
        resp = client.create_task(task)
        # create_task returns trajectory_id as plain string (per repo memory)
        task_id = resp if isinstance(resp, str) else (
            getattr(resp, "task_id", None)
            or getattr(resp, "trajectory_id", None)
            or str(resp)
        )
        print(f"[submit] task_id={task_id}", flush=True)
        placeholder.write_text(
            json.dumps(
                {
                    "slug": SLUG,
                    "headline": HEADLINE,
                    "task_id": task_id,
                    "job": "LITERATURE_HIGH",
                    "status": "submitted",
                    "submitted_at": time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                    ),
                    "source_pr_comment": (
                        "https://github.com/vertical-cloud-lab/"
                        "tensegrity-optimization/pull/24#issuecomment-4520542433"
                    ),
                },
                indent=2,
            )
            + "\n"
        )

    # Poll with get_task(task_id) until terminal.
    TERMINAL = {"success", "failed", "cancelled", "error", "crashed"}
    POLL_INTERVAL_S = 30
    BUDGET_S = 60 * 60  # 60 min budget for a single LITERATURE_HIGH task

    print(f"[fetch] polling {task_id}", flush=True)
    deadline = time.time() + BUDGET_S
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
        print(f"[fetch] no response within budget for {task_id}", flush=True)
        return 0

    status = getattr(res, "status", None) or "unknown"
    formatted = getattr(res, "formatted_answer", None) or ""
    md_path = OUT_DIR / f"{SLUG}-{task_id}.md"
    json_path = OUT_DIR / f"{SLUG}-{task_id}.json"

    header = (
        f"# Edison LITERATURE_HIGH — {HEADLINE}\n\n"
        f"- task_id: `{task_id}`\n"
        f"- slug: `{SLUG}`\n"
        f"- job: `LITERATURE_HIGH`\n"
        f"- status: `{status}`\n"
        f"- fetched_at: `{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}`\n"
        f"- source PR comment: "
        f"https://github.com/vertical-cloud-lab/tensegrity-optimization/"
        f"pull/24#issuecomment-4520542433\n\n"
        f"---\n\n"
    )
    md_path.write_text(header + (formatted or "(empty formatted_answer)\n"))

    try:
        dumped = res.model_dump_json(indent=2)
    except Exception:
        try:
            dumped = json.dumps(res.model_dump(), indent=2, default=str)
        except Exception:
            dumped = json.dumps({"task_id": task_id, "status": status}, indent=2)
    json_path.write_text(dumped + "\n")

    if placeholder.exists() and status in TERMINAL:
        placeholder.unlink()
    print(f"[fetch] wrote {md_path.name} + {json_path.name} (status={status})",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
