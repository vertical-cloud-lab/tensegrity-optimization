# Can the drop tower measure per-specimen energy absorption? A review and a metrics primer

**Requested by:** @me-madsen on
[issue #94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94),
2026-08-06. **Scope:** the current drop-tower setup and the data recorded so
far — the ABC × 123 crossover captures described on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5199261361)
(4 channels: CH2–CH4 top-vertex tri-axis output, CH5 base-plate input;
1.25 MHz, 100 ms records, 2 ms pre-trigger) plus the slow-motion video work
— judged against the campaign goal: **optimize T3 prism structures for
energy absorption.**

All in-repo numbers quoted below come from
[`docs/drop-test-abc123-blind-analysis.md`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/add-drop-test-protocol-again/docs/drop-test-abc123-blind-analysis.md)
and its committed per-drop metrics.

---

## 1. The energy ledger of one drop

The instrumented plate carrying the specimen falls 60 in and arrests on the
PU mat stack. Kinetic energy at impact is

```
E_in = ½ M v²,   v = Δv ≈ 5.47 m/s (healthy tower)  →  E_in ≈ 15.0 · M joules
```

with `M` the total falling mass — **which is not logged anywhere in the
repo**, so no energy in this program is currently expressible in joules.
That energy is partitioned, per drop, into:

1. **PU mat hysteresis** — the dominant sink by far; it is what turns a
   ~5.5 m/s arrest into a 1.7–3.2 ms, few-hundred-G pulse.
2. **Tower losses** (rail/pin friction, structural damage) — normally
   small, but issue #92 showed a damaged tower silently eating **26–38 %**
   of the drop energy. Larger than everything specimen-related combined.
3. **Fixture/plate dissipation** — unquantified, assumed small.
4. **The specimen** — which receives only a small slice of vibrational
   energy through its base, rings at ~500–550 Hz for 5–13 ms, and hops off
   the plate at ~2–3 % of the impact velocity.

The specimen never enters large deformation. It responds elastically,
rings, and settles. **The rig is a shock-transmission screen (the geometry
of ASTM D1596 cushion testing, with the specimen riding as the
"product"), not an energy-absorption test.** That is not a criticism — a
transmission screen is exactly the right instrument for the questions it
has been answering (repeatability, discriminability, blind
classification, 18/18) — but it bounds what "energy absorption" can mean
per specimen.

## 2. Verdict: what is and is not per-specimen measurable

**Not measurable with the current setup and data, by any reprocessing:**

- **Energy absorbed by the specimen, in joules.** The specimen's share of
  the ledger is small, entangled with the mat and rig, and the masses
  needed to convert accelerations to energies (carriage, specimen, vertex
  effective mass) were never recorded.
- **Energy absorption in the crashworthiness sense** — the quantity a T3
  prism designed as an absorber is actually for: work done through large
  deformation (strut buckling, snap-through, densification). The current
  test never loads the specimen into that regime, so the campaign
  objective is currently probed only through small-strain, linear-dynamics
  proxies.

**Measurable per specimen, and now demonstrated repeatable:**

| quantity | what it is physically | status in our data |
|---|---|---|
| `ζ` (ringdown damping ratio) | fraction of the specimen's *vibrational* energy dissipated per cycle (§3.6) | 5.7–11.4 %, repeats to 0.5–1.7 % absolute where r² ≥ 0.85 |
| `f_n` (ringdown frequency) | dominant modal stiffness-to-mass; for tensegrity, also a **prestress readout** (§3.5) | 500–550 Hz on good fits; cross-arrangement comparison not yet trustworthy |
| `e_rebound` | restitution-like partition of impact into the vertex hop (§3.7) | 0.019–0.030; the one quantity that transferred across sessions and the tower-damage split |
| `T` (peak ratio) | level of shock reaching the top vertex (§3.4) | ~0.99–1.02; repeatable but the *weakest* discriminator in the dataset |

`ζ` and `e_rebound` are genuine energy-dissipation *proxies* and are
defensible optimization signals for "attenuate/dissipate shock" — but
they measure dissipation of the small vibrational slice, not absorption of
drop energy. If the campaign objective is literally energy absorption,
one of the direct measurements in §4 needs to enter the loop.

## 3. Metrics primer

### 3.1 Δv — velocity change (input)

`Δv = ∫ a_base dt` over the pulse. Equals the arrest velocity of the
plate, so it doubles as a free rig-health gauge (≈ 5.4–5.5 m/s from 60 in
on a healthy tower; the pin-break sessions read 4.2–4.9). Ties to energy
only through the unlogged mass: `E_in = ½MΔv²`. Note (per the J211 audit)
Δv is a processing-dependent descriptor — its value shifts with baseline
and integration window — so it is a monitor, not a calibration.

