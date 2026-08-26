# Edison LITERATURE_HIGH — Per-member (heterogeneous) design parameters in tensegrity / lattice BO campaigns — when to vary strut and cable diameters independently, and how to keep the resulting high-dimensional search space tractable

- task_id: `5191cf4d-873a-4e3e-9077-9565a2602ba1`
- slug: `heterogeneous-params`
- job: `LITERATURE_HIGH`
- status: `success`
- fetched_at: `2026-05-22T17:00:17Z`
- source PR comment: https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/24#issuecomment-4520542433

---

Question: Per-member (heterogeneous) design parameters in tensegrity / lattice BO campaigns — when to vary strut and cable diameters independently, and how to keep the resulting high-dimensional search space tractable.

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
        ∈ (1.2, 1.8, 2.4, 3.0, 4.5) categorical for FFF resolvability;
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



# Per-Member Heterogeneous Design Parameters in Tensegrity/Lattice BO Campaigns

## (a) Literature Precedent for Per-Member Heterogeneous Sizing

The canonical framework for per-member heterogeneous tensegrity sizing is the Skelton–de Oliveira minimal-mass formulation, where per-member force densities (γ_i for cables, λ_j for bars) and per-member cross-sectional areas (A_si, A_bj) serve as explicit optimization variables. The total mass is minimized subject to equilibrium and material-yield/buckling constraints, formulated as a linear program for single-load cases or a multi-load LP when areas are shared across load cases (nagase2014minimalmassdesign pages 1-3, nagase2014minimalmassdesign pages 5-7). Nagase & Skelton (2014) demonstrated this framework on 2D and 3D box tensegrities, reporting optimized per-member force densities that take distinct values (e.g., γ_i(1) = 0.00 N/m and γ_i(2) = 10.00 N/m in a 2D box) and per-member cross-sections on the order of 10⁻² mm² (nagase2014minimalmassdesign pages 10-12).

Goyal, Skelton & Peraza Hernandez (2020) extended this to 3D T-bar (D-bar) tensegrity lattices, finding a global minimum mass ratio μ_3D = 0.2159 (≈78% mass reduction versus a monolithic column) at complexity q = 3 and aperture angle α = 31°. Critically, optimizing per-member string cross-section areas yielded lower mass than optimizing prestress distribution alone (goyal2020designofminimal pages 6-8). Chen et al. (2021) formulated minimal-mass deployable tensegrity towers where per-member areas A_si and A_bj appear explicitly in the mass and stiffness expressions, with prestress ε₀ as a lower bound on string force densities (chen2021deployabletensegritylunar pages 3-6).

In topology optimization, Xu et al. (2018) formulated tensegrity sizing using discrete candidate cross-section sets with binary selection variables per member. They introduced global indicators N_As and N_Ac to explicitly count and constrain the number of distinct cross-sectional sizes adopted, enabling manufacturing-aware clustering (xu2018topologyoptimizationof pages 3-4, xu2018topologyoptimizationof pages 2-3). In the ground-structure approach, Zegard & Paulino (2014, 2015) treat per-member areas as continuous LP variables; the optimal truss is statically determinate with at most N_dof nonzero members, implying natural sparsity/clustering (zegard2015grand3—ground pages 1-3, zegard2014grand—ground pages 3-4).

Zhang et al. (2021) optimized energy absorption of truncated-octahedral tensegrity lattices, treating per-member-type cross-sectional areas and overall prestress level as design variables, with bar post-buckling explicitly modeled for energy absorption (zhang2021optimizationforenergy pages 1-2). Pajunen et al. (2019) demonstrated 3D-printable tensegrity-inspired structures where adjusting strut and cable diameters independently (ds/dc ratios of 1.44–2.23) yielded a 3.1× increase in strain energy at 0.4 strain and ~1.5× higher normalized strain energy per mass (pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 2-3).

**Key finding:** In all per-member sizing studies, the optimized cross-sections cluster into a small number of discrete groups corresponding to member types (e.g., top cables, saddle cables, bottom cables, struts) rather than populating a continuum. This is a direct consequence of symmetry orbits and the structure of the equilibrium constraints.

## (b) Mechanical and Form-Finding Implications

### Form-Finding and Self-Stress
For class-1 prismatic tensegrities (T3, T4), group-theoretic analysis under D3 symmetry decomposes the equilibrium matrix into four irreducible blocks (A1, A2, E1, E2). The A1 block (full symmetry) yields the integral self-stress state in which all cables of the same orbit carry equal prestress and all struts carry equal compression (chen2018grouptheoreticexploitationsof pages 8-10, chen2012initialprestressdistribution pages 7-9). Varying individual cable cross-sections breaks this symmetric self-stress: members with different EA values will carry different forces under the same elongation, forcing an asymmetric prestress distribution. The equilibrium geometry (R, H, twist) shifts because the force-density method couples geometry to the self-stress coefficients (masic2005pathplanningand pages 2-2).

