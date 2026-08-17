# BambuStudio CLI multi-material PLA/TPU per-part extruder assignment bug

**Status:** investigation only — fix must be filed upstream against
[`bambulab/BambuStudio`](https://github.com/bambulab/BambuStudio); we cannot patch the
slicer from this repo.

**Why this lives here:** Phase-1 of the tensegrity-optimization prototype prints
co-extruded PLA struts + TPU 85A tendons on a multi-extruder Bambu printer
(`reviews/...`, `simulations/printable_design.py`). Any time we re-run the
slicer CLI with refreshed profiles (`--load-settings` + `--load-filaments`) the
job fails out with the bogus error reproduced below, which blocks the build
pipeline.

## Reported symptom

> After re-loading profiles with `--load-settings` / `--load-filaments`: filament
> TPU can not be printed on extruder 21842, under manual mode for multi extruder
> printer → CLI assigns a bogus extruder id to the per-part.

`21842` is not a real extruder index — only extruders `1..new_extruder_count`
exist. The value is an uninitialised / out-of-bounds read.

## Root cause (BambuStudio @ `e150b502`, `src/BambuStudio.cpp`)

The relevant block is the manual-mode printability validator at lines 6764–6796:

```cpp
// L6764
for (int index = 0; index < filament_maps.size(); index++) {
    int filament_extruder = filament_maps[index];
    if (unprintable_filament_ids[filament_extruder - 1].find(index + 1)
            != unprintable_filament_ids[filament_extruder - 1].end()) { ... }
}

// L6775
for (int f_index = 0; f_index < plate_filaments.size(); f_index++) {
    for (int f_index = 0; f_index < plate_filaments.size(); f_index++) {   // (1)
        if (plate_filaments[f_index] <= filament_count) {                  // (2)
            int filament_extruder = filament_maps[plate_filaments[f_index] - 1]; // (3)
            std::string filament_type;
            m_print_config.get_filament_type(filament_type, plate_filaments[f_index] - 1);
            auto *filament_printable_status =
                dynamic_cast<const ConfigOptionInts *>(m_print_config.option("filament_printable"));
            if (filament_printable_status &&
                (filament_printable_status->values.size() >= plate_filaments[f_index])) {
                int status = filament_printable_status->values.at(plate_filaments[f_index] - 1);
                if (!(status >> (filament_extruder - 1) & 1)) {           // (4)
                    BOOST_LOG_TRIVIAL(error)
                        << boost::format("plate %1% : filament %2% can not be printed on extruder %3%, ...")
                           % (index + 1) % filament_type % filament_extruder;
                    ...
                }
            }
        }
    }
}
```

Three defects compound to produce the symptom:

1. **Shadowed inner loop (line 6775–6776).** Both loops declare `int f_index`;
   the inner shadow makes the outer loop iterate exactly once (the inner runs
   `plate_filaments.size()` times, then increments the outer `f_index` past the
   end). Almost certainly a copy-paste regression. Cosmetic on its own, but it
   masks the defect below by appearing to "cover" all filaments.

2. **Missing bounds check on `filament_maps`.** The guard at (2) only checks
   `plate_filaments[f_index] <= filament_count`, not against
   `filament_maps.size()`. After `--load-filaments` shrinks the active filament
   set (e.g. original 3MF had 4 filaments, CLI re-loads 2: PLA + TPU), the
   `filament_map` ConfigOptionInts in `m_extra_config` is only resized to the
   new `filament_count` in some paths (line 6624–6664 only sanitises `-1`
   sentinels; it does not enforce
   `filament_maps.size() == filament_count`). Meanwhile `plate_filaments` is
   built from per-volume `ModelVolume::config.option("extruder")` on the loaded
   3MF — those still reference the *original* slot numbers (3, 4, …).
   Indexing `filament_maps[plate_filaments[f_index] - 1]` is then an
   out-of-bounds read on a `std::vector<int>`; `operator[]` returns
   uninitialised memory → `filament_extruder == 21842`.

3. **No range check before the bitshift (4).** Even when `filament_maps` is
   correctly sized, a stale per-part extruder id larger than `new_extruder_count`
   feeds `status >> (filament_extruder - 1)` with a shift count ≥ width of `int`
   → implementation-defined behaviour, in practice always producing
   "unprintable" and the same misleading error.

## Reproduction

```
bambu-studio-cli \
    --load-settings <process.json> <machine_with_2_extruders.json> \
    --load-filaments <pla.json> <tpu.json> \
    --filament-map-mode "manual" \
    --filament-map 1 2 \
    --export-3mf out.3mf \
    input.3mf          # input was sliced with 4 filaments, TPU was slot 3
```

`input.3mf` carries `ModelVolume` configs with `extruder = 3` / `4`. The CLI
keeps those volume-level assignments but truncates `filament_map` to 2 slots,
triggering the OOB read.

## Proposed upstream patch

Three small, independent fixes in `src/BambuStudio.cpp` around line 6775:

```diff
-                                    for (int f_index = 0; f_index < plate_filaments.size(); f_index++) {
-                                        for (int f_index = 0; f_index < plate_filaments.size(); f_index++) {
-                                            if (plate_filaments[f_index] <= filament_count) {
-                                                int filament_extruder = filament_maps[plate_filaments[f_index] - 1];
+                                    for (int f_index = 0; f_index < (int)plate_filaments.size(); f_index++) {
+                                        const int fid = plate_filaments[f_index];
+                                        if (fid >= 1 && fid <= filament_count
+                                            && (size_t)fid <= filament_maps.size()) {
+                                            const int filament_extruder = filament_maps[fid - 1];
+                                            if (filament_extruder < 1 || filament_extruder > new_extruder_count) {
+                                                BOOST_LOG_TRIVIAL(error) << boost::format(
+                                                    "plate %1% : filament %2% has invalid extruder id %3% "
+                                                    "(expected 1..%4%); per-part extruder map was not rebuilt "
+                                                    "after --load-filaments")
+                                                    % (index + 1) % fid % filament_extruder % new_extruder_count;
+                                                record_exit_reson(outfile_dir, CLI_INVALID_PARAMS, index + 1,
+                                                                  cli_errors[CLI_INVALID_PARAMS], sliced_info);
+                                                flush_and_exit(CLI_INVALID_PARAMS);
+                                            }
                                                 std::string filament_type;
-                                                m_print_config.get_filament_type(filament_type, plate_filaments[f_index] - 1);
+                                                m_print_config.get_filament_type(filament_type, fid - 1);
                                                 auto *filament_printable_status = dynamic_cast<const ConfigOptionInts *>(m_print_config.option("filament_printable"));
-                                                if (filament_printable_status && (filament_printable_status->values.size() >= plate_filaments[f_index])) {
-                                                    int status = filament_printable_status->values.at(plate_filaments[f_index] - 1);
+                                                if (filament_printable_status
+                                                    && (filament_printable_status->values.size() >= (size_t)fid)) {
+                                                    const int status = filament_printable_status->values.at(fid - 1);
                                                     if (!(status >> (filament_extruder - 1) & 1)) {
                                                         ...
                                                     }
                                                 }
                                             }
-                                        }
                                     }
```

Independently, the `filament_map` re-sizing branch at L6624–6664 should grow
**and shrink** `filament_maps` to exactly `filament_count` entries after
`--load-filaments`, defaulting any new slots to `1` and dropping the tail.

## Workaround for our pipeline

Until upstream merges a fix, our print scripts should either:

1. Pass `--filament-map` explicitly with exactly `filament_count` entries that
   match the post-`--load-filaments` slot order, and confirm via log that the
   sanitiser at L6644 prints `filament map default_value 1` (or the intended
   extruder) for every slot; **or**
2. Re-author the input 3MF so every `ModelVolume` `extruder` is `1` or `2`
   before CLI invocation (e.g. with a small `lib3mf` pre-pass that clamps every
   per-volume `extruder` config to `min(extruder, filament_count)`); **or**
3. Avoid `--load-filaments`/`--load-settings` and let the 3MF embedded profiles
   drive the slice.

Option (2) is the most reliable for the BO loop because option (1) still trips
the OOB read whenever Ax proposes a design whose pre-rendered 3MF references
more filament slots than the active CLI filament set.

## Upstream issue draft

Title: `CLI: out-of-bounds read on filament_maps after --load-filaments yields
"can not be printed on extruder <garbage>" under manual multi-extruder mode`

Body: paste sections "Reported symptom", "Reproduction", "Root cause", and
"Proposed upstream patch" above. Reference `src/BambuStudio.cpp` line ranges
relative to commit `e150b502b3d2afc98b83dcc9e5720e998f9eb79a`.
