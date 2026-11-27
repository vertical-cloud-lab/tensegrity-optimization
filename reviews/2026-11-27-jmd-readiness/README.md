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
| Running text (texcount, todo notes excluded) | about 12,300 words, plus 1,460 in captions | 8,500 words, plus 1,140 in captions |
| Supplementary Information | 19 pages | 25 pages (after the second run) |
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
- Also checked against the code and data and now stated: the simulator
  applies the standard J211/1 filter (unlike the bench pipeline), its 2%
  tendon prestrain only keeps the rigid struts from forming a mechanism,
  the pair screen excluded two named control pairs and its span criterion
  was a judgment with no numeric cut, Fig. S7's "Reference cloud" is the
  reference sweep, the mat crossover blinded the analyst to the shuffled
  blocks' key, the per-print mass offsets are against rendered-volume
  estimates, the learned noise matches the unscreened print scatter, and
  bag26v and bpx68c are the tested specimens printed with the 0.4 mm
  nozzle.

Still open in the SI, for a co-author:

- Fig. S1 shows the five joints no specimen used, but not Design F, the
  joint every specimen used. Add a Design F render or cut the figure.
- The printed-mass model's calibration set, sample size and whether its
  0.378 g residual is in-sample, and why the fitted infill (23.6%)
  differs from the commanded 15%. (The per-print offsets are now stated
  against each specimen's rendered-volume estimate, as the code computes
  them.)

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
| Keywords from JMD's article-keyword list (JMD) | Changed to design optimization, data-driven design, design of experiments, metamodeling, design of engineered materials system, plus tensegrity (only "design of experiments" was on the list before). The authors may restore any old term |
| Abstract 150 to 200 words, Latin characters only, background, method, results, conclusions (JMD) | 200 words, no symbols. Rewritten in places (Section 3.2); @sgbaird should approve the wording, since it started as his text |
| Order: Acknowledgment, Funding Data, Conflict of Interest, Data Availability, Nomenclature, References, caption lists (ASME) | Met; Nomenclature added this session |
| Every reference has a DOI (ASME) | 53 of the 57 main-text references; the four without are three NASA technical reports (NTRS URLs given) and the PMLR Ax paper, none of which has a DOI to give |
| Use ASME journal abbreviations | The new JMD and J. Appl. Mech. entries use the class's `jmd` and `jam` macros |
| SI units, with U.S. customary in parentheses if used (ASME) | Met (the 0.5 in mat thickness now also reads 12.7 mm) |
| Figures: TIFF or EPS at production; first submission as PDF is fine (ASME) | Convert at acceptance |
| Third-party images need permission (ASME) | The Fig. 1 Design panel reuses the proposal's BO panel (lab-made); all photographs are lab-made. No third-party material found |
| Length: 9,000 words or nine pages (JMD instructions), 12 typeset pages (JMD FAQ), 12,000 word-equivalents (ASME) | About 12.6 typeset pages through the references; 8,500 words of text plus 1,140 in captions; about 11,900 word-equivalents; see blocker 9 |

The cheapest step to 12 pages: Figs. 4 and 5 are 4.8 in wide natively
and run across both columns. Regenerated at single-column size with text
of at least 7 pt (their scripts need a run that can execute Python), they
would save about half a page; simply shrinking the current files makes
their legends about 5 pt, which is too small (tested and reverted).

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

### Submission-day checklist

- [ ] Blockers 1 to 10 of Section 2 closed or consciously accepted
- [ ] Manuscript PDF built from the final source (line numbers on, which
      ASME requires for first submission); SI as a separate PDF
- [ ] Title, abstract (150 to 200 words, no symbols), keywords from JMD's
      list, entered in the submission system exactly as in the PDF
- [ ] All five authors with department, mailing address and e-mail;
      corresponding authors marked
- [ ] Cover letter final, with the prior-dissemination statement and the
      verified suggested reviewers (BYU names excluded)
- [ ] AI-use confirmation answered consistently with the Acknowledgment
      and Methods (blocker 1)
- [ ] Data Availability Statement true on the day: branches merged or
      tagged, LICENSE present
