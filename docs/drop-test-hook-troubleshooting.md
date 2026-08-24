# Release-Hook Sticking Open — Troubleshooting Note

**Scope.** The hoist release hook on Jeff Hill's drop tower has started
sticking in the **open** position: after a drop, when the crosshead is lowered
back onto the carriage, the hook no longer falls closed under gravity to
re-engage the carriage post ([reported by @me-madsen on PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5051519185),
with video). It can be moved into place by hand "quite easily and provides
little resistance to movement". WD-40 was applied to the hook per
@Jeffrayhill1's suggestion and worked back and forth; the sticking persists.

This note records the diagnosis ladder and fixes. The tower is a custom build,
so there is no OEM known-issues list to consult — but the *mechanism class*
(gravity-reset latch pawl with an actuated release) has well-documented failure
modes, and this symptom pattern maps onto them cleanly.

## 1. What the symptom tells us

A pawl that **swings freely by hand but will not fall closed** is *not*
suffering gross binding (a seized pivot resists hand motion too). It is a
**closing-torque-margin failure**: the gravity torque returning the hook is
tiny near the open position, and some small opposing effect — magnetic pull,
oil-film adhesion, an over-center geometry, or an actuator that hasn't
retracted — now exceeds it. This is also why WD-40 didn't help: friction at
the pivot was never the deficit.

The rig has now logged well over 1,500 drops across the committed campaigns,
so wear/peening of the hook faces, a slowly-magnetizing hook, and accumulated
lubricant residue are all age-consistent.

## 2. Candidate causes, ranked

1. **Residual magnetism (remanence).** The protocol records an
   **electromagnetic release on the hoist**
   ([§1 of the protocol](drop-test-protocol.md)). DC electromagnets and
   solenoids retain a residual field after power-off that can keep holding a
   ferromagnetic armature/hook; repeated shock cycles can also progressively
   magnetize the hook steel itself. Hand force easily defeats the residual
   pull, but the hook's own gravity torque cannot — exactly the reported
   symptom. Lubricant is irrelevant to this cause.
2. **Oil-film stiction from the WD-40 (can make it worse, not better).** The
   hook is a thin flat plate running close to machined faces. A wetting oil
   film between flat faces adds viscous/surface-tension adhesion that a
   marginal-gravity pawl cannot break, and WD-40 specifically dries to a gummy
   residue that attracts dust. A **heavier rail oil on the hook would make
   this worse** (fine on the guide rails; keep it off the latch).
3. **Over-center / balance geometry.** If the open position carries the
   hook's center of gravity to (or past) vertical over the pivot, gravity
   closing torque goes to ~zero (or reverses and actively holds it open).
   Wear, a bent tail, or increased actuator throw can move a mechanism that
   used to stop short of top-dead-center past it.
4. **Release actuator not fully retracting.** A solenoid plunger or air
   cylinder that returns slowly/incompletely (weak return spring, sticky
   seal, slow exhaust) physically props the hook open. Back-driving a small
   actuator by hand is easy — also consistent with "moves easily by hand".
5. **Pivot/side-plate contact.** Over-tightened pivot bolt, a slight bend
   letting the plate rub its guard, or an impact-peened burr that catches
   only near the open angle.

## 3. Diagnosis ladder (~10 min, no parts)

Run in order; each step isolates one cause.

1. **Free-swing test.** Power (and air, if plumbed) off, crosshead away from
   the carriage. Swing the hook slowly through its travel by hand and let go
   at several angles. A healthy gravity pawl falls closed from *any* angle.
   Note the angles where it stays put — near-open only ⇒ causes 1/3/4;
   everywhere ⇒ cause 2/5.
2. **Paperclip test.** Hold a paperclip or steel screw to the hook face and
   the release-magnet face with power off. If either holds the clip, remanence
   is confirmed (cause 1).
3. **Actuator isolation.** Disconnect/space the release actuator (unplug, or
   vent air) and repeat the free-swing test. Hook now falls ⇒ cause 4 (or 1,
   if the "actuator" is the electromagnet face itself).
4. **Degrease.** Clean all WD-40 off the hook, pivot, and mating faces with
   isopropyl alcohol or brake cleaner; test **dry**. Falls now ⇒ cause 2.
5. **Pivot check.** Back the pivot bolt off a quarter turn / verify it's a
   shoulder-bolt arrangement; inspect the engagement faces for peening burrs
   (dress lightly with a fine file if found).

## 4. Fixes

- **Definitive, cause-independent: add positive closing force.** A light
  extension or torsion spring (or a few grams of weight on the hook tail)
  converts the latch from gravity-reset to spring-reset with real margin.
  Commercial drop-weight testers use spring-loaded jaws/pins for exactly this
  reason — gravity-only reset is inherently marginal. Size the spring so the
  release actuator still opens it easily (it only needs to beat remanence +
  film adhesion + friction, a few tens of grams-force at the hook tip).
- **If remanence confirmed:** put a thin (~0.5 mm) **brass/stainless/plastic
  shim** on the electromagnet pole face (standard anti-remanence air gap;
  slightly reduces holding force), and/or degauss the hook (stroke it with a
  demagnetizer, or drive the release coil with a brief reverse-polarity
  pulse). Electrically, a reverse pulse or an LC snubber across the coil at
  turn-off is the textbook fix.
- **Lubrication policy:** keep the latch **dry or dry-film lubricated**
  (PTFE/graphite "dry lube"). No WD-40, no rail oil on the hook. Rail oil
  stays on the rails.
- **If the actuator is the culprit:** stiffen/replace its return spring, or
  add a hard stop so the hook's open travel stops well short of top-dead-center.

## 5. Interim workaround

Manually seating the hook each cycle (as the team is already doing) is safe
but costs the ~42 s/drop automatic cadence that the 50–100-drop campaigns
depend on ([sample-size analysis](drop-test-sample-size-analysis.md)); at 50
drops/specimen a manual re-latch adds an operator touch every cycle and
roughly doubles attended time. The spring fix is a one-hour repair that
restores hands-off operation.

## 6. References

- WD-40 residue/dust gumming: [BladeForums](https://www.bladeforums.com/threads/wd-40-why-not-to-use-it.1160243/),
  [Bob Is The Oil Guy](https://bobistheoilguy.com/forums/threads/wd-40-causes-a-sticky-goo-and-hard-varnish.384986/page-2),
  [door/lock lubrication note](https://www.doorwindowsurgeon.com/post/the-misconception-of-locks-lubricant-and-wd-40);
  WD-40's own dry-PTFE alternative exists for this reason.
- Solenoid/electromagnet remanence holding an armature after power-off, and
  fixes (reverse-polarity degauss pulse, ejector pin, pole-face shim):
  [TLX latching-solenoid theory](https://www.tlxtech.com/solenoid-theory/latching-solenoid-theory),
  [Industrial Monitor Direct app note](https://industrialmonitordirect.com/blogs/knowledgebase/resolving-24v-dc-electromagnet-residual-magnetism-drop-issues),
  [Electronic Specifier](https://www.electronicspecifier.com/news/analysis/electro-magnets-overcome-the-problems-of-residual-magnetism/),
  [US10032551B2 (capacitor-discharge degauss)](https://patents.google.com/patent/US10032551B2/en).
- Spring-loaded (not gravity-only) engagement in drop-weight impact testers:
  [US5457984](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5457984),
  [US5540078](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5540078);
  purpose-built drop-test release hooks: [Elebia D10](https://elebia.com/droptesthook-d10/).
