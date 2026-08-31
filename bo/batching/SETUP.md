# Reproducing the batch-size slicing sweep

Environment used for the results in this directory (2026-08-31, GitHub Actions
runner, Ubuntu 24.04):

1. Download Bambu Studio v02.07.01.62 (the exact version that produced the
   as-printed batch file) and extract it. No display is needed; the CLI slices
   headless once GStreamer and WebKitGTK libraries are installed:

   ```bash
   sudo apt-get install -y libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 \
       libgstreamer-plugins-bad1.0-0 libwebkit2gtk-4.1-0
   curl -sLO https://github.com/bambulab/BambuStudio/releases/download/v02.07.01.62/BambuStudio_ubuntu24.04-v02.07.01.62-20260616195227.AppImage
   chmod +x BambuStudio_ubuntu24.04-*.AppImage
   ./BambuStudio_ubuntu24.04-*.AppImage --appimage-extract   # creates squashfs-root/
   ```

2. Fetch the as-printed Sobol batch project from the PR #102 branch and unzip
   it next to the scripts (the builders read meshes and settings from
   `batch_x/`):

   ```bash
   git show origin/claude/issue-98-20260821-0103:bo/slices/t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.as-printed.3mf > batch.3mf
   unzip -q batch.3mf -d batch_x
   ```

3. Run the sweep. It writes `single_N.3mf` and `out_N/plate_1.gcode` for
   N = 1..9, then `all9.3mf` and `out_all9/`:

   ```bash
   ./run_sweep.sh
   python3 parse_results.py   # writes batch-walltime-results.csv
   python3 plot_results.py    # writes batch-walltime-tradeoff.png
   ```

Notes:

- `build_plate.py N out.3mf` builds a one-plate project with N instances of
  Specimen 04 (object id 15 in the batch file), reusing the object definition,
  mesh file, and full `project_settings.config` verbatim. Instances sit on a
  fixed 3x3 grid (columns x=70/160/250 mm, rows y=48/125/202 mm, filled
  row-major) sized from the measured article box (77x75 mm in sliced G-code,
  organic supports and brim included) so all nine clear the wipe tower zone
  (H2D profile default position x=165, y=250) and the extrusion calibration
  strip at the plate front.
- `--arrange 1` is deliberately not used: the CLI arranger reserves
  conservative margins and overflows to a second plate beyond 6 of these
  articles. It also resets the wipe tower to the profile default position.
- `build_group.py out.3mf "objid:x:y,..."` does the same for arbitrary
  specimens; `run_sweep.sh` uses it to slice the real 9-article Sobol batch
  as two plates (specimens 5, 2, 3, 1, 8 and specimens 6, 0, 7, 4), because
  the four largest articles cannot share one plate once supports and the
  wipe tower are accounted for.
- Sanity check: a rebuilt single-instance plate re-slices to within 0.5 % of
  plate 6 of the as-printed file (position on the plate shifts travel time
  slightly).
- The G-code files (8 to 40 MB each) are not committed; per-run
  `result.json` files are, under `results-json/`.
