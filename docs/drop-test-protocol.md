# Drop-Test Protocol & Troubleshooting

**Scope.** This note captures the working setup, observed failure modes, and the
next-iteration test plan for the first crush/drop tests of multi-material
3D-printed tensegrity structures using Jeff Hill's drop tower in the BYU Smart
Materials lab. It supplements (and does not replace) the OEM documentation:

- `TP4 Quick Start Guide` (W20000-98-15 Rev A) — attached to the GitHub issue.
- `TP4 User's Guide` (W20000-98-14 Rev A) — attached to the GitHub issue.

The training walkthrough is captured on video:
<https://youtu.be/RNjpAmWWmkQ>.

## 1. Equipment

| Item | Notes |
|---|---|
| Drop tower (Jeff Hill's setup) | Hoist with electromagnetic release; rigid base plate; vertical column. |
| Accelerometer #1 (PCB / similar) | Mounted on the **drop-tower base plate** to capture the input shock. |
| Accelerometer #2 | Mounted on a **top plate** that sits on the specimen, to capture transmitted shock. |
| DAQ + laptop | Captures both channels; user/quick-start guides referenced above. Lab computer credentials are shared via Slack DM (not committed here). |
| Specimen cage | Two acrylic plates + four 18 in threaded rods + nuts (built in the Prototyping Lab by @me-madsen and @ctrhjk). Holds the top plate over the specimen and constrains its motion after impact. |
| Slow-motion camera | Phone slow-mo is acceptable for preliminary results; high-speed camera can be checked out from PSC for higher-fidelity tests. |

## 2. Quantities of interest

Per the proposal and Edison literature synthesis (see
`edison-trajectories/objective-functions/` in companion code repositories), the
drop tower contributes the following observables to the BO objective stack:

1. **Peak transmitted acceleration** `g_max` on the top-plate accelerometer
   (lower is better for cushioning) — initial ~200 ms shock window.
2. **Specific energy absorption (SEA)** inferred from drop height,
   specimen mass, and the difference between input and transmitted impulses.
3. **Post-shock decay / ringdown** captured in the **full ~10 s window** after
   impact (not only the 200 ms shock), to expose secondary modes and damping.
4. **Reusability** — qualitative survival/damage assessment per drop, and
   number of drops to failure `N_reuse`.
5. **Slow-motion video** of the descent **and** the moments before/during
   impact, framed so the specimen is in view as the hoist begins to lower
   (not only after release).

## 3. Known failure modes from the first attempts

Observed in the first instrumented drops (see the video clip linked in the
issue at <https://github.com/user-attachments/assets/878f940a-0778-4de7-a0bf-0d070e62d0bb>):

1. **Specimen / base-plate separation before impact.** The tensegrity
   structure lifts off the lower acrylic plate during descent, so the
   specimen is no longer aligned under the top plate at impact.
2. **Cage tilt.** The clearance between the acrylic-plate guide holes and
   the threaded rods is loose enough to allow ~25° tilt of the top plate,
   which biases the transmitted-acceleration measurement and risks
   off-axis loading of the accelerometer.
3. **Framing.** Slow-motion footage to date starts after the hoist has
   already begun lowering, so the initial descent is out of frame.

## 4. Next-iteration test plan

Per @sgbaird (issue comment): run the following three drops, in order,
capturing slow-motion video for each. Frame the camera so the **specimen and
the hoist release point are both in view at t = 0**.

1. **Bare specimen.** No accelerometer, no acrylic plates — just the
   tensegrity structure on the base. Establishes baseline rebound/tip-over
   behavior.
2. **Plate-on-specimen, no instrumentation.** No accelerometer; the upper
   acrylic plate is balanced on top of the specimen with no rod constraint.
   The plate is expected to bounce off; document the trajectory.
3. **Instrumented cage drop.** Accelerometer attached to the top plate;
   acrylic plate is constrained by the threaded rods so it cannot fly off;
   plate rests on top of the tensegrity structure.

For test 3, also attempt to capture the **full ~10 s ringdown** on the DAQ,
not only the initial shock window.

## 5. Mitigations under consideration

- **Tighter rod/plate tolerance.** Re-drill the acrylic plates (or move to
  thin metal plates) to reduce the rod clearance and the 25° tilt; consider
  linear bushings if the budget allows.
- **Plate retention clips.** Light clips that prevent the top plate from
  rising above its rest height, so it stays seated on the specimen until
  impact — addresses failure mode (1).
- **Vertex-mounted accelerometer with cage.** Longer-term option: attach
  the accelerometer directly to one vertex of the tensegrity and surround
  the specimen with an acrylic cage with the accelerometer cable fed
  through, so the structure cannot fly off with the accelerometer.
- **Lab access.** All three students working on the drop tests
  (@me-madsen, @ctrhjk, @achris0520) should be granted independent access
  to the lab so testing does not bottleneck on a single operator.

## 6. Related modalities (out of scope for the first drop test)

Captured here so the protocol stays consistent with the broader objective
matrix; details live in the companion `edison-trajectories/objective-functions/`
materials:

- **High-speed camera** instead of phone slow-mo, for sharper
  displacement-vs-time on the deforming struts.
- **Shaker transfer function** — mount accelerometer on top of the
  structure on a shaker and sweep frequency to measure attenuation
  vs. frequency.
- **Slug-firing (gas-gun) impact** for tiled / foam-like specimens with a
  plate in front, giving a longer-duration shock impulse than the drop
  tower.
- **Polytec / QTec LDV** for contactless displacement on the slug-firing
  rig.
