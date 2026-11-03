# Target audience: candidate reviewers, editors, and reviewer-profile diversity

> **Issue:** "Who is the target audience?" -- *Who should we suggest as potential
> reviewers? Which editors are most likely to be overseeing our submission? See
> #20 and all other PRs.*
>
> **Primary venue:** ASME Journal of Mechanical Design (JMD).
> **Backup venue:** Smart Materials and Structures (SMS, IOP).
> See `manuscript/README.md` (PR #20) for the venue selection rationale.

This document has two parts:

1. **Reviewer-profile diversity expected at JMD/SMS** for a cross-disciplinary
   *Bayesian optimization + multi-material additive manufacturing + tensegrity
   metamaterials + assistive devices* manuscript -- with the rough mix of
   reviewer subfields the editor will assemble, and the implication for which
   sections of the paper need to land for which reader.
2. **A candidate reviewer pool**, anchored in a dedicated Edison
   `LITERATURE_HIGH` query (task `9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`,
   committed at `edison-trajectories/2026-05-09-target-audience-9cc7db18.md`
   + `.json`) that asked Edison to (i) name current JMD Associate Editors by
   coverage area, (ii) propose 10-15 specific candidate reviewers with
   representative JMD-relevant papers and DOIs, (iii) flag obvious COIs for a
   BYU-affiliated team, and (iv) repeat for SMS as the backup venue. Every
   recommendation in §3 is anchored to at least one paper in JMD, a sister
   ASME journal, or a directly comparable domain-leading peer-reviewed venue
   (Composite Structures, *Adv. Mater.*, *Sci. Adv.*, *Addit. Manuf.*,
   *Extreme Mech. Lett.*, *npj Comput. Mater.*, *Struct. Multidiscip. Optim.*,
   *J. Eng. Mech.*).

## 1. Why this question matters for our PR #20 manuscript

PR #20 stands up an `asmejour`-class IMRaD scaffold targeting **JMD as the
primary venue** with **SMS as a backup**. The scope is intentionally
cross-disciplinary:

- **Methods:** multi-fidelity Bayesian optimization (BoTorch / Ax-style GP
  surrogates, qNEHVI, multi-objective stiffness vs. specific-energy-absorbed
  trade-offs).
- **Manufacturing:** PETG struts + TPU 95A tendons on a Bambu Lab H2D IDEX
  printer (per the lab's hardware standard -- see the repo's hardware memory).
- **Mechanics:** tensegrity / tensegrity-like unit cells; quasi-static
  compression and drop-tower / single-point LDV impact testing
  (Lansmont M23 + Polytec QTec, see issue #28).
- **Application motivation:** shock-absorbing crutch tips and assistive
  devices (PR #18 prior-art trajectories).

That breadth is **exactly the failure mode JMD reviewers complain about most
often** for this kind of paper: "interesting, but who is it for?" A clean
reading of which reviewer subfields the AE will recruit -- and which
journal-aligned candidate names the editor can actually pick -- gives the
co-authors a checklist for what each section of the manuscript must explicitly
do for each reader.

## 2. Reviewer-profile diversity expected at JMD (and SMS)

**JMD typically assigns 2-3 reviewers per manuscript**, and for a paper that
spans BO + AM + architected materials + an assistive-device motivation, the AE
has incentive to pick **at least one reviewer from each of the four sub-camps
below**. Our manuscript needs to anticipate all four.

| Reviewer profile | What they will look for first | Likely concerns to pre-empt |
|---|---|---|
| **(A) Design optimization & data-driven design** -- BO/GP/multi-objective, design-of-experiments, surrogate modeling. Most likely to be the AE handler at JMD. | Acquisition function choice and justification (qNEHVI, qEHVI, qLogNEI), kernel/likelihood choices, how the multi-fidelity coupling between sim and experiment is formulated, batch sizing, baseline against random / LHS / one-shot DoE, calibration of GP uncertainties against held-out experimental data. | "BO is just a wrapper here -- where is the methodological contribution beyond applying off-the-shelf BoTorch?" Address by foregrounding the *multi-fidelity* coupling and the experimental-loop closure. |
| **(B) Mechanism design / compliant & architected mechanisms / metamaterials** -- people who publish on origami, lattices, tensegrity, mechanical metamaterials. | Topology rationale: why tensegrity vs. octet/honeycomb/auxetic? Class-1 vs. tensegrity-like distinction, prestress, stability under load, scaling laws, comparison to known impact-absorbing lattice families. | "Tensegrity-like" structures where struts contact the floor and bypass the tendons (see the repo's tensegrity-simulator memory) will draw fire. Be explicit about Class-1 vs. tensegrity-like and report both. |
| **(C) Additive manufacturing / DfAM / multi-material printing** -- materials and process side. | Print process window (H2D IDEX, 0.4 mm nozzle, 3-perimeter rule), interface bonding between PETG and TPU, repeatability across builds, characterization of as-printed vs. nominal geometry, fatigue/aging if cyclic loading is implied. | "Specimen-to-specimen variability swamps the BO signal." Need to report fabrication uncertainty and, ideally, fold it into the BO noise model. |
| **(D) Biomechanics / rehabilitation / assistive devices** -- usually the smallest slice at JMD but the AE will recruit one if the application motivation (crutch tips) is foregrounded; this is the *core* readership at SMS only if we frame around smart/responsive structures. | Realism of loading conditions vs. clinical use (vertical impact only? lateral? off-axis?), HAVS / vibration transmission (see PR #18 trajectory 03), fall risk / abandonment data (also trajectory 03), comparison to commercial crutch tips. | If the manuscript over-promises clinical impact from unit-cell tests, this reviewer will recommend rejection on impact-claim grounds. PR #20's mock review already flagged exactly this (`reviews/mock_reviews.md`, "Impact claims are overstated"). Pre-empt by framing as bench-level prior-art benchmarking, not a clinical study. |

**JMD vs. SMS profile mix** (rough expectation):

- **JMD** review panels skew (A)+(B), with one (C) usually present and (D)
  occasional. The AE handler is almost always from (A) or (B). Most common
  major-revision reasons for cross-disciplinary BO/AM/metamaterials papers at
  JMD: insufficient design-theoretic novelty beyond off-the-shelf BO; weak
  manufacturing-uncertainty quantification; over-broad application claims.
- **SMS** review panels skew (B)+(C) with the framing pivoted toward
  *smart/responsive* materials. A pure BO methods reviewer is less likely; an
  experimental smart-materials reviewer more likely. Most common concerns:
  "where is the smart/active behavior?" -- which is exactly why SMS is our
  *backup* venue, not primary, and the manuscript needs a different framing
  paragraph if we retarget.

## 3. Candidate reviewer pool

> **All candidates below are grounded in the Edison `LITERATURE_HIGH`
> trajectory `edison-trajectories/2026-05-09-target-audience-9cc7db18.md`
> (task `9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`, fetched 2026-05-09), with each
> recommendation anchored to at least one paper in JMD or a directly relevant
> domain-leading peer-reviewed journal (Composite Structures, Advanced
> Materials, Science Advances, Additive Manufacturing, Extreme Mechanics
> Letters, npj Computational Materials, Structural and Multidisciplinary
> Optimization, Journal of Engineering Mechanics, Journal of Applied
> Mechanics, Journal of Mechanisms and Robotics).** That trajectory's full
> question, answer, and 25-entry numbered reference list (with DOIs and
> citation counts) is committed alongside this file. The matched `.json`
> (`model_dump_json`) artifact is committed in the same directory for full
> structured reproducibility, per the repo's Edison-trajectory convention.

### 3a. Likely JMD Associate Editor coverage

The Edison trajectory identifies these AE-coverage areas and likely AEs /
JMD-active researchers (current AE rosters should be confirmed on the live
ASME JMD editorial-board page before submission, since Edison flagged that it
could not independently verify the 2025-2026 board roster from publications
alone):

| AE-coverage area                                  | Likely AE / key JMD-active researcher        | Representative JMD paper(s) |
|---|---|---|
| Design optimization & data-driven design          | **Wei Chen** (Northwestern)                  | Wang, Yerramilli, Iyer, Apley, Zhu, Chen, *J. Mech. Des.* (2022) — scalable GPs for data-driven design with categorical factors; Lee, Chen, Wang, Chan, Chen, *Adv. Mater.* review (2024) on data-driven design for metamaterials |
| Bayesian optimization in JMD                      | **Christopher Hoyle** (Oregon State)         | Biswas & Hoyle, *J. Mech. Des.* (2021); Jetton, Campbell, Hoyle, *J. Mech. Des.* (2024) on feasibility-aware constrained BO |
| Multi-fidelity surrogates                         | **Pingfeng Wang** (UIUC)                     | Xu, Wu, Liu, Wang, Li, *J. Mech. Des.* (2024) on multi-fidelity multi-task learning |
| Generative / AI-assisted design                   | **Faez Ahmed** (MIT)                         | Chan, Ahmed, Wang, Chen, "METASET," *J. Mech. Des.* (2021); Regenwetter, Nobari, Ahmed, *J. Mech. Des.* (2022) |
| Design automation & multi-objective optimization  | **James T. Allison** (UIUC)                  | Peddada, Allison et al., *J. Mech. Des.* (2023) — co-design |
| Compliant / origami / metamaterial mechanisms     | **Larry Howell** (BYU) / **Pooya Sareh**     | Brown, Ynchausti, Lytle, Howell, Magleby, *J. Mech. Des.* (2022); Chen et al., Sareh, *J. Mech. Des.* (2023) — *Howell is a clear COI for a BYU team* |
| Additive manufacturing / DfAM                     | **David Rosen** (formerly Georgia Tech) / **Levent B. Kara** (CMU) | Liang et al., *J. Mech. Des.* (2023); Wang, Rosen et al., *J. Mech. Des.* (2023) on generative design embedding topology optimization |

### 3b. Recommended candidate reviewers (14 named, journal-grounded)

These 14 candidates are the Edison-returned recommendation set, every one of
them anchored to a paper in a JMD-relevant peer-reviewed journal (no
NeurIPS/ICML-only software contributors). Group by subtopic when populating
the manuscript "Suggested Reviewers" field; the trajectory recommends 4-6
names with at least 2 from the design-optimization community and 2 from the
tensegrity / architected-materials community.

#### Tensegrity mechanics & architected metamaterials

| Reviewer                       | Affiliation                              | Representative paper(s) (venue, year)                                                                                              |
|---|---|---|
| **Julian J. Rimoli**           | Georgia Tech                             | Bauer, Kraus, Crook, Rimoli, Valdevit, *Adv. Mater.* (2021); Zhang, Ohsaki, Rimoli, Kogiso, *Compos. Struct.* (2021)                |
| **Lorenzo Valdevit**           | UC Irvine                                | Bauer et al., *Adv. Mater.* (2021); Bauer, Sala-Casanovas, Amiri, Valdevit, *Sci. Adv.* (2022)                                      |
| **Fernando Fraternali**        | Università di Salerno                    | Micheletti, Intrigila, Nodargi, Artioli, Fraternali, Bisegna (COMPDYN, 2021); de Castro Motta, Fraternali, Saccomandi, *Meccanica* (2025) |
| **Kirsti Pajunen**             | formerly Caltech (Daraio group)          | Pajunen, Celli, Daraio, *Extreme Mech. Lett.* (2021) — prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattices |
| **Filipe A. Santos**           | Universidade NOVA de Lisboa              | Santos, *Adv. Mater.* (2023) — tensegrity energy-dissipation metamaterial with 3D-printed prototypes                              |
| **Andrea Micheletti**          | Università di Roma Tor Vergata           | Intrigila, Micheletti et al., *Addit. Manuf.* (2022) — bistable tensegrity-like unit fabrication & test                            |
| **Edwin A. Peraza Hernandez**  | UCF (formerly Texas A&M)                 | Pham & Peraza Hernandez, *J. Mech. & Robotics* (2021); Goyal, Peraza Hernandez, Skelton, *J. Appl. Mech.* (2020)                    |

#### Bayesian / multi-objective optimization for materials & structures (journal-publishing, *not* BoTorch/Ax tooling)

| Reviewer                       | Affiliation                              | Representative paper(s) (venue, year)                                                                                              |
|---|---|---|
| **Liwei Wang**                 | U. Michigan (formerly Northwestern)      | Wang et al., *J. Mech. Des.* (2022) — scalable GPs with categorical factors; Wang et al., *PNAS* (2022)                            |
| **Zacharias Vangelatos**       | UC Berkeley (Grigoropoulos group)        | Vangelatos et al., *Sci. Adv.* (2021) — Bayesian optimization of architected materials achieving 12,464× SED gain                   |
| **Haris Moazam Sheikh**        | UC Berkeley                              | Sheikh & Marcus, *Struct. Multidiscip. Optim.* (2022) — MixMOBO, mixed-variable multi-objective BO for architected materials       |
| **Chengyang Mo**               | U. Pennsylvania (Raney group)            | Mo, Perdikaris, Raney, *J. Eng. Mech.* (2023) — multi-fidelity BO for architected-material design                                  |
| **Danial Khatamsaz**           | Texas A&M                                | Khatamsaz et al., *npj Comput. Mater.* (2023) — constrained multi-objective BO for materials design                                |
| **Faez Ahmed**                 | MIT                                      | Chan, Ahmed, Wang, Chen, *J. Mech. Des.* (2021); Regenwetter, Nobari, Ahmed, *J. Mech. Des.* (2022)                                 |

#### Impact / energy-absorption design optimization for AM lattices

| Reviewer                       | Affiliation                              | Representative paper(s) (venue, year)                                                                                              |
|---|---|---|
| **Nathan Hertlein**            | (affiliation per Edison trajectory; verify before submission) | Hertlein, Vemaganti, Anand, *J. Mech. Des.* (2024) — design optimization of lattice structures under impact loading for AM         |

### 3c. Conflict-of-interest screen (BYU Mechanical Engineering)

Per the Edison trajectory, no direct BYU co-authorship signal was found for
any of the 14 named candidates above. Apply the standard ASME COI window
(co-author / advisor / advisee / shared-grant collaborator within the last
4 years) before submitting the suggested-reviewer list. **Hard exclusions
known so far:**

- **Larry L. Howell (BYU)** — same institution; do *not* suggest.
- **Brian Jensen (BYU)** — same institution; do *not* suggest.

### 3d′. "Lander"-style designs / drag-free impact survival (egg-drop demo, PR #47)

Source: Edison `LITERATURE_HIGH` trajectories committed on branch
`copilot/explore-egg-drop-idea` (PR #47): `egg-drop-tensegrity-1b90208d.md`
(task `1b90208d-3555-4479-9db0-512d67e69f5f`) and the drag-free /
V·m-benchmark follow-up `egg-drop-followup-f41b7034.md` (task
`f41b7034-439e-45de-b97f-4bf1d85b9811`). These two trajectories surfaced a
specific cluster of researchers who have actually published peer-reviewed
*lander*- or *drag-free-drop*-flavored tensegrity work — distinct from the
crutch-tip / quasi-static SEA cluster in §3b. **Best contacts to reach out to
about lander-style designs and studies, ranked by directness of fit:**

| Rank | Contact | Affiliation | Why they're the right person for "lander"-style outreach |
|---|---|---|---|
| 1 | **Julian J. Rimoli** | Georgia Tech | *On the impact tolerance of tensegrity-based planetary landers* (AIAA SciTech, 2016) — the canonical peer-reviewed virtual-drop study of a tensegrity lander. Also senior author on Bauer 2021 *Adv. Mater.* tensegrity-metamaterial paper and Pajunen 2019 *Mater. & Des.* impact-response paper. *Single best person to contact.* |
| 2 | **Adrian K. Agogino** | NASA Ames Research Center | NIAC SUPERball Phase 2 final report (2018) — the only published egg-payload tensegrity drop with quantitative deceleration data (~10 m, <25 G simulated at 15 m/s). Direct egg-drop heritage. |
| 3 | **Vytas SunSpiral** | formerly NASA Ames; now Stoke Space / RGo Robotics | NIAC SUPERball PI; co-author on Agogino 2018 and SunSpiral 2015 NIAC reports. Most lineage-aware contact for the SUPERball-class architecture our demo inherits from. |
| 4 | **Mark W. Mueller** | UC Berkeley HiPeRLab | Zha, Wu, Dimick, Mueller, *IEEE/ASME Trans. Mechatronics* (2024) and Zha et al., IROS (2020) — collision-resilient icosahedron tensegrity aerial vehicle; the most recent peer-reviewed hardware/control work on tensegrity impact survival. |
| 5 | **Andrew (AS) Zhang** + **Brian Cera** | UC Berkeley (Agogino group, lineage) | Zhang, *Design of Impact-Resistant Tensegrity Landers* (UC Berkeley dissertation, 2022) — best instrumented public dataset (10 m / 11.8 m/s / 155 g; 20 m / 14.3 m/s / 235 g; ~20 reusable drops). Cera + Zhang + Agogino, *Characterization of six-bar spherical tensegrity lattice topologies* (2018). |
| 6 | **Massimo Vespignani** | formerly NASA Ames | Vespignani et al., *Design of SUPERball v2* (2018) — fully actuated 2 m / 36 kg six-bar with cable-stiffness sweep; useful for the "what cable stiffness do we pick?" framing of our BO loop. |
| 7 | **Robert E. Skelton** / **Cornel Sultan** | TAMU / Virginia Tech | Class-1 tensegrity lander concepts, foundational form-finding theory. Best contact if outreach is framed as theory/rigidity rather than hardware. |
| 8 | **Jamshid Bayandor** | Virginia Tech (CRASH Lab) | TANDEM tensegrity-lander simulation (2017): 180–260 kg payloads, 1 m diameter, 10–30 m/s, 35–224 g peak. Best contact for *scaled-up* lander work. |
| 9 | **Jing Zhang** *(et al., Harbin Institute of Technology)* | HIT | *Design and cushioning performance analysis of spherical tensegrity structures*, *Aerospace* (2025) — class-II spherical tensegrity with centrally suspended egg payload, drops to 5 m, failure at 6 m. Most recent peer-reviewed egg-payload drop analog. |
| 10 | **Madhumati Anand** | affiliation not in trajectory; verify via arXiv 2212.11625 (2022) | Biodegradable tensegrity (wicker/bamboo + jute + coir) protecting fragile medical payloads in 25–75 m drops onto pavement — single-use, holds the highest published drag-free survival height for a fragile payload. Best contact for the *biodegradable / single-use* framing. |

**Suggested first-contact set (3 names):** Rimoli (peer-reviewed
lander-mechanics anchor), Agogino (direct egg-drop SUPERball heritage),
Mueller (newest collision-resilient hardware). Rimoli already appears in §3b
as a JMD candidate reviewer — for the egg-drop / lander demo, the framing
should foreground his AIAA 2016 lander paper and Pajunen 2019 *Mater. & Des.*
impact paper rather than the Bauer 2021 metamaterial work.

**Implication for the manuscript:** none of these names overlaps with the
crutch-tip / assistive-device cluster, and only Rimoli + Pajunen are
shared with the JMD / SMS pools above. If the demo gets folded into the
manuscript as a secondary case study, expect the AE to add a *space-systems
or aerospace-mechanisms* reviewer drawn from this list (most plausibly Rimoli
or Mueller via the IEEE/ASME T-Mech route).

### 3d″. First-contact talking points (draft sentences for outreach emails)

Drafted in response to PR comment 4427252364: "what aspects would be best
to seek feedback/help about? Consider all PRs in this repo. For example,
tech transfer, what some of the real-world challenges are, any immediate
'gotchas' that come to mind. Draft just a couple sentences each. ... Is
there also some way they could contribute collaboratively that comes to
mind? For example, external validation."

**Throwaway sentences only — expect to rewrite per recipient.** A
companion Edison `LITERATURE_HIGH` query (task
`f18aca01-00bb-4ca7-a8e9-f6312dfaaff7`, fetched 2026-05-12, ~50 KB) was
run alongside this draft and returned 7 archetype clusters, per-contact
ask routing for all 12 named contacts (Rimoli, Agogino, SunSpiral,
Mueller, Andrew Zhang, Brian Cera, Vespignani, Skelton, Sultan,
Bayandor, Jing Zhang, Anand), plus a "stretch" section of
collaborative mechanisms we hadn't considered. Full results at
`edison-trajectories/2026-05-12-outreach-topics-f18aca01-00bb-4ca7-a8e9-f6312dfaaff7.{md,json}`
— prefer those over the throwaway sentences below for any actual
outreach email body.

The aspects below are synthesized across this PR, PR #20 (manuscript),
PR #28 (Lansmont M23 + QTec/LDV instrumentation), PR #38/#43 (PETG-TPU
joint design + CAD review), and PR #47 (egg-drop demo).

#### A. Technical / scientific feedback to seek

1. **Sim-to-experiment fidelity gap on impact.** "Our rigid-strut
   tensegrity sims (MuJoCo / PyBullet / Newton-XPBD) show peak-g is
   essentially insensitive to cable stiffness because floor-contact
   stiffness dominates the impulse, while SEA varies by ~10× across
   three decades of cable stiffness. Before we invest in DiffPD or
   PolyFEM+IPC, does your group's experience suggest a cheaper
   intermediate (e.g. lumped-mass + Hertzian contact, or a calibrated
   floor-stiffness term in a rigid solver) is good enough for BO inner
   loops?" *Best contact: Rimoli (Pajunen 2019 Mater. & Des. impact
   data); Mueller (collision-resilient hardware control loop).*
2. **PETG–TPU multi-material interface characterization.** "We could
   not find peer-reviewed PETG-TPU bond data — only PLA-TPU
   (Lopes 2018, Zhang 2026, Ruwais 2025: butt 6.5 MPa, alt-deposition
   7.4 MPa, mechanical-interlock shear ~24 MPa). Do you have, or know
   of, characterization data for PETG-TPU butt / overmold / barbed
   joints printed on a Bambu H2D-class IDEX, and is the PLA-TPU
   shear-vs-interlock ratio a defensible extrapolation?" *Best
   contact: Valdevit / Crook (Bauer 2021 Adv. Mater. metamaterials),
   or any AM lab with multi-material FFF instrumentation.*
3. **Standardized drag-free egg-drop benchmark.** "No formal
   egg-drop benchmark exists in the literature; the SUPERball NIAC
   1-foot staircase, Zhang 2022 fixed-height, and Anand 2022
   single-altitude protocols are not directly comparable. We are
   proposing a Bruceton h_crit (n>=20, Δh = 0.5 m, randomized
   orientation) on a 200 mm bounding-sphere / <=500 g / 55 g egg
   shared-constraint set. Would your group co-author or endorse this
   as a community protocol?" *Best contact: Agogino + SunSpiral
   (SUPERball NIAC); Jing Zhang (HIT, Aerospace 2025).*
4. **Class-1 vs class-2 classification under FFF print constraints.**
   "Our printable strut diameter floor (≥2.0 mm at 0.4 mm nozzle) plus
   tendon Ø in [1.2, 6.0] mm pushes us toward class-2 (struts touch)
   for the smallest unit cells — does this materially change the
   form-finding and impact-mechanics intuition that has been built up
   on class-1 SUPERball geometries?" *Best contact: Skelton / Sultan
   (class-1 theory); Cera + Zhang (six-bar lattice topologies, 2018).*
5. **BO acquisition for noisy h_crit.** "h_crit from a Bruceton
   staircase is a noisy ordinal observation, not a continuous
   objective. Have you found a single-fidelity GP + qNEI workable
   here, or do we need a censored / Bernoulli observation model and a
   multi-fidelity stack (cheap rigid-strut sim → DiffPD → physical
   drop)?" *Best contact: Mueller (HW/control noise modeling);
   Bayandor (TANDEM scaled-payload sim).*

#### B. Tech-transfer / commercialization angles

1. **NIAC successor / NASA SBIR-STTR space systems.** "The SUPERball
   NIAC ended in 2018; is there appetite at NASA Ames or via a SBIR
   topic for an FFF-printable, BO-optimized successor demo at the
   200 mm scale that doesn't require custom rod stock?" *Best
   contact: SunSpiral, Agogino, Vespignani.*
2. **DoT / FAA drone-cargo airdrop and biomedical sample drop.**
   "Anand 2022 demonstrated 75 m biodegradable tensegrity drops for
   medical payloads. Would a reusable FFF-printable 200 mm version
   be of interest to a drone-cargo or rural-clinic sample-transport
   program?" *Best contact: Anand; Mueller (HiPeRLab UAV pipeline).*
3. **Assistive-device OEM pull (PR #20).** "Our primary
   application thread is a crutch-tip / orthotic energy-absorber.
   Is there a lab-to-OEM bridge (Permobil, Ottobock, Össur) you've
   used to take a tensegrity-derived component into a clinical
   pilot?" *Best contact: any with biomechanics / rehab adjacency;
   most likely Mueller via the BYU MRG biomechanics audience.*

#### C. Immediate "gotchas" to invite the recipient to call out

1. **Floor-contact stiffness swamps the cable signal.** "We expect
   you to push back on impact-mechanics claims drawn from a
   rigid-strut + tendon model; we will pre-empt by showing the
   3-decade cable-stiffness sweep in which peak-g moves <2%."
2. **TPU 85A creep shifts prestress between drops.** "Our reusability
   FoM (N_reuse) is sensitive to viscoelastic relaxation of the TPU
   tendons; we currently re-tension between drops and have not
   characterized the relaxation curve."
3. **Bambu H2D filament-swap interface as the dominant failure
   mode.** "Strut-tendon interface delamination at the IDEX hand-off
   is our most common print failure; this is upstream of any joint
   topology choice (anchor-bulb vs dovetail vs barbed rebar)."
4. **Bruceton staircase needs randomized orientations.** "A worst-case
   orientation alone is not a defensible h_crit, and isotropy claims
   for 6-bar tensegrity rest on Zhang 2022's three-orientation
   sweep — we need a larger orientation set."
5. **Embedded-egg / mid-print egg fixturing pitfalls.** "Mid-print
   embedding cooks shells at PETG print temps; we use post-print TPU
   85A cradles, and would value a sanity check on cradle compliance
   vs egg fracture envelope (Trnka 2012: 24.6-53.5 N, weakest at
   equator)."

#### D. Collaborative-contribution mechanisms

1. **External validation against published datasets.** Re-run our BO
   loop's "best" geometry through their solver of record (e.g.
   Rimoli's bar-buckling sim, Vespignani's SUPERball v2 model,
   Bayandor's TANDEM solver) and report the cross-tool delta as a
   joint short paper or supplementary.
2. **Inter-lab specimen exchange.** Print 5-10 of our top-of-curve
   geometries on the Bambu H2D and ship to UC Berkeley HiPeRLab /
   NASA Ames / Georgia Tech for independent drop testing on their
   instrumented rigs (Agogino-style staircase, Mueller HiPeRLab
   pendulum, etc.).
3. **Instrument-time swap.** Trade time on our Lansmont M23 +
   Polytec / QTec LDV (PR #28; closest analog Grétarsson & Lindell
   2023) for time on a partner's high-speed video / DIC / shake table.
4. **Shared standardized egg-drop benchmark.** Co-author the
   200 mm / 500 g / 55 g / Bruceton-staircase protocol so subsequent
   tensegrity-vs-foam-vs-lattice papers report comparable numbers.
5. **GitHub-hosted reproducible BO loop.** Publish the geometry-→-print-
   →-drop-→-update pipeline as a reusable Ax/BoTorch + Newton + slicer
   recipe so collaborators can swap in their own objective and get a
   first BO trajectory in <1 day.
6. **Co-supervised undergraduate / capstone or REU project.** A
   well-bounded scope (e.g. "characterize PETG-TPU barbed-joint pull-
   out vs barb count") fits a one-semester student project at either
   end and gives both labs a co-authored publication.
7. **Joint workshop / invited session.** Propose a session at IDETC
   (DAC + DfMLC), SMASIS, or AIAA SciTech on "BO-optimized
   tensegrity / metamaterial impact absorbers — what is and isn't
   transferable across labs?"
8. **Cross-citation in revision.** Lowest-cost ask: explicit pointer
   to their most directly relevant paper in our intro / discussion in
   exchange for a comment on a draft section.

### 3d. Backup venue: Smart Materials and Structures (IOP)

Edison flagged the SMS metamaterials / phononic-crystals and smart structural
systems sections as the right home if JMD declines, and surfaced these
directly relevant SMS-published priors as orientation: Hosseinabadi et al.,
*SMS* (2023) on negative-stiffness 3D-printed meta-structures, and Ding et
al., *SMS* (2025) on tensegrity D-bar metamaterials. Suggested SMS
reviewers (3-5):

1. **Filipe A. Santos** (NOVA Lisbon) — tensegrity energy-dissipation metamaterials, *Adv. Mater.* (2023).
2. **Fernando Fraternali** (Salerno) — tensegrity wave dynamics & metamaterial building blocks.
3. **Andrea Micheletti** (Roma Tor Vergata) — 3D-printed bistable tensegrity units, *Addit. Manuf.* (2022).
4. **Kirsti Pajunen** — 3D-printed tensegrity-inspired lattice dynamics, *Extreme Mech. Lett.* (2021).
5. **Anna Al Sabouni-Zawadzka** (Warsaw University of Technology) — 3D-printed tensegrity-inspired metamaterial experimental characterization (2022).

If retargeting to SMS, the framing also needs to pivot from the BO-workflow
contribution to the *novel metamaterial behavior and tunable energy
absorption* — SMS reviewers are more likely to ask about dynamic-testing
methodology, constitutive modeling, and comparison with other metamaterial
architectures than about acquisition-function choice or surrogate scalability.

### 3e. Why the prior "BoTorch/Ax authors" pool was dropped

The earlier draft of this section listed Balandat, Daulton, Bakshy, and Ament
(authors of the BoTorch / Ax / qNEHVI software stack) as candidates because
they appeared frequently in our consolidated `references.bib`. They are
**out of scope** as JMD reviewers: their publication venues are NeurIPS / ICML
/ JMLR (machine-learning conferences and a software framework at Meta), not
ASME design or mechanics journals. A JMD AE has no good signal to pick them
for a *design / mechanics / AM* manuscript review. They remain valuable as
methodology citations but should not appear in the "Suggested Reviewers"
field. The same caution applies to any future reviewer suggestion: every
candidate must have at least one paper in JMD, a sister ASME journal, or
a directly comparable domain-leading peer-reviewed venue (Composite
Structures, *Adv. Mater.*, *Sci. Adv.*, *Addit. Manuf.*, *Extreme Mech. Lett.*,
*npj Comput. Mater.*, *Struct. Multidiscip. Optim.*, *J. Eng. Mech.*).

## 4. Most-cited venues across our existing literature corpus (signal for AE assignment)

The AE handling our manuscript at JMD is almost certainly an active publisher
in one of the top venues from our own bibliography and trajectories. The table
below is the venue-frequency tally over all 19 Edison trajectory `.md` files
on PR branches plus the consolidated `manuscript/references.bib`; it is a
direct proxy for which JMD AE silo is the best fit.

| Frequency tier | Venues |
|---|---|
| **High (>=10 hits)** | Polymers; Materials & Design; Additive Manufacturing; Science; Science Advances; Assistive Technology |
| **Medium (4-10)**     | IEEE ICRA; IEEE IROS; Advanced Materials; Rapid Prototyping Journal; Journal of Biomechanics |
| **Low (1-3)**         | Composite Structures; Int. J. Solids and Structures; J. Mechanics and Physics of Solids; Smart Materials and Structures (×1); ASME J. Mechanisms and Robotics (×1); Structural and Multidisciplinary Optimization; Soft Robotics; Nature Communications; npj Computational Materials |

**Read of this table:** our existing literature pull is *materials- and
manufacturing-heavy* (Polymers, Mater. & Des., Addit. Manuf.) with a healthy
robotics/tensegrity slice (ICRA/IROS, Composite Structures) and an
assistive-device tail (Assistive Technology, J. Biomechanics). It is **light on
core ASME JMD venues** -- only one ASME J. Mechanisms and Robotics hit and one
SMS hit show up in this corpus. **Action item for the manuscript:** before
submission, run one more targeted Edison literature pass against JMD,
J. Mech. and Robotics, J. Applied Mechanics, and Structural and
Multidisciplinary Optimization to thicken the core-design-theory layer of the
bibliography. This will (i) make the manuscript read as if its authors are
talking to the JMD community and (ii) generate additional in-corpus reviewer
candidates for the named-reviewer table in §3b.

## 5. Sources

- **Edison `LITERATURE_HIGH` task `9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`**
  (fetched 2026-05-09): `edison-trajectories/2026-05-09-target-audience-9cc7db18.md`
  + `.json` -- the primary source for §3a-§3d (named JMD AEs, 14 named
  candidate reviewers with representative JMD/JMR/JAM/Compos. Struct./
  Adv. Mater./Sci. Adv./Addit. Manuf./Extreme Mech. Lett./npj Comput. Mater./
  S&MO/J. Eng. Mech. papers, COI screen, SMS analog, JMD-rejection-reason
  analysis).
- **Edison `LITERATURE_HIGH` tasks `1b90208d-3555-4479-9db0-512d67e69f5f` and
  `f41b7034-439e-45de-b97f-4bf1d85b9811`** (egg-drop / drag-free lander
  benchmark, branch `copilot/explore-egg-drop-idea`, PR #47):
  `edison-trajectories/egg-drop-tensegrity-1b90208d.{md,json}` and
  `edison-trajectories/egg-drop-followup-f41b7034.{md,json}` — primary source
  for §3d′ (lander-style outreach contacts: Rimoli, Agogino, SunSpiral,
  Mueller, Zhang/Cera, Vespignani, Skelton/Sultan, Bayandor, Jing Zhang,
  Anand).
- `manuscript/references.bib` (PR #20, branch `copilot/create-manuscript-template`).
- `edison-trajectories/01..04*.md` (branch `copilot/explore-impact-absorption-crutches`,
  PR #18 lineage).
- `edison-trajectories/tpu-petg-bo-variables-5ae24eaf-*.md`
  (branch `copilot/explore-tpu-petg-variables`).
- `edison-trajectories/2026-05-08-sim-survey-782657e0.md`
  (branch `copilot/explore-simulations-for-tensegrity`).
- `edison-trajectories/joint-design/*.md` and
  `edison-trajectories/{1400ca69,3b9d76b5}*.md`
  (branch `copilot/explore-joint-design-for-petg-tpu`).
- `edison-trajectories/60470477-*-naming.md`
  (branch `copilot/create-repo-project-name`).
- `reviews/mock_reviews.md` (committee-style mock review of the proposal).