- [ ] Funding Data with award numbers; Conflict of Interest statement
- [ ] Figures: PDF is fine for review; TIFF or EPS files at acceptance
- [ ] If LaTeX source is uploaded: strip the `\todo` notes and the
      non-printing `% TODO` and process comments (they name people,
      branches and agent sessions)

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

## 9. Second run: fresh-eyes read, final rebuild (2026-11-27, run 46066320059)

The first run stopped at 20:38 UTC when its seat hit the five-hour limit,
before its last three items. This run finished them.

### 9.1 How the fresh-eyes read was run

Three reviewers that had not seen any earlier edit read the condensed
draft independently. Each got only the committed PDFs (`01f0da4`), the
LaTeX sources and `manuscript/data/`, and was told not to open anything
under `reviews/`, the latexdiff PDF, the git history or the PR comments,
so that none of them was anchored on this review or on earlier ones:

- a JMD reviewer and Associate Editor (profile A of the target-audience
  document, with profiles B and C in mind), on the main text;
- a consistency and copy-edit audit: numbers stated more than once,
  counts, definitions before use, the rebound objective's naming,
  cross-references into the SI, and house style;
- an SI reviewer: whether each main-text pointer into the SI lands on
  content that supports it, and whether the reorganized SI reads on its
  own.

Two smaller checks ran alongside: the cover letter against the
manuscript, and where each item the Data Availability Statement promises
actually lives.

### 9.2 What the fresh-eyes read found

The JMD reviewer recommended **major revision**: "the evidence for the
loop's effectiveness depends on objective and screening choices that do
not hold up under the paper's own rules". The copy-edit audit recomputed
about 120 quantitative claims (every hypervolume, the 56% and 35% gains,
every MAPE and baseline, the correlations, the mass statistics and the
front membership) and found them consistent with the tables and data.
The SI reviewer confirmed every main-text SI pointer resolves.

Two findings are new, and both were checked against `manuscript/data/`
before anything changed:

1. **The rebound fraction is cut off by its own search window.** The
   pipeline looks for the second contact between 15 and 70 ms after
   impact. Three first-print sessions have a mean t_second within 0.7 ms
   of 15 ms (r2d2c6 15.70, drran3 15.36, corny4 15.35 ms), and they hold
   the three lowest I_reb values on record (3.9 to 4.1 mg); drran1 sits
   at 69.14 ms. Two of them (r2d2c6, drran3) are on the final front.
   The SI reviewer adds that the 300 to 900 Hz detection band overlaps
   the specimens' own ring-down (260 to 470 Hz), which would pile values
   up at the window start. The text now says these four values are
   bounded by the window rather than measured; fixing it needs a
   re-processing run (new blocker 2b).
2. **The seat gauge screened only batch 3.** Applied retrospectively at
   the code's 1.145 cut, it flags 10 of the 35 first-print sessions:
   bag26v and nvxsrv (seed), r2d2c3, r2d2c5, r2d2c7, r2d2c8, r2d2c9
   (batch 2), drran7 (batch 3), corny1 and corny3 (batch 4). r2d2c3, at
   gauge 1.86, is the campaign maximum (t180 = 1.334). None was
   re-seated. The text now says so.

### 9.3 Fixed in this run