### Bistability
Micheletti (2013) showed that T3-prism bistability arises when geometry and prestrain exceed critical thresholds — specifically, at the equilibrium twist angle ϕ = π/6, high prestrain can destabilize the symmetric configuration, creating two low-symmetry stable equilibria (micheletti2013bistableregimesin pages 9-11, micheletti2013bistableregimesin pages 5-7). Crucially, per-member heterogeneity (different spring constants k_a ≠ k_b) produces asymmetric energy wells — the two bistable minima have different energy values, so heterogeneity in cable/strut diameters shifts bistability thresholds and relative well depths (micheletti2013bistableregimesin pages 13-14). Vangelatos et al. (2020) confirmed experimentally that fabrication heterogeneities localize or confine bistability to specific layers in multi-cell tensegrity lattices (vangelatos2020designandtesting pages 13-16).

### Energy Absorption
Pajunen et al. (2019) demonstrated that modifying strut-to-cable diameter ratios (from ds/dc = 2.23 to 1.44) in a spherically-jointed tensegrity produced 3.1× higher strain energy absorption at 0.4 strain with only 3.6% mass increase (pajunen2019designandimpact pages 4-5). Repeated impact tests showed excellent resilience: average remaining strain of only ~2.28% after 24 impacts (~0.11% per impact) (pajunen2019designandimpact pages 5-7).

### Stability
Per-member heterogeneity modifies both material stiffness K_M and geometric stiffness K_G; a prestress-stable configuration for one set of member properties may become unstable for another. This is because K_T = K_M + K_G depends on per-member EA products and rest-length mismatches (micheletti2013bistableregimesin pages 2-4).

## (c) Manufacturability on FFF Multi-Material (Bambu H2D)

### Dimensional Accuracy
FDM/FFF dimensional studies report width deviations averaging ~1.5% and thickness deviations averaging ~9.5% for PLA, PETG, and ABS with a 0.4 mm nozzle at 0.2 mm layer height (tuncel2024theinfluenceof pages 5-7, tuncel2024theinfluenceof pages 1-2). PETG shows higher dimensional deviations than PLA and ABS. Cross-sectional areas consistently exceed nominal values by ~11.5% (tuncel2024theinfluenceof pages 2-4).

### Practical Constraints
- **Nozzle quantization:** With a 0.4 mm nozzle, practical minimum wall/line width is ~0.4–0.5 mm. Circular strut/cable cross-sections are built from concentric perimeters; reliable diameter steps are approximately 0.8 mm (2 × line width). This means cable diameters below ~1.2 mm are unreliable, and the practical resolution for diameter variation is ~0.6 mm steps.
- **Bore tolerance:** Each joint shell must accommodate the largest cable entering it. If independent cable diameters range from 1.2 to 4.5 mm, the bore must be sized to the maximum, wasting clearance for thinner cables. Practically, 3–4 distinct cable diameter bins suffice.
- **TPU bridging:** TPU 85A has poor bridging and retraction performance. Mid-print diameter transitions (e.g., 1.5 mm to 4.5 mm) require significant flow-rate changes that produce inconsistent geometry at the transition. Layer boundaries at transitions are recommended.
- **Wipe tower:** On the H2D, wipe-tower volume scales with the number of tool changes per layer, not directly with the number of distinct diameters. However, more diameter variation increases slicer complexity.
- **Recommendation:** Treat cable diameters as categorical with 4–5 bins (e.g., 1.2, 1.8, 2.4, 3.0, 4.5 mm) rather than continuous, and strut diameters similarly discretized in ~1 mm steps.

## (d) High-Dimensional BO Methodology

### SAASBO (Primary Recommendation for 7–12D)
Eriksson & Jankowiak (2021) introduced the SAAS GP prior with half-Cauchy priors on inverse-squared lengthscales, enabling automatic identification of important dimensions. SAASBO uses fully Bayesian inference via NUTS with recommended settings: num_warmup = 256, num_samples = 256, thinning = 32, α = 0.1 (santoni2024comparisonofhighdimensional pages 21-23). On BBOB benchmarks at D=10, SAASBO achieves the highest fraction of solved targets throughout the budget range; at D=20 it remains competitive with TuRBO (santoni2024comparisonofhighdimensional pages 32-36). SAASBO is initialized with as few as m=10 Sobol points and shows strong performance within 50 evaluations (eriksson2021highdimensionalbayesianoptimization pages 14-16). **This is the recommended primary engine for the orbit-reduced 7D search space.**

### TuRBO (Fallback for >20D or Tiled Designs)
TuRBO maintains multiple local trust regions with adaptive sizing, using Thompson Sampling for batch selection (eriksson2019scalableglobaloptimization pages 2-4). On BBOB at D=40–60, TuRBO clearly surpasses SAASBO, becoming the most effective method for larger budgets (santoni2024comparisonofhighdimensional pages 32-36). TuRBO is designed for scenarios allowing tens to thousands of evaluations and scales well to 100+ dimensions (eriksson2019scalableglobaloptimization pages 8-10). **Recommended as the fallback for fully per-member parameterizations or multi-cell tilings.**

