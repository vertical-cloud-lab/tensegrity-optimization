# Edison audit query: is "rebound energy" the right name and form for our drop-tower optimization objective?

Submitted 2026-08-25 from PR #97 of vertical-cloud-lab/tensegrity-optimization,
at the request of @me-madsen ("do an Edison review of this and ensure it holds
up. I'm unclear as to whether what we're doing counts as rebound energy, and
what it could be measuring. What would change if this is wrong?").

## Full query text sent to Edison

We are optimizing small 3D-printed tensegrity structures (T3 prisms, printed
mass 18 to 23 g) for impact energy absorption using a drop tower. The
instrumented plate carrying the specimen falls h = 60 in (1.524 m) and arrests
on a polyurethane mat stack, producing a ~300 G, ~1.6 ms half-sine base pulse
with velocity change dv = integral of base acceleration ~ 5.4 m/s (free-fall
speed). The specimen rides the plate, responds elastically, rings down at
f_n ~ 300-550 Hz with damping ratio zeta ~ 6-11 percent, and its top vertex
separates from its seat and lands back t_second = 17-55 ms later (detected as
an envelope burst in the accelerometer record).

From this we define, per drop:

1. e_rebound = v_sep / dv = g * t_second / (2 * dv), where v_sep = g*t_second/2
   is the ballistic separation velocity inferred from the flight time (the
   time-between-bounces method of Bernstein, Am. J. Phys. 45:41, 1977).
   Measured values: e_rebound = 0.02 to 0.05 across our batch. We interpret it
   as a kinematic coefficient-of-restitution-like quantity for the top-vertex/
   seat interaction.

2. A Bayesian-optimization objective named "rebound energy":
   e_reb_mJ = e_rebound * m_printed * g * h, in millijoules (6 to 14 mJ across
   the batch), described in our code as "absolute rebound energy returned to
   the payload per drop", with a docstring sentence claiming "the raw
   e_rebound is a fraction of the impact energy". It is minimized together
   with a transmitted-shock ratio objective. Its measurement noise model is
   SEM_rel = hypot(e_sem/e_mean, mass_sd/m).

Questions to audit, in order of importance:

A. Physics check: is e_reb_mJ = e * m * g * h a defensible quantity to call
   "rebound energy"? Standard impact mechanics (Stronge) says the kinetic
   energy returned by a contact with kinematic restitution e is
   KE = e^2 * (1/2 m v^2) = e^2 * m * g * h, which for our numbers is
   ~0.1-0.7 mJ (microjoule scale), a factor 1/e ~ 20-50 smaller than the
   published e*m*g*h values. Is there ANY standard framework (packaging,
   cushioning, rebound resilience, sports-equipment COR testing, seismic
   pounding, robotics) in which a first-power-of-e times impact-energy
   quantity has an accepted name or use? Or is e*m*g*h only defensible as an
   ad hoc scalarization (a velocity-weighted index)?

B. What could e_rebound itself actually be measuring in our setup? The body
   that flies is the top vertex of the tensegrity (plus a 0.8 g accelerometer
   and its printed seat and cable tail), not the whole printed mass, and the
   "seat" is a printed key-seat joint. Candidate physical interpretations:
   (i) a genuine restitution coefficient of the vertex-seat contact;
   (ii) a measure of how much post-pulse vibrational/elastic energy the
   structure channels into vertex separation (structure property);
   (iii) a fixture/interface property (seating, wax mount) rather than a
   design property. What experiments distinguish these (we have a
   restrained-vs-unrestrained check scheduled)? Are there literature
   precedents for using secondary-impact timing of a substructure as a
   dissipation metric?

C. Consequences if the naming/physics is wrong: (1) does using e vs e^2 change
   a Pareto-front minimization's ranking in general (we verified it does not
   for our current batch, where the e spread of 2.5x dwarfs the mass spread of
   1.2x, but want the general statement)? (2) The uncertainty model: under
   e^2*m*g*h the delta method gives SEM_rel = hypot(2*e_sem/e, mass_sd/m); is
   that correct? (3) Are there downstream dangers of an objective whose name
   over-claims (e.g., reporting "mJ returned to payload" in papers or to
   stakeholders when the true returned KE is ~40x smaller)?

D. Literature: please identify the most relevant published work for
   (i) coefficient of restitution measured from bounce/flight timing;
   (ii) rebound-based energy metrics in materials testing, e.g. rubber rebound
   resilience (ISO 4662, ASTM D2632 vertical rebound, Bashore/Schob pendulum,
   Leeb hardness), where resilience = h_return/h_drop = e^2, and whether any
   standard uses first-power e as an energy fraction;
   (iii) tensegrity or lattice/metamaterial impact testing where rebound or
   restitution was an optimization or characterization objective (e.g.
   Pajunen, Johanns, Pal, Rimoli, Daraio, Materials & Design 182:107966,
   2019; Rimoli AIAA 2016-1511 tensegrity planetary landers; SUPERball);
   (iv) drop-test/cushioning standards language for what may legitimately be
   called rebound energy (ASTM D1596, D3332, MIL-STD-810, Lalanne).

Please give a clear verdict per question, with citations, and state
explicitly if any claim above is wrong or unsupported.
