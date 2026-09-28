# Edison ANALYSIS brief: objective-definition rubber duck

- **Task ID:** `9c0ab4c7-946a-47d9-887c-eed1d0238faf`
- **Job:** `ANALYSIS`
- **Submitted:** 2026-08-24T20:44:23Z
- **Fetched:** 2026-08-24T20:59:07Z
- **Status:** success

---

Question:

# Rubber-duck request: audit our objective-definition history and critique a swap

We are optimizing 3D-printed class-1 tensegrity T3 prisms (3 PLA struts, 9 TPU
85A tendons, ~20 g printed) as impact absorbers. A bench campaign (drop tower,
Lansmont M23, 60 in drop onto a 1/2 in PU mat, ~101 drops per article, n = 9
articles) and a simulation-only mirror campaign (MuJoCo drop-tower analogue,
`drop_tower_sim.py`, attached) share a 2-objective formulation. The objective
definition has been revised repeatedly, and the operator has asked us to lay
out the full chain so a fresh reviewer can spot inconsistencies. Please act as
that reviewer.

## The chain of objective definitions, in order, with what killed each

1. Regime sims (earlier work, not attached): minimize F_peak, maximize
   SEA_J_per_g, maximize eta under two application regimes. Killed for the
   bench-mirror campaign because F_peak at the rigid-strut tier was a static
   support-load proxy (crutch median F_peak/(m g) = 1.002), SEA was a peak
   ELASTIC strain-energy proxy (~10^3 below incoming KE/mass), and the twist
   axis was never consumed by the model plumbing.
