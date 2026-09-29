# Printability screens (PDF page 4, lines 291 to 299)

Passage: [manuscript-body.tex L623-L632 at e613b86](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/e613b86/manuscript/manuscript-body.tex#L623-L632). All dimensions are commanded CAD geometry; no printed member has been measured.

## Plain-language explanation

Before printing, each design is scaled as a whole (twist unchanged) until it hits the mass target: the "projection". **As-projected** means a dimension after that resize, which is what gets printed. Two yes/no checks then run, and each answer is stored as a **flag**, a column in the design table. Nothing is deleted, resized or held back.

1. **Volume:** is πR²H at most 250 cm³? R and H are measured to the joint centres, so this undercounts the real bounding cylinder (corny9: 283 cm³, about 360 cm³ with joint shells). It is a placeholder from the simulation study later cut from the paper, not a printer limit.
2. **Cable:** is the printed TPU cable at least 3.0 mm? That minimum is the **floor**. **Self-bridging** means printing a cable across open air with nothing beneath it; thinner cables were expected to sag. The design space starts at 3.0 mm, but the resize shrinks heavy designs, so a 3.0 mm cable can print at 2.5 mm.

The data support "flags, not rejections", not "defect predictor".

## Where the screens came from

- **2026-05-08:** Edison 25c1c897 diagnoses a spaghetti failure in a PETG test print (2.4 mm top cables spanning 43.3 mm) and lists "3.0 mm or 4.0 mm" cables as one of four fixes ([L105-L118](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/21fd799/edison-trajectories/2026-05-08-t3-prism-bambu-import-25c1c897.md#L105-L118)). It does not discuss TPU.
- **2026-05-12 to 05-20:** the slicer auto-supports the top cables only at 1.3x scale ([Marcus](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4426810002)). Copilot equates this to a cable of about 3.1 mm ([comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4427470120)); a later comment says 3.9 mm and claims, untested, that TPU "can self-bridge" ([comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4462120016)). 3.0 mm becomes the cable lower bound ([7d98451](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/7d98451/bo/t3_prism_sobol_batch.py#L42-L48)).
- **2026-06-21 to 06-27:** Sterling asks for fairness "in terms of mass, volume, and contact area" ([PR #33](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/33#issuecomment-4760939061)). The reply leaves the lander volume budget "TBD" ([analysis](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/94e53a8/simulations/fair_evaluation_analysis.md#L102-L104)), and [04baa03](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/04baa03/simulations/sim_bo_hybrid_campaign.py#L145-L152) picks 250 cm³ to "bind on a meaningful fraction" of simulated shapes.
- **2026-07-30:** Sterling asks that the seed batch meet "the max volume constraint" ([PR #35](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5132975378)). [cf39fe0](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf39fe0/bo/t3_prism_sobol_batch.py#L76-L81) copies both numbers into the batch generator but only flags violations; three seed designs exceeded 250 cm³ and were printed anyway ([reply](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5132983514)).
- **2026-08-21 on:** the campaign code keeps both as flags ([mass model](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf667d8/bo/t3_prism_mass_model.py#L329-L334), ["flagged, not dropped"](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf667d8/bo/t3_prism_bo_campaign.py#L2893-L2899)); neither enters the acquisition ([PR #102](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102#issuecomment-5364709143)).

## Numbers checked

Geometry from the design tables at cf667d8 ([seed](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf667d8/bo/t3-prism-bo-batch.csv), [2](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf667d8/bo/t3-prism-bo-round1-designs.csv), [3](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf667d8/bo/t3-prism-bo-round3-designs.csv), [4](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/cf667d8/bo/t3-prism-bo-round4-designs.csv)), matched to the [print keys](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/adbb771/manuscript/data/). πR²H reproduces every `envelope_cm3` entry; the drop-results geometry columns are these as-projected values, not Sobol coordinates.

| Batch | Design | Article(s) | R (mm) | H (mm) | πR²H (cm³) | Cable (mm) | Screen flags | Logged defects (print key) |
|---|---|---|--:|--:|--:|--:|---|---|
| 1 (seed) | Spec 00 | 9hhbkp | 27.3 | 76.2 | 178 | 4.58 | ok | none logged |
| 1 (seed) | Spec 01 | 6lhxfy | 28.7 | 68.1 | 176 | 2.55 | **under 3.0** | slight misprint near top of one PLA strut; slight indent on one top TPU tendon |
| 1 (seed) | Spec 02 | autv5r | 36.4 | 93.5 | 390 | 3.67 | **over 250** | minor misalignment of TPU tendons near top |
| 1 (seed) | Spec 03 | ebdna8 | 21.7 | 62.3 | 92 | 4.03 | ok | two strings peeled off two bottom TPU tendons during support removal |
| 1 (seed) | Spec 04 | nvxsrv | 22.7 | 85.7 | 139 | 3.70 | ok | ring of misalignment near top of each diagonal tendon (post-pause artifact) |
| 1 (seed) | Spec 05 | 6nheas | 37.9 | 66.0 | 298 | 4.23 | **over 250** | two TPU strings came off two bottom tendons (support-related) |
| 1 (seed) | Spec 06 | 1zm8rv | 27.9 | 74.7 | 182 | 2.71 | **under 3.0** | stringing along diagonal tendons |
| 1 (seed) | Spec 07 | ajhby6 | 26.8 | 66.5 | 150 | 4.39 | ok | single line of filament pulled from bottom struts |
| 1 (seed) | Spec 08 | dea4ls, bag26v, ghmj4y | 30.2 | 104.9 | 300 | 3.32 | **over 250** | stringing; residual PLA on tendon (dea4ls). some stringing on tendon (bag26v). inconsistent tendon cross section near top (ghmj4y) |
| 1 (seed) | S0 ref. | bpx68c | 28.8 | 80.8 | 211 | 3.46 | ok | none major |
| 2 | Spec 03 (trial 13) | r2d2c1 | 27.3 | 65.5 | 153 | 3.28 | ok | one TPU string detached on two top tendons except at support edges; odd foot support print |
| 2 | Spec 02 (trial 12) | r2d2c2 | 22.5 | 53.9 | 85 | 2.70 | **under 3.0** | none logged |
| 2 | Spec 06 (trial 16) | r2d2c3 | 20.1 | 48.2 | 61 | 4.42 | ok | none logged |
| 2 | Spec 01 (trial 11) | r2d2c4 | 30.1 | 45.2 | 129 | 4.14 | ok | spaghetti string on one top tendon; one TPU piece about 1/4 detached from the tendon |
| 2 | Spec 08 (trial 18) | r2d2c5 | 25.1 | 60.1 | 119 | 5.51 | ok | none logged |
| 2 | Spec 04 (trial 14) | r2d2c6 | 20.4 | 49.0 | 64 | 4.49 | ok | none logged |
| 2 | Spec 05 (trial 15) | r2d2c7 | 34.9 | 52.3 | 200 | 2.62 | **under 3.0** | none logged |
| 2 | Spec 07 (trial 17) | r2d2c8 | 26.9 | 74.0 | 169 | 3.70 | ok | spaghetti string on two of the bottom tendons; spanning the entire tendon |
| 2 | Spec 00 (trial 10) | r2d2c9 | 21.9 | 52.7 | 80 | 2.63 | **under 3.0** | none logged |
| 3 | Spec 08 (trial 36) | drran1 / 2dran1 | 25.9 | 62.1 | 131 | 3.11 | ok | none logged / none logged |
| 3 | Spec 05 (trial 33) | drran2 / 2dran2 | 23.1 | 55.4 | 93 | 5.08 | ok | none logged / none logged |
| 3 | Spec 03 (trial 31) | drran3 / 2dran3 | 20.7 | 65.1 | 88 | 4.14 | ok | some tiny bubbles on the diagonal tendons / none logged |
| 3 | Spec 01 (trial 29) | drran4 / 2dran4 | 27.8 | 76.5 | 186 | 3.83 | ok | none logged / none logged |
| 3 | Spec 00 (trial 28) | drran5 / 2dran5 | 23.2 | 55.8 | 95 | 5.11 | ok | some tiny bubbles on the diagonal tendons / none logged |
| 3 | Spec 06 (trial 34) | drran6 / 2dran6 | 21.7 | 52.1 | 77 | 4.78 | ok | some tiny bubbles on the diagonal tendons / none logged |
| 3 | Spec 04 (trial 32) | drran7 / 2dran7 | 29.9 | 60.6 | 170 | 4.11 | ok | some tiny bubbles on the diagonal tendons / none logged |
| 3 | Spec 07 (trial 35) | drran8 / 2dran8 | 25.3 | 60.8 | 123 | 3.04 | ok | none logged / none logged |
| 3 | Spec 02 (trial 30) | drran9 / 2dran9 | 23.0 | 55.2 | 92 | 5.06 | ok | none logged / none logged |
| 4 | Spec 05 (trial 42) | corny1 | 17.7 | 77.7 | 76 | 3.88 | ok | TPU mixed into one layer of a PLA strut |
| 4 | Spec 01 (trial 38) | corny2 | 18.3 | 80.3 | 84 | 4.02 | ok | none logged |
| 4 | Spec 08 (trial 45) | corny3 | 19.7 | 86.5 | 105 | 4.32 | ok | none logged |
| 4 | Spec 07 (trial 44) | corny4 | 20.8 | 91.5 | 124 | 4.58 | ok | many small pores on the TPU diagonal tendons |
| 4 | Spec 03 (trial 40) | corny5 | 20.8 | 91.6 | 125 | 4.58 | ok | none logged |
| 4 | Spec 04 (trial 41) | corny6 | 33.4 | 67.3 | 236 | 2.51 | **under 3.0** | none logged |
| 4 | Spec 00 (trial 37) | corny7 | 34.3 | 67.1 | 249 | 2.58 | **under 3.0** | none logged |
| 4 | Spec 02 (trial 39) | corny8 | 34.7 | 68.3 | 258 | 2.60 | **over 250**, **under 3.0** | none logged |
| 4 | Spec 06 (trial 43) | corny9 | 37.1 | 65.5 | 283 | 2.78 | **over 250**, **under 3.0** | none logged |

- **Thresholds:** as stated, but "build envelope" is misleading.
- **(c) Flags only:** correct. Seven of 48 articles exceeded 250 cm³ and nine were under 3.0 mm; all were printed, and every flagged design except Spec 06 (1zm8rv) has a drop-tested article.
- **(a) "Both seed designs showed stringing":** half right. Only 1zm8rv logged stringing; 6lhxfy logged a strut misprint and a slight tendon "indent/divot". "Both showed tendon defects" ([PR #102](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102#issuecomment-5377560537)) drifted into "stringing". Omitted: batch 2's three sub-floor articles logged "none".
- **(b) Batch-4 attenuators:** diameters right. corny6 to corny9 (t180 0.803 to 0.954) are exactly the sub-floor batch-4 articles, at 2.51 to 2.78 mm. "Only minor stringing" is not in the [print log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5637649574) (fields blank); it comes from a Claude comment ([PR #102](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102#issuecomment-5673641118)).
- **"Defect predictor":** unsupported. Stringing or detached-strand defects were logged on 1 of 9 sub-floor articles and 7 of 39 others.
- **Mass range:** 18.50 to 22.04 g (CV 5.5%) is the eight drop-tested seed articles including S0; the SI's 18.50 to 22.29 g ([L404](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/e613b86/manuscript/supplementary.tex#L402-L404)) adds the untested duplicate dea4ls. Both are correct; the Discussion also uses 22.29 g, so name the set.

## What the defects actually were

Detached strands, as Marcus describes them ([issue #98 log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98)):

- ebdna8: "Two 'strings' were peeled off two of the bottom TPU tendons during the support removal process" ([log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5285048840)).
- 6nheas: "Two strings of TPU came off of two of the bottom TPU tendons" ([log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348663481)).
- r2d2c1: "one string of TPU on two of the top tendons was detached" ([log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5401135583)); r2d2c4: "One piece of TPU was about 1/4 detached from the rest of the tendon" ([log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5401312748)); r2d2c8: "spaghetti string on two of the bottom tendons, spanning the entire tendon" ([log](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5401479186)).
- Logged only as "stringing": [1zm8rv](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5270410479), [bag26v and dea4ls](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5270381244).

These five had cables of 3.28 to 4.23 mm. As Marcus says, they are not spaghetti failures; the log's own "spaghetti string" label likely caused the confusion. The photos would show whether the "stringing" notes are the same failure.

## Related posts

- [PR #35, 2026-08-21](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5373292206): extra care asked when painting supports on the three sub-floor batch-2 articles.
- [Issue #85, 2026-07-17](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/85#issuecomment-5008302271): first use of the name "TPU self-bridging floor".
- [PR #33, 2026-08-24](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/33#issuecomment-5398395837): in the simulation study both checks were hard constraints.
- [PR #102, 2026-09-15](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102#issuecomment-5673199005): "the floor is evidently soft here", after the corny prints.

## Suggested rewrite

> Each projected design was also checked against two printability limits, recorded as warnings and never used to reject or modify a design. The first compares $\pi R^2 H$ with 250 cm³, where $R$ is the radius of the circle through the joint centres and $H$ the joint-to-joint height. This is a placeholder packing budget from an earlier simulation study, not a printer limit; seven printed articles (five designs) exceeded it. The second is a 3.0 mm minimum on the printed TPU cable diameter, adopted after early PETG test prints whose thin, unsupported top cables failed. The projection rescales the whole cell, so a design at the 3.0 mm bound of the cable variable can print thinner: nine articles printed at 2.51 to 2.78 mm, including all four batch-4 articles with $t_{180} < 1$. With hand-painted tendon supports all nine printed: one logged stringing, one a slight tendon indent, and seven no defects. The most common tendon defect, a TPU strand that did not fuse to the tendon and separated from it, was logged on five articles with cables of 3.28 to 4.23 mm. The 3.0 mm value is therefore a conservative rule for this workflow, not a demonstrated defect threshold.
