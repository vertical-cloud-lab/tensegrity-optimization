# Edison LITERATURE_HIGH — Instron stiffness testing best practices & ASTM standards

- Task ID: `9f68e71e-c552-4333-aa5c-37de18c8eefd`
- Issue: #49
- Job: `LITERATURE_HIGH`
- Status: **success**
- Submitted: 2026-05-15 17:14:18.368392+00:00
- Started: 2026-05-15T17:14:21.924224Z
- Task summary: *Standards, Test Protocols, And Best Practices For Quasi Static Stiffness Testing Of 3D Printed Multimaterial Tensegrity Cells*

> **Note on artifact format.** The PaperQA / Phoenix-class agent for this LITERATURE_HIGH task completed all 8 internal plan objectives and produced its findings as **three structured artifacts** (standards comparison table, first-test protocol checklist, published-analogs table) rather than a single `formatted_answer` string. They are reproduced verbatim below in the order produced. References appear inline as `[paperX]` style cite-keys; the full BibTeX is preserved in the JSON dump under `agent_state[0].state.transition.agent_state.messages[*].content`.

## Plan objectives executed by the agent

- **1.** Search for ASTM/ISO standards applicable to cellular/lattice compression testing, sandwich core testing, and AM-specific standards  *(status: completed)*
- **2.** Search for best practices in Instron testing of soft cellular/lattice structures including machine compliance, preconditioning, Mullins effect in TPU, and stiffness definition  *(status: completed)*
- **3.** Search for published analogs: FFF/3D-printed tensegrity structures, multi-material PETG+TPU prints, energy absorption testing of AM lattices  *(status: completed)*
- **4.** Search for multi-material FFF-specific testing considerations  *(status: completed)*
- **5.** Gibson-Ashby framework and statistical reporting  *(status: completed)*
- **6.** Gather evidence from all retrieved documents to extract specific test parameters, standard details, and protocol recommendations  *(status: completed)*
- **7.** Create artifacts: standards comparison table, first-test protocol checklist, metadata schema, and published analogs table  *(status: completed)*
- **8.** Submit final comprehensive technical brief with all 7 sections plus open questions, properly cited  *(status: in-progress)*


## Artifact 1 (table) — Create a comprehensive standards comparison table for Section 1 of the technical brief. Include columns: Standard Number, Title/Scope, What It Measures, Specimen Geometry Requirements, Crosshead Speed

### Artifact (ID artifact-00)

| Standard Number | Title/Scope | What It Measures | Specimen Geometry Requirements | Crosshead Speed / Strain Rate | Gap vs. Tensegrity Specimens | Normative vs. Informative for AM-tensegrity paper |
|---|---|---|---|---|---|---|
| ASTM D695 | Compressive Properties of Rigid Plastics | Compressive strength, yield, strain at yield, modulus/apparent compressive behavior of rigid plastics | Standard coupon geometry for rigid plastics; intended for bulk, homogeneous specimens rather than open cellular architectures | Method-defined constant crosshead speed tied to specimen geometry/material response; report nominal strain rate and machine used | Good for PETG/PLA bulk coupons only; not directly valid for unit-cell architectures, tendon-dominated compliance, or jointed multi-material specimens. Use as constituent-material bracket, not structural-cell standard | **Normative** for PETG/PLA material-card compression coupons; **informative only** for whole tensegrity cells |
| ISO 604 | Plastics — Determination of Compressive Properties | Compressive stress-strain response and modulus of plastics | Prismatic/cylindrical bulk-plastic specimens with prescribed dimensions and end parallelism; homogeneous material assumption | Constant compression rate specified by standard by specimen type/material | Same gap as D695: appropriate for printed PETG/PLA coupons, not for sparse multi-material cells with large void fraction and mechanism-driven deformation | **Normative** for bulk plastic coupons; **informative only** for unit cells |
| ASTM D1621 | Compressive Properties of Rigid Cellular Plastics | Compressive stress-strain, strength, and apparent modulus of rigid foams/cellular plastics | Minimum specimen commonly interpreted as ~25.4 mm cube in practice for cellular materials; full specimen should be representative through thickness | Constant rate of crosshead motion selected to achieve specified nominal strain-rate regime for foams | Closest analog for single-cell or tiled rigid-dominant lattice/cellular specimens, but your specimens are open, architected, anisotropic, and multi-material rather than stochastic rigid foam. Must report architecture, loading direction, contact area definition, relative density, and any departures from cube geometry | **Normative-adjacent / preferred primary citation** for quasi-static compression of rigid-dominant cellular specimens if adapted and deviations disclosed |
| ASTM D3574 | Flexible Cellular Materials — Slab, Bonded, and Molded Urethane Foams | Flexible foam compression force-deflection, hysteresis, support factor, fatigue, and related cushioning metrics depending on test | Foam blocks/slabs with dimensions tied to specific subtests; intended for flexible foam products rather than architected open cells | Crosshead speed depends on subtest (typically force-deflection/compression-set style procedures with prescribed rates) | Useful analog for TPU-dominant cushioning response and hysteresis, but not directly for discrete tensegrity/lattice cells with rigid struts, nonuniform contact, and joint-slip risk. Must specify which subtest is adapted | **Informative**, especially for later cushioning/energy-absorption phases |
| ASTM D7726 | Standard Test Method for the Effect of Compression on High-Visibility/Protective Padding Materials (protective-material compression analog) | Compression behavior of protective padding/material systems under prescribed loading histories | Product-like padding specimens; geometry depends on protective material format | Standard-specified loading protocol for protective materials; report full test history | Potentially useful for application framing (protective gear), but not geometry-faithful for unit cells. Better for benchmarking later pad-level assemblies than early unit cells | **Informative** |
| ASTM F1614 | Test Method for Shock-Attenuating Properties of Materials Systems for Athletic Footwear / impact-attenuating systems | Shock attenuation / impact response of cushioning materials | Product/material-system specimens sized for impact apparatus, not quasi-static cell coupons | Impact protocol rather than quasi-static crosshead rate | Relevant to later impact/drop-weight campaign and protective-gear motivation, not first-round stiffness tests | **Informative** for roadmap; not primary for current quasi-static stiffness tests |
| ASTM D575 | Rubber Properties in Compression | Compression stress-strain and compressive modulus/apparent stiffness of rubber/elastomers | Cylindrical or button-type rubber specimens with controlled aspect ratio and flat ends | Prescribed crosshead rate for compression of elastomer specimens | Useful for TPU coupon behavior or TPU-dominant subcomponents; not valid for open-cell tensegrity geometry with rigid struts and large internal voids | **Normative** for bulk TPU compression coupons if made; **informative** for cells |
| ISO 7743 | Rubber, Vulcanized or Thermoplastic — Determination of Compression Stress-Strain Properties | Compression stress-strain properties of rubber/elastomers | Standard rubber compression specimen geometries and end conditions | Prescribed compression rate per standard | Same role as D575; useful for TPU constituent behavior but not sufficient for architected multi-material cells | **Normative** for TPU bulk compression coupons; **informative** for cells |
| ASTM C365 / C365M | Flatwise Compressive Properties of Sandwich Cores | Through-thickness compressive modulus, compressive strength, plateau-like response of sandwich core materials | Flatwise-loaded sandwich-core blocks/panels; requires parallel loading faces and representative core footprint | Constant crosshead displacement rate specified by standard for through-thickness compression | Very relevant for 2×2×2 tiled unit cells or panelized repeating-cell specimens loaded through thickness; less natural for isolated single tensegrity prisms unless faced/potted. Need to justify no facesheets or add platens/shims and define effective area carefully | **Normative-adjacent / strong primary analog** for tiled repeating lattices |
| ASTM C297 / C297M | Flatwise Tensile Strength of Sandwich Constructions | Tensile strength normal to sandwich faces; often used to probe core-skin or core integrity | Sandwich specimen bonded to loading blocks; requires faces/adhesive tabs | Tensile loading rate specified by standard | Not a stiffness test, but highly relevant if you need to assess through-thickness tensile integrity of tiled cells or bonded platens / jointed specimens. For your PETG–TPU joints, this is only an analogy unless a bonded sandwich-like subassembly is built | **Informative** now; potentially **normative** for future joint/core integrity subtests |
| ASTM D638 | Tensile Properties of Plastics | Tensile modulus, yield/strength, strain at break of plastics | Dog-bone coupons (e.g., Type I commonly used); for homogeneous plastic coupons | Constant crosshead rate by specimen type/property target; 5 mm/min is common in published AM studies using Type I specimens | Primary standard for PETG/PLA material cards. Must add AM reporting: build orientation, raster, infill, layer height, conditioning, actual cross-section. Not suitable for whole tensegrity cells | **Normative** for PETG/PLA coupons |
| ISO 527 | Plastics — Determination of Tensile Properties | Tensile modulus and strength of plastics | Standard tensile coupons; geometry differs somewhat from ASTM D638 but same role | Prescribed test speed by material/property stage | Equivalent role to D638. Choose one family to avoid mixing methodologies; ASTM D638 is more common in FFF polymer papers from your comparison set | **Normative alternative** to D638; cite one primary family consistently |
| ASTM D412 | Vulcanized Rubber and Thermoplastic Elastomers — Tension | Tensile modulus/stress at set elongations, tensile strength, elongation at break for elastomers/TPU-like materials | Die-cut dumbbell/ring elastomer specimens | Prescribed extension rates for elastomer tests | Best constituent-material standard for TPU 85A tendon coupons. Must report TPU hygroscopy, print orientation, and Mullins/preconditioning deviations for printed specimens | **Normative** for TPU tension coupons |
| ISO 37 | Rubber, Vulcanized or Thermoplastic — Determination of Tensile Stress-Strain Properties | Tensile stress-strain properties of elastomers | Standard dumbbell/ring elastomer coupons | Prescribed extension rates | Same role as D412; choose one family consistently. ASTM D412 is more frequently cited in TPU AM/cellular papers in your analog set | **Normative alternative** to D412 |
| ISO 13314 | Mechanical testing of metals — Ductility testing — Compression test for porous and cellular metals | Compressive proof strength, plateau stress, energy absorption, and modulus-like quantities for porous/cellular materials | Representative porous/cellular specimens; literature practice often uses at least ~8–10 cells in each direction for representativity | Quasi-static compression; published practice commonly 1 mm/min with external displacement sensing and high-rate data logging | Metal-specific but conceptually excellent for architected cellular solids. For polymer tensegrity specimens it is not formally applicable, yet it gives strong language for representative cell count, energy absorption metrics, and cyclic unloading modulus methods | **Informative but highly useful** for architected-cell methodology |
| ISO/ASTM 52900 | Additive manufacturing — General principles — Fundamentals and vocabulary | Terminology and classification; defines AM process language and reporting vocabulary | Not a mechanical test standard | N/A | Essential for consistent terminology (material extrusion, build orientation, feedstock, part orientation), but does not prescribe testing | **Normative for terminology/reporting** |
| ISO/ASTM 52902 | Additive manufacturing — Test artifacts — Geometric capability assessment / test-artifact framework | AM test artifact concepts and machine/process capability assessment | Standardized artifacts rather than mechanical specimens | N/A | Useful for print-capability qualification and documenting machine state before mechanical campaign; not a stiffness test method | **Informative / good practice** |
| ISO/ASTM 52921 | Additive manufacturing — Coordinate systems and test methodologies for orientation reporting | Standardized description of part orientation and location in build volume | Not specimen-shape specific; provides orientation framework | N/A | Critical for FFF anisotropy reporting of PETG struts and TPU tendons. Does not itself define mechanics, but reviewers expect this level of AM metadata | **Normative for AM reporting** |
| ISO/ASTM 52939 | Additive manufacturing — Acceptance tests / machine qualification guidance for polymer powder-bed or process-specific system performance (used as AM quality-framework reference) | Machine acceptance / qualification framework rather than specimen stiffness | Process-specific acceptance artifacts/procedures | N/A | Only indirectly relevant for your FFF campaign; cite if using as broader AM quality-assurance context, but it is not a direct mechanical-test standard for material extrusion stiffness | **Informative** |
| ISO/ASTM 52941 | Additive manufacturing — System performance and process qualification guidance (AM quality assurance / acceptance framework) | Process or machine qualification guidance | Qualification artifacts/process-defined | N/A | As with 52939, useful as QA language for machine readiness and reproducibility, not as the mechanical standard for your tests | **Informative** |
| ASTM E111 | Young’s Modulus, Tangent Modulus, and Chord Modulus | Procedures for extracting modulus from stress-strain data, including tangent/chord definitions and toe-region handling concepts | Requires reliable stress-strain data with verified extensometry | Not a specimen-loading standard; used alongside the underlying mechanical test standard | Extremely relevant for your need to define “stiffness.” Apply to initial linear region or unloading modulus extraction, but disclose that structural cells may not exhibit a long linear elastic region. Use with DIC/extensometer rather than crosshead alone where possible | **Normative** for modulus extraction/reporting logic |
| ASTM E9 | Compression Testing of Metallic Materials at Room Temperature | Compression test practice, fixture qualification, alignment, lubrication, and strain measurement guidance | Cylindrical/prismatic metal specimens; fixture qualification emphasized | Published interlaboratory work used nominal strain rate 0.005 min⁻¹ and extensometer-based strain, not actuator displacement | Not directly applicable to plastics/cells, but highly valuable for platen alignment, toe correction, lubrication, dual extensometers, and fixture qualification. Good source for reporting deviations and compression fixturing discipline | **Informative but strongly recommended** for compression-fixture practice |
| ASTM F2971 | Additive Manufacturing — Reporting Data for Test Specimens Prepared by AM | Standardized reporting of AM specimen fabrication metadata | Applies to all AM test specimens | N/A | Not a mechanics method, but crucial for documenting build orientation, raster, layer height, temperatures, feedstock, post-processing, and specimen traceability | **Normative for AM specimen reporting** |
| Preferred citation pairing | Recommendation when ASTM/ISO overlap | Use ASTM family for coupon mechanics if your lab/test frames/software and most analog papers are ASTM-based; pair with ISO/ASTM 52900 + 52921 + ASTM F2971 for AM reporting | N/A | N/A | For your first paper, a clean combination is: ASTM D638 + ASTM D412 + ASTM D1621 or C365 (adapted) + ASTM E111 + ASTM F2971 + ISO/ASTM 52900/52921; mention ISO equivalents in methods as recognized alternatives | **Recommended citation stack** |
| AM lattice gap statement | Common deviation language to report | Architected multi-material tensegrity specimens are open-cell, anisotropic, mechanism-dominated, and may exhibit joint slip, tendon prestrain effects, and localized contact/toe behavior not assumed by bulk/cellular standards | Report actual measured geometry, mass, relative density, cell count, build orientation, platen condition, preload/contact-find, compliance correction, and displacement source (crosshead vs DIC) | Report commanded crosshead speed and nominal specimen strain rate based on bounding-box height; if using local strain, report that separately | This deviation statement should accompany any adapted standard for the unit-cell tests | **Normative to disclose as deviation language in paper** |


*Table: This table compares the most relevant ASTM, ISO, and ISO/ASTM standards for your first-round quasi-static stiffness campaign. It highlights what each standard actually covers, how well it maps onto multi-material tensegrity-inspired unit cells, and which standards should be treated as primary versus supporting citations.*

Artifact IDs that may be injected into the answer: [artifact-00]