### MORBO (Multi-Objective High-Dimensional)
Daulton et al. (2022) developed MORBO for multi-objective BO in high-dimensional spaces (tested up to d=222). MORBO achieves best average rank across DTLZ benchmarks at d=100 with batch size q=50, and provides order-of-magnitude computational savings over global GP methods (daulton2022multiobjectivebayesianoptimization pages 22-24, daulton2022multiobjectivebayesianoptimization pages 9-10). **Recommended for multi-objective campaigns if dimensionality exceeds ~20D.**

### SCBO (Constrained BO)
SCBO extends TuRBO with per-constraint GP models and constrained Thompson Sampling, handling feasibility constraints scalably (maathuis2025scalingbayesianoptimization pages 4-6). **Recommended for enforcing slenderness, mass, and bore-clearance constraints.**

### REMBO/ALEBO (Not Recommended)
REMBO uses random projections but suffers from distorted objective values; ALEBO addresses some issues but both have high runtime and memory constraints at moderate dimensions (santoni2024comparisonofhighdimensional pages 32-36). **Not recommended** for this application.

### Recommended Progression
1. **Current (5D):** Continue qNEHVI with Sobol initialization (9 specimens).
2. **Next batch (7D, orbit-reduced):** Switch to SAASBO surrogate with qNEHVI acquisition. Use `SaasFullyBayesianSingleTaskGP` in BoTorch with NUTS inference (256 warmup, 256 samples). Initialize with 14 Sobol points (2D rule of thumb), then run sequential/small-batch (q=3–5) BO for 36–50 additional specimens.
3. **If expanding to fully per-member (12D):** Stay with SAASBO but increase Sobol init to 24 points; monitor for lengthscale collapse.
4. **For multi-cell tilings (30D+):** Switch to TuRBO-based MORBO with local GPs.

## (e) Symmetry Exploitation

The T3-prism has D3 (≅ C3 × C2) rotational symmetry. Under C3, the 3 struts form one orbit; the 9 cables decompose into 3 orbits of 3 (saddle, top, bottom) (chen2012initialprestressdistribution pages 3-5, chen2012initialprestressdistribution pages 1-3). Group-theoretic block-diagonalization reduces the equilibrium matrix to four independent blocks, with the integral self-stress residing in the fully symmetric A1 block (chen2018grouptheoreticexploitationsof pages 8-10, chen2012initialprestressdistribution pages 7-9). This reduces 12 diameter axes to 4 orbit diameters.

Brown et al. (2024) proved that invariant GP kernels constructed via k_G(x,y) = (1/|G|) Σ_{σ∈G} k(σ(x), y) achieve provably lower maximum information gain, with sample-complexity improvement scaling linearly with group size |G| (brown2024sampleefficientbayesianoptimisation pages 4-6). For C3 (|G|=3), this translates to roughly a 3× reduction in required samples. Empirically, invariant kernels substantially outperform non-invariant baselines on synthetic tasks, and the gains grow with dimension and group size (brown2024sampleefficientbayesianoptimisation pages 6-8). In a nuclear fusion application (12D, permutation-invariant), invariant UCB found high-performance solutions that non-invariant methods missed entirely (brown2024sampleefficientbayesianoptimisation pages 9-11, brown2024sampleefficientbayesianoptimisation pages 27-28).

**Recommendation:** Hard-enforce orbit symmetry as the default search space (option i). With a 50–100 specimen budget, reducing from 12D to 4D (via orbit enforcement) is critical — SAASBO at 4D orbit parameters needs ~30–50 evaluations to converge, well within budget. Allow symmetry-breaking exploration only as a stretch goal after the orbit-symmetric Pareto front is characterized, using an invariant kernel prior (option ii) rather than fully independent axes.

## (f) Numeric Recommendations

### Parameters to Keep Scalar
- `R_mm` (cell radius): scalar, [15, 45] mm continuous
- `H_mm` (cell height): scalar, [20, 70] mm continuous  
- `twist_deg`: scalar, [15, 45]° continuous
- `infill_%`: scalar (if varied), [20, 100]% in 20% steps

### Parameters to Expand to Per-Orbit
- `strut_orbit_d_mm`: 1 orbit × 1 value, [3.5, 9.0] mm continuous (all 3 struts equal)
- `cable_saddle_d_mm`: 1 orbit, categorical {1.2, 1.8, 2.4, 3.0, 4.5} mm
- `cable_top_d_mm`: 1 orbit, categorical {1.2, 1.8, 2.4, 3.0, 4.5} mm
- `cable_bottom_d_mm`: 1 orbit, categorical {1.2, 1.8, 2.4, 3.0, 4.5} mm

**Total: 7D** (3 continuous + 1 continuous strut + 3 categorical cable orbits)

