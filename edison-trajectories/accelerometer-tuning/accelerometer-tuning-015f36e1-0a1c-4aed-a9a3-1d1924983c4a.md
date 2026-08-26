I have reviewed the raw drop-tower time-domain data, your peak summary, and the analysis script. While several of your team's observations are correct, there is a critical flaw in how the filtered peaks were extracted that led to an erroneous 1.5× sensitivity discrepancy conclusion. Additionally, the "trigger artifact" interpretation is incorrect. 

Here is my point-by-step review and quantitative evidence:

### (a) Verification of CH1 Saturation
**Confirmed, but the mechanism is analog, not digital.** 
In events 2, 3, and 5, CH1 hits ceilings of 8803.5 G, 8806.2 G, and 8806.1 G respectively. However, inspecting the raw data reveals this is not a flat digital DAQ clip (which would output identical DAC values). Instead, the signal shows a "compressed" rounded top spanning ~180 µs (about 23 samples) that stays within 100 G of the peak. 
* **Evidence:** The rising slew rate decays smoothly as it approaches the ceiling (e.g., dropping from ~580 G/sample to <5 G/sample), and immediately resumes steep slew rates (-200 to -800 G/sample) on the falling edge. This asymmetric profile is the textbook signature of an analog sensor (or its ICP conditioner) reaching its electrical/physical full-scale limit. The recorded peak is invalid, and no filter can reconstruct it.

### (b) Channel-to-Sensor Mapping
**Confirmed.** 
* **Evidence:** In events 11 and 12, channels 2, 3, and 4 all respond simultaneously and peak at exactly the identical time index (t=3.896 ms) with >0.95 cross-correlation, proving they are three axes of the same sensor responding to an off-axis hit. CH4 is the Z (impact) axis because its magnitude dominates during the large hits (Events 1 and 4). CH1 has an independent, higher pre-trigger noise floor (~1.2 G RMS vs ~0.2 G RMS for CH4) and behaves entirely independently, confirming it is the single-axis sensor.

### (c) Filtering Approach and the "1.5× Discrepancy" Error
Your SAE J211 implementation (phaseless 4-pole Butterworth) and 125 kHz sample rate (which satisfies the ≥ 8×CFC Nyquist requirement) are correct. **However, your script makes a fatal error: it searches for the *global* absolute maximum of the filtered signals across the entire 0.2 s window.**

* **The Flaw:** In Event 1, CH4 hits its primary rigid-body impact at **t = 4.18 ms**. CH1 has a massive, low-frequency structural/mount oscillation that peaks at **t = 15.8 ms**. Your script compared CH1's 15.8 ms secondary resonance (483 G) to CH4's 4.18 ms primary impact (312 G) to derive the ~1.55 ratio. You are comparing two completely different physical events in the structure. 
* **The Correction:** When we restrict the peak-search to the ±1 ms impact window centered around CH4's impact:
  * **Event 1 (in-window):** CH1 CFC-180 = 342.6 G / CH4 CFC-180 = 307.2 G **(Ratio: 1.12)**
  * **Event 4 (in-window):** CH1 CFC-180 = 339.6 G / CH4 CFC-180 = 309.5 G **(Ratio: 1.10)**

The sensors agree within 10–12% on the rigid body pulse when properly time-aligned. The residual discrepancy on CFC-1000 (Ratio: ~1.65) coupled with the fact that CH1's peak lags CH4 by ~250 µs proves the sensors are at **different mechanical locations** experiencing different local shock environments, not a calibration error.

### (d) The "4.2 ms Artifact" 
**Refuted.** 
The ~4.2 ms peak on CH4 is the **actual physical impact**, not a trigger/magnet artifact. 
* **Evidence:** In quiet/aborted drops (Events 6, 7, 8), the CH4 peak between 3–5 ms is < 0.5 G. If it were a fixed electrical artifact tied to the trigger, it would appear regardless of the drop. Furthermore, the pulse at 4.2 ms has a Full-Width Half-Max (FWHM) of ~280 µs, which is a characteristic mechanical duration for a hard metal-on-metal impact, whereas electrical artifacts are typically 1-sample spikes. It simply recurs at 4.2 ms because the carriage free-fall time from release to impact is highly predictable. Do not gate this out.

### (e) Cross-Calibration Protocol
This dataset cannot be used to tune sensitivity. The sensors are clearly not co-located (evidenced by the 250 µs time lag and the massive 15.8 ms structural ringing on CH1 that CH4 doesn't see). To properly calibrate them:
1. Mount both sensors rigidly on a single heavy, stiff adapter block (e.g., steel/aluminum cube) with both sensitive Z-axes perfectly aligned to the drop axis.
2. Conduct 5–10 repeatable, sub-saturation drops (e.g., targeting 500 G, 1000 G, 2000 G).
3. Apply identical CFC-180 filtering. 
4. Gate the analysis window to ±2 ms around the impact.
5. Perform a linear regression of the `CH1_peak` vs `CH4_peak`. Force the intercept to 0. The slope is the relative scale factor. Report the standard error of the slope to quantify uncertainty. 

### (f) Recommendations and Missing Elements
1. **Fix Peak Detection:** Update the analysis pipeline to window the peak detection to the impact transient. I have uploaded a corrected peak table (`data_entry:peak-summary-impact-window-csv-z4br`) and a figure demonstrating the LF ringing misalignment (`data_entry:reviewer-ch1-ch4-alignment-png-l5fg`) to your workspace data storage.
2. **Sensor Range Selection:** The 8.8 kG hit saturated the sensor. Check your single-axis sensor's specification sheet. If it is a 10,000 G sensor, 8.8 kG is dangerously close to its actual analog limit. You must step up to a 20,000 G sensor for this test series.
3. **Mounting:** The 15.8 ms ringing on CH1 suggests it is mounted to a compliant structural member (or the carriage itself is rebounding). Ensure co-located calibration occurs on a rigid block. 

***

### Discretionary Analytical Decisions
* **Impact Window Definition:** Set a ±1.0 ms search window centered on the CH4 maximum absolute value to extract the "at-impact" CFC peaks. This window size was chosen to capture the primary rigid-body pulse (FWHM ~280 µs) while excluding the secondary 15.8 ms structural resonance.
* **CFC Filter Implementation:** Adopted the SAE J211 Appendix C difference-equation digital filter implementation (zero-phase, forward-backward) over generic `scipy.signal` Butterworth filters to strictly conform to crash testing standards. 
* **Saturation Plateau Threshold:** Defined the analog saturation "plateau" as contiguous samples within 100 G of the absolute peak. This threshold accommodates the slight curvature (non-zero slew rate) inherent in analog sensor compression, whereas a strict equality would falsely reject analog clipping.
