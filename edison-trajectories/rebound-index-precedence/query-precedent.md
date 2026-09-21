
SETTING (shared context for the question):

We rank small 3D-printed tensegrity-inspired structures (T3 prisms, printed
mass m = 18-23 g) for shock absorption with a benchtop drop tower: a plate
carrying the specimen falls h = 60 in and arrests on a polyurethane mat
(~300 G, ~2 ms base pulse, arrest velocity change dv ~ 5.4 m/s). After the
pulse, the specimen's top vertex subassembly separates from its printed seat
and lands back t_second = 17-55 ms later. Per drop we compute

    v_sep = g * t_second / 2          (ballistic time-of-flight estimate)
    e     = v_sep / dv                (~0.02-0.05; FIRST power, not squared;
                                       numerator and denominator refer to
                                       different bodies/interfaces: vertex
                                       flight vs plate arrest)
    lambda = e * m * g * h            (reported in mJ; minimized in a
                                       Bayesian-optimization campaign together
                                       with a transmitted-shock peak ratio,
                                       forming a two-objective Pareto front)

A previous audit established lambda is NOT returned kinetic energy (that would
be e^2 with the actually-flying mass) and renamed it a "velocity-weighted
impact-energy index". The question now is PRECEDENT: has anything like this
been done before, and on what stated justification?

Has anyone used a first-power coefficient-of-restitution-like velocity ratio
(rebound-to-incident velocity, NOT squared into an energy fraction), or such a
ratio multiplied by a nominal impact energy scale like m*g*h, as a
standardized index, figure of merit, or optimization objective for ranking
impact-absorbing or shock-attenuating materials, structures, equipment, or
surfaces? Examples might live in rebound hardness testing, sports-equipment
and sports-surface compliance testing, packaging/cushioning, granular or
particle damping, discrete-element-model calibration, or architected-material
impact studies. Cite specific standards or papers, give the equation each one
uses, and state the justification its authors give for using a velocity ratio
(or an unorthodox composite) rather than a true energy quantity.