Context IDs that may be cited: [pqac-00000000, pqac-00000001, pqac-00000002, pqac-00000003, pqac-00000004, pqac-00000005, pqac-00000006, pqac-00000007, pqac-00000008, pqac-00000009, pqac-00000010, pqac-00000011, pqac-00000012, pqac-00000013, pqac-00000014, pqac-00000015, pqac-00000016, pqac-00000017, pqac-00000018, pqac-00000019, pqac-00000020, pqac-00000021, pqac-00000022, pqac-00000023, pqac-00000024, pqac-00000025, pqac-00000026, pqac-00000027, pqac-00000028, pqac-00000029, pqac-00000030, pqac-00000031, pqac-00000032, pqac-00000033, pqac-00000034, pqac-00000035, pqac-00000036, pqac-00000037, pqac-00000038, pqac-00000039, pqac-00000040, pqac-00000041, pqac-00000042, pqac-00000043, pqac-00000044, pqac-00000045, pqac-00000046, pqac-00000047, pqac-00000048, pqac-00000049, pqac-00000050, pqac-00000051, pqac-00000052, pqac-00000053]

Status: Paper Count=83 | Relevant Papers=26 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=54 | Current Cost=$0.3163 | Disease-Target Evidence=0

## Artifact 2 (table) — Create a first-test protocol checklist table for Section 3 of the technical brief. This should be a step-by-step checklist that an undergraduate can follow for running the first Instron stiffness test

### Artifact (ID artifact-01)

| Phase | Step | Checklist item | Target / setting | Record in metadata / file | Why / note | Citation |
|---|---:|---|---|---|---|---|
| Pre-Test | 1 | Verify specimen has been conditioned before test | 48 h at 23 °C, 50 % RH | `conditioning_time_h`, `conditioning_temp_C`, `conditioning_RH_pct` | Reduces moisture/history variability in PETG/TPU; aligns with AM polymer coupon practice | (pqac-00000004, pqac-00000031) |
| Pre-Test | 2 | Inspect specimen visually before handling | No obvious warp, cracked struts, delaminated tendons, detached joints | `pretest_visual_status`, `notes` | Reject obviously defective prints before loading | (pqac-00000045, pqac-00000033) |
| Pre-Test | 3 | Assign and confirm unique specimen ID | Use permanent ID on bag + worksheet + CSV | `specimen_id` | Prevents data/design mismatch in later BO loop | (pqac-00000032, pqac-00000037) |
| Pre-Test | 4 | Measure mass | 0.01 g scale; 2 repeated readings if difference >0.02 g, take third and average | `mass_g` | Needed for relative density checks and SEA later | (pqac-00000000, pqac-00000022) |
| Pre-Test | 5 | Measure overall geometry | Calipers, 0.01 mm resolution; measure height and two orthogonal widths at 3 locations each | `height_mm`, `width_x_mm`, `width_y_mm`, `bounding_cube_mm` | Use measured dimensions, not CAD only | (pqac-00000017, pqac-00000022) |
| Pre-Test | 6 | Measure key feature sizes if accessible | Strut diameter and tendon diameter at 3 representative locations | `strut_diameter_mm`, `tendon_diameter_mm` | As-built dimensions can differ from nominal and affect stiffness | (pqac-00000001, pqac-00000022) |
| Pre-Test | 7 | Photograph specimen before test | All faces + top/bottom + isometric, with ruler/scale bar and specimen ID visible | image filenames in `photo_pre_paths` | Supports later failure/joint-slip interpretation | (pqac-00000030, pqac-00000032) |
| Pre-Test | 8 | Verify required print metadata is complete | Confirm print log is attached | `design_family`, `n_bars`, `cell_type`, `strut_material`, `tendon_material`, `joint_type`, `relative_density`, `print_date`, `printer_id`, `nozzle_temp_C`, `bed_temp_C`, `layer_height_mm`, `infill_pct`, `raster_angle_deg`, `build_orientation` | Essential for AM reproducibility/reporting | (pqac-00000037, pqac-00000031) |
| Mounting | 9 | Select load cell and confirm zero/load range | Prefer smallest verified cell that keeps peak load in useful range; if only available, use 5 kN and verify low-load resolution | `load_cell_kN`, `load_cell_serial`, `E4_class_if_known` | Low-load tendon-dominated response is sensitive to poor load resolution | (pqac-00000002, pqac-00000004) |
| Mounting | 10 | Confirm platen condition | Clean flat platens; remove debris; inspect for nicks | `platen_type`, `platen_surface_condition` | Surface condition affects initial contact stiffness | (pqac-00000002, pqac-00000050) |
| Mounting | 11 | Decide whether to use PTFE / low-friction film | Use PTFE film only if barreling/friction suspected; keep choice fixed within a batch | `interface_film_used`, `film_type` | Friction/lubrication changes apparent modulus and yield | (pqac-00000051, pqac-00000048) |
| Mounting | 12 | Center specimen on lower platen | Align projected center of specimen with platen centerline | `mounting_centered_yes_no` | Reduces bending/eccentric loading | (pqac-00000000, pqac-00000051) |
| Mounting | 13 | Check parallelism / alignment | Bring upper platen close without contact; verify specimen top is visually parallel; adjust if needed | `alignment_checked_yes_no` | Non-axial loading biases stiffness | (pqac-00000048, pqac-00000051) |
| Alignment / Contact-Find | 14 | Start data acquisition before contact | Record from before first contact | raw file name in `raw_data_path` | Preserves toe/contact region for later correction | (pqac-00000048, pqac-00000046) |
| Alignment / Contact-Find | 15 | Approach slowly to contact | Crosshead speed 0.5 mm/min until preload threshold reached | `contact_find_speed_mm_min` | Gentle seating limits impact/contact artifact | (pqac-00000002, pqac-00000048) |
| Alignment / Contact-Find | 16 | Set preload / contact criterion | Detect 0.5–1.0 N sustained preload | `preload_N` | Defines test zero consistently for soft specimens | (pqac-00000048, pqac-00000052) |
| Alignment / Contact-Find | 17 | Hold briefly after preload | 3–5 s hold after preload before zeroing displacement | `preload_hold_s` | Lets load settle before zeroing | (pqac-00000052) |
| Alignment / Contact-Find | 18 | Zero displacement at preload | Zero crosshead position at preload; if DIC/video extensometry is used, also define local zero | `zero_method` | Needed for repeatable structural stiffness extraction | (pqac-00000001, pqac-00000052) |
| Preconditioning | 19 | Run preconditioning cycles | 5 cycles to 5 % nominal strain at 1 mm/min | `preconditioning_cycles`, `preconditioning_strain_pct`, `preconditioning_speed_mm_min` | TPU and elastomeric systems show first-cycle softening/hysteresis/history effects | (pqac-00000010, pqac-00000011) |
| Preconditioning | 20 | Pause between cycles | 30 s between cycles | `preconditioning_pause_s` | Improves comparability of cyclic response | (pqac-00000011, pqac-00000012) |
| Preconditioning | 21 | Watch live force–displacement trace during cycling | Look for settling after first cycle and any sudden drops/clicks | `preconditioning_observation`, `notes` | Helps identify joint slip versus normal Mullins-like behavior | (pqac-00000033, pqac-00000036) |
| Preconditioning | 22 | Stop and flag if damage occurs during preconditioning | Abort if visible joint tearing, tendon detachment, or force drop >20 % at same displacement | `abort_reason` if applicable | First stiffness run should not consume specimen in preconditioning | (pqac-00000033, pqac-00000045) |
| Monotonic Stiffness Test | 23 | Set main loading rate | 1 mm/min constant crosshead speed | `crosshead_speed_mm_min` | Matches common quasi-static lattice practice | (pqac-00000000, pqac-00000002) |
| Monotonic Stiffness Test | 24 | Load specimen in compression | Load to 15–20 % nominal strain, unless early instability/slip occurs | `max_nominal_strain_pct`, `termination_reason` | First run should characterize small-strain stiffness without going to densification | (pqac-00000015, pqac-00000038) |
| Monotonic Stiffness Test | 25 | Unload at same rate | 1 mm/min back to preload or near-zero force | `unload_speed_mm_min` | Enables hysteresis and unloading stiffness estimation | (pqac-00000000, pqac-00000038) |
| Monotonic Stiffness Test | 26 | Record full force–displacement cycle | Minimum 10 Hz; prefer higher if available | `sample_rate_Hz` | Required for accurate slope and loop-area calculations | (pqac-00000001, pqac-00000000) |
| Monotonic Stiffness Test | 27 | If available, record local deformation optically | Video gauge / DIC on specimen or platen markers | `optical_measurement_used`, `optical_file_path` | Crosshead displacement includes frame compliance; optical data improves low-strain stiffness | (pqac-00000001, pqac-00000030) |
| Monotonic Stiffness Test | 28 | Note any audible/visible events during loading | Slip, crack, pop, tendon whitening, PETG crack, platen rocking | `event_log` | Sudden events can mark joint failure, not material nonlinearity | (pqac-00000032, pqac-00000033) |
| Monotonic Stiffness Test | 29 | Compute provisional stiffness values after run | Tangent stiffness from chosen linear window; secant stiffness at fixed strain; effective modulus if desired | `k_tangent_N_mm`, `k_secant_N_mm`, `E_effective_MPa`, `strain_window_used` | Report structural stiffness and be explicit about strain window | (pqac-00000046, pqac-00000038) |
| Monotonic Stiffness Test | 30 | Compute hysteresis metrics after run | Loop area / loading area or equivalent hysteresis ratio | `hysteresis_ratio` | Useful for TPU-dominant response and later cushioning correlation | (pqac-00000011, pqac-00000010) |
| Post-Test | 31 | Photograph specimen immediately after test | Same views as pre-test, include any damaged joint close-ups | image filenames in `photo_post_paths` | Supports diagnosis of slip, delamination, or buckling mode | (pqac-00000030, pqac-00000045) |
| Post-Test | 32 | Inspect joints and members | Check PETG–TPU interfaces, tendon necking, torn anchors, cracked struts, permanent set | `posttest_failure_mode`, `permanent_set_mm`, `notes` | Critical because interface integrity is an experimental unknown | (pqac-00000033, pqac-00000034) |
| Post-Test | 33 | Mark specimen disposition | Keep / retest / destructive follow-up / discard | `specimen_disposition` | Maintains traceability through campaign | (pqac-00000045) |
| Data Export | 34 | Export raw CSV immediately | Include at minimum `time_s`, `crosshead_mm`, `force_N` | `csv_file_path` | Minimum machine-data package | (pqac-00000001, pqac-00000002) |
| Data Export | 35 | Include derived columns if available | `nominal_strain`, `nominal_stress_kPa_or_MPa`, `cycle_index`, `event_flag` | `derived_csv_path` | Simplifies downstream analysis and BO ingestion | (pqac-00000038, pqac-00000023) |
| Data Export | 36 | Save metadata sidecar file | JSON/YAML/CSV row with all specimen + test fields | `metadata_file_path` | Clean handoff to BoTorch/Ax and later statistics | (pqac-00000005, pqac-00000021) |
| Data Export | 37 | Required BO-facing metadata schema | Capture: `specimen_id`, `design_family`, `n_bars`, `cell_type`, `bounding_cube_mm`, `strut_diameter_mm`, `tendon_diameter_mm`, `strut_material`, `tendon_material`, `joint_type`, `relative_density`, `mass_g`, `print_date`, `printer_id`, `nozzle_temp_C`, `bed_temp_C`, `layer_height_mm`, `infill_pct`, `raster_angle_deg`, `build_orientation`, `test_date`, `crosshead_speed_mm_min`, `preload_N`, `k_tangent_N_mm`, `k_secant_N_mm`, `E_effective_MPa`, `peak_force_N`, `strain_at_peak`, `SEA_J_g`, `hysteresis_ratio`, `notes` | All listed fields | These fields connect design, process, and response for surrogate modeling | (pqac-00000023, pqac-00000037) |
| Data Export | 38 | Backup and review before next specimen | Verify raw curve opens, metadata row is complete, images saved, filenames match specimen ID | `qc_checked_by`, `qc_time` | Prevents irreversible data loss during batch testing | (pqac-00000050, pqac-00000037) |


*Table: This table gives a step-by-step first-run quasi-static stiffness protocol for multi-material tensegrity specimens, including pre-test setup, loading sequence, and data capture. It also embeds the minimum metadata schema needed to support later Bayesian optimization of stiffness and energy-absorption responses.*

Artifact IDs that may be injected into the answer: [artifact-00, artifact-01]

Context IDs that may be cited: [pqac-00000000, pqac-00000001, pqac-00000002, pqac-00000003, pqac-00000004, pqac-00000005, pqac-00000006, pqac-00000007, pqac-00000008, pqac-00000009, pqac-00000010, pqac-00000011, pqac-00000012, pqac-00000013, pqac-00000014, pqac-00000015, pqac-00000016, pqac-00000017, pqac-00000018, pqac-00000019, pqac-00000020, pqac-00000021, pqac-00000022, pqac-00000023, pqac-00000024, pqac-00000025, pqac-00000026, pqac-00000027, pqac-00000028, pqac-00000029, pqac-00000030, pqac-00000031, pqac-00000032, pqac-00000033, pqac-00000034, pqac-00000035, pqac-00000036, pqac-00000037, pqac-00000038, pqac-00000039, pqac-00000040, pqac-00000041, pqac-00000042, pqac-00000043, pqac-00000044, pqac-00000045, pqac-00000046, pqac-00000047, pqac-00000048, pqac-00000049, pqac-00000050, pqac-00000051, pqac-00000052, pqac-00000053]

Status: Paper Count=83 | Relevant Papers=26 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=54 | Current Cost=$0.3163 | Disease-Target Evidence=0

## Artifact 3 (table) — Create a published analogs table for Section 6, listing 10-12 of the closest published papers to the multi-material tensegrity/lattice compression testing campaign. For each paper include columns: Aut

### Artifact (ID artifact-02)