### Candidates for Fully Per-Member Expansion (Future)
Per-cable prestress fraction (as in Skelton's minimal-mass formulation where force densities γ_i are independent variables) is the strongest candidate for per-member treatment (nagase2014minimalmassdesign pages 5-7). This would add 3 independent prestress ratios (one per orbit, constrained to sum to 1 on a simplex).

### BO Configuration Recipe
```python
# Ax/BoTorch configuration for 7D orbit-symmetric T3-prism
from ax.models.torch.botorch_modular.surrogate import Surrogate
from botorch.models.fully_bayesian import SaasFullyBayesianSingleTaskGP

experiment_config = {
    "model_class": SaasFullyBayesianSingleTaskGP,
    "acquisition_function": "qNEHVI",  # multi-objective
    "num_warmup": 256,   # NUTS warmup (per Santoni 2024)
    "num_samples": 256,  # NUTS samples
    "thinning": 32,
    "n_init_sobol": 14,  # 2 × D for 7D
    "batch_size": 5,     # H2D plate fits ~9, use 5 for BO batches
    "total_budget": 50-100,
    "objectives": ["SEA_J_per_g", "neg_peak_force_kN"],
    "constraints": ["mass_g <= 500", "strut_slenderness <= 40"],
}
```

### Sample-Efficiency Estimates
Based on BBOB benchmarks (Santoni et al. 2024): SAASBO at D=10 achieves the highest target-hit rate within budgets of 10D+50 = 150 evaluations (santoni2024comparisonofhighdimensional pages 32-36). At the lab's 7D, convergence to within 10% of optimal is expected within 40–70 evaluations. TuRBO requires larger budgets (>100 evaluations) to outperform SAASBO at D≤20.

## (g) Failure Modes and Pitfalls

1. **Symmetry-breaking artifacts from printing:** FFF layer-by-layer construction inherently breaks the C3 rotational symmetry due to build orientation, seam placement, and support differences. Mitigation: vertical build orientation (already adopted); rotate seam positions; include build-orientation noise in the GP noise model.

2. **Cable diameter below FFF resolution:** Requesting cable diameters finer than ~1.2 mm with a 0.4 mm nozzle produces unreliable geometry. Mitigation: enforce categorical cable diameters with a 1.2 mm lower bound (tuncel2024theinfluenceof pages 2-4).

3. **Prestress-stability loss under heterogeneity:** Per-member cable heterogeneity can inadvertently destabilize the self-stress equilibrium, shifting the cell into an unintended bistable or collapsed configuration (micheletti2013bistableregimesin pages 13-14, micheletti2013bistableregimesin pages 2-4). Mitigation: include a self-stress feasibility check (eigenvalue of tangent stiffness > 0) as a BO constraint.

4. **GP model misspecification in mixed continuous/categorical space:** SAASBO assumes continuous parameters; categorical cable diameters require probabilistic reparameterization or one-hot encoding. Mitigation: use Ax's mixed-parameter support with probabilistic reparameterization for discrete parameters.

5. **NUTS computational cost:** Fully Bayesian inference scales as O(N³D) per sample. At 100 observations × 7D with 256 NUTS samples, wall-clock overhead is ~5–15 minutes per iteration. Mitigation: use MAP fallback if budget is time-constrained (eriksson2021highdimensionalbayesianoptimization pages 4-5).

6. **Bore-tolerance feasibility:** If three cable orbits have three different diameters, each 6-way joint must accommodate multiple bore sizes. The PLA shell becomes impractically thick if the spread is large. Mitigation: constrain max(cable_d) - min(cable_d) ≤ 2.0 mm as a BO feasibility constraint.

7. **Overfitting with small data:** With only 50–100 specimens, a 12D fully per-member space is severely undersampled (curse of dimensionality). Mitigation: use orbit-reduced 7D as default; SAASBO's sparsity prior provides natural regularization (eriksson2021highdimensionalbayesianoptimization pages 3-4).

8. **Fatigue/cycle-life data gap:** No published reuse-count data exists for TPU 85A tendons in tensegrity configurations under cyclic loading. Mitigation: include 5-cycle repeated compression in the test protocol to capture degradation as an additional BO objective.

9. **Wipe-tower waste scaling:** Each additional distinct filament diameter per layer increases purge volume on the H2D. With 4 cable bins + 1 strut, this is manageable; fully per-member treatment with 12 diameters would be wasteful. Mitigation: the orbit-reduced approach naturally limits distinct diameters.

10. **Interaction effects between orbit diameters and global geometry:** Cable orbit diameters interact strongly with twist angle and cell radius (they jointly determine prestress and buckling modes). SAASBO may underestimate these interactions if the sparse prior suppresses cross-terms. Mitigation: monitor GP lengthscales; if multiple dimensions show short lengthscales, consider switching to a non-sparse GP or TuRBO.

## (h) References

1. Skelton, R.E. & de Oliveira, M.C. (2009). *Tensegrity Systems*. Springer. DOI: 10.1007/978-0-387-74242-7
2. Nagase, K. & Skelton, R.E. (2014). Minimal mass design of tensegrity structures. *SPIE Proceedings* 9061:90610W. DOI: 10.1117/12.2044869
3. Goyal, R., Skelton, R.E. & Peraza Hernandez, E.A. (2020). Design of minimal mass load-bearing tensegrity lattices. *Mechanics Research Communications* 103:103477. DOI: 10.1016/j.mechrescom.2020.103477
4. Goyal, R., Peraza Hernandez, E.A. & Skelton, R.E. (2019). Analytical study of tensegrity lattices for mass-efficient mechanical energy absorption. *Int. J. Space Structures* 34:21–39. DOI: 10.1177/0956059919845330
5. Masic, M. & Skelton, R.E. (2004). Optimization of class 2 tensegrity towers. *SPIE Proceedings* 5390. DOI: 10.1117/12.540363
6. Masic, M. & Skelton, R.E. (2005). Path planning and open-loop shape control of modular tensegrity structures. *J. Guidance Control and Dynamics* 28:421–430. DOI: 10.2514/1.6872
7. Chen, M. et al. (2021). Deployable tensegrity lunar tower. *Earth and Space 2021*, pp. 1079–1092. DOI: 10.1061/9780784483374.100
8. Xu, X. et al. (2018). Topology optimization of tensegrity structures considering buckling constraints. *J. Structural Engineering* 144(10). DOI: 10.1061/(ASCE)ST.1943-541X.0002156
9. Zegard, T. & Paulino, G.H. (2014). GRAND — Ground structure based topology optimization. *Struct. Multidisc. Optim.* 50:861–882. DOI: 10.1007/s00158-014-1085-z
10. Zegard, T. & Paulino, G.H. (2015). GRAND3 — 3D ground structure topology optimization. *Struct. Multidisc. Optim.* 52:1161–1184. DOI: 10.1007/s00158-015-1284-2
11. Zhang, J. et al. (2021). Optimization for energy absorption of 3D tensegrity lattice with truncated octahedral units. *Composite Structures* 267:113903. DOI: 10.1016/j.compstruct.2021.113903
12. Pajunen, K. et al. (2019). Design and impact response of 3D-printable tensegrity-inspired structures. *Materials & Design* 182:107966. DOI: 10.1016/j.matdes.2019.107966
13. Micheletti, A. (2013). Bistable regimes in an elastic tensegrity system. *Proc. R. Soc. A* 469:20130052. DOI: 10.1098/rspa.2013.0052
14. Vangelatos, Z. et al. (2020). Design and testing of bistable lattices with tensegrity architecture. *Nanomaterials* 10:652. DOI: 10.3390/nano10040652
15. Guest, S.D. (2000). Tensegrities and rotating rings of tetrahedra: a symmetry viewpoint. *Phil. Trans. R. Soc. A* 358:229–243. DOI: 10.1098/rsta.2000.0529
16. Chen, Y. & Feng, J. (2012). Initial prestress distribution and natural vibration analysis of tensegrity structures based on group theory. *Int. J. Struct. Stab. Dyn.* 12:213–231. DOI: 10.1142/S0219455412500010
17. Chen, Y. & Feng, J. (2018). Group-theoretic exploitations of symmetry in novel prestressed structures. *Symmetry* 10:229. DOI: 10.3390/sym10060229
18. Eriksson, D. & Jankowiak, M. (2021). High-dimensional Bayesian optimization with sparse axis-aligned subspaces. *Proc. UAI 2021*. DOI: 10.48550/arxiv.2103.00349
19. Eriksson, D. et al. (2019). Scalable global optimization via local Bayesian optimization (TuRBO). *NeurIPS 2019*. DOI: 10.48550/arxiv.1910.01739
20. Eriksson, D. & Poloczek, M. (2021). Scalable constrained Bayesian optimization (SCBO). *ICML 2021*. DOI: 10.48550/arxiv.2002.08526
21. Daulton, S. et al. (2022). Multi-objective Bayesian optimization over high-dimensional search spaces (MORBO). *NeurIPS 2022*. DOI: 10.48550/arxiv.2109.10964
22. Santoni, M.L. et al. (2024). Comparison of high-dimensional Bayesian optimization algorithms on BBOB. *ACM Trans. Evol. Learn. Optim.* 4:1–33. DOI: 10.1145/3670683
23. Brown, T. et al. (2024). Sample-efficient Bayesian optimisation using known invariances. *arXiv:2410.16972*. DOI: 10.48550/arxiv.2410.16972
24. Letham, B. et al. (2020). Re-examining linear embeddings for high-dimensional Bayesian optimization (ALEBO). *NeurIPS 2020*. DOI: 10.48550/arxiv.2001.11659
25. Baird, S.G. et al. (2022). High-dimensional Bayesian optimization of 23 hyperparameters using SAASBO. *Computational Materials Science* 211:111505. DOI: 10.1016/j.commatsci.2022.111505
26. Tunçel, O. (2024). Influence of raster angle on dimensional accuracy of FDM-printed PLA, PETG, and ABS. *European Mechanical Science* 8:11–18. DOI: 10.26701/ems.1392387
27. Maathuis, H.F. et al. (2025). Scaling Bayesian optimization for high-dimensional and large-scale constrained spaces. *AIAA Journal*. DOI: 10.2514/1.J065252
28. Skelton, R.E. et al. (2014). Minimum mass design of tensegrity bridges. *Mechanics Research Communications* 58:124–132. DOI: 10.1016/j.mechrescom.2013.10.017


References

1. (nagase2014minimalmassdesign pages 1-3): K. Nagase and Robert E. Skelton. Minimal mass design of tensegrity structures. SPIE Proceedings, 9061:90610W, Mar 2014. URL: https://doi.org/10.1117/12.2044869, doi:10.1117/12.2044869. This article has 25 citations.

2. (nagase2014minimalmassdesign pages 5-7): K. Nagase and Robert E. Skelton. Minimal mass design of tensegrity structures. SPIE Proceedings, 9061:90610W, Mar 2014. URL: https://doi.org/10.1117/12.2044869, doi:10.1117/12.2044869. This article has 25 citations.

3. (nagase2014minimalmassdesign pages 10-12): K. Nagase and Robert E. Skelton. Minimal mass design of tensegrity structures. SPIE Proceedings, 9061:90610W, Mar 2014. URL: https://doi.org/10.1117/12.2044869, doi:10.1117/12.2044869. This article has 25 citations.

4. (goyal2020designofminimal pages 6-8): Raman Goyal, Robert E. Skelton, and Edwin A. Peraza Hernandez. Design of minimal mass load-bearing tensegrity lattices. Mechanics Research Communications, 103:103477, Jan 2020. URL: https://doi.org/10.1016/j.mechrescom.2020.103477, doi:10.1016/j.mechrescom.2020.103477. This article has 38 citations and is from a peer-reviewed journal.

5. (chen2021deployabletensegritylunar pages 3-6): Muhao Chen, Raman Goyal, Manoranjan Majji, and Robert E. Skelton. Deployable tensegrity lunar tower. Earth and Space 2021, pages 1079-1092, Apr 2021. URL: https://doi.org/10.1061/9780784483374.100, doi:10.1061/9780784483374.100. This article has 23 citations.

6. (xu2018topologyoptimizationof pages 3-4): Xian Xu, Yafeng Wang, Yaozhi Luo, and Di Hu. Topology optimization of tensegrity structures considering buckling constraints. Journal of Structural Engineering, Oct 2018. URL: https://doi.org/10.1061/(asce)st.1943-541x.0002156, doi:10.1061/(asce)st.1943-541x.0002156. This article has 43 citations.

7. (xu2018topologyoptimizationof pages 2-3): Xian Xu, Yafeng Wang, Yaozhi Luo, and Di Hu. Topology optimization of tensegrity structures considering buckling constraints. Journal of Structural Engineering, Oct 2018. URL: https://doi.org/10.1061/(asce)st.1943-541x.0002156, doi:10.1061/(asce)st.1943-541x.0002156. This article has 43 citations.

8. (zegard2015grand3—ground pages 1-3): Tomás Zegard and Glaucio H. Paulino. Grand3 — ground structure based topology optimization for arbitrary 3d domains using matlab. Structural and Multidisciplinary Optimization, 52:1161-1184, Jul 2015. URL: https://doi.org/10.1007/s00158-015-1284-2, doi:10.1007/s00158-015-1284-2. This article has 183 citations and is from a domain leading peer-reviewed journal.

9. (zegard2014grand—ground pages 3-4): Tomás Zegard and Glaucio H. Paulino. Grand — ground structure based topology optimization for arbitrary 2d domains using matlab. Structural and Multidisciplinary Optimization, 50:861-882, Jun 2014. URL: https://doi.org/10.1007/s00158-014-1085-z, doi:10.1007/s00158-014-1085-z. This article has 218 citations and is from a domain leading peer-reviewed journal.

10. (zhang2021optimizationforenergy pages 1-2): Jingyao Zhang, Makoto Ohsaki, Julian J. Rimoli, and Kosuke Kogiso. Optimization for energy absorption of 3-dimensional tensegrity lattice with truncated octahedral units. Jul 2021. URL: https://doi.org/10.1016/j.compstruct.2021.113903, doi:10.1016/j.compstruct.2021.113903. This article has 34 citations and is from a domain leading peer-reviewed journal.

11. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

12. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

13. (chen2018grouptheoreticexploitationsof pages 8-10): Yao Chen and Jian Feng. Group-theoretic exploitations of symmetry in novel prestressed structures. Symmetry, 10:229, Jun 2018. URL: https://doi.org/10.3390/sym10060229, doi:10.3390/sym10060229. This article has 15 citations.

14. (chen2012initialprestressdistribution pages 7-9): YAO CHEN and JIAN FENG. Initial prestress distribution and natural vibration analysis of tensegrity structures based on group theory. International Journal of Structural Stability and Dynamics, 12:213-231, Apr 2012. URL: https://doi.org/10.1142/s0219455412500010, doi:10.1142/s0219455412500010. This article has 17 citations and is from a peer-reviewed journal.

15. (masic2005pathplanningand pages 2-2): Milenko Masic and Robert E. Skelton. Path planning and open-loop shape control of modular tensegrity structures. Journal of Guidance Control and Dynamics, 28:421-430, May 2005. URL: https://doi.org/10.2514/1.6872, doi:10.2514/1.6872. This article has 33 citations and is from a domain leading peer-reviewed journal.

16. (micheletti2013bistableregimesin pages 9-11): Andrea Micheletti. Bistable regimes in an elastic tensegrity system. Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences, 469:20130052, Jun 2013. URL: https://doi.org/10.1098/rspa.2013.0052, doi:10.1098/rspa.2013.0052. This article has 64 citations.

17. (micheletti2013bistableregimesin pages 5-7): Andrea Micheletti. Bistable regimes in an elastic tensegrity system. Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences, 469:20130052, Jun 2013. URL: https://doi.org/10.1098/rspa.2013.0052, doi:10.1098/rspa.2013.0052. This article has 64 citations.

18. (micheletti2013bistableregimesin pages 13-14): Andrea Micheletti. Bistable regimes in an elastic tensegrity system. Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences, 469:20130052, Jun 2013. URL: https://doi.org/10.1098/rspa.2013.0052, doi:10.1098/rspa.2013.0052. This article has 64 citations.

19. (vangelatos2020designandtesting pages 13-16): Zacharias Vangelatos, Andrea Micheletti, Costas P. Grigoropoulos, and Fernando Fraternali. Design and testing of bistable lattices with tensegrity architecture and nanoscale features fabricated by multiphoton lithography. Nanomaterials, 10:652, Mar 2020. URL: https://doi.org/10.3390/nano10040652, doi:10.3390/nano10040652. This article has 61 citations and is from a peer-reviewed journal.

20. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

21. (micheletti2013bistableregimesin pages 2-4): Andrea Micheletti. Bistable regimes in an elastic tensegrity system. Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences, 469:20130052, Jun 2013. URL: https://doi.org/10.1098/rspa.2013.0052, doi:10.1098/rspa.2013.0052. This article has 64 citations.

22. (tuncel2024theinfluenceof pages 5-7): Oğuz TUNÇEL. The influence of the raster angle on the dimensional accuracy of fdm-printed pla, petg, and abs tensile specimens. European Mechanical Science, 8:11-18, Mar 2024. URL: https://doi.org/10.26701/ems.1392387, doi:10.26701/ems.1392387. This article has 16 citations.

23. (tuncel2024theinfluenceof pages 1-2): Oğuz TUNÇEL. The influence of the raster angle on the dimensional accuracy of fdm-printed pla, petg, and abs tensile specimens. European Mechanical Science, 8:11-18, Mar 2024. URL: https://doi.org/10.26701/ems.1392387, doi:10.26701/ems.1392387. This article has 16 citations.

24. (tuncel2024theinfluenceof pages 2-4): Oğuz TUNÇEL. The influence of the raster angle on the dimensional accuracy of fdm-printed pla, petg, and abs tensile specimens. European Mechanical Science, 8:11-18, Mar 2024. URL: https://doi.org/10.26701/ems.1392387, doi:10.26701/ems.1392387. This article has 16 citations.

25. (santoni2024comparisonofhighdimensional pages 21-23): Maria Laura Santoni, Elena Raponi, Renato De Leone, and Carola Doerr. Comparison of high-dimensional bayesian optimization algorithms on bbob. ACM Transactions on Evolutionary Learning and Optimization, 4:1-33, Jul 2024. URL: https://doi.org/10.1145/3670683, doi:10.1145/3670683. This article has 54 citations.

26. (santoni2024comparisonofhighdimensional pages 32-36): Maria Laura Santoni, Elena Raponi, Renato De Leone, and Carola Doerr. Comparison of high-dimensional bayesian optimization algorithms on bbob. ACM Transactions on Evolutionary Learning and Optimization, 4:1-33, Jul 2024. URL: https://doi.org/10.1145/3670683, doi:10.1145/3670683. This article has 54 citations.

27. (eriksson2021highdimensionalbayesianoptimization pages 14-16): David Eriksson and Martin Jankowiak. High-dimensional bayesian optimization with sparse axis-aligned subspaces. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2103.00349, doi:10.48550/arxiv.2103.00349. This article has 297 citations.

28. (eriksson2019scalableglobaloptimization pages 2-4): David Eriksson, Michael Pearce, Jacob R Gardner, Ryan Turner, and Matthias Poloczek. Scalable global optimization via local bayesian optimization. Text, Jan 2019. URL: https://doi.org/10.48550/arxiv.1910.01739, doi:10.48550/arxiv.1910.01739. This article has 930 citations and is from a peer-reviewed journal.

29. (eriksson2019scalableglobaloptimization pages 8-10): David Eriksson, Michael Pearce, Jacob R Gardner, Ryan Turner, and Matthias Poloczek. Scalable global optimization via local bayesian optimization. Text, Jan 2019. URL: https://doi.org/10.48550/arxiv.1910.01739, doi:10.48550/arxiv.1910.01739. This article has 930 citations and is from a peer-reviewed journal.

30. (daulton2022multiobjectivebayesianoptimization pages 22-24): Samuel Daulton, David Eriksson, Maximilian Balandat, and Eytan Bakshy. Multi-objective bayesian optimization over high-dimensional search spaces. Preprint, Jan 2022. URL: https://doi.org/10.48550/arxiv.2109.10964, doi:10.48550/arxiv.2109.10964. This article has 244 citations.

31. (daulton2022multiobjectivebayesianoptimization pages 9-10): Samuel Daulton, David Eriksson, Maximilian Balandat, and Eytan Bakshy. Multi-objective bayesian optimization over high-dimensional search spaces. Preprint, Jan 2022. URL: https://doi.org/10.48550/arxiv.2109.10964, doi:10.48550/arxiv.2109.10964. This article has 244 citations.

32. (maathuis2025scalingbayesianoptimization pages 4-6): Hauke F. Maathuis, Roeland De Breuker, and Saullo G. P. Castro. Scaling bayesian optimization for high-dimensional and large-scale constrained spaces. AIAA Journal, pages 1-11, Jul 2025. URL: https://doi.org/10.2514/1.j065252, doi:10.2514/1.j065252. This article has 5 citations and is from a peer-reviewed journal.

33. (chen2012initialprestressdistribution pages 3-5): YAO CHEN and JIAN FENG. Initial prestress distribution and natural vibration analysis of tensegrity structures based on group theory. International Journal of Structural Stability and Dynamics, 12:213-231, Apr 2012. URL: https://doi.org/10.1142/s0219455412500010, doi:10.1142/s0219455412500010. This article has 17 citations and is from a peer-reviewed journal.

34. (chen2012initialprestressdistribution pages 1-3): YAO CHEN and JIAN FENG. Initial prestress distribution and natural vibration analysis of tensegrity structures based on group theory. International Journal of Structural Stability and Dynamics, 12:213-231, Apr 2012. URL: https://doi.org/10.1142/s0219455412500010, doi:10.1142/s0219455412500010. This article has 17 citations and is from a peer-reviewed journal.

35. (brown2024sampleefficientbayesianoptimisation pages 4-6): Theodore Brown, Alexandru Cioba, and Ilija Bogunovic. Sample-efficient bayesian optimisation using known invariances. ArXiv, Oct 2024. URL: https://doi.org/10.48550/arxiv.2410.16972, doi:10.48550/arxiv.2410.16972. This article has 9 citations.

36. (brown2024sampleefficientbayesianoptimisation pages 6-8): Theodore Brown, Alexandru Cioba, and Ilija Bogunovic. Sample-efficient bayesian optimisation using known invariances. ArXiv, Oct 2024. URL: https://doi.org/10.48550/arxiv.2410.16972, doi:10.48550/arxiv.2410.16972. This article has 9 citations.

37. (brown2024sampleefficientbayesianoptimisation pages 9-11): Theodore Brown, Alexandru Cioba, and Ilija Bogunovic. Sample-efficient bayesian optimisation using known invariances. ArXiv, Oct 2024. URL: https://doi.org/10.48550/arxiv.2410.16972, doi:10.48550/arxiv.2410.16972. This article has 9 citations.

38. (brown2024sampleefficientbayesianoptimisation pages 27-28): Theodore Brown, Alexandru Cioba, and Ilija Bogunovic. Sample-efficient bayesian optimisation using known invariances. ArXiv, Oct 2024. URL: https://doi.org/10.48550/arxiv.2410.16972, doi:10.48550/arxiv.2410.16972. This article has 9 citations.

39. (eriksson2021highdimensionalbayesianoptimization pages 4-5): David Eriksson and Martin Jankowiak. High-dimensional bayesian optimization with sparse axis-aligned subspaces. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2103.00349, doi:10.48550/arxiv.2103.00349. This article has 297 citations.

40. (eriksson2021highdimensionalbayesianoptimization pages 3-4): David Eriksson and Martin Jankowiak. High-dimensional bayesian optimization with sparse axis-aligned subspaces. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2103.00349, doi:10.48550/arxiv.2103.00349. This article has 297 citations.