2. Bench campaign objectives (PR #102, still current on the bench): minimize
   t180 = CFC-180-filtered transmissibility (top-vertex peak / base-plate
   peak), and minimize e_reb_mJ = e_rebound * m_printed * g * h where
   e_rebound is the restitution VELOCITY ratio read off the time to second
   impact.
3. First simulated mirror held constant SOLID CAD mass, leaving printed mass
   free: over a 68,944-design sweep, rho(e_reb_mJ, mass_g) = 0.99993 while
   simulated e_rebound spanned 0.34 %. The objective was printed mass in
   disguise. Fixed by projecting onto constant PRINTED mass (20.23 g).
4. On the constant-mass manifold the confound is gone but the second
   objective died: simulated e_rebound spans < 1 % across the whole design
   space because the calibrated Hunt-Crossley mat owns the loss budget (it is
   deliberately calibrated to the measured input pulse, NOT to restitution:
   a mat lossy enough to match measured e ~ 0.02 peaks near 300 G, far above
   the tower's 208 G, because the rig loses energy through rails/anvil/mount
   paths the model does not carry). Also rho(sim e_rebound, sim t180) = +0.84
   concordant, so the campaign was effectively single-objective. Meanwhile
   MEASURED e_rebound is real (spans 2.46x, between-article spread ~15x
   within-article noise) but hints at ANTI-correlation with measured t180
   (rho = -0.57, n = 8, p = 0.14): the one genuinely attenuating article has
   the HIGHEST rebound.
5. Proposed bench replacement: maximize zeta_pct (the article's own modal
   damping from the post-impact ringdown; spans 6.4-31 %, independent of
   measured t180 at rho = +0.07, already measured per drop). Adopted as a
   bench-only channel.
6. Tier-C simulation CANNOT resolve zeta (zeta_analysis.md attached): the
   measured ringdown band (294-468 Hz) is strut flexure, which rigid struts
   do not have (sim modes sit at 22-96 Hz); the model has a parasitic damping
   floor (~12 %) above the least-damped articles; the design response of sim
   zeta is chaotic mode-swapping, not physics; and injecting measured
   per-article damping into the tendons moves the objectives by < 0.2 %
   because the mat owns the loss.
7. THE NEW STEP WE WANT CRITIQUED: swap the simulated campaign's second
   objective from e_rebound to peak_tendon_strain = max over time and cables
   of TPU tension strain above slack length (minimized), keeping minimize
   t180. Screening over 128 Sobol designs on the constant-mass ratio manifold
   (pr102_objective_screen*.csv attached; 78 printable):
     - e_rebound: rel span 0.65 % (dead, confirmed)
     - t1000, out_180_g: rho vs t180 = +1.00 (pure duplicates)
     - in_180_g (null control): span 0.10 % (calibrated mat working)
     - pulse_ms: span 0.5 % (dead)
     - peak_tendon_strain: span 63 %, rho vs t180 = -0.41, driven by
       cable_over_strut_d (-0.76) and twist (-0.32) -- the one candidate that
       consumes the twist axis
     - peak_tendon_energy_mJ: span 157 %, rho = -0.87 (near-mirror of t180)
     - stroke_mm: span 122 %, rho = -0.89 (near-mirror)
   Rationale for the winner: genuine trade-off (the compliant articles that
   shield the payload strain their tendons hardest -- the same sign as the
   bench's t180 vs rebound hint), direct physical reading (TPU break/fatigue
   margin; TPU 85A elongation at break is large but cyclic loading at 100+
   drops makes strain a survivability proxy), and moderate independence so
   the front has genuine 2-D structure rather than a sliver.

## What we want from you

A. AUDIT THE CHAIN (the rubber-duck part). Steps 1-7 were decided across many
   sessions. Are any of the steps mutually inconsistent, circular, or
   over-claimed given the attached data? In particular: is the argument in
   step 4 for "the mat owns the loss budget" compatible with the argument in
   step 6 item 4? Is the concordance rho = +0.84 (sim) vs anti-correlation
   -0.57 (bench) contradiction correctly attributed to the missing loss
   mechanism rather than to a sign error somewhere?
B. CRITIQUE THE SWAP. Is minimize peak_tendon_strain a defensible second
   objective, or should strain be an OUTCOME CONSTRAINT (strain <= TPU
   allowable) with the campaign single-objective in t180? When is each
   formulation right? Note the anti-correlation means minimizing strain
   pushes toward stiff articles, i.e. against t180 -- is a trade-off front
   between transmissibility and a survivability proxy decision-useful for
   choosing what to print next, or is it optimizing an unmeasured quantity?
C. SIM-BENCH ASYMMETRY. The bench pair would be (t180, zeta_pct) and the sim
   pair (t180, peak_tendon_strain) -- different second axes. For later
   sim+bench fusion (multi-task / discrepancy GPs), is it a problem that the
   two campaigns optimize different second objectives, and how would you
   structure the data model so the sim still contributes despite that?
D. ANYTHING WE MISSED. Given the attached measured channels (drop-results
   CSV: t180, t1000, e_rebound, fn_hz, zeta_pct, dv health flags) and the
   simulated observables in drop_tower_sim.py, is there a better
   sim-resolvable second objective we did not screen? Note strut flexure /
   material damping / rig loss paths are all absent at this tier by
   construction.

Answer from the attached files where possible; flag any claim of ours you
cannot verify from them.

---

## Reviewer verdict

The chain is mostly coherent through the diagnosis that simulated restitution is unusable. I would **not approve step 7 as implemented**, however. The attached simulator does not currently calculate physical TPU strain in a mechanically consistent way. Treat the present `peak_tendon_strain` as a **geometric over-length diagnostic**, not a survivability objective, until the tendon model is corrected and validated.

Two earlier issues also need correction:

1. `e_reb_mJ = e_rebound * m g h` is **not rebound energy** if `e_rebound` is a velocity ratio. Rebound energy is
   $$E_{reb}=e_{rebound}^{2}mgh.$$
   The existing quantity has units of energy but the wrong dependence on restitution. Across the seven mass-mapped bench articles, using $e$ versus $e^2$ does not change the rank ordering, so it does not reverse the reported trade-off. It does change the physical interpretation and magnitude substantially. For measured $e=0.020$–0.050, the current formula exceeds actual rebound energy by roughly 20–49×. Rename it or square $e$.
2. The attachment contains **8 articles and 810 valid drops**, not 9 articles. Seven have `zeta_pct`; only six have both a zeta mean and standard deviation. Claims about nine articles may refer to an unavailable article and cannot be verified here.

## A. Audit of the chain

### Steps 1–3

The conceptual decisions are consistent, subject to unavailable evidence:

- I cannot verify the earlier regime-simulation values, including the crutch ratio of 1.002, the ~10³ strain-energy gap, or the unused twist plumbing, because those outputs are not attached.
- The constant-printed-mass correction is sound. In the supplied screen, all 78 printable designs have exactly **20.23 g** mass. I cannot independently recompute the earlier 68,944-design result, $\rho=0.99993$, because that sweep is absent.
- The bench restitution definition is verified: all eight rows satisfy
  $$e=\frac{g t_{second}}{2v_{in}}$$
  to maximum absolute error **1.8×10⁻⁵**. There is no evident sign or velocity-ratio error in that extraction.

The flaw is the name and formula of `e_reb_mJ`, not the measured `e_rebound` sign.

### Step 4: what “the mat owns the loss budget” can and cannot mean

Steps 4 and 6 item 4 are compatible only with more precise wording:

- In the **implemented model**, the fixed mat/contact and numerical/constraint mechanisms dominate the modeled global restitution response. Article tendon damping has little leverage on the reported objectives. The attached `zeta_analysis.md` reports that damping injection changes `t180` by a median **0.12%** and simulated `e_rebound` by a median **0.009%**.
- In the **physical rig**, the mat plainly does *not* account for all measured loss. Simulated restitution is ~0.61, versus measured **0.020–0.050**. The missing loss must be outside the modeled pathways, but the attachments do not identify how much belongs to rails, anvil, mount, tendon hysteresis, joint friction, or other mechanisms.
- During the post-release ringdown used to estimate zeta, the mat is no longer active. The reported ~12% simulated damping floor is attributed instead to solver/integrator/constraint and mode-coupling effects. Thus “mat owns the loss” should not be used to explain that floor.

Suggested wording: **“The calibrated contact dominates variation in simulated global restitution, while omitted rig and article mechanisms dominate the unexplained bench loss.”**

### Simulated +0.84 versus bench −0.57

This is not evidence of a sign error, but neither is it evidence that one specific missing loss path causes the reversal.

From the attached bench table:

- `t180` versus measured `e_rebound`: Spearman $\rho=-0.571$, $n=8$; asymptotic $p=0.139$, exact permutation $p=0.151$; bootstrap 95% interval **[−0.973, +0.309]**.
- Restricting to the five `healthy` articles gives $\rho=0.00$.
- Leave-one-article-out correlations range from **−0.714 to −0.357**.

The negative point estimate is a useful hypothesis, driven partly by the attenuating `6lhxfy`, but it is not an established bench relationship. Conversely, simulated `e_rebound` moves only **0.65%** in the supplied screen. Its strong rank correlation with `t180` ($\rho=+0.819$ here; +0.84 is reported for the larger unavailable sweep) describes ordering over a nearly flat response. It should not be interpreted as strong physical coupling.

So the safe conclusion is:

- no detected sign/extraction error;
- sim and bench do not demonstrate transferable restitution ordering;
- missing mechanisms are a plausible class-level explanation;
- the attachments cannot assign the disagreement specifically to rig loss rather than rigid-strut dynamics, tendon hysteresis, mounting, or model-form error.

### Steps 5–6: zeta

Tier C rejection of simulated zeta is well supported by `zeta_analysis.md`: simulated **22–96 Hz** modes do not overlap measured **294–468 Hz** modes; the model lacks strut flexure; and damping injection barely moves the campaign objectives.

The bench-side adoption is more tentative than stated:

- Measured zeta spans **6.38–31.04%** across seven articles.
- Its correlation with `t180` is $\rho=+0.071$, exact $p=0.906$, with a bootstrap interval spanning nearly the full range, **[−0.870, +0.961]**.
- Its leave-one-out correlation ranges from **−0.143 to +0.714**. Removing `autv5r`, the lowest-zeta article, produces the +0.714 value.

“Independent of `t180`” is therefore too strong. Say **“no association was detected in seven articles.”** Also, maximizing modal damping is not automatically equivalent to better impact absorption, especially when that modal family does not control `t180`. I would keep zeta as an exploratory bench response until the next plate confirms its design response and repeat/drop-order stability.

## B. Should peak tendon strain be an objective or a constraint?

### The implementation problem comes first

`drop_tower_sim.py` sets each spatial tendon as:

```xml
<spatial range="0 rest" stiffness="k" damping="c"> ... </spatial>
```

but does not set `springlength`. It then post-processes

```python
ext = max(data.ten_length - rest_len, 0)
strain = ext / rest_len
energy = 0.5*k*sum(ext**2)
```

According to the official [MuJoCo XML reference](https://mujoco.readthedocs.io/en/latest/XMLreference.html#tendon-spatial):

- `range` is an **allowed tendon-length range imposed by the constraint solver**;
- `springlength` is the elastic resting length;
- when `springlength` is omitted, its default `-1` derives the resting length from the reference configuration.

The simulator therefore uses `range[1]` as a solver-enforced maximum length, while the postprocessor treats that same value as TPU slack/rest length. Those are not equivalent. At initialization, the reported geometric over-range is already

$$\frac{L_0-0.98L_0}{0.98L_0}=2.041\%.$$

The attached screen’s reported peaks are **5.97–11.03%**, but they are maxima of geometric length relative to the limit, not validated material strains. Likewise, `peak_tendon_energy_mJ` is explicitly a nominal proxy and is not the simulator’s actual elastic or constraint energy.

This matters more than the objective-versus-constraint choice. Before campaign use:

1. represent cable elasticity with the intended `springlength`/dead-band or a validated constitutive implementation;
2. decide whether a hard length limit is physically intended and, if so, keep it separate from elastic slack length;
3. record actual per-tendon force, strain, strain rate, peak identity/time, and solver-limit force;
4. perturb timestep, integrator, constraint impedance, prestrain, cable modulus, and payload mass;
5. validate strain or extension against high-speed video, digital image correlation, or an instrumented coupon/article test.

### After correction: objective versus constraint

Use **a constraint** when:

- there is a defensible allowable strain or fatigue-damage limit for the printed TPU process, temperature, print orientation, prestrain, and 100+ cycle duty;
- failure risk is accept/reject rather than continuously valued below the limit;
- the model’s uncertainty can be propagated, preferably as a chance constraint such as
  $$P(\varepsilon_{peak}\leq\varepsilon_{allow})\geq0.95;$$
- the scientific goal remains impact attenuation.

Then optimize `t180` subject to printability, envelope, stroke, and tendon survival. This is the cleaner formulation for a safety requirement.

Use **a second objective** when:

- no credible allowable exists yet;
- lower strain plausibly improves life over the whole relevant range;
- the next-print decision explicitly values learning or trading attenuation against durability;
- stakeholders can choose a point from that trade-off after seeing both axes.

The supplied screen does contain a real numerical trade-off after printability filtering:

- 78 printable designs;
- strain relative span **63.1%**;
- $\rho(t180,\varepsilon_{peak})=-0.406$, $p=2.3×10^{-4}$, bootstrap 95% interval **[−0.584, −0.196]**;
- the relationship is stable across the two Sobol row halves ($\rho=-0.416$ and −0.391) and leave-one-out ($\rho=-0.431$ to −0.382);
- 9 of 78 points are nondominated under the two minimized quantities.

That is decision-useful geometry, not a duplicate objective. But **“consumes twist” is not enough to validate it**. Strain is primarily driven by cable geometry: $\rho=-0.764$ with `cable_over_strut_d` and **−0.877 with printed cable diameter**; a rank-linear model using the four design axes explains **89.7%** of its rank variation. It may simply reward thick cables. Twist contributes ($\rho=-0.315$), but it is not the main driver.

My recommendation is a staged formulation:

1. **Do not launch BO on the current metric.** Fix and validate the tendon semantics first.
2. Until an allowable is known, retain corrected peak strain as a **reported diagnostic or exploratory second response**, and deliberately print several points spanning the predicted attenuation–strain front.
3. Run TPU coupons and article-level cyclic tests to estimate a fatigue limit or survival curve under representative strain amplitude, mean strain, rate, and cycle count.
4. Once that relationship exists, replace raw peak strain with a probabilistic **survival/damage constraint** and optimize `t180`.

Raw peak strain alone is an incomplete fatigue proxy. Cyclic life depends on strain amplitude, mean/prestrain, rate, hysteresis/heating, stress concentration at joints, and cumulative cycles. The current maximum over nine tendons also gives no information about whether one tendon spikes briefly or several experience repeated high-amplitude cycles.

## C. Different bench and simulation second axes

Different second objectives are not intrinsically a problem for fusion. They are a problem only if you pretend both campaigns inhabit one common two-objective space or compute pooled hypervolume from unmatched axes.

Use a **partially observed multi-output model** indexed by design $x$, campaign/fidelity $s$, and response channel $k$:

- shared channel: `t180`;
- bench-only channels: `zeta_pct`, measured restitution, frequency and health responses;
- simulation-only channels: corrected tendon strain, stroke, tendon force/energy diagnostics;
- task-specific observation noise and a bench discrepancy term.

For example,

$$t_{bench}(x)=\alpha+\beta t_{sim}(x)+\delta(x)+\epsilon_b,$$

where $\delta(x)$ is a bench discrepancy Gaussian process and $\epsilon_b$ reflects article/session uncertainty. Fit the transfer using paired simulated and measured designs. Given the already reported weak transfer for `sim_t180` ($\rho=+0.50$ over seven mapped articles in `pr102_sim_campaign.md`), do not force $\beta=1$ or a small discrepancy.

Model zeta and strain as separate outputs with missing-by-design observations. Cross-output covariance may be learned only if supported by paired designs or defensible latent structural features. Do **not** treat simulated strain as a pseudo-measurement of zeta, and do not infer their relationship merely because both are “structural.”

For acquisition:

- use simulation cheaply to map `t180`, corrected strain and feasibility;
- use bench evaluations to update bench `t180`, zeta and discrepancy;
- select prints by expected improvement in **bench `t180` under survival constraints**, plus an explicit information-gain term if learning the discrepancy or zeta surface is a goal;
- report separate campaign Pareto sets. A joint decision front is available only after all decision criteria are put on common predicted outputs, for example predicted bench `t180`, predicted bench zeta, and probability of tendon survival.

Thus the simulation still contributes through the shared `t180` channel, feasibility, mechanistic covariates, and constraints. It need not share every objective.

## D. Better second objectives or diagnostics

No attached Tier-C observable is clearly superior as a *validated* second performance objective.

- `t1000` and `out_180_g` are duplicates of `t180`: $\rho=+0.997$ and +1.000. Indeed, `t180 = out_180_g/in_180_g` to maximum tabular error **4.4×10⁻⁶**, while `in_180_g` spans only 0.10%.
- `pulse_ms` and `e_rebound` have only **0.49%** and **0.65%** span.
- `stroke_mm` and nominal tendon energy have large spans, **122%** and **157%**, but are near-mirrors of `t180` ($\rho=-0.890$ and −0.875). They are useful constraints or mechanism diagnostics, not independent impact-performance objectives.
- Simulated modal frequency or zeta belongs to the wrong mode family and should not be promoted.

The most useful additions are therefore **constraint-oriented diagnostics**, not another arbitrary objective:

1. corrected per-tendon peak strain and strain amplitude;
2. peak and cumulative tendon force or stress, using actual model forces rather than `k×extension` proxies;
3. strain-rate and hysteretic energy per cycle/drop;
4. stroke and minimum clearance/bottoming margin;
5. solver-resolved energy accounting: mat work, tendon elastic energy, tendon damping work, constraint work, and residual numerical energy;
6. sensitivity of all of the above to prestrain, modulus, damping, timestep, payload mass, and impact speed.

An energy ledger is especially important. It would turn “the mat owns the loss” from an inference into a quantified statement and expose numerical constraint work.

`pr102_sim_campaign.md` reports that a separate Tier-C `SEA_J_per_cm3` observable correlated with measured `t180` at $\rho=-0.93$ over seven articles. That may be useful as a surrogate feature or prior for bench `t180`, but it is not an independent second objective and its source CSV was not attached, so I cannot reverify it.

## Claims not verifiable from the attachments

- n = 9 articles; only 8 are present.
- The earlier regime-simulation numerical claims in step 1.
- The 68,944-design mass-confounding statistics.
- The larger-reference-sweep simulated $\rho=+0.84$; the supplied 78-printable screen gives +0.819.
- The ~300 G result from calibrating to measured restitution.
- The zeta injection, damping-floor, and mode-sweep numbers beyond the summaries in `zeta_analysis.md`, because its referenced output CSVs and script are absent.
- TPU 85A allowable strain or cyclic-life margin. No material/coupon data are attached.

### Discretionary analytical decisions

- Used Spearman rank correlation because the claims concern ordering and the relationships need not be linear.
- Used exact two-sided permutation p-values for the small bench samples; also reported bootstrap percentile intervals to show instability.
- Treated articles, not repeated drops, as independent units because drops within an article are repeated measurements rather than independent designs.
- Filtered the simulation screen to its 78 `feasible=True` designs, matching the stated campaign decision set.
- Used a conventional 95% uncertainty interval and two-sided $\alpha=0.05$ only as descriptive thresholds; no causal or confirmatory inference was made.
- Evaluated robustness with leave-one-article/design-out checks and simple Sobol-half splits rather than fitting a complex surrogate to only 78 points.
- Treated `range[1]` as an allowed-length limit and `springlength` as elastic rest length according to the current official MuJoCo XML reference.