| Author / Year | Journal / DOI | Specimen Description | Materials | Standard Cited | Machine / Crosshead Speed | Key Stiffness / EA Results | Notable Deviations / Caveats |
|---|---|---|---|---|---|---|---|
| Bauer et al. 2021 | *Advanced Materials* / 10.1002/adma.202005647 | 3D space-tileable tensegrity metamaterials, 6×6×6 cells, truncated-octahedron-derived architecture; compared against octet and Kelvin lattices | IP-Dip polymer via TPP-DLW | No ASTM/ISO mechanical standard stated; custom in situ compression with DIC | Alemnis nanoindenter in SEM/FIB; constant strain rate 0.01 s⁻¹ | Defined E as max linear slope, σy by 0.2% offset, plateau stress averaged 20–40% strain, absorbed energy by stress–strain integral; tensegrity showed up to ~13× energy absorption vs octet experimentally and retained load-bearing to densification, with ηd > 90% | Highly relevant tensegrity analog, but microscale TPP specimens and custom setup differ strongly from FFF macro-specimens; not standard-based (pqac-00000038, pqac-00000039, pqac-00000040, pqac-00000041) |
| Pajunen et al. 2019 | *Materials & Design* / 10.1016/j.matdes.2019.107966 | 3D-printable tensegrity-inspired unit cells (~48.3 mm tall), fixed-jointed, pin-jointed, and spherically-jointed variants | SLS PA2200 polyamide; cited E ≈ 1.29 GPa, σy ≈ 29.1 MPa | ASTM D638 for constituent tensile characterization; compression itself not tied to a named ASTM standard | Instron E3000; displacement control; crosshead speed not reported in retrieved excerpts | Pin-jointed geometry showed initial stiffness about 10 kPa and buckling near 0.3 strain; modified geometry increased initial stiffness to 48 kPa; normalized strain energy per mass increased ~3× for one redesign and ~1.5× for spherically-jointed design | One of the closest architecture analogs, but constituent material and process differ from PETG/TPU FFF; missing crosshead-speed reporting is a reproducibility gap (pqac-00000015, pqac-00000018, pqac-00000019) |
| Lee et al. 2020 | *Science Robotics* / 10.1126/scirobotics.aay9024 | 3D-printed programmable tensegrity structures for soft robotics; monolithic tendon networks with rigid struts | Multi-material smart-material tensegrity system | No specific ASTM/ISO testing standard recovered in retrieved excerpts | Compression tests reported in paper, but machine/speed details not available in retrieved excerpts | Demonstrated programmable mechanics in printed tensegrity architectures; useful architecture/process analog | Very relevant conceptually for co-printed tensegrity, but retrieved evidence lacks enough test-protocol detail for direct protocol borrowing (paper identified in search results) |
| Sabouni-Zawadzka & Gilewski 2024 | journal not fully resolved in retrieved record / DOI not recovered in retrieved excerpt | Single-cell 4-strut simplex tensegrity-inspired modules, inscribed in 20–50 mm cubes; free upper-base rotation allowed | Multiple AM materials screened; SLA, PolyJet, SLS initially; SLS rejected as too brittle | No explicit ASTM/ISO standard cited in retrieved excerpts | Instron 5567; displacement control at 2 mm/min; force accuracy 0.5 N | Results reported as mean force–displacement curves with SD for groups of seven; strong dependence on parent-material elongation at break and specimen size; observed post-critical strut behavior | Excellent mesoscale tensegrity analog; explicit acknowledgment that manufacturing inaccuracies and free-deformation constraints strongly affect results; no standard cited and no modulus number recovered in excerpt (pqac-00000016, pqac-00000043, pqac-00000045) |
| Bates et al. 2016 | *Materials & Design* / 10.1016/j.matdes.2016.08.062 | FFF TPU hexagonal honeycombs, compressed in different directions, repeated to densification | NinjaFlex and SemiFlex TPU | ASTM D412 for tensile coupons; compression not tied to a named ASTM in retrieved excerpt | Instron 3343 (1 kN) and Shimadzu (10 kN); constant strain rates 0.03, 0.095, 0.3 s⁻¹; minimum 10 Hz acquisition; video gauge used | Tensile low-strain moduli: 26.5 MPa (NinjaFlex) and 89.5 MPa (SemiFlex); study emphasizes stress–strain regions and repeated-energy-absorption behavior | Strong TPU cushioning analog; not tensegrity, but very useful for preconditioning/hysteresis and optical displacement practice; specimen geometry intentionally chosen with L > H to avoid buckling (pqac-00000001, pqac-00000003, pqac-00000020) |
| Rossiter et al. 2020 | *3D Printing and Additive Manufacturing* / 10.1089/3dp.2019.0030 | Material-extruded truncated-octahedron lattices; factorial study on cell width, strut CSA, orientation, filleting | Nylon via material extrusion | Compression program described, but no named standard recovered in retrieved excerpt | Instron 3366; constant strain rate 1.0 s⁻¹ | Strut CSA, cell width, and their interaction had largest effects on plateau stress and energy capacity | Close topology analog for truncated-octahedral cells, but much higher strain rate than typical quasi-static stiffness tests; likely more useful for later energy-absorption studies than initial stiffness work (search result summary) |
| Arifvianto et al. 2022 | *Progress in Additive Manufacturing* / 10.1007/s40964-022-00295-6 | FFF sandwich-structured PLA/TPU multi-material parts; interface and layered architecture focus | PLA / TPU | Mechanical-property study; specific standard for excerpted hardness/interface observations not recovered here | Machine details not recovered in excerpt used here | Showed weak interfacial bonding, torn interfaces, and TPU delamination-like behavior; raster configuration not strongly significant for hardness in their tested cases | Important multi-material analog for interface failure interpretation, even though geometry is not a tensegrity/lattice cell and loading mode differs (pqac-00000033) |
| Maskery et al. 2015 | *Experimental Mechanics* / 10.1007/s11340-015-0021-5 | BCC Ti-6Al-4V latticed tensile/compression specimens with varying cell size at fixed relative density | SLM Ti-6Al-4V | Gibson–Ashby framework used; machine-compliance considerations discussed; no polymer standard | Instron 5969; detailed speed not recovered in excerpt here | Relative variables defined as E*/Es, ρ*/ρs, σU*/σUs; highlighted modulus drop with increasing cell size and the importance of unit-cell count in gauge region | Not polymer or multi-material, but canonical for nondimensional stiffness scaling and specimen-size effects in lattices; very useful for your reporting framework (pqac-00000023, pqac-00000028) |
| Solyaev et al. 2023 | *Scientific Reports* / 10.1038/s41598-023-41614-3 | 3D-printed quasi-cubic polymer lattice metamaterials with asymmetric joints | Polymeric printed lattice | Compression used flat platforms per ASTM E9; compliance correction per ASTM D790; impact per ASTM D6110 | Instron 5969; 1 mm/min; 2.5 kHz acquisition; 50 kN load cell | Compression run to 50% strain or failure; yield from 0.2% offset; toughness from area under stress–strain curve | Very useful practical analog for Instron setup, compliance correction, and reporting conventions, but load cell was oversized for your likely force range (pqac-00000002, pqac-00000014) |
| Raghavendra et al. 2021 | *Forces in Mechanics* / 10.1016/j.finmec.2020.100007 | Regular, irregular, and random AM cellular materials; nominal vs real geometry study with µCT-based models | LB-PBF Ti-6Al-4V cellular specimens | ISO 13314:2011 for compression; ASTM D638 not relevant here | Compression at 1 mm/min; 1 kHz data sampling; LVDT for compression displacement; cyclic loading–unloading used for modulus | Emphasized representative cell count (~8–10 cells in each direction), unloading-based Young’s modulus, and strong influence of as-built porosity on stiffness and yield | Excellent methodological analog for representative specimen size, external displacement sensing, and as-built geometry correction; material/process differ from FFF polymers (pqac-00000000, pqac-00000022) |
| Pahari 2024 | journal not fully resolved in retrieved record / DOI not recovered in retrieved excerpt | Multi-material FFF lap-joint/interface study with full-field deformation mapping | PLA, PETG, PETG+CF; interface-focused | Designed around an FRP lap-shear standard; references ASTM D5868 and ISO 21194 in bibliography discussion | Instron ElectroPuls E3000 (3 kN) for shear; 2D DIC with front and side imaging | Main contribution is interface-strain mapping and non-destructive detection of heterogeneous deformation and failure localization | Not a stiffness paper, but among the best analogs for detecting interfacial slip/slip-initiation using DIC rather than mislabeling it as material nonlinearity (pqac-00000030, pqac-00000032, pqac-00000035) |
| Habib 2024 | Thesis / 10.25916/sut.26281492 | 5×5×5 arrays of 10 mm unit cells at 15% relative density for wearable impact protection; multiple lattice topologies | HP PA12 via MJF | ASTM D638-14 for constituent tensile characterization | MTS Criterion Electromechanical Universal Test System Model 43 for tensile coupons with optical extensometer; compression speed not recovered in excerpt | Used quasi-static compression plus FEA to compare topologies for specific energy absorption and transmitted stress; highlighted instability from buckling-dominated topologies | Good application analog for protective cushioning and relative-density-controlled lattice screening; retrieved excerpt lacks compression machine speed/details (pqac-00000005, pqac-00000021) |


*Table: This table summarizes the closest published experimental analogs to the planned multi-material tensegrity/lattice Instron campaign. It is useful for borrowing test parameters, identifying reporting norms, and modeling justified deviations from standards.*

Artifact IDs that may be injected into the answer: [artifact-00, artifact-01, artifact-02]

Context IDs that may be cited: [pqac-00000000, pqac-00000001, pqac-00000002, pqac-00000003, pqac-00000004, pqac-00000005, pqac-00000006, pqac-00000007, pqac-00000008, pqac-00000009, pqac-00000010, pqac-00000011, pqac-00000012, pqac-00000013, pqac-00000014, pqac-00000015, pqac-00000016, pqac-00000017, pqac-00000018, pqac-00000019, pqac-00000020, pqac-00000021, pqac-00000022, pqac-00000023, pqac-00000024, pqac-00000025, pqac-00000026, pqac-00000027, pqac-00000028, pqac-00000029, pqac-00000030, pqac-00000031, pqac-00000032, pqac-00000033, pqac-00000034, pqac-00000035, pqac-00000036, pqac-00000037, pqac-00000038, pqac-00000039, pqac-00000040, pqac-00000041, pqac-00000042, pqac-00000043, pqac-00000044, pqac-00000045, pqac-00000046, pqac-00000047, pqac-00000048, pqac-00000049, pqac-00000050, pqac-00000051, pqac-00000052, pqac-00000053]

Status: Paper Count=83 | Relevant Papers=26 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=54 | Current Cost=$0.3163 | Disease-Target Evidence=0


---

## Raw source / reference dumps from the agent trajectory

(Captured from intermediate reasoning messages; may contain duplicates.)