| Where | Was | Now |
|---|---|---|
| Methods 3.3, Results 4.2, Limitations | Window-edge rebound values reported as measurements | Disclosed as bounded by the search window (finding 1) |
| Results 4.2, Limitations | Gauge applied to batch 3 only, silently | The 10 retrospective flags stated (finding 2) |
| Abstract (200 words) | "Excluding sessions that failed a seating or drift check, ... near 1 percent, so single-print extremes stay provisional until replicated." The step between the two halves was missing | "...a seating or drift check, which produced every large deviation, ... stay provisional." |
| Abstract, Contributions, Conclusions, Discussion, Limitations, Methods | "35 specimens", "53 tested specimens" | amdjwm was tested but has no weighed mass: 36 specimens in the four batches (35 with both objectives), 54 tested in all (53 with a weighed mass), each count matched to what it covers |
| Contribution 2 | "CFC 180 filtering"; the rebound index "characterized for repeatability before it enters the optimizer" | "nominal" CFC 180; the optimizer that chose batches 2 to 4 used the first-power form |
| Introduction | Fig. 1 first cited after Fig. 2 | Fig. 1 cited where the loop is introduced |
| Introduction, Methods 3.3 | T3, "session", "drift flag" and "batch 1" never defined in the main text | Each defined at first use |
| Methods 3.3.1, Fig. 3, Table 2 | "60 in (1.524 m)", "0.5 in (12.7 mm)" | SI units first, as ASME requires: 1.524 m (60 in), 12.7 mm (0.5 in) |
| Methods 3.3.4 | "about four times the ballistic estimate (median ratio 0.24)" | The 0.24 is the ballistic value over the video ratio; said so |
| Methods 3.2 | Support removal "the main source" of logged defects | The print key's most frequent defects are stringing and bubbles; two strand losses are attributed to support removal (also SI S4) |
| Methods 3.6 | Agents "transcribed our recorded reviews"; "agent session" | Names the faster-whisper model; "agent run" (session means a drop session elsewhere) |
| Results roadmap | Omitted Sections 4.3 and 4.4 | Lists all four |
| Results 4.2 | "supplies a matched comparison" | "budget-matched comparison, in simulation" |
| Results 4.4 | "a random batch already collects about 85% of the pair's reference hypervolume, BO reached 82.6%" (read as random beating BO) | The 85% is the screening sweep's share; BO's 82.6% is against the best-known reference |
| Contributions, Conclusions | "four uninformed sampling baselines" | "three space-filling samplers and a compass search" (compass search is a direct-search optimizer) |
| Fig. 1, Fig. 2, Table 3 captions | "five-variable" space (Table 1 lists more); "each batch" scaled; "printed" / "as-printed" geometry; "one millimeter scale" | Design space of Table 1; each design scaled; commanded post-projection values (dimensions were never measured); one common scale with the 20 mm bar |
| Fig. 4, Tables 3 and 4 captions | "all 35 measured specimens"; script paths in captions | "the 35 first-print specimens with both objectives"; script paths moved to source comments (the Data Availability Statement covers them). The caption lists no longer overflow the page-14 footer |
| Discussion 5.2 | Mass "channel the review flagged" (the review's findings do not mention mass); "revising objectives mid-campaign ... is probably how such loops behave in practice" | Points to the seed batch's mass confound; says the second objective was revised after the final batch |
| Discussion 5.3 | Multi-engine simulation study described nowhere; simulation credited with diagnosing the mass confound | Pointer to the archived study; the unsupported credit removed |
| Limitations | Specimen assignment discrepancy unnamed | Design 08, Section S6 |
| Data Availability | `manuscript/AI-USE.md` cited from Methods but not listed | Listed |
| SI S15 | Hunt-Crossley damping `F = kδ + λδ(−δ̇)` | `F = kδ + λδδ̇` with δ = −z, as `drop_tower_sim.py` computes it (`pen*(k - lambda*vz)`) |
| SI | "3500 g"; "checks the rebound index"; Fig. S2 "replicate plate 1" undefined; Fig. S3 "printed geometry", "one millimeter scale"; S14 "the name the main text now reserves" | 3500 G; the rebound fraction; plate 1 of the replicate study, in black PLA; commanded geometry, 20 mm bar; S14 sentence states the naming without revision history |
| SI title block | Author line 41 pt too wide | Broken over two lines |
| Cover letter | Contribution list did not follow the manuscript's; implied the seed batch had model predictions; self-assessment sentence | Follows the manuscript's five contributions; predictions archived for the three recommended batches; limits stated plainly |

### 9.4 Raised but not fixed, and why

These need data, code that this run could not execute (Python, Perl and
`make` are blocked on this pull request), or an author decision. They are
the reviewers' points a JMD panel is most likely to raise.

| Item | Why not here | Who |
|---|---|---|
| Re-process with a wider second-contact window and a detection band below the ring-down, and flag the window-edge sessions as censored (finding 1) | Needs Python | A Python-capable run, same as blocker 2 |
| Re-seat the 10 gauge-flagged first-print specimens, or report results with them flagged (finding 2) | Needs the drop tower | Lab |
| Hypervolume reference point: with t180 = 1.35, most of the hypervolume lies in the amplifying region. The reviewer recomputed it at t180 = 1.0: 0.37, 1.06, 1.16 and 7.02 across the batches, almost all from corny7 and corny6. Report that sensitivity | Needs the front recomputed and checked | A Python-capable run |
| Recommendations sit on the bounds of the box (15 of 27 at exact corners by the reviewer's count; trials 28, 30 and 33 share a geometry, as do 40 and 44). Disclose, and use 40 and 44 as near-replicates | Needs checking against the design CSVs | A Python-capable run, then @sgbaird |
| The base and top channel calibration (the 0.953 cross-calibration ratio): which channels, which way, and whether it was applied. 15 of the 26 amplifiers lie between 1.00 and 1.05 | Lab knowledge | @me-madsen, @achris0520 |
| Top-vertex mass (sensor, cable and pocket) and the mounting method; whether the weighed mass includes the sensor | Lab knowledge | @me-madsen, @achris0520 |
| Measure printed cable diameters, at least for the attenuators (2.51 to 2.78 mm commanded, below the 3.0 mm screen) | Needs calipers | Lab |
| BO reproducibility details: qNEHVI reference point, MC samples, acquisition optimizer settings, BoTorch version, input normalization | On the campaign branch | A run with that branch checked out |
| "Pre-registered" has no registry behind it; the reviewer suggests "Independent re-analysis of the objective choices" | The heading was set by @sgbaird's request of 2026-10-27 | @sgbaird |
| Present tense for completed work in parts of Methods 3.1, 3.4 and 3.5 | Time; not a correctness issue | Length or style pass |
| Figs. 2(b), 5, S5 and S6 label E_reb as "mass-weighted rebound"; Fig. 2(b) shows E_reb, not I_reb | Needs the figure scripts | A Python-capable run |
| Six reference titles in sentence case; `amendola2014` title has an en dash | Cosmetic | Any run |
| Figure text at 4 to 6 pt in Figs. 1, 2(b) and 6 | Needs the figure scripts | A Python-capable run |

### 9.5 Status of the blockers at the end of this run (2026-11-27, about 21:30 UTC)

Section 2's list stands. What changed or was checked in this run:

- **Blocker 1 (AI policy).** Rechecked against ASME's journal author
  page, which states that ASME prohibits the use of generative AI in the
  creation of content for journal submissions and that authors confirm AI
  was not used to develop their work. Unchanged: the first gate.
- **New blocker 2b (rebound window and gauge flags).** Re-process with a
  wider second-contact window and flag the window-edge and gauge-flagged
  sessions (Section 9.2). Owner: a Python-capable run, with @sgbaird
  deciding whether the results change before or after submission.
- **Blocker 3 (re-seats).** Issue #115 still says drop-tower use is
  halted (last update 2026-10-30); no repair is recorded.
- **Blocker 4 (data and code).** Still no LICENSE, no tags, and the four
  branches unmerged. One more branch is needed than the list said: the
  joint-design study's CAD source is only on PR #39's branch
  (`copilot/explore-joint-design-for-petg-tpu`). This branch must also be
  merged into `main`, which today holds none of `manuscript/`,
  `analysis/` or `scripts/figures/`. The manuscript's todo now lists all
  six.
- **Word file.** `manuscript.docx` was last regenerated on 2026-11-05 and
  predates this review; regenerate it with `make manuscript-docx` in a run
  that can execute Python, together with the Fig. 2(b) relabel.

### 9.6 Realistic submission date (updated)

BYU's fall classes end about 2026-12-10, finals run about 2026-12-12 to
2026-12-17, and winter classes start 2027-01-06, so student work pauses
from mid-December to early January.

- **Earliest plausible: 2026-12-18.** Only if ASME confirms within about
  a week that disclosed AI assistance is acceptable, the team submits
  with the corny7 re-seat still pending (the text already says so), and
  blockers 2 and 4 to 10 close before finals.
- **Realistic: the week of 2027-01-18.** The AI question is answered
  (or the co-author rewrite is done) over December and early January,
  the co-author read-through happens in the first two weeks of the winter
  semester, and the re-seat goes in if the tower is repaired by then.
- **If ASME's answer requires a rewrite and the team wants the re-seat
  first:** late January to early February 2027, depending on the tower.
