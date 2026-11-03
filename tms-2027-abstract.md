# TMS 2027 Annual Meeting & Exhibition — Abstract Submission

**Meeting:** TMS 2027 Annual Meeting & Exhibition (March 14–18, 2027, Orlando, FL)
**Abstract submission deadline:** July 1, 2026
**Format:** Plain text, ≤150 words (pasted into the ProgramMaster submission block)
**Presentation preference:** Oral

**Target symposium:** AI-Enabled Materials Processing: Integrating Accelerated
Experimental Workflows and Processing-Aware Machine Learning

## Title

Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity-Inspired Energy Absorbers

## Authors

Marcus Madsen\*; Audrey Christiansen\*; Jinkwan Han\*; Jeffrey R. Hill†
(presenting); Sterling G. Baird† — Department of Mechanical Engineering,
Brigham Young University, Provo, UT, USA

\* Equal contribution. † Equal contribution.

## Abstract

Tensegrity-inspired architectures—rigid struts in a continuous flexible
network—offer tunable nonlinear force–displacement responses and high energy
absorption per mass, but their design space (strut geometry, connectivity
topology, unit-cell tiling) is too large for trial and error. We present a
closed-loop, experiment-driven campaign that co-prints rigid PLA struts and
flexible TPU tension elements by multi-material fused deposition modeling and
uses Bayesian optimization to jointly tune architecture and FDM process
parameters—nozzle temperature, print speed, layer height—from physical
measurements, not calibrated simulation. Moving toward a self-driving lab, we
couple printer and orchestration software via direct Python integration, track
full data and metadata provenance in the cloud, and keep a human in the loop,
raising autonomy. A Gaussian-process surrogate over measured peak force, specific
energy absorption, and compaction efficiency proposes batches via noisy
multi-objective acquisition, with print failures as a feasibility constraint. We
report how Pareto trade-offs evolve, distilling lessons for accelerated,
processing-aware machine learning.