```bibtex


---

Retrieved Papers:
## 1. Assessing the Design and Compressive Performance of Material Extruded Lattice Structures.
Valid Text Names:
'rossiter2020assessingthedesign pages 1-2', 'rossiter2020assessingthedesign pages 2-3', 'rossiter2020assessingthedesign pages 3-5', 'rossiter2020assessingthedesign pages 5-6', 'rossiter2020assessingthedesign pages 6-8', 'rossiter2020assessingthedesign pages 8-9', 'rossiter2020assessingthedesign pages 9-9'

BibTex:
@article{rossiter2020assessingthedesign,
    author = "Rossiter, Jayme D. and Johnson, Andrew A. and Bingham, Guy A.",
    title = "Assessing the Design and Compressive Performance of Material Extruded Lattice Structures.",
    year = "2020",
    journal = "3D printing and additive manufacturing",
    volume = "7 1",
    pages = "19-27",
    month = "Feb",
    doi = "10.1089/3dp.2019.0030",
    url = "https://doi.org/10.1089/3dp.2019.0030",
    publisher = "Mary Ann Liebert Inc",
    issue = "1",
    issn = "2329-7662"
}


Abstract:
With additive manufacturing increasingly being embraced in the area of sports technology, focus has shifted toward cellular structures for impact protection. Periodic lattice structures can be tailored for a specific response by modifying the geometry of individual cells, with the structure capable of being modified to conform around a given body. However, the effect of modifying specific design characteristics within a lattice and the interrelationships between them are not well understood. This study examines five geometric design variables: cell width, strut cross-sectional area (CSA), strut shape, cell orientation, and joint filleting, and their effect on the compressive behavior of a lattice structure. Truncated octahedron lattices were manufactured using nylon through the process of material extrusion and tested under compression at a constant strain rate of 1.0 s-1. Design of experiments was utilized to analyze the results by implementing a 2(5-1) factorial design. Results indicated that the strut CSA, cell width, and interaction between the two design characteristics had the largest effects on the plateau stress of the lattice and its energy capacity.

Relevant Snippet:
… their effect on the compressive behavior of a lattice structure. Truncated octahedron lattices were … All compression tests were performed using an Instron 3366 Dual Column Universal …


---

## 2. Mechanical properties of hybrid structures generated by additively manufactured triply periodic minimal surface structures and foam
Valid Text Names:
'miralbes2023mechanicalpropertiesofa pages 1-6', 'miralbes2023mechanicalpropertiesofa pages 6-10', 'miralbes2023mechanicalpropertiesofa pages 10-14', 'miralbes2023mechanicalpropertiesofa pages 14-20', 'miralbes2023mechanicalpropertiesofa pages 20-26', 'miralbes2023mechanicalpropertiesofa pages 26-29', 'miralbes2023mechanicalpropertiesofa pages 29-29'

BibTex:
@article{miralbes2023mechanicalpropertiesof,
    author = "Miralbes, R. and Pascual, F.J. and Ranz, D. and Gomez, J.A.",
    title = "Mechanical properties of hybrid structures generated by additively manufactured triply periodic minimal surface structures and foam",
    year = "2023",
    journal = "Mechanics of Advanced Materials and Structures",
    volume = "30",
    pages = "4317-4328",
    month = "Jul",
    doi = "10.1080/15376494.2022.2092797",
    url = "https://doi.org/10.1080/15376494.2022.2092797",
    publisher = "Informa UK Limited",
    issue = "21",
    issn = "1537-6494"
}


Abstract:
Abstract Triply periodic minimal surface (TPMS) structures are adequate substitutes for some foams because of the high ratio of their mechanical properties and weights; furthermore, they allow the possibility of tailoring final structures. The internal space of TPMSs can be filled with low-density foam to enhance the mechanical properties and energy absorption capabilities of these structures. This study focused on the comparative analysis of non-hybrid and hybrid TPMSs. The specimens were tested under compression quasi-static loads, and their mechanical properties, capability to absorb energy per unit weight and per unit volume, ideality, efficiency, total efficiency, weight, and failure mechanisms were analyzed.

Relevant Snippet:
… ] that is centered in strut lattice structures and observed that … under compression loads according to ASTM D1621 (Table A1 … to a cellular foam, such as EPS, the ASTM D3574 was used. …


---

## 3. Analysis of the capability of cork and cork agglomerates to absorb multiple compressive quasi-static loading cycles
Valid Text Names:
'buil2021analysisofthe pages 1-2', 'buil2021analysisofthe pages 2-3', 'buil2021analysisofthe pages 3-6', 'buil2021analysisofthe pages 6-10', 'buil2021analysisofthe pages 10-13', 'buil2021analysisofthe pages 13-14', 'buil2021analysisofthe pages 14-14'

BibTex:
@article{buil2021analysisofthe,
    author = "Buil, Ramon Miralbes and Angulo, David Ranz and Ivens, Jan",
    title = "Analysis of the capability of cork and cork agglomerates to absorb multiple compressive quasi-static loading cycles",
    year = "2021",
    journal = "European Journal of Wood and Wood Products",
    volume = "79",
    pages = "1195-1208",
    month = "Feb",
    doi = "10.1007/s00107-021-01658-6",
    url = "https://doi.org/10.1007/s00107-021-01658-6",
    publisher = "Springer Science and Business Media LLC",
    issue = "5",
    issn = "0018-3768"
}


Relevant Snippet:
… of the original material (for instance, in EPS foam and the polystyrene material). In the … is a rigid cellular plastic, the more suitable standards are ISO 844 and ASTM D1621. It must …


---

## 4. Characterization of cork and cork agglomerates under compressive loads by means of energy absorption diagrams
Valid Text Names:
'miralbes2021characterizationofcork pages 1-2', 'miralbes2021characterizationofcork pages 2-3', 'miralbes2021characterizationofcork pages 3-6', 'miralbes2021characterizationofcork pages 6-8', 'miralbes2021characterizationofcork pages 8-9', 'miralbes2021characterizationofcork pages 9-10', 'miralbes2021characterizationofcork pages 10-12', 'miralbes2021characterizationofcork pages 12-13', 'miralbes2021characterizationofcork pages 13-13'

BibTex:
@article{miralbes2021characterizationofcork,
    author = "Miralbes, Ramon and Ranz, David and Ivens, Jan and Gomez, Jose Antonio",
    title = "Characterization of cork and cork agglomerates under compressive loads by means of energy absorption diagrams",
    year = "2021",
    journal = "European Journal of Wood and Wood Products",
    volume = "79",
    pages = "719-731",
    month = "Nov",
    doi = "10.1007/s00107-020-01625-7",
    url = "https://doi.org/10.1007/s00107-020-01625-7",
    publisher = "Springer Science and Business Media LLC",
    issue = "3",
    issn = "0018-3768"
}


Relevant Snippet:
… diagrams are commonly used for polymeric foams and 3D-printed lattice structures, these types of … In ASTM D1621, the minimum specimen is a 25.4 mm cube, while in ASTM D3574, the …


---

## 5. Simulation of high strain rate deformation in structural polymeric foam: innovation report.
Valid Text Names:
'carnegie2016simulationofhigh pages 1-7', 'carnegie2016simulationofhigh pages 7-10', 'carnegie2016simulationofhigh pages 10-12', 'carnegie2016simulationofhigh pages 12-16', 'carnegie2016simulationofhigh pages 16-21', 'carnegie2016simulationofhigh pages 21-25', 'carnegie2016simulationofhigh pages 25-29', 'carnegie2016simulationofhigh pages 29-33', 'carnegie2016simulationofhigh pages 33-38', 'carnegie2016simulationofhigh pages 38-42', 'carnegie2016simulationofhigh pages 42-49', 'carnegie2016simulationofhigh pages 49-55', 'carnegie2016simulationofhigh pages 55-60', 'carnegie2016simulationofhigh pages 60-65', 'carnegie2016simulationofhigh pages 65-71', 'carnegie2016simulationofhigh pages 71-77', 'carnegie2016simulationofhigh pages 77-84', 'carnegie2016simulationofhigh pages 84-90', 'carnegie2016simulationofhigh pages 90-94', 'carnegie2016simulationofhigh pages 94-99', 'carnegie2016simulationofhigh pages 99-105', 'carnegie2016simulationofhigh pages 105-110', 'carnegie2016simulationofhigh pages 110-114', 'carnegie2016simulationofhigh pages 114-119', 'carnegie2016simulationofhigh pages 119-123', 'carnegie2016simulationofhigh pages 123-127', 'carnegie2016simulationofhigh pages 127-129'

BibTex:
@article{carnegie2016simulationofhigh,
    author = "Carnegie, CR",
    title = "Simulation of high strain rate deformation in structural polymeric foam: innovation report.",
    year = "2016",
    journal = "Unknown journal"
}


Relevant Snippet:
… rate (VHS) testing rig; each used to understand the effect of compression testing at a range of … For closed cell foam a significant increase in compressive strength during high strain rate …


Unobtainable Papers:
Enrique Cuan-Urquizo and Rafael Guerra Silva. Fused filament fabrication of cellular, lattice and porous mechanical metamaterials: a review. Virtual and Physical Prototyping, Jul 2023. URL: https://doi.org/10.1080/17452759.2023.2224300, doi:10.1080/17452759.2023.2224300.
Maria C. Bedoya, J. William Restrepo, Luis V. Wilches, and Johnnatan Rodriguez. Cellular structures analysis under compression test. Polymers, 17:1476, May 2025. URL: https://doi.org/10.3390/polym17111476, doi:10.3390/polym17111476.
A novel framework for design-property decision-making in polymer lattices when controlling for printed mass
Neerakallu Dasappa Shivakumar and Anindya Deb. Dependence of the mechanical properties of rigid pu foam on density. Journal of Reinforced Plastics and Composites, 41:355-363, Jan 2022. URL: https://doi.org/10.1177/07316844211051737, doi:10.1177/07316844211051737.
Rafael Guerra Silva. Characterization of additively manufactured architected cellular polymers: influence of specimen size and cell type on compressive behavior. Results in Engineering, 26:105001, Jun 2025. URL: https://doi.org/10.1016/j.rineng.2025.105001, doi:10.1016/j.rineng.2025.105001.
Mohammad Javad Hooshmand and Mohammad Abu Hasan Khondoker. Mechanical characterization of ultra-violet-curable resin-based polymer foams containing triply periodic minimal surface lattice structures. 1st International Conference on Industrial, Manufacturing, and Process Engineering (ICIMP-2024), pages 55, Oct 2024. URL: https://doi.org/10.3390/engproc2024076055, doi:10.3390/engproc2024076055.
Alvin Dio Nugroho, Herianto, Daffa Alandro, and Muhammad Akhsin Muflikhun. Additively manufactured lattice and sandwich structure consists of hybrid gfrp–pla pu–graphite-foam for lightweight structure applications. Progress in Additive Manufacturing, 10:1201-1216, Jun 2025. URL: https://doi.org/10.1007/s40964-024-00699-6, doi:10.1007/s40964-024-00699-6.

Artifact IDs that may be injected into the answer: []

Context IDs that may be cited: []

Status: Paper Count=29 | Relevant Papers=0 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=0 | Current Cost=$0.0000 | Disease-Target Evidence=0

---

Retrieved Papers:
## 1. Design and impact response of 3D-printable tensegrity-inspired structures
Valid Text Names:
'pajunen2019designandimpact pages 1-2', 'pajunen2019designandimpact pages 2-3', 'pajunen2019designandimpact pages 3-4', 'pajunen2019designandimpact pages 4-5', 'pajunen2019designandimpact pages 5-7', 'pajunen2019designandimpact pages 7-8', 'pajunen2019designandimpact pages 8-9', 'pajunen2019designandimpact pages 9-9'

BibTex:
@article{pajunen2019designandimpact,
    author = "Pajunen, Kirsti and Johanns, Paul and Pal, Raj Kumar and Rimoli, Julian J. and Daraio, Chiara",
    title = "Design and impact response of 3D-printable tensegrity-inspired structures",
    year = "2019",
    journal = "Materials \& Design",
    volume = "182",
    pages = "107966",
    month = "Nov",
    doi = "10.1016/j.matdes.2019.107966",
    url = "https://doi.org/10.1016/j.matdes.2019.107966",
    publisher = "Elsevier BV",
    issn = "0264-1275"
}


Relevant Snippet:
… with superior mechanical properties. However, traditional fabrication methods for tensegrity … under severe deformation, high elastic strain energy absorption, and load-limitation. This …


---

## 2. Mechanical and energy absorption properties of 3D-printed honeycomb structures with Voronoi tessellations
Valid Text Names:
'ahmed2023mechanicalandenergy pages 1-2', 'ahmed2023mechanicalandenergy pages 2-3', 'ahmed2023mechanicalandenergy pages 3-4', 'ahmed2023mechanicalandenergy pages 4-8', 'ahmed2023mechanicalandenergy pages 8-9', 'ahmed2023mechanicalandenergy pages 9-13', 'ahmed2023mechanicalandenergy pages 13-14', 'ahmed2023mechanicalandenergy pages 14-15', 'ahmed2023mechanicalandenergy pages 15-15'

BibTex:
@article{ahmed2023mechanicalandenergy,
    author = "Ahmed, Abdelrahman Mohamed Ragab M. and Mahdi, Elsadig and Oosterhuis, Kas and Dean, Aamir and Cabibihan, John-John",
    title = "Mechanical and energy absorption properties of 3D-printed honeycomb structures with Voronoi tessellations",
    year = "2023",
    journal = "Frontiers in Mechanical Engineering",
    volume = "9",
    month = "Jun",
    doi = "10.3389/fmech.2023.1204893",
    url = "https://doi.org/10.3389/fmech.2023.1204893",
    publisher = "Frontiers Media SA",
    issn = "2297-3079"
}


Abstract:
3D printing technology is the new frontier in building construction. It is especially useful for making small structures within a short period. Full construction, including interior partitions and exterior façades, can be achieved with this technology. This paper proposes a parametric Voronoi tessellations model for quickly generating and fabricating 3D-printed hexagonal honeycomb partitions for interior design. Comprehensive experimental testing was conducted to characterize the mechanical properties and investigate the energy absorption characteristics of the proposed 3D-printed hexagonal honeycomb while comparing it to alternative hexagonal honeycomb structures. The tests included tensile testing (ASTM-D638) of the printed Polylactic Acid (PLA) material, especially with the almost total absence of conducted research that reported mechanical properties for 3D printed material with low infill percentages such as 10%. In addition, an in-plane quasi-static axial compression testing of the lightweight honeycomb structures was also conducted on the printed structure with the same low infill percentage. Compared to non-Voronoi honeycomb structures, the Voronoi honeycomb resulted in superior mechanical and energy absorption properties with energy absorption values ranging from 350 to 435 J and crash force efficiency being 1.42 to 1.65.

Relevant Snippet:
… research that reported mechanical properties for 3D printed material with low infill percentages such as 10%. In addition, an in-plane quasi-static axial compression testing of the …


---

## 3. 3D-printed programmable tensegrity for soft robotics
Valid Text Names:
'lee20203dprintedprogrammabletensegrity pages 1-2', 'lee20203dprintedprogrammabletensegrity pages 1-1', 'lee20203dprintedprogrammabletensegrity pages 2-3', 'lee20203dprintedprogrammabletensegrity pages 3-4', 'lee20203dprintedprogrammabletensegrity pages 4-4', 'lee20203dprintedprogrammabletensegrity pages 4-5', 'lee20203dprintedprogrammabletensegrity pages 5-6', 'lee20203dprintedprogrammabletensegrity pages 6-6', 'lee20203dprintedprogrammabletensegrity pages 6-7', 'lee20203dprintedprogrammabletensegrity pages 7-8', 'lee20203dprintedprogrammabletensegrity pages 8-9', 'lee20203dprintedprogrammabletensegrity pages 9-10', 'lee20203dprintedprogrammabletensegrity pages 10-11', 'lee20203dprintedprogrammabletensegrity pages 10-10', 'lee20203dprintedprogrammabletensegrity pages 11-12', 'lee20203dprintedprogrammabletensegrity pages 12-12'

BibTex:
@article{lee20203dprintedprogrammabletensegrity,
    author = "Lee, Hajun and Jang, Yeonwoo and Choe, Jun Kyu and Lee, Suwoo and Song, Hyeonseok and Lee, Jin Pyo and Lone, Nasreena and Kim, Jiyun",
    title = "3D-printed programmable tensegrity for soft robotics",
    year = "2020",
    journal = "Science Robotics",
    volume = "5",
    month = "Aug",
    doi = "10.1126/scirobotics.aay9024",
    url = "https://doi.org/10.1126/scirobotics.aay9024",
    publisher = "American Association for the Advancement of Science (AAAS)",
    issue = "45",
    issn = "2470-9476"
}


Abstract:
Additive manufacturing enables the integration of smart materials into tensegrity metamaterials for functional soft systems. Tensegrity structures provide both structural integrity and flexibility through the combination of stiff struts and a network of flexible tendons. These structures exhibit useful properties: high stiffness-to-mass ratio, controllability, reliability, structural flexibility, and large deployment. The integration of smart materials into tensegrity structures would provide additional functionality and may improve existing properties. However, manufacturing approaches that generate multimaterial parts with intricate three-dimensional (3D) shapes suitable for such tensegrities are rare. Furthermore, the structural complexity of tensegrity systems fabricated through conventional means is generally limited because these systems often require manual assembly. Here, we report a simple approach to fabricate tensegrity structures made of smart materials using 3D printing combined with sacrificial molding. Tensegrity structures consisting of monolithic tendon networks based on smart materials supported by struts could be realized without an additional post-assembly process using our approach. By printing tensegrity with coordinated soft and stiff elements, we could use design parameters (such as geometry, topology, density, coordination number, and complexity) to program system-level mechanics in a soft structure. Last, we demonstrated a tensegrity robot capable of walking in any direction and several tensegrity actuators by leveraging smart tendons with magnetic functionality and the programmed mechanics of tensegrity structures. The physical realization of complex tensegrity metamaterials with programmable mechanical components can pave the way toward more algorithmic designs of 3D soft machines.

Relevant Snippet:
… , tunable mechanical properties, and energy absorption. For … of tensegrity structures with programmed mechanical property … we conducted compressive tests. We placed samples on the …


---

## 4. 3D printed polyurethane honeycombs for repeated tailored energy absorption
Valid Text Names:
'bates20163dprintedpolyurethane pages 1-4', 'bates20163dprintedpolyurethane pages 4-7', 'bates20163dprintedpolyurethane pages 7-10', 'bates20163dprintedpolyurethane pages 10-13', 'bates20163dprintedpolyurethane pages 13-16', 'bates20163dprintedpolyurethane pages 16-18', 'bates20163dprintedpolyurethane pages 18-22'

BibTex:
@article{bates20163dprintedpolyurethane,
    author = "Bates, Simon R.G. and Farrow, Ian R. and Trask, Richard S.",
    title = "3D printed polyurethane honeycombs for repeated tailored energy absorption",
    year = "2016",
    journal = "Materials \& Design",
    volume = "112",
    pages = "172-183",
    month = "Dec",
    doi = "10.1016/j.matdes.2016.08.062",
    url = "https://doi.org/10.1016/j.matdes.2016.08.062",
    publisher = "Elsevier BV",
    issn = "0264-1275"
}


Relevant Snippet:
… lattices were achieved in this way using multi-material PolyJet 3D printing. … 3D printing of TPU for the manufacture of recoverable energy absorbing structures with tailorable properties. …


---

## 5. Mechanical properties and energy absorption of 3D printed square hierarchical honeycombs under in-plane axial compression
Valid Text Names:
'tao2019mechanicalpropertiesand pages 1-2', 'tao2019mechanicalpropertiesand pages 2-3', 'tao2019mechanicalpropertiesand pages 3-4', 'tao2019mechanicalpropertiesand pages 4-5', 'tao2019mechanicalpropertiesand pages 5-7', 'tao2019mechanicalpropertiesand pages 7-9', 'tao2019mechanicalpropertiesand pages 9-10', 'tao2019mechanicalpropertiesand pages 10-11', 'tao2019mechanicalpropertiesand pages 10-10'

BibTex:
@article{tao2019mechanicalpropertiesand,
    author = "Tao, Yong and Li, Weiguo and Wei, Kai and Duan, Shenyu and Wen, Weibin and Chen, Liming and Pei, Yongmao and Fang, Daining",
    title = "Mechanical properties and energy absorption of 3D printed square hierarchical honeycombs under in-plane axial compression",
    year = "2019",
    journal = "Composites Part B: Engineering",
    volume = "176",
    pages = "107219",
    month = "Nov",
    doi = "10.1016/j.compositesb.2019.107219",
    url = "https://doi.org/10.1016/j.compositesb.2019.107219",
    publisher = "Elsevier BV",
    issn = "1359-8368"
}


Relevant Snippet:
… In-plane quasi-static compressive tests were conducted on … mode, mechanical properties and energy absorption performance were … on the mechanical properties and energy absorption …


---

## 6. Prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattice structures
Valid Text Names:
'pajunen2021prestraininducedbandgaptuning pages 1-2', 'pajunen2021prestraininducedbandgaptuning pages 2-3', 'pajunen2021prestraininducedbandgaptuning pages 3-4', 'pajunen2021prestraininducedbandgaptuning pages 4-6', 'pajunen2021prestraininducedbandgaptuning pages 6-7', 'pajunen2021prestraininducedbandgaptuning pages 7-7'

BibTex:
@article{pajunen2021prestraininducedbandgaptuning,
    author = "Pajunen, Kirsti and Celli, Paolo and Daraio, Chiara",
    title = "Prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattice structures",
    year = "2021",
    journal = "Extreme Mechanics Letters",
    volume = "44",
    pages = "101236",
    month = "Apr",
    doi = "10.1016/j.eml.2021.101236",
    url = "https://doi.org/10.1016/j.eml.2021.101236",
    publisher = "Elsevier BV",
    issn = "2352-4316"
}


Relevant Snippet:
… -manufactured tensegrity-inspired lattice structures. These lattices are extremely lightweight and designed to exhibit a nonlinear compressive response that mimics that of a tensegrity …


---

## 7. Experimental investigations on mechanical properties of 3D-printed tensegrity-inspired metamaterials based on 4-strut simplex module
Valid Text Names:
'sabounizawadzka2024experimentalinvestigationson pages 1-3', 'sabounizawadzka2024experimentalinvestigationson pages 3-6', 'sabounizawadzka2024experimentalinvestigationson pages 6-11', 'sabounizawadzka2024experimentalinvestigationson pages 11-13', 'sabounizawadzka2024experimentalinvestigationson pages 13-15'

BibTex:
@article{sabounizawadzka2024experimentalinvestigationson,
    author = "Sabouni-Zawadzka, A Al and Gilewski, W",
    title = "Experimental investigations on mechanical properties of 3D-printed tensegrity-inspired metamaterials based on 4-strut simplex module",
    year = "2024",
    journal = "Unknown journal"
}


Relevant Snippet:
… results of uniaxial compression tests carried out on a number of 3D-printed tensegrity-based … -based struts, exhibiting good energy absorption and tuneable dynamic properties. Liu et al. …


Unobtainable Papers:
Nara Almeida, Ben Gulledge, Jesse Park, Kasra Momeni, A. Tajyar, K. Davami, and Sadie Beck. High strain rate response of 3d-printable tensegrity-inspired structures. International Journal of Solids and Structures, Nov 2025. URL: https://doi.org/10.1016/j.ijsolstr.2025.113590, doi:10.1016/j.ijsolstr.2025.113590.
Filipe A. Santos. Tensegrity metastructure with tunable stiffness, strength, and energy dissipation. Extreme Mechanics Letters, 81:102420, Dec 2025. URL: https://doi.org/10.1016/j.eml.2025.102420, doi:10.1016/j.eml.2025.102420.
Ping Xia, Qiancheng Liu, H. Fu, Ya-Hua Yu, Lijuan Wang, Qingyuan Wang, Xueyi Yu, and Feng Zhao. Mechanical properties and energy absorption of 3d printed double-layered helix honeycomb under in-plane compression. Composite Structures, 315:116982, Jul 2023. URL: https://doi.org/10.1016/j.compstruct.2023.116982, doi:10.1016/j.compstruct.2023.116982.
Hao Zeng, Ruinan Mu, Keyan Huo, Haifeng Zhao, Ke Wang, and Anping Wang. A novel 3d-printable tensegrity-inspired metamaterial enabling dynamic attenuation. International Journal of Mechanics and Materials in Design, 19:883-901, Apr 2023. URL: https://doi.org/10.1007/s10999-023-09656-7, doi:10.1007/s10999-023-09656-7.
Jesse Park, Michael Constantine, Justice Hunt, Braylon Irvin, Cory R. Otto, and Keivan Davami. Additively manufactured tensegrity-inspired structures: density-tuned deformation pathways and specific energy absorption under quasi-static and dynamic loading. Unknown journal, Jan 2026. URL: https://doi.org/10.2139/ssrn.6603990, doi:10.2139/ssrn.6603990.
Connor Simmons, Justice Hunt, Easton Wolfe, Robert Kamin, Shreeraj Pawar, Kasra Momeni, Sadie Beck, and Keivan Davami. Energy absorption and shape reformation analysis of low density additively manufactured star-shaped tensegrity structures. Engineering Research Express, Jan 2026. URL: https://doi.org/10.1088/2631-8695/ae3530, doi:10.1088/2631-8695/ae3530.
Jianwei Sun, Mingyu Gai, Meiling Zhang, Guangsheng Song, Yuyang Wei, Zhihui Zhang, Jinkui Chu, and Luquan Ren. Isotropic energy‐absorbing metamaterial with tensegrity‐inspired architecture and auxetic behavior. Advanced Materials, Nov 2026. URL: https://doi.org/10.1002/adma.202510155, doi:10.1002/adma.202510155.
Silvio Schröder, Christian D. Grimm, Lars Witte, Adli Dimassi, and Philip Buchholz. Design, development and testing of 3d-printed conformal energy absorbing structures. Materials Today Communications, 35:106204, Jun 2023. URL: https://doi.org/10.1016/j.mtcomm.2023.106204, doi:10.1016/j.mtcomm.2023.106204.
Keivan Davami, Russell A. Rowe, Ben Gulledge, Jesse Park, Ali Beheshti, Anthony Palazotto, Fariborz Tavangarian, and Sadie Beck. Dynamic analysis of additively manufactured tensegrity structures. International Journal of Impact Engineering, Dec 2025. URL: https://doi.org/10.1016/j.ijimpeng.2024.105208, doi:10.1016/j.ijimpeng.2024.105208.
Haitao Ye, Xingjian Huang, Liuchao Jin, Sicong Zhou, Guoquan Xie, Zongxin Hu, Rui Li, Haoming Mo, Shitong Fang, Wei-Hsin Liao, Qi Ge, and Xu Song. Multi-material 3d printed compression-induced stretching lattice metamaterials with superior reusable energy absorption. Virtual and Physical Prototyping, Mar 2026. URL: https://doi.org/10.1080/17452759.2026.2637380, doi:10.1080/17452759.2026.2637380.
Leire Roma Rubi, Ryan Kuo, Brennan Birn, and Dr. Grace X. Gu. Tensegrity structures for energy absorption in aerospace landing and reusable rocket systems. In 2025 Regional Student Conferences. American Institute of Aeronautics and Astronautics, Jan 2025. URL: https://doi.org/10.2514/6.2025-97105, doi:10.2514/6.2025-97105.
Jianwei Sun, Haoran Zhang, Meiling Zhang, Guangsheng Song, Yuyang Wei, Jinkui Chu, and Luquan Ren. Twist, recover, repeat: helical tensegrity metamaterials with compression‐torsion coupling, negative dissipation, and programmable energy response. Sep 2026. URL: https://doi.org/10.1002/adfm.202516110, doi:10.1002/adfm.202516110.
Claudio Intrigila, Andrea Micheletti, Nicola Antonio Nodargi, and Paolo Bisegna. Mechanical response of multistable tensegrity-like lattice chains. Additive Manufacturing, Aug 2023. URL: https://doi.org/10.1016/j.addma.2023.103724, doi:10.1016/j.addma.2023.103724.

Artifact IDs that may be injected into the answer: []

Context IDs that may be cited: []

Status: Paper Count=26 | Relevant Papers=0 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=0 | Current Cost=$0.0000 | Disease-Target Evidence=0

---

Retrieved Papers:
## 1. 3D printing of bio-inspired, multi-material structures to enhance stiffness and toughness
Valid Text Names:
'zhang20213dprintingof pages 1-7', 'zhang20213dprintingof pages 7-10', 'zhang20213dprintingof pages 10-13', 'zhang20213dprintingof pages 13-19', 'zhang20213dprintingof pages 19-23', 'zhang20213dprintingof pages 23-28', 'zhang20213dprintingof pages 28-32', 'zhang20213dprintingof pages 32-38', 'zhang20213dprintingof pages 38-44', 'zhang20213dprintingof pages 44-52', 'zhang20213dprintingof pages 52-60', 'zhang20213dprintingof pages 60-66', 'zhang20213dprintingof pages 66-74', 'zhang20213dprintingof pages 74-81', 'zhang20213dprintingof pages 81-89', 'zhang20213dprintingof pages 89-93', 'zhang20213dprintingof pages 93-96', 'zhang20213dprintingof pages 96-98', 'zhang20213dprintingof pages 98-100'

BibTex:
@article{zhang20213dprintingof,
    author = "Zhang, X",
    title = "3D printing of bio-inspired, multi-material structures to enhance stiffness and toughness",
    year = "2021",
    journal = "Unknown journal"
}


Relevant Snippet:
… through Fused filament fabrication (FFF)/ Fused Deposition … for the multi-material PLA & TPU structure under tensile testing. … the required bending, compressive and tensile strengths, as …


---

## 2. Mechanical properties of the FFF sandwich-structured parts made of PLA/TPU multi-material
Valid Text Names:
'arifvianto2022mechanicalpropertiesof pages 1-2', 'arifvianto2022mechanicalpropertiesof pages 2-4', 'arifvianto2022mechanicalpropertiesof pages 4-6', 'arifvianto2022mechanicalpropertiesof pages 6-8', 'arifvianto2022mechanicalpropertiesof pages 8-10', 'arifvianto2022mechanicalpropertiesof pages 10-11'

BibTex:
@article{arifvianto2022mechanicalpropertiesof,
    author = "Arifvianto, Budi and Satiti, Baikhati E. and Salim, Urip A. and Suyitno and Nuryanti, Archadian and Mahardika, Muslim",
    title = "Mechanical properties of the FFF sandwich-structured parts made of PLA/TPU multi-material",
    year = "2022",
    journal = "Progress in Additive Manufacturing",
    volume = "7",
    pages = "1213-1223",
    month = "Apr",
    doi = "10.1007/s40964-022-00295-6",
    url = "https://doi.org/10.1007/s40964-022-00295-6",
    publisher = "Springer Science and Business Media LLC",
    issue = "6",
    issn = "2363-9512"
}


Relevant Snippet:
… of having the multi-material structure in the FFF-processed … /TPU in a sandwich form could improve the low strength and … by the axial tensile or compressive strengths (indicated by the …


---

## 3. Interface boundary mechanical resistance analysis in FFF multi-material parts
Valid Text Names:
'lopes2024interfaceboundarymechanical pages 1-12', 'lopes2024interfaceboundarymechanical pages 12-14', 'lopes2024interfaceboundarymechanical pages 14-17', 'lopes2024interfaceboundarymechanical pages 17-23', 'lopes2024interfaceboundarymechanical pages 23-27', 'lopes2024interfaceboundarymechanical pages 27-30', 'lopes2024interfaceboundarymechanical pages 30-33', 'lopes2024interfaceboundarymechanical pages 33-37', 'lopes2024interfaceboundarymechanical pages 37-40', 'lopes2024interfaceboundarymechanical pages 40-45', 'lopes2024interfaceboundarymechanical pages 45-49', 'lopes2024interfaceboundarymechanical pages 49-55', 'lopes2024interfaceboundarymechanical pages 55-61', 'lopes2024interfaceboundarymechanical pages 61-69', 'lopes2024interfaceboundarymechanical pages 69-75', 'lopes2024interfaceboundarymechanical pages 75-79', 'lopes2024interfaceboundarymechanical pages 79-83', 'lopes2024interfaceboundarymechanical pages 83-87', 'lopes2024interfaceboundarymechanical pages 87-93', 'lopes2024interfaceboundarymechanical pages 93-100', 'lopes2024interfaceboundarymechanical pages 100-105', 'lopes2024interfaceboundarymechanical pages 105-108', 'lopes2024interfaceboundarymechanical pages 108-113', 'lopes2024interfaceboundarymechanical pages 113-116', 'lopes2024interfaceboundarymechanical pages 116-118', 'lopes2024interfaceboundarymechanical pages 118-119'

BibTex:
@article{lopes2024interfaceboundarymechanical,
    author = "Lopes, LMA",
    title = "Interface boundary mechanical resistance analysis in FFF multi-material parts",
    year = "2024",
    journal = "Unknown journal"
}


Relevant Snippet:
… (PETG), polypropylene (PP), thermoplastic polyurethane (TPU) … could increase TPU print's compressive strength. Despite … the adhesion strength between CB/TPU and natural TPU, with …


---

## 4. Mechanical Characterization and Interface Evaluation of Multi-Material Composites Manufactured by Hybrid Fused Deposition Modeling (HFDM)
Valid Text Names:
'daglı2025mechanicalcharacterizationand pages 1-2', 'daglı2025mechanicalcharacterizationand pages 2-4', 'daglı2025mechanicalcharacterizationand pages 4-7', 'daglı2025mechanicalcharacterizationand pages 7-9', 'daglı2025mechanicalcharacterizationand pages 9-11', 'daglı2025mechanicalcharacterizationand pages 11-14', 'daglı2025mechanicalcharacterizationand pages 14-15', 'daglı2025mechanicalcharacterizationand pages 15-17', 'daglı2025mechanicalcharacterizationand pages 17-17'

BibTex:
@article{daglı2025mechanicalcharacterizationand,
    author = "Dağlı, Salih",
    title = "Mechanical Characterization and Interface Evaluation of Multi-Material Composites Manufactured by Hybrid Fused Deposition Modeling (HFDM)",
    year = "2025",
    journal = "Polymers",
    volume = "17",
    pages = "1631",
    month = "Jun",
    doi = "10.3390/polym17121631",
    url = "https://doi.org/10.3390/polym17121631",
    publisher = "MDPI AG",
    issue = "12",
    issn = "2073-4360"
}


Abstract:
In this study, the mechanical behavior and interfacial bonding characteristics of multi-material composites produced using the Hybrid Fused Deposition Modeling (HFDM) technique were systematically investigated. Polylactic Acid (PLA), Polyethylene Terephthalate Glycol (PETG), and Acrylonitrile Butadiene Styrene (ABS) filaments were utilized within a single structure to explore the effects of material combinations on mechanical performance. Specimens were fabricated using two distinct levels of infill density (50–100%) and raster angle (45–90°) to evaluate the influence of these parameters on tensile strength, flexural resistance, and impact toughness. Experimental tests were conducted following ASTM standards, and microstructural examinations were performed using Scanning Electron Microscopy (SEM) to assess interfacial adhesion between different polymers. The results revealed that PETG demonstrated the highest tensile strength among single-material samples, while the PLA-PETG-ABS configuration exhibited notable mechanical stability among hybrid structures. Increasing infill density and raster angle significantly enhanced mechanical performance across all configurations. SEM analyses confirmed that interfacial bonding quality critically affected structural integrity, with better adhesion observed in PLA–PETG interfaces compared to PLA–ABS transitions. The potential of HFDM in developing tailored multi-material components with optimized mechanical properties offers valuable insights for the advancement of functional additive manufacturing applications in engineering fields.

Relevant Snippet:
… multi-material printing using thermoplastic polyurethane (… the mechanical performance and interfacial quality of PLA, PETG, and … The tensile strength values of the multi-material hybrid …


---

## 5. Analysis of the Interface Properties of Multi-material 3D Printed Structures
Valid Text Names:
'pahari2024analysisofthe pages 1-6', 'pahari2024analysisofthe pages 6-10', 'pahari2024analysisofthe pages 10-14', 'pahari2024analysisofthe pages 14-20', 'pahari2024analysisofthe pages 20-25', 'pahari2024analysisofthe pages 25-30', 'pahari2024analysisofthe pages 30-36', 'pahari2024analysisofthe pages 36-41', 'pahari2024analysisofthe pages 41-46', 'pahari2024analysisofthe pages 46-51', 'pahari2024analysisofthe pages 51-55', 'pahari2024analysisofthe pages 55-60', 'pahari2024analysisofthe pages 60-65', 'pahari2024analysisofthe pages 65-70', 'pahari2024analysisofthe pages 70-77', 'pahari2024analysisofthe pages 77-84', 'pahari2024analysisofthe pages 84-93', 'pahari2024analysisofthe pages 93-99', 'pahari2024analysisofthe pages 99-104', 'pahari2024analysisofthe pages 104-109', 'pahari2024analysisofthe pages 109-115', 'pahari2024analysisofthe pages 115-122', 'pahari2024analysisofthe pages 122-132', 'pahari2024analysisofthe pages 132-138', 'pahari2024analysisofthe pages 138-143', 'pahari2024analysisofthe pages 143-147', 'pahari2024analysisofthe pages 147-148'

BibTex:
@article{pahari2024analysisofthe,
    author = "Pahari, S",
    title = "Analysis of the Interface Properties of Multi-material 3D Printed Structures",
    year = "2024",
    journal = "Unknown journal"
}


Relevant Snippet:
… feasibility of FFF printing to fabricate multi-material structures … bonding between thermoplastic polyurethane (TPU) and … The PETC used in this study was PETG infused with 20 % …


---

## 6. On Laminated Object Manufactured FDM-Printed ABS/TPU Multimaterial Specimens: An Insight into Mechanical and Morphological Characteristics
Valid Text Names:
'kumar2022onlaminatedobject pages 1-2', 'kumar2022onlaminatedobject pages 2-4', 'kumar2022onlaminatedobject pages 4-5', 'kumar2022onlaminatedobject pages 5-9', 'kumar2022onlaminatedobject pages 9-11', 'kumar2022onlaminatedobject pages 11-14', 'kumar2022onlaminatedobject pages 14-16', 'kumar2022onlaminatedobject pages 16-18', 'kumar2022onlaminatedobject pages 18-19'

BibTex:
@article{kumar2022onlaminatedobject,
    author = "Kumar, S. and Singh, I. and Koloor, S. S. R. and Kumar, D. and Yahya, M. Y.",
    title = "On Laminated Object Manufactured FDM-Printed ABS/TPU Multimaterial Specimens: An Insight into Mechanical and Morphological Characteristics",
    year = "2022",
    journal = "Polymers",
    volume = "14",
    pages = "4066",
    month = "Sep",
    doi = "10.3390/polym14194066",
    url = "https://doi.org/10.3390/polym14194066",
    publisher = "MDPI AG",
    issue = "19",
    issn = "2073-4360"
}


Abstract:
Fused deposition modeling (FDM) printing of commercial and reinforced filaments is a proven and well-explored method for the enhancement of mechanical properties. However, little has hitherto been reported on the multi-material components, fused or laminated together into a single specimen by using the laminated object manufacturing (LOM) technique for sustainable/renewable polymers. TPU is one such durable and flexible, sustainable material exhibiting renewable and biocompatible properties that have been explored very less often in combination with the ABS polymer matrix in a single specimen, such as the LOM specimen. The current research work presents the LOM manufacturing of 3D-printed flexural specimens of two different, widely used polymers available viz. ABS and TPU and tested as per ASTM D790 standards. The specimens were made and laminated in three layers. They were grouped into two categories, namely ABS: TPU: ABS (ATA) and TPU: ABS: TPU (TAT), which are functionally graded, sandwiched structures of polymeric material. The investigation of the flexural properties, microscopic imaging, and porosity characteristics of the specimens was made for the above categories. The results of the study suggest that ATA-based samples held larger flexural strength than TAT laminated manufactured samples. A significant improvement in the peak elongation and break elongation of the samples was achieved and has shown a 187% increase in the break elongation. Similarly, for the TAT-based specimen, flexural strength was improved significantly from approximately 6.8 MPa to 13 MPa, which represents a nearly 92% increase in the flexural strength. The morphological testing using Tool Maker’s microscopic analysis and porosity analysis has supported the observed trends of mechanical behavior of ATA and TAT samples.

Relevant Snippet:
… Among these AM technologies, FFF has been extensively used … ABS and polyethylene terephthalate glycol (PETG) use 50%:… aims to investigate a multi-material ABS/TPU test specimen …


---

## 7. Enhancing the Performance of FFF-Printed Parts: A Review of Reinforcement and Modification Strategies for Thermoplastic Polymers
Valid Text Names:
'lesniowski2025enhancingtheperformance pages 1-2', 'lesniowski2025enhancingtheperformance pages 2-4', 'lesniowski2025enhancingtheperformance pages 4-6', 'lesniowski2025enhancingtheperformance pages 6-8', 'lesniowski2025enhancingtheperformance pages 8-9', 'lesniowski2025enhancingtheperformance pages 9-11', 'lesniowski2025enhancingtheperformance pages 11-13', 'lesniowski2025enhancingtheperformance pages 13-14', 'lesniowski2025enhancingtheperformance pages 14-16', 'lesniowski2025enhancingtheperformance pages 16-18', 'lesniowski2025enhancingtheperformance pages 18-20', 'lesniowski2025enhancingtheperformance pages 20-22', 'lesniowski2025enhancingtheperformance pages 22-23', 'lesniowski2025enhancingtheperformance pages 23-26', 'lesniowski2025enhancingtheperformance pages 26-27', 'lesniowski2025enhancingtheperformance pages 27-29', 'lesniowski2025enhancingtheperformance pages 29-32', 'lesniowski2025enhancingtheperformance pages 32-33', 'lesniowski2025enhancingtheperformance pages 33-35', 'lesniowski2025enhancingtheperformance pages 35-36', 'lesniowski2025enhancingtheperformance pages 38-39', 'lesniowski2025enhancingtheperformance pages 39-41', 'lesniowski2025enhancingtheperformance pages 41-42', 'lesniowski2025enhancingtheperformance pages 43-45', 'lesniowski2025enhancingtheperformance pages 45-45'

BibTex:
@article{lesniowski2025enhancingtheperformance,
    author = "Leśniowski, Jakub and Stawiarski, Adam and Barski, Marek",
    title = "Enhancing the Performance of FFF-Printed Parts: A Review of Reinforcement and Modification Strategies for Thermoplastic Polymers",
    volume = "18",
    issn = "1996-1944",
    url = "https://doi.org/10.3390/ma18225185",
    doi = "10.3390/ma18225185",
    number = "22",
    journal = "Materials",
    publisher = "MDPI AG",
    year = "2025",
    month = "Nov",
    pages = "5185",
    issue = "22"
}


Abstract:
<jats:p>The technology of 3D printing has become one of the most effective methods of creating various parts, such as those used for fast prototyping. The most important aspect of 3D printing is the selection and application of the appropriate material, also known as filament. The current review concerns mainly the description of the mechanical and physical properties of the different filaments and the possibilities of improving those properties. The review begins with a short description of the development of 3D printing technology. Next, the basic characteristics of thermoplastics used in the fused filament fabrication (FFF) are discussed, namely polylactic acid (PLA), acrylonitrile butadiene styrene (ABS), and polyethylene terephthalate glycol (PETG). According to modern concepts, the printed parts can be reinforced with the use of different kinds of fibers, namely synthetic fibers (carbon, glass, aramid) or natural fibers (wood, flax, hemp, jute). Thus, the impact of such a reinforcement on the performance of FFF composites is also presented. The current review, unlike other works, primarily addresses the problem of the aging of parts made from the thermoplastics above. Environmental conditions, including UV radiation, can drastically reduce the physical and mechanical properties of printed elements. Moreover, the current review contains a detailed discussion about the influence of the different fibers on the final mechanical properties of the printed elements. Generally, the synthetic fibers improve the mechanical performance, with documented increases in tensile modulus reaching, for instance, 700% for carbon-fiber-reinforced ABS or over 15-fold for continuous aramid composites, enabling their use in functional, load-bearing components. In contrast, the natural ones could even decrease the stiffness and strength (e.g., wood–plastic composites), or, as in the case of flax, significantly increase stiffness (by 88–121%) while offering a sustainable, lightweight alternative for non-structural applications.</jats:p>

Relevant Snippet:
… with impact modifiers eg, thermoplastic polyurethane (TPU) or ethylene vinyl acetate … mechanical properties in FFF-printed PETG. Specifically, the ultimate tensile strength of the PETG …


---

## 8. Sensor development for biomechanical applications through additive manufacturing techniques
Valid Text Names:
'bretos2025sensordevelopmentfor pages 1-5', 'bretos2025sensordevelopmentfor pages 5-9', 'bretos2025sensordevelopmentfor pages 9-10', 'bretos2025sensordevelopmentfor pages 10-14', 'bretos2025sensordevelopmentfor pages 14-19', 'bretos2025sensordevelopmentfor pages 19-23', 'bretos2025sensordevelopmentfor pages 23-26', 'bretos2025sensordevelopmentfor pages 26-28', 'bretos2025sensordevelopmentfor pages 28-34', 'bretos2025sensordevelopmentfor pages 34-38', 'bretos2025sensordevelopmentfor pages 38-43', 'bretos2025sensordevelopmentfor pages 43-48', 'bretos2025sensordevelopmentfor pages 48-52', 'bretos2025sensordevelopmentfor pages 52-55', 'bretos2025sensordevelopmentfor pages 55-60', 'bretos2025sensordevelopmentfor pages 60-64', 'bretos2025sensordevelopmentfor pages 64-67', 'bretos2025sensordevelopmentfor pages 67-72', 'bretos2025sensordevelopmentfor pages 72-76', 'bretos2025sensordevelopmentfor pages 76-79', 'bretos2025sensordevelopmentfor pages 79-82', 'bretos2025sensordevelopmentfor pages 82-87', 'bretos2025sensordevelopmentfor pages 87-94', 'bretos2025sensordevelopmentfor pages 94-96'

BibTex:
@article{bretos2025sensordevelopmentfor,
    author = "Bretos, Ò Palau",
    title = "Sensor development for biomechanical applications through additive manufacturing techniques",
    year = "2025",
    journal = "Unknown journal"
}


Relevant Snippet:
… ; and PETG, used for the final printing; with conductive TPU … In terms of strength, PETG has a tensile strength around 49 MPa … For example, in (43) and in (44), where multi-material FFF …


Unobtainable Papers:
Maria Tanase, Alexandra Ileana Portoaca, and Alin Dinita. Mechanical properties assessment of multi-material samples, pages 33-65. Elsevier, Jan 2025. URL: https://doi.org/10.1016/b978-0-443-29228-6.00003-7, doi:10.1016/b978-0-443-29228-6.00003-7.
Omar Khatir, Bel Abbes Bachir Bouiadjra, Amine Yerou, Mohamed Amine Bellali, Belaid Mechab, Mokadem Salem, and Mohamed Elmeguenni. Analysis of the mechanical properties of 3d-printed polylactic acid/thermoplastic polyurethane multi-materials. Journal of Materials Engineering and Performance, 35(4):3863-3873, Aug 2026. URL: https://doi.org/10.1007/s11665-025-11833-y, doi:10.1007/s11665-025-11833-y.
Günther Schuh, Georg Bergweiler, Jan Cluse, and Bernd Löffler. 3d printed multi-material force sensor for load monitoring of structural components. SSRN Electronic Journal, Jan 2022. URL: https://doi.org/10.2139/ssrn.4113339, doi:10.2139/ssrn.4113339.
Khawlah Alabdouli, Wesley Cantwell, Sean Swei, and Kamran A. Khan. Energy absorption performance of 3d and 4d printed multi-material origami-inspired polyhedral sandwich structures under compression and impact loads. Polymer Testing, 158:109183, May 2026. URL: https://doi.org/10.1016/j.polymertesting.2026.109183, doi:10.1016/j.polymertesting.2026.109183.
Imran Khan, Muhammad Tariq, Muhammad Abas, Muhammad Shakeel, Fatima Hira, Ans Al Rashid, and Muammer Koç. Parametric investigation and optimisation of mechanical properties of thick tri-material based composite of pla-petg-abs 3d-printed using fused filament fabrication. Composites Part C: Open Access, 12:100392, Oct 2023. URL: https://doi.org/10.1016/j.jcomc.2023.100392, doi:10.1016/j.jcomc.2023.100392.
Jesús A. Díaz-Zaragoza and Hugo I. Medellín-Castillo. Multimaterial experimental characterization of fff tensile specimens with variable infill density using a universalized methodology. The International Journal of Advanced Manufacturing Technology, 140:3301-3319, Sep 2025. URL: https://doi.org/10.1007/s00170-025-16453-3, doi:10.1007/s00170-025-16453-3.
Dinesh Deshwal, Gaurav Jangra, Monika Deshwal, and Ashish Kaushik. Bioinspired design and metaheuristic driven process optimization of fdm printed petg–tpu thermoplastic composites for improved mechanical performance. Journal of Thermoplastic Composite Materials, Apr 2026. URL: https://doi.org/10.1177/08927057261442118, doi:10.1177/08927057261442118.
Shauvik Pahari and Garrett W. Melenka. Analysis of the interface properties of multi-material fused filament fabricated (fff) printed polymer composite structures. International Journal of Adhesion and Adhesives, Jun 2025. URL: https://doi.org/10.1016/j.ijadhadh.2025.104074, doi:10.1016/j.ijadhadh.2025.104074.
H. Ettayan, I. Abdous, A. Ouballouch, and L. Boutahar. Review on multi-material 3d printing via fdm: insights into mechanical performance and printing parameters. Archives of Materials Science and Engineering, May 2025. URL: https://doi.org/10.5604/01.3001.0055.4326, doi:10.5604/01.3001.0055.4326.
Özkan Öz and Fatih Huzeyfe Öztürk. Influence of layer thickness on bending and interlayer adhesion of mono-material and multi-material pla and petg structures. Journal of the Brazilian Society of Mechanical Sciences and Engineering, Mar 2026. URL: https://doi.org/10.1007/s40430-025-06241-1, doi:10.1007/s40430-025-06241-1.
Yassmin Seid Ahmed. Transfer learning-guided process-structure–property mapping in dual-material fused filament fabrication. Progress in Additive Manufacturing, 11:4313-4340, Mar 2026. URL: https://doi.org/10.1007/s40964-026-01588-w, doi:10.1007/s40964-026-01588-w.

Artifact IDs that may be injected into the answer: []

Context IDs that may be cited: []

Status: Paper Count=33 | Relevant Papers=0 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=0 | Current Cost=$0.0000 | Disease-Target Evidence=0

---

Retrieved Papers:
## 1. Analysis of the compression behaviour of different composite lattice designs
Valid Text Names:
'umer2018analysisofthe pages 1-2', 'umer2018analysisofthe pages 2-4', 'umer2018analysisofthe pages 4-6', 'umer2018analysisofthe pages 6-7', 'umer2018analysisofthe pages 7-9', 'umer2018analysisofthe pages 9-12', 'umer2018analysisofthe pages 12-14', 'umer2018analysisofthe pages 14-15'

BibTex:
@article{umer2018analysisofthe,
    author = "Umer, R. and Barsoum, Z. and Jishi, HZ and Ushijima, K. and Cantwell, W.",
    title = "Analysis of the compression behaviour of different composite lattice designs",
    year = "2018",
    journal = "Journal of Composite Materials",
    volume = "52",
    pages = "715-729",
    month = "Mar",
    doi = "10.1177/0021998317714531",
    url = "https://doi.org/10.1177/0021998317714531",
    publisher = "SAGE Publications",
    issue = "6",
    issn = "0021-9983"
}


Relevant Snippet:
… Compression tests on the four lattice structures indicated that the F 2 BCC lattice offered the highest compression … were evaluated by loading the specimens in an Instron 1425 at a …


---

## 2. Compressive behaviour of stainless steel micro-lattice structures
Valid Text Names:
'gumruk2013compressivebehaviourof pages 1-2', 'gumruk2013compressivebehaviourof pages 2-4', 'gumruk2013compressivebehaviourof pages 4-5', 'gumruk2013compressivebehaviourof pages 5-6', 'gumruk2013compressivebehaviourof pages 6-7', 'gumruk2013compressivebehaviourof pages 7-9', 'gumruk2013compressivebehaviourof pages 9-10', 'gumruk2013compressivebehaviourof pages 10-12', 'gumruk2013compressivebehaviourof pages 12-13', 'gumruk2013compressivebehaviourof pages 13-14', 'gumruk2013compressivebehaviourof pages 14-15', 'gumruk2013compressivebehaviourof pages 15-15'

BibTex:
@article{gumruk2013compressivebehaviourof,
    author = "Gümrük, R. and Mines, R.A.W.",
    title = "Compressive behaviour of stainless steel micro-lattice structures",
    year = "2013",
    journal = "International Journal of Mechanical Sciences",
    volume = "68",
    pages = "125-139",
    month = "Mar",
    doi = "10.1016/j.ijmecsci.2013.01.006",
    url = "https://doi.org/10.1016/j.ijmecsci.2013.01.006",
    publisher = "Elsevier BV",
    issn = "0020-7403"
}


Relevant Snippet:
This paper focuses on investigating the mechanical static compression behaviour of 316L stainless steel micro-lattice materials manufactured using selective laser melting method. In …


---

## 3. MECHANICAL DESIGN OF A NOVEL LATTICE STRUCTURE
Valid Text Names:
'distefano2022mechanicaldesignof pages 1-7', 'distefano2022mechanicaldesignof pages 7-11', 'distefano2022mechanicaldesignof pages 11-14', 'distefano2022mechanicaldesignof pages 14-19', 'distefano2022mechanicaldesignof pages 19-26', 'distefano2022mechanicaldesignof pages 26-31', 'distefano2022mechanicaldesignof pages 31-34', 'distefano2022mechanicaldesignof pages 34-41', 'distefano2022mechanicaldesignof pages 41-46', 'distefano2022mechanicaldesignof pages 46-52', 'distefano2022mechanicaldesignof pages 52-56', 'distefano2022mechanicaldesignof pages 56-64', 'distefano2022mechanicaldesignof pages 64-75', 'distefano2022mechanicaldesignof pages 75-80', 'distefano2022mechanicaldesignof pages 80-85', 'distefano2022mechanicaldesignof pages 85-90', 'distefano2022mechanicaldesignof pages 90-99', 'distefano2022mechanicaldesignof pages 99-103', 'distefano2022mechanicaldesignof pages 103-108', 'distefano2022mechanicaldesignof pages 108-112', 'distefano2022mechanicaldesignof pages 112-120', 'distefano2022mechanicaldesignof pages 120-126', 'distefano2022mechanicaldesignof pages 126-134', 'distefano2022mechanicaldesignof pages 134-137', 'distefano2022mechanicaldesignof pages 137-140', 'distefano2022mechanicaldesignof pages 140-143', 'distefano2022mechanicaldesignof pages 143-146', 'distefano2022mechanicaldesignof pages 146-150', 'distefano2022mechanicaldesignof pages 150-153', 'distefano2022mechanicaldesignof pages 153-157', 'distefano2022mechanicaldesignof pages 157-160', 'distefano2022mechanicaldesignof pages 160-164', 'distefano2022mechanicaldesignof pages 164-168'

BibTex:
@article{distefano2022mechanicaldesignof,
    author = "Distefano, F",
    title = "MECHANICAL DESIGN OF A NOVEL LATTICE STRUCTURE",
    year = "2022",
    journal = "Unknown journal"
}


Relevant Snippet:
… Bending-dominated structures are compliant and absorb … TPMS sheet lattice structures by carrying out compressive tests. … cell, while an INSTRON 8854 servo-hydraulic testing machine, …


---

## 4. Improved mechanical performance of quasi-cubic lattice metamaterials with asymmetric joints
Valid Text Names:
'solyaev2023improvedmechanicalperformance pages 1-2', 'solyaev2023improvedmechanicalperformance pages 2-3', 'solyaev2023improvedmechanicalperformance pages 3-4', 'solyaev2023improvedmechanicalperformance pages 4-5', 'solyaev2023improvedmechanicalperformance pages 5-6', 'solyaev2023improvedmechanicalperformance pages 6-7', 'solyaev2023improvedmechanicalperformance pages 7-8', 'solyaev2023improvedmechanicalperformance pages 8-9', 'solyaev2023improvedmechanicalperformance pages 9-11', 'solyaev2023improvedmechanicalperformance pages 11-11', 'solyaev2023improvedmechanicalperformance pages 11-12', 'solyaev2023improvedmechanicalperformance pages 12-13', 'solyaev2023improvedmechanicalperformance pages 13-14'

BibTex:
@article{solyaev2023improvedmechanicalperformance,
    author = "Solyaev, Yury O. and Ustenko, Anastasia D. and Babaytsev, Arseniy V. and Dobryanskiy, Vasiliy N.",
    title = "Improved mechanical performance of quasi-cubic lattice metamaterials with asymmetric joints",
    year = "2023",
    journal = "Scientific Reports",
    volume = "13",
    month = "Sep",
    doi = "10.1038/s41598-023-41614-3",
    url = "https://doi.org/10.1038/s41598-023-41614-3",
    publisher = "Research Square Platform LLC"
}


Abstract:
In this paper, we propose a simple method for the modification of the unit cells in the lattice metamaterials that provides an improvement of their impact strength. The idea is based on the introduction of small mutual offsets of the interconnected struts inside the unit cells. In such way, the joints between the struts become asymmetric and the overall geometry of the unit cells can be defined as the quasi-cubic with the axis of chirality. Considering four types of cubic lattices with BCC, BCT, FCC and octahedron structures, we modified their geometry and investigated the influence of the offsets and the unit cell size on the overall performance in static and dynamic tests. From the experiments we found that the small offsets (less than the strut diameter) can allow to increase the impact strength of 3d-printed polymeric specimens in 1.5–3 times remaining almost the same density and static mechanical properties. Based on the numerical simulations, we show that the explanation of the observed phenomena can be related to the increase of plastic deformations and damage accumulation in the unit-cells with asymmetric joints leading to the transition from the quasi-brittle to the ductile type of fracture in tested specimens.

Relevant Snippet:
… Additionally, we used the compression test to find the … tests were performed by using Instron 5969 universal testing … Compliance correction of the testing machine was performed …


---

## 5. Mechanical properties of diamond lattice structures based on main parameters and strain rate
Valid Text Names:
'miralbes2023mechanicalpropertiesof pages 1-6', 'miralbes2023mechanicalpropertiesof pages 6-11', 'miralbes2023mechanicalpropertiesof pages 11-15', 'miralbes2023mechanicalpropertiesof pages 15-21', 'miralbes2023mechanicalpropertiesof pages 21-28', 'miralbes2023mechanicalpropertiesof pages 28-31', 'miralbes2023mechanicalpropertiesof pages 31-32'

BibTex:
@article{miralbes2023mechanicalpropertiesof,
    author = "Miralbés, R. and Santamaria, N. and Ranz, D. and Garcia, J. A.",
    title = "Mechanical properties of diamond lattice structures based on main parameters and strain rate",
    year = "2023",
    journal = "Mechanics of Advanced Materials and Structures",
    volume = "30",
    pages = "3721-3733",
    month = "Jun",
    doi = "10.1080/15376494.2022.2081749",
    url = "https://doi.org/10.1080/15376494.2022.2081749",
    publisher = "Informa UK Limited",
    issue = "18",
    issn = "1537-6494"
}


Abstract:
Abstract The diamond triply periodic minimal surface structure has a high mechanical property–weight ratio. They can be modified by changing their internal parameters or the material. They are generated using the additive manufacturing (AM) that possibilities the use of various materials for generating zones with different mechanical properties or by modifying their internal parameters. However, the effects of internal parameters in the mechanical properties have not been defined in detail. Furthermore, the strain rate modifies these mechanical properties. In this study, the effects of the internal parameters and strain rate were evaluated and additionally, the failure mechanism of the structures.

Relevant Snippet:
… and quasistatic compressive loads using an 8032 Instron universal testing machine. … was determined based on the maximum velocity of the Instron machine (4 mm/s) applied to the …


---

## 6. Mechanical Properties of Ti-6Al-4V Selectively Laser Melted Parts with Body-Centred-Cubic Lattices of Varying cell size
Valid Text Names:
'maskery2015mechanicalpropertiesof pages 1-2', 'maskery2015mechanicalpropertiesof pages 2-4', 'maskery2015mechanicalpropertiesof pages 4-5', 'maskery2015mechanicalpropertiesof pages 5-7', 'maskery2015mechanicalpropertiesof pages 7-9', 'maskery2015mechanicalpropertiesof pages 9-10', 'maskery2015mechanicalpropertiesof pages 10-11', 'maskery2015mechanicalpropertiesof pages 11-12', 'maskery2015mechanicalpropertiesof pages 12-12'

BibTex:
@article{maskery2015mechanicalpropertiesof,
    author = "Maskery, I. and Aremu, A.O. and Simonelli, M. and Tuck, C. and Wildman, R.D. and Ashcroft, I.A. and Hague, R.J.M.",
    title = "Mechanical Properties of Ti-6Al-4V Selectively Laser Melted Parts with Body-Centred-Cubic Lattices of Varying cell size",
    year = "2015",
    journal = "Experimental Mechanics",
    volume = "55",
    pages = "1261-1272",
    month = "Apr",
    doi = "10.1007/s11340-015-0021-5",
    url = "https://doi.org/10.1007/s11340-015-0021-5",
    publisher = "Springer Science and Business Media LLC",
    issue = "7",
    issn = "0014-4851"
}


Abstract:
Significant weight savings in parts can be made through the use of additive manufacture (AM), a process which enables the construction of more complex geometries, such as functionally graded lattices, than can be achieved conventionally. The existing framework describing the mechanical properties of lattices places strong emphasis on one property, the relative density of the repeating cells, but there are other properties to consider if lattices are to be used effectively. In this work, we explore the effects of cell size and number of cells, attempting to construct more complete models for the mechanical performance of lattices. This was achieved by examining the modulus and ultimate tensile strength of latticed tensile specimens with a range of unit cell sizes and fixed relative density. Understanding how these mechanical properties depend upon the lattice design variables is crucial for the development of design tools, such as finite element methods, that deliver the best performance from AM latticed parts. We observed significant reductions in modulus and strength with increasing cell size, and these reductions cannot be explained by increasing strut porosity as has previously been suggested. We obtained power law relationships for the mechanical properties of the latticed specimens as a function of cell size, which are similar in form to the existing laws for the relative density dependence. These can be used to predict the properties of latticed column structures comprised of body-centred-cubic (BCC) cells, and may also be adapted for other part geometries. In addition, we propose a novel way to analyse the tensile modulus data, which considers a relative lattice cell size rather than an absolute size. This may lead to more general models for the mechanical properties of lattice structures, applicable to parts of varying size.

Relevant Snippet:
… However, for an open-celled lattice under compression, … made using an Instron-5969 universal testing machine, with the … due to the the machine compliance correction discussed above, …


---

## 7. The Influence of Processing Parameters on the Mechanical Properties of Selectively Laser Melted Stainless Steel Microlattice Structures
Valid Text Names:
'tsopanos2010theinfluenceof pages 1-2', 'tsopanos2010theinfluenceof pages 2-3', 'tsopanos2010theinfluenceof pages 3-5', 'tsopanos2010theinfluenceof pages 5-6', 'tsopanos2010theinfluenceof pages 6-8', 'tsopanos2010theinfluenceof pages 8-10', 'tsopanos2010theinfluenceof pages 10-11', 'tsopanos2010theinfluenceof pages 11-12'

BibTex:
@article{tsopanos2010theinfluenceof,
    author = "Tsopanos, S. and Mines, R. A. W. and McKown, S. and Shen, Y. and Cantwell, W. J. and Brooks, W. and Sutcliffe, C. J.",
    title = "The Influence of Processing Parameters on the Mechanical Properties of Selectively Laser Melted Stainless Steel Microlattice Structures",
    year = "2010",
    journal = "Journal of Manufacturing Science and Engineering-transactions of The Asme",
    volume = "132",
    pages = "041011",
    month = "Aug",
    doi = "10.1115/1.4001743",
    url = "https://doi.org/10.1115/1.4001743",
    publisher = "ASME International",
    issue = "4",
    issn = "1087-1357"
}


Relevant Snippet:
… compression tests were conducted on 20 mm cubed lattice blocks placed between lubricated compression platens on an Instron 4024 universal test … Hence, the compliance correction …


---

## 8. Compressive response of lattice structures: a multiscale approach to model the influence of internal defects
Valid Text Names:
'ciampaglia2025compressiveresponseof pages 1-2', 'ciampaglia2025compressiveresponseof pages 2-5', 'ciampaglia2025compressiveresponseof pages 5-8', 'ciampaglia2025compressiveresponseof pages 8-10', 'ciampaglia2025compressiveresponseof pages 10-13', 'ciampaglia2025compressiveresponseof pages 13-14', 'ciampaglia2025compressiveresponseof pages 14-15', 'ciampaglia2025compressiveresponseof pages 15-15'

BibTex:
@article{ciampaglia2025compressiveresponseof,
    author = "Ciampaglia, Alberto and Niutta, Carlo Boursier and Benelli, Alessandro and Tridello, Andrea",
    title = "Compressive response of lattice structures: a multiscale approach to model the influence of internal defects",
    year = "2025",
    journal = "Progress in Additive Manufacturing",
    volume = "10",
    pages = "4107-4121",
    month = "Mar",
    doi = "10.1007/s40964-025-01026-3",
    url = "https://doi.org/10.1007/s40964-025-01026-3",
    publisher = "Springer Science and Business Media LLC",
    issue = "7",
    issn = "2363-9512"
}


Relevant Snippet:
… diameter correction modeled defect influence in PA-12 lattice … were tested on an Instron 8801 servo hydraulic machine at a … of the compression tests of the lattice structures is presented …


Unobtainable Papers:
Christiane Beyer and Dustin Figueroa. Design and analysis of lattice structures for additive manufacturing. Journal of Manufacturing Science and Engineering-transactions of The Asme, 138:121014, Dec 2016. URL: https://doi.org/10.1115/1.4033957, doi:10.1115/1.4033957.
Ramakrishna Doodi and Bala Murali Gunji. An experimental and numerical investigation on the performance of novel hybrid bio-inspired 3d printed lattice structures for stiffness and energy absorption applications. Mechanics of Advanced Materials and Structures, 31:3970-3979, Mar 2024. URL: https://doi.org/10.1080/15376494.2023.2188324, doi:10.1080/15376494.2023.2188324.
Parham Mostofizadeh, Robert A. Dorey, and Iman Mohagheghian. Effect of temperature variation and strain rate on the mechanical properties of multi-material lattice structures. Feb 2025. URL: https://doi.org/10.1016/j.matdes.2025.113596, doi:10.1016/j.matdes.2025.113596.
Ramakrishna Doodi and Bala Murali Gunji. Experimental and numerical investigation on novel three-dimensional printed bio-inspired hexagonal lattices for energy absorption and stiffness behavior. Mechanics Based Design of Structures and Machines, 52:8727-8743, Mar 2024. URL: https://doi.org/10.1080/15397734.2024.2326609, doi:10.1080/15397734.2024.2326609.
James Jiyung Lee. Development and mechanical characterisation of additively manufactured lattice structures. Text, 2023. URL: https://doi.org/10.25560/102852, doi:10.25560/102852.
S. L. Sing, W. Y. Yeong, F. E. Wiria, and B. Y. Tay. Characterization of titanium lattice structures fabricated by selective laser melting using an adapted compressive test method. Experimental Mechanics, 56:735-748, Jan 2016. URL: https://doi.org/10.1007/s11340-015-0117-y, doi:10.1007/s11340-015-0117-y.
Stephen Daynes, Stefanie Feih, Wen Feng Lu, and Jun Wei. Optimisation of functionally graded lattice structures using isostatic lines. Materials & Design, 127:215-223, Aug 2017. URL: https://doi.org/10.1016/j.matdes.2017.04.082, doi:10.1016/j.matdes.2017.04.082.
Oliver Weeger, Iman Valizadeh, Yash Mistry, and Dhruv Bhate. Inelastic finite deformation beam modeling, simulation, and validation of additively manufactured lattice structures. Additive Manufacturing Letters, 4:100111, Feb 2023. URL: https://doi.org/10.1016/j.addlet.2022.100111, doi:10.1016/j.addlet.2022.100111.

Artifact IDs that may be injected into the answer: []

Context IDs that may be cited: []

Status: Paper Count=33 | Relevant Papers=0 | Clinical Trial Count=0 | Relevant Clinical Trials=0 | Current Evidence=0 | Current Cost=$0.0000 | Disease-Target Evidence=0

---

Retrieved Papers:
## 1. Strain induced strengthening of soft thermoplastic polyurethanes under cyclic deformation
Valid Text Names:
'scetta2021straininducedstrengthening pages 1-6', 'scetta2021straininducedstrengthening pages 6-12', 'scetta2021straininducedstrengthening pages 12-17', 'scetta2021straininducedstrengthening pages 17-21', 'scetta2021straininducedstrengthening pages 21-22'

BibTex:
@article{scetta2021straininducedstrengthening,
    author = "Scetta, Giorgia and Ju, Jianzhu and Selles, Nathan and Heuillet, Patrick and Ciccotti, Matteo and Creton, Costantino",
    title = "Strain induced strengthening of soft thermoplastic polyurethanes under cyclic deformation",
    year = "2021",
    journal = "ArXiv",
    volume = "59",
    pages = "685-696",
    month = "Apr",
    doi = "10.48550/arxiv.2104.02504",
    url = "https://doi.org/10.48550/arxiv.2104.02504",
    publisher = "Wiley",
    issue = "8",
    issn = "2642-4150"
}


Abstract:
We investigate the cyclic mechanical behavior in uniaxial tension of three different commercial thermoplastic polyurethane elastomers (TPU) often considered as a sustainable replacement for common filled elastomers. All TPU have similar hard segment contents and linear moduli but sensibly different large strain properties as shown by X-Ray analysis. Despite these differences, we found a stiffening effect after conditioning in step cyclic loading which greatly differs from the common softening (also referred as Mullins effect) observed in chemically crosslinked filled rubbers. We propose that this self-reinforcement is related to the fragmentation of hard domains, naturally present in TPU, in smaller but more numerous subunits that may act as new physical crosslinking points. The proposed stiffening mechanism is not dissimilar to the strain-induced crystallization observed in stretched natural rubber, but it presents a persistent nature. In particular, it may cause a local reinforcement where an inhomogeneous strain field is present, as is the case of a crack propagating in cyclic fatigue, providing a potential explanation for the well-known toughness and wear resistance of TPU.

Relevant Snippet:
… effect after conditioning in step cyclic loading which greatly differs from the common softening (also referred as Mullins effect) … stiffening in TPU with applied strain in cyclic loading. While …


---

## 2. Cyclic fatigue failure of TPU using a crack propagation approach
Valid Text Names:
'scetta2021cyclicfatiguefailure pages 1-2', 'scetta2021cyclicfatiguefailure pages 2-3', 'scetta2021cyclicfatiguefailure pages 3-4', 'scetta2021cyclicfatiguefailure pages 4-6', 'scetta2021cyclicfatiguefailure pages 6-7', 'scetta2021cyclicfatiguefailure pages 7-9', 'scetta2021cyclicfatiguefailure pages 9-9'

BibTex:
@misc{scetta2021cyclicfatiguefailure,
    author = "Scetta, Giorgia and Selles, Nathan and Heuillet, Patrick and Ciccotti, Matteo and Creton, Costantino",
    title = "Cyclic fatigue failure of TPU using a crack propagation approach",
    year = "2021",
    journal = "Polymer Testing",
    volume = "97",
    pages = "107140",
    month = "May",
    doi = "10.1016/j.polymertesting.2021.107140",
    url = "https://doi.org/10.1016/j.polymertesting.2021.107140",
    publisher = "Elsevier BV",
    issn = "0142-9418"
}


Relevant Snippet:
… Thermoplastic polyurethane elastomers (TPU) are stretchable, … toughness and cyclic fatigue resistance of TPUs, opening new … to crack propagation under cyclic loading at large strains. …


---

## 3. Characterization and modeling of the fatigue behavior of TPU
Valid Text Names:
'holzweber2018characterizationandmodeling pages 1-4', 'holzweber2018characterizationandmodeling pages 4-6', 'holzweber2018characterizationandmodeling pages 6-6'

BibTex:
@article{holzweber2018characterizationandmodeling,
    author = "Holzweber, J. and Müller, J. and Çakmak, U.D. and Major, Z.",
    title = "Characterization and modeling of the fatigue behavior of TPU",
    year = "2018",
    journal = "Materials Today: Proceedings",
    volume = "5",
    pages = "26572-26577",
    month = "Jan",
    doi = "10.1016/j.matpr.2018.08.118",
    url = "https://doi.org/10.1016/j.matpr.2018.08.118",
    publisher = "Elsevier BV",
    issue = "13",
    issn = "2214-7853"
}


Relevant Snippet:
… and fatigue characteristics of thermoplastic polyurethanes (TPU), … Cyclic transient behavior including Mullin’s effect is also … to crack propagation under cyclic loading at large strains. …


---

## 4. Parametric Study of Geometry and Process Parameter Influences on Additively Manufactured Piezoresistive Sensors Under Cyclic Loading
Valid Text Names:
'goutier2025parametricstudyof pages 1-1'

BibTex:
@article{goutier2025parametricstudyof,
    author = "Goutier, Marijn and Vietor, Thomas",
    title = "Parametric Study of Geometry and Process Parameter Influences on Additively Manufactured Piezoresistive Sensors Under Cyclic Loading",
    year = "2025",
    journal = "Polymers",
    volume = "17",
    pages = "1625",
    month = "Jun",
    doi = "10.3390/polym17121625",
    url = "https://doi.org/10.3390/polym17121625",
    publisher = "MDPI AG",
    issue = "12",
    issn = "2073-4360"
}


Abstract:
The additive manufacturing of piezoresistive sensors offers several advantages, such as the elimination of assembly or installation steps, enabling integration into complex parts precisely where desired, and compatibility with soft robotics applications. Previous studies have demonstrated that several characteristics of additively manufactured sensors, such as their resistance and sensitivity, are significantly affected by the selected printing parameters. This work seeks to further the understanding of the relationships between process parameters, material, sensor design, and the resulting sensor characteristics. To this end, sensors made from two materials, with differing printing layer heights, infill angles, and thicknesses, are characterized under cyclic tensile loading. For these sensors, the nonlinearity, hysteresis, and drift are analyzed. The findings indicate that both nonlinearity and hysteresis are significantly affected by the material choice, as well as the selected parameters. Notably, parameters that affect the sensitivity of the sensor, e.g., the infill angle, can have significant indirect effects on the nonlinearity and hysteresis errors. Through correct parameter selection, nonlinearity errors can be reduced by up to 30.7% or 25.3%, depending on the material used. The hysteresis error can be reduced by up to 38.7% or 23.8%, depending on the material. The drift over multiple cycles is found to be strongly material dependent, but can also be affected by the process parameters, e.g., the infill angle. Understanding the interactions between material, design, process, and the resulting sensor characteristics provides valuable insights for the successful design and additive manufacturing of piezoresistive sensors.

Relevant Snippet:
… preconditioning possibilities may not exist. In these cases, it is important to understand how the behavior changes during the first loading … Eel, a thermoplastic polyurethane (TPU)-based …


---

## 5. Enhancing the Energy Absorption Performance of 3D-Printed CF/TPU Composite Materials by Introducing a “Rigid–Elastic” Structure Through Multi-Scale Synergies
Valid Text Names:
'zhou2025enhancingtheenergy pages 1-2', 'zhou2025enhancingtheenergy pages 2-5', 'zhou2025enhancingtheenergy pages 5-7', 'zhou2025enhancingtheenergy pages 7-9', 'zhou2025enhancingtheenergy pages 9-12', 'zhou2025enhancingtheenergy pages 12-15', 'zhou2025enhancingtheenergy pages 15-17', 'zhou2025enhancingtheenergy pages 17-18', 'zhou2025enhancingtheenergy pages 18-19'

BibTex:
@article{zhou2025enhancingtheenergy,
    author = "Zhou, Xuanyu and He, Ouyang and Zhang, Yuan and Zhu, Ziqiang and Wang, Zhen and Cheng, Zirui and Hu, Yubing and Zhang, Yanan",
    title = "Enhancing the Energy Absorption Performance of 3D-Printed CF/TPU Composite Materials by Introducing a “Rigid–Elastic” Structure Through Multi-Scale Synergies",
    year = "2025",
    journal = "Polymers",
    volume = "17",
    pages = "1880",
    month = "Jul",
    doi = "10.3390/polym17131880",
    url = "https://doi.org/10.3390/polym17131880",
    publisher = "MDPI AG",
    issue = "13",
    issn = "2073-4360"
}


Abstract:
<jats:p>Thermoplastic polyurethane (TPU) combines elastomeric and thermoplastic properties but suffers from insufficient rigidity and strength for structural applications. Herein, we developed novel carbon fiber-reinforced TPU (CF/TPU) composites filaments and utilize melt extrusion for 3D printing to maintain elasticity, while achieving enhanced stiffness and strength through multi scale-the control of fiber content and optimization of printing parameters, reaching a rigid–elastic balance. A systematic evaluation of CF content (0–25%) and printing parameters revealed optimal performance to be at 220–230 °C and 40 mm/s for ensuring proper flow to wet fibers without polymer degradation. Compared with TPU, 20% CF/TPU exhibited 63.65%, 105.51%, and 93.69% improvements in tensile, compressive, and impact strength, respectively, alongside 70.88% and 72.92% enhancements in compression and impact energy absorption. This work establishes a fundamental framework for developing rigid–elastic hybrid materials with tailored energy absorption capabilities through rational material design and optimized additive manufacturing processes.</jats:p>

Relevant Snippet:
… of the Mullins effect in polyurethane elastomers under cyclic … microstructural damage during preconditioning. Similarly, the … -reinforced thermoplastic polyurethane (CF/TPU) composite …


Unobtainable Papers:
Dror Raf, Itay Magen, Lee Jordan Dotan, and Dana Solav. Characterization of the mechanical properties of tpu fabricated by sls in different printing orientations. EngRxiv, Jul 2025. URL: https://doi.org/10.31224/4689, doi:10.31224/4689.
A. Vaz-Romero, A. Montoya, J.P. Fernández-Blázquez, and S.C. Cifuentes. Strain-induced crystallization and elastocaloric response in sls-printed thermoplastic polyurethane. Polymer Testing, 153:109014, Dec 2025. URL: https://doi.org/10.1016/j.polymertesting.2025.109014, doi:10.1016/j.polymertesting.2025.109014.
Giorgia Scetta. Fatigue cracking of thermoplastic elastomers. PhD thesis, Agence Bibliographique de l’Enseignement Supérieur, 2020. URL: https://doi.org/10.70675/997a8d4bz6628z407bza822z254c0650766e, doi:10.70675/997a8d4bz6628z407bza822z254c0650766e.
Shuze Zhu, Nikolaos Lempesis, Pieter J. in ‘t Veld, and Gregory C. Rutledge. Molecular simulation of thermoplastic polyurethanes under large compressive deformation. Macromolecules, 51:9306-9316, Nov 2018. URL: https://doi.org/10.1021/acs.macromol.8b01922, doi:10.1021/acs.macromol.8b01922.
A. Avanzini and D. Gallina. Effect of cyclic strain on the mechanical behavior of a thermoplastic polyurethane. Journal of Engineering Materials and Technology-transactions of The Asme, 133:021005, Apr 2011. URL: https://doi.org/10.1115/1.4003101, doi:10.1115/1.4003101.
Florian Krebs, Michael Johlitz, and Alexander Lion. Mullins Effect: Overview of Recent Advances, pages 126-146. Springer Nature Switzerland, Jan 2026. URL: https://doi.org/10.1007/978-3-032-09384-4\_9, doi:10.1007/978-3-032-09384-4\_9.
Cong Shi, Chen‐Hu Yuan, Lan‐Wei Li, Wei‐Jian Wu, Wen‐Yu Jiang, Shun Liu, Zhao‐Xia Huang, and Jin‐Ping Qu. Cyclic pulsating pressure–induced structural evolution and interfacial coupling in <scp>tpu</scp> / <scp>cnt</scp> composites. Journal of Applied Polymer Science, Feb 2026. URL: https://doi.org/10.1002/app.70638, doi:10.1002/app.70638.
Shuze Zhu, Nikolaos Lempesis, Pieter J. in ‘t Veld, and Gregory C. Rutledge. Molecular simulation of thermoplastic polyurethanes under large tensile deformation. Macromolecules, 51:1850-1864, Feb 2018. URL: https://doi.org/10.1021/acs.macromol.7b02367, doi:10.1021/acs.macromol.7b02367.
Julia de Castro Motta, Saeedeh Qaderi, Ilenia Farina, Narinder Singh, Ada Amendola, and Fernando Fraternali. Experimental characterization and mechanical modeling of additively manufactured tpu components of innovative seismic isolators. Acta Mechanica, 235:1637-1648, Dec 2024. URL: https://doi.org/10.1007/s00707-022-03447-5, doi:10.1007/s00707-022-03447-5.
Mohammed Jaradat, Eslam Soliman, and Mahmoud Reda Taha. Experimental investigation of 3d-printed elastomeric dampers. Lifelines 2022, pages 595-604, Nov 2022. URL: https://doi.org/10.1061/9780784484449.053, doi:10.1061
```