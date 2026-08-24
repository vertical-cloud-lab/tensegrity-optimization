# `prc1kn` slow-mo videos (60 in campaign)

Two slow-motion drop videos attached directly to PR #86 by @me-madsen
(2026-07-21), with the Sony camera XML sidecars. Recorded 15:30 / 15:58 MDT
— ~5.5 h before the 20:56–22:06 DAQ campaign, i.e. rehearsal/setup drops.

| file | contents |
|---|---|
| `prc1kn_video1_slomo.mp4` | drop 1 — grid taped near the tower (1080×1920 / 30 fps re-encode, 791 frames) |
| `prc1kn_video2_slomo.mp4` | drop 2 — grid on the far OSB backdrop (962 frames) |
| `prc1kn_video1.XML`, `prc1kn_video2.XML` | Sony DSC-RX100M4 non-real-time metadata — **captureFps = 959.04p**, formatFps = 23.98p, slowAndQuickMotion |

Time base: the uploads are 23.98p→30 fps re-encodes, so ~1 in 5 frames is a
pulldown duplicate; after duplicate removal, real time = unique frame /
959.04 (see the analysis script).

Both videos include the black/white checkerboard calibration grid
(**20 mm squares**, per @me-madsen), placed at a different distance behind
the drop axis in each video. The grid is *not* in the specimen plane —
using it directly would over-read speeds by +72 % (video 1) / +122 %
(video 2); see §4 of the writeup for placement recommendations.

## Analysis

- Script: [`scripts/analysis/drop_test_prc1kn_video_analysis.py`](../../../../scripts/analysis/drop_test_prc1kn_video_analysis.py)
- Writeup: [`docs/drop-test-prc1kn-video-analysis.md`](../../../../docs/drop-test-prc1kn-video-analysis.md)
- Figures + machine-readable metrics: [`figures/`](figures/)
  (`08_video_kinematics`, `09_grid_parallax`, `10_video_montage_{drop1,drop2}`,
  `11_three_specimen_video`, `video_metrics.json`)
