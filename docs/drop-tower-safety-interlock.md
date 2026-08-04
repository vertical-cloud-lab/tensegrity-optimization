# Drop tower — safety pin interlock

Status: **the machine is tagged "DO NOT OPERATE (safety non-functional)" and the pin
interlock is not in the circuit.** This document records what the equipment is, how the
safety pin system is intended to work, what the current state appears to be, and what has
to happen before the tower is used for anything that puts a person under the carriage.

Raised in [#92](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92)
after a second guide-rod locking pin was sheared by a drop.

## 1. Equipment

| Item | Identification |
|---|---|
| Machine | **Lansmont Model 23 Shock Test System** (spec sheet posted in [#27](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/27#issuecomment-4408498939)) |
| Controller | Lansmont **TouchTest™ Shock II** tabletop console — PLC + Beijer X2 base HMI, keyed *System Power* switch |
| DAQ | Lansmont **Test Partner 4** |
| Machine envelope | 96–120 in. tall, 21 × 24 in. footprint |
| Capability | 5000 g max, 0.25 ms min half-sine, Δv 24–32 ft/s, 80 lb max payload |

Relevant mechanics: the carriage is raised by an electric hoist and falls on chrome-plated
steel guide rods machined to tight tolerance. **Those same guide rods are the surfaces the
brake pistons clamp after impact** to prevent a secondary impact — so guide rod surface
damage is not cosmetic, it degrades both alignment and braking.

## 2. How the safety pin system is intended to work

The guide rods are cross-drilled. A **locking / safety pin** is passed through the rod
below the carriage so the carriage is physically blocked from descending. This is the
mechanical protection used while a person's hands are in the impact zone — for us, while
programmer mats (felt stacks, polyurethane sheets) are being swapped or reoriented.

The white enclosure photographed in #92 with two rubber-grommeted, stepped bores is the
**pin park (stow) station**: one bore per pin, each with a switch behind it that detects
whether that pin is seated. The intended control logic is a two-place trapped-key
argument:

> A pin can only be in one of two places — in a guide rod, or in the park station.
> The machine grants the arm/drop permissive **only when both pins are sensed in the park
> station**, which is proof that neither is in a guide rod.

Lansmont advertises "programmable safety interlocks" on the TouchTest Shock 2 controller
— note *programmable*, i.e. an interlock that can be configured, and therefore also
disabled.

### Should the tower operate with one or both pins removed?

Two readings of "removed", and they give opposite answers:

- **Removed from the guide rods and stowed in the park station** — yes. This is the *only*
  state in which the machine should fire.
- **Removed from the park station** (in a rod, broken, lost, lying on the bench) — **no.**
  With either pin unaccounted for, the machine should refuse to arm or release. That
  applies to one pin as much as to two.

So the tower being fireable today, with one pin destroyed and the park station unbolted on
a bench, is not a tolerance in the design — it is the interlock being absent from the
circuit.

The pin is a **secondary mechanical hold protecting a person**, not a component the machine
is ever meant to load. Shearing one is a near-miss, not a consumable being consumed.

## 3. Observed state (from the #92 photographs)

1. The HMI carries a taped handwritten label: **"DO NOT OPERATE (safety non-functional)."**
   The condition was known and recorded, and the machine kept being used.
2. The pin park station is **unbolted from the machine and sitting on the workbench** with
   its mounting bracket loose and no cable visible. A pin-presence interlock that has been
   physically removed cannot inhibit anything.
3. The pin that broke was a **screwdriver shaft** (Klein), snapped into two pieces. A
   screwdriver blade is hardened, notch-sensitive tool steel sized for a driver, not for
   the rod cross-hole; it fails brittle and throws fragments. This is a substitution to
   stop, not one to reorder.
4. A guide rod cross-hole is visible in the third #92 photo. The rod must be inspected at
   that hole for a raised burr / ovalisation from the shear event, since it is both a
   bearing and a brake surface.

## 4. Applicable requirements

- **OSHA 29 CFR 1910.212(a)(1)** — general machine guarding.
- **OSHA 29 CFR 1910.147 (LOTO)** — servicing where unexpected energization or release of
  *stored energy* could injure. A raised carriage is stored gravitational energy; changing
  mats under it is servicing.
- **ANSI B11.19** / **ISO 14119** — interlocking devices associated with guards; interlocks
  must be designed to minimise *reasonably foreseeable defeat*. Unbolting the device is the
  textbook defeat mode.
- **ISO 14119 Annex J — fault masking.** A two-position park station is normally two
  normally-closed contacts in series. If one is jumpered or fails closed, the other masks
  it and the fault is silent. Relevant if the interlock is restored by hand-wiring rather
  than by Lansmont.

## 5. Required actions

### Before any further use
- Honour the existing tag. No operation that requires a hand or body in the impact zone
  until the interlock is restored and verified.
- Inspect the guide rods at the cross-holes, the carriage bushings, and the brake piston
  contact surfaces for damage from both shear events.
- Whenever mats are changed: raise carriage → insert **both** pins → **key off and LOTO the
  console** → change mats → remove both pins → stow both in the park station → confirm the
  HMI permissive → clear the zone → fire. Two-person pin count before every drop.

### Restore the interlock — via Lansmont, not in-house
Contact [Lansmont service](https://www.lansmont.com/contact/service) with the machine
serial number and request:

1. Model 23 / TouchTest Shock II operation & maintenance manual (not published publicly).
2. The **safety pin part number** — a matched pair, OEM, not a screwdriver.
3. The park-station wiring / PLC interlock diagram.
4. A determination of **how the interlock came to be inoperative**: disabled in PLC
   configuration, jumpered in hardware, or never commissioned. Ask them to verify the
   permissive on recommissioning rather than trial-and-error in the lab.

### Record keeping
- Add a pin count field to the drop log. The pin was left in the rod during a repetitive
  configuration series (repeat mat swaps in fixed order) — the highest-risk task shape for
  omission errors, and a checklist is the standard control.
- Log which signal files correspond to the two breakage drops. A drop that struck and
  sheared a pin is not a valid data point, and drops after it on a possibly burred rod carry
  altered friction/alignment. See
  [#86](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/86) /
  [#94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94) — if the
  first breakage falls inside the 40-drop PU-configuration series, it is a confound for
  that comparison.

## 6. Confidence

Lansmont does not publish machine manuals. The equipment identification, the guide-rod /
brake description, and the TouchTest Shock 2 "programmable safety interlocks" feature are
sourced. **The specific interlock logic above is inferred** from the park-station hardware
in the photos plus standard machine-safety practice — the alternative implementation
(sensor at the rod rather than at the park station) yields the same answer to the question
in §2, but the wiring differs. Confirm against the manual before anyone rewires anything.

## References

- [Lansmont Model 23 Shock Test System](https://www.lansmont.com/products/shock/standard-shock-test-systems/lansmont-23) · spec sheet in [#27](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/27#issuecomment-4408498939)
- [Lansmont TouchTest Shock (TTS) controllers](https://www.lansmont.com/tts)
- [Lansmont service contact](https://www.lansmont.com/contact/service)
- [ISO 14119:2024 — Interlocking devices associated with guards](https://www.iso.org/obp/ui/en/#!iso:std:75942:en)
- [EN ISO 14119 overview (fault masking, defeat)](https://machinebuilding.net/en-iso-141192013-the-standard-for-guard-interlocking-devices)
