# Minimum fps for the post-impact deformation window (issue #89)

Answers @sgbaird's reframing on
[issue #89](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/89):
the camera requirement is set by the specimen deformation over the **100s of
ms after impact**, not the ~1.6 ms deceleration pulse.

## Inputs

- `prc1kn_video{1,2}_slomo.mp4` + Sony XML sidecars (959.04 fps capture)
  from the PR #86 branch (`copilot/add-drop-test-protocol-again`),
  `data/drop-tests/prc1kn-60in-5felt/video/`
- `prc1kn - set 1 - 1.zip` (this branch): 25 TP4 captures, 200 ms @ 125 kHz,
  CH2–4 top-vertex tri-axis, CH5 base plate, 60 in / 4 felt + 1 cardboard

## Reproduce

```bash
pip install numpy scipy matplotlib opencv-python-headless
unzip "prc1kn - set 1 - 1.zip" -d /tmp/prc1kn
# put the two mp4s from the PR #86 branch in /tmp/vids, then:
python postimpact_minfps.py --videos-dir /tmp/vids --daq-dir /tmp/prc1kn --out figures
```

## Key results (details in `figures/minfps_metrics.json`)

- The post-impact deformation is a **~150 ms transient**: snap-back
  oscillation (first ~25 ms, dominant ~20–50 Hz), a sustained ~3.5 %
  height dip recovering by ~90–100 ms, brake catch at ~79 ms, then the
  specimen is static to within tracking noise (±0.6 mm) for the remaining
  ~350+ ms of footage.
- DAQ post-pulse displacement content at the top vertex: ~1 mm RMS at
  20–50 Hz, 0.19 mm at 50–100 Hz, 0.07 mm at 100–200 Hz, <20 µm above
  200 Hz — i.e. everything a camera can *see* lives below ~100 Hz.
- Decimation of the 959 fps deformation trace: 240 fps reproduces it to
  within tracking noise, 120 fps is the floor (errors ~2× noise, dip
  captured), 60 fps distorts the oscillation peaks, 30 fps aliases and
  misses the dip by ~2.2 mm.
