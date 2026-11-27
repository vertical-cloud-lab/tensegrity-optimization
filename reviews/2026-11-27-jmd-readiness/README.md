# JMD readiness review, 2026-11-27

Requested by @sgbaird on PR #76 ([comment 7226057609](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/76#issuecomment-7226057609)):
take the manuscript as close to a submission to the ASME Journal of
Mechanical Design (JMD) as possible, review it the way a JMD panel would,
fix what can be fixed, and list what needs a person.

The panel this review imitates is the one `reviews/target_audience.md`
(branch `copilot/who-is-the-target-audience`) predicts: (A) a design
optimization and data-driven design reviewer, most likely also the
Associate Editor; (B) an architected-materials or tensegrity reviewer;
(C) an additive-manufacturing reviewer; and, less likely now that the
crutch tip is only future work, (D) an application reviewer.

How the checks were run. This run could not execute Python, pip, node or
make (the action's guard for pull requests opened by a bot), so nothing was
recomputed by re-running the analysis scripts. Instead, every number below
was recomputed from the committed data with awk, jq and bc, or read from a
committed results file, and the LaTeX was built by hand. Three independent
checks ran in parallel: a recomputation of the quantitative claims, a
Crossref check of all 75 cited references, and a search for JMD and ASME
papers a reviewer would expect to see cited.

## 1. Where it stands

| | Before (`3107245`) | Now |
|---|---|---|
| Main text, typeset | 17 pages + 1 page of caption lists | 13 pages through the references (references fill two-thirds of page 13), + 1 page of caption lists |
| Running text (texcount, todo notes excluded) | about 10,900 words | 8,500 words, plus 1,140 in captions |
| Supplementary Information | 19 pages | 23 pages |
| References in the main text | 69, none from JMD or any ASME journal | 57, six from JMD and J. Appl. Mech. |
| Cited references with a verified DOI | 60 of 75, two of them wrong | main text 53 of 57 (the other four have no DOI to give) |
| Build | clean | clean: no errors, no undefined references or citations |

Commits of this session: [`20fe24a`](https://github.com/vertical-cloud-lab/tensegrity-optimization/commit/20fe24a)
(length pass and first corrections), [`dcf9abe`](https://github.com/vertical-cloud-lab/tensegrity-optimization/commit/dcf9abe)
(numbers audit, JMD citations, Nomenclature, abstract),
[`fe95797`](https://github.com/vertical-cloud-lab/tensegrity-optimization/commit/fe95797)
(references, cover letter, AI-use inventory), and the commits that follow
this file. The latexdiff PDF marks every change against `3107245`.

The science is in reasonable shape for a JMD Research Paper once the
items in Section 2 are done. The binding constraints are not the text but
four things outside it: ASME's AI policy, the unconfirmed record specimen,
the analysis filter, and the data release.

## 2. What still blocks submission, and who has to do it

| # | Item | Why it blocks | Who |
|---|---|---|---|
| 1 | **ASME AI position statement.** Para. IV.A.8: AI tools "may not be used to create, contribute, generate, produce, or otherwise submit substantive portions" of a submission, including "drafting text, creating data, making observations from data, conducting any analysis ... drawing conclusions"; such content "will be rejected". IV.A.10 bars AI from creating or modifying images. The JMD submission form asks authors to confirm AI was not used in developing the work. | The paper's own Acknowledgment and Methods disclose AI use for text, figures, analysis and code, so the authors cannot make that confirmation as things stand, and V.C says non-compliant content will be rejected. The figures are affected too: every plot was drawn by AI-written code, and the photo panels were cropped and labeled by AI-written scripts. | @sgbaird and Jeff Hill decide among: (a) the co-authors rewrite the text in their own words, draw their own conclusions from the analyses, and prepare the photo panels themselves, with AI kept to the editing and coding roles IV.A.7 and IV.A.9 allow, fully disclosed; (b) ask aipolicy@asme.org how the policy applies before submitting (draft below); (c) choose a journal whose policy allows disclosed AI assistance. I have not contacted anyone. |
| 2 | **Analysis filter.** The campaign pipeline (`analyze_capture` on `copilot/add-drop-test-protocol-again`) filters with `butter(2, 1.65*CFC)` run forward and backward, which is about 20% narrower than SAE J211/1. The draft said this had been corrected before the campaign; the code says otherwise. The text now describes what was run. | Every reported t180 and seat-gauge value comes from that filter. On the one drop checked, t180 is unchanged and the CFC-1000 ratio moves from 1.204 to 1.287, so the gauge threshold of 1.145 may shift. A J211 citation with a non-J211 filter invites a rejection on method. | Re-process the sessions with `butter(2, 2.0775*CFC)` forward and backward and regenerate the tables, in a session that can run Python (for example a PR the Claude app opens, per #136). Or keep the current description and accept the comment. Decision: @sgbaird. |
| 3 | **Re-seat corny7 (and corny6).** The record specimen supplies over a third of the 56% hypervolume gain (without it the gain is 35%; without corny7 and corny6, batch 4 adds nothing), and both are single-seating values. Drop testing has stopped since the base-input fault of 2026-10-19 (#115). | A reviewer will ask for the confirmation the paper's own replication rule requires. It is possible to submit without it, as the text now says, but the abstract's headline would rest on an unreplicated session. | Lab (Marcus, Audrey, Jinkwan): repair or replace the base channel, then re-seat corny7 and corny6. Also say what failed on 2026-10-19 (#115 says the 10,000 g accelerometer, the plate-1 check-in says the CH5 cable; the paper says "input-channel instrumentation" until someone confirms). |
| 4 | **Data and code availability.** The statement promises the campaign code, drop-test pipeline, simulation study and video analysis in the repository, but they live on unmerged branches (`claude/issue-98-20260821-0103`, `copilot/add-drop-test-protocol-again`, `copilot/explore-simulations-for-tensegrity`, `claude/issue-134-20261116-1959`), and the repository has no LICENSE. | The link would not resolve to what the paper says it holds. | @sgbaird (repository admin): merge or tag those branches and add a license (the draft suggests MIT for code, CC BY 4.0 for data). Zenodo DOI at acceptance, as stated. |
| 5 | **Author block.** E-mail addresses of Marcus Madsen, Audrey Christiansen and Jinkwan Han are missing (ASME asks for each author's department, university, mailing address and e-mail). | Required by the submission system. | Marcus, Audrey, Jinkwan. |
| 6 | **Lab confirmations** (each is a `\todo` in `manuscript-todos.pdf`): every campaign specimen used the captive-core joint (Design F); the TPU nozzle hardware and 240 °C; the carriage photo in Fig. 1 is a campaign specimen (it may be mdt6ja from the July defect study); the carriage-bounce and video observations behind the rebound caveat. | The text states these as facts. | Marcus and Audrey. |
| 7 | **Funding data.** The MRG award number, and any Utah NASA Space Grant Consortium support. | ASME prints funding data with award numbers. | Jeff Hill or @sgbaird. |
| 8 | **Prior dissemination.** An extended abstract was presented at IDETC-CIE 2026 (Track DAC-10). If it appears in the proceedings, JMD wants its paper number at the end of the title and a statement of what is new. | Disclosure. | @sgbaird or Marcus. |
| 9 | **Length.** Now about 12.6 typeset pages through the references and about 8,500 words of text. That is at ASME's general limit (about 11,900 word-equivalents against 12,000, counting figures and tables by area) and just over the JMD FAQ's 12 pages (pages beyond 12 carry a charge the editor can waive), but JMD's own instructions say 9,000 words "or the equivalent of nine journal pages". | The Editor may return a long paper before review. | @sgbaird: ask the JMD office which limit applies, or cut further. The cheapest further cuts are listed in Section 4. |
| 10 | **Co-author read-through.** Large parts of the text were condensed in this session. The co-authors reviewed earlier versions in detail, and their direct edits to Introduction paragraphs 1 to 3 are untouched, but the condensed Methods, Results and Discussion have not been read by a person. | Accountability (and item 1). | All authors, using `manuscript-diff.pdf`. |

Optional, not blocking: the replicate rank-stability study (27 specimens
printed, record withheld); a budget-matched physical Sobol baseline; the
learned-noise surrogate for the next batch; the metal-analog and
quasi-static campaigns. The paper presents all of these as future work.

## 3. Reviewer pass

### 3.1 Claims against the figures and the data

An independent recomputation from `manuscript/data`,
`manuscript/data/sim`, `analysis/bo-review` and `analysis/logocv-baselines`
reproduced the hypervolume after every batch (14.722, 16.976, 17.133,
23.021), every front, every row of the seed table and of the generated
batch-results table (all 27 rows, with flags), the three-print statistics
(residual sd 0.0087 at 10 degrees of freedom, ICC 0.58 vs 0.06), the
leave-one-design-out metrics, the learned-noise re-analysis, and the
simulated-campaign statistics. It found these errors, all fixed:

| Where | Was | Now |
|---|---|---|
| Methods 3.4 | A single-objective log-EI baseline "retained" to quantify the multi-objective benefit | No such run exists in the campaign code. Removed, with the TuRBO plan. |
| Methods 3.3, SI | The narrow CFC filter "corrected before the campaign" | Describes the filter actually run (see blocker 2) |
| Methods 3.4 | Seed mass vs t180, r = 0.83 (n = 7) | r = 0.82 over the eight mapped specimens (the seven Sobol designs give 0.85; nothing gives 0.83) |
| Results 4.2 | ajhby6 left the front "when the batch-4 record dominated" it | corny6 dominated it; corny7 dominated 6lhxfy |
| Discussion | "more than 1,400 stabilized captures across 35 specimens" | 1,614 across all 53 tested specimens (the 35 alone: about 1,290) |
| Methods 3.3, Results 4.1 | The seed attenuator "reproduced its value within 0.13% across an independent re-seat" | 0.14%, against a shorter, slightly drifting seating on the previous day, not a later re-seat |
| Methods 3.3, Results 4.2, SI | Re-seat threshold "1.15 or more" | 1.145, the code's cut (2dran2 reads 1.1466) |
| Results 4.2 | rho = 0.55, p = 0.13 | p = 0.12 |
| Results 4.2 | Eight batch-3 design means "span 1.028 to 1.045" | Labeled as offset-adjusted means |
| Contributions, Conclusions | Baselines "77 to 79%" | 76.5 to 79.1% |
| Results 4.3, Limitations | E_reb held-out rho_s = -0.40 means the ordering "runs against the measured one" | A predictor that returns each fold's training mean scores rho_s = -0.87 (t180) and -0.79 (E_reb) on these folds by construction, so -0.40 reflects near-flat predictions. The text now leads with R2_oos (0.12 and -0.05 against 0 for the mean) |
| Methods 3.1 | "scaled to a ~50 mm bounding box" | Reference prism: circumradius 28.8 mm, height 80.8 mm |
| SI | Closest drop-replay pair "kept its order" | Effectively tied at 20 drops (difference 0.00006 against standard errors of 0.0003 and 0.0010) |
| SI | Seed specimens "18.50 to 22.29 g" | Printed seed specimens 18.50 to 22.29 g; the eight tested ones 18.50 to 22.04 g |

Claims stated more strongly than the data support, now qualified in the
text:

- **The 56% hypervolume gain.** Hypervolume can only grow as specimens are
  added, and there is no budget-matched physical baseline. Over a third of
  the gain comes from corny7 alone, a single seating (35% without it).
  Results 4.2 and the abstract now say so.
- **"The model chose every design on the final front."** True, but 27 of
  the 35 specimens came from model-recommended batches, so a five-member
  front drawn at random from them would be all model-recommended about a
  quarter of the time (hypergeometric, 0.25). Results 4.2 now says so, and
  the abstract no longer leads with it.
- **Prospective prediction accuracy.** Batch 2's MAPE (14.4%) was worse
  than predicting the training mean (8.6%), batch 3's (3.8%) matched it
  (3.7%), and batch 4's (6.0%) beat it (9.6%). All three are now stated.
- **Coverage of 93%** is 41 of 44 values, and the learned-noise E_reb
  intervals cover 73% because they leave out the learned noise. Stated.
- **The mass confound.** "The projection removed the confound" became
  "the seed correlation did not persist once printed mass was held near
  constant"; batch 4 still shows r = 0.85 because its two families differ
  by about 1 g.

Still open (no fix possible here): the seed positive control rests on one
interrupted 33-drop seating; the "near 1 percent" print-to-print figure
uses a screen (gauge plus drift flag) that was defined after the first two
prints, as the text and abstract now say; the per-batch gains depend on the
hypervolume reference point.

### 3.2 The m·e² objective throughout

- **Text.** Eq. (1) defines I_reb = m e_reb²; every reported value is
  I_reb in mg; E_reb appears only where the text describes the optimizer of
  batches 2 to 4, its archived predictions, or the surrogate audits fit on
  it; VLI appears only as a descriptor. The e-versus-e² comparison moved to
  a new SI section, "Rebound Index: Video Check and First Power Versus
  Square".
- **What e_reb measures.** The abstract used to call it "the fraction of
  impact velocity returned at the top". The issue #134 video tracking (27
  specimens, three filmed drops each) shows that the ballistic estimate is
  about a quarter of the tracked rebound-to-arrival ratio (median 0.24) and
  ranks the specimens similarly but loosely (Spearman 0.52, p = 0.005), and
  that the vertex rises 12.5 to 28.4 mm back toward rest rather than
  hopping 0.3 to 5.9 mm in free flight. The abstract and Methods now call
  e_reb a timing-based index, the draft no longer says its validation is
  "scheduled", and the results files are snapshotted in
  `manuscript/data/video-check/`. The same video shows the attenuators
  returning more of their arrival speed (Spearman -0.59 against t180),
  which independently supports the two-dimensional front.
- **Figures.** Fig. 4 (front evolution) and Fig. 6 (three prints) plot
  I_reb. Fig. 5 (batch-4 predictions) plots E_reb on purpose, because the
  archived predictions are in E_reb, and its caption says so. Fig. 2(b)
  still labels its six specimens with E_reb values; switching them to I_reb
  needs `scripts/figures/build_design_space_figure.py`, which this run could
  not execute. Its caption matches the figure.

### 3.3 BO versus baselines, and the statistics

- **Physical campaign.** No budget-matched physical baseline was run, so
  the only physical comparison is against the campaign's own Sobol seed.
  The text says this plainly, gives the hypervolume caveats above, and
  points to the simulated campaign for the matched comparison. The
  strongest physical evidence that the model helped is prospective: the
  predictions archived before batch 4 ranked its nine specimens with
  Spearman 0.82 (exact recomputation 0.817) and put the record specimen
  first. A reviewer from profile A will still ask for a physical baseline;
  the honest answer is cost, and the Discussion should keep saying so.
- **Simulated campaign.** One-sided exact Mann-Whitney p = 5.4e-6 is the
  floor for ten runs against ten (1/C(20,10)), and it survives a four-way
  Bonferroni correction; BO also won on all ten paired seeds. The control
  pair does not separate (smallest p = 0.018, 0.07 after Bonferroni), and
  the text says so. Two limits a reviewer will raise, both disclosed: the
  envelope pair was chosen by a screen for the pair that random sampling
  covers least, and the simulated optimizer (single-task GP, envelope
  volume, four shape ratios) is not the physical one (SAASBO, rebound,
  twelve inputs).
- **Surrogate audits.** Leave-one-design-out is the right fold structure,
  and the permutation p-values are correct as tests of association, but the
  reference for rank correlations on these folds is the training-mean
  predictor (-0.87 and -0.79), not zero. The text now leads with R2_oos,
  whose reference is zero.

### 3.4 Supplementary Information

An SI review against the main text, the data and the code found about 70
items. Fixed, each code-dependent one checked against the code first:

- Table S5 had four "code of record" placeholders, one of them the
  second-contact rule that defines e_reb. It now gives every parameter as
  implemented: impact location, the ±5 ms peak search (the text said
  about 1.5 ms), the tail-median baseline, the 300 to 900 Hz envelope rule
  for the second contact, the capture exclusions, the filter construction,
  the drift flag and the 1.145 gauge cut.
- The drift flag, used to screen sessions, was never defined. It is now:
  slope steeper than 0.06% per drop with p < 0.01, or more than 2.5%
  between the first and last five stabilized drops.
- Dry-box humidity: the logs say 8% (seed), 11% (batches 2 and 3) and 7%
  (batch 4), not "near or below 8%". This reverses wording requested on
  2026-10-27, because the logged values contradict it.
- The simulator's mat was calibrated to S0's input peak and pulse width,
  explicitly not to its rebound (the module docstring says otherwise; the
  `calibrate` function is what ran). Its 5.30 m/s start speed is the mean
  Δv, about 0.6 m/s above the video-measured arrival speed.
- Objective naming in Table S1, the S7 provenance paragraph, the
  metal-analog plan and the S14 figure discussion.
- The metal-analog section is now "Planned Metal-Analog Comparison" and
  notes that an exact two-sided rank test needs at least five designs.
- Smaller: the SI draft box, a journal-facing introduction with an
  abbreviation list, S-numbered equations, Fig. S1 cited, figures kept in
  their sections, branch names replaced by repository locations, the
  five specimens with strand defects (not two), session time about 70
  minutes of drops (not 90), video coverage from batch 3 on.

Still open in the SI, for a co-author:

- Fig. S1 shows the five joints no specimen used, but not Design F, the
  joint every specimen used. Add a Design F render or cut the figure.
- The printed-mass model's calibration set, sample size and whether its
  0.378 g residual is in-sample; why the fitted infill (23.6%) differs
  from the commanded 15%; and that the per-print offsets are against
  per-specimen predictions, not the 20.23 g target.
- Why the learned noise standard deviation (0.044 to 0.049 in t180) is
  about five times the replicate standard deviation (0.0087).
- Simulation details: the second "existing pair", the screen's
  threshold, which CFC filter the simulator applies, and why 2% tendon
  prestrain for unprestressed cells. Fig. S7's legend says "Reference
  cloud" where the caption says "printable reference sweep".
- What was blinded in the mat-selection crossover experiment.
- Table S3 could carry a nozzle column (bag26v and bpx68c printed with
  the 0.4 mm TPU nozzle).

### 3.5 Additive manufacturing (profile C)

Present and adequate: print settings from the archived slicer projects
(SI), the mass model and its residual, the three-print repeatability, the
defect log, and the statement that member dimensions were never measured.
Open: dimensional metrology of printed members, the joint pull-out and
fatigue tests, and the lab confirmations in blocker 6.

### 3.6 Application framing (profile D)

The planetary-lander motivation is stated once and bounded ("not flight
hardware"). The crutch-tip discussion, previously twelve citations of
clinical literature, is now one sentence of future work with three
citations, which matches the instruction to keep the crutch tip as future
work only.

## 4. ASME template, length and figure rules

| Rule (source) | Status |
|---|---|
| `asmejour` class, two columns, line numbers, page numbers (ASME) | Met |
| Title case, prepositions of four letters or more capitalized (JMD) | Met |
| Abstract 150 to 200 words, Latin characters only, background, method, results, conclusions (JMD) | 200 words, no symbols. Rewritten in places (Section 3.2); @sgbaird should approve the wording, since it started as his text |
| Order: Acknowledgment, Funding Data, Conflict of Interest, Data Availability, Nomenclature, References, caption lists (ASME) | Met; Nomenclature added this session |
| Every reference has a DOI (ASME) | 53 of the 57 main-text references; the four without are three NASA technical reports (NTRS URLs given) and the PMLR Ax paper, none of which has a DOI to give |
| Use ASME journal abbreviations | The new JMD and J. Appl. Mech. entries use the class's `jmd` and `jam` macros |
| SI units, with U.S. customary in parentheses if used (ASME) | Met (the 0.5 in mat thickness now also reads 12.7 mm) |
| Figures: TIFF or EPS at production; first submission as PDF is fine (ASME) | Convert at acceptance |
| Third-party images need permission (ASME) | The Fig. 1 Design panel reuses the proposal's BO panel (lab-made); all photographs are lab-made. No third-party material found |
| Length: 9,000 words or nine pages (JMD instructions), 12 typeset pages (JMD FAQ), 12,000 word-equivalents (ASME) | About 12.6 typeset pages through the references; 8,500 words of text plus 1,140 in captions; about 11,900 word-equivalents; see blocker 9 |

If the 9-page figure applies, these would cut about three pages without
losing results: move Fig. 3 (trace) and Table 1 (design variables) to the
SI and keep one sentence each; move the simulated campaign's table to the
SI and keep its headline sentence; shorten the Background to one
paragraph per subsection; drop the roadmap paragraph.

## 5. Nomenclature, data and code statement

- **Nomenclature.** Added after the Data Availability Statement, Latin
  symbols (capitals first) then Greek, with units.
- **Data Availability Statement.** Uses ASME's "freely available at"
  wording and lists what the repository holds. It is accurate only after
  blocker 4. `manuscript/data/` now also holds the issue #134 video results
  and the round-4 leave-one-out folds, both quoted in the text and
  previously missing from this branch.

## 6. References

All 75 cited keys (main text and SI) were checked against Crossref, arXiv,
PMLR, NeurIPS and NASA NTRS records.

- Two entries were not real: `fraternali2015tensegrity` and
  `michailidis2011establishment` carried DOIs of unrelated papers (a
  boron-carbide constitutive model and a hydroxyapatite synthesis paper),
  and their titles exist nowhere in Crossref. The first is now the same
  authors' JMPS 74 (2015) paper on the softening and stiffening of
  tensegrity prisms, which is what the sentence cites it for; the second
  is replaced in the SI by Li, Magkiriadis and Harrigan (2006) on the onset
  of densification. **Please confirm both.**
- Three NASA entries (`caluwaerts2014superball`,
  `agogino2018superball`, `deitrich2022titan`) had wrong authors, two
  documents merged into one, or the wrong venue; corrected from NTRS.
- Ten DOIs added; nineteen entries had their whole citation stuffed into
  the journal field (they printed as one string); several author and page
  errors fixed.
- Six JMD and ASME papers added, each verified against its Crossref record
  and abstract: Hertlein et al. 2024 (BO for impact-loaded AM lattices),
  Biswas, Fuentes and Hoyle 2022 (multi-objective BO), Liu et al. 2019
  (BO for crashworthy multimaterial structures), Yoo et al. 2021 (BO of
  elastomeric beams), van Beek et al. 2021 (batch sampling with
  replication under heteroscedastic noise), and Cao et al. 2024 (twist of
  self-equilibrated tensegrity prisms). JMD's instructions ask authors to
  include relevant JMD work; the list had none. More candidates, including
  two J. Mech. Robot. tensegrity papers from Jeff Hill's group, are in the
  session notes if the authors want them.

## 7. Cover letter, and a draft question to ASME

[`manuscript/cover-letter.md`](../../manuscript/cover-letter.md): a draft
with bracketed decisions (prior IDETC dissemination, the AI paragraph) and
six suggested reviewers drawn from `reviews/target_audience.md` and the JMD
check, each to be verified for affiliation and conflicts. BYU colleagues
are excluded.

### Draft question to ASME (for blocker 1, option b; not sent)

> Subject: Pre-submission question: disclosed AI assistance in a JMD
> research paper
>
> We are preparing a Research Paper for the ASME Journal of Mechanical
> Design on experiment-driven Bayesian optimization of 3D-printed
> tensegrity-inspired structures. Every data point is a physical drop-test
> measurement made by the human authors. Under our direction, AI coding
> agents (Claude Code by Anthropic, GitHub Copilot) wrote most of the
> campaign, analysis, and figure code, drafted and revised manuscript text
> that we then reviewed and edited, and transcribed our recorded reviews of
> the draft; an AI analysis agent (Edison Scientific) produced mock reviews
> and an audit. Every request to these tools, with its date, order, and
> output, is archived in our public repository, and the manuscript's
> Methods and Acknowledgment disclose this use in the detail Section IV.B of
> the position statement asks for. Paragraph IV.A.8 prohibits AI-generated
> substantive content, while IV.A.9 allows AI assistance in research with
> full disclosure. Before we submit, could you tell us whether a manuscript
> prepared this way is eligible for JMD, and if not, which parts the
> authors would need to redo themselves (for example the text, the
> analyses, or the figures)?

## 8. Realistic submission date

The dates assume the team starts on Monday 2026-11-30, that BYU's
finals week and winter break (mid-December to early January) pause
student work, and that the drop tower is repaired before the re-seats.

- **If the authors resolve the AI question by a co-author rewrite**
  (blocker 1, option a), that rewrite is the critical path: about three
  to four weeks of part-time work for three student co-authors, plus the
  photo panels and a PI read. With the filter re-run, the corny7 re-seat
  and the branch merges done in parallel, a realistic submission date is
  **the week of 2027-01-18**.
- **If ASME confirms that disclosed AI assistance is acceptable**
  (option b), the remaining items take one to two weeks once ASME
  answers and the tower is repaired: **about 2026-12-18** if both happen
  within two weeks, otherwise the week of 2027-01-04.
- **If the authors retarget to another journal** (option c), add a week
  for reformatting to that journal's template and limits.

Not done in this session, and why: the replicate study and re-seats need a
working tower; the filter re-run and the Fig. 2(b) relabel need Python;
the cringe-filter lint needs pip. None of those could run here.