### 3.2 Pulse width τ (FWHM) and `f·τ`

Duration of the base pulse at half its peak. A *shape* metric — invariant
to overall level — which is why it survived an unlogged 22 % energy change
and carried the blind classification. `f_n·τ` locates the specimen on the
shock-response spectrum: our τ = 1.7–3.2 ms against f_n ≈ 520 Hz gives
`f·τ ≈ 0.9–1.7`, near the SRS peak — the specimen neither isolates nor
strongly amplifies; it rides the pulse and rings afterwards. (The old
`f·τ ≤ 1.5 ⇒ quasi-static` rule of thumb was checked and refuted in the
#86 adversarial review.)

### 3.3 SRS — shock response spectrum

The standard language for "what does this shock do to hardware?": imagine
an array of single-degree-of-freedom oscillators of varying natural
frequency riding the measured base pulse; plot each one's peak response
against its frequency. Defined in ISO 18431-4 and MIL-STD-810 Method 516;
[Tom Irvine's free tutorial](https://www.vibrationdata.com/tutorials2/srs_intr.pdf)
is the best entry point. An *input-conditioned output SRS* remains the
recommended replacement for `T` as a transmission metric.

### 3.4 `T` — CFC-filtered peak ratio (the "transmissibility" misnomer)

```
T = max|a_out,filtered| / max|a_in,filtered|
```

with `a_out` the tri-axis vector magnitude at the top vertex and `a_in`
the single-axis base channel, both through a CFC low-pass. Three cautions,
all now independently established in this repo's audits: (1) the two
peaks are **not simultaneous** and the output is a nonlinear magnitude, so
this is not transmissibility in any standard (SAE J211, ISO 6487,
ISO 18431, ASTM D3332/D7136, MIL-STD-810 checked — Edison audit
`6af9d904`); call it a *filtered peak-acceleration ratio*. (2) Its value
is filter- and baseline-dependent (the CFC implementation bug and the
baseline-window sensitivity both moved it). (3) Empirically it is the
weakest specimen discriminator we have. True **transmissibility** is a
frequency-response function `|H(f)| = |X_out(f)/X_in(f)|` with a coherence
estimate — it needs averaged broadband or repeated excitation (shaker or
tap testing), which the single-transient drop does not provide.

### 3.5 `f_n` — ringdown natural frequency

After the pulse, the specimen vibrates freely at (approximately) its
dominant natural frequency, `f_n ≈ (1/2π)√(k_eff/m_eff)`. We estimate it
from the slope of the analytic (Hilbert) phase of the band-passed
ringdown, which gives sub-bin resolution on short records. Two readings
matter for this campaign:

- **For a tensegrity structure, `f_n` is a prestress gauge.** Natural
  frequencies of tensegrities shift measurably with member self-stress —
  the basis of vibration-based tension assessment
  ([Ashwear & Eriksson 2014](https://www.researchgate.net/publication/260156059_Natural_frequencies_describe_the_pre-stress_in_tensegrity_structures);
  demonstrated by modal-hammer tests on a tensegrity *simplex* — the T3
  prism topology — in
  [Appl. Sci. 10:8733, 2020](https://www.mdpi.com/2076-3417/10/23/8733),
  open access). So per-specimen `f_n` drift is a print-tension /
  wax-mount health metric, and potentially a design-variable readout.
- **Current caveat:** across arrangements our fitted `f_n` ranged
  317–552 Hz with specimen orderings that flip — the estimate still
  carries input-spectrum and multi-mode contamination. Standardizing on
  arrangement B removes the input variation; a bench tap test (specimen
  suspended, no tower) would give the clean modal reference the
  adversarial review asked for.

### 3.6 `ζ` — ringdown decay fit (the closest thing we have to an energy-dissipation measurement)

Model the free decay as a damped sinusoid:

```
x(t) ≈ A e^(−ζ ω_n t) cos(ω_d t + φ),   ω_n = 2π f_n,  ω_d = ω_n √(1−ζ²)
```

Take the band-passed ringdown, form its Hilbert envelope, fit a line to
`ln(envelope)`; the slope is `−ζω_n`, giving the damping ratio `ζ`.
Equivalent classical quantities: logarithmic decrement
`δ = 2πζ/√(1−ζ²)` (amplitude ratio of successive cycles = `e^−δ`), quality
factor `Q = 1/(2ζ)`, and — the energy statement — **fraction of
vibrational energy dissipated per cycle**:

```
ΔE/E per cycle = 1 − e^(−2δ) ≈ 4πζ  (small ζ)
```

At our fitted ζ ≈ 6–8 % and f_n ≈ 520 Hz that is **~50–60 % of the
vibrational energy dissipated every cycle**, envelope time-constant
`1/(ζω_n) ≈ 4–5 ms — which is exactly why the usable ringdown is only
5–13 ms long. Validity checklist (all enforced in
[`drop_test_abc123_blind_analysis.py`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/add-drop-test-protocol-again/scripts/analysis/drop_test_abc123_blind_analysis.py)):
single-mode band selection, fit window ending before the secondary event,
r² reported — **a ζ with r² < ~0.85 is not a damping ratio**, it is the
estimator reporting that the envelope is not one decaying mode (B1, B2,
C1 in the current data). Textbook treatments: Inman, *Engineering
Vibration* (log decrement); Ewins, *Modal Testing* (FRF/half-power);
Feldman, *Hilbert Transform Applications in Mechanical Vibration* (the
envelope method itself).

### 3.7 `t_second` and `e_rebound` — the hop

Every record shows the top vertex separating and landing back
`t_second` = 17–35 ms after impact. Ballistic flight gives the separation
velocity `v_sep = g·t_second/2`, and normalizing by impact velocity:

```
e_rebound = v_sep/Δv = g·t_second/(2Δv)
```

This is mathematically identical to measuring a coefficient of
restitution from time-between-bounces — a classic technique
([Bernstein, *Am. J. Phys.* 45:41, 1977](https://pubs.aip.org/aapt/ajp/article-pdf/45/1/41/11809656/41_1_online.pdf),
free PDF). Energy view: the hop returns only `e²` (≈ 0.04–0.09 %) of the
corresponding kinetic-energy scale — i.e. the vertex-plate interaction is
almost totally dissipative — and `e_rebound` measures the *partition*, a
dimensionless specimen constant (0.019/0.022–0.024/0.028–0.030 for
specimens 2/1/3) that survived the session and tower-damage changes.
Open question, already scheduled: the restrained-vs-unrestrained check
decides whether it characterizes the structure or the fixture interface.

### 3.8 The vocabulary the campaign objective actually lives in

For optimizing an absorber, the standard quantities (all defined in
Lu & Yu, *Energy Absorption of Structures and Materials*) are:

- **Absorbed energy** `E_abs = ∮F dx` — area of the loading–unloading
  force-displacement hysteresis loop;
- **SEA** = `E_abs`/mass — the usual optimization objective;
- **Plateau (mean crush) stress** and **densification strain**;
- **Crush-force efficiency** = mean force / peak force — high CFE means
  energy absorbed without transmitting a high peak (the absorber ideal);
- **Cushion curve** — peak transmitted G vs static loading, per drop
  height and thickness (ASTM D1596), and the **damage
  boundary/fragility** framing of ASTM D3332.

None of these is computable from the current captures. All are computable
from §4.

## 4. Three upgrade paths to a true energy-absorption measurement

**A. Quasi-static compression (recommended first).** Load frame,
compress each specimen through its working stroke, record F–d,
integrate the hysteresis loop → `E_abs`, SEA, CFE per specimen. This is
precisely the protocol of the closest paper to this program —
[Pajunen, Johanns, Pal, Rimoli & Daraio, "Design and impact response of
3D-printable tensegrity-inspired structures," *Materials & Design* 182
(2019) 107966](https://www.sciencedirect.com/science/article/pii/S0264127519304046)
([open-access version](https://authors.library.caltech.edu/96998)) —
which characterized 3D-printed tensegrity-inspired cells by quasi-static
compression *plus* drop-weight impact and showed the two agree on the
mechanism. Caveat: PU-printed material is rate-dependent, so quasi-static
numbers complement rather than replace dynamic ones. Cost: load-frame
access; specimens likely survive if kept short of densification.

**B. Instrumented direct impact.** Drop a *known mass* fitted with the
existing accelerometer directly onto the specimen: `F = M_imp·a`,
integrate once for velocity, twice for displacement, and the F–d loop per
impact gives **absorbed energy per impact in joules**, plus a
carriage-level coefficient of restitution from `v_rebound/v_impact`.
This is the energy bookkeeping of drop-weight impact standards
(ASTM D7136's instrumented-impactor method). It converts the existing
tower with minimal hardware, but it is a real protocol change and loads
specimens much harder — sacrifice articles first.

**C. Slow-motion velocimetry on the current test.** The slo-mo has so far
been used for event timing (brake catch at +76–89 ms). Its higher use is
**velocity**: a marker on the carriage, a calibrated length scale in
frame, and a known frame rate give incident and rebound velocity, hence
stack-level absorbed energy `½M(v_in² − v_out²)` per drop — once `M` is
logged. Per-*specimen* differencing this way will almost certainly drown
in mat/rig variability (the specimen's share is too small), so treat C as
a rig/stack energy audit and a Δv cross-check, not a specimen metric.
A photogate or encoder does the same job with less analysis.

**Metadata to start logging now, cost ≈ zero:** carriage/falling mass,
specimen mass (each print), mat mass and batch, drop height per session
(already agreed), first-block Δv (already adopted as the health gauge).

## 5. Reading list

**Tensegrity impact & energy absorption**
- [Pajunen et al., *Mater. Des.* 182:107966 (2019)](https://www.sciencedirect.com/science/article/pii/S0264127519304046) · [open access](https://authors.library.caltech.edu/96998) — 3D-printed tensegrity-inspired structures under quasi-static compression and drop-weight impact; the closest published analogue of this campaign. Pajunen's [PhD thesis](https://thesis.caltech.edu/13754/9/Thesis_Kirsti_Pajunen_6-2-2020_Full.pdf) (free) extends it to dynamics of tensegrity-inspired metamaterials.
- [Rimoli, "On the impact tolerance of tensegrity-based planetary landers," AIAA SciTech 2016-1511](https://arc.aiaa.org/doi/abs/10.2514/6.2016-1511) — virtual drop tests with post-buckling strut behavior; why tensegrity absorbs impact at all.
- [SUPERball: Sabelhaus et al., ICRA 2015 / NASA NTRS (free PDF)](https://ntrs.nasa.gov/api/citations/20140011157/downloads/20140011157.pdf) — the flagship tensegrity-lander hardware program.
- [Ashwear & Eriksson, *Comput. Struct.* 138:162 (2014)](https://www.researchgate.net/publication/260156059_Natural_frequencies_describe_the_pre-stress_in_tensegrity_structures) — natural frequencies as a prestress readout.
- [Obara et al., *Appl. Sci.* 10:8733 (2020), open access](https://www.mdpi.com/2076-3417/10/23/8733) — modal-hammer testing of a tensegrity simplex (T3 topology) at different self-stress levels; the experimental template for a bench `f_n` measurement.

**Shock, vibration, and damping fundamentals**
- [Irvine, "An Introduction to the Shock Response Spectrum" (free PDF)](https://www.vibrationdata.com/tutorials2/srs_intr.pdf) — and the wider [vibrationdata.com](https://www.vibrationdata.com) tutorial library.
- Lalanne, *Mechanical Vibration and Shock Analysis*, Vol. 2: *Mechanical Shock* (Wiley) — the reference monograph for pulse shapes, SRS, and drop testing.
- Harris & Piersol, *Harris' Shock and Vibration Handbook* (McGraw-Hill) — encyclopedic; chapters on shock data analysis and package cushioning.
- Inman, *Engineering Vibration* (Pearson) — log decrement, SDOF damping.
- Ewins, *Modal Testing: Theory, Practice and Application* (Wiley) — FRFs, coherence, half-power damping.
- Feldman, *Hilbert Transform Applications in Mechanical Vibration* (Wiley, 2011) — the envelope/instantaneous-phase method our ringdown fit uses.
- Lu & Yu, [*Energy Absorption of Structures and Materials* (Woodhead, 2003)](https://www.sciencedirect.com/book/9781855736887/energy-absorption-of-structures-and-materials) — SEA, CFE, plateau stress, and design of absorbers.

**Standards**
- SAE J211-1 — instrumentation for impact tests (CFC filters; see the audited notes in [`edison-trajectories/j211-audit/`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/claude/issue-94-20260806-0326/edison-trajectories/j211-audit)).
- ISO 18431-4 — shock-response spectrum analysis. · MIL-STD-810 Method 516 (freely downloadable via EverySpec) — shock testing and SRS practice.
- [ASTM D1596](https://www.astm.org/Standards/D1596.htm) — dynamic shock cushioning (our rig's geometry); ASTM D3332 — mechanical-shock fragility (damage boundary); ASTM D7136 — instrumented drop-weight impact (the §4B bookkeeping).
- ISO 5348:2021 — accelerometer mounting.

**Coefficient of restitution from timing**
- [Bernstein, *Am. J. Phys.* 45:41 (1977), free PDF](https://pubs.aip.org/aapt/ajp/article-pdf/45/1/41/11809656/41_1_online.pdf) — COR from time between bounces; the math behind `e_rebound`. Follow-ups: [Aguiar & Laudares, *Am. J. Phys.* 71:499 (2003)](https://www.if.ufrj.br/~carlos/artigos/AJP2003_listening.pdf).

---

*Prepared for issue #94; no analysis scripts or published numbers were
modified. Companion docs: the metric-by-metric audit trail lives in
[`docs/drop-test-abc123-blind-analysis.md`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/add-drop-test-protocol-again/docs/drop-test-abc123-blind-analysis.md)
and the standards audit in the j211-audit trajectory.*
